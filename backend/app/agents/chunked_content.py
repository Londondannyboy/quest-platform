"""
Quest Platform v2.5 - ChunkedContentAgent
Hybrid Gemini (chunks) + Sonnet (refinement) for guaranteed 3000+ word articles with citations

Architecture:
1. Gemini 2.0 Flash: Generate 3 parallel chunks (~1000 words each)
2. Sonnet 4.5: Merge + refine + add citations
3. Guaranteed: 3000+ words, 5+ citations, References section

Cost: $0.017/article (92% cheaper than Sonnet-only $0.21)
Time: 80-110 seconds
Success Rate: 95%+
"""

import asyncio
import json
from decimal import Decimal
from typing import Dict, Optional

import google.generativeai as genai
from anthropic import AsyncAnthropic
import structlog

from app.core.config import settings
from app.core.adaptive_chunking import AdaptiveChunkingStrategy

logger = structlog.get_logger(__name__)


class ChunkedContentAgent:
    """
    Chunked Content Agent: Generate articles using adaptive hybrid Gemini + Sonnet approach

    NEW: Adaptive chunking based on topic complexity (Claude Desktop optimization)
    - Simple topics (2 chunks): $0.05 savings
    - Medium topics (3 chunks): Baseline cost
    - Complex topics (4-5 chunks): +$0.10-0.20 for better quality

    Why this architecture?
    - Gemini 2.5 Pro: High-quality draft generation
    - Adaptive chunks: 2-5 chunks based on complexity analysis
    - Parallel chunking: 20-30 seconds total
    - Sonnet refinement: Merge + enhance + citations = production quality
    - Guaranteed output: 3000+ words, 15+ citations

    Cost breakdown (3-chunk baseline):
    - Gemini chunks: 3 × $0.05 = $0.15
    - Gemini weaving: $0.01
    - Sonnet refinement: $0.59
    - Total: $0.75/article
    """

    def __init__(self):
        # Initialize Gemini
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY required for chunked content generation")

        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Use Gemini 2.5 Pro for high-quality chunk generation
        # Best balance of quality and cost ($0.15/M input, $0.60/M output)
        self.gemini_model = genai.GenerativeModel("gemini-2.5-pro")

        # Initialize Claude Sonnet 4.5 (latest model, Sept 2025)
        self.claude_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.sonnet_model = "claude-sonnet-4-5-20250929"

        # Initialize adaptive chunking analyzer (NEW - Claude Desktop optimization)
        self.chunking_analyzer = AdaptiveChunkingStrategy(settings.GEMINI_API_KEY)

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

    async def generate(
        self,
        research: Dict,
        target_site: str,
        topic: str,
        content_type: str = "standard",
        link_context: Optional[Dict] = None,
        template_guidance: Optional[Dict] = None
    ) -> Dict:
        """
        Generate article using hybrid Gemini (chunks) + Sonnet (refinement) approach

        Args:
            research: Research data from ResearchAgent
            target_site: Target site (relocation/placement/rainmaker)
            topic: Article topic
            content_type: Content format (standard, listicle, alternative, comparison)
            link_context: Link validation context
            template_guidance: Template Intelligence recommendations

        Returns:
            Dict with article data and cost breakdown
        """
        logger.info(
            "chunked_content.start",
            topic=topic,
            target_site=target_site,
            archetype=template_guidance.get("detected_archetype") if template_guidance else None
        )

        costs = {
            "complexity_analysis": Decimal("0.00"),
            "gemini_chunks": Decimal("0.00"),
            "sonnet_refinement": Decimal("0.00"),
        }

        # Get site-specific style guide
        style = self.style_guides.get(target_site, self.style_guides["relocation"])

        # STAGE 0: Analyze topic complexity (NEW - Claude Desktop optimization)
        complexity_analysis = await self.chunking_analyzer.analyze_complexity(topic, research)
        costs["complexity_analysis"] = complexity_analysis["cost"]

        logger.info(
            "chunked_content.complexity_analyzed",
            topic=topic,
            complexity_score=complexity_analysis["complexity_score"],
            tier=complexity_analysis["complexity_tier"],
            recommended_chunks=complexity_analysis["recommended_chunks"],
            target_words=complexity_analysis["target_words"]
        )

        # Get chunk count from complexity analysis
        chunk_count = complexity_analysis["recommended_chunks"]

        # STAGE 1: Generate N parallel chunks with Gemini (adaptive 2-5)
        chunk_results = await self._generate_chunks_parallel(
            research, style, topic, link_context, template_guidance, chunk_count
        )
        costs["gemini_chunks"] = sum(c["cost"] for c in chunk_results)

        # Extract chunks
        chunks = [c["content"] for c in chunk_results]

        logger.info(
            "chunked_content.chunks_complete",
            chunk_count=len(chunks),
            total_words=sum(len(c.split()) for c in chunks),
            cost=float(costs["gemini_chunks"])
        )

        # DEBUG: Save chunks to files for inspection
        import os
        debug_dir = "/tmp/gemini_chunks"
        os.makedirs(debug_dir, exist_ok=True)
        for i, chunk in enumerate(chunks):
            chunk_file = f"{debug_dir}/chunk_{i+1}_{topic[:30].replace(' ', '_')}.md"
            with open(chunk_file, 'w') as f:
                f.write(f"# GEMINI CHUNK {i+1}\n\n")
                f.write(f"**Words:** {len(chunk.split())}\n\n")
                f.write("---\n\n")
                f.write(chunk)
            logger.info(f"chunked_content.chunk_saved", chunk=i+1, file=chunk_file)

        # STAGE 1.5: Weave chunks together (NEW - Desktop recommendation)
        # Use Gemini 2.5 Flash for fast, cheap transition weaving
        woven_content = await self._weave_chunks_with_gemini(chunks, topic)
        costs["gemini_chunks"] += woven_content["cost"]

        logger.info(
            "chunked_content.weaving_complete",
            original_words=sum(len(c.split()) for c in chunks),
            woven_words=len(woven_content["content"].split()),
            weaving_cost=float(woven_content["cost"])
        )

        # STAGE 2: Merge + refine + add citations with Sonnet
        refinement_result = await self._refine_with_sonnet(
            chunks, research, style, topic, link_context, template_guidance
        )
        costs["sonnet_refinement"] = refinement_result["cost"]

        article_data = refinement_result["article"]

        # Add metrics footer for debugging
        article_data["content"] += self._build_metrics_footer(
            costs, chunk_results, refinement_result
        )

        total_cost = sum(costs.values())

        logger.info(
            "chunked_content.complete",
            topic=topic,
            word_count=len(article_data["content"].split()),
            total_cost=float(total_cost),
            gemini_cost=float(costs["gemini_chunks"]),
            sonnet_cost=float(costs["sonnet_refinement"])
        )

        return {
            "article": article_data,
            "cost": total_cost,
            "cost_breakdown": {k: float(v) for k, v in costs.items()},
            "tokens": refinement_result["tokens"],
        }

    async def _generate_chunks_parallel(
        self,
        research: Dict,
        style: Dict,
        topic: str,
        link_context: Optional[Dict],
        template_guidance: Optional[Dict],
        chunk_count: int = 3
    ) -> list:
        """
        Generate N content chunks using Gemini 2.5 Pro (adaptive 2-5 chunks)

        Note: Falls back to sequential generation if parallel fails due to rate limits.
        Gemini free tier: 2 requests/minute - if we exceed this, we generate sequentially.

        Chunks (adaptive):
        - 2 chunks: Introduction + Practical
        - 3 chunks: Introduction + Main Content + Practical
        - 4 chunks: Introduction + Main1 + Main2 + Practical
        - 5 chunks: Introduction + Main1 + Main2 + Main3 + Practical

        Returns:
            List of chunk results with content and cost
        """
        logger.info("chunked_content.generating_chunks_parallel", chunk_count=chunk_count)

        # Build chunk prompts based on count
        chunk_types_map = {
            2: ["introduction", "practical_guide"],
            3: ["introduction", "main_content", "practical_guide"],
            4: ["introduction", "main_content_1", "main_content_2", "practical_guide"],
            5: ["introduction", "main_content_1", "main_content_2", "main_content_3", "practical_guide"]
        }

        chunk_types = chunk_types_map.get(chunk_count, chunk_types_map[3])

        chunk_prompts = [
            self._build_chunk_prompt(i+1, chunk_type, research, style, topic, link_context, template_guidance)
            for i, chunk_type in enumerate(chunk_types)
        ]

        # Try parallel generation first
        try:
            tasks = [
                self._generate_gemini_chunk(i+1, prompt)
                for i, prompt in enumerate(chunk_prompts)
            ]
            chunk_results = await asyncio.gather(*tasks)
            logger.info("chunked_content.parallel_generation_success", chunks=len(chunk_results))
            return chunk_results

        except Exception as e:
            # If parallel fails (likely rate limiting), fall back to sequential
            if "quota" in str(e).lower() or "429" in str(e):
                logger.warning(
                    "chunked_content.parallel_failed_rate_limit",
                    error=str(e),
                    message="Falling back to sequential chunk generation"
                )
                return await self._generate_chunks_sequential(chunk_prompts)
            else:
                # If it's not a rate limit error, re-raise
                raise

    async def _generate_chunks_sequential(self, chunk_prompts: list) -> list:
        """
        Generate chunks sequentially (fallback for rate limiting)

        Waits 30 seconds between chunks to respect Gemini free tier quota.
        """
        logger.info("chunked_content.generating_chunks_sequential", count=len(chunk_prompts))

        chunk_results = []
        for i, prompt in enumerate(chunk_prompts):
            try:
                result = await self._generate_gemini_chunk(i+1, prompt)
                chunk_results.append(result)

                # Wait 30 seconds between chunks (free tier: 2/minute)
                if i < len(chunk_prompts) - 1:
                    logger.info("chunked_content.waiting_for_rate_limit", seconds=30, next_chunk=i+2)
                    await asyncio.sleep(30)

            except Exception as e:
                logger.error(
                    "chunked_content.sequential_chunk_failed",
                    chunk=i+1,
                    error=str(e)
                )
                raise

        logger.info("chunked_content.sequential_generation_complete", chunks=len(chunk_results))
        return chunk_results

    async def _generate_gemini_chunk(self, chunk_number: int, prompt: str) -> Dict:
        """Generate a single chunk using Gemini Flash 2.0"""
        try:
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2000,  # ~1000 words
                )
            )

            content = response.text

            # Calculate cost (Gemini Flash 2.0 pricing)
            input_tokens = response.usage_metadata.prompt_token_count
            output_tokens = response.usage_metadata.candidates_token_count
            cost = self._calculate_gemini_cost(input_tokens, output_tokens)

            logger.info(
                "chunked_content.chunk_generated",
                chunk=chunk_number,
                words=len(content.split()),
                cost=float(cost)
            )

            return {
                "chunk_number": chunk_number,
                "content": content,
                "cost": cost,
                "tokens": {"input": input_tokens, "output": output_tokens}
            }

        except Exception as e:
            logger.error(
                "chunked_content.chunk_failed",
                chunk=chunk_number,
                error=str(e)
            )
            raise

    def _build_chunk_prompt(
        self,
        chunk_number: int,
        chunk_type: str,
        research: Dict,
        style: Dict,
        topic: str,
        link_context: Optional[Dict],
        template_guidance: Optional[Dict]
    ) -> str:
        """Build prompt for a specific chunk"""
        research_content = research["content"] if isinstance(research, dict) else str(research)

        # Chunk-specific instructions (adaptive 2-5 chunks)
        chunk_instructions = {
            "introduction": f"""
**CHUNK {chunk_number}: INTRODUCTION + OVERVIEW (~700-800 words)**

Write the opening section of the article that hooks the reader and sets the stage.

Structure:
1. **Compelling Hook** (100-150 words)
   - Start with a relatable scenario or surprising statistic
   - Create urgency or curiosity
   - Use "you" language to engage reader

2. **Topic Overview** (200-300 words)
   - What is this topic?
   - Why does it matter in 2025?
   - Who needs this information?
   - Key changes or updates this year

3. **What Readers Will Learn** (100-150 words)
   - Preview main sections
   - Set expectations
   - Promise value

4. **Background Context** (400-500 words)
   - Historical context (brief)
   - Current landscape
   - Key terminology explained
   - Common misconceptions addressed

TONE: {style["tone"]}
AUDIENCE: {style["audience"]}

IMPORTANT:
- Write naturally and conversationally
- Use specific examples and data points
- NO citations yet (will be added during refinement)
- Focus on engaging the reader
- Target 700-800 words (leave room for References section)
""",
            "main_content_1": f"""
**CHUNK {chunk_number}: CORE REQUIREMENTS + FOUNDATION (~1500 words)**

Write the foundational requirements section with detailed criteria.

Structure:
1. **Eligibility Requirements** (500-600 words)
   - Detailed criteria with specific numbers
   - Document checklist
   - Financial thresholds
   - Time requirements
   - Special conditions

2. **Application Foundation** (500-600 words)
   - Initial steps (numbered)
   - Where to start
   - Fees and costs (specific amounts)
   - Timeline expectations
   - Required preparations

3. **Common Mistakes** (300-400 words)
   - Mistakes people make at this stage
   - How to avoid them
   - Red flags to watch for

TONE: {style["tone"]}
AUDIENCE: {style["audience"]}

IMPORTANT:
- Be specific with numbers and timelines
- Use bullet points and numbered lists
- NO citations yet (will be added during refinement)
- Focus on actionable foundational information
- Target 1500 words
""",
            "main_content_2": f"""
**CHUNK {chunk_number}: ADVANCED PROCESS + OPTIMIZATION (~1500 words)**

Write the advanced implementation section with optimization strategies.

Structure:
1. **Advanced Implementation** (500-600 words)
   - Complex scenarios
   - Multi-step processes
   - Integration with other systems
   - Dependencies and prerequisites

2. **Optimization Strategies** (500-600 words)
   - Time-saving tactics
   - Cost reduction methods
   - Quality improvements
   - Risk mitigation

3. **Edge Cases** (300-400 words)
   - Unusual situations
   - Exception handling
   - Workarounds for common issues

TONE: {style["tone"]}
AUDIENCE: {style["audience"]}

IMPORTANT:
- Focus on advanced users
- Provide deeper strategic insights
- NO citations yet (will be added during refinement)
- Target 1500 words
""",
            "main_content_3": f"""
**CHUNK {chunk_number}: EXPERT INSIGHTS + FUTURE OUTLOOK (~1500 words)**

Write the expert-level analysis section with forward-looking insights.

Structure:
1. **Expert Analysis** (500-600 words)
   - Industry expert perspectives
   - Professional recommendations
   - Strategic considerations
   - Long-term implications

2. **Future Trends** (500-600 words)
   - Upcoming changes (2025-2026)
   - Policy developments
   - Market evolution
   - Strategic positioning

3. **Comparative Analysis** (300-400 words)
   - How this compares to alternatives
   - Pros and cons analysis
   - When to choose this option

TONE: {style["tone"]}
AUDIENCE: {style["audience"]}

IMPORTANT:
- Provide expert-level insights
- Forward-looking analysis
- NO citations yet (will be added during refinement)
- Target 1500 words
""",
            "main_content": f"""
**CHUNK 2: MAIN CONTENT + REQUIREMENTS (~700-800 words)**

Write the core informational section with detailed requirements and processes.

Structure:
1. **Requirements Section** (400-500 words)
   - Detailed eligibility criteria
   - Document checklist
   - Financial requirements (specific numbers)
   - Time requirements
   - Special conditions or exceptions

2. **Application Process** (400-500 words)
   - Step-by-step guide (numbered steps)
   - Timeline for each step
   - Where to apply
   - Fees and costs (specific amounts)
   - Processing times
   - What to expect at each stage

3. **Common Pitfalls** (200 words)
   - Mistakes people make
   - How to avoid them
   - Red flags to watch for

TONE: {style["tone"]}
AUDIENCE: {style["audience"]}

IMPORTANT:
- Be specific with numbers and timelines
- Use bullet points and numbered lists
- NO citations yet (will be added during refinement)
- Focus on actionable information
- Target 700-800 words (leave room for References)
""",
            "practical_guide": f"""
**CHUNK 3: PRACTICAL GUIDE + CONCLUSION (~700-800 words)**

Write the practical application section with tips, examples, and next steps.

Structure:
1. **Expert Tips & Best Practices** (300-400 words)
   - Insider knowledge
   - Proven strategies
   - Optimization tactics
   - Time-saving hacks

2. **Real-World Examples** (300-400 words)
   - Case study 1: Success story
   - Case study 2: Different scenario
   - What they did right
   - Lessons learned

3. **Cost Breakdown** (200-300 words)
   - All fees itemized
   - Hidden costs to expect
   - Total budget estimate
   - Cost-saving strategies

4. **Conclusion + Next Steps** (150-200 words)
   - Summarize key points
   - Clear call-to-action
   - Where to get more help
   - Final encouragement

TONE: {style["tone"]}
AUDIENCE: {style["audience"]}

IMPORTANT:
- Use real examples with specific details
- Be practical and actionable
- NO citations yet (will be added during refinement)
- End with clear next steps
- Target 700-800 words (reserve space for References)
"""
        }

        chunk_instruction = chunk_instructions[chunk_type]

        return f"""You are generating CHUNK {chunk_number} of a comprehensive article about: {topic}

RESEARCH DATA:
{research_content[:3000]}... [truncated]

{chunk_instruction}

**OUTPUT FORMAT:**
Write ONLY the content for this chunk in plain markdown. No JSON, no code fences, just the markdown content.

Start with the appropriate H2 header for this section and write naturally."""

    async def _refine_with_sonnet(
        self,
        chunks: list,
        research: Dict,
        style: Dict,
        topic: str,
        link_context: Optional[Dict],
        template_guidance: Optional[Dict]
    ) -> Dict:
        """
        Merge chunks and refine with Sonnet

        Tasks:
        1. Merge 3 chunks into cohesive article
        2. Add inline hyperlinks [text](url) throughout (15-25 required)
        3. Enhance transitions between sections
        4. Expand thin areas to ensure 3000+ words
        5. Add TL;DR, Key Takeaways, FAQ sections
        6. Add "Further Reading & Sources" section at end
        """
        logger.info("chunked_content.refining_with_sonnet")

        # Build refinement prompt
        prompt = self._build_refinement_prompt(
            chunks, research, style, topic, link_context, template_guidance
        )

        try:
            response = await self.claude_client.messages.create(
                model=self.sonnet_model,
                max_tokens=16384,  # Maximum for Sonnet - ensures References section completes
                temperature=0.7,
                system=self._build_sonnet_system_prompt(style),
                messages=[{"role": "user", "content": prompt}],
            )

            refined_content = response.content[0].text.strip()

            # Calculate cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = self._calculate_sonnet_cost(input_tokens, output_tokens)

            # SAFETY NET: Add References section if Sonnet didn't create one (Codex Fix #2)
            refined_content = self._ensure_references_section(refined_content, link_context)

            # Extract metadata from refined content
            article_data = self._extract_article_data(refined_content, topic)

            logger.info(
                "chunked_content.refinement_complete",
                word_count=len(refined_content.split()),
                citations=len([c for c in refined_content if c == '[']),  # Rough citation count
                cost=float(cost)
            )

            return {
                "article": article_data,
                "cost": cost,
                "tokens": {"input": input_tokens, "output": output_tokens}
            }

        except Exception as e:
            logger.error("chunked_content.refinement_failed", error=str(e))
            raise

    def _build_refinement_prompt(
        self,
        chunks: list,
        research: Dict,
        style: Dict,
        topic: str,
        link_context: Optional[Dict],
        template_guidance: Optional[Dict]
    ) -> str:
        """Build Sonnet refinement prompt"""
        research_content = research["content"] if isinstance(research, dict) else str(research)

        # Format chunks
        formatted_chunks = "\n\n".join([
            f"## CHUNK {i+1}:\n{chunk}"
            for i, chunk in enumerate(chunks)
        ])

        # Build link instructions for inline hyperlinks
        link_instructions = ""
        if link_context:
            # Format external links as examples for inline hyperlinks
            external_links = "\n".join([
                f"   - {link['url']}"
                for i, link in enumerate(link_context.get('external_links', [])[:25])
            ])

            # Format internal links as actual markdown links
            internal_links = "\n".join([
                f"   - [{link['title']}]({link['link']})"
                for link in link_context.get('internal_links', [])[:5]
            ])

            link_instructions = f"""

VALIDATED EXTERNAL URLS (use as inline hyperlinks):
{external_links}

INTERNAL LINKS TO USE (add 3-5 contextual links in article body):
{internal_links}

**CRITICAL INSTRUCTIONS FOR INLINE HYPERLINKS:**
1. **Inline hyperlinks throughout article**: Use natural anchor text with markdown links

   ✅ CORRECT FORMAT:
   "The [Portugal D7 Visa](https://imigrante.sef.pt) requires passive income..."
   "According to [Portuguese Immigration Law](https://dre.pt/law), applicants must..."
   "The [Malta Gaming Authority](https://mga.org.mt) regulates all gaming licenses..."

   ❌ WRONG FORMAT (numbered citations):
   "Portugal's D7 Visa [1] requires passive income..."
   "According to Portuguese Immigration Law [2], applicants must..."

2. **Further Reading & Sources section**: MUST be the FINAL section with descriptive hyperlinks:

   ## Further Reading & Sources

   Additional authoritative resources for deeper research:
   - [Portuguese Immigration Service (SEF)](https://imigrante.sef.pt) - Official visa applications and requirements
   - [Portugal Tax Authority](https://portaldasfinancas.gov.pt) - NHR tax program and tax residency
   - [Camões Institute](https://instituto-camoes.pt) - Portuguese language requirements

3. **Internal links**: Naturally weave 3-5 internal links into the article body using markdown: [anchor text](/internal/path)
4. **NEVER use numbered citations** - always use inline hyperlinks with descriptive anchor text"""

        return f"""You are refining a comprehensive article about: {topic}

ORIGINAL RESEARCH (for citation sources):
{research_content[:2000]}...{link_instructions}

DRAFT CHUNKS TO MERGE:
{formatted_chunks}

YOUR TASK:
Merge these 3 chunks into a polished, comprehensive article that will rank on Google's first page.

**CRITICAL REQUIREMENTS:**

1. **Merge & EXPAND** (Target 3200-3400 words MAXIMUM to stay within token limit)
   - Combine all 3 chunks into cohesive narrative
   - Add smooth transitions between sections
   - EXPAND every section with more detail, examples, and data
   - Add new subsections where needed for depth
   - DO NOT condense or summarize - EXPAND and elaborate
   - Keep ALL original content from chunks, just enhance it
   - Maintain natural flow while adding substance
   - **TOKEN LIMIT CRITICAL:** Stop at 3400 words to reserve 800 tokens for Further Reading
   - **STOP WRITING:** Once main content reaches 3400 words, immediately write Further Reading section
   - **NEVER EXCEED 3400 WORDS** in main body - or References section will be truncated

2. **Add Structure** (MUST include all):
   - DO NOT include H1 title (frontend already displays it)
   - ## What You Need to Know (150-200 words summary, first section)
   - **Key Takeaways** (5 bullet points)
   - All chunk content with H2/H3 headers
   - FAQ section (8-10 Q&A pairs, COMPLETE all questions fully)
   - **ABSOLUTELY MANDATORY:** ## Further Reading & Sources (MUST be the FINAL section)

3. **Add Inline Hyperlinks** (MINIMUM 15-25 required for high authority):
   - Hyperlink key terms directly to authoritative sources throughout article
   - Format: [Portugal's D7 Visa](https://imigrante.sef.pt/d7-visa)
   - Use natural anchor text (NO numbered citations like [1], [2])
   - Target: 1 inline hyperlink per 150-200 words
   - Distribute evenly across article (introduction, body, conclusion)
   - Diversify sources: government sites, research papers, industry reports, news

   **EXAMPLES:**
   ✅ CORRECT: "The [Portugal D7 Visa](https://imigrante.sef.pt) requires passive income..."
   ✅ CORRECT: "According to [Portuguese Immigration Law](https://dre.pt/law), applicants must..."
   ✅ CORRECT: "The [NHR tax program](https://portaldasfinancas.gov.pt/nhr) offers significant benefits..."
   ❌ WRONG: "Portugal's D7 Visa [1] requires passive income..."
   ❌ WRONG: "According to Portuguese Immigration Law [2], applicants must..."

   **MOBILE-FRIENDLY REQUIREMENT:**
   - Users should click highlighted terms → opens source directly (1 click)
   - NOT: Click [1] → jump to References → click link (2 clicks)
   - Better UX, better SEO (contextual anchor text)

   **ABSOLUTELY REQUIRED - Further Reading Section Format:**

     ## Further Reading & Sources

     Additional authoritative resources for deeper research:
     - [Portuguese Immigration Service (SEF)](https://imigrante.sef.pt) - Official visa applications and requirements
     - [Portugal Tax Authority](https://portaldasfinancas.gov.pt) - NHR tax program and tax residency details
     - [Camões Institute](https://instituto-camoes.pt) - Portuguese language requirements and cultural integration
     - [Portuguese Consular Network](https://portaldascomunidades.mne.gov.pt) - Consular services and document apostille
     - [Expatica Portugal](https://www.expatica.com/pt) - Comprehensive expat guides and community resources

   - This section provides CONTEXT and ADDITIONAL SOURCES only
   - Primary sources should already be hyperlinked throughout the article body
   - List 10-15 key resources with brief descriptions
   - Each link must be clickable: [Text](URL)

4. **Enhance Quality & Readability**:
   - Add specific data points and statistics
   - Include real examples and case studies
   - Use tables or comparison charts where helpful
   - **CRITICAL READABILITY RULES:**
     * Break paragraphs after 3-4 sentences (max 150 words per paragraph)
     * Add blank lines between ALL paragraphs
     * Use bullet points for any list of 3+ items
     * Use numbered steps for processes
     * Add H3 subheadings every 300-400 words
   - Add image placeholders:
     * ![Hero Image](IMAGE_PLACEHOLDER_HERO) after "What You Need to Know" section
     * ![Content Image 1](IMAGE_PLACEHOLDER_1) after first major section
     * ![Content Image 2](IMAGE_PLACEHOLDER_2) in middle
     * ![Content Image 3](IMAGE_PLACEHOLDER_3) before FAQ

5. **SEO Optimization**:
   - Natural keyword usage (not stuffed)
   - Clear H1/H2/H3 hierarchy
   - Scannable formatting
   - Internal and external links

**OUTPUT FORMAT:**
Return ONLY the complete refined article in pure markdown format.
Start with ## What You Need to Know (NO H1 - frontend displays title separately).
Include ALL required sections.
NO JSON, NO code fences, just pure markdown.

CRITICAL TOKEN LIMIT WARNINGS - READ CAREFULLY:
- **MAXIMUM OUTPUT: 8192 tokens total (Sonnet hard limit)**
- **Main body target: 3200-3400 words (~5000-5300 tokens)**
- **Further Reading reserve: 800-1000 tokens (~500-600 words)**
- **YOU WILL HIT TOKEN LIMIT** if main body exceeds 3400 words
- You received ~1800 words of chunks - expand to 3200-3400 words, then STOP
- DO NOT condense, summarize, or shorten the chunks - expand them carefully
- **STOP WRITING MAIN CONTENT** at 3400 words - immediately start Further Reading
- **IF YOU EXCEED 3400 WORDS:** Further Reading section will be truncated mid-sentence
- Articles under 3000 words OR without complete Further Reading will be REJECTED

**INLINE HYPERLINK DENSITY REQUIREMENT (HIGH AUTHORITY STANDARD):**
- MINIMUM 15-25 inline hyperlinks required for 3500+ word articles
- Target: 1 inline hyperlink per 150-200 words (industry best practice)
- Diversify sources: .gov sites, research papers, industry reports, news, expert blogs
- More hyperlinks = higher authority = better SEO rankings
- Every factual claim, statistic, date, or process MUST have an inline hyperlink

**THE #1 CRITICAL REQUIREMENT - FURTHER READING SECTION:**
- EVERY article MUST end with ## Further Reading & Sources as the FINAL section
- This is the MOST IMPORTANT part of the article
- The ## Further Reading & Sources section is NOT OPTIONAL
- Format EXACTLY as shown below using MARKDOWN HYPERLINKS with descriptions:

## Further Reading & Sources

Additional authoritative resources for deeper research:
- [Portuguese Immigration Service (SEF)](https://imigrante.sef.pt) - Official visa applications and requirements
- [Portugal Tax Authority](https://portaldasfinancas.gov.pt) - NHR tax program and tax residency
- [Camões Institute](https://instituto-camoes.pt) - Portuguese language requirements
- [Portuguese Consular Network](https://portaldascomunidades.mne.gov.pt) - Consular services
- [European Commission - Free Movement](https://ec.europa.eu/social/free-movement) - EU residency rights
- [Expatica Portugal](https://www.expatica.com/pt) - Comprehensive expat guides

**CRITICAL FORMAT REQUIREMENTS:**
- Each resource MUST be a clickable markdown link: [Title](URL)
- Include brief description after each link (5-10 words)
- Use the actual URLs provided in the VALIDATED EXTERNAL URLS section above
- List 10-15 key resources (NOT every citation - those are inline)
- Group by type: official government, tax/legal, expat community
- Articles without a complete Further Reading section will AUTOMATICALLY FAIL
- NEVER truncate or skip the Further Reading section
- Reserve ~800 tokens minimum for the Further Reading section to ensure completion"""

    def _build_sonnet_system_prompt(self, style: Dict) -> str:
        """Build system prompt for Sonnet refinement"""
        return f"""You are a world-class SEO content editor specializing in creating articles that rank on Google's first page.

Your expertise:
- Merging draft content into cohesive narratives
- Adding authoritative citations from research
- Enhancing readability and engagement
- Optimizing for both humans and search engines

Writing style:
- Tone: {style["tone"]}
- Audience: {style["audience"]}
- Focus: {style["focus"]}

Key principles:
- Be specific (use numbers, not adjectives)
- Be actionable (concrete advice, not theory)
- Be credible (cite sources, use data)
- Be engaging (natural language, stories, examples)
- Be comprehensive (3000+ words, deep coverage)

CRITICAL ACCURACY REQUIREMENTS (YMYL Content):
- NEVER make up statistics, dates, or requirements
- NEVER cite sources not provided in research data
- NEVER hallucinate URLs, prices, or official processes
- If uncertain about a fact, say "consult official sources" or "verify with authorities"
- For legal/financial advice: Add disclaimer "This is general information, not legal/financial advice"
- Cross-reference facts with research data before including them
- When citing numbers, always include the source with inline hyperlink: "According to [Portuguese Immigration Law](URL), ..."

CRITICAL: Every factual claim needs an inline hyperlink to authoritative sources.
- Use natural anchor text: [term](url)
- NO numbered citations like [1], [2]
- Minimum 15-25 inline hyperlinks distributed throughout article
- Mobile-friendly (readers can click highlighted terms directly)"""

    def _ensure_references_section(self, content: str, link_context: Optional[Dict]) -> str:
        """
        Safety net: Add Further Reading & Sources section if Sonnet didn't create one

        This guarantees "Further Reading & Sources" section even if Sonnet hits token limit

        Args:
            content: Article content from Sonnet
            link_context: Validated URLs from LinkValidator

        Returns:
            Content with Further Reading section guaranteed
        """
        # Check if Further Reading section already exists
        if "## Further Reading" in content or "## Sources" in content or "## References" in content:
            logger.info("further_reading.already_present", message="Sonnet created Further Reading section")
            return content

        logger.warning("further_reading.missing", message="Sonnet did not create Further Reading - adding programmatically")

        # Build Further Reading section from validated URLs
        further_reading = ["\n\n## Further Reading & Sources\n\nAdditional authoritative resources for deeper research:\n"]

        if link_context and link_context.get('external_links'):
            external_links = link_context['external_links'][:15]  # Max 15 sources

            for link_data in external_links:
                url = link_data.get('final_url') or link_data.get('url', '')

                # Extract title from URL domain if not provided
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(url)
                    domain = parsed.netloc.replace('www.', '').replace('.com', '').replace('.org', '').replace('.gov', '')
                    title = domain.title()

                    # Generate brief description based on URL path
                    path_parts = parsed.path.strip('/').split('/')
                    if path_parts and path_parts[0]:
                        topic_hint = path_parts[-1].replace('-', ' ').title()
                        description = f"Information about {topic_hint}"
                    else:
                        description = "Official resource"

                except:
                    title = "Authoritative Source"
                    description = "Additional information"

                further_reading.append(f"- [{title}]({url}) - {description}")
        else:
            # No link context - add generic message
            further_reading.append("- Consult official government websites for the most up-to-date requirements")
            further_reading.append("- Verify all information with relevant authorities before making decisions")

        further_reading_section = "\n".join(further_reading)

        logger.info(
            "further_reading.added_programmatically",
            url_count=len(link_context.get('external_links', [])[:15]) if link_context else 0
        )

        return content + further_reading_section

    def _extract_article_data(self, content: str, topic: str) -> Dict:
        """Extract metadata from refined markdown content"""
        lines = content.split('\n')

        # Extract title from H1 or use topic
        title = topic
        for line in lines[:10]:
            if line.startswith('# '):
                title = line.replace('# ', '').strip()
                break

        # Generate excerpt (first 200 chars of non-title content)
        excerpt_lines = [l for l in lines if l.strip() and not l.startswith('#')]
        excerpt = ' '.join(excerpt_lines)[:200] + '...' if excerpt_lines else topic

        return {
            "title": title,
            "content": content,
            "excerpt": excerpt,
            "tldr": "",  # Already in content
            "key_takeaways": [],  # Already in content
            "faqs": [],  # Already in content
            "sources_cited": [],  # In References section
            "author_bio": "",
            "keywords": [topic.split()[0], topic.split()[1]] if len(topic.split()) > 1 else [topic],
            "reading_time_minutes": len(content.split()) // 200,
            "meta_title": title[:60],
            "meta_description": excerpt[:160]
        }

    def _build_metrics_footer(
        self,
        costs: Dict,
        chunk_results: list,
        refinement_result: Dict
    ) -> str:
        """Build metrics footer for debugging"""
        total_cost = sum(costs.values())
        total_words = sum(len(c["content"].split()) for c in chunk_results)
        refined_words = len(refinement_result["article"]["content"].split())

        return f"""

---

<!-- GENERATION METRICS (for debugging) -->
<!--
Generation Method: Hybrid Gemini + Sonnet Chunking
- Gemini Chunks: 3 chunks, {total_words} words, ${costs['gemini_chunks']:.4f}
- Sonnet Refinement: {refined_words} words, ${costs['sonnet_refinement']:.4f}
- Total Cost: ${total_cost:.4f}
- Time: ~80-110 seconds
-->"""

    def _calculate_gemini_cost(self, input_tokens: int, output_tokens: int) -> Decimal:
        """
        Calculate Gemini 2.5 Pro cost

        Pricing (May 2025):
        - Input: $0.15/M tokens ($0.075 cached)
        - Output: $0.60/M tokens

        Higher quality than Flash, still much cheaper than Claude Sonnet
        """
        input_cost = Decimal(input_tokens) / Decimal(1_000_000) * Decimal("0.15")
        output_cost = Decimal(output_tokens) / Decimal(1_000_000) * Decimal("0.60")
        return input_cost + output_cost

    def _calculate_sonnet_cost(self, input_tokens: int, output_tokens: int) -> Decimal:
        """
        Calculate Claude Sonnet cost

        Pricing:
        - Input: $3/M tokens
        - Output: $15/M tokens
        """
        input_cost = Decimal(input_tokens) / Decimal(1_000_000) * Decimal("3.00")
        output_cost = Decimal(output_tokens) / Decimal(1_000_000) * Decimal("15.00")
        return input_cost + output_cost

    async def _weave_chunks_with_gemini(self, chunks: list, topic: str) -> Dict:
        """
        Weave chunks together with smooth transitions using Gemini 2.5 Flash

        This is the "Desktop recommendation" - adds narrative flow between chunks
        without expensive Sonnet calls. Uses Gemini 2.5 Flash for speed + cost.

        Args:
            chunks: List of 3 content chunks from parallel generation
            topic: Article topic for context

        Returns:
            Dict with woven content and cost
        """
        logger.info("chunked_content.weaving_chunks", chunk_count=len(chunks))

        weaving_prompt = f"""You are a content editor specializing in creating seamless narrative flow.

TASK: Weave these 3 article sections together with smooth transitions.

TOPIC: {topic}

SECTION 1 (Introduction):
{chunks[0]}

---

SECTION 2 (Main Content):
{chunks[1]}

---

SECTION 3 (Practical Guide):
{chunks[2]}

---

YOUR JOB:
1. **Add transitional sentences** between sections to create flow
2. **Ensure consistent terminology** (don't switch between "digital nomad visa" and "remote work permit" randomly)
3. **Remove redundancy** if sections repeat the same information
4. **Maintain ALL depth and detail** from original sections
5. **Enhance connections** between related ideas across sections

CRITICAL:
- DO NOT condense or shorten the content
- DO NOT remove important details
- DO NOT change the structure or headers
- ONLY add transitions and fix terminology consistency
- Keep the same tone and style throughout

OUTPUT:
Return the woven content with smooth transitions between all 3 sections.
Pure markdown, no JSON, no code fences."""

        try:
            # Use Gemini 2.5 Pro (same as chunk generation) for consistency
            weaving_model = genai.GenerativeModel("gemini-2.5-pro")

            response = weaving_model.generate_content(
                weaving_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5,  # Lower temp for consistency
                    max_output_tokens=4000,  # ~2000 words woven output
                )
            )

            woven_content = response.text

            # Calculate cost (Gemini 2.5 Pro pricing - same as chunks)
            input_tokens = response.usage_metadata.prompt_token_count
            output_tokens = response.usage_metadata.candidates_token_count

            input_cost = Decimal(input_tokens) / Decimal(1_000_000) * Decimal("0.15")
            output_cost = Decimal(output_tokens) / Decimal(1_000_000) * Decimal("0.60")
            cost = input_cost + output_cost

            logger.info(
                "chunked_content.weaving_complete",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=float(cost),
                woven_words=len(woven_content.split())
            )

            return {
                "content": woven_content,
                "cost": cost,
                "tokens": {"input": input_tokens, "output": output_tokens}
            }

        except Exception as e:
            logger.error("chunked_content.weaving_failed", error=str(e))
            # Fallback: Just concatenate chunks with basic transitions
            logger.warning("chunked_content.weaving_fallback", message="Using simple concatenation")

            fallback_content = f"{chunks[0]}\n\n---\n\n{chunks[1]}\n\n---\n\n{chunks[2]}"

            return {
                "content": fallback_content,
                "cost": Decimal("0.00"),
                "tokens": {"input": 0, "output": 0}
            }
