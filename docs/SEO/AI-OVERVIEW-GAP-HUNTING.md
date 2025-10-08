# AI Overview Gap Hunting Strategy

**Version:** 2.3.2
**Date:** October 8, 2025
**Source:** Julian Goldie AI SEO Insights
**Status:** Monthly Process

---

## 🎯 Overview

**AI Overview Gap Hunting** = Finding queries where AI systems give incomplete answers, then creating content that fills those gaps.

**Julian Goldie's Key Insight:**
> "Most AI overview answers are incomplete. They pull brief summaries but miss the deep stuff. That's your opportunity."

**Why This Works:**
- AI overviews change **daily**
- Low competition (most sites target traditional keywords)
- Faster rankings (AI systems actively looking for better sources)
- Higher conversion (matches exact user intent)

**Goal:** Identify 20 AI gap opportunities per month, publish within 24-48 hours

---

## 📊 The Opportunity

### **Traditional SEO vs AI Overview SEO**

**Traditional SEO:**
```
Target: High-volume keywords
Competition: Extremely high
Timeline: 3-6 months to rank
Success Rate: 5-10%
```

**AI Overview SEO:**
```
Target: Queries with incomplete AI answers
Competition: Low (most don't look for these)
Timeline: 24-48 hours to get cited
Success Rate: 40-60%
```

**Example:**

**Query:** "portugal digital nomad visa application timeline"

**Current AI Overview (ChatGPT):**
```
"The application typically takes 2-3 months. You'll need proof of income,
health insurance, and a clean criminal record."
```

**What's Missing:**
- Step-by-step timeline breakdown
- Document preparation time
- Appointment wait times
- Processing time by consulate
- Common delays and how to avoid them
- Expedited processing options

**Our Opportunity:**
Create "Portugal Digital Nomad Visa: Complete Application Timeline Guide"
- Fill all gaps
- Become THE authoritative source
- Get cited by AI systems

---

## 🛠️ Monthly Workflow

### **Step 1: Identify 20 Test Queries (Week 1)**

**For Each Site:**

**Relocation.quest (20 queries):**
```
1. "portugal digital nomad visa application timeline"
2. "best cities for digital nomads 2025"
3. "digital nomad visa requirements comparison"
4. "expat tax guide for digital nomads"
5. "cost of living comparison digital nomad cities"
6. "how to get digital nomad visa quickly"
7. "portugal vs spain digital nomad visa"
8. "digital nomad visa income requirements"
9. "best countries for remote workers"
10. "digital nomad healthcare options"
... (continue to 20)
```

**Placement.quest (20 queries):**
```
1. "remote work interview questions"
2. "software engineer resume for remote jobs"
3. "how to negotiate remote work salary"
4. "best remote job boards 2025"
5. "remote work job scams to avoid"
... (continue to 20)
```

**Rainmaker.quest (20 queries):**
```
1. "how to start a saas business with no code"
2. "bootstrapping vs vc funding comparison"
3. "best marketing strategies for startups"
4. "how to validate startup ideas quickly"
5. "startup funding options 2025"
... (continue to 20)
```

**Where to Find Queries:**
- Data for SEO keyword research
- Google Search Console (queries with impressions but low clicks)
- "People Also Ask" boxes
- Reddit/Quora questions in your niche
- ChatGPT: "What are 20 common questions about [topic]?"

---

### **Step 2: Test Each Query in AI Systems (Week 1-2)**

**Test Matrix:**

| Query | ChatGPT Answer | Perplexity Answer | Claude Answer | What's Missing? | Opportunity Score (1-10) |
|-------|----------------|-------------------|---------------|-----------------|--------------------------|
| portugal digital nomad visa timeline | Brief, generic | Mentions 2-3 months | Similar to ChatGPT | Timeline breakdown, document prep time, delays | 9/10 |
| best cities for digital nomads 2025 | Lists 5 cities | Lists 10 with data | Lists 7 cities | Cost comparison, visa info, internet speeds | 7/10 |

