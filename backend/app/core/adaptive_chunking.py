"""
Adaptive Chunking Strategy

Determines optimal chunk count (2-5) based on topic complexity analysis.
Uses Gemini 2.5 Flash for fast, cheap complexity scoring.

Cost Impact:
- Complexity analysis: $0.001/topic (negligible)
- Simple topics (2 chunks): Save $0.05/article
- Medium topics (3 chunks): Current cost (baseline)
- Complex topics (4-5 chunks): Add $0.10-0.20/article

Benefits:
- Prevents over-engineering simple topics
- Ensures depth for complex topics
- Dynamic cost optimization
- Better quality-cost tradeoff
"""

from typing import Dict, Optional
from decimal import Decimal
import json
import structlog

import google.generativeai as genai

logger = structlog.get_logger()


class AdaptiveChunkingStrategy:
    """
    Analyze topic complexity and recommend optimal chunking strategy

    Complexity Scoring (1-10):
    - 1-3: Simple (e.g., "What is a digital nomad?") → 2 chunks
    - 4-7: Medium (e.g., "Portugal D7 Visa Requirements") → 3 chunks
    - 8-10: Complex (e.g., "Tax Optimization for Multi-Jurisdiction Nomads") → 4-5 chunks
    """

    # Complexity thresholds
    THRESHOLDS = {
        "simple": {"max_score": 3, "chunks": 2, "target_words": 2500},
        "medium": {"max_score": 7, "chunks": 3, "target_words": 3500},
        "complex": {"max_score": 10, "chunks": 4, "target_words": 5000},
        "expert": {"max_score": 10, "chunks": 5, "target_words": 6000}
    }

    def __init__(self, gemini_api_key: str):
        """
        Initialize adaptive chunking analyzer

        Args:
            gemini_api_key: Gemini API key for complexity analysis
        """
        genai.configure(api_key=gemini_api_key)
        # Use Flash for ultra-fast, ultra-cheap analysis ($0.001/analysis)
        self.flash_model = genai.GenerativeModel("gemini-2.5-flash")

    async def analyze_complexity(self, topic: str, research: Optional[Dict] = None) -> Dict:
        """
        Analyze topic complexity and recommend chunking strategy

        Args:
            topic: Article topic
            research: Optional research data for context

        Returns:
            Dict with complexity score and chunking recommendations
        """
        logger.info("adaptive_chunking.analyzing", topic=topic)

        # Build analysis prompt
        prompt = self._build_analysis_prompt(topic, research)

        try:
            # Generate complexity analysis
            response = self.flash_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Low temp for consistent scoring
                    max_output_tokens=500,
                )
            )

            # Parse JSON response
            response_text = response.text.strip()

            # Extract JSON from markdown code fence if present
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            analysis = json.loads(response_text)

            # Calculate cost (negligible - Flash is $0.075/M input, $0.30/M output)
            input_tokens = response.usage_metadata.prompt_token_count
            output_tokens = response.usage_metadata.candidates_token_count
            cost = self._calculate_flash_cost(input_tokens, output_tokens)

            # Determine chunk strategy based on complexity
            strategy = self._determine_strategy(analysis["complexity_score"])

            result = {
                "complexity_score": analysis["complexity_score"],
                "complexity_tier": strategy["tier"],
                "recommended_chunks": strategy["chunks"],
                "target_words": strategy["target_words"],
                "subtopics": analysis.get("subtopics", []),
                "chunk_focus_areas": analysis.get("chunk_focus_areas", []),
                "estimated_depth": analysis.get("estimated_depth", "medium"),
                "reasoning": analysis.get("reasoning", ""),
                "cost": cost
            }

            logger.info(
                "adaptive_chunking.complete",
                topic=topic,
                complexity_score=result["complexity_score"],
                tier=result["complexity_tier"],
                chunks=result["recommended_chunks"],
                cost=float(cost)
            )

            return result

        except json.JSONDecodeError as e:
            logger.error(
                "adaptive_chunking.json_parse_failed",
                error=str(e),
                response=response_text
            )
            # Fallback to medium complexity (3 chunks)
            return self._get_fallback_strategy(topic)

        except Exception as e:
            logger.error("adaptive_chunking.failed", error=str(e))
            # Fallback to medium complexity (3 chunks)
            return self._get_fallback_strategy(topic)

    def _build_analysis_prompt(self, topic: str, research: Optional[Dict]) -> str:
        """Build complexity analysis prompt for Gemini"""
        research_context = ""
        if research:
            research_content = research.get("content", "")[:1000] if isinstance(research, dict) else str(research)[:1000]
            research_context = f"\n\nRESEARCH CONTEXT:\n{research_content}"

        return f"""Analyze the complexity of this content topic and recommend a chunking strategy.

TOPIC: {topic}{research_context}

Rate the complexity on a scale of 1-10 considering:
1. **Number of Subtopics** - How many distinct aspects need coverage?
2. **Required Depth** - How deep must each aspect be explored?
3. **Technical Complexity** - How technical or specialized is the subject?
4. **Data Requirements** - How much data/statistics/examples are needed?
5. **Target Length** - How comprehensive should the article be?

COMPLEXITY SCALE:
- **1-3 (Simple)**: Single concept, basic explanation
  - Examples: "What is a digital nomad?", "Benefits of remote work"
  - Can be covered in 2 chunks: Introduction + Practical Guide

- **4-7 (Medium)**: Multiple related concepts, moderate depth
  - Examples: "Portugal D7 Visa Guide", "Best Digital Nomad Cities"
  - Needs 3 chunks: Introduction + Main Content + Practical Guide

- **8-10 (Complex)**: Many interconnected concepts, deep analysis
  - Examples: "Tax Optimization for Multi-Country Nomads", "Complete Guide to EU Immigration"
  - Requires 4-5 chunks: Introduction + Main Content 1 + Main Content 2 + Advanced Topics + Practical Guide

Return your analysis as JSON:
{{
  "complexity_score": 7,
  "subtopics": ["Subtopic 1", "Subtopic 2", "Subtopic 3"],
  "chunk_focus_areas": [
    "Introduction + Overview",
    "Requirements + Process",
    "Practical Guide + Examples"
  ],
  "estimated_depth": "medium",
  "reasoning": "Brief explanation of score"
}}

Respond with ONLY the JSON object, no other text."""

    def _determine_strategy(self, complexity_score: int) -> Dict:
        """
        Determine chunking strategy based on complexity score

        Args:
            complexity_score: 1-10 complexity rating

        Returns:
            Dict with tier, chunks, target_words
        """
        if complexity_score <= 3:
            return {
                "tier": "simple",
                "chunks": 2,
                "target_words": 2500
            }
        elif complexity_score <= 7:
            return {
                "tier": "medium",
                "chunks": 3,
                "target_words": 3500
            }
        elif complexity_score <= 9:
            return {
                "tier": "complex",
                "chunks": 4,
                "target_words": 5000
            }
        else:
            return {
                "tier": "expert",
                "chunks": 5,
                "target_words": 6000
            }

    def _get_fallback_strategy(self, topic: str) -> Dict:
        """
        Fallback strategy if analysis fails

        Defaults to medium complexity (3 chunks) for safety
        """
        logger.warning(
            "adaptive_chunking.using_fallback",
            topic=topic,
            message="Defaulting to medium complexity (3 chunks)"
        )

        return {
            "complexity_score": 5,
            "complexity_tier": "medium",
            "recommended_chunks": 3,
            "target_words": 3500,
            "subtopics": [],
            "chunk_focus_areas": [
                "Introduction + Overview",
                "Main Content + Requirements",
                "Practical Guide + Conclusion"
            ],
            "estimated_depth": "medium",
            "reasoning": "Fallback to medium complexity due to analysis failure",
            "cost": Decimal("0.00")
        }

    def _calculate_flash_cost(self, input_tokens: int, output_tokens: int) -> Decimal:
        """
        Calculate Gemini 2.5 Flash cost

        Pricing:
        - Input: $0.075/M tokens
        - Output: $0.30/M tokens
        """
        input_cost = Decimal(input_tokens) / Decimal(1_000_000) * Decimal("0.075")
        output_cost = Decimal(output_tokens) / Decimal(1_000_000) * Decimal("0.30")
        return input_cost + output_cost

    def build_chunk_briefs(self, chunk_count: int, subtopics: list, focus_areas: list) -> list:
        """
        Build chunk briefs based on recommended strategy

        Args:
            chunk_count: Number of chunks to generate (2-5)
            subtopics: List of subtopics to cover
            focus_areas: List of focus areas for chunks

        Returns:
            List of chunk brief dicts
        """
        if chunk_count == 2:
            return self._build_2_chunk_briefs(subtopics, focus_areas)
        elif chunk_count == 3:
            return self._build_3_chunk_briefs(subtopics, focus_areas)
        elif chunk_count == 4:
            return self._build_4_chunk_briefs(subtopics, focus_areas)
        else:  # 5 chunks
            return self._build_5_chunk_briefs(subtopics, focus_areas)

    def _build_2_chunk_briefs(self, subtopics: list, focus_areas: list) -> list:
        """Simple topics: Introduction + Practical Guide"""
        return [
            {
                "chunk_number": 1,
                "chunk_type": "introduction",
                "focus": "Introduction + Core Concept",
                "target_words": 1200,
                "sections": ["Hook", "Overview", "Key Points"]
            },
            {
                "chunk_number": 2,
                "chunk_type": "practical",
                "focus": "Practical Application + Examples",
                "target_words": 1300,
                "sections": ["How-To", "Examples", "Next Steps"]
            }
        ]

    def _build_3_chunk_briefs(self, subtopics: list, focus_areas: list) -> list:
        """Medium topics: Introduction + Main Content + Practical Guide"""
        return [
            {
                "chunk_number": 1,
                "chunk_type": "introduction",
                "focus": "Introduction + Overview",
                "target_words": 1000,
                "sections": ["Hook", "Overview", "Background"]
            },
            {
                "chunk_number": 2,
                "chunk_type": "main_content",
                "focus": "Main Content + Requirements",
                "target_words": 1500,
                "sections": ["Requirements", "Process", "Pitfalls"]
            },
            {
                "chunk_number": 3,
                "chunk_type": "practical_guide",
                "focus": "Practical Guide + Conclusion",
                "target_words": 1000,
                "sections": ["Tips", "Examples", "Conclusion"]
            }
        ]

    def _build_4_chunk_briefs(self, subtopics: list, focus_areas: list) -> list:
        """Complex topics: Introduction + 2x Main Content + Practical Guide"""
        return [
            {
                "chunk_number": 1,
                "chunk_type": "introduction",
                "focus": "Introduction + Strategic Overview",
                "target_words": 1000,
                "sections": ["Hook", "Overview", "Strategic Context"]
            },
            {
                "chunk_number": 2,
                "chunk_type": "main_content_1",
                "focus": "Core Requirements + Process",
                "target_words": 1500,
                "sections": ["Requirements", "Step-by-Step", "Timeline"]
            },
            {
                "chunk_number": 3,
                "chunk_type": "main_content_2",
                "focus": "Advanced Topics + Edge Cases",
                "target_words": 1500,
                "sections": ["Advanced", "Edge Cases", "Optimization"]
            },
            {
                "chunk_number": 4,
                "chunk_type": "practical_guide",
                "focus": "Practical Implementation + Resources",
                "target_words": 1000,
                "sections": ["Implementation", "Examples", "Resources"]
            }
        ]

    def _build_5_chunk_briefs(self, subtopics: list, focus_areas: list) -> list:
        """Expert topics: Introduction + 3x Main Content + Practical Guide"""
        return [
            {
                "chunk_number": 1,
                "chunk_type": "introduction",
                "focus": "Introduction + Strategic Framework",
                "target_words": 1000,
                "sections": ["Hook", "Overview", "Framework"]
            },
            {
                "chunk_number": 2,
                "chunk_type": "main_content_1",
                "focus": "Foundation + Core Concepts",
                "target_words": 1500,
                "sections": ["Foundation", "Core Concepts", "Principles"]
            },
            {
                "chunk_number": 3,
                "chunk_type": "main_content_2",
                "focus": "Implementation + Process",
                "target_words": 1500,
                "sections": ["Implementation", "Step-by-Step", "Best Practices"]
            },
            {
                "chunk_number": 4,
                "chunk_type": "main_content_3",
                "focus": "Advanced Optimization + Edge Cases",
                "target_words": 1500,
                "sections": ["Advanced", "Optimization", "Edge Cases"]
            },
            {
                "chunk_number": 5,
                "chunk_type": "practical_guide",
                "focus": "Practical Guide + Case Studies",
                "target_words": 1000,
                "sections": ["Case Studies", "Examples", "Resources"]
            }
        ]
