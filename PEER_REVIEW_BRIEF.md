# Quest Platform - Peer Review Brief

## Context
AI-powered SEO content platform that generates high-quality articles with images for relocation/digital nomad websites. The system uses Claude Sonnet 3.5 for content generation and FLUX Schnell for image generation.

## Current Status

### ✅ What's Working
1. **Backend Article Generation** (Python/FastAPI on Railway)
   - Research agent successfully gathers data via Perplexity API
   - Content agent generates well-formatted markdown articles (14K+ chars)
   - Quality scoring (82/100 on test articles)
   - Image generation via Together AI's FLUX Schnell API
   - Cloudinary image storage with proper URL-safe slugs
   - PostgreSQL database (Neon) stores all data correctly

2. **Image Pipeline**
   - Hero image: ✅ Generated and uploaded to Cloudinary
   - Content images (3): ✅ Generated and uploaded to Cloudinary
   - Database schema includes: `hero_image_url`, `content_image_1_url`, `content_image_2_url`, `content_image_3_url`
   - All 4 images visible in Cloudinary console
   - URLs stored correctly in database

3. **Frontend** (Astro/Vercel)
   - Fetches articles from Neon database
   - Hero image displays correctly
   - Markdown parsed with `marked` library
   - Tailwind Typography (`prose` classes) for styling

### ❌ CRITICAL ISSUES (Live Site Broken)

#### Issue #1: Markdown NOT Parsing to HTML
**Problem**: The article content is displaying as RAW TEXT instead of parsed HTML. Markdown syntax is visible to users.

