"""
Multi-API Research Module
Integrates multiple research APIs with fallback chain
"""
import asyncio
import json
import base64
from typing import Dict, List, Optional, Any
from decimal import Decimal
from abc import ABC, abstractmethod

import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class ResearchProvider(ABC):
    """Base class for research providers"""

    @abstractmethod
    async def search(self, query: str) -> Dict:
        """Perform search and return results"""
        pass

    @abstractmethod
    def get_cost(self) -> Decimal:
        """Get cost per query"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if API is configured and available"""
        pass


class PerplexityProvider(ResearchProvider):
    """Perplexity Sonar API provider"""

    def __init__(self):
        self.api_key = settings.PERPLEXITY_API_KEY
        self.api_url = "https://api.perplexity.ai/chat/completions"

    async def search(self, query: str) -> Dict:
        """Search using Perplexity"""
        if not self.is_available():
            return {}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "sonar",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a research assistant. Provide comprehensive, factual information with citations.",
                },
                {"role": "user", "content": query},
            ],
            "temperature": 0.2,
            "max_tokens": 2000,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                return {
                    "provider": "perplexity",
                    "content": data["choices"][0]["message"]["content"],
                    "sources": data.get("citations", []),
                    "cost": self.get_cost()
                }
        except Exception as e:
            logger.error("perplexity_search_failed", error=str(e))
            return {}

    def get_cost(self) -> Decimal:
        return Decimal("0.20")

    def is_available(self) -> bool:
        return bool(self.api_key)


class TavilyProvider(ResearchProvider):
    """Tavily Search API provider"""

    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY
        self.api_url = "https://api.tavily.com/search"

    async def search(self, query: str) -> Dict:
        """Search using Tavily"""
        if not self.is_available():
            return {}

        headers = {
            "Content-Type": "application/json",
        }

        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "advanced",
            "include_answer": True,
            "include_raw_content": False,
            "max_results": 10,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                # Extract content from results
                sources = []
                content_parts = [data.get("answer", "")]

                for result in data.get("results", []):
                    content_parts.append(f"- {result.get('title', '')}: {result.get('snippet', '')}")
                    sources.append({
                        "url": result.get("url"),
                        "title": result.get("title")
                    })

                return {
                    "provider": "tavily",
                    "content": "\n\n".join(content_parts),
                    "sources": sources,
                    "cost": self.get_cost()
                }
        except Exception as e:
            logger.error("tavily_search_failed", error=str(e))
            return {}

    def get_cost(self) -> Decimal:
        return Decimal("0.10")

    def is_available(self) -> bool:
        return bool(self.api_key)


