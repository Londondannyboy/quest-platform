# Quest Platform - Content Publishing & Generation Guidelines

**Version:** 2.0
**Last Updated:** October 11, 2025
**Enforcement:** MANDATORY for all AI agents & human editors
**Consolidates:** Publishing guidelines, generation process, and SEO requirements

**Purpose:** Comprehensive guide for content creation, quality assurance, and publication across Quest Platform sites. Ensures Google spam policy compliance while maintaining platform quality standards.

**Reference:** https://developers.google.com/search/docs/essentials/spam-policies

---

## 1. Content Quality Standards

### 🚨 CRITICAL: Read Before Every Batch Generation

**This document is the AUTHORITY for content publication decisions.**

Any AI agent (Claude, GPT, Gemini, etc.) generating content for Quest Platform MUST:
1. ✅ Read this document at the start of each session
2. ✅ Validate content against these guidelines before publication
3. ✅ Flag violations for human review
4. ✅ Document any guideline changes in this file

### Google Spam Policy Compliance Matrix

Based on: https://developers.google.com/search/docs/essentials/spam-policies

| Spam Type | Our Risk | Mitigation Strategy | Enforcement |
|-----------|----------|---------------------|-------------|
| **Scaled Content Abuse** | 🔴 HIGH | Publication rate limits, quality gates | CRITICAL |
| **Cloaking** | 🟢 NONE | N/A (no cloaking) | N/A |
| **Doorway Pages** | 🟡 MEDIUM | Topic diversity, unique value per page | Monitor |
| **Hacked Content** | 🟢 NONE | N/A (we control content) | N/A |
| **Hidden Text/Links** | 🟢 NONE | Clean markdown, no tricks | Automated check |
| **Keyword Stuffing** | 🟡 MEDIUM | Natural language, AI detection | Automated check |
| **Link Spam** | 🟢 LOW | Curated external links, no PBNs | Manual review |
| **Machine-Generated Traffic** | 🟢 NONE | N/A (no bot traffic) | N/A |
| **Malware/Malicious** | 🟢 NONE | N/A (clean content) | N/A |
| **Misleading Functionality** | 🟢 NONE | N/A (no fake buttons) | N/A |
| **Scraped Content** | 🟡 MEDIUM | Original synthesis, not copying | Automated check |
| **Sneaky Redirects** | 🟢 LOW | Clean 301s only | Manual review |
| **Spammy Auto-Generated** | 🔴 HIGH | Quality gates, human review | CRITICAL |
| **Thin Affiliate Content** | 🟡 MEDIUM | 3000+ words, unique insights | Automated check |
| **User-Generated Spam** | 🟢 LOW | Moderation if we add comments | Monitor |

### 🔴 CRITICAL: Scaled Content Abuse Prevention

**Google's Definition:** "Creating large amounts of unoriginal content that provides little to no value to users."

**Our Risk Profile:**
- 🚨 **HIGH RISK:** Planning 1000-5000 articles/month
- 🚨 **AI-GENERATED:** 99% AI content
- ✅ **HIGH QUALITY:** 5K+ words with depth

### Publication Rate Limits (ENFORCED)

**ABSOLUTE MAXIMUMS (DO NOT EXCEED):**

```python
PUBLICATION_LIMITS = {
    # Site age: 0-3 months
    "new_site": {
        "daily": 2,
        "weekly": 10,
        "monthly": 40,
        "rationale": "Building authority, avoiding spam flags"
    },

    # Site age: 3-6 months
    "growing_site": {
        "daily": 5,
        "weekly": 25,
        "monthly": 100,
        "rationale": "Controlled growth, monitoring Search Console"
    },

    # Site age: 6+ months, clean record
    "established_site": {
        "daily": 10,
        "weekly": 50,
        "monthly": 200,
        "rationale": "Sustainable scale with quality maintenance"
    },

    # Special case: Penalty detected
    "penalty_recovery": {
        "daily": 1,
        "weekly": 3,
        "monthly": 10,
        "rationale": "Rebuilding trust with Google"
    }
}
```

### Quality Gates (ENFORCED)

**Minimum Requirements for Publication:**

