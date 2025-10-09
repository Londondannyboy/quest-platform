"""
Quest Platform v2.2 - EditorAgent
Quality scoring and HITL (Human-in-the-Loop) decision gate
"""

import json
import re
from decimal import Decimal
from typing import Dict, Literal

from anthropic import AsyncAnthropic
import structlog

from app.core.config import settings
from app.core.research_apis import CritiqueLabsProvider

logger = structlog.get_logger(__name__)

QualityDecision = Literal["publish", "review", "reject"]


class EditorAgent:
    """
    Editor Agent: Score article quality and determine workflow

    Workflow:
    - Score ≥ 75: Auto-publish → ImageAgent
    - Score 60-74: Human review → HITL queue
    - Score < 60: Reject → retry or discard

    Cost: ~$0.005 per evaluation
    """

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
        self.critique_labs = CritiqueLabsProvider()

    async def score(self, article: Dict) -> Dict:
        """
        Score article quality on 0-100 scale

        Args:
            article: Article data from ContentAgent

        Returns:
            Dict with quality score, decision, and cost
        """
        logger.info("editor_agent.start", title=article.get("title", "Unknown"))

        # Validate citations before scoring
        citation_validation = self._validate_citations(article.get("content", ""))

        # Build evaluation prompt
        prompt = self._build_prompt(article, citation_validation)

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.2,  # Lower temp for consistent scoring
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse response
            evaluation_json = response.content[0].text

            # Calculate cost (minimal)
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = self._calculate_cost(input_tokens, output_tokens)

            # Parse evaluation (strip markdown code fences if present)
            try:
                # Strip markdown code fences (```json ... ```)
                cleaned_json = evaluation_json.strip()
                if cleaned_json.startswith('```'):
                    # Remove ```json at start and ``` at end
                    lines = cleaned_json.split('\n')
                    if lines[0].startswith('```'):
                        lines = lines[1:]  # Remove first line
                    if lines and lines[-1].strip() == '```':
                        lines = lines[:-1]  # Remove last line
                    cleaned_json = '\n'.join(lines)

                evaluation = json.loads(cleaned_json)
            except json.JSONDecodeError:
                logger.warning("editor_agent.json_parse_failed")
                evaluation = self._fallback_evaluation()

            # Add decision logic
            decision = self._make_decision(evaluation["overall_score"])

            # Fact-check if score is high enough (≥70) and Critique Labs available
            critique_result = None
            if evaluation["overall_score"] >= 70 and self.critique_labs.is_available():
                logger.info("editor_agent.running_fact_check", score=evaluation["overall_score"])
                critique_result = await self._fact_check_article(article)

                if critique_result:
                    # Add fact-check cost
                    cost += critique_result.get("cost", Decimal("0"))

                    # Adjust score based on fact-check accuracy
                    accuracy_score = critique_result.get("accuracy_score", 100)
                    if accuracy_score < 80:
                        logger.warning(
                            "editor_agent.low_fact_check_score",
                            accuracy=accuracy_score,
                            issues=len(critique_result.get("issues", []))
                        )
                        # Downgrade decision if fact-check fails
                        if decision == "publish":
                            decision = "review"

            logger.info(
                "editor_agent.complete",
                score=evaluation["overall_score"],
                decision=decision,
                cost=float(cost),
                fact_checked=critique_result is not None
            )

            result = {
                "quality_score": evaluation["overall_score"],
                "dimensions": evaluation.get("dimensions", {}),
                "feedback": evaluation.get("feedback", ""),
                "decision": decision,
                "citation_validation": citation_validation,  # Add citation validation results
                "cost": cost,
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                },
            }

            # Add fact-check results if available
            if critique_result:
                result["fact_check"] = {
                    "accuracy_score": critique_result.get("accuracy_score"),
                    "issues_count": len(critique_result.get("issues", [])),
                    "verified_facts": len(critique_result.get("verified_facts", [])),
                }

            return result

        except Exception as e:
            logger.error("editor_agent.scoring_failed", error=str(e), exc_info=e)
            raise

    def _validate_citations(self, content: str) -> Dict:
        """
        Validate citation format and count

        Args:
            content: Article content

        Returns:
            {
                "citation_count": int,
                "has_references_section": bool,
                "format_valid": bool,
                "passed": bool
            }
        """
        # Count inline citations [1], [2], etc.
        citations = re.findall(r'\[\d+\]', content)
        citation_count = len(set(citations))  # Unique citations

        # Check for References section
        has_references = bool(re.search(r'##\s*References?\s*\n', content, re.IGNORECASE))

        # Format validation: citations should be numeric and sequential
        format_valid = all(c.strip('[]').isdigit() for c in citations)

        # Word count check
        word_count = len(content.split())

        # Validation passed if:
        # - At least 5 unique citations
        # - References section exists
        # - Format is valid
        # - At least 2000 words
        passed = (
            citation_count >= 5 and
            has_references and
            format_valid and
            word_count >= 2000
        )

        logger.info(
            "editor_agent.citation_validation",
            citations=citation_count,
            references_section=has_references,
            word_count=word_count,
            passed=passed
        )

        return {
            "citation_count": citation_count,
            "has_references_section": has_references,
            "format_valid": format_valid,
            "word_count": word_count,
            "passed": passed
        }

    def _build_prompt(self, article: Dict, citation_validation: Dict = None) -> str:
        """
        Build evaluation prompt for Claude
        """
        title = article.get("title", "")
        content = article.get("content", "")
        keywords = article.get("keywords", [])

        # Truncate content for evaluation (reduce tokens)
        content_preview = content[:2000] + "..." if len(content) > 2000 else content

        # Add citation validation context
        citation_context = ""
        if citation_validation:
            citation_context = f"""

CITATION VALIDATION:
- Inline Citations Found: {citation_validation['citation_count']} (minimum required: 5)
- References Section: {'✅ Present' if citation_validation['has_references_section'] else '❌ Missing'}
- Format Valid: {'✅ Yes' if citation_validation['format_valid'] else '❌ No'}
- Word Count: {citation_validation['word_count']} (minimum required: 2000)
- Overall: {'✅ PASSED' if citation_validation['passed'] else '❌ FAILED'}

**IMPORTANT**: Articles MUST have at least 5 citations and a References section. Penalize score if missing."""

        return f"""You are a content quality analyst. Evaluate this article on a 0-100 scale.

ARTICLE TITLE:
{title}

ARTICLE CONTENT (preview):
{content_preview}

KEYWORDS:
{', '.join(keywords)}
{citation_context}

EVALUATION CRITERIA:

1. Factual Accuracy (0-100):
   - **CRITICAL: At least 5 inline citations [1], [2], [3] required**
   - **CRITICAL: References section at the end required**
   - Claims supported by evidence
   - No misleading information
   - Data sources cited properly

2. Writing Quality (0-100):
   - **CRITICAL: Minimum 2000 words required**
   - Grammar and spelling
   - Readability (clear, concise)
   - Logical flow and structure
   - Engaging style
   - Professional tone

3. SEO Optimization (0-100):
   - Keyword usage (natural, not stuffed)
   - Title and headers optimization
   - Meta description quality
   - Content structure (H1, H2, lists)
   - Internal and external links

4. Engagement (0-100):
   - Compelling hook
   - Actionable insights
   - Clear takeaways
   - Audience relevance
   - FAQ section included

OUTPUT FORMAT (JSON):
{{
  "overall_score": 85,
  "dimensions": {{
    "accuracy": 90,
    "writing": 85,
    "seo": 80,
    "engagement": 85
  }},
  "feedback": "Brief 1-2 sentence explanation of score",
  "strengths": ["strength1", "strength2"],
  "improvements": ["improvement1", "improvement2"]
}}

IMPORTANT: Return ONLY the JSON object, no additional text."""

    def _make_decision(self, score: int) -> QualityDecision:
        """
        Determine workflow based on quality score

        Args:
            score: Quality score (0-100)

        Returns:
            Decision: publish, review, or reject
        """
        if score >= 75:
            return "publish"
        elif score >= 60:
            return "review"
        else:
            return "reject"

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> Decimal:
        """
        Calculate evaluation cost (small)
        """
        input_cost = Decimal(input_tokens) / Decimal(1_000_000) * Decimal("3.00")
        output_cost = Decimal(output_tokens) / Decimal(1_000_000) * Decimal("15.00")
        return input_cost + output_cost

    async def _fact_check_article(self, article: Dict) -> Dict:
        """
        Fact-check article content using Critique Labs

        Args:
            article: Article data

        Returns:
            Fact-check results
        """
        content = article.get("content", "")
        # Limit content for fact-checking (cost control)
        content_sample = content[:3000] if len(content) > 3000 else content

        try:
            result = await self.critique_labs.fact_check(content_sample)
            logger.info(
                "editor_agent.fact_check_complete",
                accuracy=result.get("accuracy_score"),
                issues=len(result.get("issues", []))
            )
            return result
        except Exception as e:
            logger.warning(
                "editor_agent.fact_check_failed",
                error=str(e)
            )
            return None

    def _fallback_evaluation(self) -> Dict:
        """
        Fallback evaluation if JSON parsing fails

        Returns:
            Conservative mid-range score (triggers human review)
        """
        return {
            "overall_score": 75,  # Trigger human review
            "dimensions": {
                "accuracy": 75,
                "writing": 75,
                "seo": 75,
                "engagement": 75,
            },
            "feedback": "Unable to parse evaluation, defaulting to human review",
            "strengths": [],
            "improvements": ["Manual review required"],
        }
