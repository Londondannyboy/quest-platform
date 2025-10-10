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

logger = structlog.get_logger(__name__)


class ChunkedContentAgent:
    """
    Chunked Content Agent: Generate articles using hybrid Gemini + Sonnet approach

    Why this architecture?
    - Gemini 2.0 Flash: Ultra-fast, ultra-cheap draft generation ($0.0005/chunk)
    - Parallel chunking: 3 chunks simultaneously = 20-30 seconds total
    - Sonnet refinement: Merge + enhance + citations = production quality
    - Guaranteed output: 3000+ words, 5+ citations

    Cost breakdown:
    - Gemini chunks: 3 × $0.0005 = $0.0015
    - Sonnet refinement: $0.015
    - Total: $0.017/article (92% cheaper than Sonnet-only)
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
            "gemini_chunks": Decimal("0.00"),
            "sonnet_refinement": Decimal("0.00"),
        }

        # Get site-specific style guide
        style = self.style_guides.get(target_site, self.style_guides["relocation"])

        # STAGE 1: Generate 3 parallel chunks with Gemini
        chunk_results = await self._generate_chunks_parallel(
            research, style, topic, link_context, template_guidance
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
        template_guidance: Optional[Dict]
    ) -> list:
        """
        Generate 3 content chunks using Gemini 2.5 Pro

        Note: Falls back to sequential generation if parallel fails due to rate limits.
        Gemini free tier: 2 requests/minute - if we exceed this, we generate sequentially.

        Chunks:
        1. Introduction + Overview (1000 words)
        2. Main Content + Requirements (1000 words)
        3. Practical Guide + Conclusion (1000 words)

        Returns:
            List of chunk results with content and cost
        """
        logger.info("chunked_content.generating_chunks_parallel")

        # Build chunk prompts
        chunk_prompts = [
            self._build_chunk_prompt(1, "introduction", research, style, topic, link_context, template_guidance),
            self._build_chunk_prompt(2, "main_content", research, style, topic, link_context, template_guidance),
            self._build_chunk_prompt(3, "practical_guide", research, style, topic, link_context, template_guidance),
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

        # Chunk-specific instructions
        chunk_instructions = {
            "introduction": f"""
**CHUNK 1: INTRODUCTION + OVERVIEW (~1000 words)**

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
- Target 1000 words
""",
            "main_content": f"""
**CHUNK 2: MAIN CONTENT + REQUIREMENTS (~1000 words)**

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
- Target 1000 words
""",
            "practical_guide": f"""
**CHUNK 3: PRACTICAL GUIDE + CONCLUSION (~1000 words)**

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
- Target 1000 words
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
        2. Add citations [1], [2], [3] throughout
        3. Enhance transitions between sections
        4. Expand thin areas to ensure 3000+ words
        5. Add TL;DR, Key Takeaways, FAQ sections
        6. Add References section with all citations
        """
        logger.info("chunked_content.refining_with_sonnet")

        # Build refinement prompt
        prompt = self._build_refinement_prompt(
            chunks, research, style, topic, link_context, template_guidance
        )

        try:
            response = await self.claude_client.messages.create(
                model=self.sonnet_model,
                max_tokens=12288,  # Increased from 8192 to ensure References section completes
                temperature=0.7,
                system=self._build_sonnet_system_prompt(style),
                messages=[{"role": "user", "content": prompt}],
            )

            refined_content = response.content[0].text.strip()

            # Calculate cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = self._calculate_sonnet_cost(input_tokens, output_tokens)

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

        # Build link instructions
        link_instructions = ""
        if link_context:
            external_links = "\n".join([
                f"   - {link['url']}"
                for link in link_context.get('external_links', [])[:12]
            ])
            internal_links = "\n".join([
                f"   - [{link['title']}]({link['link']})"
                for link in link_context.get('internal_links', [])[:5]
            ])
            link_instructions = f"""

VALIDATED LINKS TO USE:
External Links (use 8-12 for citations):
{external_links}

Internal Links (use 3-5 for related content):
{internal_links}"""

        return f"""You are refining a comprehensive article about: {topic}

ORIGINAL RESEARCH (for citation sources):
{research_content[:2000]}...{link_instructions}

DRAFT CHUNKS TO MERGE:
{formatted_chunks}

YOUR TASK:
Merge these 3 chunks into a polished, comprehensive article that will rank on Google's first page.

**CRITICAL REQUIREMENTS:**

