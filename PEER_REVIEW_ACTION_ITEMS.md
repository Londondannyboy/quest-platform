# Peer Review - Action Items

## Summary

Peer LLM identified 3 critical bugs preventing content images from displaying:

### Bug #1: API Missing Content Image Columns ✅ (Can Fix)
**Location**: `backend/app/api/articles.py`
**Lines**: 153-156 (by-slug), 195-198 (by-id), 269-272 (list)

**Problem**: All SELECT queries omit:
- `content_image_1_url`
- `content_image_2_url` 
- `content_image_3_url`

**Fix**: Add these 3 columns to every SELECT statement

**Impact**: Frontend ALWAYS receives null for content images, so conditional rendering never triggers

---

### Bug #2: Orchestrator Never Persists Content Images ❌ (Needs Investigation)
**Location**: `backend/app/agents/orchestrator.py:238`

**Problem**: Only `_update_article_image()` called for hero image. No equivalent for content images.

**Current Code**:
```python
# Only saves hero image
await self._update_article_image(article_id, image_result["hero_url"])
```

**Missing**: UPDATE for `content_image_1_url`, `content_image_2_url`, `content_image_3_url`

**Impact**: Even if API queries fixed, database has NULL values

---

###Bug #3: Frontend Code Not in Workspace ❌ (Blocker)
**Location**: `~/relocation-quest/` (separate repo)

**Problem**: Cannot debug markdown parsing without actual Astro code

**Required**: 
1. Sync `londondannyboy/relocation-quest` repo locally
2. Verify `marked` package in `package.json`
3. Check Vercel build logs for dependency installation
4. Investigate why `set:html` directive not working

---

## Recommended Fix Order

1. ✅ Fix API queries (15 min)
2. ❌ Fix orchestrator to save content images (30 min - needs code review)
3. ❌ Sync frontend repo and debug markdown parsing (45 min)
4. ✅ Test end-to-end
5. ✅ Deploy to Railway + Vercel

---

## Current Status

- **Backend Code**: In workspace ✅
- **Frontend Code**: Missing from workspace ❌
- **Deployment**: Both live but broken ⚠️
- **Peer Review Brief**: Created ✅

---

## Next Session Goals

1. Fix all 3 bugs
2. Generate test article
3. Verify images + markdown work on live site
4. Close this issue permanently

---

**Created**: 2025-10-09
**Reviewer**: Claude Sonnet (Peer LLM)
**Original Implementation**: Claude Sonnet 3.5
