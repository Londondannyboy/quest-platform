# Quest Platform URL Structure & Content Types

**Date:** October 11, 2025
**Status:** Design Document (Implementation Pending)
**Authority:** Single Source of Truth for URL patterns across all Quest sites

---

## Content-Type-Based URL Architecture

### Core Philosophy

Instead of generic `/blog` or `/articles`, Quest uses **semantic URL paths** that signal content type to both users and search engines:

- ✅ **GOOD:** `relocation.quest/guide/italy-digital-nomad-visa`
- ✅ **GOOD:** `placement.quest/comparison/tech-hubs-berlin-vs-amsterdam`
- ❌ **BAD:** `relocation.quest/articles/italy-digital-nomad-visa`
- ❌ **BAD:** `placement.quest/blog/post-123`

**Benefits:**
1. **SEO:** Clear semantic signals (Google understands content type from URL)
2. **UX:** Users know what to expect before clicking
3. **Multi-site:** Different sites can specialize in different content types
4. **Template Intelligence:** URL maps directly to visual template

---

## URL Pattern by Content Type

### Relocation.quest

**Primary Focus:** Immigration, visas, digital nomad guides

| Content Type | URL Pattern | Example | Template |
|--------------|-------------|---------|----------|
| **Guide** | `/guide/{topic}` | `/guide/italy-digital-nomad-visa-2025` | Ultimate Guide |
| **Comparison** | `/comparison/{topics}` | `/comparison/spain-vs-portugal-digital-nomad-visa` | Comparison Matrix |
| **Listicle** | `/list/{topic}` | `/list/top-10-digital-nomad-cities-europe` | Listicle |
| **Country Hub** | `/country/{country}` | `/country/portugal` | Cluster Hub |
| **Deep Dive** | `/deep-dive/{topic}` | `/deep-dive/tax-implications-portugal-d7-visa` | Deep Dive Specialist |

**Optional:** Add country prefix for location-specific content:
- `/guide/portugal/d7-visa-requirements`
- `/guide/italy/digital-nomad-visa`

### Placement.quest

**Primary Focus:** Career guidance, job markets, recruitment

| Content Type | URL Pattern | Example | Template |
|--------------|-------------|---------|----------|
| **Guide** | `/guide/{country}/{topic}` | `/guide/germany/tech-job-market` | Location Guide |
| **Comparison** | `/comparison/{topics}` | `/comparison/berlin-vs-amsterdam-tech-hubs` | Comparison Matrix |
| **Market Report** | `/market/{country}` | `/market/germany/tech-salaries-2025` | Deep Dive Specialist |
| **Interview Guide** | `/interview/{industry}` | `/interview/tech/faang-preparation` | Ultimate Guide |

### Rainmaker.quest

**Primary Focus:** Business growth, sales, entrepreneurship

| Content Type | URL Pattern | Example | Template |
|--------------|-------------|---------|----------|
| **Guide** | `/guide/{topic}` | `/guide/saas-pricing-strategies` | Ultimate Guide |
| **Case Study** | `/case-study/{company}` | `/case-study/stripe-go-to-market` | Deep Dive Specialist |
| **Playbook** | `/playbook/{topic}` | `/playbook/cold-email-outreach` | Location Guide |
| **Comparison** | `/comparison/{tools}` | `/comparison/hubspot-vs-salesforce` | Comparison Matrix |

---

## Database Schema: `content_type` Column

### New Column Definition

```sql
ALTER TABLE articles
ADD COLUMN content_type VARCHAR(50);

-- Allowed values
CREATE TYPE content_type_enum AS ENUM (
    'guide',           -- Comprehensive guides (Ultimate Guide template)
    'comparison',      -- Side-by-side comparisons (Comparison Matrix)
    'listicle',        -- Top X lists (Listicle template)
    'deep-dive',       -- In-depth analysis (Deep Dive Specialist)
    'country-hub',     -- Country cluster pages (Cluster Hub)
    'market-report',   -- Market analysis (Deep Dive Specialist)
    'case-study',      -- Real-world examples (Deep Dive Specialist)
    'playbook',        -- Step-by-step processes (Location Guide)
    'interview-guide', -- Interview prep (Ultimate Guide)
    'conversational'   -- AI search optimization (Conversational Answer Hub)
);
```

### Mapping: Content Type → Surface Template

| content_type | surface_template | target_archetype |
|--------------|------------------|------------------|
| `guide` | `ultimate_guide` | `skyscraper` |
| `comparison` | `comparison` | `comparison_matrix` |
| `listicle` | `listicle` | `skyscraper` or `cluster_hub` |
| `deep-dive` | `deep_dive_tutorial` | `deep_dive` |
| `country-hub` | `location_guide` | `cluster_hub` |
| `market-report` | `deep_dive_tutorial` | `deep_dive` |
| `case-study` | `deep_dive_tutorial` | `deep_dive` |
| `playbook` | `location_guide` | `deep_dive` |
| `interview-guide` | `ultimate_guide` | `skyscraper` |
| `conversational` | `conversational_answer` | `conversational_answer_hub` |

---

## URL Generation Logic

### Backend: Orchestrator

```python
def generate_url_slug(
    title: str,
    content_type: str,
    target_site: str,
    country: Optional[str] = None
) -> str:
    """
    Generate SEO-friendly URL slug based on content type and site.

    Examples:
        relocation.quest:
            - guide + "Italy Digital Nomad Visa" → /guide/italy-digital-nomad-visa
            - comparison + "Spain vs Portugal" → /comparison/spain-vs-portugal-digital-nomad-visa

        placement.quest:
            - guide + country="germany" → /guide/germany/tech-job-market
            - market + country="germany" → /market/germany/tech-salaries-2025
    """

    # Sanitize title
    base_slug = re.sub(r'[^a-z0-9\s-]', '', title.lower())
    base_slug = re.sub(r'\s+', '-', base_slug).strip('-')[:100]

    # Build URL path based on content type and site
    if target_site == 'placement' and country:
        return f"{content_type}/{country}/{base_slug}"
    else:
        return f"{content_type}/{base_slug}"
```

