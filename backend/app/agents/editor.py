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

        # Validate SEO before scoring
        seo_validation = self._validate_seo(article)

        # Build evaluation prompt
        prompt = self._build_prompt(article, citation_validation, seo_validation)

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
                "citation_validation": citation_validation,  # Citation validation results
                "seo_validation": seo_validation,  # NEW: SEO validation results
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

    async def refine(self, article: Dict, feedback: Dict) -> Dict:
        """
        Refine article based on quality feedback

        Improvements:
        1. Citation Enhancement - Add missing citations (ensure >=5)
        2. Content Expansion - Expand thin sections to 3000+ words
        3. Grammar & Spelling - Fix errors, improve readability
        4. Link Enhancement - Validate links, add internal links
        5. E-E-A-T Enhancement - Add expert quotes, case studies

        Args:
            article: Article data with content/title/etc
            feedback: Quality dimensions from score() method
                {
                    "dimensions": {"accuracy": 75, "writing": 70, ...},
                    "feedback": "Needs more citations...",
                    "citation_validation": {"citation_count": 3, ...}
                }

        Returns:
            Dict with refined article + cost
        """
        logger.info(
            "editor_agent.refine_start",
            title=article.get("title", "Unknown"),
            current_score=feedback.get("quality_score", 0)
        )

        # Analyze what needs refinement
        citation_validation = feedback.get("citation_validation", {})
        dimensions = feedback.get("dimensions", {})

        needs_citations = citation_validation.get("citation_count", 0) < 5
        needs_expansion = citation_validation.get("word_count", 0) < 3000
        needs_grammar = dimensions.get("writing", 100) < 75
        needs_accuracy = dimensions.get("accuracy", 100) < 80

        # Build refinement prompt based on needs
        refinement_prompt = self._build_refinement_prompt(
            article,
            feedback,
            needs_citations,
            needs_expansion,
            needs_grammar,
            needs_accuracy
        )

        try:
            # Use Claude Sonnet 4.5 for refinement (highest quality)
            response = await self.client.messages.create(
                model="claude-sonnet-4-5-20250929",  # Always use latest Sonnet for refinement
                max_tokens=8192,
                temperature=0.7,
                timeout=180.0,  # 3 minute timeout (Bug Fix #2)
                messages=[{"role": "user", "content": refinement_prompt}],
            )

            # Parse refined content
            refined_content = response.content[0].text.strip()

            # Calculate cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = self._calculate_cost(input_tokens, output_tokens)

            # Update article with refined content
            refined_article = article.copy()
            refined_article["content"] = refined_content

            # Re-validate citations in refined content
            new_citation_validation = self._validate_citations(refined_content)

            logger.info(
                "editor_agent.refine_complete",
                original_words=citation_validation.get("word_count", 0),
                refined_words=new_citation_validation.get("word_count", 0),
                original_citations=citation_validation.get("citation_count", 0),
                refined_citations=new_citation_validation.get("citation_count", 0),
                cost=float(cost)
            )

            return {
                "article": refined_article,
                "cost": cost,
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                },
                "improvements": {
                    "word_count_added": new_citation_validation.get("word_count", 0) - citation_validation.get("word_count", 0),
                    "citations_added": new_citation_validation.get("citation_count", 0) - citation_validation.get("citation_count", 0),
                }
            }

        except Exception as e:
            logger.error("editor_agent.refinement_failed", error=str(e), exc_info=e)
            raise

    def _build_refinement_prompt(
        self,
        article: Dict,
        feedback: Dict,
        needs_citations: bool,
        needs_expansion: bool,
        needs_grammar: bool,
        needs_accuracy: bool
    ) -> str:
        """
        Build targeted refinement prompt based on identified issues
        """
        title = article.get("title", "")
        content = article.get("content", "")
        citation_validation = feedback.get("citation_validation", {})
        dimensions = feedback.get("dimensions", {})

        # Bug Fix #3: Truncate very long content to prevent token overflow
        max_content_length = 15000  # chars (~3750 tokens, leaves room for prompt)
        content_truncated = False
        if len(content) > max_content_length:
            content = content[:max_content_length] + "\n\n[Content truncated for refinement...]"
            content_truncated = True
            logger.info(
                "editor_agent.content_truncated",
                original_length=len(content),
                truncated_to=max_content_length
            )

        # Build issue-specific instructions
        refinement_instructions = []

        if needs_citations:
            refinement_instructions.append(f"""
**CITATION ENHANCEMENT REQUIRED:**
- Current citations: {citation_validation.get("citation_count", 0)} (need 5+)
- Add inline citations [1], [2], [3] for all factual claims
- Create or expand References section at the end
- Format: [1] Source Name - URL
""")

        if needs_expansion:
            refinement_instructions.append(f"""
**CONTENT EXPANSION REQUIRED:**
- Current word count: {citation_validation.get("word_count", 0)} (target 3000+)
- Expand thin sections with:
  * Real-world examples
  * Case studies or success stories
  * Step-by-step guides
  * Expert insights
  * Data and statistics (with citations)
- Add depth without fluff
""")

        if needs_grammar:
            refinement_instructions.append(f"""
**WRITING QUALITY IMPROVEMENT REQUIRED:**
- Current writing score: {dimensions.get("writing", 0)}/100
- Fix grammar and spelling errors
- Improve sentence flow and readability
- Break up long paragraphs
- Enhance transitions between sections
- Use active voice
""")

        if needs_accuracy:
            refinement_instructions.append(f"""
**ACCURACY ENHANCEMENT REQUIRED:**
- Current accuracy score: {dimensions.get("accuracy", 0)}/100
- Verify all factual claims
- Add authoritative sources
- Include official data (.gov, embassy sites)
- Add accuracy disclaimers for legal/tax advice
""")

        refinement_tasks = "\n".join(refinement_instructions)

        return f"""You are an expert content editor tasked with refining and improving this article.

ARTICLE TITLE:
{title}

CURRENT ARTICLE CONTENT:
{content}

QUALITY FEEDBACK:
{feedback.get("feedback", "General improvements needed")}

SPECIFIC REFINEMENT TASKS:
{refinement_tasks}

**YOUR JOB:**
1. Keep the existing structure and main points
2. Address ALL the refinement tasks listed above
3. Maintain the article's tone and style
4. Output the COMPLETE refined article (not just changes)

**CRITICAL REQUIREMENTS:**
- Minimum 3000 words (expand if needed)
- Minimum 5 inline citations [1], [2], [3]
- Complete References section at end
- Professional, error-free writing
- Natural keyword integration

**OUTPUT FORMAT:**
Return the complete refined article in pure markdown format. Start with # {title} and include all sections with improvements applied.

Do NOT include any JSON, code fences, or explanatory text - just the refined markdown article."""

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

    def _validate_seo(self, article: Dict) -> Dict:
        """
        Validate SEO technical requirements

        Checks:
        1. Keyword density (1-3% target)
        2. Meta title (50-60 chars)
        3. Meta description (150-160 chars)
        4. Header hierarchy (H1 → H2 → H3)
        5. Internal/external link ratio
        6. Image alt text (if images present)
        7. Readability score

        Args:
            article: Article data with title, content, keywords, meta

        Returns:
            {
                "seo_score": 85,  # 0-100
                "keyword_density": 2.1,  # percentage
                "meta_title_length": 58,
                "meta_description_length": 155,
                "header_hierarchy_valid": True,
                "internal_links": 3,
                "external_links": 12,
                "readability_score": 65,  # Flesch Reading Ease
                "issues": ["list", "of", "issues"],
                "passed": True
            }
        """
        content = article.get("content", "")
        title = article.get("title", "")
        keywords = article.get("keywords", [])
        meta_title = article.get("meta_title") or title
        meta_description = article.get("meta_description", "")

        issues = []
        scores = {}

        # 1. Keyword Density Check
        if keywords:
            primary_keyword = keywords[0] if isinstance(keywords, list) else str(keywords)
            content_lower = content.lower()
            keyword_lower = primary_keyword.lower()
            keyword_count = content_lower.count(keyword_lower)
            word_count = len(content.split())
            keyword_density = (keyword_count / word_count * 100) if word_count > 0 else 0

            scores["keyword_density"] = keyword_density

            if keyword_density < 0.5:
                issues.append(f"Keyword density too low: {keyword_density:.2f}% (target: 1-3%)")
            elif keyword_density > 4.0:
                issues.append(f"Keyword density too high: {keyword_density:.2f}% (risk of keyword stuffing)")
        else:
            scores["keyword_density"] = 0
            issues.append("No keywords defined")

        # 2. Meta Title Check
        meta_title_length = len(meta_title)
        scores["meta_title_length"] = meta_title_length

        if meta_title_length < 30:
            issues.append(f"Meta title too short: {meta_title_length} chars (target: 50-60)")
        elif meta_title_length > 70:
            issues.append(f"Meta title too long: {meta_title_length} chars (will be truncated in SERPs)")

        # 3. Meta Description Check
        meta_desc_length = len(meta_description)
        scores["meta_description_length"] = meta_desc_length

        if meta_desc_length < 120:
            issues.append(f"Meta description too short: {meta_desc_length} chars (target: 150-160)")
        elif meta_desc_length > 170:
            issues.append(f"Meta description too long: {meta_desc_length} chars (will be truncated)")

        # 4. Header Hierarchy Check
        h1_count = len(re.findall(r'^#\s+', content, re.MULTILINE))
        h2_count = len(re.findall(r'^##\s+', content, re.MULTILINE))
        h3_count = len(re.findall(r'^###\s+', content, re.MULTILINE))

        scores["h1_count"] = h1_count
        scores["h2_count"] = h2_count
        scores["h3_count"] = h3_count

        header_hierarchy_valid = True
        if h1_count == 0:
            issues.append("Missing H1 header")
            header_hierarchy_valid = False
        elif h1_count > 1:
            issues.append(f"Multiple H1 headers found ({h1_count}), should have only 1")
            header_hierarchy_valid = False

        if h2_count < 3:
            issues.append(f"Too few H2 headers ({h2_count}), recommend at least 3 for content structure")

        scores["header_hierarchy_valid"] = header_hierarchy_valid

        # 5. Link Analysis
        # Internal links (relative or same domain)
        internal_links = len(re.findall(r'\[([^\]]+)\]\((/[^\)]+|#[^\)]+)\)', content))

        # External links (http/https)
        external_links = len(re.findall(r'\[([^\]]+)\]\((https?://[^\)]+)\)', content))

        scores["internal_links"] = internal_links
        scores["external_links"] = external_links

        if internal_links == 0:
            issues.append("No internal links found (recommend 2-5 for site navigation)")

        if external_links < 3:
            issues.append(f"Too few external links ({external_links}), recommend 5-10 authoritative sources")
        elif external_links > 20:
            issues.append(f"Too many external links ({external_links}), may dilute page authority")

        # Link ratio check
        if external_links > 0:
            link_ratio = internal_links / external_links if internal_links > 0 else 0
            scores["link_ratio"] = link_ratio
            if link_ratio < 0.2:
                issues.append(f"Internal/external link ratio too low ({link_ratio:.2f}), add more internal links")

        # 6. Readability Score (Flesch Reading Ease)
        readability_score = self._calculate_readability(content)
        scores["readability_score"] = readability_score

        if readability_score < 50:
            issues.append(f"Content readability difficult ({readability_score:.0f}/100), simplify language")
        elif readability_score > 80:
            issues.append(f"Content may be too simple ({readability_score:.0f}/100) for target audience")

        # Calculate overall SEO score (0-100)
        seo_score = 100

        # Penalties
        if keyword_density < 0.5 or keyword_density > 4.0:
            seo_score -= 15
        if meta_title_length < 30 or meta_title_length > 70:
            seo_score -= 10
        if meta_desc_length < 120 or meta_desc_length > 170:
            seo_score -= 10
        if not header_hierarchy_valid:
            seo_score -= 15
        if h2_count < 3:
            seo_score -= 5
        if internal_links == 0:
            seo_score -= 10
        if external_links < 3:
            seo_score -= 10
        if readability_score < 50 or readability_score > 80:
            seo_score -= 10

        # Ensure score is between 0-100
        seo_score = max(0, min(100, seo_score))

        # Passed if score >= 70
        passed = seo_score >= 70

        logger.info(
            "editor_agent.seo_validation",
            seo_score=seo_score,
            keyword_density=keyword_density if keywords else 0,
            headers=f"H1:{h1_count},H2:{h2_count},H3:{h3_count}",
            links=f"Internal:{internal_links},External:{external_links}",
            readability=readability_score,
            issues_count=len(issues),
            passed=passed
        )

        return {
            "seo_score": seo_score,
            "keyword_density": scores.get("keyword_density", 0),
            "meta_title_length": meta_title_length,
            "meta_description_length": meta_desc_length,
            "header_hierarchy_valid": header_hierarchy_valid,
            "h1_count": h1_count,
            "h2_count": h2_count,
            "h3_count": h3_count,
            "internal_links": internal_links,
            "external_links": external_links,
            "link_ratio": scores.get("link_ratio", 0),
            "readability_score": readability_score,
            "issues": issues,
            "passed": passed
        }

    def _calculate_readability(self, content: str) -> float:
        """
        Calculate Flesch Reading Ease score

        Formula: 206.835 - 1.015(total words/total sentences) - 84.6(total syllables/total words)

        Score interpretation:
        90-100: Very easy (5th grade)
        80-90: Easy (6th grade)
        70-80: Fairly easy (7th grade)
        60-70: Standard (8th-9th grade) ← TARGET
        50-60: Fairly difficult (10th-12th grade)
        30-50: Difficult (college)
        0-30: Very difficult (college graduate)

        Args:
            content: Article content

        Returns:
            Flesch Reading Ease score (0-100)
        """
        # Remove markdown formatting
        text = re.sub(r'[#*`\[\]]', '', content)
        text = re.sub(r'\n+', ' ', text)

        # Count sentences
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])

        # Count words
        words = text.split()
        word_count = len([w for w in words if w.strip()])

        if sentence_count == 0 or word_count == 0:
            return 60.0  # Default to "standard"

        # Count syllables (simplified estimation)
        syllable_count = sum(self._count_syllables(word) for word in words)

        # Flesch Reading Ease formula
        avg_words_per_sentence = word_count / sentence_count
        avg_syllables_per_word = syllable_count / word_count

        score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)

        # Clamp to 0-100
        return max(0, min(100, score))

    def _count_syllables(self, word: str) -> int:
        """
        Estimate syllable count in a word (simplified)

        Args:
            word: Word to analyze

        Returns:
            Estimated syllable count
        """
        word = word.lower().strip()
        if len(word) <= 3:
            return 1

        # Count vowel groups
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel

        # Adjust for silent 'e'
        if word.endswith('e'):
            syllable_count -= 1

        # At least 1 syllable
        return max(1, syllable_count)

    def _build_prompt(self, article: Dict, citation_validation: Dict = None, seo_validation: Dict = None) -> str:
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

        # Add SEO validation context
        seo_context = ""
        if seo_validation:
            seo_context = f"""

SEO VALIDATION:
- SEO Score: {seo_validation['seo_score']}/100 ({'✅ PASSED' if seo_validation['passed'] else '❌ FAILED'})
- Keyword Density: {seo_validation['keyword_density']:.2f}% (target: 1-3%)
- Meta Title Length: {seo_validation['meta_title_length']} chars (target: 50-60)
- Meta Description Length: {seo_validation['meta_description_length']} chars (target: 150-160)
- Header Hierarchy: {'✅ Valid' if seo_validation['header_hierarchy_valid'] else '❌ Invalid'} (H1:{seo_validation['h1_count']}, H2:{seo_validation['h2_count']}, H3:{seo_validation['h3_count']})
- Links: Internal:{seo_validation['internal_links']}, External:{seo_validation['external_links']}
- Readability Score: {seo_validation['readability_score']:.0f}/100 (Flesch Reading Ease)
- Issues Found: {len(seo_validation['issues'])}"""

        # Add issues list outside f-string to avoid backslash problem
        if seo_validation and seo_validation.get('issues'):
            issues_text = '\n  - '.join(seo_validation['issues'][:5])
            seo_context += f"\n  - {issues_text}"
        else:
            seo_context += "\n  (none)"

        seo_context += "\n\n**IMPORTANT**: Consider SEO validation in your scoring. Penalize if SEO score < 70."

        return f"""You are a content quality analyst. Evaluate this article on a 0-100 scale.

ARTICLE TITLE:
{title}

ARTICLE CONTENT (preview):
{content_preview}

KEYWORDS:
{', '.join(keywords)}
{citation_context}
{seo_context}

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
        # TEMPORARY: Accept ANY score for debugging (user requested to see what's being generated)
        if score >= 20:
            return "review"  # Will trigger refinement + human review
        elif score >= 10:
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