**Testing Process:**
```python
# Manual testing (no tool needed)
queries = [
    "portugal digital nomad visa application timeline",
    "best cities for digital nomads 2025",
    # ... 20 queries total
]

for query in queries:
    # Test in ChatGPT
    chatgpt_response = test_in_chatgpt(query)

    # Test in Perplexity
    perplexity_response = test_in_perplexity(query)

    # Test in Claude
    claude_response = test_in_claude(query)

    # Document what's missing
    gaps = identify_gaps(chatgpt_response, perplexity_response, claude_response)

    # Score opportunity (1-10)
    opportunity_score = calculate_opportunity(gaps, competition, search_volume)
```

**Scoring Criteria:**
```
Opportunity Score = (Gap Size × 0.4) + (Low Competition × 0.3) + (Search Volume × 0.3)

Where:
- Gap Size: How much is missing? (1-10, 10 = huge gaps)
- Low Competition: How many sites cover this well? (10 = none, 1 = many)
- Search Volume: Monthly searches (normalize to 1-10)

Target: Score > 7 = High priority
```

---

### **Step 3: Prioritize Top 10 Opportunities (Week 2)**

**Sort by Opportunity Score:**

| Rank | Query | Score | Why High Priority |
|------|-------|-------|-------------------|
| 1 | portugal digital nomad visa timeline | 9/10 | Huge gaps, low competition, 500 searches/mo |
| 2 | remote work interview red flags | 8.5/10 | AI gives generic advice, 800 searches/mo |
| 3 | startup funding comparison 2025 | 8/10 | Data outdated in AI, 400 searches/mo |

