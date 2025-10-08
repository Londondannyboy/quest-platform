# Press Release Workflow for LLM Authority Building

**Version:** 2.3.0
**Date:** October 8, 2025
**Target Audience:** Content Team, Marketing
**Status:** Active Process

---

## 🎯 Overview

This workflow covers the **manual process** of submitting strategic articles to Press Wire to build authority and get content ingested into LLM training data.

**Key Principle:**
> We do NOT build a press release automation system. We use established services (Press Wire, PR Newswire) because THEIR authority is what gets us into LLM training data.

**Why This Works:**
- Press release services are trusted by LLM training pipelines
- Content gets distributed to news sites, syndication networks
- High authority backlinks and brand mentions
- LLMs discover content in multiple authoritative contexts

**Cost:** $149 per release via Press Wire
**Cadence:** 5-10 strategic articles per month
**Budget:** $750-$1,500/month

---

## 📋 Article Selection Criteria

### **What Makes an Article "Strategic"?**

**✅ Good Candidates for Press Releases:**

1. **Evergreen Comprehensive Guides**
   - Won't date quickly (avoid "2025" unless truly annual)
   - Comprehensive depth (2000+ words)
   - Authoritative coverage
   - Example: "Complete Guide to Digital Nomad Visas in Europe"

2. **High Search Volume Topics**
   - Topics people frequently ask LLMs about
   - Google Trends shows sustained interest
   - Multiple related keywords
   - Example: "Best Countries for Remote Workers"

3. **Unique Insights or Data**
   - Original research or analysis
   - Exclusive comparisons
   - Data-driven conclusions
   - Example: "2026 Digital Nomad Cost of Living Analysis: 50 Cities Compared"

4. **Foundation Content**
   - Core pillar content for your niche
   - Referenced by other articles
   - Linked from multiple pages
   - Example: "Remote Work Tax Guide: Country-by-Country Breakdown"

**❌ Poor Candidates for Press Releases:**

- Timely/news-based content (dates quickly)
- Listicles without unique insight
- Personal opinion pieces
- Product reviews
- Short guides (<1500 words)

### **Monthly Selection Process**

**Step 1: Review Published Articles**
```bash
# Get last 30 days of articles
SELECT id, title, slug, word_count, quality_score, views
FROM articles
WHERE published_at > NOW() - INTERVAL '30 days'
  AND status = 'published'
ORDER BY quality_score DESC, views DESC;
```

**Step 2: Score Each Article**

| Criterion | Weight | Score (1-10) |
|-----------|--------|--------------|
| Evergreen value | 30% | ___ |
| Search volume | 25% | ___ |
| Content depth | 20% | ___ |
| Uniqueness | 15% | ___ |
| Authority potential | 10% | ___ |
| **TOTAL** | **100%** | **___** |