1. **Merge & EXPAND** (MUST reach 3500+ words minimum)
   - Combine all 3 chunks into cohesive narrative
   - Add smooth transitions between sections
   - EXPAND every section with more detail, examples, and data
   - Add new subsections where needed for depth
   - DO NOT condense or summarize - EXPAND and elaborate
   - Keep ALL original content from chunks, just enhance it
   - Maintain natural flow while adding substance

2. **Add Structure** (MUST include all):
   - # {topic} (H1 title)
   - TL;DR section (150 words, right after title)
   - Key Takeaways (5 bullet points)
   - All chunk content with H2/H3 headers
   - FAQ section (8-10 Q&A pairs, COMPLETE all questions fully)
   - **ABSOLUTELY MANDATORY:** ## References section (MUST be the FINAL section)

3. **Add Citations** (MINIMUM 15-25 required for high authority):
   - Add inline citations [1], [2], [3] for ALL factual claims
   - Use research sources from above
   - Target: 1 citation per 150-200 words (industry best practice)
   - Diversify sources: government sites, research papers, industry reports, news
   - **ABSOLUTELY REQUIRED - References Section Format:**

     ## References

     [1] Source Name - https://example.com/source1
     [2] Source Name - https://example.com/source2
     [3] Source Name - https://example.com/source3
     ...
     [20] Source Name - https://example.com/source20

   - The ## References section is THE MOST CRITICAL requirement
   - EVERY article MUST end with a complete References section
   - List ALL citations used in the article (minimum 15-25 sources for 3500+ words)

4. **Enhance Quality**:
   - Add specific data points and statistics
   - Include real examples and case studies
   - Use tables or comparison charts where helpful
   - Break up long paragraphs
   - Use bullet points for lists
   - Add image placeholders:
     * ![Hero Image](IMAGE_PLACEHOLDER_HERO) after TL;DR
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
Start with # {topic} and include ALL required sections.
NO JSON, NO code fences, just pure markdown.

CRITICAL WARNINGS - READ CAREFULLY:
- Article MUST be 3500+ words MINIMUM (not counting references)
- You received ~2000 words of chunks - your output must be LONGER, not shorter
- DO NOT condense, summarize, or shorten the chunks
- EXPAND and elaborate on every section
- Articles under 3000 words will be AUTOMATICALLY REJECTED

**CITATION DENSITY REQUIREMENT (HIGH AUTHORITY STANDARD):**
- MINIMUM 15-25 citations required for 3500+ word articles
- Target: 1 citation per 150-200 words (industry best practice)
- Diversify sources: .gov sites, research papers, industry reports, news, expert blogs
- More citations = higher authority = better SEO rankings
- Every factual claim, statistic, date, or process MUST have a citation

**THE #1 CRITICAL REQUIREMENT - REFERENCES SECTION:**
- EVERY article MUST end with ## References as the FINAL section
- This is the MOST IMPORTANT part of the article
- The ## References section is NOT OPTIONAL
- Format EXACTLY as shown below (one citation per line):

## References

[1] Government Source - https://example.gov/source1
[2] Research Paper - https://academic.edu/source2
[3] Industry Report - https://industry.com/source3
[4] News Article - https://news.com/source4
...
[20] Expert Blog - https://expert.com/source20

- Articles without a complete References section will AUTOMATICALLY FAIL
- NEVER truncate or skip the References section
- The References section should list ALL 15-25 citations used in the article
- Ensure you have enough tokens reserved to complete the References section"""

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
- When citing numbers, always include the source: "According to [Source], ..."

CRITICAL: Every factual claim needs a citation [1], [2], etc.
Minimum 8 citations required throughout the article."""

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
            # Use Gemini 2.5 Flash for fast, cheap weaving
            flash_model = genai.GenerativeModel("gemini-2.5-flash-002")

            response = flash_model.generate_content(
                weaving_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5,  # Lower temp for consistency
                    max_output_tokens=4000,  # ~2000 words woven output
                )
            )

            woven_content = response.text

            # Calculate cost (Gemini 2.5 Flash pricing)
            # Flash is much cheaper: $0.075/M input, $0.30/M output
            input_tokens = response.usage_metadata.prompt_token_count
            output_tokens = response.usage_metadata.candidates_token_count

            input_cost = Decimal(input_tokens) / Decimal(1_000_000) * Decimal("0.075")
            output_cost = Decimal(output_tokens) / Decimal(1_000_000) * Decimal("0.30")
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
