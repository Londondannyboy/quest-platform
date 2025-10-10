# Quest Platform Peer Review Request - October 10, 2025

**Status:** 🔴 **CRITICAL ISSUES BLOCKING PRODUCTION**
**Focus:** References Section Missing + No Hyperlinks in Citations
**Last Commit:** `86931b5` - "refactor: Use Gemini 2.5 Pro everywhere"

---

## 🎯 Review Request Summary

We've implemented a chunked content generation system (Gemini 2.5 Pro → Sonnet 4.5) that **should** produce 3500+ word articles with 15-25 citations and a complete References section with hyperlinks.

**THE PROBLEM:** Articles are generating, but critical quality requirements are failing.

---

## 🔴 Critical Issues Found (Malta Article Test)

### Test Article: "Malta Gaming License 2025: Complete Cost Breakdown and Application Guide"
**Generation Time:** ~7 minutes
**Cost:** $0.45
**Quality Score:** 45/100 ❌
**Status:** REJECTED

### Issue #1: References Section Missing ❌
```
Expected: ## References section at end with 15-25 hyperlinked sources
Actual: Article cuts off mid-sentence, no References section
```

**Evidence:**
- Article ends at: "For gaming companies, the combination of gaming tax on Malta-"
- Word count: 8,127 words (but incomplete)
- Citations present: 53 bracket citations [1], [2], [3]
- **References section: NONE**

**Root Cause Hypothesis:**
- Sonnet max_tokens=16384 (maximum allowed)
- Article might be hitting token limit before References section
- OR Sonnet is ignoring the prompt requirement

### Issue #2: No Hyperlinks in Citations ❌
```
Expected: References section with [1] [Title](https://url.com) format
Actual: In-text citations are bare brackets [1], [2] with no URLs linked anywhere
```

**Evidence:**
```bash
# From check_article.py output:
Has References section: False
Total '[' brackets (approx citations): 53
Hyperlink count: 0  # ← CRITICAL: Zero hyperlinks in entire 8,127-word article
```

**What We're Doing:**
1. ✅ Providing 25 validated external URLs to Sonnet in link_context
2. ✅ Explicit prompt instructions to create References section with hyperlinks
3. ✅ Example format in prompt: `[1] [Source Title](https://url.com)`

**What's Happening:**
- Sonnet adds [1], [2], [3] citations throughout article ✅
- Sonnet NEVER creates References section ❌
- Sonnet NEVER adds any hyperlinks anywhere ❌

---

## 📊 Architecture & Code Context

### Current Chunked Content Flow

```
1. ResearchAgent → Gather intelligence + validate external URLs
   ↓
2. LinkValidator → Prepare link context with 25 URLs
   ↓
3. ChunkedContentAgent:
   a. Gemini 2.5 Pro: Generate 3 parallel chunks (~1,500 words each)
   b. Gemini 2.5 Pro: Weave chunks together (smooth transitions)
   c. Sonnet 4.5: Refine + add citations + SHOULD add References section
   ↓
4. EditorAgent → Score quality (needs References section for high score)
```

### The Critical Prompt (Lines 738-820 in chunked_content.py)

