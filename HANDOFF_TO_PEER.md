# Handoff to Peer LLM - Markdown Rendering Issue *(Status: Resolved Oct 9, 2025)*

> **Update (Codex, Oct 9, 2025):** Backend serialization hardened, malformed rows cleaned in Neon, and frontend updated. Markdown now renders correctly on live site. Original handoff notes retained below for historical context.

**Date:** 2025-10-09
**Status:** Content images ✅ working | Markdown rendering ❌ broken
**Handoff Reason:** Database contains truncated JSON instead of clean markdown

---

## What's Working ✅

1. **Content Images Displaying**
   - Hero image: ✅ Working
   - Content images at bottom: ✅ Working
   - API returns all image URLs correctly
   - Database has valid Cloudinary URLs

2. **Frontend Code**
   - `relocation-quest/src/pages/[slug].astro` has excellent JSON parsing logic (lines 38-96)
   - Handles IMAGE_PLACEHOLDER replacement
   - TL;DR and key takeaways rendering
   - `marked.parse()` configured correctly

3. **Backend API**
   - All 3 SELECT queries include content_image_1/2/3_url columns
   - `_serialize_article()` function exists and is called

---

## What's Broken ❌

### Issue: Markdown Displays as Raw Text (# ** --)

**Live Site:** https://relocation.quest/best-cafes-for-remote-work-in-lisbon-2025

**Symptoms:**
- Raw `#` symbols visible (not converted to `<h1>`)
- Raw `**bold**` asterisks visible (not converted to `<strong>`)
- Raw `-` bullet points (not converted to `<ul><li>`)

**Root Cause:** Database contains **truncated/invalid JSON strings**

---

## Technical Analysis

### What Railway API Currently Returns

```bash
curl https://quest-platform-production-b8e3.up.railway.app/api/articles/by-slug/best-cafes-for-remote-work-in-lisbon-2025
```

**Returns:**
```json
{
  "content": "{
  \"title\": \"Best Cafes for Remote Work in Lisbon 2025: Digital Nomad Guide\",
  \"tldr\": \"Lisbon's cafe culture makes it a digital nomad paradise, wit..."
  // ❌ TRUNCATED - not valid JSON!
}
```

**Expected:**
```json
{
  "content": "# Best Cafes for Remote Work in Lisbon 2025\n\nLisbon has become..."
  // ✅ Clean markdown string
}
```

### Why `_serialize_article()` Fails

**File:** `quest-platform/backend/app/api/articles.py`
**Lines:** 136-179

```python
def _serialize_article(row) -> Dict[str, Any]:
    article = dict(row)
    raw_content = article.get("content")
    structured = None

    if isinstance(raw_content, str):
        try:
            structured = json.loads(raw_content)  # ❌ FAILS - truncated JSON
        except json.JSONDecodeError:
            structured = None  # ❌ Silent failure

    if isinstance(structured, dict):  # ❌ Never True
        # Extract markdown from nested 'content' field
        markdown = structured.get("content")
        if isinstance(markdown, str):
            article["content"] = markdown

    return article  # ❌ Returns broken JSON string
```

**Problem:**
1. Database has `content` = `"{\"title\": \"...\", \"tldr\": \"...\"` (cut off mid-string)
2. `json.loads()` throws `JSONDecodeError`
3. Exception caught, `structured = None`
4. Never extracts markdown
5. Returns raw broken JSON to frontend

---

## The Fix (3 Options)

### Option 1: Fix Content Agent (RECOMMENDED)

**File:** `quest-platform/backend/app/agents/content.py`

**Current Behavior:** Returns JSON-wrapped content
**Desired Behavior:** Return ONLY markdown string

**Change:**
```python
# BEFORE
return {
    "article": {
        "title": "...",
        "content": "# Markdown here...",  # Nested
        ...
    }
}

# AFTER
return {
    "article": {
        "title": "...",
        "content": "# Markdown here...",  # Direct markdown
        ...
    }
}
```

Then update orchestrator to NOT serialize to JSON before saving to DB.

---

### Option 2: Make `_serialize_article()` More Robust

**File:** `quest-platform/backend/app/api/articles.py:136-179`

**Enhancement:**
```python
def _serialize_article(row) -> Dict[str, Any]:
    article = dict(row)
    raw_content = article.get("content")

    # Try to extract markdown from JSON-wrapped content
    if isinstance(raw_content, str) and raw_content.strip().startswith('{'):
        try:
            structured = json.loads(raw_content)
            if isinstance(structured, dict) and "content" in structured:
                article["content"] = structured["content"]
        except json.JSONDecodeError:
            # Try partial parsing with regex fallback
            import re
            match = re.search(r'"content":\s*"([^"]+)"', raw_content)
            if match:
                article["content"] = match.group(1)

    return article
```

---

### Option 3: Generate New Test Article

**Simplest Fix:** Generate a fresh article with clean markdown

```bash
cd ~/quest-platform/backend
python3 -c "
import asyncio
from app.core.database import get_db

async def fix():
    pool = get_db()
    async with pool.acquire() as conn:
        # Get one article and check its content
        article = await conn.fetchrow(
            'SELECT id, content FROM articles WHERE slug = \$1',
            'best-cafes-for-remote-work-in-lisbon-2025'
        )
        print('Current content length:', len(article['content']))
        print('Starts with:', article['content'][:100])

asyncio.run(fix())
"
```

Then generate a new article and verify it stores clean markdown.

---

## Test Plan

1. **Verify Database Content**
   ```sql
   SELECT LEFT(content, 200) FROM articles
   WHERE slug = 'best-cafes-for-remote-work-in-lisbon-2025';
   ```

2. **Test API Response**
   ```bash
   curl https://quest-platform-production-b8e3.up.railway.app/api/articles/by-slug/best-cafes-for-remote-work-in-lisbon-2025 | jq '.content[:200]'
   ```

3. **Verify Frontend Rendering**
   - Visit: https://relocation.quest/best-cafes-for-remote-work-in-lisbon-2025
   - Should see: Proper `<h1>`, `<strong>`, `<ul>` tags
   - Should NOT see: Raw `#`, `**`, `-` symbols

---

## Files to Review

### Backend
- `quest-platform/backend/app/agents/content.py` - Content generation
- `quest-platform/backend/app/api/articles.py:136-179` - Serialization
- `quest-platform/backend/app/agents/orchestrator.py:305-363` - Article creation

### Frontend
- `relocation-quest/src/pages/[slug].astro:38-96` - JSON parsing (already excellent!)

---

## Success Criteria

- [ ] API returns `content` as clean markdown string (starts with `#`, not `{`)
- [ ] Frontend displays formatted HTML (no raw `#` or `**`)
- [ ] Content images still display at bottom
- [ ] TL;DR and key takeaways still render

---

## Deployment

**Backend:** Railway auto-deploys on push to `main`
**Frontend:** Vercel auto-deploys on push to `main`

Both are already configured and working - just need clean data!

---

**Good luck!** The frontend code is perfect - this is purely a backend data quality issue.
