# Codex Code Review Recommendations
**Date:** October 10, 2025 (Late Evening)
**Review Focus:** Chunked Content System (Gemini + Sonnet Hybrid)

---

## ✅ What's Working (Validated by Codex)

1. **Orchestrator wiring** - Gemini + Sonnet integration complete
2. **Chunk generation** - 3 parallel chunks (~1k words each)
3. **Sonnet refinement** - Expansion with citations, TL;DR, FAQ, References
4. **Debug files** - Chunks saved to `/tmp/gemini_chunks/` for inspection
5. **Metrics tracking** - Token counts, costs, stop reasons logged

**Test Results:**
- Gemini 2.5 Pro: 1,293 words (3 chunks)
- Sonnet 4.5: 5,344 words final (310% expansion!)
- Cost: $0.75/article
- Quality: High (just needed References section fix)

---

## 🎯 Recommendations (Priority Order)

### 1. ✅ COMPLETED - Handle Gemini Rate Limiting
**Status:** FIXED (Commit `3bce9f2`)

**Problem:** Gemini free tier 2 requests/minute - parallel chunks fail

**Solution:**
- Added try/catch around parallel generation
- Automatic fallback to sequential generation
- 30-second wait between chunks for free tier
- Still uses parallel on paid tier

**Impact:** 100% success rate vs 33% before

---

### 2. ⏳ HIGH PRIORITY - Enforce Citation/Word-Count Guarantees

**Codex Quote:**
> "Make that a real check: if the final article has < 8 [n] tags or < 3,500 words, fire an automated second refinement or inject a post-processing pass that adds the missing references before handing off to the editor."

**Current State:**
- ✅ max_tokens=12,288 ensures article completes
- ✅ Prompt emphasizes 8-12 citations + References section
- ⏳ No automatic retry if requirements not met

**Recommendation:**
Add post-refinement validation in `chunked_content.py`:

```python
async def _validate_and_retry_refinement(self, article, min_citations=8, min_words=3500):
    """
    Validate article meets requirements, retry if needed

    Returns:
        (article, retry_count)
    """
    content = article["content"]

    # Count citations and words
    citations = len(set(re.findall(r'\[(\d+)\]', content)))
    words = len(content.split())
    has_references = bool(re.search(r'##\s*References', content, re.IGNORECASE))

    if citations < min_citations or words < min_words or not has_references:
        logger.warning(
            "chunked_content.validation_failed",
            citations=citations,
            words=words,
            has_references=has_references
        )
        # Retry with targeted prompt
        return await self._targeted_refinement(article, citations, words, has_references)

    return article, 0
```

**Benefits:**
- Guarantees quality standards
- Reduces editor rejection rate
- Automatic recovery from weak output

**Effort:** 2-3 hours
**Priority:** HIGH (do this week)

---

### 3. ⏳ MEDIUM PRIORITY - Leverage Template Guidance in Chunks

**Codex Quote:**
> "Feed that into chunk prompts and the Sonnet refinement path—e.g., swap in archetype-specific chunk structures, module lists, and target word counts so a 'comparison matrix' article gets different chunk instructions than a 'skyscraper'."

**Current State:**
- ✅ Template Intelligence detects archetype (skyscraper, comparison, etc.)
- ⏳ Archetype not used in chunk prompts (generic structure only)

**Recommendation:**
Create archetype-specific chunk templates:

```python
ARCHETYPE_CHUNK_TEMPLATES = {
    "skyscraper": {
        "chunk_1": "Comprehensive overview with market context...",
        "chunk_2": "Deep dive into 8-12 key modules...",
        "chunk_3": "Case studies + FAQ (20+ Q&A pairs)...",
        "target_words": 3000,
        "target_modules": 12
    },
    "comparison": {
        "chunk_1": "Feature matrix + decision criteria...",
        "chunk_2": "Side-by-side analysis (5-8 options)...",
        "chunk_3": "Pros/cons + recommendations...",
        "target_words": 2500,
        "target_modules": 8
    },
    "deep_dive": {
        "chunk_1": "Expert-level foundation...",
        "chunk_2": "Technical implementation details...",
        "chunk_3": "Advanced strategies + pitfalls...",
        "target_words": 4000,
        "target_modules": 6
    }
}
```

**Benefits:**
- Archetype-specific structure (not generic)
- Better SERP competitiveness
- Appropriate depth per archetype

**Effort:** 4-6 hours
**Priority:** MEDIUM (after validation guarantees)

---

### 4. ⏳ MEDIUM PRIORITY - Cache SERP/Competitor Data

**Codex Quote:**
> "Store successful SERP/competitor payloads in the new template intelligence tables and let TemplateDetector.run() fall back to cached competitor detail instead of failing back to defaults."

**Current State:**
- ⏳ LinkUp/Firecrawl throw 429s in logs
- ⏳ TemplateDetector falls back to generic defaults

**Recommendation:**
Add caching layer in `template_detector.py`:

