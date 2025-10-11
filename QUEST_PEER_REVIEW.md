# Quest Platform - Peer Review Guide

**Purpose:** Track milestones and guide external reviews
**Updated:** October 11, 2025
**Status:** 🎉 **MILESTONE ACHIEVED** - Citation Format + AstroWind Deployment Complete

---

## 🎉 MILESTONE: Citation Hyperlinks + AstroWind Integration (Oct 11, 2025)

**Achievement:** First complete article deployed with inline hyperlink citations!

**Live Example:** https://relocation.quest/iceland-digital-nomad-visa-2025

**What Works:**
- ✅ 5,164 words (full article, not summary)
- ✅ 77 inline hyperlinks using `[anchor text](url)` format
- ✅ 4 Cloudinary images rendering correctly
- ✅ "Further Reading & Sources" section at end
- ✅ Mobile-friendly 1-click citations (no numbered references)
- ✅ AstroWind theme rendering perfectly
- ✅ Vercel deployment successful

**Technical Fixes:**
1. Backend: Updated Sonnet refinement prompts for inline hyperlinks
2. Backend: Changed References → "Further Reading & Sources" with bullets
3. Frontend: Fixed YAML frontmatter (quoted excerpt, simplified tags)
4. Frontend: Vercel build successful

**Status:** ✅ RESOLVED - Production workflow validated end-to-end

---

## 🔍 PREVIOUS ISSUE (Now Resolved): References Section Not Appearing

### Problem Summary

Articles are generating successfully but **failing quality validation** due to missing References sections and zero hyperlinks.

**Test Article:** "Malta Gaming License 2025: Complete Cost Breakdown and Application Guide"
- **Cost:** $0.45
- **Generation Time:** ~7 minutes
- **Quality Score:** 45/100 ❌ (target: 75+)
- **Status:** REJECTED

### What's Wrong

```bash
# Evidence from Malta article:
Has References section: False  ❌
Total citations: 53            ✅ (in-text [1], [2], [3])
Hyperlink count: 0             ❌ (zero clickable links)
Article cuts off: Mid-sentence ❌
```

**Expected Output:**
```markdown
## References

[1] [Government Source](https://example.gov/source1)
[2] [Research Paper](https://academic.edu/source2)
[3] [Industry Report](https://industry.com/source3)
...
[20] [Expert Blog](https://expert.com/source20)
```

**Actual Output:**
- Article ends at: "For gaming companies, the combination of gaming tax on Malta-"
- No References section
- Zero hyperlinks in 8,127-word article

---

## 🔍 What We've Tried

### 1. Prompt Engineering ✅ Implemented
**Location:** `backend/app/agents/chunked_content.py` lines 738-820

**Current Approach:**
- ✅ Explicit instructions: "EVERY article MUST end with ## References"
- ✅ Example format provided: `[1] [Title](URL)`
- ✅ 25 validated external URLs provided in link_context
- ✅ ALL CAPS emphasis, bold, repetition

**Result:** Sonnet still ignores it ❌

### 2. Token Limit Investigation
**Current:** `max_tokens=16384` (maximum for Sonnet)
**Hypothesis:** Article reaching token limit before References section

**Evidence:**
- Malta article: 8,127 words
- Article cuts off mid-sentence
- References section would need ~1,500 tokens minimum

**Question:** Is 16,384 insufficient for 8K-word article + References?

### 3. Link Validation System ✅ Working
**Location:** `backend/app/core/link_validator.py`

**Confirmed Working:**
- ✅ External URLs validated with httpx
- ✅ 25 valid URLs provided to Sonnet
- ✅ URLs in proper format: `[1] https://example.com/source1`

**Result:** Sonnet receives the URLs but doesn't use them ❌

---

## 🧪 Reproduction Steps

```bash
# 1. Check Malta article
cd ~/quest-platform/backend
python3 check_article.py

# Expected output shows the problem:
# Has References section: False
# Hyperlink count: 0

# 2. Generate new test article
python3 generate_article.py \
  --topic "Test: Portugal D7 Visa Guide 2025" \
  --site relocation

# 3. Check if References section appears
# Article should end with hyperlinked sources
```

---

## 💡 Proposed Solutions (Need Validation)

### Option A: Two-Stage Sonnet Calls
```python
# Stage 1: Generate main content
article_content = await sonnet.generate(main_content_prompt)

# Stage 2: Generate References separately
references = await sonnet.generate(
    prompt=f"Create ## References section for citations: {extract_citations(article_content)}",
    urls=link_context
)

# Combine
final_article = article_content + "\n\n" + references
```

