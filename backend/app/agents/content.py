"""
Quest Platform v2.2 - ContentAgent
Generates high-quality article content using Claude Sonnet 4.5
"""

import json
from decimal import Decimal
from typing import Dict, Optional

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
        self.model = settings.CONTENT_MODEL  # Configurable: Sonnet or Haiku

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
        content_type: str = "standard",
        link_context: Optional[Dict] = None
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
            prompt = self._build_listicle_prompt(research, style, topic, link_context)
        elif content_type == "alternative":
            prompt = self._build_alternative_prompt(research, style, topic, link_context)
        elif content_type == "comparison":
            prompt = self._build_comparison_prompt(research, style, topic, link_context)
        else:
            prompt = self._build_prompt(research, style, topic, link_context)

        # Call Claude API
        try:
            # System prompt for role specialization
            system_prompt = f"""You are an expert content writer specializing in {style['focus']} for {style['audience']}.

You write comprehensive, well-researched articles that provide real value to readers. Every claim you make is backed by citations using [1], [2] format, with a complete References section at the end."""

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=8000,  # Increased to 8000 for 2000+ word articles in pure markdown format
                temperature=0.7,
                system=system_prompt,  # Add system prompt for better context
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse response
            content_json = response.content[0].text

            # Calculate cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = self._calculate_cost(input_tokens, output_tokens)

            # Parse JSON response (strip markdown code fences if present)
            cleaned_json = content_json.strip()

            # Remove markdown code fences if present
            if cleaned_json.startswith('```'):
                lines = cleaned_json.split('\n')
                if lines[0].startswith('```'):
                    lines = lines[1:]  # Remove first line (```json or ```)
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]  # Remove last line (```)
                cleaned_json = '\n'.join(lines).strip()

            # Try parsing as JSON, but always use content if JSON fails
            try:
                article_data = json.loads(cleaned_json)
                logger.info("content_agent.json_parsed_successfully", has_title=bool(article_data.get("title")))
            except json.JSONDecodeError as e:
                logger.warning("content_agent.using_raw_content", error=str(e))
                # Extract title from first H1 or use topic
                lines = cleaned_json.split('\n')
                title = topic  # Default to topic
                for line in lines[:5]:
                    if line.startswith('# '):
                        title = line.replace('# ', '').strip()
                        break

                # Use raw markdown as content (JSON parsing not critical)
                article_data = {
                    "title": title,
                    "tldr": "",
                    "key_takeaways": [],
                    "excerpt": lines[1][:200] if len(lines) > 1 else topic,
                    "content": cleaned_json,  # Raw markdown works fine
                    "faqs": [],
                    "sources_cited": [],
                    "author_bio": "",
                    "keywords": [topic.split()[0], topic.split()[1]] if len(topic.split()) > 1 else [topic],
                    "reading_time_minutes": len(cleaned_json.split()) // 200,
                    "meta_title": title[:60],
                    "meta_description": lines[1][:160] if len(lines) > 1 else topic
                }

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

    def _build_prompt(self, research: Dict, style: Dict, topic: str, link_context: Optional[Dict] = None) -> str:
        """
        Build Claude prompt with research and style guide
        """
        research_content = (
            research["content"] if isinstance(research, dict) else str(research)
        )

        # Build link instructions if context provided
        link_instructions = ""
        if link_context:
            # Format external links
            external_links = "\n".join([
                f"   - {link['url']}"
                for link in link_context.get('external_links', [])[:12]
            ])

            # Format internal links
            internal_links = "\n".join([
                f"   - [{link['title']}]({link['link']})"
                for link in link_context.get('internal_links', [])[:5]
            ])

            link_instructions = f"""

VALIDATED LINKS TO USE:
External Links (use 8-12 of these from research sources):
{external_links}

Internal Links (use 3-5 of these for related content):
{internal_links}

**IMPORTANT**: Only use the links provided above. Do NOT make up or hallucinate any links."""

        # SEO instructions if provided
        seo_instructions = ""
        if link_context and link_context.get('seo_data'):
            seo_data = link_context['seo_data']
            seo_instructions = f"""

**SEO OPTIMIZATION REQUIREMENTS:**
- Primary Keyword: "{seo_data.get('primary_keyword', topic)}"
- Target keyword density: 1-2% (use naturally, not forced)
- Include keyword in: Title, first paragraph, H2 headers, conclusion
- Search Volume: {seo_data.get('search_volume', 'N/A')}/month
- Competition: {seo_data.get('competition', 'N/A')}
- Secondary Keywords: {', '.join(seo_data.get('secondary_keywords', [])[:3])}
"""

        return f"""You are an expert content writer specializing in {style['focus']} for {style['audience']}.

You write comprehensive, well-researched articles that provide real value to readers. Every claim is backed by citations using [1], [2] format.

RESEARCH DATA (Multi-Source Intelligence):
{research_content}
{link_instructions}
{seo_instructions}

**CRITICAL INSTRUCTIONS FOR USING RESEARCH:**
The research data above comes from multiple sources:
- **Serper.dev**: Top-ranking Google competitor analysis - these are the articles currently winning on page 1
- **Firecrawl**: Actual scraped content from competitors - see what they wrote and write BETTER
- **Perplexity**: Deep factual research and gap analysis - use this to find what competitors are missing
- **Tavily**: Comprehensive search results - additional context and sources
- **DataForSEO**: SEO metrics showing search volume and competition level

YOUR JOB: Analyze the competitor content and write an article that BEATS them by:
1. **Covering all their key points** (so you rank alongside them)
2. **Adding insights they missed** (from Perplexity gap analysis)
3. **Better structure and readability** (TL;DR, key takeaways, FAQs)
4. **More authoritative sources** (use links from research)
5. **Deeper, more actionable advice** (specific numbers, steps, examples)

TASK: Write a comprehensive, SEO-optimized article about: {topic}

STYLE GUIDE:
- Tone: {style['tone']}
- Audience: {style['audience']}
- Focus: {style['focus']}

ARTICLE STRUCTURE (Follow this exact outline):
1. **Compelling Introduction** - Hook the reader, establish authority, preview what they'll learn
2. **Overview** - What is this topic? Why does it matter? Who needs this information?
3. **Key Benefits and Advantages** - Clear value propositions
4. **Step-by-Step Process or Methodology** - Actionable how-to guide
5. **Common Challenges and Solutions** - Address pain points
6. **Cost Considerations and Budgeting** - Practical financial guidance
7. **Legal and Regulatory Aspects** (if applicable) - Compliance and requirements
8. **Expert Tips and Best Practices** - Insider knowledge
9. **Case Studies or Success Stories** - Real-world examples
10. **Future Trends and Outlook** - What's changing in this space
11. **Conclusion with Clear Call-to-Action** - Summarize and guide next steps

REQUIREMENTS (AI-Optimized for ChatGPT/Perplexity):
1. TL;DR summary (150 words) at the top - direct, confident language
2. Key Takeaways section (3-5 bullet points) - actionable insights
3. Clear H1/H2/H3 hierarchy - LLMs read headings first
4. FAQ section (4-10 Q&A pairs) - LLMs love Q&A format
5. **CRITICAL: Include 8-12 external links throughout content** - Link to authoritative sources (government sites, official docs, reputable news)
6. **CRITICAL: Include 3-5 internal links** - Link to related topics using markdown: [Digital Nomad Visas](/digital-nomad-visas), [Cost of Living](/cost-of-living-portugal), [Best Cities](/best-cities-digital-nomads)
7. **CRITICAL: Use inline citations [1], [2], [3] for all factual claims** - Minimum 5 citations required
8. **CRITICAL: Add References section at the end** - List all sources in [1], [2], [3] format with URLs
9. Expert quotes or credentials - builds trust
10. Data-driven insights from research (specific statistics with citations)
11. Conversational, direct tone - avoid hedging language
12. **Minimum 2000 words** (aim for 2500 words for comprehensive coverage)
13. Markdown formatting with proper link syntax: [Link Text](https://example.com)
14. **Include image placeholders strategically throughout content**:
   - Add `![Hero Image Alt](IMAGE_PLACEHOLDER_HERO)` after the TL;DR section
   - Add `![Content Image 1 Alt](IMAGE_PLACEHOLDER_1)` after the first major section
   - Add `![Content Image 2 Alt](IMAGE_PLACEHOLDER_2)` in the middle of the article
   - Add `![Content Image 3 Alt](IMAGE_PLACEHOLDER_3)` before the FAQ section
   - Use descriptive alt text that explains what the image should show

OUTPUT FORMAT: Pure markdown article

Write the complete article in markdown format with:
- H1 title at the top (# Title)
- TL;DR section immediately after title
- Key Takeaways section
- Full article content with H2/H3 headers
- FAQ section near the end
- References section at the very end (## References with numbered citations)

IMPORTANT: Output ONLY the markdown article. No JSON, no code fences, just pure markdown content starting with # and the title.

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> Decimal:
        """
        Calculate Claude API cost

        Pricing (with 50% batch API discount):
        - Input: $3/M tokens -> $1.50/M with batch
        - Output: $15/M tokens -> $7.50/M with batch
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
        # Try to extract JSON from content (handle markdown code fences)
        cleaned = content.strip()

        # Remove markdown code fences if present
        if cleaned.startswith('```'):
            lines = cleaned.split('\n')
            # Remove first line (```json or ```)
            if lines[0].startswith('```'):
                lines = lines[1:]
            # Remove last line if it's ```)
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            cleaned = '\n'.join(lines)

        # Try parsing as JSON one more time
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # If still can't parse, return raw content
        lines = cleaned.split("\n")
        title = lines[0].replace("#", "").strip() if lines else "Untitled Article"

        return {
            "title": title,
            "tldr": "",
            "key_takeaways": [],
            "excerpt": cleaned[:150],
            "content": cleaned,
            "faqs": [],
            "sources_cited": [],
            "author_bio": "",
            "keywords": [],
            "reading_time_minutes": len(cleaned.split()) // 200,  # ~200 words/min
            "meta_title": title[:60],
            "meta_description": cleaned[:160],
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
