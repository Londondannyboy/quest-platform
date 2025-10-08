"""
Quest Platform v2.2 - Health Check API
System health and monitoring endpoints
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict
import structlog

from app.core.database import get_db
from app.core.redis_client import get_redis
from app.core.config import settings

logger = structlog.get_logger(__name__)

router = APIRouter()


# ============================================================================
# RESPONSE MODELS
# ============================================================================


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    version: str
    environment: str
    checks: Dict[str, str]


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    System health check

    Checks:
    - API status
    - Database connectivity
    - Redis connectivity
    - Queue depth

    Returns 200 if all healthy, 503 if any service unhealthy
    """
    checks = {
        "api": "healthy",
        "database": await check_database(),
        "redis": await check_redis(),
        "queue": await check_queue_depth(),
    }

    all_healthy = all(v == "healthy" for v in checks.values())
    status_code = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if all_healthy else "unhealthy",
            "version": "2.2.0",
            "environment": settings.APP_ENV,
            "checks": checks,
        },
    )


@router.get("/metrics")
async def get_metrics():
    """
    System metrics for monitoring

    Returns:
        - Queue depth
        - Recent job stats
        - Cost metrics
        - Cache performance
    """
    try:
        pool = get_db()

        async with pool.acquire() as conn:
            # Queue depth (from Redis)
            redis_client = get_redis()
            queue_depth = await redis_client.llen("quest:jobs:queued")

            # Recent job stats (last 24 hours)
            job_stats = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) as total_jobs,
                    COUNT(*) FILTER (WHERE status = 'completed') as completed,
                    COUNT(*) FILTER (WHERE status = 'failed') as failed,
                    COUNT(*) FILTER (WHERE status = 'processing') as processing,
                    AVG(total_cost) as avg_cost
                FROM job_status
                WHERE created_at > NOW() - INTERVAL '24 hours'
                """
            )

            # Cache performance (last 24 hours)
            cache_stats = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) as cache_entries,
                    SUM(cache_hits) as total_hits,
                    AVG(cache_hits) as avg_hits_per_entry
                FROM article_research
                WHERE last_accessed > NOW() - INTERVAL '24 hours'
                """
            )

            # Daily cost (today)
            daily_cost = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) as articles_today,
                    SUM(total_cost) as total_cost_today,
                    AVG(total_cost) as avg_cost_per_article
                FROM job_status
                WHERE status = 'completed'
                AND DATE(created_at) = CURRENT_DATE
                """
            )

            return {
                "queue": {
                    "depth": queue_depth,
                },
                "jobs_24h": {
                    "total": job_stats["total_jobs"],
                    "completed": job_stats["completed"],
                    "failed": job_stats["failed"],
                    "processing": job_stats["processing"],
                    "avg_cost": float(job_stats["avg_cost"] or 0),
                },
                "cache_24h": {
                    "entries": cache_stats["cache_entries"],
                    "total_hits": cache_stats["total_hits"],
                    "avg_hits": float(cache_stats["avg_hits_per_entry"] or 0),
                },
                "today": {
                    "articles": daily_cost["articles_today"],
                    "total_cost": float(daily_cost["total_cost_today"] or 0),
                    "avg_cost": float(daily_cost["avg_cost_per_article"] or 0),
                },
            }

    except Exception as e:
        logger.error("api.health.metrics_failed", error=str(e), exc_info=e)
        return {"error": str(e)}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


async def check_database() -> str:
    """Check database connectivity"""
    try:
        pool = get_db()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return "healthy"
    except Exception as e:
        logger.error("health.database_check_failed", error=str(e))
        return "unhealthy"


async def check_redis() -> str:
    """Check Redis connectivity"""
    try:
        redis_client = get_redis()
        await redis_client.ping()
        return "healthy"
    except Exception as e:
        logger.error("health.redis_check_failed", error=str(e))
        return "unhealthy"


async def check_queue_depth() -> str:
    """Check queue depth (warn if >100)"""
    try:
        redis_client = get_redis()
        depth = await redis_client.llen("quest:jobs:queued")

        if depth > 100:
            return f"warning: {depth} jobs queued"
        return "healthy"
    except Exception as e:
        logger.error("health.queue_check_failed", error=str(e))
        return "unhealthy"
