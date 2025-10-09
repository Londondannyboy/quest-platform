"""
Quest Platform - KeywordResearcher Agent
Uses Perplexity to identify keywords and DataForSEO to validate SEO value
"""

import json
import re
from typing import Dict, List, Optional
from decimal import Decimal

import structlog
from anthropic import AsyncAnthropic

from app.core.config import settings
from app.core.research_apis import DataForSEOProvider

logger = structlog.get_logger(__name__)


class KeywordResearcher:
    """
    Keyword Research Agent

    Phase 1 of content creation pipeline:
    1. Uses Perplexity to identify 15-20 relevant keywords
    2. Uses DataForSEO to validate search volume, competition, CPC
    3. Returns primary + secondary keywords with SEO metrics

    Cost: ~$0.22 per research (Perplexity $0.20 + DataForSEO $0.02)
    """

    def __init__(self):
        self.perplexity_client = AsyncAnthropic(api_key=settings.PERPLEXITY_API_KEY)
        self.perplexity_model = settings.PERPLEXITY_MODEL
        self.dataforseo = DataForSEOProvider()

    async def identify_keywords(self, topic: str, target_site: str = "relocation") -> List[str]:
        """
        Use Perplexity to identify relevant keywords for a topic

        Args:
            topic: Article topic (e.g., "Cyprus relocation services")
            target_site: Target site (relocation/placement/rainmaker)

        Returns:
            List of 15-20 keywords
        """
        logger.info("keyword_researcher.identifying", topic=topic)

        # Domain-specific context
        domain_context = {
            "relocation": "digital nomads, expats, international relocation, visa requirements",
            "placement": "job seekers, career professionals, recruitment, hiring",
            "rainmaker": "entrepreneurs, business builders, revenue growth, sales"
        }.get(target_site, "")

        prompt = f"""Identify 15-20 high-value SEO keywords for the topic: "{topic}"

Context: This is for {target_site}.quest, focusing on {domain_context}.

Focus on:
- Long-tail keywords with commercial intent (3-5 words)
- Location-specific variations (if applicable)
- Service-specific terms
- Common questions people ask
- Related search terms

CRITICAL: Return ONLY a JSON array of keywords, no explanation or markdown.

Example format:
["keyword 1", "keyword 2", "keyword 3", ...]

Keywords:"""

        try:
            # Use Perplexity API for keyword identification
            from httpx import AsyncClient

            async with AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.perplexity_model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3  # Lower for consistency
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]

                    # Extract JSON array from response
                    try:
                        # Clean the response to get just the JSON
                        json_match = re.search(r'\[.*\]', content, re.DOTALL)
                        if json_match:
                            keywords = json.loads(json_match.group())
                            logger.info("keyword_researcher.identified", count=len(keywords))
                            return keywords[:20]  # Limit to 20
                    except json.JSONDecodeError:
                        logger.warning("keyword_researcher.parse_failed", using_fallback=True)
                        # Fallback: split by lines/commas
                        keywords = [k.strip(' -"[]') for k in content.split('\n') if k.strip()]
                        return keywords[:20]
                else:
                    logger.error("perplexity_error", status=response.status_code)
                    return self._get_fallback_keywords(topic)

        except Exception as e:
            logger.error("keyword_researcher.identification_failed", error=str(e))
            return self._get_fallback_keywords(topic)

    def _get_fallback_keywords(self, topic: str) -> List[str]:
        """Generate fallback keywords when API fails"""
        base = topic.lower()
        return [
            f"{base}",
            f"{base} guide",
            f"{base} 2025",
            f"best {base}",
            f"{base} cost",
            f"{base} services",
            f"{base} companies",
            f"how to {base}",
            f"{base} requirements",
            f"{base} process",
            f"professional {base}",
            f"{base} experts",
            f"{base} tips",
            f"{base} benefits",
            f"{base} challenges"
        ]

    async def validate_keywords(self, keywords: List[str]) -> List[Dict]:
        """
        Use DataForSEO to validate keyword SEO value

        Args:
            keywords: List of keywords to validate

        Returns:
            List of keywords with SEO metrics (sorted by search volume)
        """
        logger.info("keyword_researcher.validating", count=len(keywords))

        if not self.dataforseo.is_available():
            logger.warning("dataforseo_not_configured", using_basic_validation=True)
            # Return keywords without metrics
            return [{"keyword": k, "search_volume": 0, "competition": "unknown", "cpc": 0}
                    for k in keywords[:10]]

        result = await self.dataforseo.validate_keywords(keywords)

        if result and result.get("keywords"):
            validated = result["keywords"]
            logger.info("keyword_researcher.validated", count=len(validated))
            return validated[:10]  # Return top 10 by search volume
        else:
            logger.warning("dataforseo_validation_empty")
            return [{"keyword": k, "search_volume": 0, "competition": "unknown", "cpc": 0}
                    for k in keywords[:10]]

    async def research_keywords(self, topic: str, target_site: str = "relocation") -> Dict:
        """
        Complete keyword research pipeline

        Args:
            topic: Article topic
            target_site: Target site (relocation/placement/rainmaker)

        Returns:
            {
                "topic": str,
                "total_keywords_found": int,
                "validated_keywords": List[Dict],
                "primary_keyword": str,
                "secondary_keywords": List[str],
                "seo_metrics": Dict,
                "cost": Decimal
            }
        """
        logger.info("keyword_researcher.start", topic=topic, target_site=target_site)

        # Step 1: Identify keywords with Perplexity
        keywords = await self.identify_keywords(topic, target_site)

        # Step 2: Validate with DataForSEO
        validated_keywords = await self.validate_keywords(keywords)

        # Extract primary and secondary keywords
        primary_keyword = validated_keywords[0]["keyword"] if validated_keywords else topic
        secondary_keywords = [k["keyword"] for k in validated_keywords[1:6]] if len(validated_keywords) > 1 else []

        # Get SEO metrics for primary keyword
        seo_metrics = validated_keywords[0] if validated_keywords else {
            "keyword": primary_keyword,
            "search_volume": 0,
            "competition": "unknown",
            "cpc": 0
        }

        # Calculate cost
        perplexity_cost = Decimal("0.20")  # Estimated
        dataforseo_cost = Decimal("0.02") if self.dataforseo.is_available() else Decimal("0")
        total_cost = perplexity_cost + dataforseo_cost

        result = {
            "topic": topic,
            "total_keywords_found": len(keywords),
            "validated_keywords": validated_keywords,
            "primary_keyword": primary_keyword,
            "secondary_keywords": secondary_keywords,
            "seo_metrics": seo_metrics,
            "cost": total_cost
        }

        logger.info(
            "keyword_researcher.complete",
            primary=primary_keyword,
            secondary_count=len(secondary_keywords),
            search_volume=seo_metrics.get("search_volume", 0),
            cost=float(total_cost)
        )

        return result
