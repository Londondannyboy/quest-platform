"""
Quest Platform - Authority Discovery System
Discovers high-DA niche authorities during research phase for SEO optimization

Key Insight: Link to high-DA competitors (60-89 DA) in our niche = authority by association
Strategy: Wikipedia/BBC (90+) in first paragraph, then niche authorities throughout
"""

import asyncio
import hashlib
from typing import Dict, List, Optional
from urllib.parse import urlparse
import httpx
import structlog
from bs4 import BeautifulSoup

from app.core.config import settings
from app.core.database import get_db

logger = structlog.get_logger(__name__)


class AuthorityDiscovery:
    """
    Discovers and validates high-authority domains in a specific niche

    Workflow:
    1. Serper: Get top 10 SERP results for target keyword
    2. DataForSEO: Batch query domain authority for all results
    3. Filter: Keep DA 60+ as "linkable niche authorities"
    4. Crawl: Visit each high-DA page, extract working deep URLs
    5. Cache: Store in validated_urls table with DA scores

    Cost: $0.10 per keyword (DataForSEO batch query)
    Cache: 30 days (DA doesn't change frequently)
    """

    def __init__(self):
        self.dataforseo_user = settings.DATAFORSEO_LOGIN
        self.dataforseo_pass = settings.DATAFORSEO_PASSWORD
        self.serper_api_key = settings.SERP_API_KEY

        # DA thresholds for classification
        self.DA_THRESHOLDS = {
            "ultra_high": 90,  # Wikipedia, BBC, Reuters
            "high": 70,        # Established authorities
            "medium": 60,      # Niche authorities (our target!)
            "low": 50,         # Acceptable
        }

        # Tier 1 pre-seeded authorities (always suggest)
        self.TIER1_DOMAINS = [
            "wikipedia.org", "en.wikipedia.org",
            "bbc.com", "bbc.co.uk", "reuters.com",
            "nytimes.com", "theguardian.com",
            "europa.eu", "oecd.org"
        ]

    async def discover_authorities(
        self,
        keyword: str,
        topic: str,
        target_site: str = "relocation"
    ) -> Dict:
        """
        Main entry point: Discover high-authority linkable sources for a topic

        Args:
            keyword: Primary keyword from KeywordResearcher
            topic: Full article topic
            target_site: relocation/placement/rainmaker

        Returns:
            {
                "niche_authorities": [
                    {
                        "domain": "nomadlist.com",
                        "da": 72,
                        "working_urls": ["https://nomadlist.com/lisbon", ...],
                        "reason": "Top 3 SERP + DA 72",
                        "authority_class": "high"
                    }
                ],
                "tier1_authorities": [
                    {
                        "domain": "wikipedia.org",
                        "da": 98,
                        "suggested_url": "https://en.wikipedia.org/wiki/Portugal",
                        "authority_class": "ultra_high"
                    }
                ],
                "cost": 0.10,
                "cache_hits": 3,
                "new_discoveries": 7
            }
        """
        logger.info(
            "authority_discovery.start",
            keyword=keyword,
            topic=topic
        )

        cost = 0.0
        cache_hits = 0
        new_discoveries = 0

        # Step 1: Check cache first
        cached_authorities = await self._get_cached_authorities(keyword)
        if cached_authorities:
            logger.info(
                "authority_discovery.cache_hit",
                keyword=keyword,
                cached_count=len(cached_authorities["niche_authorities"])
            )
            return cached_authorities

        # Step 2: Get SERP results from Serper
        serp_results = await self._get_serp_results(keyword)
        cost += 0.002  # Serper cost

        if not serp_results:
            logger.warning(
                "authority_discovery.no_serp_results",
                keyword=keyword
            )
            return await self._fallback_tier1_only(topic)

        # Step 3: Extract domains from SERP
        domains = self._extract_domains(serp_results)

        # Step 4: Batch query DataForSEO for DA scores
        da_scores = await self._get_domain_authority_batch(domains)
        cost += 0.10  # DataForSEO cost

        # Step 5: Filter high-DA domains (60+)
        high_da_domains = [
            d for d in da_scores
            if d["domain_authority"] >= self.DA_THRESHOLDS["medium"]
        ]

        # Step 6: For each high-DA domain, crawl for working deep URLs
        niche_authorities = []
        for domain_data in high_da_domains:
            # Find corresponding SERP result for this domain
            serp_url = self._find_serp_url(domain_data["domain"], serp_results)
            if not serp_url:
                continue

            # Crawl page for additional deep URLs
            deep_urls = await self._crawl_for_deep_urls(
                serp_url,
                domain_data["domain"],
                max_urls=5
            )

            # Classify authority level
            authority_class = self._classify_authority(domain_data["domain_authority"])

            niche_authorities.append({
                "domain": domain_data["domain"],
                "da": domain_data["domain_authority"],
                "working_urls": deep_urls,
                "reason": f"SERP position {domain_data.get('position', '?')} + DA {domain_data['domain_authority']}",
                "authority_class": authority_class,
                "backlinks": domain_data.get("backlinks", 0),
                "referring_domains": domain_data.get("referring_domains", 0)
            })

            new_discoveries += 1

            # Cache each discovered authority
            await self._cache_authority(domain_data, deep_urls, authority_class)

        # Step 7: Add Tier 1 authorities with suggested URLs
        tier1_authorities = await self._get_tier1_with_suggestions(topic)

        result = {
            "niche_authorities": niche_authorities,
            "tier1_authorities": tier1_authorities,
            "cost": cost,
            "cache_hits": cache_hits,
            "new_discoveries": new_discoveries,
            "keyword": keyword
        }

        # Cache the full result
        await self._cache_keyword_authorities(keyword, result)

        logger.info(
            "authority_discovery.complete",
            keyword=keyword,
            niche_count=len(niche_authorities),
            tier1_count=len(tier1_authorities),
            cost=cost
        )

        return result

    async def _get_serp_results(self, keyword: str) -> List[Dict]:
        """Get top 10 organic results from Serper"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://google.serper.dev/search",
                    headers={
                        "X-API-KEY": self.serper_api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "q": keyword,
                        "gl": "us",
                        "hl": "en",
                        "num": 10
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get("organic", [])
                else:
                    logger.warning(
                        "authority_discovery.serper_failed",
                        status=response.status_code
                    )
                    return []

        except Exception as e:
            logger.error(
                "authority_discovery.serper_error",
                error=str(e)
            )
            return []

    def _extract_domains(self, serp_results: List[Dict]) -> List[str]:
        """Extract unique domains from SERP results"""
        domains = []
        for result in serp_results:
            url = result.get("link", "")
            if url:
                domain = urlparse(url).netloc
                # Remove www prefix
                domain = domain.replace("www.", "")
                if domain and domain not in domains:
                    domains.append(domain)

        logger.info(
            "authority_discovery.domains_extracted",
            count=len(domains),
            domains=domains[:5]  # Log first 5
        )

        return domains

    async def _get_domain_authority_batch(self, domains: List[str]) -> List[Dict]:
        """
        Batch query DataForSEO for domain authority scores

        Endpoint: /v3/backlinks/domain_metrics
        Cost: $0.10 per batch (up to 50 domains)
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.dataforseo.com/v3/backlinks/domain_metrics",
                    auth=(self.dataforseo_user, self.dataforseo_pass),
                    json=[{
                        "targets": domains
                    }],
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.error(
                        "authority_discovery.dataforseo_failed",
                        status=response.status_code,
                        response=response.text[:200]
                    )
                    return []

                data = response.json()

                if not data.get("tasks") or not data["tasks"][0].get("result"):
                    logger.warning("authority_discovery.dataforseo_no_results")
                    return []

                results = []
                for item in data["tasks"][0]["result"]:
                    results.append({
                        "domain": item["target"],
                        "domain_authority": item.get("rank", 0),  # 0-100
                        "backlinks": item.get("backlinks", 0),
                        "referring_domains": item.get("referring_domains", 0),
                        "organic_traffic": item.get("organic_traffic", 0),
                        "first_seen": item.get("first_seen", "")
                    })

                logger.info(
                    "authority_discovery.dataforseo_success",
                    domains_checked=len(results),
                    avg_da=sum(r["domain_authority"] for r in results) / len(results) if results else 0
                )

                return results

        except Exception as e:
            logger.error(
                "authority_discovery.dataforseo_error",
                error=str(e)
            )
            return []

    def _find_serp_url(self, domain: str, serp_results: List[Dict]) -> Optional[str]:
        """Find the actual URL from SERP results for a given domain"""
        for result in serp_results:
            url = result.get("link", "")
            if domain in url:
                return url
        return None

    async def _crawl_for_deep_urls(
        self,
        start_url: str,
        domain: str,
        max_urls: int = 5
    ) -> List[str]:
        """
        Crawl a high-DA page to find additional working deep URLs on same domain

        Strategy:
        1. Fetch the SERP result page
        2. Extract all links to same domain
        3. Validate each link (HEAD request)
        4. Return up to max_urls working deep URLs
        """
        working_urls = [start_url]  # Always include the SERP URL

        try:
            async with httpx.AsyncClient() as client:
                # Fetch the page
                response = await client.get(
                    start_url,
                    timeout=10.0,
                    follow_redirects=True,
                    headers={"User-Agent": "QuestBot/1.0 (Research)"}
                )

                if response.status_code != 200:
                    return working_urls

                # Parse HTML for links
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all('a', href=True)

                # Extract URLs on same domain
                candidate_urls = []
                for link in links:
                    href = link['href']

                    # Make absolute URL
                    if href.startswith('/'):
                        href = f"https://{domain}{href}"
                    elif href.startswith('http'):
                        if domain not in href:
                            continue  # Different domain
                    else:
                        continue  # Relative or anchor

                    # Avoid duplicates and fragments
                    if href not in candidate_urls and '#' not in href:
                        candidate_urls.append(href)

                # Validate URLs (HEAD request)
                for url in candidate_urls[:15]:  # Check max 15 candidates
                    if len(working_urls) >= max_urls:
                        break

                    try:
                        head_response = await client.head(
                            url,
                            timeout=5.0,
                            follow_redirects=True
                        )

                        if head_response.status_code < 400:
                            working_urls.append(url)
                            logger.debug(
                                "authority_discovery.deep_url_found",
                                domain=domain,
                                url=url
                            )

                    except:
                        continue  # Skip invalid URLs

                logger.info(
                    "authority_discovery.crawl_complete",
                    domain=domain,
                    found_urls=len(working_urls)
                )

        except Exception as e:
            logger.warning(
                "authority_discovery.crawl_failed",
                domain=domain,
                error=str(e)
            )

        return working_urls

    def _classify_authority(self, da_score: int) -> str:
        """Classify authority level based on DA score"""
        if da_score >= self.DA_THRESHOLDS["ultra_high"]:
            return "ultra_high"
        elif da_score >= self.DA_THRESHOLDS["high"]:
            return "high"
        elif da_score >= self.DA_THRESHOLDS["medium"]:
            return "medium"
        else:
            return "low"

    async def _get_tier1_with_suggestions(self, topic: str) -> List[Dict]:
        """
        Get Tier 1 authorities (pre-seeded) with suggested URLs based on topic

        Example: For "Portugal Digital Nomad Visa", suggest:
        - https://en.wikipedia.org/wiki/Portugal
        - https://en.wikipedia.org/wiki/Digital_nomad
        """
        tier1 = []

        # Wikipedia suggestions (always ultra-high value)
        wiki_keywords = self._extract_wiki_keywords(topic)
        for keyword in wiki_keywords[:2]:  # Max 2 Wikipedia links
            tier1.append({
                "domain": "en.wikipedia.org",
                "da": 98,
                "suggested_url": f"https://en.wikipedia.org/wiki/{keyword}",
                "authority_class": "ultra_high",
                "reason": "Wikipedia - highest trust signal"
            })

        # BBC News (if topic is news-relevant)
        if any(word in topic.lower() for word in ["2025", "2024", "new", "changes"]):
            tier1.append({
                "domain": "bbc.com",
                "da": 96,
                "suggested_url": "https://bbc.com/news",
                "authority_class": "ultra_high",
                "reason": "BBC - recent news context"
            })

        return tier1

    def _extract_wiki_keywords(self, topic: str) -> List[str]:
        """Extract keywords suitable for Wikipedia URLs"""
        # Simple extraction: Capitalize words, replace spaces with underscores
        words = topic.split()

        # Common patterns for Wikipedia
        keywords = []

        # Country names
        countries = ["Portugal", "Spain", "Italy", "Germany", "Croatia", "Greece"]
        for country in countries:
            if country.lower() in topic.lower():
                keywords.append(country)

        # Concepts
        if "digital nomad" in topic.lower():
            keywords.append("Digital_nomad")
        if "visa" in topic.lower():
            keywords.append("Travel_visa")
        if "remote work" in topic.lower():
            keywords.append("Remote_work")

        return keywords

    async def _cache_authority(
        self,
        domain_data: Dict,
        working_urls: List[str],
        authority_class: str
    ):
        """Cache discovered authority in validated_urls table"""
        pool = get_db()

        try:
            async with pool.acquire() as conn:
                # For each working URL, insert/update in validated_urls
                for url in working_urls:
                    url_hash = hashlib.sha256(url.encode()).hexdigest()

                    await conn.execute("""
                        INSERT INTO validated_urls (
                            url, url_hash, domain,
                            domain_authority, backlinks_count, referring_domains_count,
                            authority_class, is_competitor, trust_score,
                            last_validated_at, last_da_check
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
                        ON CONFLICT (url_hash) DO UPDATE SET
                            domain_authority = EXCLUDED.domain_authority,
                            backlinks_count = EXCLUDED.backlinks_count,
                            referring_domains_count = EXCLUDED.referring_domains_count,
                            authority_class = EXCLUDED.authority_class,
                            is_competitor = EXCLUDED.is_competitor,
                            last_validated_at = NOW(),
                            last_da_check = NOW()
                    """,
                        url,
                        url_hash,
                        domain_data["domain"],
                        domain_data["domain_authority"],
                        domain_data.get("backlinks", 0),
                        domain_data.get("referring_domains", 0),
                        authority_class,
                        True,  # is_competitor (from SERP)
                        domain_data["domain_authority"],  # trust_score = DA for now
                    )

        except Exception as e:
            logger.error(
                "authority_discovery.cache_failed",
                error=str(e)
            )

    async def _cache_keyword_authorities(self, keyword: str, result: Dict):
        """Cache the full authority discovery result for this keyword"""
        # TODO: Implement keyword-level caching (30 days TTL)
        # For now, individual URLs are cached above
        pass

    async def _get_cached_authorities(self, keyword: str) -> Optional[Dict]:
        """Check if we have cached authority data for this keyword"""
        # TODO: Implement keyword-level cache lookup
        # For now, return None (always discover fresh)
        return None

    async def _fallback_tier1_only(self, topic: str) -> Dict:
        """Fallback: Return only Tier 1 authorities if SERP/DataForSEO fails"""
        tier1 = await self._get_tier1_with_suggestions(topic)

        return {
            "niche_authorities": [],
            "tier1_authorities": tier1,
            "cost": 0.0,
            "cache_hits": 0,
            "new_discoveries": 0,
            "fallback": True
        }
