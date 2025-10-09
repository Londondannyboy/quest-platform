# Quest Platform Restart Prompt

**Last Updated:** October 9, 2025 (Evening Session)
**Last Commit:** `48849fb` - "Fix critical peer review issues"
**Context:** 178k tokens used - Session ended addressing multi-API research chain

---

## ⚡ IMMEDIATE PRIORITY: Multi-API Research Chain

**CRITICAL ISSUE IDENTIFIED:** ResearchAgent only uses Perplexity - missing 5 other APIs

### The Problem (From Boring Marketer Video Analysis)
Current flow:
```
ResearchAgent → Perplexity ONLY → Cache → ContentAgent writes
```

Desired flow (like video):
```
1. Perplexity → Topic discovery
2. DataForSEO → Keyword validation + volume
3. Tavily → Additional sources
4. Firecrawl → Competitor scraping
5. Serper → SERP analysis
6. LinkUp → Link validation
7. Critique Labs → Fact checking
   ↓
Store in Neon → ContentAgent writes with ALL context
```

### Status Check
✅ All 5 API keys configured in .env:
- TAVILY_API_KEY
- SERPER_API_KEY
- LINKUP_API_KEY
- FIRECRAWL_API_KEY
- CRITIQUE_API_KEY

❌ NOT wired into ResearchAgent yet

### What Was Done This Session
1. ✅ Fixed Codex peer review issues (commit `48849fb`)
   - Job ID tracking (HIGH priority)
   - Orchestrator metadata return
   - Documentation accuracy
2. ✅ Committed and pushed to GitHub
3. 🔄 Started test article generation (Job ID: 06e8e942)
   - Topic: "Best Digital Nomad Visa Options for 2025"
   - Hit cache, skipped multi-API research
   - Currently generating content

---

## System Architecture

```
Backend: Railway (quest-platform-production-b8e3.up.railway.app)
Frontend: Vercel (relocation.quest)
Database: Neon (postgresql://neondb_owner@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb)
Queue: Redis + BullMQ
Storage: Cloudinary (images)
CMS: Directus (local development)
```

## Current Pipeline (4 Agents + LinkValidator)

```
ArticleOrchestrator
  ├── ResearchAgent (Perplexity ONLY - needs 5 more APIs)
  ├── LinkValidator (validates external URLs, suggests internal)
  ├── ContentAgent (Claude Sonnet 4.5)
  ├── EditorAgent (Quality scoring)
  └── ImageAgent (FLUX + Cloudinary)
```

**Note:** SEOAgent and PDFAgent are planned for TIER 1

---

## To Restart & Continue

```bash
# 1. Check if article finished generating
cd ~/quest-platform/backend
python3 -c "
import asyncio
import asyncpg

async def check():
    conn = await asyncpg.connect('postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require')

    articles = await conn.fetch('SELECT title, slug, quality_score FROM articles ORDER BY created_at DESC LIMIT 1')

    if articles:
        print(f\"Latest: {articles[0]['title']}\")
        print(f\"Quality: {articles[0]['quality_score']}/100\")
        print(f\"URL: https://relocation.quest/{articles[0]['slug']}\")

    await conn.close()

asyncio.run(check())
"

# 2. Implement Multi-API Research Chain
# Primary file: backend/app/agents/research.py
# Add methods for each API, chain them together
# Reference: backend/test_all_apis.py for API usage examples

# 3. Test with fresh article (no cache)
python3 ../generate_article.py --topic "New unique topic 2025"
```

---

## Key Files for Multi-API Implementation

- **backend/app/agents/research.py** - ResearchAgent (needs 5 API integrations)
- **backend/test_all_apis.py** - Working examples of all APIs
- **backend/.env** - All API keys configured
- **backend/app/core/config.py** - Settings management

---

## Documentation

- **QUEST_GENERATION.md** - Primary script documentation
- **QUEST_TRACKER.md** - Progress tracking (TIER 0 #2 = Research Chain)
- **CLAUDE.md** - Technical reference + peer review history
- **QUEST_ARCHITECTURE_V2_3.md** - Full architecture spec

---

## Next Steps (Priority Order)

1. **Implement Multi-API Research Chain** (TIER 0 #2)
   - Wire up 5 APIs into ResearchAgent
   - Create fallback chain (if one fails, use next)
   - Store results in Neon with embeddings

2. **Test End-to-End**
   - Generate article with fresh topic (force API calls)
   - Verify all 6 APIs are called
   - Check content quality improvement

3. **Measure Impact**
   - Compare articles: Perplexity-only vs Multi-API
   - Track quality scores
   - Validate "sounds less like Perplexity" concern

---

## Recent Commits

- `48849fb` - Fix critical peer review issues (job ID tracking, metadata, docs)
- `cfa3c30` - Previous session work
- See full history: `git log --oneline -10`

---

**REMINDER:** You're at 89% context (178k/200k tokens). Start fresh conversation focused on multi-API research chain implementation.
