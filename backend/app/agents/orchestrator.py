"""
Quest Platform v2.2 - Article Generation Orchestrator
Coordinates 4-agent pipeline with cost tracking and error handling
"""

import asyncio
import json
from decimal import Decimal
from typing import Dict, Literal
from uuid import uuid4

import structlog

from app.core.config import settings
from app.core.database import get_db
from app.agents.keyword_researcher import KeywordResearcher
from app.agents.template_detector import TemplateDetector
from app.agents.research import ResearchAgent
from app.agents.gemini_summarizer import GeminiSummarizer
from app.agents.content import ContentAgent
from app.agents.chunked_content import ChunkedContentAgent
from app.agents.editor import EditorAgent
from app.agents.citation_verifier import CitationVerifierAgent
from app.agents.image import ImageAgent
from app.core.link_validator import LinkValidator

logger = structlog.get_logger(__name__)

TargetSite = Literal["relocation", "placement", "rainmaker"]


def detect_content_type(topic: str) -> str:
    """
    Detect content type from topic string.

    Examples:
        "Italy vs Spain Digital Nomad Visa" → comparison
        "Top 10 Cities for Remote Work" → listicle
        "Complete Guide to Portugal D7 Visa" → guide
        "Tax Implications of NHR Status" → deep-dive

    Args:
        topic: Article topic string

    Returns:
        Content type (guide, comparison, listicle, deep-dive, etc.)
    """
    topic_lower = topic.lower()

    # Comparison indicators
    if ' vs ' in topic_lower or ' versus ' in topic_lower:
        return 'comparison'

    # Listicle indicators
    if re.match(r'(top|best) \d+', topic_lower):
        return 'listicle'

    # Deep dive indicators
    if any(word in topic_lower for word in ['implications', 'analysis', 'breakdown']):
        return 'deep-dive'

    # Default to guide
    return 'guide'


def extract_country(topic: str, title: str = None) -> str:
    """
    Extract country name from topic or title.

    Args:
        topic: Article topic
        title: Article title (optional)

    Returns:
        Country name in lowercase or None
    """
    text = (topic + " " + (title or "")).lower()

    # Country detection patterns
    countries = [
        'portugal', 'spain', 'italy', 'germany', 'france',
        'croatia', 'greece', 'iceland', 'netherlands', 'estonia',
        'czech republic', 'poland', 'malta', 'cyprus', 'ireland'
    ]

    for country in countries:
        if country in text:
            return country

    return None


def generate_url_slug(
    title: str,
    content_type: str,
    target_site: str,
    country: str = None
) -> str:
    """
    Generate SEO-friendly URL slug with site and content type prefixes.

    URL Structure: {site}/{content_type}/{country?}/{slug}

    Examples:
        relocation.quest:
            - guide + "Italy Digital Nomad Visa" → relocation/guide/italy-digital-nomad-visa
            - comparison + "Spain vs Portugal" → relocation/comparison/spain-vs-portugal-digital-nomad-visa

        placement.quest:
            - guide + country="germany" → placement/guide/germany/tech-job-market
            - market + country="germany" → placement/market/germany/tech-salaries-2025

    Args:
        title: Article title
        content_type: Content type (guide, comparison, etc.)
        target_site: Target site (relocation, placement, rainmaker)
        country: Optional country for location-specific content

    Returns:
        Full slug with site and content type prefixes
    """
    import re

    # Sanitize title (remove punctuation, lowercase, hyphens)
    base_slug = re.sub(r'[^a-z0-9\s-]', '', title.lower())
    base_slug = re.sub(r'\s+', '-', base_slug).strip('-')[:100]

    # Build URL path with site prefix
    if target_site == 'placement' and country:
        # placement.quest includes country in path
        return f"{target_site}/{content_type}/{country}/{base_slug}"
    else:
        # relocation.quest and rainmaker.quest don't include country
        return f"{target_site}/{content_type}/{base_slug}"