```python
QUALITY_GATES = {
    "word_count": {
        "minimum": 3000,
        "target": 5000,
        "rationale": "Depth signals value to Google"
    },

    "citations": {
        "minimum": 15,
        "target": 25,
        "format": "Inline hyperlinks [text](url)",
        "rationale": "E-E-A-T authority signals"
    },

    "references_section": {
        "required": True,
        "format": "## Further Reading & Sources\n- [Title](URL) - Description",
        "rationale": "Trustworthiness + verification"
    },

    "originality": {
        "minimum_unique": 80,  # 80% unique vs existing content
        "check_method": "Embedding similarity",
        "rationale": "Not scaled/duplicate content"
    },

    "quality_score": {
        "minimum": 75,
        "target": 85,
        "scored_by": "EditorAgent",
        "rationale": "Overall quality threshold"
    },

    "eeat_signals": {
        "author_attribution": True,
        "last_updated": True,
        "expert_citations": True,
        "data_sources": True,
        "rationale": "Google's quality guidelines"
    }
}
```

### Pre-Publication Checklist

**EVERY article MUST pass this checklist before publication:**

```python
async def validate_for_publication(article: Dict) -> Dict:
    """
    Comprehensive pre-publication validation

    Returns:
        {
            "approved": bool,
            "violations": List[str],
            "warnings": List[str]
        }
    """

    violations = []
    warnings = []

    # 1. Rate limit check
    can_publish, reason = await publication_limiter.can_publish(article)
    if not can_publish:
        violations.append(f"RATE_LIMIT: {reason}")

    # 2. Word count
    word_count = len(article["content"].split())
    if word_count < QUALITY_GATES["word_count"]["minimum"]:
        violations.append(f"WORD_COUNT: {word_count} < 3000 minimum")
    elif word_count < QUALITY_GATES["word_count"]["target"]:
        warnings.append(f"Word count {word_count} below target (5000)")

    # 3. Citations
    citations = re.findall(r'\[.*?\]\(.*?\)', article["content"])
    if len(citations) < QUALITY_GATES["citations"]["minimum"]:
        violations.append(f"CITATIONS: {len(citations)} < 15 minimum")

    # 4. References section
    has_refs = bool(re.search(r'##\s*(Further Reading|References)', article["content"]))
    if not has_refs:
        violations.append("REFERENCES_SECTION: Missing required section")

    # 5. Author attribution
    if not article.get("author"):
        violations.append("AUTHOR: Missing author attribution")

    # 6. AI disclosure
    if "AI technology" not in article["content"]:
        warnings.append("AI_DISCLOSURE: Missing AI disclosure statement")

    # 7. Originality check
    similarity = await check_similarity_to_existing(article)
    if similarity > 20:  # >20% similar to existing content
        violations.append(f"ORIGINALITY: {similarity}% similar to existing content")

    # 8. Quality score
    if article.get("quality_score", 0) < QUALITY_GATES["quality_score"]["minimum"]:
        violations.append(f"QUALITY: Score {article['quality_score']} < 75 minimum")

    # 9. Keyword stuffing check
    if await detect_keyword_stuffing(article):
        violations.append("KEYWORD_STUFFING: Detected unnatural keyword density")

    # 10. Spam patterns
    spam_score = await check_spam_patterns(article)
    if spam_score > 30:
        violations.append(f"SPAM_PATTERNS: Score {spam_score}/100")

    return {
        "approved": len(violations) == 0,
        "violations": violations,
        "warnings": warnings,
        "passed_checks": 10 - len(violations),
        "total_checks": 10
    }
```

### Spam Pattern Detection

**Automated checks for spam signals:**

```python
async def check_spam_patterns(article: Dict) -> int:
    """
    Score article for spam patterns (0-100, lower is better)

    Returns spam score where:
    - 0-20: Clean
    - 21-40: Minor concerns
    - 41-60: Review required
    - 61-100: High spam risk
    """

    spam_score = 0
    content = article["content"]

    # 1. Keyword density (should be <3%)
    keyword_density = calculate_keyword_density(content, article["keywords"])
    if keyword_density > 3:
        spam_score += 20

    # 2. Repetitive phrases
    repetition_score = detect_phrase_repetition(content)
    if repetition_score > 30:
        spam_score += 15

    # 3. Thin content sections
    sections = content.split("\n\n")
    thin_sections = [s for s in sections if len(s.split()) < 100]
    if len(thin_sections) / len(sections) > 0.3:
        spam_score += 10

    # 4. Unnatural link patterns
    links = re.findall(r'\[.*?\]\((.*?)\)', content)
    if len(links) > 30:  # Too many links
        spam_score += 10

    # 5. AI detection patterns
    ai_patterns = [
        r"As an AI",
        r"I don't have personal",
        r"I apologize",
        r"It's important to note that",
        r"Please note",
        r"It's worth mentioning"
    ]
    for pattern in ai_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            spam_score += 5

    # 6. Over-optimization signals
    if article["meta_title"] == article["title"]:  # Lazy SEO
        spam_score += 5

    return min(spam_score, 100)
```

