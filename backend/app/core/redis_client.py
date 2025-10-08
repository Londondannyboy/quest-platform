"""
Quest Platform v2.2 - Redis Client
Connection management for BullMQ queue and caching
"""

import redis.asyncio as redis
from typing import Optional
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Global Redis client
_redis_client: Optional[redis.Redis] = None


async def init_redis() -> redis.Redis:
    """
    Initialize Redis connection
    """
    global _redis_client

    if _redis_client is not None:
        logger.warning("quest.redis.already_initialized")
        return _redis_client

    try:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            ssl_cert_reqs=None,  # Upstash Redis requires SSL but no cert verification
        )

        # Test connection
        await _redis_client.ping()
        logger.info("quest.redis.connected")

        return _redis_client

    except Exception as e:
        logger.error("quest.redis.connection_failed", error=str(e), exc_info=e)
        raise


async def close_redis():
    """
    Close Redis connection
    """
    global _redis_client

    if _redis_client is None:
        return

    try:
        await _redis_client.close()
        logger.info("quest.redis.closed")
        _redis_client = None
    except Exception as e:
        logger.error("quest.redis.close_failed", error=str(e), exc_info=e)


def get_redis() -> redis.Redis:
    """
    Get Redis client

    Raises:
        RuntimeError: If Redis not initialized
    """
    if _redis_client is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return _redis_client
