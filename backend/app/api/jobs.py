"""
Quest Platform v2.2 - Jobs API
Endpoints for job status tracking and management
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import structlog

from app.core.database import get_db

logger = structlog.get_logger(__name__)

router = APIRouter()


# ============================================================================
# RESPONSE MODELS
# ============================================================================


class JobStatusResponse(BaseModel):
    """Job status response"""

    job_id: str
    status: str
    progress: int
    current_step: str
    article_id: Optional[str] = None
    cost_breakdown: Optional[dict] = None
    total_cost: Optional[float] = None
    error_message: Optional[str] = None
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get job status by ID

    Used for polling article generation progress.

    Example:
        GET /api/jobs/abc123

    Returns:
        {
            "job_id": "abc123",
            "status": "processing",
            "progress": 60,
            "current_step": "editor",
            "article_id": null,
            "created_at": "2025-10-07T10:30:00Z"
        }
    """
    pool = get_db()

    try:
        query = """
            SELECT
                job_id, status, progress, current_step,
                article_id, cost_breakdown, total_cost,
                error_message, created_at, started_at, completed_at
            FROM job_status
            WHERE job_id = $1
        """

        async with pool.acquire() as conn:
            job = await conn.fetchrow(query, job_id)

            if not job:
                raise HTTPException(status_code=404, detail="Job not found")

            return JobStatusResponse(
                job_id=job["job_id"],
                status=job["status"],
                progress=job["progress"],
                current_step=job["current_step"],
                article_id=str(job["article_id"]) if job["article_id"] else None,
                cost_breakdown=job["cost_breakdown"],
                total_cost=float(job["total_cost"]) if job["total_cost"] else None,
                error_message=job["error_message"],
                created_at=job["created_at"].isoformat(),
                started_at=job["started_at"].isoformat() if job["started_at"] else None,
                completed_at=job["completed_at"].isoformat()
                if job["completed_at"]
                else None,
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("api.jobs.get_failed", job_id=job_id, error=str(e), exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_jobs(status: str = None, limit: int = 50, offset: int = 0):
    """
    List recent jobs

    Query params:
        status: Filter by status (queued/processing/completed/failed)
        limit: Max results (default 50)
        offset: Pagination offset (default 0)

    Returns:
        List of jobs
    """
    pool = get_db()

    try:
        conditions = []
        params = []
        param_count = 0

        if status:
            param_count += 1
            conditions.append(f"status = ${param_count}")
            params.append(status)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        param_count += 1
        limit_param = f"${param_count}"
        params.append(limit)

        param_count += 1
        offset_param = f"${param_count}"
        params.append(offset)

        query = f"""
            SELECT
                job_id, status, progress, current_step,
                article_id, total_cost, error_message,
                created_at, completed_at
            FROM job_status
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT {limit_param}
            OFFSET {offset_param}
        """

        async with pool.acquire() as conn:
            jobs = await conn.fetch(query, *params)

            return [
                {
                    "job_id": job["job_id"],
                    "status": job["status"],
                    "progress": job["progress"],
                    "current_step": job["current_step"],
                    "article_id": str(job["article_id"]) if job["article_id"] else None,
                    "total_cost": float(job["total_cost"]) if job["total_cost"] else None,
                    "error_message": job["error_message"],
                    "created_at": job["created_at"].isoformat(),
                    "completed_at": job["completed_at"].isoformat()
                    if job["completed_at"]
                    else None,
                }
                for job in jobs
            ]

    except Exception as e:
        logger.error("api.jobs.list_failed", error=str(e), exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))
