"""
Research Caching System

Implements cluster-level research caching to prevent redundant API calls
for related topics (e.g., all "Portugal visa" articles share cluster research).

Cost Impact:
- Without caching: 1000 articles × $0.25 = $250/month
- With caching (90% hit rate): 100 clusters × $0.25 + 900 cache hits × $0 = $25/month
- Savings: $225/month (90% reduction)

Architecture:
- Topic clusters (e.g., "portugal_visas", "spain_immigration")
- 90-day cache TTL (quarterly refresh)
- Shared research across related topics
- Cache key includes cluster_id + research_tier
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone
import structlog
from app.core.database import get_db

logger = structlog.get_logger()


class ClusterResearchCache:
    """
    Cache research at topic cluster level for massive cost savings

    Example clusters:
    - portugal_digital_nomad: All Portugal visa/nomad articles
    - spain_visas: All Spain immigration topics
    - remote_work: All remote work strategies
    """

    # Topic cluster definitions (expand as you add topics)
    TOPIC_CLUSTERS = {
        "portugal_digital_nomad": {
            "keywords": ["portugal", "d7", "digital nomad visa", "golden visa", "nhr"],
            "priority": "high",
            "research_tier": "perplexity"
        },
        "spain_immigration": {
            "keywords": ["spain", "non-lucrative", "digital nomad visa", "golden visa"],
            "priority": "high",
            "research_tier": "perplexity"
        },
        "italy_visas": {
            "keywords": ["italy", "elective residence", "digital nomad", "startup visa"],
            "priority": "medium",
            "research_tier": "tavily"
        },
        "france_immigration": {
            "keywords": ["france", "long-stay visa", "talent passport", "auto-entrepreneur"],
            "priority": "medium",
            "research_tier": "tavily"
        },
        "remote_work_strategies": {
            "keywords": ["remote work", "work from anywhere", "distributed team", "async"],
            "priority": "medium",
            "research_tier": "tavily"
        },
        "tax_optimization": {
            "keywords": ["tax", "residency", "non-dom", "territorial taxation", "treaty"],
            "priority": "high",
            "research_tier": "perplexity"
        },
        "digital_nomad_hubs": {
            "keywords": ["digital nomad city", "coworking", "nomad visa", "remote work hub"],
            "priority": "low",
            "research_tier": "haiku"
        }
    }

    def __init__(self):
        pass  # Uses get_db() for pool access

    async def identify_cluster(self, topic: str) -> Optional[Dict]:
        """
        Identify which cluster a topic belongs to

        Args:
            topic: Article topic (e.g., "Portugal D7 Visa 2025 Guide")

        Returns:
            Cluster info dict or None if no match
        """
        topic_lower = topic.lower()

        for cluster_name, cluster_info in self.TOPIC_CLUSTERS.items():
            # Check if any cluster keywords appear in topic
            if any(keyword in topic_lower for keyword in cluster_info["keywords"]):
                return {
                    "cluster_id": cluster_name,
                    "priority": cluster_info["priority"],
                    "research_tier": cluster_info["research_tier"]
                }

        return None

    async def get_research(self, topic: str) -> Optional[Dict]:
        """
        Check cluster cache before running expensive research

        Args:
            topic: Article topic

        Returns:
            Cached research dict or None if no cache hit
        """
        cluster = await self.identify_cluster(topic)

        if not cluster:
            logger.info("research_cache.no_cluster", topic=topic)
            return None

        cluster_id = cluster["cluster_id"]

        # Query cluster_research table
        query = """
            SELECT
                research_data,
                seo_data,
                serp_analysis,
                ai_insights,
                reuse_count,
                created_at
            FROM cluster_research
            WHERE cluster_id = $1
              AND expires_at > NOW()
            ORDER BY created_at DESC
            LIMIT 1
        """

        pool = get_db()
        async with pool.acquire() as conn:
            result = await conn.fetchrow(query, cluster_id)

            if result:
                # Increment reuse counter
                await conn.execute(
                    "UPDATE cluster_research SET reuse_count = reuse_count + 1 WHERE cluster_id = $1",
                    cluster_id
                )

            # Make created_at timezone-aware if it isn't already
            created_at = result["created_at"]
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)

            age_days = (datetime.now(timezone.utc) - created_at).days

            logger.info(
                "research_cache.hit",
                cluster_id=cluster_id,
                topic=topic,
                reuse_count=result["reuse_count"] + 1,
                cost_saved=0.25,
                age_days=age_days
            )

            return {
                "cluster_id": cluster_id,
                "research_data": result["research_data"],
                "seo_data": result["seo_data"],
                "serp_analysis": result["serp_analysis"],
                "ai_insights": result["ai_insights"],
                "cached": True,
                "cache_age_days": age_days
            }

        logger.info(
            "research_cache.miss",
            cluster_id=cluster_id,
            topic=topic
        )
        return None

    async def save_research(
        self,
        topic: str,
        research_data: Dict,
        seo_data: Optional[Dict] = None,
        serp_analysis: Optional[Dict] = None,
        ai_insights: Optional[Dict] = None
    ) -> bool:
        """
        Save research to cluster cache

        Args:
            topic: Article topic
            research_data: Full research from ResearchAgent
            seo_data: DataForSEO keyword data
            serp_analysis: Serper/DataForSEO SERP data
            ai_insights: Perplexity/Tavily narrative research

        Returns:
            True if saved successfully
        """
        cluster = await self.identify_cluster(topic)

        if not cluster:
            logger.warning("research_cache.save_failed_no_cluster", topic=topic)
            return False

        cluster_id = cluster["cluster_id"]
        expires_at = datetime.now(timezone.utc) + timedelta(days=90)

        # Insert or update cluster research
        query = """
            INSERT INTO cluster_research (
                cluster_id,
                research_data,
                seo_data,
                serp_analysis,
                ai_insights,
                reuse_count,
                expires_at,
                created_at
            ) VALUES ($1, $2, $3, $4, $5, 0, $6, NOW())
            ON CONFLICT (cluster_id)
            DO UPDATE SET
                research_data = EXCLUDED.research_data,
                seo_data = EXCLUDED.seo_data,
                serp_analysis = EXCLUDED.serp_analysis,
                ai_insights = EXCLUDED.ai_insights,
                expires_at = EXCLUDED.expires_at,
                created_at = NOW()
        """

        pool = get_db()
        async with pool.acquire() as conn:
            await conn.execute(
                query,
                cluster_id,
                research_data,
                seo_data or {},
                serp_analysis or {},
                ai_insights or {},
                expires_at
            )

        logger.info(
            "research_cache.saved",
            cluster_id=cluster_id,
            topic=topic,
            expires_at=expires_at.isoformat()
        )

        return True

    async def get_cache_stats(self) -> Dict:
        """
        Get cache performance statistics

        Returns:
            Dict with hit rate, savings, cluster stats
        """
        query = """
            SELECT
                COUNT(*) as cluster_count,
                SUM(reuse_count) as total_reuses,
                AVG(reuse_count) as avg_reuses_per_cluster,
                MAX(reuse_count) as max_reuses,
                SUM(CASE WHEN expires_at < NOW() THEN 1 ELSE 0 END) as expired_count
            FROM cluster_research
        """

        pool = get_db()
        async with pool.acquire() as conn:
            stats = await conn.fetchrow(query)

        total_reuses = stats["total_reuses"] or 0
        cluster_count = stats["cluster_count"] or 0

        # Calculate cost savings
        cost_per_research = 0.25
        cost_saved = total_reuses * cost_per_research

        # Calculate hit rate (reuses / total_requests)
        # Assumption: Each cluster has 1 original + N reuses
        total_requests = cluster_count + total_reuses
        hit_rate = (total_reuses / total_requests * 100) if total_requests > 0 else 0

        return {
            "cluster_count": cluster_count,
            "total_reuses": total_reuses,
            "avg_reuses_per_cluster": float(stats["avg_reuses_per_cluster"] or 0),
            "max_reuses": stats["max_reuses"] or 0,
            "expired_count": stats["expired_count"] or 0,
            "hit_rate_percent": round(hit_rate, 2),
            "cost_saved_usd": round(cost_saved, 2),
            "active_clusters": cluster_count - (stats["expired_count"] or 0)
        }
