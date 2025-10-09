# Quest Platform Restart Prompt

**Last Commit:** `05263c7` - "BullMQ worker deployed to Railway"
**Status:** 🟡 Worker deploying (check logs) | Vercel needs manual trigger
**Date:** October 9, 2025

---

## 🎯 Immediate Next Steps

### 1. Check BullMQ Worker Logs (2 mins)
**Railway project:** `bull_mq` (ID: 3cff0bbc-19a7-43a9-8804-056c906e7f53)

**Look for in logs:**
- ✅ `"worker.starting"`
- ✅ `"worker.ready"`
- ✅ Database connected
- ✅ Redis connected

**If no logs yet:** Wait 1-2 minutes for build to complete

**If errors:** Check environment variables are copied correctly

### 2. Trigger Vercel Redeploy (MANUAL - 2 mins)
**⚠️ MUST DO MANUALLY - Claude can't trigger Vercel**

1. Go to: https://vercel.com/londondannyboys-projects/relocation-quest
2. Click "Deployments" tab
3. Find latest deployment
4. Click "..." menu → "Redeploy"
5. Wait ~1 minute for deployment

**Why:** Frontend has `published_at` fix but hasn't auto-deployed

### 3. Verify Articles Live (after Vercel deploys)
Check these URLs:
- https://relocation.quest/portugal-golden-visa-2025-requirements-costs-application-guide
- https://relocation.quest/spain-digital-nomad-visa-requirements-and-application-process-2025
- https://relocation.quest/croatia-digital-nomad-visa-2025-complete-guide

---

## 💡 What BullMQ Worker Means

**HUGE UPGRADE** for production:

| Before (Synchronous) | After (BullMQ Worker) |
|---------------------|----------------------|
| ❌ 2-3 min = timeout | ✅ Instant API response |
| ❌ 1 article at a time | ✅ 100+ articles simultaneously |
| ❌ No retry on failure | ✅ Auto-retry with backoff |
| ❌ FastAPI blocks | ✅ Background processing |
| ❌ Can't scale | ✅ Add more workers = faster |

**Unlocks:**
- Batch generation (100+ articles overnight)
- Concurrent processing (5-10 articles at once)
- Job monitoring & progress tracking
- Production-grade reliability

---

## 🚀 Railway Setup

**Project: `bull_mq`** (BullMQ Worker)
- **ID:** 3cff0bbc-19a7-43a9-8804-056c906e7f53
- **Status:** ⏳ Deploying (check logs)
- **Start:** `python -m app.worker`
- **Root:** `backend`

**Project: `zoological-adaptation`** (Main API)
- **URL:** https://quest-platform-production-9ee0.up.railway.app
- **Status:** ✅ Running
- **TODO:** Rename to `quest-platform-api`

---

## ✅ Session Achievements

**Backend:**
1. Fixed LinkUp API parameters
2. Fixed auto-publish (`published_at` always set)
3. Published 3 test articles manually

**Frontend:**
4. Fixed schema (`published_date` → `published_at`)
5. Pushed redeploy trigger commit

**Infrastructure:**
6. ✅ BullMQ worker deployed to Railway
7. ✅ All environment variables configured
8. ✅ Worker code ready (`backend/app/worker.py`)

**Documentation:**
9. Slim restart prompt policy (<100 lines)
10. Policy documented in CLAUDE.md
11. Prompt: 325 → ~110 lines

---

## 🔧 Quick Commands

### Check Worker Health
```bash
curl https://quest-platform-production-9ee0.up.railway.app/api/health | jq .queue
# Should show "healthy" once worker running
```

### Generate Article
```bash
cd ~/quest-platform/backend
python3 generate_article.py --topic "Your topic" --site relocation
```

### Check Published Articles
```bash
curl -s "https://quest-platform-production-9ee0.up.railway.app/api/articles/?status=published" | python3 -c "import sys, json; print('\n'.join([a['title'] for a in json.load(sys.stdin)['articles']]))"
```

---

## ⚠️ Known Issues

1. **Critique Labs** - Not triggering (needs investigation)
2. **JSON Parsing** - ContentAgent returns malformed JSON (fallback works)
3. **Directus** - Configured locally, not deployed
4. **Worker Logs** - May take 1-2 mins to appear after deployment

---

## 📚 References

- **History:** CLAUDE.md (Peer Reviews #1-5)
- **Progress:** QUEST_TRACKER.md
- **Architecture:** QUEST_ARCHITECTURE_V2_3.md

---

**After Break:** Check worker logs → Trigger Vercel → Verify articles live