### Topic Diversity Requirements

**Prevent "doorway pages" by ensuring topic diversity:**

```python
TOPIC_DIVERSITY_RULES = {
    "maximum_similar_topics": {
        "per_day": 2,
        "per_week": 5,
        "similarity_threshold": 0.7,  # Cosine similarity
        "rationale": "Avoid appearing like doorway pages"
    },

    "required_variety": {
        "categories": 5,  # Minimum 5 different categories per week
        "formats": 3,  # Mix guides, comparisons, listicles
        "rationale": "Show editorial judgment, not automation"
    }
}
```

---

## 2. SEO Requirements

### Technical Fundamentals (Zero Tolerance)

AI crawlers have **zero tolerance** for technical issues. Fix these first:

#### Crawlability Verification

**Check robots.txt:**
```txt
# ✅ CORRECT
User-agent: *
Allow: /
Sitemap: https://relocation.quest/sitemap.xml

# ❌ WRONG (blocks all crawlers)
User-agent: *
Disallow: /
```

**Check Meta Robots:**
```html
<!-- ✅ CORRECT: Allows indexing -->
<meta name="robots" content="index, follow">

<!-- ❌ WRONG: Blocks indexing -->
<meta name="robots" content="noindex, nofollow">
```

**Site Indexing Test:**
```bash
# Google search
site:relocation.quest

# Expected: All your pages show up
```

#### HTML-First Architecture (CRITICAL)

**Why This Matters:**
- HTML: AI crawlers can read immediately ✅
- JavaScript: Most AI crawlers don't render JS well ❌
- **Result:** JS sites get ignored in favor of HTML competitors

**Quest Platform Status:**
- ✅ Astro 4.x - HTML-first by default
- ✅ Static generation - Pre-rendered HTML at build time
- ✅ No client-side rendering - Content available immediately

**Verification Test:**
```bash
# Disable JavaScript in browser
# Reload page
# Can you see content?
✅ YES = HTML-first (good for AI)
❌ NO = JS-required (bad for AI)
```

#### Core Web Vitals Optimization

**Target: < 2.5 Seconds (p95)**

**Critical Optimization:**
- **Images:** < 150KB each, WebP format, quality 85
- **LCP:** < 2.5 seconds
- **FID:** < 100ms
- **CLS:** < 0.1
- **PageSpeed Score:** > 90

**Astro Implementation:**
```javascript
// astro.config.mjs
export default defineConfig({
  image: {
    service: squooshImageService(),
    formats: ['webp'], // WebP format
    quality: 85, // Balance quality vs size
  },
});
```

#### Mobile Responsiveness

**Requirements:**
- ✅ Viewport meta tag present
- ✅ Text readable without zooming (min 16px)
- ✅ Touch targets ≥ 48x48px
- ✅ No horizontal scrolling
- ✅ Fast mobile load time (< 3s)

#### Indexing & Sitemap

**Sitemap Requirements:**
```xml
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://relocation.quest/portugal-digital-nomad-visa</loc>
    <lastmod>2025-10-08</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
```

### On-Page Optimization

#### Meta Tags Requirements

**Every article MUST have:**
- Meta title (< 60 chars, keyword-rich)
- Meta description (< 160 chars, compelling)
- Keywords (5-10 relevant terms)
- Alt text for all images
- Internal links (3-5 related articles)
- External links (3-5 authoritative sources)

#### Header Structure

**H1 Usage (CRITICAL):**
- ❌ NO H1 in article content (frontend displays it)
- ✅ Start with "## What You Need to Know" (not "TL;DR")

**Proper Header Hierarchy:**
```markdown
## What You Need to Know
Brief summary section

## Main Topic Section
Content here

### Subtopic
Detailed content

### Another Subtopic
More details
```