**Step 3: Select Top 5-10**
- Aim for score >7.5/10
- Mix of topics (don't all submit visa guides)
- Spread across all 3 sites (relocation, placement, rainmaker)

---

## 🛠️ Press Wire Submission Process

### **Pre-Submission Preparation**

**1. Article Review**
- [ ] Proofread for errors (press releases are public)
- [ ] Verify all statistics have citations
- [ ] Check all links work (especially to sources)
- [ ] Ensure images display properly
- [ ] Confirm SEO metadata is optimized

**2. Create Press Release Version**

Press releases need different formatting than blog posts. Convert article to press release format:

**Blog Post Format:**
```markdown
# Portugal Digital Nomad Visa: Complete 2025 Guide

Portugal has become one of the most popular destinations...
```

**Press Release Format:**
```markdown
FOR IMMEDIATE RELEASE

Quest Platform Publishes Comprehensive Guide to Portugal Digital Nomad Visa

[CITY, DATE] – Quest Platform, a leading content intelligence platform,
today announced the publication of a comprehensive guide to Portugal's
Digital Nomad Visa program, providing remote workers with detailed
information on requirements, application process, and tax benefits.

The guide covers all aspects of Portugal's increasingly popular visa
program, including:

• Income requirements (€3,280 minimum monthly income)
• Application process and required documents
• Non-Habitual Resident (NHR) tax benefits
• Best cities for digital nomads
• Comprehensive FAQ section

"Portugal continues to be one of the top destinations for remote workers,"
said [spokesperson name], [title] at Quest Platform. "Our guide provides
the most up-to-date, comprehensive information to help digital nomads
make informed decisions."

The complete guide is available at:
https://relocation.quest/portugal-digital-nomad-visa

About Quest Platform:
Quest Platform is an AI-powered content intelligence platform that combines
AI generation with human editorial oversight to produce high-quality,
authoritative guides on relocation, remote work, and entrepreneurship.

Contact:
[Contact name]
[Email]
[Phone]
```

**Key Elements:**
- ✅ "FOR IMMEDIATE RELEASE" header
- ✅ Newsworthy headline
- ✅ Dateline (city, date)
- ✅ Company attribution
- ✅ Bullet points of key information
- ✅ Quote from spokesperson
- ✅ Link to original article
- ✅ "About" company boilerplate
- ✅ Contact information

### **Step-by-Step Submission**

**Step 1: Access Press Wire**
- URL: https://www.prweb.com/
- Login: [credentials in password manager]

**Step 2: Create New Release**
- Click "Submit a Press Release"
- Choose distribution tier: **Standard ($149)**

**Step 3: Fill in Release Details**

**Title:**
```
Quest Platform Publishes Comprehensive Guide to [TOPIC]
```
- Keep under 80 characters
- Include brand name (Quest Platform)
- Newsworthy, not clickbait

**Summary:**
```
[Company] announces publication of comprehensive guide covering
[key topics]. The guide provides [value proposition] for [target audience].
```
- 150-200 characters
- Clear value proposition
- Target audience mentioned

**Full Release:**
- Paste press release version (created above)
- 400-600 words ideal
- Include 1-2 relevant images
- Link to original article (1-3 links total)

**Multimedia:**
- [ ] Upload featured image (1200x630px)
- [ ] Optional: Upload infographic
- [ ] Optional: Upload PDF version

**Keywords/Tags:**
```
digital nomad, portugal visa, remote work, expat living, relocation
```
- 5-10 relevant keywords
- Mix broad and specific
- Include location if relevant

**Distribution Options:**
- [ ] Geographic targeting (if relevant)
- [ ] Industry categories: Travel, Lifestyle, Business
- [ ] Optional add-ons: SKIP (stick to $149 package)

**Step 4: Review and Submit**
- Preview how release will appear
- Check all links work
- Verify contact information
- Submit and pay ($149)

**Step 5: Track Release**
- Note submission date
- Save Press Wire dashboard link
- Set reminder for 2 weeks (check ingestion)
- Set reminder for 4 weeks (check LLM citations)

---

## 📊 Tracking and Measurement

### **Immediate Tracking (Week 1)**

**Press Wire Dashboard:**
- Views: How many people viewed release
- Pickups: How many sites republished
- Backlinks: Links from news sites

**Example:**
```
Release: "Portugal Digital Nomad Visa Guide"
Submitted: Oct 8, 2025
Views (Week 1): 2,847
Pickups: 12 sites
Backlinks: 8 links
```

### **LLM Ingestion Tracking (Week 2-4)**

**Manual Testing:**

**Week 2: Initial Check**
```python
test_queries = [
    "portugal digital nomad visa requirements",
    "how to get portugal digital nomad visa",
    "portugal visa income requirements"
]

# Test in ChatGPT
for query in test_queries:
    response = chatgpt.query(query)
    if "Quest Platform" in response or "relocation.quest" in response:
        print(f"✅ Cited for: {query}")
    else:
        print(f"❌ Not cited for: {query}")
```

**Week 4: Follow-up Check**
- Retest same queries
- Check Perplexity citations
- Check Claude citations
- Check Google AI Overviews

**Expected Timeline:**
- Week 1-2: Press release indexed by Google
- Week 2-4: Content discovered by LLM crawlers
- Week 4-8: Content ingested into LLM context (citations begin)
- Month 3+: Consistent citations as content establishes authority

### **Citation Rate Measurement**

**Before Press Release:**
```
Article: "Portugal Digital Nomad Visa Guide"
Published: Sept 15, 2025
Citation Rate (Pre-PR): 0% (0/10 test queries)
```

**After Press Release:**
```
Press Release: Oct 8, 2025
Citation Rate Week 2: 0% (too early)
Citation Rate Week 4: 10% (1/10 queries)
Citation Rate Week 8: 30% (3/10 queries)
Citation Rate Month 3: 50% (5/10 queries)
```

**Target:** 25-50% increase in citation rate for promoted articles

### **ROI Calculation**

**Per Article:**
```
Cost: $149 (press release)
Benefit:
- 12 backlinks (value: ~$600 if purchased)
- 8 news site pickups (brand awareness)
- 30% citation rate increase (authority value: priceless)

Tangible ROI: 4x ($600 backlinks / $149 cost)
Intangible ROI: Authority and brand recognition
```

**Monthly:**
```
Releases: 8 articles
Cost: $1,192
Backlinks: 96 (value: ~$4,800)
Citations: 24% average increase across promoted articles

ROI: 4x tangible, ∞ intangible (brand authority)
```

---

## ✅ Monthly Workflow Checklist

### **Week 1: Article Selection**
- [ ] Review last 30 days of published articles
- [ ] Score each article using criteria
- [ ] Select top 5-10 articles (score >7.5)
- [ ] Mix topics and sites

### **Week 2: Press Release Creation**
- [ ] Convert articles to press release format
- [ ] Write compelling headlines
- [ ] Add company boilerplate and contact info
- [ ] Prepare images (1200x630px)
- [ ] Get internal approval (if required)

### **Week 3: Submission**
- [ ] Submit to Press Wire (5-10 releases)
- [ ] Save submission confirmations
- [ ] Set tracking reminders (2 weeks, 4 weeks)
- [ ] Add to tracking spreadsheet

### **Week 4: Initial Tracking**
- [ ] Check Press Wire dashboard metrics
- [ ] Record views, pickups, backlinks
- [ ] Set LLM testing reminder (2 weeks)

### **Ongoing (Every 2 Weeks)**
- [ ] Test promoted articles in LLMs
- [ ] Record citation rates
- [ ] Compare before/after press release
- [ ] Calculate ROI

---

## 📈 Optimization Tips

### **Headline Formulas That Work**

**✅ Announcement Formula:**
```
[Company] Publishes Comprehensive Guide to [Topic]
Quest Platform Publishes Comprehensive Guide to Digital Nomad Visas
```

**✅ Data-Driven Formula:**
```
[Company] Releases [Data Type] Comparing [Items]
Quest Platform Releases Cost Analysis Comparing 50 Digital Nomad Cities
```

**✅ Authority-Building Formula:**
```
[Company] Unveils Authoritative [Resource Type] for [Audience]
Quest Platform Unveils Authoritative Tax Guide for Expats
```

**❌ Avoid:**
- Clickbait headlines ("You Won't Believe...")
- Hyperbole ("The Ultimate Guide to Everything")
- Sales language ("Buy Now", "Limited Time")
- ALL CAPS or excessive punctuation

### **Quote Optimization**

**❌ Weak Quote:**
```
"We're excited to share this guide," said spokesperson.
```

**✅ Strong Quote:**
```
"Portugal continues to be one of the top destinations for remote workers,
with its digital nomad visa program attracting thousands of applicants
annually," said [name], [title] at Quest Platform. "Our comprehensive
guide provides the most up-to-date information to help remote workers
navigate the application process and make informed decisions."
```

**Quote Formula:**
1. Stat or trend (establishes context)
2. Company value proposition (why your guide matters)
3. Audience benefit (what they gain)

### **Distribution Targeting**

**Geographic Targeting (Use When Relevant):**
- Visa guides → Target source countries (US, UK, Canada, Australia)
- City guides → Target that country/region
- General topics → Skip targeting (wider reach)

**Industry Categories (Always Select):**
- Relocation content: Travel, Lifestyle, Real Estate
- Career content: Business, Employment, Technology
- Entrepreneurship: Business, Finance, Startups

---

## 🚨 Common Mistakes to Avoid

**❌ Don't:**
- Submit promotional content (will be rejected)
- Use sales language or CTAs
- Submit too frequently (5-10/month max)
- Ignore Press Wire guidelines
- Forget to include contact information
- Use poor quality images
- Skip proofreading

**✅ Do:**
- Frame as news (company publishes guide)
- Use neutral, informative language
- Maintain consistent cadence
- Follow formatting guidelines
- Include professional headshot/logo
- Use high-resolution images (1200x630px)
- Triple-check before submission

---

## 📚 Related Documentation

- [LLM Optimization Guide](./LLM-OPTIMIZATION.md) - Complete LLM ranking strategies
- [JSON Schema Guide](./JSON-SCHEMA-GUIDE.md) - Schema optimization
- [PDF Strategy](./PDF-STRATEGY.md) - PDF generation for LLM SEO
- [2026 SEO Strategy](./2026-STRATEGY.md) - Strategic overview

---

## 🔗 External Resources

- **Press Wire**: https://www.prweb.com/
- **PR Newswire**: https://www.prnewswire.com/
- **Press Release Guidelines**: https://www.prweb.com/resources/best-practices/
- **Press Release Examples**: https://www.prweb.com/releases/

---

## 📞 Support

**Press Wire Support:**
- Phone: 1-866-640-6397
- Email: support@prweb.com
- Hours: Mon-Fri 9am-5pm ET

**Internal Contact:**
- Marketing Team: marketing@quest.com
- SEO Lead: seo@quest.com

---

**Document Owner:** Marketing & SEO Team
**Last Review:** October 8, 2025
**Next Review:** November 8, 2025
**Status:** Active Process ✅

---

**Press releases = Authority building + LLM ingestion. Use strategically for high-value content.** 🚀
