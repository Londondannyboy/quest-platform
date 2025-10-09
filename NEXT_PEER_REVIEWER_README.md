# Next Peer Reviewer - Complete Context

## Quick Summary

**Status**: Live site broken - displaying raw markdown instead of HTML
**Articles**: 3 articles in database with hero + content images ✅
**Issue**: Images generated but not displaying on frontend ❌

## Test Article

**Latest**: https://relocation.quest/best-cafes-for-remote-work-in-lisbon-2025
- Created: 2025-10-09 00:03:26 UTC
- Database has: hero_image_url ✅, content_image_1_url ✅
- Live site shows: Raw markdown text (broken)

## Code Locations

### Backend (This Repo)
- **Location**: `~/quest-platform/backend/`
- **API**: `backend/app/api/articles.py`
- **Orchestrator**: `backend/app/agents/orchestrator.py`
- **Deployment**: Railway (auto-deploys on push)

### Frontend (Separate Repo - NOW CLONED)
- **Location**: `~/relocation-quest-clone/`
- **Article Template**: `src/pages/[slug].astro`
- **Package**: `package.json`
- **Deployment**: Vercel (auto-deploys on push)

## 3 Critical Bugs to Fix

### Bug #1: API Missing Image Columns
**File**: `backend/app/api/articles.py`
**Lines**: 153-156, 195-198, 269-272

**Current**:
```python
SELECT
    id, title, slug, content, excerpt,
    hero_image_url, target_site, status,
    ...
```

**Missing**: `content_image_1_url`, `content_image_2_url`, `content_image_3_url`

**Fix**: Add these 3 columns to ALL SELECT statements

---

### Bug #2: Orchestrator Not Saving Content Images
**File**: `backend/app/agents/orchestrator.py`
**Line**: ~238

**Current**: Only calls `_update_article_image()` for hero image

**Missing**: No UPDATE for content images after generation

**Fix**: Add UPDATE statements like:
```python
await conn.execute("""
    UPDATE articles 
    SET content_image_1_url = $1,
        content_image_2_url = $2,
        content_image_3_url = $3
    WHERE id = $4
""", img1_url, img2_url, img3_url, article_id)
```

---

### Bug #3: Markdown Not Parsing to HTML
**File**: `~/relocation-quest-clone/src/pages/[slug].astro`
**Line**: 26

**Current Code**:
```javascript
const htmlContent = await marked.parse(article.content);
```

**Problem**: Raw markdown showing on live site

**Debug Steps**:
1. Check `~/relocation-quest-clone/package.json` - is `marked` in dependencies?
2. Check Vercel build logs - did `marked` install?
3. Verify `set:html` directive working (line 83)
4. Test locally: `npm install && npm run dev`

---

## How to Test

### 1. Check Database
```bash
cd ~/quest-platform/backend
python3 -c "
import asyncio, asyncpg

async def check():
    conn = await asyncpg.connect('$NEON_CONNECTION_STRING')
    article = await conn.fetchrow('''
        SELECT slug, hero_image_url, content_image_1_url 
        FROM articles 
        ORDER BY created_at DESC LIMIT 1
    ''')
    print(f'Slug: {article[\"slug\"]}')
    print(f'Hero: {article[\"hero_image_url\"][:80]}...')
    print(f'Content1: {article[\"content_image_1_url\"][:80]}...')
    await conn.close()

asyncio.run(check())
"
```

### 2. Test Frontend Locally
```bash
cd ~/relocation-quest-clone
npm install
npm run dev
# Visit http://localhost:4321/best-cafes-for-remote-work-in-lisbon-2025
```

### 3. Check Vercel Deployment
```bash
cd ~/relocation-quest-clone
vercel logs --prod
```

---

## File Structure

```
~/quest-platform/              ← Backend (quest-platform repo)
├── backend/
│   ├── app/api/articles.py    ← Bug #1: Add content image columns
│   ├── app/agents/
│   │   └── orchestrator.py    ← Bug #2: Save content images
│   └── requirements.txt
├── PEER_REVIEW_BRIEF.md       ← Original issue documentation
└── PEER_REVIEW_ACTION_ITEMS.md ← Peer findings

~/relocation-quest-clone/      ← Frontend (relocation-quest repo)
├── src/pages/
│   └── [slug].astro           ← Bug #3: Markdown not parsing
├── package.json               ← Check `marked` dependency
└── vercel.json
```

---

## Expected Outcome After Fixes

Visit: https://relocation.quest/best-cafes-for-remote-work-in-lisbon-2025

**Should See**:
1. ✅ Hero image at top
2. ✅ Properly formatted HTML content (paragraphs, headings, lists)
3. ✅ Content image at bottom of article
4. ✅ Clickable links (internal + external)

**Currently Showing**:
1. ✅ Hero image (working)
2. ❌ Raw markdown text (`# Heading`, `**bold**`, etc.)
3. ❌ No content image
4. ❌ Links not clickable

---

## Deployment After Fixes

### Backend
```bash
cd ~/quest-platform/backend
git add .
git commit -m "fix: Add content image columns to API queries + save to DB"
git push origin main  # Auto-deploys to Railway
```

### Frontend
```bash
cd ~/relocation-quest-clone
git add .
git commit -m "fix: Ensure marked package installed + markdown parsing works"
git push origin main  # Auto-deploys to Vercel
```

---

## Environment Variables

Already configured in Railway + Vercel dashboards:

- `NEON_CONNECTION_STRING` (Database)
- `ANTHROPIC_API_KEY` (Claude)
- `CLOUDINARY_*` (Image storage)
- `TOGETHER_API_KEY` (Image generation)

No changes needed.

---

## Success Criteria

- [ ] API returns content image URLs
- [ ] Database has content image URLs saved
- [ ] Frontend renders markdown as HTML
- [ ] Content image displays at article bottom
- [ ] Live site works: https://relocation.quest/best-cafes-for-remote-work-in-lisbon-2025

---

## Previous Session Summary

**What I Did**:
- ✅ Created peer review brief
- ✅ Identified 3 critical bugs (via peer LLM)
- ✅ Generated 3 test articles with images
- ✅ Cloned frontend repo for debugging
- ❌ Did NOT fix bugs (ran out of time)

**What You Need to Do**:
1. Fix all 3 bugs listed above
2. Test locally
3. Deploy to production
4. Verify live site works

---

**Created**: 2025-10-09
**Last Updated**: 2025-10-09 01:29 UTC
**Repositories**: 
- Backend: https://github.com/Londondannyboy/quest-platform
- Frontend: https://github.com/Londondannyboy/relocation-quest