```python
async def _get_serp_with_fallback(self, keyword):
    """
    Try SERP APIs with caching fallback

    Priority:
    1. Fresh SERP data (DataForSEO/Serper)
    2. Cached SERP data (< 7 days old)
    3. Generic default
    """
    # Check cache first
    cached = await self._get_cached_serp(keyword)
    if cached and cached['age_days'] < 7:
        logger.info("template_detector.using_cached_serp", age=cached['age_days'])
        return cached['data']

    # Try live APIs
    try:
        serp_data = await self._fetch_live_serp(keyword)
        await self._cache_serp(keyword, serp_data)
        return serp_data
    except Exception as e:
        if cached:
            logger.warning("template_detector.stale_cache_fallback", error=str(e))
            return cached['data']
        else:
            logger.warning("template_detector.no_serp_data", error=str(e))
            return None
```

**Benefits:**
- Reduces API failures
- Faster template detection (cached)
- Better chunk prompts (competitive intel)

**Effort:** 3-4 hours
**Priority:** MEDIUM

---

### 5. ⏳ MEDIUM PRIORITY - Add Integration Tests

**Codex Quote:**
> "Consider a dedicated integration test that runs the chunked path against a test topic and asserts basic outcomes (e.g., citations ≥ 8, word count ≥ 3,500, References section present)."

**Recommendation:**
Create `backend/tests/test_chunked_content_integration.py`:

```python
import pytest
from app.agents.chunked_content import ChunkedContentAgent

@pytest.mark.integration
@pytest.mark.asyncio
async def test_chunked_content_quality_guarantees():
    """
    Integration test: Verify chunked content meets quality standards
    """
    agent = ChunkedContentAgent()

    # Test topic
    research = {"content": "Test research data about Portugal visa..."}
    topic = "Portugal Digital Nomad Visa 2025"

    # Generate article
    result = await agent.generate(research, "relocation", topic)
    article = result["article"]
    content = article["content"]

    # Assertions
    assert len(content.split()) >= 3500, "Article must be 3500+ words"

    citations = len(set(re.findall(r'\[(\d+)\]', content)))
    assert citations >= 8, f"Article must have 8+ citations, found {citations}"

    assert "## References" in content, "Article must have References section"

    # Verify References section has actual citations
    refs_section = content.split("## References")[1]
    ref_lines = [l for l in refs_section.split('\n') if l.strip().startswith('[')]
    assert len(ref_lines) >= 8, f"References section must list 8+ sources, found {len(ref_lines)}"
```

**Run tests:**
```bash
pytest backend/tests/test_chunked_content_integration.py -v
```

**Benefits:**
- Catches regressions early
- Documents quality expectations
- CI/CD integration ready

**Effort:** 2-3 hours
**Priority:** MEDIUM

---

### 6. ⏳ LOW PRIORITY - UX Niceties

**Codex Suggestions:**

1. **Expose metrics via `/api/jobs/{id}`**
   ```python
   # Add to job_status payload
   {
       "status": "completed",
       "metrics": {
           "word_count": 5344,
           "citations": 9,
           "cost": 0.75,
           "generation_method": "chunked",
           "chunk_words": [504, 418, 371],
           "refinement_expansion": "310%"
       }
   }
   ```

2. **Persist chunk debug files**
   - Save chunks to database or S3
   - Allow editors to see source chunks
   - Trace which sections came from which chunks

3. **Regeneration knob**
   - Add `/api/articles/{id}/regenerate` endpoint
   - Rerun Sonnet with variance prompt
   - Useful when editor flags low citations

**Effort:** 6-8 hours total
**Priority:** LOW (polish after core guarantees)

---

## 📊 Implementation Roadmap

### Week 1 (This Week)
- ✅ Rate limiting fix (DONE - Commit `3bce9f2`)
- ⏳ Citation/word-count validation + retry
- ⏳ Integration tests

### Week 2
- Archetype-specific chunk templates
- SERP caching layer
- Metrics API exposure

### Week 3+
- UX niceties (regeneration, chunk tracing)
- Performance optimization
- Cost monitoring dashboard

---

## 🎯 Success Metrics

**Before (Lucky Run):**
- 1 successful test article
- No guarantees on quality
- Manual verification required

**After (Repeatable Factory):**
- 95%+ articles meet 3500+ words
- 95%+ articles have 8+ citations + References
- Automatic retry recovers 80% of weak articles
- Integration tests prevent regressions

---

## 📝 Notes

**Codex Bottom Line:**
> "The hybrid Gemini → Sonnet pipeline is doing what you hoped: large, high-authority drafts at a fraction of the Sonnet-only cost. The next improvements are about making those wins automatic—fall back gracefully when Gemini truncates, formally enforce the citation/word-count bar, and fold the template intelligence signals into the chunk prompts so every piece feels bespoke rather than 'lucky'."

**Current Status:** Proof of concept validated ✅
**Next Phase:** Make it repeatable (validation + tests)
**Timeline:** 2-3 weeks to production-ready

---

**Last Updated:** October 10, 2025
**Reviewer:** Claude Codex
**Next Review:** After validation guarantees implemented
