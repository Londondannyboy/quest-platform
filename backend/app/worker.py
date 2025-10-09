"""
BullMQ-compatible Worker for Quest Platform
Background job processor for article generation
"""
import asyncio
import signal
import sys
from typing import Optional

import structlog

from app.core.config import settings
from app.core.queue import queue, JobStatus
from app.core.database import get_db
from app.agents.orchestrator import ArticleOrchestrator

logger = structlog.get_logger()


class QuestWorker:
    """
    Worker process that polls Redis queue and processes article generation jobs
    """

    def __init__(self):
        self.orchestrator = ArticleOrchestrator()
        self.running = False
        self.current_job = None
        self.poll_interval = 5  # seconds

    async def start(self):
        """Start worker process"""
        logger.info("worker.starting", redis_url=settings.REDIS_URL[:30] + "..." if settings.REDIS_URL else "None")

        # Connect to queue
        connected = await queue.connect()
        if not connected:
            logger.error("worker.queue_connection_failed")
            # Continue anyway - API can still use background tasks
            logger.info("worker.running_without_queue")

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

        self.running = True
        logger.info("worker.ready")

        # Main worker loop
        while self.running:
            try:
                # Get next job from queue
                job = await queue.dequeue()

                if job:
                    self.current_job = job
                    await self._process_job(job)
                    self.current_job = None
                else:
                    # No jobs available, wait before polling again
                    await asyncio.sleep(self.poll_interval)

            except Exception as e:
                logger.error(
                    "worker.loop_error",
                    error=str(e),
                    exc_info=True
                )
                await asyncio.sleep(self.poll_interval)

        # Cleanup on shutdown
        await self._shutdown()

    async def _process_job(self, job: dict):
        """
        Process a single job

        Args:
            job: Job data from queue
        """
        job_id = job.get("id")
        job_type = job.get("type")
        job_data = job.get("data", {})

        logger.info(
            "worker.processing_job",
            job_id=job_id,
            job_type=job_type
        )

        try:
            if job_type == "generate_article":
                await self._process_article_generation(job_id, job_data)
            else:
                logger.warning(
                    "worker.unknown_job_type",
                    job_id=job_id,
                    job_type=job_type
                )
                await queue.fail_job(job_id, f"Unknown job type: {job_type}")

        except Exception as e:
            logger.error(
                "worker.job_processing_failed",
                job_id=job_id,
                error=str(e),
                exc_info=True
            )
            await queue.fail_job(job_id, str(e))

    async def _process_article_generation(self, job_id: str, data: dict):
        """
        Process article generation job

        Args:
            job_id: Job ID
            data: Job data containing topic, target_site, etc.
        """
        topic = data.get("topic")
        target_site = data.get("target_site", "relocation")
        priority = data.get("priority", 0)

        logger.info(
            "worker.generating_article",
            job_id=job_id,
            topic=topic,
            target_site=target_site
        )

        try:
            # Generate article using orchestrator
            result = await self.orchestrator.generate_article(
                topic=topic,
                target_site=target_site,
                job_id=job_id,
                priority=priority
            )

            # Mark job as completed
            await queue.complete_job(job_id, result)

            # Update job status in database
            pool = get_db()
            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    UPDATE job_status
                    SET status = $1, updated_at = NOW()
                    WHERE job_id = $2
                    """,
                    "completed",
                    job_id
                )

            logger.info(
                "worker.article_generated",
                job_id=job_id,
                article_id=result.get("article_id"),
                total_cost=result.get("total_cost")
            )

        except Exception as e:
            logger.error(
                "worker.article_generation_failed",
                job_id=job_id,
                topic=topic,
                error=str(e)
            )

            # Update job status in database
            pool = get_db()
            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    UPDATE job_status
                    SET status = $1, error_message = $2, updated_at = NOW()
                    WHERE job_id = $3
                    """,
                    "failed",
                    str(e),
                    job_id
                )

            raise

    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signal"""
        logger.info(
            "worker.shutdown_signal_received",
            signal=signum
        )
        self.running = False

    async def _shutdown(self):
        """Graceful shutdown"""
        logger.info("worker.shutting_down")

        # Wait for current job to complete (max 30 seconds)
        if self.current_job:
            logger.info(
                "worker.waiting_for_current_job",
                job_id=self.current_job.get("id")
            )
            for _ in range(30):
                if not self.current_job:
                    break
                await asyncio.sleep(1)

        # Disconnect from queue
        await queue.disconnect()

        logger.info("worker.shutdown_complete")


async def main():
    """Main worker entry point"""
    worker = QuestWorker()
    await worker.start()


if __name__ == "__main__":
    # Set up logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Run worker
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("worker.interrupted")
        sys.exit(0)
    except Exception as e:
        logger.error("worker.fatal_error", error=str(e), exc_info=True)
        sys.exit(1)