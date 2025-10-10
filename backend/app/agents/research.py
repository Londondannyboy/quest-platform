"""
Quest Platform v2.2 - ResearchAgent
Gathers intelligence using Perplexity + pgvector cache for cost savings
"""

import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
import json

import httpx
from openai import AsyncOpenAI
import structlog

from app.core.config import settings
from app.core.database import get_db
from app.core.research_queue import ResearchGovernance
from app.core.research_apis import MultiAPIResearch
from app.core.research_cache import ClusterResearchCache

logger = structlog.get_logger(__name__)


class ResearchAgent:
    """
    Research Agent: Gather intelligence with multi-level caching

    Cost optimization (Claude Desktop recommendations):
    - Cluster cache hit: $0.00 (90% hit rate target)
    - Topic cache hit: $0.00 (40% hit rate)
    - Cache miss: ~$0.45 (multi-API research)
    - Monthly savings: $225 at 1000 articles/month
    """

    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.perplexity_api_key = settings.PERPLEXITY_API_KEY
        self.cache_enabled = settings.RESEARCH_CACHE_ENABLED
        self.similarity_threshold = settings.RESEARCH_CACHE_SIMILARITY_THRESHOLD
        self.cache_ttl_days = settings.RESEARCH_CACHE_TTL_DAYS
        self.governance = ResearchGovernance()
        self.multi_api = MultiAPIResearch()
        self.cluster_cache = ClusterResearchCache()

    async def run(self, topic: str) -> Dict:
        """
        Main research workflow with governance and caching

        Args:
            topic: Research topic/query

        Returns:
            Dict with research data and cost
        """
        logger.info("research_agent.start", topic=topic)

        # Step 0: Research Governance Check (TIER 0 Priority)
        await self.governance.load_completed_topics()  # Refresh completed list
        validation = self.governance.validate_research_request(topic)

        if not validation["approved"]:
            logger.warning(
                "research_agent.topic_rejected",
                topic=topic,
                reason=validation["reason"],
                suggested=validation["suggested_alternative"]
            )
            # Use suggested alternative if available
            if validation["suggested_alternative"]:
                topic = validation["suggested_alternative"]
                logger.info(
                    "research_agent.using_alternative",
                    original_topic=topic,
                    new_topic=validation["suggested_alternative"]
                )
        else:
            logger.info(
                "research_agent.topic_approved",
                topic=topic,
                priority=validation["priority_score"],
                category=validation["category"]
            )

        # Step 1: Check cluster cache FIRST (highest priority - 90% savings)
        if self.cache_enabled:
            cluster_result = await self.cluster_cache.get_research(topic)
            if cluster_result and cluster_result.get("cached"):
                logger.info(
                    "research_agent.cluster_cache_hit",
                    topic=topic,
                    cluster_id=cluster_result["cluster_id"],
                    age_days=cluster_result["cache_age_days"],
                    cost_saved=0.45
                )
                return {
                    "topic": topic,
                    "research": cluster_result["research_data"],
                    "cache_hit": True,
                    "cluster_cache": True,
                    "cost": Decimal("0.00"),
                }

        # Step 2: Generate embedding for topic cache
        embedding = await self._generate_embedding(topic)

        # Step 3: Check topic cache (secondary - 40% hit rate)
        if self.cache_enabled:
            cache_result = await self._check_cache(embedding)
            if cache_result:
                logger.info(
                    "research_agent.topic_cache_hit",
                    topic=topic,
                    cache_id=cache_result["id"],
                )
                return {
                    "topic": topic,
                    "research": cache_result["research_json"],
                    "cache_hit": True,
                    "cluster_cache": False,
                    "cost": Decimal("0.00"),
                }

        # Step 4: Cache miss - use multi-API research
        logger.info("research_agent.cache_miss", topic=topic)

        # Determine if this is a high-priority topic that warrants comprehensive research
        priority_score, _ = self.governance.get_priority_score(topic)

        # ALWAYS use all APIs for comprehensive research (Serper for competitors, Tavily for depth, Firecrawl for scraping)
        # This is critical for SEO - we need to know what competitors are ranking for
        use_all_apis = True  # Changed: Always use full API stack for competitive intelligence

        # Query using multi-API system with ALL providers
        research_result = await self.multi_api.research(
            query=topic,
            use_all=use_all_apis,
            fact_check=(priority_score >= 70)  # Fact-check important content (lowered threshold)
        )

        research_data = {
            "content": research_result.get("content", ""),
            "sources": research_result.get("sources", []),
            "providers_used": research_result.get("providers_used", [])
        }

        # Step 4: Score research quality
        quality_score = self.multi_api.score_research_quality(
            content=research_data.get("content", ""),
            sources=research_data.get("sources", [])
        )

        logger.info(
            "research_agent.quality_score",
            topic=topic,
            score=quality_score["total_score"],
            is_sufficient=quality_score["is_sufficient"],
            metrics=quality_score["metrics"]
        )

        # Add quality score to research data
        research_data["quality_score"] = quality_score

        # Step 5: Store in BOTH caches (only if quality is sufficient)
        if self.cache_enabled and research_data.get("content") and quality_score["is_sufficient"]:
            # Store in topic cache (legacy)
            await self._store_in_cache(topic, embedding, research_data)

            # Store in cluster cache (NEW - Claude Desktop optimization)
            await self.cluster_cache.save_research(
                topic=topic,
                research_data=research_data,
                seo_data=research_result.get("seo_data"),
                serp_analysis=research_result.get("serp_analysis"),
                ai_insights=research_result.get("ai_insights")
            )
            logger.info("research_agent.saved_to_cluster_cache", topic=topic)

        # Extract sources for link validation
        sources = []
        if "sources" in research_data:
            for source in research_data["sources"]:
                if isinstance(source, str):
                    sources.append(source)
                elif isinstance(source, dict) and "url" in source:
                    sources.append(source["url"])

        return {
            "topic": topic,
            "research": research_data,
            "sources": sources,  # Pass sources explicitly for link validation
            "cache_hit": False,
            "cost": research_result.get("total_cost", Decimal("0.20")),
            "quality_score": quality_score
        }

    async def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate OpenAI embedding for text

        Cost: ~$0.000016 per query (negligible)
        """
        try:
            response = await self.openai_client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL, input=text
            )
            return response.data[0].embedding

        except Exception as e:
            logger.error("research_agent.embedding_failed", error=str(e), exc_info=e)
            raise

    async def _check_cache(self, embedding: List[float]) -> Optional[Dict]:
        """
        Check cache using pgvector similarity search

        Args:
            embedding: Query embedding vector

        Returns:
            Cached research if found, None otherwise
        """
        pool = get_db()

        try:
            # pgvector cosine similarity search
            query = """
                SELECT
                    id,
                    topic_query,
                    research_json,
                    cache_hits,
                    1 - (embedding <=> $1::vector) as similarity
                FROM article_research
                WHERE 1 - (embedding <=> $1::vector) > $2
                AND expires_at > NOW()
                ORDER BY similarity DESC
                LIMIT 1
            """

            # Convert Python list to pgvector format string
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'

            async with pool.acquire() as conn:
                result = await conn.fetchrow(
                    query, embedding_str, self.similarity_threshold
                )

                if result:
                    # Update cache hit stats
                    await conn.execute(
                        """
                        UPDATE article_research
                        SET cache_hits = cache_hits + 1,
                            last_accessed = NOW()
                        WHERE id = $1
                        """,
                        result["id"],
                    )

                    return dict(result)

                return None

        except Exception as e:
            logger.error("research_agent.cache_check_failed", error=str(e), exc_info=e)
            # Don't fail on cache errors - continue to API call
            return None

    async def _query_perplexity(self, topic: str) -> Dict:
        """
        Query Perplexity Sonar Pro API for research

        Cost: ~$0.20 per request
        """
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.perplexity_api_key}",
            "Content-Type": "application/json",
        }

        # Julian Goldie AI SEO: Gap analysis for AI overview opportunities
        gap_analysis_prompt = f"""Research "{topic}" with AI overview gap analysis:

