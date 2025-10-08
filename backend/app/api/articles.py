"""
Quest Platform v2.2 - Articles API
Endpoints for article generation and management
"""

from uuid import uuid4
from typing import Literal
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, BackgroundTasks
import structlog

from app.agents.orchestrator import ArticleOrchestrator
from app.core.redis_client import get_redis
from app.core.database import get_db

logger = structlog.get_logger(__name__)

router = APIRouter()

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class ArticleRequest(BaseModel):
    """Request to generate an article"""

    topic: str = Field(..., min_length=10, max_length=200, description="Article topic")
    target_site: Literal["relocation", "placement", "rainmaker"] = Field(
        ..., description="Target site for publication"
    )
    priority: Literal["low", "normal", "high"] = Field(
        default="normal", description="Processing priority"
    )


class ArticleResponse(BaseModel):
    """Response for article generation"""

    job_id: str
    status: str
    poll_url: str
    message: str


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post("/generate", response_model=ArticleResponse)
async def generate_article(
    request: ArticleRequest, background_tasks: BackgroundTasks
):
    """
    Queue article generation job

    Returns immediately with job_id for status polling.
    Actual generation happens in background worker.

    Example:
        POST /api/articles/generate
        {
            "topic": "Portugal digital nomad visa 2025",
            "target_site": "relocation",
            "priority": "high"
        }

    Returns:
        {
            "job_id": "abc123",
            "status": "queued",
            "poll_url": "/api/jobs/abc123",
            "message": "Article generation queued"
        }
    """
    logger.info(
        "api.articles.generate_requested",
        topic=request.topic,
        target_site=request.target_site,
    )

    try:
        # Generate job ID
        job_id = str(uuid4())

        # Insert initial job status in database BEFORE returning
        # This ensures /api/jobs/{job_id} polling works immediately
        pool = get_db()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO job_status (job_id, status, progress, current_step, cost_breakdown, created_at)
                VALUES ($1::varchar(255), $2::varchar(50), $3::integer, $4::varchar(100), $5::jsonb, NOW())
                """,
                job_id,
                "queued",
                0,
                "initializing",
                "{}",  # Empty JSONB object
            )

        # Queue job in Redis (BullMQ simulation)
        redis_client = get_redis()
        job_data = {
            "job_id": job_id,
            "topic": request.topic,
            "target_site": request.target_site,
            "priority": request.priority,
        }

        # Add to queue (in production, use BullMQ properly)
        await redis_client.lpush("quest:jobs:queued", str(job_data))

        # Trigger background processing
        background_tasks.add_task(
            process_article_job,
            job_id,
            request.topic,
            request.target_site,
            request.priority,
        )

        return ArticleResponse(
            job_id=job_id,
            status="queued",
            poll_url=f"/api/jobs/{job_id}",
            message="Article generation queued successfully",
        )

    except Exception as e:
        logger.error("api.articles.generate_failed", error=str(e), exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{article_id}")
async def get_article(article_id: str):
    """
    Get article by ID

    Args:
        article_id: Article UUID

    Returns:
        Article data
    """
    pool = get_db()

    try:
        query = """
            SELECT
                id, title, slug, content, excerpt,
                hero_image_url, target_site, status,
                quality_score, reading_time_minutes,
                keywords, meta_title, meta_description,
                published_date, created_at, updated_at
            FROM articles
            WHERE id = $1
        """

        async with pool.acquire() as conn:
            article = await conn.fetchrow(query, article_id)

            if not article:
                raise HTTPException(status_code=404, detail="Article not found")

            return dict(article)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "api.articles.get_failed", article_id=article_id, error=str(e), exc_info=e
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_articles(
    target_site: str = None,
    status: str = None,
    limit: int = 20,
    offset: int = 0,
):
    """
    List articles with filtering

    Query params:
        target_site: Filter by site (relocation/placement/rainmaker)
        status: Filter by status (draft/review/approved/published)
        limit: Max results (default 20)
        offset: Pagination offset (default 0)

    Returns:
        List of articles
    """
    pool = get_db()

    try:
        # Build dynamic query
        conditions = []
        params = []
        param_count = 0

        if target_site:
            param_count += 1
            conditions.append(f"target_site = ${param_count}")
            params.append(target_site)

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
                id, title, slug, excerpt, hero_image_url,
                target_site, status, quality_score,
                reading_time_minutes, published_date,
                created_at
            FROM articles
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT {limit_param}
            OFFSET {offset_param}
        """

        async with pool.acquire() as conn:
            articles = await conn.fetch(query, *params)
            return [dict(article) for article in articles]

    except Exception as e:
        logger.error("api.articles.list_failed", error=str(e), exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BACKGROUND WORKER FUNCTION
# ============================================================================


async def process_article_job(
    job_id: str, topic: str, target_site: str, priority: str
):
    """
    Background task to process article generation

    In production, this would be handled by a separate worker service.
    """
    logger.info("worker.article_job_started", job_id=job_id, topic=topic)

    try:
        orchestrator = ArticleOrchestrator()
        result = await orchestrator.generate_article(
            topic=topic,
            target_site=target_site,
            job_id=job_id,
            priority=priority,
        )

        logger.info(
            "worker.article_job_completed",
            job_id=job_id,
            article_id=result.get("article_id"),
            status=result.get("status"),
        )

    except Exception as e:
        logger.error("worker.article_job_failed", job_id=job_id, error=str(e), exc_info=e)