#### LLM-First JSON Schema

**Critical Insight:** LLMs read JSON schema FIRST before article body.

**LLM-Optimized Schema (Verbose):**
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Portugal Digital Nomad Visa: Complete 2025 Guide",
  "description": "Comprehensive guide covering requirements, application process, costs, tax benefits, and best cities for remote workers in Portugal",
  "keywords": "portugal, digital nomad, visa, remote work, 2025",
  "wordCount": 5000,
  "author": {
    "@type": "Organization",
    "name": "Quest Platform",
    "description": "AI-powered content intelligence platform with human verification"
  },
  "mentions": [
    {
      "@type": "Place",
      "name": "Portugal",
      "sameAs": "https://en.wikipedia.org/wiki/Portugal"
    }
  ],
  "citation": [
    {"@type": "WebPage", "url": "https://imigrante.sef.pt"}
  ],
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How much income needed for Portugal Digital Nomad Visa?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Minimum €3,280/month ($3,500 USD) from remote work"
      }
    }
  ]
}
```

**Key Elements for LLMs:**
1. Verbose descriptions (LLMs don't penalize verbosity)
2. Entity mentions with Wikipedia links (context)
3. FAQ sections (Q&A format LLMs love)
4. Citations (authority signal)
5. Complete metadata

### Link Building Requirements & Domain Authority Strategy

**CRITICAL INSIGHT:** We're new → Link to high-DA competitors in our niche!

**Why This Works:**
- Google rewards linking to authority sites (trust signal)
- Competitors already ranking = authority in our domain
- Sending them traffic doesn't hurt them (they're already winning)
- We gain authority by association
- DataForSEO/Serper tells us WHO is ranking high

**External Link Strategy:**

1. **Tier 1: Ultra-High Authority (DA 90+)** - FIRST PARAGRAPH
   - Wikipedia, BBC, Reuters, .gov sites
   - Purpose: Initial trust signal for Google's crawler
   - Placement: First 500 words, even if just "setting the scene"

2. **Tier 2: Niche Authority (DA 60-89)** - THROUGHOUT ARTICLE
   - **HIGH PRIORITY:** Sites ranking on page 1 for our target keyword
   - Nomad List, Expatica, InterNations (for relocation niche)
   - WHY: Google sees them as authorities in THIS specific domain
   - Strategy: Link to their deep content (not homepage)
   - Example: Link to Nomad List's Lisbon guide from our Portugal article

3. **Tier 3: Official Sources (DA varies)** - DETAILS SECTIONS
   - Country-specific government sites
   - Embassy pages, consulate portals
   - Official visa application sites

**DataForSEO/Serper Integration:**

```python
# During keyword research, get SERP rankings
serp_results = await serper.search(keyword)

# Extract DA from top 10 results
for result in serp_results["organic"][:10]:
    domain = extract_domain(result["link"])
    da_score = await dataforseo.get_domain_authority(domain)

    # If DA 60+, ADD to validated_urls as "niche_authority"
    if da_score >= 60:
        await cache_as_linkable_competitor(result["link"], da_score)

# ContentAgent receives these as "approved niche authority links"
```

**Link Distribution Requirements:**

| Link Type | Count | DA Range | Placement | Purpose |
|-----------|-------|----------|-----------|---------|
| Ultra-High (Wikipedia, BBC) | 1-2 | 90+ | First paragraph | Initial trust |
| Niche Authority (competitors) | 3-5 | 60-89 | Throughout | Domain relevance |
| Official Sources (.gov) | 2-3 | Varies | Detail sections | Factual backup |
| Internal Links | 3-5 | N/A | Throughout | Cluster building |

**Example (Portugal Digital Nomad Visa Article):**

```markdown
## What You Need to Know