## 1. CURRENT AI OVERVIEW
What do AI systems (ChatGPT, Perplexity, Claude) currently say about {topic}?
Provide the typical 2-3 sentence AI overview response.

## 2. SOURCES USED
Which websites and sources do AI systems commonly cite when answering about {topic}?
List 5-10 authoritative sources.

## 3. MISSING SUBTOPICS
What important aspects of {topic} are NOT well-covered in AI overviews?
Identify 5-7 content gaps.

## 4. COMMON QUESTIONS
What questions do users ask about {topic} that AI can't answer well?
List 5-10 frequently asked questions with incomplete AI answers.

## 5. LATEST DEVELOPMENTS
What's new in 2024-2025 regarding {topic}?
Recent trends, policy changes, or updates.

## 6. DATA & STATISTICS
Key numbers, facts, and figures about {topic} with sources.

## 7. EXPERT PERSPECTIVES
What do industry experts or authorities say about {topic}?

## 8. OPPORTUNITY AREAS
Where can Quest Platform add unique value that AI overviews are missing?

Provide comprehensive, factual information with specific citations."""

        payload = {
            "model": settings.PERPLEXITY_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a research assistant specializing in AI SEO gap analysis. Identify what AI overviews are missing and where new content can add value.",
                },
                {
                    "role": "user",
                    "content": gap_analysis_prompt,
                },
            ],
            "max_tokens": 3000,  # Increased for comprehensive gap analysis
            "temperature": 0.2,
            "return_citations": True,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()

                data = response.json()

                return {
                    "topic": topic,
                    "content": data["choices"][0]["message"]["content"],
                    "citations": data.get("citations", []),
                    "timestamp": datetime.now().isoformat(),
                    "model": settings.PERPLEXITY_MODEL,
                }

        except httpx.TimeoutException:
            logger.error("research_agent.perplexity_timeout", topic=topic)
            raise Exception("Perplexity API timeout")

        except httpx.HTTPStatusError as e:
            logger.error(
                "research_agent.perplexity_http_error",
                status=e.response.status_code,
                error=e.response.text,
            )
            raise Exception(f"Perplexity API error: {e.response.status_code}")

        except Exception as e:
            logger.error("research_agent.perplexity_failed", error=str(e), exc_info=e)
            raise

    async def _store_in_cache(
        self, topic: str, embedding: List[float], research_data: Dict
    ):
        """
        Store research in cache for future reuse

        Args:
            topic: Research topic
            embedding: Topic embedding vector
            research_data: Research results
        """
        pool = get_db()

        try:
            query = """
                INSERT INTO article_research
                (topic_query, embedding, research_json, expires_at)
                VALUES ($1::text, $2::vector, $3::jsonb, NOW() + INTERVAL '{} days')
            """.format(
                self.cache_ttl_days
            )

            # Convert Python list to pgvector format string
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'

            async with pool.acquire() as conn:
                await conn.execute(
                    query,
                    topic,
                    embedding_str,
                    json.dumps(research_data),
                )

            logger.info("research_agent.cache_stored", topic=topic)

        except Exception as e:
            logger.error("research_agent.cache_store_failed", error=str(e), exc_info=e)
            # Don't fail if caching fails - research data is still valid

    async def invalidate_cache(self, topic: str):
        """
        Invalidate cache for a specific topic (admin function)

        Args:
            topic: Topic to invalidate
        """
        pool = get_db()

        try:
            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    UPDATE article_research
                    SET expires_at = NOW()
                    WHERE topic_query ILIKE $1
                    """,
                    f"%{topic}%",
                )

            logger.info("research_agent.cache_invalidated", topic=topic)

        except Exception as e:
            logger.error(
                "research_agent.cache_invalidation_failed", error=str(e), exc_info=e
            )
            raise
