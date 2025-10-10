"""
Quest Platform - CitationVerifierAgent
Two-pass citation verification to prevent hallucinated sources

Based on Reddit research: https://www.reddit.com/r/PromptEngineering/comments/...
Implements multi-model chain verification for citation accuracy
"""

import re
import json
from decimal import Decimal
from typing import Dict, List, Optional
from urllib.parse import urlparse

from anthropic import AsyncAnthropic
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class CitationVerifierAgent:
    """
    Citation Verifier Agent: Two-pass verification to prevent hallucinated sources

    Workflow:
    1. Extract all citations [N] and References from article
    2. Verify each reference URL exists in research sources
    3. Use separate model context to verify claim → citation match
    4. Return confidence scores and flag suspicious citations

    Cost: ~$0.01 per article (cheap insurance against fake sources)
    """

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-5-20250929"

    async def verify_citations(
        self,
        article: Dict,
        research_sources: List[Dict]
    ) -> Dict:
        """
        Verify all citations in article against research sources

        Args:
            article: Article with content and citations
            research_sources: List of research sources with URLs

        Returns:
            {
                "verification_passed": bool,
                "total_citations": int,
                "verified_citations": int,
                "unverified_citations": List[str],
                "suspicious_urls": List[str],
                "confidence_score": 0.0-1.0,
                "cost": Decimal
            }
        """
        logger.info("citation_verifier.start")

        content = article.get("content", "")

        # Step 1: Extract citations and references
        extraction = self._extract_citations_and_references(content)

        # Step 2: Verify URLs exist in research sources
        url_verification = self._verify_urls_against_sources(
            extraction["references"],
            research_sources
        )

        # Step 3: Verify claims match citations (using separate model context)
        claim_verification = await self._verify_claims_match_citations(
            content,
            extraction,
            research_sources
        )

        # Step 4: Calculate confidence score
        total_refs = len(extraction["references"])
        verified_urls = len(url_verification["verified_urls"])
        verified_claims = len(claim_verification["verified_claims"])

        confidence_score = 0.0
        if total_refs > 0:
            url_score = verified_urls / total_refs
            claim_score = verified_claims / total_refs
            confidence_score = (url_score * 0.6) + (claim_score * 0.4)

        verification_passed = (
            confidence_score >= 0.7 and  # 70% confidence minimum
            len(url_verification["fake_urls"]) == 0  # No fake URLs
        )

        result = {
            "verification_passed": verification_passed,
            "total_citations": len(extraction["inline_citations"]),
            "total_references": total_refs,
            "verified_urls": verified_urls,
            "verified_claims": verified_claims,
            "unverified_references": url_verification["unverified_urls"],
            "fake_urls": url_verification["fake_urls"],
            "suspicious_claims": claim_verification["suspicious_claims"],
            "confidence_score": confidence_score,
            "cost": claim_verification["cost"]
        }

        logger.info(
            "citation_verifier.complete",
            passed=verification_passed,
            confidence=confidence_score,
            verified_urls=verified_urls,
            total_refs=total_refs
        )

        return result

    def _extract_citations_and_references(self, content: str) -> Dict:
        """
        Extract inline citations [1], [2] and References section

        Returns:
            {
                "inline_citations": ["[1]", "[2]", ...],
                "references": [
                    {"number": 1, "text": "Source Name", "url": "https://..."},
                    ...
                ]
            }
        """
        # Extract inline citations
        inline_citations = re.findall(r'\[(\d+)\]', content)
        unique_citations = sorted(set(inline_citations), key=int)

        # Extract References section
        references = []
        refs_match = re.search(r'##\s*References?\s*\n(.*?)(?:\n##|\Z)', content, re.DOTALL | re.IGNORECASE)

        if refs_match:
            refs_text = refs_match.group(1)
            # Match format: [1] Source Name - URL or [1] Source Name (URL)
            ref_pattern = r'\[(\d+)\]\s*([^\n\-\(]+?)(?:\s*[-\(]\s*|\s+)(https?://[^\s\)]+)'
            matches = re.findall(ref_pattern, refs_text)

            for num, title, url in matches:
                references.append({
                    "number": int(num),
                    "text": title.strip(),
                    "url": url.strip()
                })

        logger.info(
            "citation_verifier.extraction",
            inline_count=len(unique_citations),
            references_count=len(references)
        )

        return {
            "inline_citations": unique_citations,
            "references": references
        }

    def _verify_urls_against_sources(
        self,
        references: List[Dict],
        research_sources: List[Dict]
    ) -> Dict:
        """
        Verify each reference URL exists in research sources

        Returns:
            {
                "verified_urls": List[str],
                "unverified_urls": List[str],
                "fake_urls": List[str]
            }
        """
        # Extract all URLs from research sources
        research_urls = set()
        for source in research_sources:
            if isinstance(source, dict):
                if "url" in source:
                    research_urls.add(source["url"])
                if "sources" in source and isinstance(source["sources"], list):
                    for s in source["sources"]:
                        if isinstance(s, dict) and "url" in s:
                            research_urls.add(s["url"])
                        elif isinstance(s, str):
                            research_urls.add(s)

        verified_urls = []
        unverified_urls = []
        fake_urls = []

        for ref in references:
            url = ref.get("url", "")

            # Check if URL is valid
            try:
                parsed = urlparse(url)
                if not parsed.scheme or not parsed.netloc:
                    fake_urls.append(url)
                    continue
            except Exception:
                fake_urls.append(url)
                continue

            # Check if URL exists in research sources
            if url in research_urls:
                verified_urls.append(url)
            else:
                # Check if domain matches (partial match)
                domain_matched = False
                for research_url in research_urls:
                    if urlparse(research_url).netloc == urlparse(url).netloc:
                        verified_urls.append(url)
                        domain_matched = True
                        break

                if not domain_matched:
                    unverified_urls.append(url)

        logger.info(
            "citation_verifier.url_verification",
            verified=len(verified_urls),
            unverified=len(unverified_urls),
            fake=len(fake_urls)
        )

        return {
            "verified_urls": verified_urls,
            "unverified_urls": unverified_urls,
            "fake_urls": fake_urls
        }

    async def _verify_claims_match_citations(
        self,
        content: str,
        extraction: Dict,
        research_sources: List[Dict]
    ) -> Dict:
        """
        Use separate model context to verify claims match their citations

        Based on Reddit: "Ask for exact snippet from source that supports claim"
        """
        # Sample first 5 citations for verification (to control cost)
        citations_to_verify = extraction["inline_citations"][:5]

        if not citations_to_verify:
            return {
                "verified_claims": [],
                "suspicious_claims": [],
                "cost": Decimal("0")
            }

        # Build verification prompt
        prompt = self._build_verification_prompt(content, citations_to_verify, extraction["references"])

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )

            # Calculate cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = (Decimal(input_tokens) / Decimal(1_000_000) * Decimal("3.00") +
                   Decimal(output_tokens) / Decimal(1_000_000) * Decimal("15.00"))

            # Parse response
            response_text = response.content[0].text

            # Extract verified and suspicious claims
            verified_claims = []
            suspicious_claims = []

            if "VERIFIED" in response_text.upper():
                verified_count = response_text.upper().count("VERIFIED")
                verified_claims = list(range(min(verified_count, len(citations_to_verify))))

            if "SUSPICIOUS" in response_text.upper() or "UNVERIFIED" in response_text.upper():
                # Extract suspicious citation numbers
                suspicious_matches = re.findall(r'\[(\d+)\].*?(?:suspicious|unverified)', response_text, re.IGNORECASE)
                suspicious_claims = [int(n) for n in suspicious_matches]

            logger.info(
                "citation_verifier.claim_verification",
                verified=len(verified_claims),
                suspicious=len(suspicious_claims)
            )

            return {
                "verified_claims": verified_claims,
                "suspicious_claims": suspicious_claims,
                "cost": cost
            }

        except Exception as e:
            logger.error("citation_verifier.claim_verification_failed", error=str(e))
            return {
                "verified_claims": [],
                "suspicious_claims": [],
                "cost": Decimal("0")
            }

    def _build_verification_prompt(
        self,
        content: str,
        citations_to_verify: List[str],
        references: List[Dict]
    ) -> str:
        """Build prompt for claim verification"""

        # Extract context around each citation
        citation_contexts = []
        for cit_num in citations_to_verify:
            pattern = rf'([^.!?]*\[{cit_num}\][^.!?]*[.!?])'
            matches = re.findall(pattern, content)
            if matches:
                citation_contexts.append({
                    "citation": f"[{cit_num}]",
                    "context": matches[0].strip()
                })

        # Build reference list
        ref_list = "\n".join([
            f"[{ref['number']}] {ref['text']} - {ref['url']}"
            for ref in references
            if ref['number'] in [int(c) for c in citations_to_verify]
        ])

        # Build context list
        context_list = "\n\n".join([
            f"Citation {ctx['citation']}:\n\"{ctx['context']}\""
            for ctx in citation_contexts
        ])

        return f"""You are a fact-checker. Verify if citations properly support their claims.

REFERENCES:
{ref_list}

CLAIMS TO VERIFY:
{context_list}

For each citation, determine:
1. Does the claim require a citation? (factual claims need citations, opinions don't)
2. Is the reference source likely to contain this information?
3. Is there any red flag (claim too specific, source seems irrelevant, suspicious URL)?

Respond with:
- "VERIFIED [N]" if citation seems appropriate
- "SUSPICIOUS [N]" if there are red flags

Focus on detecting obviously fake or mismatched citations. Be generous with VERIFIED if plausible."""