According to [Wikipedia](https://en.wikipedia.org/wiki/Portugal), Portugal has become
one of Europe's top destinations for remote workers. [Nomad List](https://nomadlist.com/lisbon)
ranks Lisbon as #3 globally for digital nomads, citing low cost of living and excellent
infrastructure.

The [Portuguese Immigration Service (SEF)](https://imigrante.sef.pt) officially launched
the digital nomad visa in October 2022. As [Expatica](https://expatica.com/pt/moving/visas/portugal-digital-nomad-visa)
reports, over 1,200 applications were approved in the first year.
```

**Why This Example Works:**
- ✅ Wikipedia (DA 98) - First sentence
- ✅ Nomad List (DA 72) - Competitor we're trying to outrank!
- ✅ SEF.pt (DA 85) - Official government source
- ✅ Expatica (DA 68) - Established competitor with authority

**Strategic Benefits:**
1. **Authority Halo:** Linking to DA 60-90 sites = "we know the good sources"
2. **Topical Relevance:** Google sees we understand the niche landscape
3. **No Downside:** Competitors already dominate SERPs, our link doesn't change that
4. **Algorithm Signal:** "This site curates quality info, not just self-promotion"

**Validation Requirements:**
- All links must be validated (no 404s)
- Minimum DA 50 for any external link
- Cache validated URLs with DA scores
- Use inline hyperlink format: `[anchor text](url)`

**Internal Links:**
- 3-5 related articles per piece
- Use descriptive anchor text
- Build topic clusters through internal linking
- Prioritize after external authority links established

### Domain Authority Data Sources

**Primary: DataForSEO Backlinks API** (RECOMMENDED - Already Integrated!)

**Why DataForSEO:**
- ✅ Already using for keyword validation (cost synergy)
- ✅ Comprehensive metrics: DA, backlinks, referring domains, traffic
- ✅ Cost: $0.10/domain query (cheaper than MOZ $0.016/URL)
- ✅ Cache-friendly: 30-day TTL for stable domains
- ✅ Batch queries: Check 50 domains in one request

**Alternative: Serper.dev SERP Data**
- ✅ Already integrated for Template Detection
- ✅ Provides page 1 rankings (implicit authority signal)
- ✅ Cost: $0.002/query (extremely cheap)
- ✅ Use case: "If it ranks page 1 for our keyword → it's authoritative"

**DataForSEO Endpoint:**
```python
POST https://api.dataforseo.com/v3/backlinks/domain_metrics

{
  "targets": [
    "nomadlist.com",
    "expatica.com",
    "internations.org"
  ]
}

Response:
{
  "tasks": [{
    "result": [{
      "target": "nomadlist.com",
      "rank": 72,  # 0-100 (our DA score)
      "backlinks": 125000,
      "referring_domains": 3400,
      "organic_traffic": 450000,
      "first_seen": "2014-05-01"
    }]
  }]
}
```

**Cost Optimization Strategy:**

1. **Cache Aggressively:**
   - DA 90+ sites: Cache 90 days (they don't change)
   - DA 60-89 sites: Cache 30 days
   - DA <60 sites: Cache 7 days (volatile)

2. **Batch Query During Keyword Research:**
   - Serper returns top 10 results
   - Extract all domains → Single DataForSEO batch request
   - Store in `validated_urls` table
   - Cost: $0.10 per keyword (not per article)

3. **SERP-Only Fallback:**
   - If domain not in cache AND budget tight
   - Use Serper ranking as proxy: Page 1 = assumed DA 60+
   - Cost: $0.002 vs $0.10

**Implementation Priority:**
1. **Phase 1:** Integrate DataForSEO domain metrics (1 hour)
2. **Phase 2:** Build validated_urls cache table (30 min)
3. **Phase 3:** Update ContentAgent prompts with DA requirements (1 hour)
4. **Phase 4:** Add authority scoring to EditorAgent (1 hour)

**Expected ROI:**
- DA data cost: $0.10/keyword × 1 keyword/article = $0.10/article
- Authority signal boost: Estimated +15-25% organic traffic
- Break-even: If 1 extra conversion per 50 articles → ROI positive

---

## 3. Article Structure Requirements

### Content Format Standards

**CRITICAL RULES:**

1. **No H1 in Content**
   - Frontend displays H1 from title field
   - Article content starts with H2

2. **Start with "What You Need to Know"**
   - Not "TL;DR" (outdated format)
   - 150-word summary of key points

3. **Paragraph Length Limits**
   - Maximum 150 words per paragraph
   - Use bullet points for lists
   - Break long sections with H3 subheadings

4. **Readability Requirements**
   - Flesch Reading Ease: 60-70 (target)
   - Use short sentences (avg 15-20 words)
   - Active voice preferred
   - Avoid jargon without explanation

### Required Sections

**Every Article Must Include:**

1. **What You Need to Know** (H2)
   - 150-word summary
   - Key takeaways in bullet points

2. **Main Content Sections** (H2)
   - Logical flow
   - Clear section breaks
   - Comprehensive coverage

3. **FAQ Section** (H2)
   - Minimum 4-10 Q&A pairs
   - Common user questions
   - Direct, concise answers

4. **Further Reading & Sources** (H2)
   - Bullet list format
   - `- [Title](URL) - Description`
   - Minimum 5 sources cited

### Citation Format (UPDATED)

**CORRECT Format (Mobile-Friendly):**
```markdown
The [Portugal Digital Nomad Visa](https://imigrante.sef.pt) requires minimum income of €3,280/month.

Portugal's [Non-Habitual Resident (NHR) tax regime](https://info.portaldasfinancas.gov.pt) offers significant benefits.
```

**WRONG Format (Deprecated):**
```markdown
Portugal Digital Nomad Visa requires minimum income [1].
Portugal's NHR tax regime offers benefits [2].

## References
[1] Source - URL
[2] Source - URL
```

**Requirements:**
- Minimum 15-25 inline hyperlinks per article
- Distribute throughout content
- Use descriptive anchor text
- All URLs must be validated
- Add "Further Reading & Sources" section at end

---

## 4. Article Generation Process

### Primary Generation Script

**`generate_article.py` (at backend/) is the SINGLE SOURCE OF TRUTH for article generation in Quest Platform.**

This script:
- Uses the full 7-agent orchestrator pipeline
- Includes LinkValidator for preventing hallucinated URLs
- Supports Directus publishing workflow
- Can scale to generate 100+ articles
- Tracks costs and quality metrics

### Usage Examples

#### Single Article Generation

```bash
# With specific topic
python3 generate_article.py --topic "Best cafes for remote work in Lisbon 2025"

# Interactive mode (will prompt for topic)
python3 generate_article.py

# Target different site
python3 generate_article.py --topic "Career growth strategies" --site placement
```

#### Batch Generation

```bash
# Generate 10 articles with default topics
python3 generate_article.py --auto --count 10

# Generate 100 articles for production
python3 generate_article.py --auto --count 100

# Generate from topics file (one topic per line)
python3 generate_article.py --batch topics.txt

# Limit batch size
python3 generate_article.py --batch topics.txt --count 50
```

### Architecture Flow

```
backend/generate_article.py
    ↓
QUEST_CONTENT_PUBLISHING_GUIDELINES.md (Read compliance rules)
    ↓
Pre-Publication Validation (Rate limits, topic diversity)
    ↓
ArticleOrchestrator (ChunkedContentAgent + 4 Support Agents)
    ├── ResearchAgent (6 APIs: Perplexity + Tavily + Serper + LinkUp + Firecrawl + DataForSEO)
    ├── LinkValidator (External URL validation + internal link suggestions)
    ├── ChunkedContentAgent (Hybrid Gemini + Sonnet)
    │   ├── Gemini 2.5 Pro: Generate 3 chunks in parallel (1,293 words)
    │   ├── Gemini 2.5 Flash: Weave chunks with transitions
    │   └── Sonnet 4.5: Expand & refine to 5,344 words (310% growth!)
    ├── EditorAgent (Quality scoring + citation validation + References section check)
    └── ImageAgent (FLUX + Cloudinary - 4 images/article)
    ↓
Post-Publication Validation (Quality gates, spam pattern detection)
    ↓
Database (Neon PostgreSQL)
    ↓
Directus CMS (Publishing workflow - if quality > 75)
    ↓
Frontend (relocation.quest)
```

### Command Line Arguments

| Argument | Description | Example | Status |
|----------|-------------|---------|--------|
| `--topic` | Single article topic | `--topic "Portugal visa guide"` | ✅ Working |
| `--batch` | File with topics (one per line) | `--batch topics.txt` | ✅ Working |
| `--auto` | Use default high-value topics | `--auto` | ✅ Working |
| `--count` | Number of articles to generate | `--count 100` | ✅ Working |
| `--site` | Target site (relocation/placement/rainmaker) | `--site relocation` | ✅ Working |
| `--concurrent` | Max concurrent generations (default=1) | `--concurrent 3` | ⚠️ Accepted but not used yet |

### Key Features

**Link Validation:**
- All external URLs are validated before inclusion
- Internal links suggest related articles
- No more hallucinated links (Option 3 implementation)

**Progress Tracking:**
- Real-time progress updates
- Cost tracking per article
- Quality score reporting
- Success rate monitoring

**Error Recovery:**
- Graceful error handling
- Partial batch completion
- Detailed error logging
- Resume capability via summaries

**Cost Management:**
- Per-article cost tracking
- Total batch cost calculation
- Cost breakdown by agent
- Average cost metrics

### Output Files

The script generates summary files for tracking:

**Single Article: `generation_summary.json`**
```json
{
  "timestamp": "2025-10-10T14:30:00",
  "articles_generated": 1,
  "total_cost": 0.75,
  "article": {
    "id": "uuid",
    "title": "Article Title",
    "slug": "article-slug",
    "quality": 85,
    "url": "https://relocation.quest/article-slug"
  }
}
```

**Batch Generation: `batch_generation_summary.json`**
```json
{
  "timestamp": "2025-10-10T14:30:00",
  "articles_requested": 100,
  "articles_generated": 98,
  "success_rate": "98.0%",
  "total_cost": 73.50,
  "average_quality": 83.5,
  "articles": [...]
}
```

### Cost Analysis

**Per Article Breakdown:**
```
Research (6 APIs):        $0.44
ChunkedContent (Gemini):  $0.01 (weaving)
Content (Sonnet):         $0.75 (refinement)
Editor Scoring:           $0.005
Images (4x FLUX):         $0.12
─────────────────────────────────
Total per article:        $0.75
```

**Monthly Operating Costs (1000 articles):**
```
Infrastructure: $80/month
  Neon Database: $50
  Railway Backend: $30
  Vercel Frontend: $0 (free tier)
  Cloudinary: $0 (free tier)

AI APIs: $355/month (with 40% cache)
  Perplexity: $300
  Claude Sonnet 4.5: $52.50
  OpenAI Embeddings: $0.10
  Replicate FLUX: $3

Total: $435/month = $0.44/article
```

---

## 5. Publishing Workflow

### Quality Gates Enforcement

**Article Status Flow:**

```python
# Quality score determines status
if quality_score >= 85:
    status = "approved"  # Auto-publish
elif quality_score >= 75:
    status = "review"    # Human review required
elif quality_score >= 60:
    status = "refine"    # Editor refinement triggered
else:
    status = "reject"    # Below minimum threshold
```

### Rate Limits Enforcement

**Pre-Batch Validation:**

```python
async def validate_batch(topics: List[str]) -> Dict:
    """
    Validate entire batch before starting generation
    """

    # Check rate limits
    allowed_count = await get_remaining_daily_quota(site)
    if len(topics) > allowed_count:
        return {
            "approved": False,
            "reason": f"Batch size {len(topics)} exceeds daily limit {allowed_count}"
        }

    # Check topic diversity
    diversity_score = calculate_topic_diversity(topics)
    if diversity_score < 0.5:
        return {
            "approved": False,
            "reason": "Topics too similar - may trigger doorway page detection"
        }

    # Check for duplicates
    existing = await check_existing_topics(topics)
    if existing:
        return {
            "approved": False,
            "reason": f"Duplicate topics found: {existing}"
        }

    return {"approved": True}
```

### Manual Review Process

**During generation:**
- Monitor quality scores in real-time
- Auto-reject any article with violations
- Save violations log for review

**Post-batch review:**
- Human spot-check 10% of generated articles
- Verify no spam patterns detected
- Confirm all pass quality gates

### Monitoring & Alerts

**Google Search Console monitoring (daily):**

```python
MONITORING_ALERTS = {
    "critical": {
        "manual_action": True,
        "traffic_drop": 30,  # >30% drop
        "indexation_rate": 50,  # <50% pages indexed
        "action": "STOP ALL PUBLICATION + Human review"
    },

    "warning": {
        "traffic_drop": 15,  # >15% drop
        "indexation_rate": 70,  # <70% pages indexed
        "position_drop": 10,  # Average drop >10 positions
        "action": "Pause publication + Audit recent content"
    },

    "info": {
        "traffic_drop": 5,  # >5% drop
        "indexation_delay": 7,  # Pages not indexed in 7 days
        "action": "Monitor + Document"
    }
}
```

---

## 6. Compliance & Safety

### E-E-A-T Requirements

**Experience, Expertise, Authoritativeness, Trustworthiness**

**Required for ALL Articles:**

1. **Experience:**
   - Real case studies with names/photos
   - First-hand accounts
   - Practical examples

2. **Expertise:**
   - Expert quotes from professionals
   - Data from authoritative sources
   - Official documentation cited

3. **Authoritativeness:**
   - .gov and .edu sources
   - Press mentions
   - Expert contributor bios

4. **Trustworthiness:**
   - Update dates displayed
   - Transparent methodology
   - Clear sourcing
   - Accuracy disclaimers for YMYL

### YMYL Considerations

**Your Money or Your Life Topics**

Quest's entire niche is YMYL-heavy:
- Visa/immigration = YMYL (life-changing decisions)
- Tax advice = YMYL (financial impact)
- Legal processes = YMYL (legal consequences)

**Enhanced Requirements for YMYL:**
- Minimum quality score: 85 (not 75)
- Expert review required
- Legal disclaimers included
- Update frequency: Monthly
- Source verification: Double-checked

### Citation Standards

**Authoritative Sources Required:**

**Tier 1 (Preferred):**
- Government websites (.gov)
- Official immigration portals
- Tax authority sites
- Embassy/consulate pages

**Tier 2 (Acceptable):**
- Established news organizations
- Professional associations
- Academic institutions (.edu)
- Recognized industry experts

**Tier 3 (Use Sparingly):**
- Reputable blogs
- Industry publications
- Verified company sites

**Not Acceptable:**
- User-generated content sites
- Unverified sources
- Competitor marketing content
- Outdated resources (>2 years old for legal/tax)

### AI Disclosure

**Required Statement:**
Include in every article footer:
```
This article was created with AI technology and reviewed by human editors
to ensure accuracy and quality. Last updated: [DATE]
```

---

## 7. Emergency Procedures

### If Manual Action Detected

**Immediate Response:**

1. ✅ **STOP** all automated publication immediately
2. ✅ Review last 50 published articles
3. ✅ Identify pattern in flagged content
4. ✅ Update guidelines to prevent recurrence
5. ✅ Submit reconsideration request to Google
6. ✅ Resume at "penalty_recovery" rate limits

### Schema Migration & Redirects

**Handling URL changes:**

**Option 1: 301 Redirects (RECOMMENDED)**
```python
@app.get("/posts/{slug}")
async def redirect_old_posts(slug: str):
    article = await db.get_article_by_slug(slug)
    if article:
        return RedirectResponse(
            url=f"/articles/{slug}",
            status_code=301
        )
    else:
        raise HTTPException(status_code=404)
```

**Pros:**
- ✅ Preserves SEO value
- ✅ Google recognizes as permanent move
- ✅ User-friendly (auto-redirects)

---

## 8. Troubleshooting

### Database Connection Error
```bash
# Ensure backend is running
cd ~/quest-platform/backend
python3 -m app.main
```

### API Key Issues
```bash
# Check .env file has all keys
cat ~/quest-platform/backend/.env | grep API_KEY
```

### Memory Issues with Large Batches
```bash
# Split into smaller batches
python3 generate_article.py --batch topics.txt --count 25
```

### Low Quality Scores
- Verify research quality (6 APIs working)
- Check citation count (minimum 15)
- Validate word count (minimum 3000)
- Review E-E-A-T signals

---

## 9. Document Updates

**This document must be updated when:**
- Google updates spam policies
- Manual actions received
- New spam patterns detected
- Quality thresholds change
- Site performance data suggests changes

**Update Process:**
1. Document change in git commit
2. Notify all AI agents (system prompt update)
3. Test with 10 articles before full rollout

---

## Version History

- **v2.0 (Oct 11, 2025):** Consolidated from 3 source documents
  - Merged QUEST_CONTENT_PUBLISHING_GUIDELINES.md (528 lines)
  - Merged QUEST_GENERATION.md (466 lines)
  - Merged relevant sections from QUEST_SEO.md (1040 lines)
  - Updated citation format to inline hyperlinks
  - Updated article structure requirements (no H1, "What You Need to Know")
  - Added chunked content system documentation

- **v1.0 (Oct 10, 2025):** Initial guidelines based on Google spam policies

**Next Review:** January 11, 2026