class FirecrawlProvider(ResearchProvider):
    """Firecrawl web scraping API"""

    def __init__(self):
        self.api_key = settings.FIRECRAWL_API_KEY
        self.api_url = "https://api.firecrawl.dev/v0/scrape"

    async def scrape(self, url: str) -> Dict:
        """Scrape a specific URL"""
        if not self.is_available():
            return {}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "url": url,
            "pageOptions": {
                "onlyMainContent": True,
                "includeHtml": False
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                return {
                    "provider": "firecrawl",
                    "content": data.get("data", {}).get("content", ""),
                    "sources": [{"url": url}],
                    "cost": self.get_cost()
                }
        except Exception as e:
            logger.error("firecrawl_scrape_failed", error=str(e), url=url)
            return {}

    async def search(self, query: str) -> Dict:
        """Firecrawl doesn't search, but can scrape URLs from query"""
        # Extract URLs from query if present
        import re
        urls = re.findall(r'https?://[^\s]+', query)

        if urls:
            results = []
            for url in urls[:3]:  # Limit to 3 URLs
                result = await self.scrape(url)
                if result:
                    results.append(result["content"])

            if results:
                return {
                    "provider": "firecrawl",
                    "content": "\n\n---\n\n".join(results),
                    "sources": [{"url": url} for url in urls],
                    "cost": self.get_cost() * len(results)
                }
        return {}

    def get_cost(self) -> Decimal:
        return Decimal("0.05")

    def is_available(self) -> bool:
        return bool(self.api_key)


class SerperProvider(ResearchProvider):
    """Serper.dev search results API"""

    def __init__(self):
        self.api_key = settings.SERPER_API_KEY
        self.api_url = "https://google.serper.dev/search"

    async def search(self, query: str) -> Dict:
        """Get search results from Serper.dev"""
        if not self.is_available():
            return {}

        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "q": query,
            "gl": "us",
            "hl": "en",
            "num": 10
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                # Extract search results
                content_parts = []
                sources = []

                for result in data.get("organic_results", []):
                    content_parts.append(
                        f"**{result.get('title')}**\n{result.get('snippet', '')}"
                    )
                    sources.append({
                        "url": result.get("link"),
                        "title": result.get("title")
                    })

                # Include featured snippet if available
                if "featured_snippet" in data:
                    snippet = data["featured_snippet"]
                    content_parts.insert(0, f"**Featured:** {snippet.get('snippet', '')}")

                return {
                    "provider": "serper",
                    "content": "\n\n".join(content_parts),
                    "sources": sources,
                    "cost": self.get_cost()
                }
        except Exception as e:
            logger.error("serper_search_failed", error=str(e))
            return {}

    def get_cost(self) -> Decimal:
        return Decimal("0.05")

    def is_available(self) -> bool:
        return bool(self.api_key)


class CritiqueLabsProvider(ResearchProvider):
    """Critique Labs fact-checking API"""

    def __init__(self):
        self.api_key = settings.CRITIQUE_LABS_API_KEY
        self.api_url = "https://api.critiquelabs.com/v1/fact-check"

    async def fact_check(self, content: str, sources: List[str] = None) -> Dict:
        """Fact-check content"""
        if not self.is_available():
            return {}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "content": content,
            "sources": sources or [],
            "check_citations": True,
            "check_facts": True
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                return {
                    "provider": "critique_labs",
                    "accuracy_score": data.get("accuracy_score", 0),
                    "issues": data.get("issues", []),
                    "suggestions": data.get("suggestions", []),
                    "verified_facts": data.get("verified_facts", []),
                    "cost": self.get_cost()
                }
        except Exception as e:
            logger.error("critique_labs_fact_check_failed", error=str(e))
            return {}

    async def search(self, query: str) -> Dict:
        """Critique Labs doesn't search but can validate claims"""
        # Extract factual claims from query
        result = await self.fact_check(query)
        if result:
            content = f"Fact-check results:\n"
            content += f"Accuracy Score: {result.get('accuracy_score', 0)}%\n"

            if result.get("verified_facts"):
                content += "\nVerified facts:\n"
                for fact in result["verified_facts"]:
                    content += f"- {fact}\n"

            return {
                "provider": "critique_labs",
                "content": content,
                "sources": [],
                "cost": self.get_cost()
            }
        return {}

    def get_cost(self) -> Decimal:
        return Decimal("0.15")

    def is_available(self) -> bool:
        return bool(self.api_key)


class LinkUpProvider(ResearchProvider):
    """Link Up link validation API"""

    def __init__(self):
        self.api_key = settings.LINKUP_API_KEY
        self.api_url = "https://api.linkup.so/v1/search"  # Fixed: was .dev, should be .so

    async def search(self, query: str) -> Dict:
        """Search with Link Up API"""
        if not self.is_available():
            return {}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "q": query,
            "depth": "deep",
            "outputType": "sourcedAnswer",
            "includeImages": False,
            "includeInlineCitations": False
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                # Extract results
                content_parts = []
                sources = []

                for result in data.get("results", []):
                    content_parts.append(
                        f"**{result.get('name')}**\n{result.get('snippet', '')}"
                    )
                    sources.append({
                        "url": result.get("url"),
                        "title": result.get("name")
                    })

                return {
                    "provider": "linkup",
                    "content": "\n\n".join(content_parts),
                    "sources": sources,
                    "cost": self.get_cost()
                }
        except Exception as e:
            logger.error("linkup_search_failed", error=str(e))
            return {}

    def get_cost(self) -> Decimal:
        return Decimal("0.08")

    def is_available(self) -> bool:
        return bool(self.api_key)


class DataForSEOProvider(ResearchProvider):
    """DataForSEO - Keyword validation and SEO metrics"""

    def __init__(self):
        self.login = settings.DATAFORSEO_LOGIN
        self.password = settings.DATAFORSEO_PASSWORD

        # Create Base64 auth for DataForSEO (uses Basic auth, not Bearer)
        if self.login and self.password:
            auth_string = f"{self.login}:{self.password}"
            self.auth = base64.b64encode(auth_string.encode()).decode()
        else:
            self.auth = None

        self.api_url = "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live"

    async def validate_keywords(self, keywords: List[str], location_code: int = 2826) -> Dict:
        """
        Validate keyword SEO value

        Args:
            keywords: List of keywords to validate
            location_code: Location code (2826 = UK, 2196 = Cyprus, 2840 = USA)

        Returns:
            {
                "keywords": [
                    {
                        "keyword": "relocation services Cyprus",
                        "search_volume": 1200,
                        "competition": "medium",
                        "cpc": 2.5
                    }
                ]
            }
        """
        if not self.is_available():
            logger.warning("dataforseo_not_configured")
            return {}

        headers = {
            "Authorization": f"Basic {self.auth}",
            "Content-Type": "application/json"
        }

        payload = [{
            "keywords": keywords[:20],  # Limit to 20 keywords
            "location_code": location_code,
            "language_code": "en"
        }]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                # Extract keyword data from response
                validated = []
                if data.get("tasks") and data["tasks"][0].get("result"):
                    results = data["tasks"][0]["result"]

                    for item in results:
                        if isinstance(item, dict) and item.get("keyword"):
                            validated.append({
                                "keyword": item["keyword"],
                                "search_volume": item.get("search_volume") or 0,
                                "competition": item.get("competition", "unknown"),
                                "cpc": item.get("cpc") or 0,
                                "competition_level": item.get("competition_level", "unknown")
                            })

                    # Sort by search volume
                    validated.sort(key=lambda x: x.get("search_volume", 0) or 0, reverse=True)

                logger.info("dataforseo_validation_complete", keywords_validated=len(validated))

                return {
                    "provider": "dataforseo",
                    "keywords": validated,
                    "cost": self.get_cost()
                }
        except Exception as e:
            logger.error("dataforseo_validation_failed", error=str(e))
            return {}

    async def search(self, query: str) -> Dict:
        """
        Search method for ResearchProvider interface
        Validates the query as a keyword
        """
        result = await self.validate_keywords([query])
        if result and result.get("keywords"):
            keyword_data = result["keywords"][0]
            content = f"""**SEO Metrics for "{query}":**
- Search Volume: {keyword_data.get('search_volume', 'N/A')}/month
- Competition: {keyword_data.get('competition', 'unknown')}
- CPC: ${keyword_data.get('cpc', 0):.2f}
- Competition Level: {keyword_data.get('competition_level', 'unknown')}"""

            return {
                "provider": "dataforseo",
                "content": content,
                "sources": [],
                "seo_data": keyword_data,
                "cost": self.get_cost()
            }
        return {}

    def get_cost(self) -> Decimal:
        return Decimal("0.02")

    def is_available(self) -> bool:
        return bool(self.login and self.password)


class MultiAPIResearch:
    """
    Orchestrates multiple research APIs with fallback chain
    Priority: Perplexity -> Tavily -> LinkUp -> SerpDev
    Specialized: Firecrawl (scraping), Critique Labs (fact-checking)

    Optimal Flow:
    1. Serper → Get top 10 competitor URLs
    2. Firecrawl → Scrape competitor content
    3. Perplexity → Gap analysis
    4. Tavily → Additional research
    """

    def __init__(self):
        self.providers = {
            "perplexity": PerplexityProvider(),
            "tavily": TavilyProvider(),
            "firecrawl": FirecrawlProvider(),
            "serper": SerperProvider(),
            "critique_labs": CritiqueLabsProvider(),
            "linkup": LinkUpProvider(),
            "dataforseo": DataForSEOProvider()
        }

        # Priority chain for fallback (tried in order)
        self.priority_chain = [
            "perplexity",
            "tavily",
            "linkup",
            "serper",
            "firecrawl"
        ]

        # Parallel groups for redundancy (each group runs simultaneously)
        self.research_groups = [
            ["perplexity", "tavily"],      # Primary AI research
            ["serper", "linkup"],           # Search engines
            ["firecrawl"]                   # Web scraping (if URLs in query)
        ]

    async def scrape_competitor_urls(self, urls: List[str], max_urls: int = 5) -> Dict:
        """
        Scrape competitor URLs using Firecrawl

        Args:
            urls: List of competitor URLs to scrape
            max_urls: Maximum number of URLs to scrape (default 5)

        Returns:
            Combined scraping results with content and sources
        """
        if not urls or not self.providers["firecrawl"].is_available():
            return {"content": "", "sources": [], "cost": Decimal("0")}

        firecrawl = self.providers["firecrawl"]
        results = []
        total_cost = Decimal("0")

        # Limit URLs to avoid excessive costs
        urls_to_scrape = urls[:max_urls]

        logger.info(
            "firecrawl.scraping_competitors",
            url_count=len(urls_to_scrape)
        )

        # Scrape each URL
        for url in urls_to_scrape:
            try:
                result = await firecrawl.scrape(url)
                if result and result.get("content"):
                    results.append({
                        "url": url,
                        "content": result["content"][:3000]  # Limit to 3000 chars per URL
                    })
                    total_cost += result.get("cost", Decimal("0"))
            except Exception as e:
                logger.warning("firecrawl.scrape_failed", url=url, error=str(e))
                continue

        if not results:
            return {"content": "", "sources": [], "cost": Decimal("0")}

        # Format content
        content_parts = []
        sources = []

        for i, result in enumerate(results, 1):
            content_parts.append(
                f"**Competitor #{i} Content ({result['url']}):**\n{result['content']}"
            )
            sources.append({"url": result["url"]})

        logger.info(
            "firecrawl.scraping_complete",
            urls_scraped=len(results),
            total_cost=float(total_cost)
        )

        return {
            "provider": "firecrawl",
            "content": "\n\n---\n\n".join(content_parts),
            "sources": sources,
            "cost": total_cost
        }

    async def research(
        self,
        query: str,
        use_all: bool = False,
        fact_check: bool = False
    ) -> Dict:
        """
        Perform research using available APIs

        Optimal Flow (when use_all=True):
        1. Serper → Get top 10 competitor URLs
        2. Firecrawl → Scrape competitor content
        3. Perplexity → Gap analysis
        4. Tavily → Additional research
        5. LinkUp → Validation (if not rate limited)

        Args:
            query: Research query
            use_all: Use all available APIs for comprehensive research
            fact_check: Run fact-checking on results

        Returns:
            Combined research results
        """
        results = []
        total_cost = Decimal("0")
        providers_used = []
        competitor_urls = []

        if use_all:
            # STEP 1: Get competitor URLs from Serper first
            if self.providers["serper"].is_available():
                logger.info("research.running_serper_first")
                serper_result = await self._search_with_provider("serper", self.providers["serper"], query)
                if serper_result:
                    results.append(serper_result)
                    total_cost += serper_result.get("cost", Decimal("0"))
                    providers_used.append("serper")

                    # Extract competitor URLs from Serper results
                    competitor_urls = [
                        source["url"] for source in serper_result.get("sources", [])
                        if source.get("url")
                    ]
                    logger.info("research.serper_urls_found", url_count=len(competitor_urls))

            # STEP 2: Scrape competitor URLs with Firecrawl
            if competitor_urls and self.providers["firecrawl"].is_available():
                logger.info("research.scraping_competitors", url_count=len(competitor_urls))
                firecrawl_result = await self.scrape_competitor_urls(competitor_urls, max_urls=5)
                if firecrawl_result and firecrawl_result.get("content"):
                    results.append(firecrawl_result)
                    total_cost += firecrawl_result.get("cost", Decimal("0"))
                    providers_used.append("firecrawl")
                    logger.info("research.firecrawl_success")

            # STEP 3: Run remaining providers in parallel
            tasks = []
            for name, provider in self.providers.items():
                # Skip already-run providers and critique_labs
                if name in ["serper", "firecrawl", "critique_labs"]:
                    continue
                if provider.is_available():
                    tasks.append(self._search_with_provider(name, provider, query))

            if tasks:
                logger.info("research.running_parallel_providers", count=len(tasks))
                provider_results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in provider_results:
                    if isinstance(result, dict) and result:
                        results.append(result)
                        total_cost += result.get("cost", Decimal("0"))
                        providers_used.append(result.get("provider"))
        else:
            # Use priority chain with fallback
            for provider_name in self.priority_chain:
                provider = self.providers[provider_name]
                if provider.is_available():
                    result = await self._search_with_provider(
                        provider_name, provider, query
                    )
                    if result:
                        results.append(result)
                        total_cost += result.get("cost", Decimal("0"))
                        providers_used.append(provider_name)
                        break  # Stop after first successful provider

        # Combine results
        combined_content = self._combine_results(results)

        # Fact-check if requested and available
        if fact_check and self.providers["critique_labs"].is_available():
            fact_result = await self.providers["critique_labs"].fact_check(
                combined_content,
                sources=[s["url"] for r in results for s in r.get("sources", []) if "url" in s]
            )
            if fact_result:
                combined_content += f"\n\n**Fact Check:**\n"
                combined_content += f"Accuracy Score: {fact_result.get('accuracy_score', 0)}%"
                total_cost += fact_result.get("cost", Decimal("0"))
                providers_used.append("critique_labs")

        logger.info(
            "multi_api_research.complete",
            providers_used=providers_used,
            total_cost=float(total_cost)
        )

        return {
            "content": combined_content,
            "sources": self._combine_sources(results),
            "providers_used": providers_used,
            "total_cost": total_cost
        }

    async def _search_with_provider(
        self,
        name: str,
        provider: ResearchProvider,
        query: str
    ) -> Optional[Dict]:
        """Search with a specific provider"""
        try:
            logger.debug(f"research.trying_provider", provider=name)
            result = await provider.search(query)
            if result:
                logger.info(f"research.provider_success", provider=name)
                return result
            else:
                logger.warning(f"research.provider_empty", provider=name)
                return None
        except Exception as e:
            logger.error(
                f"research.provider_failed",
                provider=name,
                error=str(e)
            )
            return None

    def _combine_results(self, results: List[Dict]) -> str:
        """Combine content from multiple providers"""
        if not results:
            return ""

        content_parts = []
        for result in results:
            provider = result.get("provider", "unknown")
            content = result.get("content", "")
            if content:
                content_parts.append(f"**Source: {provider.title()}**\n{content}")

        return "\n\n---\n\n".join(content_parts)

    def _combine_sources(self, results: List[Dict]) -> List[Dict]:
        """Combine and deduplicate sources"""
        all_sources = []
        seen_urls = set()

        for result in results:
            for source in result.get("sources", []):
                # Handle both string URLs and dict sources
                if isinstance(source, str):
                    url = source
                    source_dict = {"url": url}
                else:
                    url = source.get("url")
                    source_dict = source

                if url and url not in seen_urls:
                    all_sources.append(source_dict)
                    seen_urls.add(url)

        return all_sources

    def score_research_quality(self, content: str, sources: List[Dict]) -> Dict:
        """
        Score research quality to determine if it's good enough to proceed
        Returns score 0-100 and breakdown of metrics
        """
        import re

        # Count metrics
        word_count = len(content.split()) if content else 0
        source_count = len(sources)

        # Count external links in content
        external_links = len(re.findall(r'https?://[^\s]+', content)) if content else 0

        # Score components (each out of 25)
        word_score = min(25, (word_count / 500) * 25)  # 500+ words = full score
        source_score = min(25, (source_count / 5) * 25)  # 5+ sources = full score
        link_score = min(25, (external_links / 10) * 25)  # 10+ links = full score
        content_score = 25 if content and len(content) > 100 else 0  # Has substantial content

        total_score = word_score + source_score + link_score + content_score

        # Minimum threshold: 60/100 to proceed
        is_sufficient = total_score >= 60

        return {
            "total_score": round(total_score),
            "is_sufficient": is_sufficient,
            "metrics": {
                "word_count": word_count,
                "source_count": source_count,
                "external_links": external_links,
                "word_score": round(word_score),
                "source_score": round(source_score),
                "link_score": round(link_score),
                "content_score": round(content_score)
            },
            "threshold": 60,
            "recommendation": "Proceed with content generation" if is_sufficient else "Insufficient research data"
        }