```python
def _build_refinement_prompt(...) -> str:
    # ...
    link_instructions = f"""
VALIDATED EXTERNAL URLS (MUST use in References section):
{external_links}  # 25 numbered URLs provided

**CRITICAL INSTRUCTIONS FOR LINKS:**
1. **In-text citations**: Use simple brackets like [1], [2], [3] ✅ WORKING
2. **References section**: MUST create actual HYPERLINKS like this:

   ## References

   [1] [Source Title](https://actual-url.com/page)
   [2] [Another Source](https://example.gov/source)
   [3] [Research Paper](https://academic.edu/paper)

3. **Internal links**: Weave 3-5 internal links into article body
4. **NEVER use bare URLs** - always format as markdown links: [Text](URL)
"""

    return f"""... YOUR TASK: ...

**THE #1 CRITICAL REQUIREMENT - REFERENCES SECTION WITH HYPERLINKS:**
- EVERY article MUST end with ## References as the FINAL section
- This is the MOST IMPORTANT part of the article
- The ## References section is NOT OPTIONAL
- Format EXACTLY as shown below using MARKDOWN HYPERLINKS:

## References

[1] [Government Source Title](https://example.gov/source1)
[2] [Research Paper Title](https://academic.edu/source2)
...
[20] [Expert Blog Title](https://expert.com/source20)

**CRITICAL FORMAT REQUIREMENTS:**
- Each reference MUST be a clickable markdown link: [Title](URL)
- Use the actual URLs provided in the VALIDATED EXTERNAL URLS section above
- Match citation numbers [1], [2] in article to reference numbers
- Articles without a complete References section will AUTOMATICALLY FAIL
- NEVER truncate or skip the References section
- Reserve ~1500 tokens minimum for the References section
"""
```

**QUESTION FOR REVIEWERS:** Why is Sonnet ignoring these explicit requirements?

---

## 🔧 Recent Fixes Applied

### Fix #1: Gemini Model Names ✅
**Problem:** Using non-existent `gemini-2.5-flash` and `gemini-2.5-flash-002`
**Solution:** Switched to `gemini-2.5-pro` everywhere (complexity analysis, weaving, chunks)
**Commits:** `384428b`, `86931b5`
**Status:** FIXED

**Rationale:**
- Gemini 2.5 series Flash models don't exist
- Simplified architecture: One model instead of two
- Better reliability, marginal cost increase (~$0.01/article)

---

## 🎯 What We Need From Peer Review

### Primary Questions

**1. Token Limit Issue?**
- Is 16,384 tokens insufficient for 8,000-word article + References section?
- Should we split into multiple Sonnet calls (content → references separately)?
- Current approach: Everything in one `messages.create()` call

**2. Prompt Effectiveness?**
- Are we being clear enough about References section requirement?
- Should we use different formatting/emphasis?
- Current approach: ALL CAPS, bold, repetition, explicit examples

**3. Markdown Hyperlink Format?**
- Is `[Title](URL)` the correct format for Sonnet?
- Should we use different syntax?
- Current approach: Standard markdown link syntax

**4. Alternative Architectures?**
- Should we POST-PROCESS article to add References section?
- Should we use a separate agent call just for References?
- Should we use JSON schema to enforce structure?

### Secondary Questions

**5. Quality Threshold**
- Current: Reject articles without References section (score drops to 45/100)
- Should we auto-retry with stronger prompt if References missing?

**6. Cost vs Quality Trade-off**
- Is chunked Gemini + Sonnet the right approach?
- Should we just use Sonnet for everything (simpler, more expensive)?

---

## 📁 Key Files to Review

### Core Logic
1. **`backend/app/agents/chunked_content.py`** (lines 594-820)
   - `_build_refinement_prompt()` - Where References instructions live
   - `_refine_with_sonnet()` - The actual Sonnet API call

2. **`backend/app/agents/editor.py`** (lines 90-150)
   - Citation validation logic
   - Why it's failing (no References section detected)

3. **`backend/app/core/link_validator.py`** (lines 50-120)
   - How we prepare the 25 external URLs for Sonnet
   - URL validation process

### Testing Evidence
4. **`backend/check_article.py`** - Quick script showing the problem
5. **Database:** Malta article (UUID: `b916047b-5730-4515-8b1b-71e0f90ffed4`)

---

## 🧪 How to Reproduce

```bash
# 1. Check Malta article in database
cd ~/quest-platform/backend
python3 check_article.py

# Expected output:
# Has References section: False  ← PROBLEM
# Hyperlink count: 0              ← PROBLEM
# Total citations: 53             ← GOOD

# 2. Generate new test article
cd ~/quest-platform/backend
python3 generate_article.py \
  --topic "Test Article: Portugal D7 Visa Requirements 2025" \
  --site relocation

# 3. Check for References section
# Should end with:
## References

[1] [Source 1 Title](https://url1.com)
[2] [Source 2 Title](https://url2.com)
...
```

