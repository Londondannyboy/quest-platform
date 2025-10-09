# Quest Platform Restart Prompt

**Last Commit:** `98175ef` - "Document restart prompt policy in CLAUDE.md"
**Railway:** ✅ Deployed | **Vercel:** ⏳ Needs manual redeploy
**Date:** October 9, 2025

---

## 🎯 Current Priorities

### 1. **Deploy BullMQ Worker to Railway** (30 mins - NOW POSSIBLE!)
**Railway incident RESOLVED - can now create services**

**Steps:**
1. Go to Railway project: `quest-platform-production`
2. Click "+ New" → "Service" → "GitHub Repo" → `Londondannyboy/quest-platform`
3. Configure:
   - **Name:** `quest-worker`
   - **Root Directory:** `backend`
   - **Start Command:** `python -m app.worker`
   - **Environment Variables:** Copy ALL from main service
4. Deploy → Watch logs for `"worker.ready"`

### 2. **Trigger Vercel Redeploy** (2 mins)
**Frontend has schema fix but hasn't deployed**

- Go to: https://vercel.com/londondannyboys-projects/relocation-quest
- Click "Redeploy" on latest deployment
- **Why:** Pick up `published_at` schema fix (was `published_date`)
- **Result:** 3 test articles will appear on relocation.quest

### 3. **Verify Articles Live** (5 mins)
After Vercel redeploys, check:
- https://relocation.quest/portugal-golden-visa-2025-requirements-costs-application-guide
- https://relocation.quest/spain-digital-nomad-visa-requirements-and-application-process-2025
- https://relocation.quest/croatia-digital-nomad-visa-2025-complete-guide

---

## ✅ This Session's Achievements

### Fixed (Backend)
1. LinkUp API parameters (`"q"` + `"depth": "deep"`)
2. Auto-publish logic (always set `published_at` when decision="publish")
3. Manually published 3 test articles in database

### Fixed (Frontend)
4. Schema fix: `published_date` → `published_at`
5. Pushed empty commit to force Vercel redeploy

### Documentation
6. Created slim restart prompt policy (<100 lines)
7. Documented policy in CLAUDE.md
8. Reduced restart prompt: 325 → 85 lines

---

## 🔧 Quick Commands

### Generate Article
```bash
cd ~/quest-platform/backend
python3 generate_article.py --topic "Your topic" --site relocation
```

### Check Published Articles
```bash
curl -s "https://quest-platform-production-9ee0.up.railway.app/api/articles/?status=published" | python3 -c "import sys, json; print('\n'.join([a['title'] for a in json.load(sys.stdin)['articles']]))"
```

### Manually Publish Article (when Directus not available)
```python
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

## ⚠️ Known Issues

1. **Critique Labs** - Not triggering despite ≥70 scores (API key set but integration not calling)
2. **JSON Parsing** - ContentAgent returning malformed JSON (fallback works)
3. **Directus** - Configured locally but not deployed (needs Railway service)

---

## 📚 References

- **Full History:** CLAUDE.md (Peer Reviews #1-5)
- **Progress:** QUEST_TRACKER.md
- **Architecture:** QUEST_ARCHITECTURE_V2_3.md

---

**Next Session:** Deploy BullMQ worker + verify frontend articles live
