"""
Redis Queue Implementation (BullMQ-compatible pattern)
Handles job queueing and processing for article generation
"""
import asyncio
import json
import time
from typing import Dict, Optional, Any
from uuid import uuid4
from enum import Enum

import redis.asyncio as redis
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class JobStatus(Enum):
    """Job status states"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


class QuestQueue:
    """
    Redis-based job queue for Quest Platform
    Implements BullMQ-like patterns for Python
    """

    def __init__(self):
        self.redis_url = settings.REDIS_URL or settings.UPSTASH_REDIS_URL
        self.redis_client = None
        self.queue_name = "quest:articles"
        self.job_prefix = "quest:job:"
        self.max_retries = 3
        self.retry_delay = [1000, 5000, 15000]  # Exponential backoff in ms

    async def connect(self):
        """Connect to Redis"""
        try:
            if not self.redis_url:
                logger.warning("queue.redis_not_configured")
                return False

            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )

            # Test connection
            await self.redis_client.ping()
            logger.info("queue.connected", url=self.redis_url[:30] + "...")
            return True

        except Exception as e:
            logger.error("queue.connection_failed", error=str(e))
            self.redis_client = None
            return False

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None

    async def enqueue(
        self,
        job_type: str,
        data: Dict,
        priority: int = 0,
        delay: int = 0,
        job_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Add job to queue

        Args:
            job_type: Type of job (e.g., "generate_article")
            data: Job data
            priority: Job priority (higher = more important)
            delay: Delay in milliseconds before processing
            job_id: Optional external job ID (if None, generates new UUID)

        Returns:
            Job ID if successful, None otherwise
        """
        if not self.redis_client:
            if not await self.connect():
                return None

        # Use provided job_id or generate new one
        job_id = job_id or str(uuid4())
        job_key = f"{self.job_prefix}{job_id}"

        job_data = {
            "id": job_id,
            "type": job_type,
            "data": data,
            "status": JobStatus.PENDING.value,
            "priority": priority,
            "attempts": 0,
            "created_at": time.time(),
            "updated_at": time.time()
        }

        try:
            # Store job data
            await self.redis_client.hset(
                job_key,
                mapping={
                    k: json.dumps(v) if isinstance(v, (dict, list)) else str(v)
                    for k, v in job_data.items()
                }
            )

            # Set expiry (24 hours)
            await self.redis_client.expire(job_key, 86400)

            # Add to queue (with priority and delay)
            if delay > 0:
                # Add to delayed queue
                score = time.time() + (delay / 1000)
                await self.redis_client.zadd(
                    f"{self.queue_name}:delayed",
                    {job_id: score}
                )
            else:
                # Add to priority queue
                await self.redis_client.zadd(
                    f"{self.queue_name}:waiting",
                    {job_id: -priority}  # Negative for descending sort
                )

            logger.info(
                "queue.job_enqueued",
                job_id=job_id,
                job_type=job_type,
                priority=priority,
                delay=delay
            )

            return job_id

        except Exception as e:
            logger.error(
                "queue.enqueue_failed",
                job_id=job_id,
                error=str(e)
            )
            return None

    async def dequeue(self) -> Optional[Dict]:
        """
        Get next job from queue

        Returns:
            Job data if available, None otherwise
        """
        if not self.redis_client:
            if not await self.connect():
                return None

        try:
            # First, check delayed jobs
            await self._process_delayed_jobs()

            # Get next job from priority queue
            result = await self.redis_client.zpopmin(
                f"{self.queue_name}:waiting",
                count=1
            )

            if not result:
                return None

            job_id = result[0][0]
            job_key = f"{self.job_prefix}{job_id}"

            # Get job data
            job_data = await self.redis_client.hgetall(job_key)

            if not job_data:
                logger.warning("queue.job_not_found", job_id=job_id)
                return None

            # Parse job data
            job = {
                k: json.loads(v) if k in ["data"] else v
                for k, v in job_data.items()
            }

            # Update status to processing
            await self.update_job_status(job_id, JobStatus.PROCESSING)

            # Move to processing set
            await self.redis_client.sadd(
                f"{self.queue_name}:processing",
                job_id
            )

            logger.info(
                "queue.job_dequeued",
                job_id=job_id,
                job_type=job.get("type")
            )

            return job

        except Exception as e:
            logger.error("queue.dequeue_failed", error=str(e))
            return None

    async def complete_job(self, job_id: str, result: Any = None):
        """
        Mark job as completed

        Args:
            job_id: Job ID
            result: Job result data
        """
        if not self.redis_client:
            return

        job_key = f"{self.job_prefix}{job_id}"

        try:
            # Update job data
            updates = {
                "status": JobStatus.COMPLETED.value,
                "completed_at": str(time.time()),
                "updated_at": str(time.time())
            }

            if result is not None:
                updates["result"] = json.dumps(result)

            await self.redis_client.hset(job_key, mapping=updates)

            # Remove from processing set
            await self.redis_client.srem(
                f"{self.queue_name}:processing",
                job_id
            )

            # Add to completed set
            await self.redis_client.sadd(
                f"{self.queue_name}:completed",
                job_id
            )

            logger.info("queue.job_completed", job_id=job_id)

        except Exception as e:
            logger.error(
                "queue.complete_job_failed",
                job_id=job_id,
                error=str(e)
            )

    async def fail_job(self, job_id: str, error: str):
        """
        Mark job as failed and handle retries

        Args:
            job_id: Job ID
            error: Error message
        """
        if not self.redis_client:
            return

        job_key = f"{self.job_prefix}{job_id}"

        try:
            # Get current job data
            job_data = await self.redis_client.hgetall(job_key)

            if not job_data:
                return

            attempts = int(job_data.get("attempts", 0))

            if attempts < self.max_retries:
                # Retry with exponential backoff
                delay = self.retry_delay[min(attempts, len(self.retry_delay) - 1)]

                # Update job data
                await self.redis_client.hset(
                    job_key,
                    mapping={
                        "status": JobStatus.RETRY.value,
                        "attempts": str(attempts + 1),
                        "last_error": error,
                        "updated_at": str(time.time())
                    }
                )

                # Remove from processing
                await self.redis_client.srem(
                    f"{self.queue_name}:processing",
                    job_id
                )

                # Add back to delayed queue
                score = time.time() + (delay / 1000)
                await self.redis_client.zadd(
                    f"{self.queue_name}:delayed",
                    {job_id: score}
                )

                logger.info(
                    "queue.job_retry",
                    job_id=job_id,
                    attempt=attempts + 1,
                    delay=delay
                )
            else:
                # Max retries exceeded - mark as failed
                await self.redis_client.hset(
                    job_key,
                    mapping={
                        "status": JobStatus.FAILED.value,
                        "failed_at": str(time.time()),
                        "last_error": error,
                        "updated_at": str(time.time())
                    }
                )

                # Remove from processing
                await self.redis_client.srem(
                    f"{self.queue_name}:processing",
                    job_id
                )

                # Add to failed set
                await self.redis_client.sadd(
                    f"{self.queue_name}:failed",
                    job_id
                )

                logger.error(
                    "queue.job_failed",
                    job_id=job_id,
                    attempts=attempts + 1,
                    error=error
                )

        except Exception as e:
            logger.error(
                "queue.fail_job_error",
                job_id=job_id,
                error=str(e)
            )

    async def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        data: Optional[Dict] = None
    ):
        """
        Update job status

        Args:
            job_id: Job ID
            status: New status
            data: Additional data to update
        """
        if not self.redis_client:
            return

        job_key = f"{self.job_prefix}{job_id}"

        updates = {
            "status": status.value,
            "updated_at": str(time.time())
        }

        if data:
            updates.update({
                k: json.dumps(v) if isinstance(v, (dict, list)) else str(v)
                for k, v in data.items()
            })

        try:
            await self.redis_client.hset(job_key, mapping=updates)
            logger.debug(
                "queue.job_status_updated",
                job_id=job_id,
                status=status.value
            )
        except Exception as e:
            logger.error(
                "queue.update_status_failed",
                job_id=job_id,
                error=str(e)
            )

    async def get_job(self, job_id: str) -> Optional[Dict]:
        """
        Get job data

        Args:
            job_id: Job ID

        Returns:
            Job data if found, None otherwise
        """
        if not self.redis_client:
            return None

        job_key = f"{self.job_prefix}{job_id}"

        try:
            job_data = await self.redis_client.hgetall(job_key)

            if not job_data:
                return None

            # Parse JSON fields
            for field in ["data", "result"]:
                if field in job_data and job_data[field]:
                    try:
                        job_data[field] = json.loads(job_data[field])
                    except:
                        pass

            return job_data

        except Exception as e:
            logger.error("queue.get_job_failed", job_id=job_id, error=str(e))
            return None

    async def _process_delayed_jobs(self):
        """Move ready delayed jobs to waiting queue"""
        if not self.redis_client:
            return

        try:
            # Get jobs ready to process (score <= current time)
            current_time = time.time()
            ready_jobs = await self.redis_client.zrangebyscore(
                f"{self.queue_name}:delayed",
                min=0,
                max=current_time
            )

            if ready_jobs:
                # Move to waiting queue
                for job_id in ready_jobs:
                    # Get job priority
                    job_key = f"{self.job_prefix}{job_id}"
                    priority = await self.redis_client.hget(job_key, "priority")
                    priority = int(priority) if priority else 0

                    # Add to waiting queue
                    await self.redis_client.zadd(
                        f"{self.queue_name}:waiting",
                        {job_id: -priority}
                    )

                    # Remove from delayed queue
                    await self.redis_client.zrem(
                        f"{self.queue_name}:delayed",
                        job_id
                    )

                    logger.debug(
                        "queue.delayed_job_ready",
                        job_id=job_id
                    )

        except Exception as e:
            logger.error("queue.process_delayed_failed", error=str(e))

    async def get_queue_stats(self) -> Dict:
        """Get queue statistics"""
        if not self.redis_client:
            return {
                "connected": False,
                "waiting": 0,
                "processing": 0,
                "completed": 0,
                "failed": 0,
                "delayed": 0
            }

        try:
            stats = {
                "connected": True,
                "waiting": await self.redis_client.zcard(f"{self.queue_name}:waiting"),
                "processing": await self.redis_client.scard(f"{self.queue_name}:processing"),
                "completed": await self.redis_client.scard(f"{self.queue_name}:completed"),
                "failed": await self.redis_client.scard(f"{self.queue_name}:failed"),
                "delayed": await self.redis_client.zcard(f"{self.queue_name}:delayed")
            }
            return stats
        except:
            return {
                "connected": False,
                "waiting": 0,
                "processing": 0,
                "completed": 0,
                "failed": 0,
                "delayed": 0
            }


# Global queue instance
queue = QuestQueue()