**Select Top 10:**
- Highest scores
- Mix of topics (don't all do visas)
- Spread across all 3 sites

---

### **Step 4: Create Gap-Filling Content (Week 2-3)**

**For Each Opportunity:**

**1. Research Using Enhanced ResearchAgent**
```python
# ResearchAgent now includes gap analysis
research = await research_agent.run(
    topic="Portugal Digital Nomad Visa: Complete Application Timeline"
)

# Returns:
# - Current AI overview
# - Sources used
# - Missing subtopics (the gaps!)
# - Common questions
# - Latest developments
# - Data & statistics
# - Expert perspectives
# - Opportunity areas
```

**2. Generate Content Filling ALL Gaps**
```python
# ContentAgent creates comprehensive article
article = await content_agent.run(
    research=research,
    target_site="relocation",
    topic="Portugal Digital Nomad Visa: Complete Application Timeline",
    content_type="standard"
)

# Output includes:
# - TL;DR (what AI overviews need)
# - Key Takeaways (quick scannable)
# - Comprehensive content (fills all gaps)
# - FAQs (common questions AI can't answer)
# - Sources cited (authority)
```

**3. Publish Within 24-48 Hours**
- No perfectionism
- Good enough is good enough
- Speed wins (AI overviews change daily)

---

### **Step 5: Track Citation Success (Week 4)**

**2 Weeks After Publishing:**

Test same queries again:

| Query | Before (AI Answer) | After (AI Answer) | Cited? | Citation Position |
|-------|-------------------|-------------------|--------|-------------------|
| portugal digital nomad visa timeline | Generic 2-3 months | "According to relocation.quest..." | ✅ YES | Position 2 |
| best cities digital nomads 2025 | Generic list | Still generic | ❌ NO | N/A |

**Success Metrics:**
- **Citation Rate:** % of articles cited by AI (Target: 40-60%)
- **Citation Position:** Average position when cited (Target: Top 3)
- **Citation Diversity:** How many AI systems cite us (Target: 2+)

**4 Weeks After Publishing:**
- Retest queries
- Check if citation rate improved
- Identify patterns (what works best?)

---

## 📋 Monthly Template

### **Month 1 (October 2025)**

**Week 1: Identify & Test**
- Monday-Tuesday: Generate 20 queries per site (60 total)
- Wednesday-Friday: Test all queries in ChatGPT, Perplexity, Claude
- Document gaps and score opportunities

**Week 2: Prioritize & Create**
- Monday: Select top 10 opportunities
- Tuesday-Friday: Create 10 articles (2-3 per day)
- Publish within 24-48 hours of creation

**Week 3: Continue Publishing**
- Monday-Wednesday: Finish remaining articles if needed
- Thursday-Friday: Monitor initial indexing

**Week 4: Track & Analyze**
- Monday-Wednesday: Test queries again (2 weeks post-publish)
- Thursday: Calculate citation rate
- Friday: Report results, identify patterns

**Results to Track:**
```markdown
## October 2025 Gap Hunting Results

**Queries Tested:** 60
**High-Priority Opportunities:** 10
**Articles Published:** 10
**Citation Rate (Week 2):** 20% (2/10 cited)
**Citation Rate (Week 4):** 40% (4/10 cited)

**Top Performers:**
1. "portugal digital nomad visa timeline" - Cited by ChatGPT (position 2) and Perplexity (position 1)
2. "remote work interview red flags" - Cited by Claude (position 3)

**Patterns:**
- Queries with "timeline", "comparison", "step-by-step" have highest citation rate
- Listicles cited less (AI prefers comprehensive guides)
- Articles with data/statistics cited more

**Next Month Adjustments:**
- Focus on "how-to" and "timeline" queries
- Add more data/statistics
- Create more FAQ-heavy content
```

---

## ✅ Best Practices

### **DO:**
- ✅ Test queries in multiple AI systems (not just one)
- ✅ Document specific gaps (what's missing)
- ✅ Publish within 24-48 hours (speed wins)
- ✅ Fill ALL gaps identified (comprehensive)
- ✅ Track citation rate monthly
- ✅ Adjust strategy based on results

### **DON'T:**
- ❌ Target high-competition keywords (traditional SEO)
- ❌ Wait for perfection (speed > perfection)
- ❌ Create shallow content (fill gaps completely)
- ❌ Test only in one AI system
- ❌ Ignore patterns in results
- ❌ Give up after one month (takes 2-3 months to see full results)

---

## 📊 Expected Results

**Month 1:**
- 10 articles published
- 10-20% citation rate
- Learning phase (identify what works)

**Month 2:**
- 10 more articles published
- 30-40% citation rate
- Patterns emerging

**Month 3:**
- 10 more articles published
- 50-60% citation rate
- Consistent results, refine strategy

**Month 6:**
- 60 articles published
- 60%+ citation rate
- Established authority in AI systems

---

## 🎯 Quick Start Checklist

**This Month (Week 1):**
- [ ] Generate 20 queries per site (use Data for SEO, GSC, Reddit)
- [ ] Test all 60 queries in ChatGPT, Perplexity, Claude
- [ ] Document gaps for each query
- [ ] Score opportunities (1-10)
- [ ] Select top 10 highest scores

**This Month (Week 2-3):**
- [ ] Use ResearchAgent (gap analysis prompt) for each topic
- [ ] Generate articles with ContentAgent
- [ ] Publish within 24-48 hours of creation
- [ ] Track publishing dates

**This Month (Week 4):**
- [ ] Retest all 10 queries (2 weeks post-publish)
- [ ] Document which were cited
- [ ] Calculate citation rate
- [ ] Identify patterns (what worked?)
- [ ] Plan next month's queries

---

## 📚 Related Documentation

- [LLM Optimization Guide](./LLM-OPTIMIZATION.md) - AI SEO strategy
- [Topic Domination](./TOPIC-DOMINATION.md) - Content volume strategy
- [Competitor Seeding](./COMPETITOR-SEEDING.md) - Comparison content

---

**Document Owner:** Content & SEO Team
**Last Review:** October 8, 2025
**Next Review:** November 8, 2025
**Status:** Active Monthly Process ✅

---

**Find the gaps. Fill the gaps. Get cited. Repeat monthly.** 🚀