**Evidence** (Screenshot from https://relocation.quest/best-cafes-for-remote-work-in-lisbon-2025):
```
# Best Cafes for Remote Work in Lisbon... (visible as text)
**bold text** (visible as asterisks)
- bullet points (visible as dashes)
```

**Frontend Code** (`relocation-quest/src/pages/[slug].astro` lines 25-26):
```javascript
// Parse markdown to HTML
const htmlContent = await marked.parse(article.content);
```

**Root Cause**: UNKNOWN - Code looks correct but Vercel deployment is NOT executing markdown parsing
- Local code has `marked.parse()` ✅
- Deployed to Vercel 10 minutes ago ✅
- Still showing raw markdown ❌

**Possible Causes**:
1. Vercel build cache not clearing
2. `marked` package not installed in deployment
3. Astro `set:html` directive not working
4. Deployment using old code

#### Issue #2: Content Image Missing from Bottom of Article
**Problem**: No content image showing at article bottom despite being in database.

**Frontend Code** (`relocation-quest/src/pages/[slug].astro` lines 87-96):
```javascript
<!-- Single Content Image at Bottom -->
{article.content_image_1_url && (
  <figure class="my-12 not-prose">
    <img
      src={article.content_image_1_url}
      alt={article.title}
      class="w-full h-96 object-cover rounded-lg shadow-lg"
      loading="lazy"
    />
  </figure>
)}
```

**Database Status**: content_image_1_url EXISTS ✅
**Display Status**: Image NOT showing ❌

**Test Article**: https://relocation.quest/best-cafes-for-remote-work-in-lisbon-2025
- Hero image: ✅ Working correctly
- Markdown parsing: ❌ BROKEN (raw text visible)
- Content image at bottom: ❌ Not showing

---

## Technical Stack

### Backend (Railway)
- **Language**: Python 3.9+
- **Framework**: FastAPI
- **Database**: PostgreSQL (Neon)
- **AI**: Claude Sonnet 3.5 (Anthropic), FLUX Schnell (Together AI)
- **Storage**: Cloudinary
- **Location**: `~/quest-platform/backend/`
- **Key Files**:
  - `app/agents/orchestrator.py` - Main article generation orchestration
  - `app/agents/image_agent.py` - Image generation with FLUX
  - `app/agents/content_agent.py` - Markdown content generation
  - `app/core/database.py` - Database connection

### Frontend (Vercel)
- **Framework**: Astro 5.0
- **Styling**: Tailwind CSS + Tailwind Typography
- **Markdown**: `marked` library
- **Location**: `~/relocation-quest/`
- **Key Files**:
  - `src/pages/[slug].astro` - Article template
  - `src/lib/api.ts` - Database queries
  - `tailwind.config.mjs` - Tailwind configuration

### Database Schema
```sql
CREATE TABLE articles (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,  -- Markdown format
    hero_image_url TEXT,    -- Cloudinary URL
    content_image_1_url TEXT,
    content_image_2_url TEXT,
    content_image_3_url TEXT,
    quality_score INTEGER,
    reading_time_minutes INTEGER,
    meta_title TEXT,
    meta_description TEXT,
    keywords TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    published_date TIMESTAMPTZ
);
```

---

## Peer Review Tasks

### Task 1: CRITICAL - Fix Markdown Parsing
**Goal**: Make markdown parse to HTML on live site

**Current Diagnosis**:
- Code shows `marked.parse()` ✅
- Deployed to Vercel ✅
- Still showing raw markdown ❌

**Investigation Steps**:
1. Check `package.json` - is `marked` listed in dependencies?
2. Check Vercel build logs - did `marked` install correctly?
3. Verify `set:html` directive is working in Astro
4. Check if there's a build/deploy mismatch (cache issue)
5. Try adding `marked` import debugging

**Files to Investigate**:
- `relocation-quest/package.json` (dependencies)
- `relocation-quest/src/pages/[slug].astro` (lines 1-5 imports, line 26 parsing)
- Vercel deployment logs

**Debugging Steps to Try**:
1. Check if `marked` is in package.json dependencies
2. Add console.log before/after `marked.parse()`
3. Check if `htmlContent` contains HTML or markdown
4. Verify Vercel build installed dependencies correctly
5. Force clear Vercel cache and redeploy

### Task 2: Fix Content Image Display
**Goal**: Show content image at bottom of article

**Current Code** (lines 87-96 of [slug].astro):
```javascript
{article.content_image_1_url && (
  <figure class="my-12 not-prose">
    <img src={article.content_image_1_url} .../>
  </figure>
)}
```

**Diagnosis Needed**:
1. Is `article.content_image_1_url` populated from database?
2. Is the conditional rendering working?
3. Is the image URL valid?

**Success Criteria** (Both Tasks):
- Visit https://relocation.quest/best-cafes-for-remote-work-in-lisbon-2025
- Should see **properly formatted HTML content** (no raw markdown) ✅
- Should see **content image at article bottom** ✅
- Hero image should still work ✅

---

## Test Data

**Test Article Database Record**:
- **Slug**: `best-cafes-for-remote-work-in-lisbon-2025`
- **Hero Image**: https://res.cloudinary.com/...best-cafes-for-remote-work-in-lisbon-2025-hero.jpg
- **Content Image 1**: https://res.cloudinary.com/...best-cafes-for-remote-work-in-lisbon-2025-content-1.jpg
- **Content Image 2**: https://res.cloudinary.com/...best-cafes-for-remote-work-in-lisbon-2025-content-2.jpg
- **Content Image 3**: https://res.cloudinary.com/...best-cafes-for-remote-work-in-lisbon-2025-content-3.jpg

**Content Sample** (first 500 chars):
```markdown
# Best Cafes for Remote Work in Lisbon: 2025 Digital Nomad Guide

Lisbon has become one of Europe's premier destinations for remote workers and digital nomads, offering an ideal combination of affordable living costs, vibrant culture, and excellent infrastructure. The city's cafe scene has adapted to meet the needs of location-independent professionals, with establishments offering high-speed Wi-Fi, comfortable seating, power outlets, and a welcoming atmosphere for extended work sessions...
```

---

## Deployment Info

**Backend**: https://quest-platform-production-b8e3.up.railway.app
- Railway auto-deploys on git push to main branch
- Environment variables configured in Railway dashboard

**Frontend**: https://relocation.quest (Vercel)
- Vercel auto-deploys on git push to main branch
- Connected to GitHub repo: `londondannyboy/relocation-quest`

**Database**: Neon PostgreSQL
- Connection string in environment variables
- Direct psql access available

---

## Previous Attempts & Learnings

1. ✅ Fixed Cloudinary slug to be URL-safe (removed `:` and `&` characters)
2. ✅ Changed orchestrator to generate images for ALL articles (not just quality > 85)
3. ✅ Confirmed images are generated and uploaded successfully
4. ✅ Confirmed markdown content is stored correctly in database
5. ✅ Confirmed hero image displays correctly
6. ❌ Content images still not appearing in article body
7. ❌ Markdown formatting needs improvement

---

## Questions for Peer Reviewer

1. What's the best pattern for injecting 3 images into varying-length markdown articles?
2. Should we switch to a placeholder approach in the content generation phase?
3. Are there Tailwind Typography configuration issues?
4. Should we use a different markdown parser (e.g., remark/rehype)?

---

## Success Definition

**Minimal Success**:
- Content images (3) display throughout article
- Markdown has proper paragraph spacing
- Links are clickable
- Hero image continues to work

**Full Success**:
- All of above ✅
- Images positioned naturally at logical breaks
- Typography matches professional blog standards
- Code is maintainable and scalable

---

## How to Test

1. **Backend**:
   ```bash
   cd ~/quest-platform/backend
   python3 generate_final_demo.py
   ```

2. **Check Database**:
   ```bash
   psql $NEON_CONNECTION_STRING -c "SELECT slug, hero_image_url IS NOT NULL, content_image_1_url IS NOT NULL FROM articles ORDER BY created_at DESC LIMIT 1"
   ```

3. **View Article**:
   - Open https://relocation.quest/best-cafes-for-remote-work-in-lisbon-2025
   - Inspect for content images
   - Check paragraph spacing

---

## Priority
**HIGH** - Blocks production launch. Images are generated and paid for but not displaying to users.

---

## Contact
This brief created for LLM peer review. Original implementation by Claude Sonnet 3.5.

Last Updated: 2025-10-09
