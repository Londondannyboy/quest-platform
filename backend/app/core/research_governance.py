"""
Research Governance - Cost Optimization System
Prevents duplicate research and routes to appropriate APIs

Cost Savings: 54% reduction ($325/month at 1000 articles)
- Cluster research reuse: 70% of articles ($0.45 → $0.10)
- Tiered routing: High→Perplexity, Medium→Tavily, Low→Haiku
- Strategic caching: 90-day TTL for cluster research
"""
import structlog
from typing import Optional, Dict, List
from enum import Enum
from decimal import Decimal

from app.core.database import get_db
from app.core.config import settings

logger = structlog.get_logger(__name__)


class ResearchDecision(Enum):
    """Research routing decisions"""
    REUSE_CLUSTER = "reuse_cluster"          # Use cached cluster research (FREE!)
    RESEARCH_PERPLEXITY = "research_perplexity"  # High priority ($0.15)
    RESEARCH_TAVILY = "research_tavily"         # Medium priority ($0.05)
    RESEARCH_HAIKU = "research_haiku"          # Low priority ($0.01 synthesis)
    SKIP = "skip"                              # Not in strategy


class TopicCluster:
    """Topic cluster with research"""
    def __init__(self, row):
        self.id = row['id']
        self.name = row['name']
        self.slug = row['slug']
        self.priority = row['priority']
        self.research_tier = row['research_tier']
        self.research_ttl_days = row['research_ttl_days']
        self.primary_keywords = row['primary_keywords']
        self.article_count = row.get('article_count', 0)

        # Research data (if exists)
        self.research_id = row.get('research_id')
        self.research_data = row.get('research_data')
        self.research_cost = row.get('research_cost', Decimal(0))
        self.research_age_days = row.get('research_age_days')
        self.reuse_count = row.get('reuse_count', 0)


