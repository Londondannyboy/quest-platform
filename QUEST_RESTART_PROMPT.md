# Quest Platform - Session Restart Guide
**Date:** October 9, 2025 | **Version:** 2.7
**Status:** ✅ Production - Article generation working end-to-end

---

## 🎯 CURRENT STATE

### ✅ Production (Live)
- **Site:** https://relocation.quest (3+ articles published)
- **API:** https://quest-platform-production-b8e3.up.railway.app
- **Database:** Neon PostgreSQL with 4-image pipeline
- **Cost:** $0.44/article | **Time:** 2-3 min/article
- **Success Rate:** 100%

### ⚠️ Known Issues (Non-Blocking)
1. **Schema Mismatch** - Content agent returns JSON, DB expects markdown (has adapter workaround)
2. **Only 1 of 6 Research APIs** - Perplexity only (missing Tavily, Firecrawl, SERP.dev, Critique Labs, Link Up)
3. **No Queue System** - Synchronous execution (won't scale past 100 articles)
4. **Directus Not Deployed** - No CMS/HITL workflow yet
5. **GraphQL Not Implemented** - Using direct SQL queries (simpler for now)

---

## 📚 DOCUMENTATION (7 Core Files)

```
quest-platform/
├── QUEST_ARCHITECTURE_V2_3.md     ← Complete system architecture
├── QUEST_SEO.md                   ← Complete SEO strategy (LLM-first, technical, content)
├── QUEST_RELOCATION_RESEARCH.md   ← Content strategy & topic queue (OPERATIONAL)
├── QUEST_PEER_REVIEW.md           ← Peer review guide
├── QUEST_RESTART_PROMPT.md        ← This file (quick reference)
├── QUEST_TRACKER.md                ← Progress tracking
└── CLAUDE.md                       ← Technical reference + history
```

**For detailed architecture, costs, schemas, etc:** Read `QUEST_ARCHITECTURE_V2_3.md`
**For SEO strategy, LLM optimization, technical setup:** Read `QUEST_SEO.md`
**For content strategy & article queue:** Read `QUEST_RELOCATION_RESEARCH.md`

---

## 🚀 QUICK COMMANDS

### Generate Test Article
```bash
cd ~/quest-platform/backend && python3 generate_full_article.py
```

### Check Latest Articles
```bash
NEON_CONNECTION_STRING="postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require" \
psql -c "SELECT id, title, slug, status FROM articles ORDER BY created_at DESC LIMIT 3;"
```

### Deploy
```bash
# Backend (Railway auto-deploys)
cd ~/quest-platform && git add . && git commit -m "Update" && git push

# Frontend (Vercel auto-deploys)
cd ~/relocation-quest && git add . && git commit -m "Update" && git push
```

---

## 🔗 QUICK LINKS

**Production:**
- Site: https://relocation.quest
- API: https://quest-platform-production-b8e3.up.railway.app/api/health

**Dashboards:**
- Railway: https://railway.app/
- Vercel: https://vercel.com/londondannyboys-projects/relocation-quest
- Neon: https://console.neon.tech/
- Cloudinary: https://cloudinary.com/console

**GitHub:**
- Backend: https://github.com/Londondannyboy/quest-platform
- Frontend: https://github.com/Londondannyboy/relocation-quest

---

## 🎯 NEXT SESSION OPTIONS

### OPTION 1: Research Governance (TIER 0 - CRITICAL)
**Status:** Codex Peer Review finding (Oct 9, 2025)
**Priority:** HIGHEST - Implement before generating more articles
**Time:** 3-4 hours
**Impact:** Connects content strategy (993 topics) to execution, reduces duplicate costs

1. Create `backend/app/core/research_queue.py` - Parse QUEST_RELOCATION_RESEARCH.md
2. Update `backend/app/agents/research.py` - Add pre-flight checks before Perplexity
3. Test with existing topics

### OPTION 2: Generate High-Value Articles
Run production pipeline to publish 10-20 articles and validate research governance.

### OPTION 3: TIER 1 Technical Improvements (After 20 articles)
1. **TaskMaster AI Integration** (4-5h) - Task orchestration + dependency enforcement (npm: `task-master-ai`)
2. **GitHub Spec Kit Integration** (3-4h) - Runtime schema validation (npm: `@github/spec-kit`)
3. **Cost Monitoring Dashboard** (2-3h) - Add `/api/metrics/*` endpoints
4. **BullMQ Worker** (4-5h) - Fix worker.py, deploy to Railway
5. **Fix Schema Mismatch** (2-3h) - Content agent returns plain markdown
6. **Integrate Missing APIs** (6-8h) - Add Tavily, Firecrawl, SERP.dev

### OPTION 4: Deploy Directus CMS (TIER 1)
**Time:** 3-4 hours
**Prerequisite:** 20+ articles in database

---

## 🤖 4-AGENT PIPELINE STATUS

```
ResearchAgent → ContentAgent → EditorAgent → ImageAgent
   30-60s          60-90s         20-30s        60s (parallel)

   ✅ Perplexity   ✅ Claude 4.5  ✅ Quality    ✅ FLUX
   ❌ Tavily       ⚠️ JSON bug   ✅ Scoring    ✅ Cloudinary
   ❌ Firecrawl                  ❌ Fact-check
   ❌ SERP.dev
   ❌ Critique
   ❌ Link Up
```

---

## 💰 COST (Current)

- **Infrastructure:** $80/month (Neon $50 + Railway $30)
- **AI APIs:** $355/month at 1000 articles (Perplexity $300, Claude $52.50, FLUX $3)
- **Cost Per Article:** $0.44 ✅ (target: <$0.50)

---

## 📊 DATABASE SCHEMA (Quick Ref)

```sql
articles (
  id UUID PRIMARY KEY,
  title TEXT,
  slug TEXT UNIQUE,
  content TEXT,                    -- ⚠️ Plain markdown expected
  hero_image_url TEXT,             -- ✅ Working
  content_image_1_url TEXT,        -- ✅ Working
  content_image_2_url TEXT,        -- ✅ Working
  content_image_3_url TEXT,        -- ✅ Working
  target_site VARCHAR(50),         -- relocation/placement/rainmaker
  status VARCHAR(20),              -- draft/review/published
  quality_score INTEGER
)

article_research (
  embedding vector(1536),          -- pgvector cache
  research_json JSONB,
  expires_at TIMESTAMPTZ
)

job_status (
  job_id VARCHAR(255) PRIMARY KEY,
  article_id UUID,
  cost_breakdown JSONB,
  total_cost DECIMAL(10,4)
)
```

---

## ✅ RECENT UPDATES (Oct 9, 2025)

**V2.8 Session - Documentation Cleanup + Codex Peer Review:**
- ✅ Deleted 19 redundant files (docs/archive, runbooks, scripts, migrations)
- ✅ Deleted ~/quest-platform/frontend/ stub folder
- ✅ Unified 9 SEO docs → QUEST_SEO.md
- ✅ Added QUEST_RELOCATION_RESEARCH.md cross-references
- ✅ Codex peer review integrated (7/10 overall score)
- ✅ Research governance identified as TIER 0 priority
- ✅ Confirmed separate-repo architecture (not Turborepo) is correct
- ✅ Context reduction: ~12,500 tokens saved (55% reduction in doc overhead)

**V2.7 Session:**
- ✅ Fixed JSONB bug in orchestrator.py (json.dumps for cost_breakdown)
- ✅ Killed 18 ghost background process trackers
- ✅ Compacted restart prompt (12KB → 6KB)

---

**For detailed information:** Read `QUEST_ARCHITECTURE_V2_3.md`
**For progress tracking:** Read `QUEST_TRACKER.md`
**For technical history:** Read `CLAUDE.md`
