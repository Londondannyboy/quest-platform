"""
Quest Platform v2.3 - Link Validation System
Validates internal and external links before content generation
"""

import asyncio
from typing import Dict, List, Optional
import httpx
import structlog
from app.core.database import get_db

logger = structlog.get_logger(__name__)


class LinkValidator:
    """
    Pre-validates internal and external links for content generation
    Implements Option 3: Pass validated links to ContentAgent
    """

    def __init__(self):
        self.timeout = 5.0  # 5 second timeout for external checks
        self.internal_link_cache = {}

    async def load_existing_articles(self) -> Dict[str, str]:
        """
        Load all existing article slugs and titles for internal linking

        Returns:
            Dict mapping slugs to titles
        """
        pool = get_db()
        async with pool.acquire() as conn:
            articles = await conn.fetch("""
                SELECT slug, title, keywords
                FROM articles
                WHERE status IN ('published', 'draft')
                ORDER BY created_at DESC
            """)

            article_map = {}
            for article in articles:
                article_map[article['slug']] = {
                    'title': article['title'],
                    'keywords': article['keywords'] or []
                }

            self.internal_link_cache = article_map
            logger.info(
                "link_validator.loaded_articles",
                count=len(article_map)
            )

            return article_map

    async def validate_external_url(self, url: str) -> Dict:
        """
        Check if an external URL is accessible

        Args:
            url: URL to check

        Returns:
            Dict with validation result
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.head(
                    url,
                    timeout=self.timeout,
                    follow_redirects=True
                )

                is_valid = response.status_code < 400

                return {
                    'url': url,
                    'valid': is_valid,
                    'status_code': response.status_code,
                    'final_url': str(response.url) if response.url != url else url
                }
        except Exception as e:
            logger.warning(
                "link_validator.external_check_failed",
                url=url,
                error=str(e)
            )
            return {
                'url': url,
                'valid': False,
                'error': str(e)
            }

    async def validate_external_urls(self, urls: List[str]) -> List[Dict]:
        """
        Validate multiple external URLs in parallel

        Args:
            urls: List of URLs to check

        Returns:
            List of validation results
        """
        tasks = [self.validate_external_url(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        validated = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                validated.append({
                    'url': urls[i],
                    'valid': False,
                    'error': str(result)
                })
            else:
                validated.append(result)

        valid_count = sum(1 for r in validated if r.get('valid', False))
        logger.info(
            "link_validator.external_validation_complete",
            total=len(urls),
            valid=valid_count,
            invalid=len(urls) - valid_count
        )

        return validated

    def suggest_internal_links(self, topic: str, max_links: int = 5) -> List[Dict]:
        """
        Suggest relevant internal links based on topic

        Args:
            topic: Article topic
            max_links: Maximum number of links to suggest

        Returns:
            List of suggested internal links
        """
        if not self.internal_link_cache:
            return []

        # Simple keyword matching for now
        topic_words = set(topic.lower().split())
        suggestions = []

        for slug, data in self.internal_link_cache.items():
            title_words = set(data['title'].lower().split())
            keywords = set(kw.lower() for kw in data.get('keywords', []))

            # Calculate relevance score
            title_overlap = len(topic_words & title_words)
            keyword_overlap = len(topic_words & keywords)
            score = title_overlap * 2 + keyword_overlap

            if score > 0:
                suggestions.append({
                    'slug': slug,
                    'title': data['title'],
                    'score': score,
                    'link': f"/{slug}"
                })

        # Sort by relevance and limit
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        top_suggestions = suggestions[:max_links]

        logger.info(
            "link_validator.internal_suggestions",
            topic=topic,
            found=len(suggestions),
            returned=len(top_suggestions)
        )

        return top_suggestions

    async def prepare_link_context(
        self,
        topic: str,
        research_sources: List[str]
    ) -> Dict:
        """
        Prepare validated link context for ContentAgent

        Args:
            topic: Article topic
            research_sources: Source URLs from research

        Returns:
            Dict with validated internal and external links
        """
        # Load existing articles for internal linking
        await self.load_existing_articles()

        # Validate external sources
        validated_external = await self.validate_external_urls(research_sources)

        # Get only valid external links
        valid_external = [
            r for r in validated_external
            if r.get('valid', False)
        ]

        # Suggest internal links
        internal_suggestions = self.suggest_internal_links(topic)

        context = {
            'external_links': valid_external[:12],  # Max 12 external links
            'internal_links': internal_suggestions[:5],  # Max 5 internal links
            'total_articles': len(self.internal_link_cache),
            'validation_summary': {
                'external_checked': len(research_sources),
                'external_valid': len(valid_external),
                'internal_available': len(self.internal_link_cache),
                'internal_suggested': len(internal_suggestions)
            }
        }

        logger.info(
            "link_validator.context_prepared",
            topic=topic,
            external_valid=len(valid_external),
            internal_suggested=len(internal_suggestions)
        )

        return context