---

## 📊 Expected vs Actual Results

### Expected High-Quality Article (75+ score)
✅ 3,500+ words
✅ 15-25 in-text citations [1], [2], [3]
✅ ## References section at end
✅ All references as hyperlinks: `[Title](URL)`
✅ 3-5 internal links in body

### Actual Malta Article (45 score)
✅ 8,127 words (excellent!)
✅ 53 in-text citations (excellent!)
❌ NO References section
❌ ZERO hyperlinks anywhere
❌ Article cuts off mid-sentence

---

## 💡 Proposed Solutions (Need Validation)

### Option A: Two-Stage Sonnet Calls
```python
# Stage 1: Generate main content (no References yet)
article_content = await sonnet.generate(...)

# Stage 2: Generate References section separately
references = await sonnet.generate(
    prompt=f"Create References section for these citations: {citations}",
    urls=link_context
)

# Combine
final_article = article_content + "\n\n" + references
```

**Pros:** Each stage has full token budget
**Cons:** 2x Sonnet cost (~$0.40 → $0.80/article)

### Option B: Stronger Prompt Enforcement
```python
# Add to system prompt:
"YOU WILL BE PENALIZED if the article does not end with ## References"
"CRITICAL: The LAST section MUST be ## References with hyperlinks"
"DO NOT END the article until you have written the References section"
```

**Pros:** No architecture change
**Cons:** Might not work if it's a token limit issue

### Option C: Post-Processing References
```python
# After Sonnet generates article:
if "## References" not in article:
    # Extract citation numbers [1], [2], [3]
    citations = extract_citations(article)

    # Build References section programmatically
    references_section = build_references(citations, link_context)

    # Append to article
    article += "\n\n" + references_section
```

**Pros:** Guaranteed References section
**Cons:** Less natural, might not match article context

---

## 🎯 Success Criteria for Fix

### Validation Test
Generate 3 articles on different topics and verify:

1. ✅ Each article ≥3,500 words
2. ✅ Each article has 15-25 in-text citations [1], [2], [3]
3. ✅ Each article ends with ## References section
4. ✅ Each reference is a markdown hyperlink: `[Title](URL)`
5. ✅ Reference numbers match in-text citation numbers
6. ✅ Quality score ≥75/100
7. ✅ No articles cut off mid-sentence

### Performance Targets
- **Cost:** ≤$1.00/article
- **Time:** ≤3 minutes/article
- **Success rate:** ≥95% (19/20 articles pass validation)

---

## 📝 Additional Context

### Why This Matters (YMYL Content)
- Our niche: Visa/immigration/tax advice = YMYL (Your Money Your Life)
- Google requires HIGH citation density for YMYL
- E-E-A-T signals: Citations + References = Expertise + Authority
- Without References section: Quality score tanks to 45/100
- Cannot publish articles scoring <75/100

### Current Blocking State
- **Articles generated:** 16 (only 3 published)
- **Reason for low publish rate:** No References sections
- **Impact:** $7.20 wasted on rejected articles this week
- **Opportunity cost:** 16 indexed Google URLs returning 404

---

## 🔗 Related Documentation

- **QUEST_ARCHITECTURE.md** - v2.6 chunked content system
- **QUEST_GENERATION.md** - How to use generate_article.py
- **QUEST_CONTENT_PUBLISHING_GUIDELINES.md** - Quality gates (15+ citations required)
- **TAILRIDE_CASE_STUDY_ANALYSIS.md** - Why quality matters (avoid Google penalty)

---

## 🙏 Review Request

**Timeline Needed:** This week (blocking production scale-up)
**Preferred Review Depth:** Deep dive on prompt engineering + Sonnet behavior
**Deliverable:** Actionable recommendations for fixing References section issue

**Thank you for your expertise!** 🚀

---

**Last Updated:** October 10, 2025
**Commits:** `384428b`, `86931b5`
**Next Session:** Awaiting peer review feedback to implement fix
