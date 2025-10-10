# Peer Review Debug Guide: Content Generation Issues

**Created:** October 10, 2025
**Status:** Production system generating low-quality articles (25-35/100 quality, 524-889 words)
**Goal:** Diagnose why Sonnet is producing short articles with no citations

---

## Problem Statement

The Quest Platform is generating articles that consistently fail quality checks:

**Symptoms:**
- Word count: 524-889 words (need 3000+)
- Citations: 0-2 (need 5+ with [1], [2] format)
- Quality scores: 25-35/100 (need 80+)
- No References section
- Articles rejected or require human review

**Expected Behavior:**
- Word count: 3000-3800 words
- Citations: 8-12 inline citations
- Quality scores: 80-90/100
- Complete References section

---

## Current Architecture (What's Happening)

```
Research (cache hit) → Gemini Compression (DISABLED) → Sonnet Generation → Editor Validation → REJECT
                                                       ↓
                                               524-889 words, 0-2 citations
```

**Key Logs from Test Runs:**
```
[warning] gemini_summarizer.no_api_key - Gemini API key not configured
[info] content_agent.complete - cost=0.0140895 input_tokens=3093 output_tokens=1260
[info] editor_agent.citation_validation - citations=0 passed=False word_count=524
[info] editor_agent.complete - score=25 decision=reject
```

---

## Root Cause Analysis

### Issue #1: Sonnet Stopping Early (CRITICAL)

**File:** `backend/app/agents/content.py`
**Lines:** 137-143

```python
response = await self.client.messages.create(
    model=self.model,
    max_tokens=8192,  # Required parameter - Claude will stop naturally when article is complete
    temperature=0.7,
    system=system_prompt,
    messages=[{"role": "user", "content": prompt}],
)
```

**Problem:** Sonnet is stopping at 1260 output tokens (524-889 words) instead of continuing to 3000+ words.

**Hypothesis:** The prompt may not be emphatic enough about minimum word count, OR Sonnet is interpreting the 8192 max_tokens as a soft target.

**Check:**
1. Does the prompt clearly state "MINIMUM 3000 words required"? (content.py:356)
2. Is the prompt reinforcing this requirement multiple times?
3. Are we providing enough research context for a 3000+ word article?

### Issue #2: No Citations Being Generated (CRITICAL)

**File:** `backend/app/agents/content.py`
**Lines:** 351-352

```python
7. **CRITICAL: Use inline citations [1], [2], [3] for all factual claims** - Minimum 5 citations required
8. **CRITICAL: Add References section at the end** - List all sources in [1], [2], [3] format with URLs
```

**Problem:** Despite explicit instructions, Sonnet is not adding citations.

**Hypothesis:** Either:
1. The research data doesn't contain source URLs
2. The prompt formatting isn't clear enough
3. Sonnet is prioritizing other requirements over citations

**Check:**
1. Review research data structure - does it include `sources` array with URLs?
2. Is the link_context being passed correctly? (orchestrator.py:177-183)
3. Are example citations shown in the prompt?

### Issue #3: Research Data May Be Too Large/Too Small

**File:** `backend/app/agents/orchestrator.py`
**Lines:** 159-174

```python
gemini_result = await self.gemini_summarizer.compress_research(
    research_result.get("research", {}),
    topic,
    target_site
)
costs["gemini_compression"] = gemini_result["cost"]

# Use compressed research for content generation (saves 90% on input tokens!)
compressed_research = gemini_result["compressed_research"]
```

**Current Behavior:** Gemini summarizer is DISABLED (no API key), so compression is skipped:
```
[warning] gemini_summarizer.no_api_key
[info] orchestrator.research_compressed - compression_ratio=100.00%
```

**Problem:** Without compression, research might be too verbose OR research is being used uncompressed.

**Check:**
1. What's the actual size of the research being passed to Sonnet? (log `len(compressed_research)`)
2. Is the research comprehensive enough to support 3000 words?
3. Should we require Gemini compression to work?

### Issue #4: Gemini Chunked Content Not Being Used

**File:** `backend/app/agents/orchestrator.py`
**Lines:** 193-219

```python
if settings.ENABLE_CHUNKED_CONTENT and self.chunked_content_agent:
    # Use Gemini 2.5 Pro chunks + Sonnet refinement
    content_result = await self.chunked_content_agent.generate(...)
else:
    # Single-shot Sonnet (current behavior)
    content_result = await self.content_agent.run(...)
```

**Current State:**
- `ENABLE_CHUNKED_CONTENT=True` (default)
- `GEMINI_API_KEY` is NOT set
- `self.chunked_content_agent` is None (conditional init at line 56)
- Falls back to single-shot Sonnet

**Problem:** The new chunked content system (which guarantees 3000+ words) is not being used because Gemini API key is missing.

**Solution:** Add `GEMINI_API_KEY` to `.env` file.

---

## Investigation Steps (Priority Order)

### Step 1: Add Debug Logging to Content Agent

**File:** `backend/app/agents/content.py`
**Location:** After line 143 (after API response)

```python
# Add this logging:
logger.info(
    "content_agent.response_details",
    model=self.model,
    input_tokens=response.usage.input_tokens,
    output_tokens=response.usage.output_tokens,
    stop_reason=response.stop_reason,  # NEW - why did it stop?
    content_preview=response.content[0].text[:500]  # First 500 chars
)
```

**Why:** We need to see WHY Sonnet is stopping (stop_reason could be `end_turn`, `max_tokens`, or `stop_sequence`).

### Step 2: Log Research Data Size

**File:** `backend/app/agents/orchestrator.py`
**Location:** After line 174 (after compression)

