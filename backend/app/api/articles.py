"""
Quest Platform v2.2 - Articles API
Endpoints for article generation and management
"""

from uuid import uuid4
from typing import Literal, Dict, Any, Optional
import json
import re
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, BackgroundTasks
import structlog

from app.agents.orchestrator import ArticleOrchestrator
from app.core.redis_client import get_redis
from app.core.database import get_db
from app.core.queue import queue

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

        # Add job to proper queue
        priority_value = {"low": -1, "normal": 0, "high": 1}.get(request.priority, 0)

        queue_job_id = await queue.enqueue(
            job_type="generate_article",
            data={
                "topic": request.topic,
                "target_site": request.target_site,
                "priority": priority_value,
            },
            priority=priority_value,
            job_id=job_id  # Pass the external job_id
        )

        # If queue is not available, fall back to background task
        if not queue_job_id:
            logger.warning(
                "api.articles.queue_unavailable",
                job_id=job_id,
                topic=request.topic
            )
            # Fall back to background task processing
            background_tasks.add_task(
                process_article_job,
                job_id,
                request.topic,
                request.target_site,
                request.priority,
            )
        else:
            # Update job_status with queue ID
            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    UPDATE job_status
                    SET status = 'queued', updated_at = NOW()
                    WHERE job_id = $1
                    """,
                    job_id
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


def _serialize_article(row) -> Dict[str, Any]:
    """
    Convert an asyncpg row to a standard dict and normalise content/images.
    """
    article = dict(row)

    raw_content = article.get("content")
    structured = None

    if isinstance(raw_content, str):
        structured = _load_structured_content(raw_content)

    if isinstance(structured, dict):
        article["content_structured"] = structured

        markdown = structured.get("content")
        if isinstance(markdown, str):
            article["content"] = markdown

        article.setdefault("excerpt", structured.get("excerpt"))
        article.setdefault("meta_title", structured.get("meta_title"))
        article.setdefault("meta_description", structured.get("meta_description"))

        keywords = structured.get("keywords")
        if keywords and not article.get("keywords"):
            article["keywords"] = keywords

        # Populate image URLs if the structured payload contains them.
        content_images = structured.get("content_images") or []
        for idx, field in enumerate(
            ("content_image_1_url", "content_image_2_url", "content_image_3_url")
        ):
            if not article.get(field) and idx < len(content_images):
                article[field] = content_images[idx]

        hero_image = structured.get("hero_image_url")
        if hero_image and not article.get("hero_image_url"):
            article["hero_image_url"] = hero_image

    return article


def _load_structured_content(raw_content: str) -> Optional[Dict[str, Any]]:
    """
    Attempt to load structured JSON content, handling partially truncated blobs.
    """
    stripped = raw_content.strip()

    if not stripped.startswith("{"):
        return None

    # First, try normal JSON parsing.
    try:
        parsed = json.loads(stripped)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        parsed = None

    # Fallback: extract known fields via regex from malformed JSON strings.
    pattern_content = re.compile(
        r'"content"\s*:\s*"(.*?)"(?:\s*,\s*[\r\n]?\s*"\w+"|\s*}$)',
        re.DOTALL,
    )
    match = pattern_content.search(stripped)

    if not match:
        return None

    def decode_fragment(fragment: str) -> str:
        try:
            return json.loads(f'"{fragment}"')
        except json.JSONDecodeError:
            return bytes(fragment, "utf-8").decode("unicode_escape", "ignore")

    structured: Dict[str, Any] = {
        "content": decode_fragment(match.group(1))
    }

    # Optional string fields we care about.
    optional_keys = (
        "title",
        "tldr",
        "excerpt",
        "meta_title",
        "meta_description",
        "author_bio",
    )
    for key in optional_keys:
        key_match = re.search(rf'"{key}"\s*:\s*"(.*?)"', stripped, re.DOTALL)
        if key_match:
            structured[key] = decode_fragment(key_match.group(1))

    # Keywords array.
    keywords_match = re.search(r'"keywords"\s*:\s*(\[[^\]]*\])', stripped, re.DOTALL)
    if keywords_match:
        try:
            structured["keywords"] = json.loads(keywords_match.group(1))
        except json.JSONDecodeError:
            pass

    # Hero image + content images.
    hero_match = re.search(r'"hero_image_url"\s*:\s*"(.*?)"', stripped)
    if hero_match:
        structured["hero_image_url"] = decode_fragment(hero_match.group(1))

    content_images = []
    for idx in range(1, 4):
        img_match = re.search(
            rf'"content_image_{idx}_url"\s*:\s*"(.*?)"', stripped
        )
        if img_match:
            content_images.append(decode_fragment(img_match.group(1)))
    if content_images:
        structured["content_images"] = content_images

    return structured


@router.get("/by-slug/{slug}")
async def get_article_by_slug(slug: str):
    """
    Get article by slug (for frontend routing)

    Args:
        slug: Article slug (URL-friendly identifier)

    Returns:
        Article data
    """
    pool = get_db()

    try:
        query = """
            SELECT
                id, title, slug, content, excerpt,
                hero_image_url, content_image_1_url, content_image_2_url, content_image_3_url,
                target_site, status,
                quality_score, reading_time_minutes,
                keywords, meta_title, meta_description,
                published_date, created_at, updated_at
            FROM articles
            WHERE slug = $1
        """

        async with pool.acquire() as conn:
            article = await conn.fetchrow(query, slug)

            if not article:
                raise HTTPException(status_code=404, detail="Article not found")

            return _serialize_article(article)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "api.articles.get_by_slug_failed", slug=slug, error=str(e), exc_info=e
        )
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
                hero_image_url, content_image_1_url, content_image_2_url, content_image_3_url,
                target_site, status,
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

            return _serialize_article(article)

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
                content_image_1_url, content_image_2_url, content_image_3_url,
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
            serialized = [_serialize_article(article) for article in articles]
            return {"articles": serialized}

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
