"""
Quest Platform v2.5 - TemplateDetector Agent
Analyzes SERP results and scrapes competitors to detect content archetypes and recommend templates
"""

import hashlib
import re
import json
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta

import structlog
from bs4 import BeautifulSoup

from app.core.config import settings
from app.core.database import get_db
from app.core.research_apis import SerperProvider, FirecrawlProvider

logger = structlog.get_logger(__name__)


class TemplateDetector:
    """
    Template Detector Agent: Analyze SERP winners to detect archetypes and recommend templates

    Workflow:
    1. Check cache (serp_intelligence table with 30-day TTL)
    2. If cache miss:
       a. Serper.dev → Get top 10 Google SERP results
       b. Firecrawl → Scrape top 3-5 competitor pages
       c. Multi-dimensional archetype detection algorithm
       d. Recommendation engine → Select archetype + template
       e. Store in cache
    3. Return recommendations with confidence score

    Cost: ~$0.08 per keyword analysis (Serper $0.05 + Firecrawl $0.05 for 1 URL, up to $0.30 for 5 URLs)
    """

    def __init__(self):
        self.serper = SerperProvider()
        self.firecrawl = FirecrawlProvider()

        # Archetype detection thresholds
        self.archetype_thresholds = {
            "skyscraper": {
                "min_word_count": 6000,
                "min_sections": 10,
                "min_modules": 8,
                "min_internal_links": 20
            },
            "cluster_hub": {
                "min_word_count": 3000,
                "min_sections": 6,
                "min_modules": 5,
                "min_internal_links": 8
            },
            "deep_dive": {
                "min_word_count": 2500,
                "min_sections": 6,
                "min_modules": 6,
                "min_internal_links": 2
            },
            "comparison_matrix": {
                "min_word_count": 2000,
                "min_sections": 5,
                "min_modules": 4,
                "min_internal_links": 3
            },
            "news_hub": {
                "min_word_count": 1500,
                "min_sections": 4,
                "min_modules": 3,
                "min_internal_links": 2
            }
        }

    async def run(
        self,
        keyword: str,
        use_cache: bool = True,
        max_competitors: int = 3
    ) -> Dict:
        """
        Detect archetype and recommend template for a given keyword

        Args:
            keyword: Target keyword/topic to analyze
            use_cache: Check cache before running analysis
            max_competitors: Number of competitor pages to scrape (1-5)

        Returns:
            {
                "detected_archetype": "skyscraper",
                "recommended_template": "ultimate_guide",
                "confidence_score": 0.85,
                "target_word_count": 8500,
                "target_module_count": 14,
                "common_modules": ["tldr", "faq", "calculator"],
                "serp_results": {...},
                "competitor_analysis": [...],
                "cost": Decimal("0.20")
            }
        """
        logger.info("template_detector.start", keyword=keyword, use_cache=use_cache)

        # Step 1: Check cache
        if use_cache:
            cached = await self._check_cache(keyword)
            if cached:
                logger.info("template_detector.cache_hit", keyword=keyword)
                return cached

        # Step 2: SERP analysis with Serper.dev
        serp_result = await self._analyze_serp(keyword)
        if not serp_result or not serp_result.get("competitor_urls"):
            logger.warning("template_detector.no_serp_results", keyword=keyword)
            return self._default_recommendation(keyword)

        # Step 3: Scrape competitors with Firecrawl
        competitor_urls = serp_result["competitor_urls"][:max_competitors]
        scraped_competitors = await self._scrape_competitors(competitor_urls)

        if not scraped_competitors:
            logger.warning("template_detector.no_competitors_scraped", keyword=keyword)
            return self._default_recommendation(keyword)

        # Step 4: Multi-dimensional archetype detection
        archetype_scores = self._detect_archetype(scraped_competitors)

        # Step 5: Template recommendation
        detected_archetype = max(archetype_scores, key=archetype_scores.get)
        recommended_template = self._recommend_template(detected_archetype, keyword)
        confidence_score = archetype_scores[detected_archetype]

        # Step 6: Calculate targets and extract modules
        target_word_count = self._calculate_target_word_count(scraped_competitors)
        target_module_count = self._calculate_target_module_count(scraped_competitors)
        common_modules = self._extract_common_modules(scraped_competitors)

        # Step 7: Calculate total cost
        total_cost = Decimal("0.05")  # Serper
        total_cost += Decimal(str(len(scraped_competitors))) * Decimal("0.05")  # Firecrawl per URL

        # Step 8: Build result
        result = {
            "detected_archetype": detected_archetype,
            "recommended_template": recommended_template,
            "confidence_score": round(confidence_score, 2),
            "target_word_count": target_word_count,
            "target_module_count": target_module_count,
            "common_modules": common_modules,
            "archetype_scores": {k: round(v, 2) for k, v in archetype_scores.items()},
            "serp_results": serp_result,
            "competitor_analysis": [
                {
                    "url": comp["url"],
                    "position": comp["position"],
                    "word_count": comp["word_count"],
                    "modules_found": comp["modules_found"]
                }
                for comp in scraped_competitors
            ],
            "cost": total_cost
        }

        # Step 9: Store in cache
        await self._store_cache(keyword, result, serp_result, scraped_competitors)

        logger.info(
            "template_detector.complete",
            keyword=keyword,
            archetype=detected_archetype,
            template=recommended_template,
            confidence=confidence_score,
            cost=float(total_cost)
        )

        return result

    async def _check_cache(self, keyword: str) -> Optional[Dict]:
        """Check if SERP analysis exists in cache and is still valid"""
        keyword_hash = hashlib.md5(keyword.encode()).hexdigest()

        async with get_db() as db:
            result = await db.fetchrow(
                """
                SELECT
                    detected_archetype,
                    recommended_template,
                    confidence_score,
                    avg_word_count as target_word_count,
                    avg_module_count as target_module_count,
                    common_modules,
                    serp_results,
                    cache_hits
                FROM serp_intelligence
                WHERE keyword_hash = $1
                AND expires_at > NOW()
                """,
                keyword_hash
            )

            if result:
                # Increment cache hit counter
                await db.execute(
                    """
                    UPDATE serp_intelligence
                    SET cache_hits = cache_hits + 1,
                        last_accessed = NOW()
                    WHERE keyword_hash = $1
                    """,
                    keyword_hash
                )

                return {
                    "detected_archetype": result["detected_archetype"],
                    "recommended_template": result["recommended_template"],
                    "confidence_score": float(result["confidence_score"]) if result["confidence_score"] else 0.0,
                    "target_word_count": result["target_word_count"],
                    "target_module_count": result["target_module_count"],
                    "common_modules": result["common_modules"] or [],
                    "serp_results": result["serp_results"],
                    "cost": Decimal("0"),  # Cache hit = no cost
                    "from_cache": True,
                    "cache_hits": result["cache_hits"] + 1
                }

        return None

    async def _analyze_serp(self, keyword: str) -> Optional[Dict]:
        """Use Serper.dev to get top 10 SERP results"""
        if not self.serper.is_available():
            logger.warning("template_detector.serper_unavailable")
            return None

        try:
            result = await self.serper.search(keyword)

            if not result or not result.get("sources"):
                return None

            # Extract competitor URLs from sources
            competitor_urls = []
            for i, source in enumerate(result["sources"][:10], 1):
                if source.get("url"):
                    competitor_urls.append({
                        "url": source["url"],
                        "title": source.get("title", ""),
                        "position": i
                    })

            return {
                "competitor_urls": competitor_urls,
                "raw_serp": result
            }

        except Exception as e:
            logger.error("template_detector.serper_failed", error=str(e))
            return None

    async def _scrape_competitors(self, competitor_urls: List[Dict]) -> List[Dict]:
        """Scrape competitor pages with Firecrawl and analyze content"""
        if not self.firecrawl.is_available():
            logger.warning("template_detector.firecrawl_unavailable")
            return []

        scraped = []

        for comp in competitor_urls:
            try:
                result = await self.firecrawl.scrape(comp["url"])

                if not result or not result.get("content"):
                    logger.warning("template_detector.scrape_empty", url=comp["url"])
                    continue

                content = result["content"]

                # Analyze scraped content
                analysis = self._analyze_content(content, comp["url"])
                analysis["position"] = comp["position"]
                analysis["title"] = comp["title"]

                scraped.append(analysis)

                logger.info(
                    "template_detector.scraped",
                    url=comp["url"],
                    word_count=analysis["word_count"],
                    modules=len(analysis["modules_found"])
                )

            except Exception as e:
                logger.error("template_detector.scrape_failed", url=comp["url"], error=str(e))
                continue

        return scraped

    def _analyze_content(self, content: str, url: str) -> Dict:
        """Analyze scraped content to extract metrics"""

        # Word count
        word_count = len(content.split())

        # Section count (count H2/H3 headers)
        section_count = len(re.findall(r'^#{2,3}\s+', content, re.MULTILINE))

        # Average section depth (words per section)
        avg_section_depth = word_count // max(section_count, 1)

        # Module detection (based on common patterns)
        modules_found = []

        # TL;DR
        if re.search(r'(tl;?dr|key\s+takeaways|summary)', content, re.IGNORECASE):
            modules_found.append("tldr")

        # FAQ
        if re.search(r'(frequently\s+asked|faq|q:?\s+|question)', content, re.IGNORECASE):
            modules_found.append("faq")

        # Calculator/Tool
        if re.search(r'(calculator|tool|estimate|compute)', content, re.IGNORECASE):
            modules_found.append("calculator")

        # Comparison table
        if re.search(r'(\||comparison|vs\.?|versus)', content, re.IGNORECASE):
            modules_found.append("comparison_table")

        # Step-by-step
        if re.search(r'(step\s+\d+|how\s+to|process)', content, re.IGNORECASE):
            modules_found.append("step_by_step")

        # Expert quotes
        if re.search(r'(according\s+to|expert|says|quoted|interview)', content, re.IGNORECASE):
            modules_found.append("expert_quote")

        # Case study
        if re.search(r'(case\s+study|example|success\s+story|real[-\s]world)', content, re.IGNORECASE):
            modules_found.append("case_study")

        # Stats/data
        if re.search(r'(\d+%|\d+,\d+|statistics|data\s+shows)', content, re.IGNORECASE):
            modules_found.append("stats_callout")

        # Internal links (estimate based on markdown links)
        internal_links_count = len(re.findall(r'\[([^\]]+)\]\((?!https?://)[^\)]+\)', content))

        # External links
        external_links_count = len(re.findall(r'\[([^\]]+)\]\(https?://[^\)]+\)', content))

        # E-E-A-T signals
        has_expert_quotes = "expert_quote" in modules_found
        has_case_studies = "case_study" in modules_found
        has_author_bio = bool(re.search(r'(author|written\s+by|about\s+the\s+author)', content, re.IGNORECASE))

        # Citation count (look for [1], [2] style citations or footnotes)
        citations_count = len(re.findall(r'\[\d+\]', content))

        return {
            "url": url,
            "word_count": word_count,
            "section_count": section_count,
            "avg_section_depth": avg_section_depth,
            "modules_found": modules_found,
            "module_count": len(modules_found),
            "internal_links_count": internal_links_count,
            "external_links_count": external_links_count,
            "has_expert_quotes": has_expert_quotes,
            "has_case_studies": has_case_studies,
            "has_author_bio": has_author_bio,
            "citations_count": citations_count,
            "scraped_content": content[:5000]  # Store first 5000 chars
        }

    def _detect_archetype(self, scraped_competitors: List[Dict]) -> Dict[str, float]:
        """
        Multi-dimensional archetype detection algorithm

        Returns archetype scores (0-1) for each archetype based on competitor analysis
        """
        if not scraped_competitors:
            return {"skyscraper": 0.5}  # Default

        # Calculate average metrics across top 3 competitors
        avg_word_count = sum(c["word_count"] for c in scraped_competitors) // len(scraped_competitors)
        avg_section_count = sum(c["section_count"] for c in scraped_competitors) // len(scraped_competitors)
        avg_module_count = sum(c["module_count"] for c in scraped_competitors) // len(scraped_competitors)
        avg_internal_links = sum(c["internal_links_count"] for c in scraped_competitors) // len(scraped_competitors)

        # Score each archetype (0-1)
        scores = {}

        for archetype, thresholds in self.archetype_thresholds.items():
            score = 0.0

            # Word count score (25%)
            if avg_word_count >= thresholds["min_word_count"]:
                score += 0.25
            else:
                score += 0.25 * (avg_word_count / thresholds["min_word_count"])

            # Section count score (25%)
            if avg_section_count >= thresholds["min_sections"]:
                score += 0.25
            else:
                score += 0.25 * (avg_section_count / thresholds["min_sections"])

            # Module count score (25%)
            if avg_module_count >= thresholds["min_modules"]:
                score += 0.25
            else:
                score += 0.25 * (avg_module_count / thresholds["min_modules"])

            # Internal links score (25%)
            if avg_internal_links >= thresholds["min_internal_links"]:
                score += 0.25
            else:
                score += 0.25 * (avg_internal_links / thresholds["min_internal_links"])

            scores[archetype] = min(1.0, score)  # Cap at 1.0

        return scores

    def _recommend_template(self, archetype: str, keyword: str) -> str:
        """
        Recommend visual template based on archetype and keyword pattern

        Template selection logic:
        - Archetype defines strategy (depth)
        - Keyword pattern suggests visual expectation
        """

        # Keyword pattern detection
        keyword_lower = keyword.lower()

        # Listicle patterns
        if re.search(r'(top\s+\d+|best\s+\d+|\d+\s+best)', keyword_lower):
            if archetype in ["skyscraper", "comparison_matrix"]:
                return "listicle"

        # Comparison patterns
        if re.search(r'(vs\.?|versus|compare|comparison)', keyword_lower):
            return "comparison"

        # Location patterns
        if re.search(r'(in\s+\w+|city|country|portugal|spain|cyprus)', keyword_lower):
            if archetype in ["skyscraper", "deep_dive"]:
                return "location_guide"

        # How-to patterns
        if re.search(r'(how\s+to|guide\s+to|step\s+by\s+step)', keyword_lower):
            if archetype == "deep_dive":
                return "deep_dive_tutorial"

        # Default: Ultimate Guide (most versatile template)
        return "ultimate_guide"

    def _calculate_target_word_count(self, scraped_competitors: List[Dict]) -> int:
        """Calculate target word count (average of top 3 + 10% buffer)"""
        if not scraped_competitors:
            return 3000  # Default

        avg = sum(c["word_count"] for c in scraped_competitors) // len(scraped_competitors)
        return int(avg * 1.1)  # 10% longer than average competitor

    def _calculate_target_module_count(self, scraped_competitors: List[Dict]) -> int:
        """Calculate target module count (average of top 3 + 2 modules)"""
        if not scraped_competitors:
            return 8  # Default

        avg = sum(c["module_count"] for c in scraped_competitors) // len(scraped_competitors)
        return avg + 2  # 2 more modules than average competitor

    def _extract_common_modules(self, scraped_competitors: List[Dict]) -> List[str]:
        """Extract modules that appear in 2+ competitors"""
        module_counts = {}

        for comp in scraped_competitors:
            for module in comp["modules_found"]:
                module_counts[module] = module_counts.get(module, 0) + 1

        # Return modules appearing in 2+ competitors
        threshold = max(2, len(scraped_competitors) // 2)
        common = [module for module, count in module_counts.items() if count >= threshold]

        # Always include these essential modules
        essential = ["tldr", "faq"]
        for module in essential:
            if module not in common:
                common.append(module)

        return common

    def _default_recommendation(self, keyword: str) -> Dict:
        """Return default recommendation if SERP analysis fails"""
        logger.warning("template_detector.using_default", keyword=keyword)

        return {
            "detected_archetype": "skyscraper",
            "recommended_template": "ultimate_guide",
            "confidence_score": 0.5,
            "target_word_count": 3000,
            "target_module_count": 8,
            "common_modules": ["tldr", "faq", "step_by_step"],
            "archetype_scores": {"skyscraper": 0.5},
            "serp_results": None,
            "competitor_analysis": [],
            "cost": Decimal("0"),
            "from_default": True
        }

    async def _store_cache(
        self,
        keyword: str,
        result: Dict,
        serp_result: Dict,
        scraped_competitors: List[Dict]
    ):
        """Store analysis results in cache"""
        keyword_hash = hashlib.md5(keyword.encode()).hexdigest()

        async with get_db() as db:
            # Insert into serp_intelligence
            serp_id = await db.fetchval(
                """
                INSERT INTO serp_intelligence (
                    keyword,
                    keyword_hash,
                    serp_results,
                    detected_archetype,
                    recommended_template,
                    confidence_score,
                    avg_word_count,
                    avg_module_count,
                    common_modules,
                    target_word_count,
                    target_module_count,
                    cache_hits,
                    expires_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, 0, NOW() + INTERVAL '30 days')
                ON CONFLICT (keyword_hash) DO UPDATE SET
                    detected_archetype = EXCLUDED.detected_archetype,
                    recommended_template = EXCLUDED.recommended_template,
                    confidence_score = EXCLUDED.confidence_score,
                    avg_word_count = EXCLUDED.avg_word_count,
                    avg_module_count = EXCLUDED.avg_module_count,
                    common_modules = EXCLUDED.common_modules,
                    target_word_count = EXCLUDED.target_word_count,
                    target_module_count = EXCLUDED.target_module_count,
                    expires_at = NOW() + INTERVAL '30 days'
                RETURNING id
                """,
                keyword,
                keyword_hash,
                json.dumps(serp_result),
                result["detected_archetype"],
                result["recommended_template"],
                result["confidence_score"],
                result["target_word_count"],
                result["target_module_count"],
                result["common_modules"],
                result["target_word_count"],
                result["target_module_count"]
            )

            # Insert scraped competitors
            for comp in scraped_competitors:
                await db.execute(
                    """
                    INSERT INTO scraped_competitors (
                        serp_intelligence_id,
                        url,
                        position,
                        word_count,
                        section_count,
                        avg_section_depth,
                        modules_found,
                        module_count,
                        internal_links_count,
                        external_links_count,
                        has_expert_quotes,
                        has_case_studies,
                        has_author_bio,
                        citations_count,
                        scraped_content
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                    """,
                    serp_id,
                    comp["url"],
                    comp["position"],
                    comp["word_count"],
                    comp["section_count"],
                    comp["avg_section_depth"],
                    comp["modules_found"],
                    comp["module_count"],
                    comp["internal_links_count"],
                    comp["external_links_count"],
                    comp["has_expert_quotes"],
                    comp["has_case_studies"],
                    comp["has_author_bio"],
                    comp["citations_count"],
                    comp["scraped_content"]
                )

        logger.info("template_detector.cache_stored", keyword=keyword, serp_id=str(serp_id))
