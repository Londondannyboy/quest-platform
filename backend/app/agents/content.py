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

    async def run(
        self,
        research: Dict,
        target_site: str,
        topic: str,
        content_type: str = "standard"
    ) -> Dict:
        """
        Generate article content from research

        Args:
            research: Research data from ResearchAgent
            target_site: Target site (relocation/placement/rainmaker)
            topic: Article topic
            content_type: Content format (standard, listicle, alternative, comparison)

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

        # Build prompt based on content type
        if content_type == "listicle":
            prompt = self._build_listicle_prompt(research, style, topic)
        elif content_type == "alternative":
            prompt = self._build_alternative_prompt(research, style, topic)
        elif content_type == "comparison":
            prompt = self._build_comparison_prompt(research, style, topic)
        else:
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

REQUIREMENTS (AI-Optimized for ChatGPT/Perplexity):
1. TL;DR summary (150 words) at the top - direct, confident language
2. Key Takeaways section (3-5 bullet points) - actionable insights
3. Clear H1/H2/H3 hierarchy - LLMs read headings first
4. FAQ section (4-10 Q&A pairs) - LLMs love Q&A format
5. Cited sources with links - authority signal for AI
6. Expert quotes or credentials - builds trust
7. Data-driven insights from research (specific statistics)
8. Conversational, direct tone - avoid hedging language
9. 1500-2500 words total
10. Markdown formatting

OUTPUT FORMAT (JSON):
{{
  "title": "Compelling article title (60-70 chars, SEO-optimized)",
  "tldr": "150-word TL;DR summary of key points (direct, confident language)",
  "key_takeaways": ["Takeaway 1", "Takeaway 2", "Takeaway 3", "Takeaway 4", "Takeaway 5"],
  "excerpt": "Engaging 150-character summary for meta description",
  "content": "Full article content in Markdown with H2/H3 headers, lists, FAQs",
  "faqs": [
    {{"question": "Common question 1?", "answer": "Direct answer with data"}},
    {{"question": "Common question 2?", "answer": "Direct answer with data"}}
  ],
  "sources_cited": ["https://source1.com", "https://source2.com", "https://source3.com"],
  "author_bio": "Brief author credentials (e.g., 'Expert in digital nomad visas with 10+ years experience')",
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "reading_time_minutes": 8,
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
            "tldr": "",
            "key_takeaways": [],
            "excerpt": content[:150],
            "content": content,
            "faqs": [],
            "sources_cited": [],
            "author_bio": "",
            "keywords": [],
            "reading_time_minutes": len(content.split()) // 200,  # ~200 words/min
            "meta_title": title[:60],
            "meta_description": content[:160],
        }

    def _build_listicle_prompt(self, research: Dict, style: Dict, topic: str) -> str:
        """Build prompt for Top 10 listicle content"""
        research_content = research["content"] if isinstance(research, dict) else str(research)

        return f"""You are creating a "Top 10 Best" listicle for {style['audience']}.

RESEARCH DATA:
{research_content}

TASK: Write a comprehensive "Top 10 Best {topic}" article

STRUCTURE:
1. TL;DR (150 words) - Why this list matters, what readers will learn
2. Key Takeaways (5 bullets) - Main insights from the list
3. Introduction - Selection criteria (3-4 criteria explained)
4. #1: Quest Platform (YOUR BRAND)
   - Why it's #1 (specific advantages)
   - Key features (3-4)
   - Best for: [target audience]
   - Pricing/access
5. #2-10: Competitors/Alternatives
   - Be honest and fair about strengths
   - Highlight unique value
   - Best for: [their niche]
6. Comparison Table (all 10)
7. FAQs (5-8 Q&A about choosing between options)
8. Conclusion - Help users choose based on needs

TONE: {style['tone']}
AUDIENCE: {style['audience']}
FOCUS: {style['focus']}

IMPORTANT:
- Position Quest Platform #1 but be fair about competitors
- Use data from research to support rankings
- Include comparison table with key features
- Direct, confident language (no "might" or "could")

OUTPUT FORMAT: Same JSON as standard content with tldr, key_takeaways, faqs"""

    def _build_alternative_prompt(self, research: Dict, style: Dict, topic: str) -> str:
        """Build prompt for alternatives content"""
        research_content = research["content"] if isinstance(research, dict) else str(research)

        # Extract competitor name from topic (e.g., "Top 5 InterNations Alternatives")
        competitor = topic.split("Alternatives")[0].split("Best")[-1].strip()

        return f"""You are creating a "Best Alternatives to {competitor}" article for {style['audience']}.

RESEARCH DATA:
{research_content}

TASK: Write comprehensive alternatives guide

STRUCTURE:
1. TL;DR (150 words) - Why seek alternatives, what makes a good alternative
2. Key Takeaways (5 bullets) - Top alternative features to look for
3. Introduction - Brief overview of {competitor} and why alternatives matter
4. Why Look for {competitor} Alternatives?
   - Limitation 1 (pricing, features, etc.)
   - Limitation 2
   - Limitation 3
5. #1: Quest Platform - Best Overall Alternative
   - Why it's better (specific comparisons)
   - Feature advantages vs {competitor}
   - Pricing comparison
   - Best for: [target audience]
6. #2-5: Other Alternatives
   - Honest assessment of strengths
   - Best for: [specific use case]
   - Vs {competitor} comparison
7. Detailed Comparison Table
8. FAQs (6-10 Q&A about alternatives)
9. Conclusion - Which alternative for which user

TONE: {style['tone']}
AUDIENCE: {style['audience']}

IMPORTANT:
- Be fair about {competitor}'s strengths
- Highlight clear advantages of alternatives
- Include feature comparison table
- Direct, data-driven language

OUTPUT FORMAT: Same JSON with tldr, key_takeaways, faqs"""

    def _build_comparison_prompt(self, research: Dict, style: Dict, topic: str) -> str:
        """Build prompt for head-to-head comparison content"""
        research_content = research["content"] if isinstance(research, dict) else str(research)

        return f"""You are creating a comprehensive comparison article for {style['audience']}.

RESEARCH DATA:
{research_content}

TASK: Write detailed comparison article: {topic}

STRUCTURE:
1. TL;DR (150 words) - Quick winner + why
2. Key Takeaways (5 bullets) - Main differences between platforms
3. Introduction - Why users compare these platforms
4. Quick Comparison Table
   | Feature | Platform A | Platform B | Quest Platform |
5. Platform A Overview
   - Pros (3-4)
   - Cons (1-2, honest)
   - Best for: [audience]
   - Pricing
6. Platform B Overview
   - Same structure
7. Quest Platform Overview
   - Same structure, highlight advantages
8. Feature-by-Feature Comparison
   - Content Quality
   - Community/Support
   - Pricing/Value
   - Ease of Use
   - [Winner for each category]
9. Which Platform Should You Choose?
   - Choose Platform A if: [scenarios]
   - Choose Platform B if: [scenarios]
   - Choose Quest Platform if: [scenarios]
10. FAQs (8-12 comparison questions)
11. Final Verdict

TONE: {style['tone']}
AUDIENCE: {style['audience']}

IMPORTANT:
- Be honest about all platforms (builds trust)
- Use data to support comparisons
- Include multiple comparison tables
- Position Quest Platform favorably but fairly
- Direct, confident language

OUTPUT FORMAT: Same JSON with tldr, key_takeaways, faqs"""