```python
# Add this logging:
logger.info(
    "orchestrator.research_stats",
    compressed_size=len(str(compressed_research)),
    compression_enabled=gemini_result["cost"] > 0,
    source_count=len(research_result.get("sources", [])),
    has_urls=any("url" in s for s in research_result.get("sources", []))
)
```

**Why:** We need to verify research contains URLs and is appropriately sized.

### Step 3: Add Metrics Footer to Articles

**File:** `backend/app/agents/content.py`
**Location:** After line 193 (when building article_data dict)

```python
# Add metrics footer to content
metrics_footer = f"""

---

<!-- GENERATION METRICS -->
<!--
Model: {self.model}
Input Tokens: {input_tokens}
Output Tokens: {output_tokens}
Cost: ${float(cost):.4f}
Word Count: {len(cleaned_json.split())}
Stop Reason: {response.stop_reason}
Research Sources: {len(research.get("sources", []))} sources
Generation Time: {response.usage.total_duration if hasattr(response.usage, 'total_duration') else 'N/A'}
-->
"""

article_data["content"] += metrics_footer
```

**Why:** This allows us to inspect generated articles and see exactly what happened during generation.

### Step 4: Test Chunked Content Generation

**Action:** Add Gemini API key and test the chunked approach:

```bash
# In .env file:
GEMINI_API_KEY="your-gemini-api-key"

# Test generation:
python3 backend/generate_article.py \
  --topic "Test Article with Chunked Content" \
  --site relocation
```

**Expected Log Output:**
```
[info] orchestrator.using_chunked_content - Gemini 2.5 Pro chunks + Sonnet refinement
[info] chunked_content.chunks_complete - chunk_count=3 total_words=~3000
[info] chunked_content.refinement_complete - word_count=3500+ citations=10+
```

---

## Code Sections to Review

### Priority 1: Content Generation Prompts

**File:** `backend/app/agents/content.py`

**Key Sections:**
1. **Lines 356-377:** Main prompt OUTPUT FORMAT section
   - Check: Is "MINIMUM 3000 words required" emphatic enough?
   - Check: Are citations instructions clear?

2. **Lines 265-377:** `_build_prompt()` method
   - Review entire prompt structure
   - Verify citations example is shown
   - Confirm word count requirement is repeated multiple times

3. **Lines 216-249:** `_build_link_instructions()`
   - Verify sources are being formatted correctly
   - Check if external_links have URLs

### Priority 2: Orchestrator Research Flow

**File:** `backend/app/agents/orchestrator.py`

**Key Sections:**
1. **Lines 150-174:** Research + Gemini compression
   - Add logging for research size
   - Verify compression is working (or failing gracefully)

2. **Lines 177-183:** Link validation
   - Check if `sources` array is populated
   - Verify link_context structure

3. **Lines 193-219:** Content generation (chunked vs single-shot)
   - Verify chunked agent initialization (line 56)
   - Add logging for which path is taken

### Priority 3: Editor Validation

**File:** `backend/app/agents/editor.py`

**Key Sections:**
1. **Lines 359-413:** `_validate_citations()` method
   - Review citation regex pattern (line 375)
   - Check if it's finding citations correctly
   - Verify References section detection (line 379)

2. **Lines 499-516:** `_make_decision()` method
   - Currently set to VERY low thresholds for debugging (score >= 20 → review)
   - Should be reset to production values once fixed

---

## Quick Diagnostic Commands

```bash
# 1. Check if Gemini API key is set
grep "GEMINI_API_KEY" backend/.env

# 2. Check which model is configured
grep "CONTENT_MODEL" backend/.env

# 3. View last generated article to see metrics
cat backend/generation_summary.json | jq '.costs'

# 4. Check research cache
psql $DATABASE_URL -c "SELECT topic, length(research_data::text) as size, created_at FROM article_research ORDER BY created_at DESC LIMIT 5;"

# 5. Generate test article with verbose logging
LOG_LEVEL=DEBUG python3 backend/generate_article.py --topic "Test Article" --site relocation
```

---

## Expected Fix

**The chunked content approach should solve this:**

1. **Gemini 2.5 Pro generates 3 chunks in parallel (guaranteed 3000 words)**
2. **Sonnet merges + adds citations (guaranteed 5+ citations)**
3. **Editor validates (should pass with 80-90 quality)**

**But first we need:**
1. Add `GEMINI_API_KEY` to `.env`
2. Add debug logging to understand why single-shot Sonnet is failing
3. Add metrics footer to track generation details

---

## Questions for Debugging Session

1. **Why is Sonnet stopping at ~1260 output tokens?**
   - Check stop_reason in API response
   - Review prompt for confusing instructions
   - Verify max_tokens isn't being interpreted as target

2. **Why are citations not being generated?**
   - Check if research sources contain URLs
   - Review citation instruction clarity in prompt
   - Test with manual citation examples in prompt

3. **Should we abandon single-shot Sonnet?**
   - If chunked approach works, make it the default
   - Keep single-shot as fallback only
   - Document limitations of single-shot approach

---

## Success Criteria

After fixes, test article should show:
- ✅ Word count: 3000-3800 words
- ✅ Citations: 8-12 inline citations [1], [2], [3]
- ✅ References section: Present with URLs
- ✅ Quality score: 80-90/100
- ✅ Metrics footer: Shows generation stats
- ✅ Decision: "publish" or "review" (not "reject")

---

**Next Reviewer:** Please start with Step 1 (add debug logging) and run a test generation. The logs will reveal why Sonnet is stopping early and not adding citations.