### Database: Full URL Column

```sql
ALTER TABLE articles
ADD COLUMN full_url TEXT GENERATED ALWAYS AS (
    CASE target_site
        WHEN 'relocation' THEN 'https://relocation.quest/' || slug
        WHEN 'placement' THEN 'https://placement.quest/' || slug
        WHEN 'rainmaker' THEN 'https://rainmaker.quest/' || slug
    END
) STORED;
```

---

## Frontend: Astro Dynamic Routes

### Relocation.quest

```
src/pages/
├── guide/
│   └── [...slug].astro         # /guide/*
├── comparison/
│   └── [...slug].astro         # /comparison/*
├── list/
│   └── [...slug].astro         # /list/*
├── country/
│   └── [country].astro         # /country/{country}
├── deep-dive/
│   └── [...slug].astro         # /deep-dive/*
```

### Placement.quest

```
src/pages/
├── guide/
│   └── [country]/
│       └── [...slug].astro     # /guide/{country}/*
├── comparison/
│   └── [...slug].astro         # /comparison/*
├── market/
│   └── [country].astro         # /market/{country}
├── interview/
│   └── [industry]/
│       └── [...slug].astro     # /interview/{industry}/*
```

### Shared Logic: `getStaticPaths()`

```typescript
// src/pages/guide/[...slug].astro
export async function getStaticPaths() {
  // Query Neon or API for all articles where:
  // - target_site = 'relocation'
  // - content_type = 'guide'
  // - status = 'published'

  const articles = await fetchArticles({
    site: 'relocation',
    contentType: 'guide'
  });

  return articles.map(article => ({
    params: { slug: article.slug.replace('guide/', '') },
    props: { article }
  }));
}
```

---

## Migration Path

### Phase 1: Add Schema Columns (Non-Breaking)

```sql
-- Add new columns with defaults
ALTER TABLE articles
ADD COLUMN content_type VARCHAR(50) DEFAULT 'guide';

-- Backfill existing articles
UPDATE articles
SET content_type = CASE
    WHEN slug LIKE '%comparison%' OR title LIKE '%vs%' THEN 'comparison'
    WHEN slug LIKE '%top-%' OR title LIKE 'Top %' THEN 'listicle'
    ELSE 'guide'
END;

-- Make required after backfill
ALTER TABLE articles
ALTER COLUMN content_type SET NOT NULL;
```

### Phase 2: Update Slug Format

```sql
-- Update slugs to include content type prefix
UPDATE articles
SET slug = content_type || '/' || slug
WHERE slug NOT LIKE content_type || '/%';
```

### Phase 3: Update Astro Routes

1. Create new dynamic route files
2. Update `getStaticPaths()` to filter by content_type
3. Deploy with 301 redirects for old URLs

### Phase 4: Update Orchestrator

```python
# In orchestrator.py
article_data = {
    "title": title,
    "content_type": detect_content_type(topic),  # NEW
    "slug": generate_url_slug(
        title,
        content_type,
        target_site,
        country=extracted_country  # NEW
    ),
    ...
}
```

---

## Content Type Detection Rules

### Automatic Detection (in Orchestrator)

```python
def detect_content_type(topic: str) -> str:
    """
    Detect content type from topic string.

    Examples:
        "Italy vs Spain Digital Nomad Visa" → comparison
        "Top 10 Cities for Remote Work" → listicle
        "Complete Guide to Portugal D7 Visa" → guide
        "Tax Implications of NHR Status" → deep-dive
    """

    topic_lower = topic.lower()

    # Comparison indicators
    if ' vs ' in topic_lower or ' versus ' in topic_lower:
        return 'comparison'

    # Listicle indicators
    if re.match(r'(top|best) \d+', topic_lower):
        return 'listicle'

    # Deep dive indicators
    if any(word in topic_lower for word in ['implications', 'analysis', 'breakdown']):
        return 'deep-dive'

    # Default to guide
    return 'guide'
```

### Manual Override

User can specify when generating:

```bash
python3 generate_article.py \
    --topic "Spain vs Portugal Digital Nomad Visa" \
    --site relocation \
    --content-type comparison
```

---

## Benefits Summary

### SEO Impact
- **Clear semantic signals:** Google understands `/guide/` vs `/comparison/`
- **Keyword optimization:** Content type becomes part of URL
- **Breadcrumbs:** Natural hierarchy (relocation.quest > guide > italy)

### User Experience
- **Predictability:** Users know what to expect from URL
- **Navigation:** Easy to browse all guides, all comparisons, etc.
- **Shareability:** URLs are human-readable and descriptive

### Development
- **Template mapping:** URL directly maps to Astro component
- **Content strategy:** Easy to see content type distribution
- **Analytics:** Track performance by content type

---

## Next Steps

1. ✅ Document URL structure (this file)
2. ⏳ Add `content_type` column to Neon schema
3. ⏳ Update Orchestrator with content type detection
4. ⏳ Implement URL slug generation with content type prefix
5. ⏳ Create Astro dynamic routes for each content type
6. ⏳ Backfill existing articles with content types
7. ⏳ Deploy with 301 redirects

---

**Status:** Ready for Implementation
**Impact:** High (affects all future article generation)
**Breaking Changes:** No (additive only with migration path)