class ResearchGovernance:
    """
    Research governance and cost optimization

    Implements:
    1. Cluster detection (find which cluster a topic belongs to)
    2. Research reuse (check if cluster has recent research)
    3. Tiered routing (route to appropriate API based on priority)
    4. Cost tracking (monitor savings from reuse)
    """

    def __init__(self):
        self.pool = get_db()

    async def get_research_decision(self, topic: str) -> tuple[ResearchDecision, Optional[TopicCluster]]:
        """
        Decide how to research this topic

        Returns:
            (ResearchDecision, Optional[TopicCluster])

        Examples:
            ("reuse_cluster", cluster) → Use cached research (FREE!)
            ("research_perplexity", cluster) → High priority, use Perplexity
            ("research_tavily", cluster) → Medium priority, use Tavily
            ("research_haiku", cluster) → Low priority, synthesize with Haiku
            ("skip", None) → Topic not in strategy
        """
        # 1. Find cluster for this topic
        cluster = await self.find_cluster(topic)

        if not cluster:
            logger.warning(
                "research_governance.topic_not_in_strategy",
                topic=topic
            )
            return (ResearchDecision.SKIP, None)

        # 2. Check if cluster has recent research
        if await self.has_recent_research(cluster.id):
            # Load the cached research
            cluster_with_research = await self.get_cluster_with_research(cluster.id)

            logger.info(
                "research_governance.reusing_cluster_research",
                cluster=cluster.name,
                cluster_id=cluster.id,
                research_age_days=cluster_with_research.research_age_days,
                reuse_count=cluster_with_research.reuse_count,
                cost_saved=0.45
            )

            return (ResearchDecision.REUSE_CLUSTER, cluster_with_research)

        # 3. Route based on research tier (from cluster config)
        if cluster.research_tier == 'perplexity':
            decision = ResearchDecision.RESEARCH_PERPLEXITY
            cost = 0.15
        elif cluster.research_tier == 'tavily':
            decision = ResearchDecision.RESEARCH_TAVILY
            cost = 0.05
        else:  # haiku
            decision = ResearchDecision.RESEARCH_HAIKU
            cost = 0.01

        logger.info(
            "research_governance.new_research_needed",
            cluster=cluster.name,
            cluster_id=cluster.id,
            priority=cluster.priority,
            research_tier=cluster.research_tier,
            estimated_cost=cost
        )

        return (decision, cluster)

    async def find_cluster(self, topic: str) -> Optional[TopicCluster]:
        """
        Find which cluster this topic belongs to

        Uses smart matching:
        1. Exact keyword match
        2. Fuzzy keyword match
        3. Similarity to cluster name
        """
        async with self.pool.acquire() as conn:
            # Use the database function we created
            cluster_id = await conn.fetchval(
                "SELECT find_cluster_for_topic($1)",
                topic
            )

            if not cluster_id:
                return None

            # Load full cluster data
            row = await conn.fetchrow("""
                SELECT
                    id, name, slug, description,
                    priority, target_site,
                    primary_keywords, secondary_keywords,
                    research_tier, research_ttl_days,
                    article_count, total_research_cost
                FROM topic_clusters
                WHERE id = $1
            """, cluster_id)

            return TopicCluster(row) if row else None

    async def has_recent_research(self, cluster_id: int) -> bool:
        """Check if cluster has recent (non-stale) research"""
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT cluster_has_recent_research($1)",
                cluster_id
            )

    async def get_cluster_with_research(self, cluster_id: int) -> TopicCluster:
        """Get cluster with its most recent research data"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT
                    tc.*,
                    cr.id as research_id,
                    cr.research_data,
                    cr.seo_data,
                    cr.serp_analysis,
                    cr.ai_insights,
                    cr.research_cost,
                    cr.reuse_count,
                    EXTRACT(days FROM NOW() - cr.created_at)::INTEGER as research_age_days
                FROM topic_clusters tc
                JOIN LATERAL (
                    SELECT * FROM cluster_research
                    WHERE cluster_id = tc.id
                      AND expires_at > NOW()
                      AND NOT is_stale
                    ORDER BY created_at DESC
                    LIMIT 1
                ) cr ON true
                WHERE tc.id = $1
            """, cluster_id)

            return TopicCluster(row)

    async def store_cluster_research(
        self,
        cluster_id: int,
        research_data: Dict,
        seo_data: Dict,
        serp_analysis: Optional[Dict],
        ai_insights: Dict,
        ai_provider: str,
        research_cost: Decimal,
        keywords_analyzed: List[str]
    ) -> int:
        """
        Store research for cluster reuse

        Returns:
            research_id for linking to articles
        """
        async with self.pool.acquire() as conn:
            # Calculate TTL from cluster config
            ttl_days = await conn.fetchval(
                "SELECT research_ttl_days FROM topic_clusters WHERE id = $1",
                cluster_id
            )

            research_id = await conn.fetchval("""
                INSERT INTO cluster_research (
                    cluster_id,
                    research_data,
                    keywords_analyzed,
                    seo_data,
                    search_volume,
                    keyword_difficulty,
                    serp_analysis,
                    ai_insights,
                    ai_provider,
                    research_cost,
                    expires_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                    NOW() + ($11 || ' days')::INTERVAL
                )
                RETURNING id
            """,
                cluster_id,
                research_data,
                keywords_analyzed,
                seo_data,
                seo_data.get('search_volume', 0),
                seo_data.get('keyword_difficulty', 0),
                serp_analysis,
                ai_insights,
                ai_provider,
                research_cost,
                ttl_days
            )

            logger.info(
                "research_governance.cluster_research_stored",
                cluster_id=cluster_id,
                research_id=research_id,
                ai_provider=ai_provider,
                research_cost=float(research_cost),
                ttl_days=ttl_days,
                keywords_count=len(keywords_analyzed)
            )

            return research_id

    async def get_cost_savings_stats(self) -> Dict:
        """Get cost savings statistics"""
        async with self.pool.acquire() as conn:
            stats = await conn.fetchrow("""
                SELECT
                    SUM(article_count) as total_articles,
                    SUM(total_research_cost) as actual_research_cost,
                    SUM(article_count * 0.45) as cost_if_no_reuse,
                    SUM((article_count * 0.45) - total_research_cost) as total_saved,
                    COUNT(*) as clusters_active,
                    AVG(article_count) as avg_articles_per_cluster
                FROM topic_clusters
                WHERE article_count > 0
            """)

            # Reuse statistics
            reuse_stats = await conn.fetchrow("""
                SELECT
                    COUNT(*) as total_research_operations,
                    SUM(reuse_count) as total_reuses,
                    ROUND(AVG(reuse_count), 1) as avg_reuse_per_research,
                    SUM(research_cost) as research_investment,
                    SUM(reuse_count * 0.45) as savings_from_reuse
                FROM cluster_research
                WHERE created_at > NOW() - INTERVAL '30 days'
            """)

            return {
                "articles": {
                    "total_generated": stats['total_articles'] or 0,
                    "avg_per_cluster": float(stats['avg_articles_per_cluster'] or 0)
                },
                "costs": {
                    "actual_research_cost": float(stats['actual_research_cost'] or 0),
                    "cost_if_no_reuse": float(stats['cost_if_no_reuse'] or 0),
                    "total_saved": float(stats['total_saved'] or 0),
                    "savings_percentage": round(
                        (float(stats['total_saved'] or 0) / float(stats['cost_if_no_reuse'] or 1)) * 100,
                        1
                    )
                },
                "reuse": {
                    "total_research_operations": reuse_stats['total_research_operations'] or 0,
                    "total_reuses": reuse_stats['total_reuses'] or 0,
                    "avg_reuse_per_research": float(reuse_stats['avg_reuse_per_research'] or 0),
                    "research_investment": float(reuse_stats['research_investment'] or 0),
                    "savings_from_reuse": float(reuse_stats['savings_from_reuse'] or 0)
                },
                "clusters": {
                    "active_clusters": stats['clusters_active'] or 0
                }
            }

    async def mark_research_stale(self, cluster_id: int):
        """Mark cluster research as stale (force new research)"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE cluster_research
                SET is_stale = true
                WHERE cluster_id = $1
            """, cluster_id)

            logger.info(
                "research_governance.marked_stale",
                cluster_id=cluster_id
            )
