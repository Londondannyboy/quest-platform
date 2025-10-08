"""
Quest Platform v2.2 - ContentAgent
Generates high-quality article content using Claude Sonnet 4.5
"""

import json
from decimal import Decimal
from typing import Dict

from anthropic import AsyncAnthropic
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class ContentAgent:
    """
    Content Agent: Generate articles with Claude Sonnet 4.5

    Cost:
    - Input: $3/M tokens
    - Output: $15/M tokens
    - Average: ~$0.04 per article with batch API discount
    """

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL

        # Site-specific writing styles
        self.style_guides = {
            "relocation": {
                "tone": "Practical, expat-focused, conversational",
                "audience": "Digital nomads and international relocators",
                "focus": "Actionable advice, visa requirements, cost of living",
            },
            "placement": {
                "tone": "Data-driven, analytical, professional",
                "audience": "Job seekers and career professionals",
                "focus": "Market trends, salary data, skill requirements",
            },
            "rainmaker": {
                "tone": "Entrepreneurial, action-oriented, motivational",
                "audience": "Entrepreneurs and business builders",
                "focus": "Growth strategies, revenue tactics, case studies",
            },
        }

    async def run(self, research: Dict, target_site: str, topic: str) -> Dict:
        """
        Generate article content from research

        Args:
            research: Research data from ResearchAgent
            target_site: Target site (relocation/placement/rainmaker)
            topic: Article topic

        Returns:
            Dict with article data and cost
        """
        logger.info(
            "content_agent.start", topic=topic, target_site=target_site
        )

        # Get site-specific style guide
        style = self.style_guides.get(
            target_site, self.style_guides["relocation"]
        )

        # Build prompt
        prompt = self._build_prompt(research, style, topic)

        # Call Claude API
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse response
            content_json = response.content[0].text

            # Calculate cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = self._calculate_cost(input_tokens, output_tokens)

            # Parse JSON response
            try:
                article_data = json.loads(content_json)
            except json.JSONDecodeError:
                # If Claude didn't return valid JSON, extract content manually
                logger.warning("content_agent.json_parse_failed", attempting_extraction=True)
                article_data = self._extract_article_data(content_json)

            logger.info(
                "content_agent.complete",
                topic=topic,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=float(cost),
            )

            return {
                "article": article_data,
                "cost": cost,
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                },
            }

        except Exception as e:
            logger.error("content_agent.generation_failed", error=str(e), exc_info=e)
            raise

    def _build_prompt(self, research: Dict, style: Dict, topic: str) -> str:
        """
        Build Claude prompt with research and style guide
        """
        research_content = (
            research["content"] if isinstance(research, dict) else str(research)
        )

        return f"""You are a professional content writer for {style['audience']}.

RESEARCH DATA:
{research_content}

TASK: Write a comprehensive, SEO-optimized article about: {topic}

STYLE GUIDE:
- Tone: {style['tone']}
- Audience: {style['audience']}
- Focus: {style['focus']}

REQUIREMENTS:
1. Engaging introduction with a compelling hook
2. 5-7 main sections with clear H2 headers
3. Data-driven insights from the research (cite specific statistics)
4. Actionable takeaways and practical advice
5. Natural SEO optimization (keywords flow naturally)
6. 1500-2000 words total
7. Markdown formatting

OUTPUT FORMAT (JSON):
{{
  "title": "Compelling article title (60-70 chars, SEO-optimized)",
  "excerpt": "Engaging 150-character summary for meta description",
  "content": "Full article content in Markdown with headers, lists, etc.",
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "reading_time_minutes": 7,
  "meta_title": "SEO-optimized title for <title> tag (max 60 chars)",
  "meta_description": "SEO-optimized description for meta tag (max 160 chars)"
}}

IMPORTANT: Return ONLY the JSON object, no additional text before or after."""

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> Decimal:
        """
        Calculate Claude API cost

        Pricing (with 50% batch API discount):
        - Input: $3/M tokens → $1.50/M with batch
        - Output: $15/M tokens → $7.50/M with batch
        """
        if settings.ENABLE_BATCH_API:
            # 50% discount for batch API
            input_cost = Decimal(input_tokens) / Decimal(1_000_000) * Decimal("1.50")
            output_cost = Decimal(output_tokens) / Decimal(1_000_000) * Decimal("7.50")
        else:
            input_cost = Decimal(input_tokens) / Decimal(1_000_000) * Decimal("3.00")
            output_cost = Decimal(output_tokens) / Decimal(1_000_000) * Decimal("15.00")

        return input_cost + output_cost

    def _extract_article_data(self, content: str) -> Dict:
        """
        Fallback: Extract article data if JSON parsing fails

        Args:
            content: Raw content from Claude

        Returns:
            Dict with extracted article data
        """
        # Simple extraction logic
        lines = content.split("\n")
        title = lines[0].replace("#", "").strip() if lines else "Untitled Article"

        return {
            "title": title,
            "excerpt": content[:150],
            "content": content,
            "keywords": [],
            "reading_time_minutes": len(content.split()) // 200,  # ~200 words/min
            "meta_title": title[:60],
            "meta_description": content[:160],
        }