class ArticleOrchestrator:
    """
    Orchestrates the Template Intelligence pipeline for SERP-competitive article generation

    Pipeline (v2.5 - Template Intelligence):
    0. KeywordResearcher (20-30s) → Identify & validate keywords with DataForSEO
    0.5. TemplateDetector (10-20s) → Analyze SERP winners, detect archetype/template
    1. ResearchAgent (30-60s) → Gather intelligence from 6 APIs
    1.5. LinkValidator → Validate external links, suggest internal links
    2. ContentAgent (60-90s) → Generate archetype-specific content with E-E-A-T
    3. EditorAgent (20-30s) → Score quality & E-E-A-T compliance
    4. ImageAgent (60s, parallel) → Generate 4 specialized images
    5. PerformanceTracker → Store archetype/template metrics for learning

    Total: 2.5-3.5 minutes per article
    Cost: ~$0.68-$0.90 per article (Template Intelligence + all APIs)
    Cost (cached): ~$0.60 per article (50%+ cache hit rate)
    """

    def __init__(self):
        self.keyword_researcher = KeywordResearcher()
        self.template_detector = TemplateDetector()
        self.research_agent = ResearchAgent()
        self.gemini_summarizer = GeminiSummarizer()
        self.content_agent = ContentAgent()
        self.chunked_content_agent = ChunkedContentAgent() if settings.GEMINI_API_KEY else None
        self.editor_agent = EditorAgent()
        self.citation_verifier = CitationVerifierAgent()
        self.image_agent = ImageAgent()
        self.link_validator = LinkValidator()

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
            "keyword_research": Decimal("0.00"),
            "template_detection": Decimal("0.00"),
            "research": Decimal("0.00"),
            "gemini_compression": Decimal("0.00"),
            "content": Decimal("0.00"),
            "editor": Decimal("0.00"),  # Includes refinement if triggered
            "citation_verification": Decimal("0.00"),
            "image": Decimal("0.00"),
        }

        try:
            # STEP 0: Keyword Research (20-30s) - NEW!
            await self._update_job_status(
                job_id, "processing", 5, "keyword_research"
            )

            keyword_result = await self.keyword_researcher.research_keywords(
                topic, target_site
            )
            costs["keyword_research"] = keyword_result["cost"]

            # Extract SEO data for content optimization
            seo_data = {
                "primary_keyword": keyword_result["primary_keyword"],
                "secondary_keywords": keyword_result["secondary_keywords"],
                "search_volume": keyword_result["seo_metrics"].get("search_volume", 0),
                "competition": keyword_result["seo_metrics"].get("competition", "unknown"),
                "cpc": keyword_result["seo_metrics"].get("cpc", 0),
            }

            logger.info(
                "orchestrator.keywords_identified",
                primary=seo_data["primary_keyword"],
                volume=seo_data["search_volume"],
                competition=seo_data["competition"]
            )

            # STEP 0.5: Template Intelligence - SERP Analysis (10-20s) - NEW!
            await self._update_job_status(
                job_id, "processing", 10, "template_detection"
            )

            # Use primary keyword for SERP analysis
            template_guidance = await self.template_detector.run(
                keyword=seo_data["primary_keyword"],
                use_cache=True,
                max_competitors=3
            )
            costs["template_detection"] = template_guidance.get("cost", Decimal("0.00"))

            logger.info(
                "orchestrator.template_detected",
                archetype=template_guidance.get("detected_archetype"),
                template=template_guidance.get("recommended_template"),
                confidence=template_guidance.get("confidence_score"),
                target_words=template_guidance.get("target_word_count"),
                from_cache=template_guidance.get("from_cache", False)
            )

            # STEP 1: Research (30-60s)
            await self._update_job_status(
                job_id, "processing", 15, "research"
            )

            research_result = await self.research_agent.run(topic)
            costs["research"] = research_result["cost"]

            # STEP 1.25: Gemini Research Compression (NEW - 5-10s)
            # Compress massive research data into high-signal summary
            await self._update_job_status(
                job_id, "processing", 20, "gemini_compression"
            )

            gemini_result = await self.gemini_summarizer.compress_research(
                research_result.get("research", {}),
                topic,
                target_site
            )
            costs["gemini_compression"] = gemini_result["cost"]

            # Use compressed research for content generation (saves 90% on input tokens!)
            compressed_research = gemini_result["compressed_research"]

            logger.info(
                "orchestrator.research_compressed",
                compression_ratio=f"{gemini_result['compression_ratio']:.2%}",
                gemini_cost=float(gemini_result["cost"]),
                input_tokens_saved=gemini_result["tokens"]["input"]
            )

            # STEP 1.5: Link Validation (Option 3 - Pre-generation)
            sources = research_result.get("sources", [])
            link_context = await self.link_validator.prepare_link_context(
                topic, sources
            )

            # Add SEO data to link context for content generation
            link_context["seo_data"] = seo_data

            await self._update_job_status(
                job_id, "processing", 35, "content"
            )

            # STEP 2: Content Generation (60-90s)
            # Use chunked generation (Gemini 2.5 Pro + Sonnet) if enabled, otherwise single-shot Sonnet
            if settings.ENABLE_CHUNKED_CONTENT and self.chunked_content_agent:
                logger.info(
                    "orchestrator.using_chunked_content",
                    job_id=job_id,
                    reason="ENABLE_CHUNKED_CONTENT=True - Gemini 2.5 Pro chunks + Sonnet refinement"
                )
                content_result = await self.chunked_content_agent.generate(
                    {"content": compressed_research},
                    target_site,
                    topic,
                    link_context=link_context,
                    template_guidance=template_guidance
                )
            else:
                logger.info(
                    "orchestrator.using_single_shot_content",
                    job_id=job_id,
                    reason="ENABLE_CHUNKED_CONTENT=False or no Gemini API key - Single-shot Sonnet"
                )
                content_result = await self.content_agent.run(
                    {"content": compressed_research},  # Use Gemini-compressed research (90% fewer input tokens!)
                    target_site,
                    topic,
                    link_context=link_context,  # Pass validated links + SEO data
                    template_guidance=template_guidance  # Pass Template Intelligence recommendations
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

            # Check cost cap before potential refinement
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

            # STEP 3.5: Article Refinement (NEW - if score 60-74)
            # Trigger refinement for medium-quality articles
            if 60 <= quality_score < 75:
                # Store original score before refinement for improvement tracking
                original_quality_score = quality_score

                logger.info(
                    "orchestrator.triggering_refinement",
                    job_id=job_id,
                    quality_score=quality_score,
                    reason="Medium quality score - attempting improvement"
                )

                await self._update_job_status(
                    job_id, "processing", 70, "refinement"
                )

                try:
                    # Refine the article
                    refinement_result = await self.editor_agent.refine(
                        article=content_result["article"],
                        feedback=editor_result
                    )

                    # Track refinement cost
                    costs["editor"] += refinement_result["cost"]

                    # Update article with refined version
                    content_result["article"] = refinement_result["article"]

                    logger.info(
                        "orchestrator.refinement_complete",
                        job_id=job_id,
                        word_count_added=refinement_result["improvements"]["word_count_added"],
                        citations_added=refinement_result["improvements"]["citations_added"],
                        refinement_cost=float(refinement_result["cost"])
                    )

                    # Re-score the refined article
                    await self._update_job_status(
                        job_id, "processing", 75, "re_scoring"
                    )

                    editor_result = await self.editor_agent.score(
                        content_result["article"]
                    )
                    costs["editor"] += editor_result["cost"]

                    # Update decision and quality score with refined version
                    decision = editor_result["decision"]
                    quality_score = editor_result["quality_score"]

                    # Calculate actual score improvement (fixed bug)
                    score_improvement = quality_score - original_quality_score

                    logger.info(
                        "orchestrator.refinement_rescored",
                        job_id=job_id,
                        original_score=original_quality_score,
                        new_score=quality_score,
                        score_improvement=score_improvement,
                        new_decision=decision
                    )

                except Exception as refinement_error:
                    logger.warning(
                        "orchestrator.refinement_failed",
                        job_id=job_id,
                        error=str(refinement_error),
                        message="Continuing with original article"
                    )
                    # Continue with original article if refinement fails
                    pass

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

            # STEP 3.75: Citation Verification (NEW - 5-10s)
            # Verify citations against research sources to prevent hallucinations
            await self._update_job_status(
                job_id, "processing", 82, "citation_verification"
            )

            try:
                citation_result = await self.citation_verifier.verify_citations(
                    content_result["article"],
                    research_result.get("sources", [])
                )
                costs["citation_verification"] = citation_result["cost"]

                # Log verification results
                logger.info(
                    "orchestrator.citation_verification_complete",
                    job_id=job_id,
                    passed=citation_result["verification_passed"],
                    confidence=citation_result["confidence_score"],
                    verified_urls=citation_result["verified_urls"],
                    total_refs=citation_result["total_references"],
                    fake_urls=len(citation_result["fake_urls"])
                )

                # Flag article for review if citation verification fails
                if not citation_result["verification_passed"]:
                    logger.warning(
                        "orchestrator.citation_verification_failed",
                        job_id=job_id,
                        confidence=citation_result["confidence_score"],
                        fake_urls=citation_result["fake_urls"],
                        suspicious_claims=len(citation_result["suspicious_claims"])
                    )
                    # Downgrade to review status
                    if decision == "publish":
                        decision = "review"
                        logger.info(
                            "orchestrator.decision_downgraded",
                            job_id=job_id,
                            reason="Citation verification failed",
                            new_decision="review"
                        )

            except Exception as citation_error:
                logger.warning(
                    "orchestrator.citation_verification_error",
                    job_id=job_id,
                    error=str(citation_error),
                    message="Continuing without citation verification"
                )
                # Continue without failing the entire job
                pass

            # Create article in database (with Template Intelligence metadata)
            article_id = await self._create_article(
                content_result["article"],
                target_site,
                quality_score,
                editor_result["feedback"],
                status="review" if decision == "review" else "approved",
                template_guidance=template_guidance,  # Include archetype/template
                eeat_score=editor_result.get("eeat_score", 0),  # E-E-A-T score from editor
                topic=topic  # Pass topic for content_type and country detection
            )

            await self._update_job_status(
                job_id, "processing", 90, "image", article_id=article_id
            )

            # STEP 4: Image Generation (ALWAYS generate hero, content images only for high quality)
            if settings.ENABLE_IMAGE_GENERATION:
                # Generate URL-safe slug for images
                import re
                safe_slug = re.sub(r'[^a-z0-9-]', '', content_result["article"]["title"]
                    .lower()
                    .replace(" ", "-"))[:50]

                # Generate hero image for ALL articles + content images for high quality
                image_result = await self.image_agent.generate(
                    content_result["article"],
                    target_site,
                    safe_slug,
                )
                costs["image"] = image_result["cost"]

                # Update article with all images
                await self._update_article_images(article_id, image_result)

                # Determine final status and publish if quality threshold met
                if decision == "publish":
                    # Always publish high-quality articles (set status + published_at)
                    await self._publish_article(article_id)
                    final_status = "published"
                else:
                    # Medium quality - human review required
                    final_status = "review"
            else:
                # No image generation
                final_status = "review" if decision != "publish" else "approved"

            # STEP 5: Store Template Performance (non-blocking)
            # Calculate word count from content
            content_word_count = len(content_result["article"].get("content", "").split())
            await self._store_template_performance(
                article_id,
                template_guidance,
                quality_score,
                editor_result.get("eeat_score", 0),
                content_word_count
            )

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

            # Fetch article metadata from database for return payload
            pool = get_db()
            async with pool.acquire() as conn:
                article = await conn.fetchrow(
                    """
                    SELECT title, slug, LENGTH(content) as word_count
                    FROM articles
                    WHERE id = $1
                    """,
                    article_id
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
                "title": article["title"] if article else None,
                "slug": article["slug"] if article else None,
                "word_count": article["word_count"] if article else None,
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
                VALUES ($1::varchar(255), $2::varchar(50), $3::integer, $4::varchar(100), $5::uuid, $6::jsonb, $7::decimal, $8::text,
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

            # Convert Decimal cost_breakdown to JSON string for JSONB column
            cost_json = (
                json.dumps({k: str(v) for k, v in cost_breakdown.items()})
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
        template_guidance: Dict = None,
        eeat_score: int = 0,
        topic: str = None
    ) -> str:
        """
        Create article in database with site-prefixed URL structure

        Returns:
            Article UUID
        """
        pool = get_db()

        try:
            query = """
                INSERT INTO articles
                (title, slug, content, excerpt, target_site, content_type, country, status, quality_score,
                 keywords, meta_title, meta_description, reading_time_minutes,
                 target_archetype, surface_template, eeat_score)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                RETURNING id
            """

            # Detect content type from topic or title
            title = article_data.get("title", "untitled")
            content_type = detect_content_type(topic or title)

            # Extract country if present
            country = extract_country(topic or "", title)

            # Generate full slug with site + content_type prefix
            slug = generate_url_slug(title, content_type, target_site, country)

            # Extract Template Intelligence metadata
            target_archetype = template_guidance.get("detected_archetype") if template_guidance else None
            surface_template = template_guidance.get("recommended_template") if template_guidance else None

            async with pool.acquire() as conn:
                article_id = await conn.fetchval(
                    query,
                    article_data.get("title"),
                    slug,
                    article_data.get("content"),
                    article_data.get("excerpt"),
                    target_site,
                    content_type,
                    country,
                    status,
                    quality_score,
                    article_data.get("keywords", []),
                    article_data.get("meta_title"),
                    article_data.get("meta_description"),
                    article_data.get("reading_time_minutes"),
                    target_archetype,
                    surface_template,
                    eeat_score
                )

            logger.info(
                "orchestrator.article_created",
                article_id=article_id,
                title=article_data.get("title"),
                slug=slug,
                content_type=content_type,
                country=country
            )

            return str(article_id)

        except Exception as e:
            logger.error(
                "orchestrator.article_creation_failed",
                error=str(e),
                exc_info=e,
            )
            raise

    async def _update_article_images(self, article_id: str, image_result: Dict):
        """
        Update article with all image URLs (hero + 3 content images)
        AND replace IMAGE_PLACEHOLDER strings in content with actual Cloudinary URLs
        """
        pool = get_db()

        try:
            async with pool.acquire() as conn:
                # First, update image URL columns
                await conn.execute(
                    """
                    UPDATE articles
                    SET hero_image_url = $1,
                        content_image_1_url = $2,
                        content_image_2_url = $3,
                        content_image_3_url = $4
                    WHERE id = $5
                    """,
                    image_result.get("hero_image_url"),
                    image_result.get("content_image_1_url"),
                    image_result.get("content_image_2_url"),
                    image_result.get("content_image_3_url"),
                    article_id,
                )

                # Second, fetch current content to replace IMAGE_PLACEHOLDER strings
                article_content = await conn.fetchval(
                    """
                    SELECT content
                    FROM articles
                    WHERE id = $1
                    """,
                    article_id
                )

                # Replace IMAGE_PLACEHOLDER strings with actual Cloudinary URLs
                if article_content:
                    import re

                    # Replace IMAGE_PLACEHOLDER_HERO with hero_image_url
                    if image_result.get("hero_image_url"):
                        article_content = re.sub(
                            r'!\[([^\]]*)\]\(IMAGE_PLACEHOLDER_HERO\)',
                            f'![\\1]({image_result["hero_image_url"]})',
                            article_content
                        )

                    # Replace IMAGE_PLACEHOLDER_1 with content_image_1_url
                    if image_result.get("content_image_1_url"):
                        article_content = re.sub(
                            r'!\[([^\]]*)\]\(IMAGE_PLACEHOLDER_1\)',
                            f'![\\1]({image_result["content_image_1_url"]})',
                            article_content
                        )

                    # Replace IMAGE_PLACEHOLDER_2 with content_image_2_url
                    if image_result.get("content_image_2_url"):
                        article_content = re.sub(
                            r'!\[([^\]]*)\]\(IMAGE_PLACEHOLDER_2\)',
                            f'![\\1]({image_result["content_image_2_url"]})',
                            article_content
                        )

                    # Replace IMAGE_PLACEHOLDER_3 with content_image_3_url
                    if image_result.get("content_image_3_url"):
                        article_content = re.sub(
                            r'!\[([^\]]*)\]\(IMAGE_PLACEHOLDER_3\)',
                            f'![\\1]({image_result["content_image_3_url"]})',
                            article_content
                        )

                    # Update content field with replaced placeholders
                    await conn.execute(
                        """
                        UPDATE articles
                        SET content = $1
                        WHERE id = $2
                        """,
                        article_content,
                        article_id
                    )

            logger.info(
                "orchestrator.images_updated",
                article_id=article_id,
                hero=bool(image_result.get("hero_image_url")),
                content_images=sum([
                    bool(image_result.get("content_image_1_url")),
                    bool(image_result.get("content_image_2_url")),
                    bool(image_result.get("content_image_3_url")),
                ]),
                placeholders_replaced=True
            )

        except Exception as e:
            logger.error(
                "orchestrator.images_update_failed",
                error=str(e),
                exc_info=e,
            )

    async def _publish_article(self, article_id: str):
        """
        Publish article (set status to published and published_at)
        """
        pool = get_db()

        try:
            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    UPDATE articles
                    SET status = 'published',
                        published_at = NOW()
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

    async def _store_template_performance(
        self,
        article_id: str,
        template_guidance: Dict,
        quality_score: int,
        eeat_score: int,
        word_count: int
    ):
        """
        Store template performance data for learning

        Args:
            article_id: Article UUID
            template_guidance: Template Intelligence recommendations
            quality_score: Overall quality score
            eeat_score: E-E-A-T compliance score
            word_count: Actual word count
        """
        pool = get_db()

        try:
            # Extract module count from content (count H2 headers as modules)
            module_count = len(template_guidance.get("common_modules", []))

            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO template_performance
                    (article_id, archetype_used, template_used, modules_used,
                     word_count, module_count, quality_score, eeat_score)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """,
                    article_id,
                    template_guidance.get("detected_archetype"),
                    template_guidance.get("recommended_template"),
                    template_guidance.get("common_modules", []),
                    word_count,
                    module_count,
                    quality_score,
                    eeat_score
                )

            logger.info(
                "orchestrator.performance_tracked",
                article_id=article_id,
                archetype=template_guidance.get("detected_archetype"),
                quality=quality_score,
                eeat=eeat_score
            )

        except Exception as e:
            logger.error(
                "orchestrator.performance_tracking_failed",
                error=str(e),
                exc_info=e
            )
            # Don't raise - performance tracking is non-critical
