# Quest Platform Restart Prompt

**Last Commit:** `cbc42cb` - "Fix: Always publish articles with decision='publish'"
**Railway:** ✅ Deployed
**Vercel:** ⏳ Pending redeploy (manual trigger needed)
**Date:** October 9, 2025

---

## 🎯 Current Priorities

### 1. **Manual: Trigger Vercel Redeploy** (5 mins)
- Go to: https://vercel.com/londondannyboys-projects/relocation-quest
- Click "Redeploy" to pick up `published_at` schema fix
- **Why:** Frontend using old `published_date` field, needs `published_at`

### 2. **Deploy BullMQ Worker** (30 mins - BLOCKED)
- **Status:** Railway GitHub incident blocking new services
- **Code:** Ready in `backend/app/worker.py`
- **Action:** Wait for Railway incident to clear, then create separate service

### 3. **Deploy Directus CMS** (BLOCKED)
- **Status:** Configured locally in `directus/`, not on Railway
- **Action:** Deploy when Railway incident clears
- **Why:** Need UI for publishing workflow (currently manual DB updates)

### 4. **Generate Test Articles** (DONE - 3 articles)
- ✅ Portugal Golden Visa (score: 82)
- ✅ Spain Digital Nomad Visa (score: 82)
- ✅ Croatia Digital Nomad Visa (score: 82)
- ⚠️ Not visible on frontend until Vercel redeploys

---

## 🔧 Quick Commands

### Generate Article
```bash
cd ~/quest-platform/backend
python3 generate_article.py --topic "Your topic" --site relocation
```

### Check Published Articles (API)
```bash
curl -s "https://quest-platform-production-9ee0.up.railway.app/api/articles/?status=published"
```

### Manually Publish Article (SQL)
```python
# When Directus not available
python3 << EOF
import asyncio, asyncpg
async def publish():
    conn = await asyncpg.connect("postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require")
    await conn.execute("UPDATE articles SET status='published', published_at=NOW() WHERE title='ARTICLE_TITLE'")
    await conn.close()
asyncio.run(publish())
EOF
```

---

## 📋 Issues This Session

### ✅ Fixed
1. LinkUp API parameters (`"q"` + `"depth": "deep"`)
2. Frontend schema (`published_date` → `published_at`)
3. Backend auto-publish (always set `published_at` when decision="publish")

### ⚠️ Open
1. Critique Labs not triggering (despite ≥70 scores)
2. JSON parsing errors in ContentAgent (fallback works)
3. Vercel not auto-deploying from GitHub push

---

## 📚 References

- **Full History:** See CLAUDE.md (Peer Reviews #1-5)
- **Progress Tracking:** See QUEST_TRACKER.md
- **Architecture:** See QUEST_ARCHITECTURE_V2_3.md

---

**Next Session:** Trigger Vercel redeploy manually, then verify articles live on relocation.quest
