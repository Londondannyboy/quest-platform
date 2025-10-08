"""
Quest Platform v2.2 - Article Generation Orchestrator
Coordinates 4-agent pipeline with cost tracking and error handling
"""

import asyncio
from decimal import Decimal
from typing import Dict, Literal
from uuid import uuid4

import structlog

from app.core.config import settings
from app.core.database import get_db
from app.agents.research import ResearchAgent
from app.agents.content import ContentAgent
from app.agents.editor import EditorAgent
from app.agents.image import ImageAgent

logger = structlog.get_logger(__name__)

TargetSite = Literal["relocation", "placement", "rainmaker"]


class ArticleOrchestrator:
    """
    Orchestrates the 4-agent pipeline for article generation

    Pipeline:
    1. ResearchAgent (30-60s) → Gather intelligence
    2. ContentAgent (60-90s) → Generate article
    3. EditorAgent (20-30s) → Score quality
    4. ImageAgent (60s, parallel) → Generate hero image

    Total: 2-3 minutes per article
    """

    def __init__(self):
        self.research_agent = ResearchAgent()
        self.content_agent = ContentAgent()
        self.editor_agent = EditorAgent()
        self.image_agent = ImageAgent()

    async def generate_article(
        self,
        topic: str,
        target_site: TargetSite,
        job_id: str,
        priority: str = "normal",
    ) -> Dict:
        """
        Full article generation pipeline

        Args:
            topic: Article topic
            target_site: Target site (relocation/placement/rainmaker)
            job_id: Job ID for tracking
            priority: Priority level (low/normal/high)

        Returns:
            Dict with article ID and metadata
        """
        logger.info(
            "orchestrator.start",
            topic=topic,
            target_site=target_site,
            job_id=job_id,
        )

        # Initialize cost tracking
        costs = {
            "research": Decimal("0.00"),
            "content": Decimal("0.00"),
            "editor": Decimal("0.00"),
            "image": Decimal("0.00"),
        }

        try:
            # Update job status
            await self._update_job_status(
                job_id, "processing", 10, "research"
            )

            # STEP 1: Research (30-60s)
            research_result = await self.research_agent.run(topic)
            costs["research"] = research_result["cost"]

            await self._update_job_status(
                job_id, "processing", 30, "content"
            )

            # STEP 2: Content Generation (60-90s)
            content_result = await self.content_agent.run(
                research_result["research"], target_site, topic
            )
            costs["content"] = content_result["cost"]

            await self._update_job_status(
                job_id, "processing", 60, "editor"
            )

            # STEP 3: Quality Scoring (20-30s)
            editor_result = await self.editor_agent.score(
                content_result["article"]
            )
            costs["editor"] = editor_result["cost"]

            # Check cost cap
            total_cost = sum(costs.values())
            if (
                settings.ENABLE_COST_CIRCUIT_BREAKER
                and total_cost > settings.PER_JOB_COST_CAP
            ):
                logger.error(
                    "orchestrator.cost_cap_exceeded",
                    job_id=job_id,
                    total_cost=float(total_cost),
                    cap=float(settings.PER_JOB_COST_CAP),
                )
                raise Exception(
                    f"Cost cap exceeded: ${total_cost} > ${settings.PER_JOB_COST_CAP}"
                )

            # Decision based on quality score
            decision = editor_result["decision"]
            quality_score = editor_result["quality_score"]

            if decision == "reject":
                logger.warning(
                    "orchestrator.article_rejected",
                    job_id=job_id,
                    quality_score=quality_score,
                )
                await self._update_job_status(
                    job_id,
                    "failed",
                    100,
                    "completed",
                    error_message=f"Quality score too low: {quality_score}",
                )
                return {
                    "status": "rejected",
                    "quality_score": quality_score,
                    "reason": editor_result["feedback"],
                    "costs": costs,
                }

            # Create article in database
            article_id = await self._create_article(
                content_result["article"],
                target_site,
                quality_score,
                editor_result["feedback"],
                status="review" if decision == "review" else "approved",
            )

            await self._update_job_status(
                job_id, "processing", 90, "image", article_id=article_id
            )

            # STEP 4: Image Generation (parallel, non-blocking for high-quality only)
            if decision == "publish" and settings.ENABLE_IMAGE_GENERATION:
                # High quality - auto-publish with image
                image_result = await self.image_agent.generate(
                    content_result["article"],
                    target_site,
                    content_result["article"]["title"]
                    .lower()
                    .replace(" ", "-")[:50],
                )
                costs["image"] = image_result["cost"]

                # Update article with image
                if image_result["hero_image_url"]:
                    await self._update_article_image(
                        article_id, image_result["hero_image_url"]
                    )

                # Auto-publish
                if settings.ENABLE_AUTO_PUBLISH:
                    await self._publish_article(article_id)
                    final_status = "published"
                else:
                    final_status = "approved"

            else:
                # Medium quality - human review required
                final_status = "review"

            # Update job as completed
            total_cost = sum(costs.values())
            await self._update_job_status(
                job_id,
                "completed",
                100,
                "completed",
                article_id=article_id,
                cost_breakdown=costs,
                total_cost=total_cost,
            )

            logger.info(
                "orchestrator.complete",
                job_id=job_id,
                article_id=article_id,
                quality_score=quality_score,
                decision=decision,
                total_cost=float(total_cost),
            )

            return {
                "status": "success",
                "article_id": article_id,
                "article_status": final_status,
                "quality_score": quality_score,
                "decision": decision,
                "costs": {k: float(v) for k, v in costs.items()},
                "total_cost": float(total_cost),
            }

        except Exception as e:
            logger.error(
                "orchestrator.failed",
                job_id=job_id,
                error=str(e),
                exc_info=e,
            )

            await self._update_job_status(
                job_id,
                "failed",
                0,
                "error",
                error_message=str(e),
            )

            raise

    async def _update_job_status(
        self,
        job_id: str,
        status: str,
        progress: int,
        current_step: str,
        article_id: str = None,
        cost_breakdown: Dict = None,
        total_cost: Decimal = None,
        error_message: str = None,
    ):
        """
        Update job status in database
        """
        pool = get_db()

        try:
            query = """
                INSERT INTO job_status
                (job_id, status, progress, current_step, article_id, cost_breakdown, total_cost, error_message, started_at, completed_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8,
                        CASE WHEN $2 = 'processing' THEN NOW() ELSE NULL END,
                        CASE WHEN $2 IN ('completed', 'failed') THEN NOW() ELSE NULL END)
                ON CONFLICT (job_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    progress = EXCLUDED.progress,
                    current_step = EXCLUDED.current_step,
                    article_id = COALESCE(EXCLUDED.article_id, job_status.article_id),
                    cost_breakdown = COALESCE(EXCLUDED.cost_breakdown, job_status.cost_breakdown),
                    total_cost = COALESCE(EXCLUDED.total_cost, job_status.total_cost),
                    error_message = EXCLUDED.error_message,
                    started_at = COALESCE(job_status.started_at, EXCLUDED.started_at),
                    completed_at = EXCLUDED.completed_at
            """

            cost_json = (
                {k: str(v) for k, v in cost_breakdown.items()}
                if cost_breakdown
                else None
            )

            async with pool.acquire() as conn:
                await conn.execute(
                    query,
                    job_id,
                    status,
                    progress,
                    current_step,
                    article_id,
                    cost_json,
                    total_cost,
                    error_message,
                )

        except Exception as e:
            logger.error(
                "orchestrator.job_update_failed",
                job_id=job_id,
                error=str(e),
                exc_info=e,
            )

    async def _create_article(
        self,
        article_data: Dict,
        target_site: str,
        quality_score: int,
        editor_feedback: str,
        status: str = "draft",
    ) -> str:
        """
        Create article in database

        Returns:
            Article UUID
        """
        pool = get_db()

        try:
            query = """
                INSERT INTO articles
                (title, slug, content, excerpt, target_site, status, quality_score,
                 keywords, meta_title, meta_description, reading_time_minutes)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING id
            """

            async with pool.acquire() as conn:
                article_id = await conn.fetchval(
                    query,
                    article_data.get("title"),
                    article_data.get("title", "")
                    .lower()
                    .replace(" ", "-")[:100],
                    article_data.get("content"),
                    article_data.get("excerpt"),
                    target_site,
                    status,
                    quality_score,
                    article_data.get("keywords", []),
                    article_data.get("meta_title"),
                    article_data.get("meta_description"),
                    article_data.get("reading_time_minutes"),
                )

            logger.info(
                "orchestrator.article_created",
                article_id=article_id,
                title=article_data.get("title"),
            )

            return str(article_id)

        except Exception as e:
            logger.error(
                "orchestrator.article_creation_failed",
                error=str(e),
                exc_info=e,
            )
            raise

    async def _update_article_image(self, article_id: str, image_url: str):
        """
        Update article with hero image URL
        """
        pool = get_db()

        try:
            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    UPDATE articles
                    SET hero_image_url = $1
                    WHERE id = $2
                    """,
                    image_url,
                    article_id,
                )

            logger.info(
                "orchestrator.image_updated",
                article_id=article_id,
                image_url=image_url[:50],
            )

        except Exception as e:
            logger.error(
                "orchestrator.image_update_failed",
                error=str(e),
                exc_info=e,
            )

    async def _publish_article(self, article_id: str):
        """
        Publish article (set status to published and published_date)
        """
        pool = get_db()

        try:
            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    UPDATE articles
                    SET status = 'published',
                        published_date = NOW()
                    WHERE id = $1
                    """,
                    article_id,
                )

            logger.info("orchestrator.article_published", article_id=article_id)

        except Exception as e:
            logger.error(
                "orchestrator.publish_failed",
                error=str(e),
                exc_info=e,
            )
