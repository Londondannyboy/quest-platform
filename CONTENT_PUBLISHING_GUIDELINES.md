# Quest Platform - Content Publishing Guidelines
**Version:** 1.0
**Last Updated:** October 10, 2025
**Enforcement:** MANDATORY for all AI agents & human editors

**Purpose:** Ensure all published content complies with Google's spam policies and maintains platform quality standards.

**Reference:** https://developers.google.com/search/docs/essentials/spam-policies

---

## 🚨 CRITICAL: Read Before Every Batch Generation

**This document is the AUTHORITY for content publication decisions.**

Any AI agent (Claude, GPT, Gemini, etc.) generating content for Quest Platform MUST:
1. ✅ Read this document at the start of each session
2. ✅ Validate content against these guidelines before publication
3. ✅ Flag violations for human review
4. ✅ Document any guideline changes in this file

---

## 📊 Google Spam Policy Compliance Matrix

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

---

## 🔴 CRITICAL: Scaled Content Abuse Prevention

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

**Enforcement Mechanism:**
```python
# backend/app/core/publication_limiter.py

async def can_publish(article: Dict) -> Tuple[bool, str]:
    """
    Check if publication is allowed under current limits

    Returns:
        (allowed: bool, reason: str)
    """

    site = article["target_site"]
    site_age_days = await get_site_age(site)
    today_count = await get_published_count(site, period="day")

    # Determine limit tier
    if site_age_days < 90:
        limits = PUBLICATION_LIMITS["new_site"]
    elif site_age_days < 180:
        limits = PUBLICATION_LIMITS["growing_site"]
    else:
        limits = PUBLICATION_LIMITS["established_site"]

    # Check for penalties
    if await has_manual_action(site):
        limits = PUBLICATION_LIMITS["penalty_recovery"]

    # Enforce daily limit
    if today_count >= limits["daily"]:
        return False, f"Daily limit reached ({limits['daily']})"

    # Check weekly/monthly
    week_count = await get_published_count(site, period="week")
    if week_count >= limits["weekly"]:
        return False, f"Weekly limit reached ({limits['weekly']})"

    return True, "OK"
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
        "format": "[1], [2], [3] with References section",
        "rationale": "E-E-A-T authority signals"
    },

    "references_section": {
        "required": True,
        "format": "## References\n[1] Source - URL",
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

---

## 📝 Pre-Publication Checklist

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
    citations = re.findall(r'\[\d+\]', article["content"])
    if len(citations) < QUALITY_GATES["citations"]["minimum"]:
        violations.append(f"CITATIONS: {len(citations)} < 15 minimum")

    # 4. References section
    has_refs = bool(re.search(r'##\s*References?\s*\n', article["content"]))
    if not has_refs:
        violations.append("REFERENCES_SECTION: Missing required References section")

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

---

## 🔍 Spam Pattern Detection

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

---

## 🎯 Topic Diversity Requirements

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

## 📊 Monitoring & Alerts

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

## 🔄 Schema Migration & Redirects

**Handling `/posts/` → `/articles/` migration:**

### Option 1: 301 Redirects (RECOMMENDED)
```python
# backend/app/main.py

@app.get("/posts/{slug}")
async def redirect_old_posts(slug: str):
    """
    Redirect old /posts/ URLs to new /articles/ URLs
    """

    # Check if article exists with this slug
    article = await db.get_article_by_slug(slug)

    if article:
        # 301 permanent redirect
        return RedirectResponse(
            url=f"/articles/{slug}",
            status_code=301
        )
    else:
        raise HTTPException(status_code=404)
```

**Pros:**
- ✅ Preserves SEO value (link juice transfers)
- ✅ Google recognizes as permanent move
- ✅ User-friendly (auto-redirects)

**Cons:**
- ⚠️ Extra server processing for each old URL

### Option 2: Let Google Figure It Out
**Google's Approach:**
- Crawls new `/articles/` pages
- Finds better content + newer dates
- Gradually replaces old pages in index

**Pros:**
- ✅ No redirect infrastructure needed
- ✅ Works naturally over time

**Cons:**
- ⚠️ Takes 2-4 weeks for Google to re-index
- ⚠️ Potential duplicate content period
- ⚠️ Loses existing link equity

**RECOMMENDATION:** Use 301 redirects if old pages have significant traffic/backlinks. Otherwise let Google naturally replace them.

### Schema Update
```sql
-- Neon migration (already done)
-- Just ensure slug format is consistent

UPDATE articles
SET slug = REPLACE(slug, '/posts/', '')
WHERE slug LIKE '/posts/%';
```

---

## 📋 Batch Generation Guidelines

**When running batch article generation:**

1. **Pre-batch validation:**
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

2. **During generation:**
   - Monitor quality scores in real-time
   - Auto-reject any article with violations
   - Save violations log for review

3. **Post-batch review:**
   - Human spot-check 10% of generated articles
   - Verify no spam patterns detected
   - Confirm all pass quality gates

---

## 🚨 Emergency Procedures

**If manual action detected:**

1. ✅ **STOP** all automated publication immediately
2. ✅ Review last 50 published articles
3. ✅ Identify pattern in flagged content
4. ✅ Update guidelines to prevent recurrence
5. ✅ Submit reconsideration request to Google
6. ✅ Resume at "penalty_recovery" rate limits

---

## 📝 Document Updates

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

**Version History:**
- v1.0 (Oct 10, 2025): Initial guidelines based on Google spam policies

**Next Review:** January 10, 2026
