"""
Quest Platform v2.3 - GeminiSummarizer Agent
Compress massive research data into high-signal summaries using Gemini's 2M token context
"""

import json
from decimal import Decimal
from typing import Dict, Optional

import google.generativeai as genai
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class GeminiSummarizer:
    """
    Gemini Summarizer Agent: Compress research data using Gemini's massive context window

    Why Gemini?
    - 2M token context window (vs Claude's 200K)
    - Ultra-cheap: $0.075/M tokens input (83% cheaper than Claude Haiku)
    - Can process all 6 research APIs simultaneously

    Cost:
    - Input: $0.075/M tokens
    - Output: $0.30/M tokens
    - Average: ~$0.004 per article (research compression)
    """

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            logger.warning("gemini_summarizer.no_api_key", message="Gemini API key not configured, summarizer disabled")
            self.enabled = False
            return

        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.enabled = True
        logger.info("gemini_summarizer.initialized", model=settings.GEMINI_MODEL)

    async def compress_research(
        self,
        research_data: Dict,
        topic: str,
        target_site: str = "relocation"
    ) -> Dict:
        """
        Compress massive research data into high-signal summary

        Args:
            research_data: Dictionary with research from all APIs OR JSON string from cache
                {
                    "perplexity": {...},
                    "tavily": {...},
                    "dataforseo": {...},
                    "serper": {...},
                    "firecrawl": {...},
                    "linkup": {...}
                }
            topic: Article topic
            target_site: Target site (relocation/placement/rainmaker)

        Returns:
            Dict with compressed research and cost
        """
        if not self.enabled:
            logger.info("gemini_summarizer.disabled", message="Returning original research")
            return {
                "compressed_research": research_data,
                "compression_ratio": 1.0,
                "cost": Decimal("0.00"),
                "tokens": {"input": 0, "output": 0}
            }

        # Handle both dict and JSON string from cache
        if isinstance(research_data, str):
            try:
                research_data = json.loads(research_data)
                logger.info("gemini_summarizer.parsed_json_string", message="Parsed JSON string from cache")
            except json.JSONDecodeError:
                # If it's already a markdown string, just return it
                logger.info("gemini_summarizer.already_compressed", message="Research data is already a string")
                return {
                    "compressed_research": research_data,
                    "compression_ratio": 1.0,
                    "cost": Decimal("0.00"),
                    "tokens": {"input": 0, "output": 0}
                }

        logger.info(
            "gemini_summarizer.start",
            topic=topic,
            target_site=target_site,
            api_count=len(research_data) if isinstance(research_data, dict) else 1
        )

        # Build compression prompt
        prompt = self._build_compression_prompt(research_data, topic, target_site)

        try:
            # Call Gemini API
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Low temp for factual compression
                    max_output_tokens=8192,  # Compressed output
                )
            )

            # Extract compressed research
            compressed_text = response.text

            # Calculate cost
            input_tokens = response.usage_metadata.prompt_token_count
            output_tokens = response.usage_metadata.candidates_token_count
            cost = self._calculate_cost(input_tokens, output_tokens)

            # Calculate compression ratio
            original_length = len(json.dumps(research_data))
            compressed_length = len(compressed_text)
            compression_ratio = compressed_length / original_length if original_length > 0 else 1.0

            logger.info(
                "gemini_summarizer.complete",
                topic=topic,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=float(cost),
                compression_ratio=f"{compression_ratio:.2%}"
            )

            return {
                "compressed_research": compressed_text,
                "compression_ratio": compression_ratio,
                "cost": cost,
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens
                }
            }

        except Exception as e:
            logger.error("gemini_summarizer.failed", error=str(e), exc_info=e)
            # Graceful fallback: Return original research
            return {
                "compressed_research": research_data,
                "compression_ratio": 1.0,
                "cost": Decimal("0.00"),
                "tokens": {"input": 0, "output": 0},
                "error": str(e)
            }

    def _build_compression_prompt(
        self,
        research_data: Dict,
        topic: str,
        target_site: str
    ) -> str:
        """Build Gemini compression prompt"""

        # Format research data as structured text
        research_sections = []
        for api_name, api_data in research_data.items():
            if api_data:
                research_sections.append(f"## {api_name.upper()} Research:\n{json.dumps(api_data, indent=2)}\n")

        research_text = "\n".join(research_sections)

        return f"""You are a research analyst specializing in {target_site} content. Your task is to compress and synthesize research data into a high-signal summary for content generation.

TOPIC: {topic}

RESEARCH DATA FROM 6 APIs:
{research_text}

TASK: Create a structured, comprehensive summary that:

1. **KEY FACTS & STATISTICS**: Extract all important numbers, dates, requirements, costs, deadlines
   - Be specific (not "many" but "15+", not "expensive" but "$3000-5000")
   - Include sources for each fact

2. **COMPETITIVE INSIGHTS**: What are top-ranking articles doing?
   - Common topics/sections they cover
   - Depth and structure patterns
   - Unique angles they take
   - Gaps or weaknesses we can exploit

3. **KEYWORD INTELLIGENCE**: From DataForSEO and Serper
   - Primary keywords with search volume
   - Secondary keywords to target
   - Related questions people ask
   - Trending topics in this space

4. **AUTHORITATIVE SOURCES**: Links to cite
   - Government/official sources (.gov, .edu, embassy sites)
   - Industry experts and quotes
   - Recent news articles
   - Reliable statistics sources

5. **UNIQUE ANGLES**: What competitors missed
   - Underserved subtopics
   - Recent changes or updates
   - User pain points not addressed
   - Opportunities for differentiation

6. **CONTENT STRUCTURE RECOMMENDATIONS**: Based on SERP analysis
   - Recommended word count (based on competitors)
   - Key sections to include
   - Content modules (FAQ, tables, comparisons)
   - Visual elements needed

OUTPUT FORMAT: Structured markdown summary (2000-3000 words max)

IMPORTANT:
- Be specific and data-driven (numbers, not adjectives)
- Prioritize high-signal information (not fluff)
- Organize clearly for easy reference during content generation
- Include source URLs for all factual claims
- Focus on actionable insights"""

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> Decimal:
        """
        Calculate Gemini API cost

        Pricing:
        - Input: $0.075/M tokens
        - Output: $0.30/M tokens
        """
        input_cost = Decimal(input_tokens) / Decimal(1_000_000) * Decimal("0.075")
        output_cost = Decimal(output_tokens) / Decimal(1_000_000) * Decimal("0.30")

        return input_cost + output_cost
