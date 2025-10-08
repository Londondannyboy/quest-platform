"""
Quest Platform v2.2 - EditorAgent
Quality scoring and HITL (Human-in-the-Loop) decision gate
"""

import json
from decimal import Decimal
from typing import Dict, Literal

from anthropic import AsyncAnthropic
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

QualityDecision = Literal["publish", "review", "reject"]


class EditorAgent:
    """
    Editor Agent: Score article quality and determine workflow

    Workflow:
    - Score ≥ 85: Auto-publish → ImageAgent
    - Score 70-84: Human review → HITL queue
    - Score < 70: Reject → retry or discard

    Cost: ~$0.005 per evaluation
    """

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL

    async def score(self, article: Dict) -> Dict:
        """
        Score article quality on 0-100 scale

        Args:
            article: Article data from ContentAgent

        Returns:
            Dict with quality score, decision, and cost
        """
        logger.info("editor_agent.start", title=article.get("title", "Unknown"))

        # Build evaluation prompt
        prompt = self._build_prompt(article)

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

            logger.info(
                "editor_agent.complete",
                score=evaluation["overall_score"],
                decision=decision,
                cost=float(cost),
            )

            return {
                "quality_score": evaluation["overall_score"],
                "dimensions": evaluation.get("dimensions", {}),
                "feedback": evaluation.get("feedback", ""),
                "decision": decision,
                "cost": cost,
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                },
            }

        except Exception as e:
            logger.error("editor_agent.scoring_failed", error=str(e), exc_info=e)
            raise

    def _build_prompt(self, article: Dict) -> str:
        """
        Build evaluation prompt for Claude
        """
        title = article.get("title", "")
        content = article.get("content", "")
        keywords = article.get("keywords", [])

        # Truncate content for evaluation (reduce tokens)
        content_preview = content[:2000] + "..." if len(content) > 2000 else content

        return f"""You are a content quality analyst. Evaluate this article on a 0-100 scale.

ARTICLE TITLE:
{title}

ARTICLE CONTENT (preview):
{content_preview}

KEYWORDS:
{', '.join(keywords)}

EVALUATION CRITERIA:

1. Factual Accuracy (0-100):
   - Citations and data correctness
   - Claims supported by evidence
   - No misleading information

2. Writing Quality (0-100):
   - Grammar and spelling
   - Readability (clear, concise)
   - Logical flow and structure
   - Engaging style

3. SEO Optimization (0-100):
   - Keyword usage (natural, not stuffed)
   - Title and headers optimization
   - Meta description quality
   - Content structure (H1, H2, lists)

4. Engagement (0-100):
   - Compelling hook
   - Actionable insights
   - Clear takeaways
   - Audience relevance

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
        if score >= 85:
            return "publish"
        elif score >= 70:
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
