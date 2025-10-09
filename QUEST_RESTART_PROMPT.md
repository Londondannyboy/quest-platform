# Quest Platform Restart Prompt

**Last Commit:** `015ab49` - "Update restart prompt: Railway incident resolved"
**Railway:** ✅ Backend + BullMQ Worker deployed
**Vercel:** ⏳ Needs manual redeploy
**Date:** October 9, 2025

---

## 🎯 Current Priorities

### 1. **Verify BullMQ Worker Running** (5 mins)
**Worker deployed to Railway project `bull_mq`**

Check logs for:
- ✅ `"worker.starting"`
- ✅ `"worker.ready"`
- ✅ Redis connection successful
- ✅ Database connection successful

**Health check should show queue healthy:**
```bash
curl https://quest-platform-production-9ee0.up.railway.app/api/health
# Should show "queue": "healthy" (not "unhealthy")
```

### 2. **Trigger Vercel Redeploy** (2 mins)
**Frontend has schema fix but hasn't auto-deployed**

- Go to: https://vercel.com/londondannyboys-projects/relocation-quest
- Click "Redeploy" on latest deployment
- **Result:** 3 test articles will appear on relocation.quest

### 3. **Verify Articles Live** (5 mins)
After Vercel redeploys:
- https://relocation.quest/portugal-golden-visa-2025-requirements-costs-application-guide
- https://relocation.quest/spain-digital-nomad-visa-requirements-and-application-process-2025
- https://relocation.quest/croatia-digital-nomad-visa-2025-complete-guide

---

## 🚀 Railway Projects

**Project: `bull_mq`** (NEW - BullMQ Worker)
- **ID:** 3cff0bbc-19a7-43a9-8804-056c906e7f53
- **Service:** Worker process polling Redis queue
- **Start Command:** `python -m app.worker`
- **Root Directory:** `backend`

**Project: `zoological-adaptation`** (Main Backend)
- **Service:** FastAPI REST API
- **URL:** https://quest-platform-production-9ee0.up.railway.app
- **TODO:** Rename to `quest-platform-api` for clarity

---

## ✅ This Session's Achievements

### Backend Fixes
1. LinkUp API parameters (`"q"` + `"depth": "deep"`)
2. Auto-publish logic (always set `published_at` when decision="publish")
3. Manually published 3 test articles in database

### Frontend Fixes
4. Schema fix: `published_date` → `published_at`
5. Pushed empty commit to force Vercel redeploy

### Infrastructure
6. ✅ **BullMQ Worker deployed** to Railway (`bull_mq` project)
7. Worker configured with all environment variables
8. Ready for true async article generation

### Documentation
9. Slim restart prompt policy (<100 lines)
10. Documented policy in CLAUDE.md
11. Restart prompt: 325 → ~100 lines

---

## 🔧 Quick Commands

### Generate Article (will use worker if queue healthy)
```bash
cd ~/quest-platform/backend
python3 generate_article.py --topic "Your topic" --site relocation
```

### Check Queue Health
```bash
curl https://quest-platform-production-9ee0.up.railway.app/api/health | jq
```

### Check Published Articles
```bash
curl -s "https://quest-platform-production-9ee0.up.railway.app/api/articles/?status=published" | python3 -c "import sys, json; print('\n'.join([a['title'] for a in json.load(sys.stdin)['articles']]))"
```

---

## ⚠️ Known Issues

1. **Critique Labs** - Not triggering (API key set, integration not calling)
2. **JSON Parsing** - ContentAgent returning malformed JSON (fallback works)
3. **Directus** - Configured locally, not deployed

---

## 📚 References

- **Full History:** CLAUDE.md
- **Progress:** QUEST_TRACKER.md
- **Architecture:** QUEST_ARCHITECTURE_V2_3.md

---

**Next Session:** Verify worker running + trigger Vercel redeploy + see articles live