**Pros:** Each stage has full token budget
**Cons:** 2x Sonnet cost (~$0.40 → $0.80/article)

### Option B: Post-Processing References
```python
# After Sonnet generates article:
if "## References" not in article:
    citations = extract_citations(article)  # [1], [2], [3]
    references_section = build_references_section(citations, link_context)
    article += "\n\n" + references_section
```

**Pros:** Guaranteed References section, no extra AI cost
**Cons:** Less natural, might not match article tone

### Option C: Stronger Prompt (Last Resort)
```python
# Add to system prompt:
"YOU WILL BE REJECTED if article doesn't end with ## References"
"The LAST thing you write MUST be the References section"
"Reserve 25% of your token budget for References"
```

**Pros:** No architecture change
**Cons:** Might not work if it's a token limit issue

---

## 📊 Key Files to Review

### Core Logic
1. **`backend/app/agents/chunked_content.py`** (lines 594-820)
   - `_build_refinement_prompt()` - References instructions
   - `_refine_with_sonnet()` - Sonnet API call

2. **`backend/app/agents/editor.py`** (lines 90-150)
   - Citation validation logic
   - Why quality score drops to 45/100

3. **`backend/app/core/link_validator.py`** (lines 50-120)
   - URL preparation for Sonnet
   - Validation process

### Testing
4. **`backend/check_article.py`** - Verifies the problem
5. **Database:** Malta article UUID `b916047b-5730-4515-8b1b-71e0f90ffed4`

---

## 🎯 What We Need From Review

### Primary Questions

**1. Is this a token limit issue?**
- Should we split content + references into 2 calls?
- Is 16,384 tokens insufficient for 8K words + References?

**2. Is our prompt clear enough?**
- Are we emphasizing References section correctly?
- Should we use different wording/format?

**3. Should we post-process instead?**
- Is programmatic References section generation acceptable?
- Would it hurt article quality/coherence?

### Success Criteria

A fix is validated when:
1. ✅ 3/3 test articles have ## References sections
2. ✅ All references are hyperlinks: `[Title](URL)`
3. ✅ Reference numbers match in-text citations
4. ✅ Quality score ≥75/100
5. ✅ No articles cut off mid-sentence
6. ✅ Cost ≤$1.00/article

---

## 📈 Why This Matters

### YMYL Content Requirements
- **Our niche:** Visa/immigration/tax = YMYL (Your Money Your Life)
- **Google requirement:** HIGH citation density for YMYL
- **E-E-A-T signals:** Citations + References = Expertise + Authority
- **Without References:** Quality score tanks to 45/100
- **Threshold:** Cannot publish articles <75/100

### Current Impact
- **Articles generated:** 16 total
- **Articles published:** 3 (only 18% success rate)
- **Wasted cost:** $7.20 on rejected articles this week
- **Opportunity cost:** 16 indexed Google URLs returning 404

---

## 🔗 Related Documentation

- **QUEST_ARCHITECTURE.md** - v2.6 chunked content system
- **QUEST_GENERATION.md** - Article generation script
- **QUEST_CONTENT_PUBLISHING_GUIDELINES.md** - Quality gates (15+ citations required)
- **TAILRIDE_CASE_STUDY_ANALYSIS.md** - Google penalty case study

---

## 🚀 Recent Fixes (Already Applied)

### Fixed: Gemini Model Names ✅
- **Problem:** Using non-existent `gemini-2.5-flash`
- **Solution:** Switched to `gemini-2.5-pro` everywhere
- **Commits:** `384428b`, `86931b5`
- **Status:** FIXED ✅

---

**Last Updated:** October 10, 2025
**Commits:** `384428b`, `86931b5`
**Awaiting:** Peer review feedback on References section issue

---

## 📝 Review Template

**Copy this for your review:**

```markdown
# Quest Peer Review - References Section Fix

**Reviewer:** [Name/Model]
**Date:** [Date]

## Recommended Solution
[A/B/C or new option]

## Reasoning
[Why this approach will work]

## Implementation Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Risks
[Potential issues with this approach]

## Expected Outcome
[What should happen after fix]
```

---

**Need Help With:** References section not appearing despite explicit prompts
**Timeline:** This week (blocking production scale-up)
**Thank you!** 🙏
