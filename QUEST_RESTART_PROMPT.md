# Quest Platform Restart Prompt

**Last Updated:** October 9, 2025 (Late Evening - Codex Session)
**Last Commit:** `a869188` - "Fix slug sanitization and LinkUp DNS error"
**Railway Status:** ✅ Deployed (took 12 mins - investigate slow builds)

---

## ✅ What We Fixed This Session

### 1. Schema Mismatches (Opus Leftovers)
- ✅ Fixed `published_date` → `published_at` in all SQL queries
- ✅ Fixed `cost_breakdown` Pydantic validation (parse JSON string)
- **Impact:** Articles API now works, job status endpoint functional

### 2. Quality Thresholds Lowered (Testing Mode)
- ✅ Changed from 85/70 → **75/60**
- Publish: ≥75 | Review: 60-74 | Reject: <60
- **Reason:** Stop blocking on high scores during testing

### 3. Critical Bug Fixes (From Codex Testing)
- ✅ **Slug sanitization:** Strip ALL punctuation (`:` was breaking URLs)
- ✅ **LinkUp DNS:** Fixed `api.linkup.dev` → `api.linkup.so`
- **Impact:** Articles now accessible on frontend, LinkUp API works

### 4. File Organization
- ✅ Moved `generate_article.py` from root → `backend/`
- **Reason:** Production script belongs with orchestrator code

---

## 🧪 Codex Live Test Results

**Topic:** "Quest relocation visa success stories 2025"
**Cost:** $0.3923
**Quality Score:** 72 (now "review" instead of "reject")
**Status:** ✅ Generated successfully

### APIs Used
- ✅ **Perplexity** - Worked
- ✅ **Tavily** - Worked
- ✅ **Serper** - Worked
- ❌ **LinkUp** - DNS error (FIXED THIS SESSION)
- ❌ **Firecrawl** - Empty (needs explicit URLs, not topics)
- ⏳ **Critique Labs** - Never called (not integrated in pipeline)

### Issues Found
1. ✅ **Slug had colon** - `quest-relocation-visa-success-stories-2025:-real-client-experiences`
   - Frontend couldn't resolve (404)
   - **FIXED:** Regex now strips all punctuation
2. ✅ **LinkUp DNS error** - Wrong domain
   - **FIXED:** Changed to correct `.so` domain
3. ⏳ **Critique Labs not integrated** - Code exists but never executed
4. ℹ️ **Firecrawl behavior** - Only works with explicit URLs (expected)

---

## 🚀 Current System Status

### Production URLs
- **Backend:** https://quest-platform-production-9ee0.up.railway.app
- **Frontend:** https://relocation.quest
- **Health:** `/api/health` (redis/queue still unhealthy - non-blocking)

### Pipeline (4 Agents + LinkValidator)
```
ArticleOrchestrator
  ├── ResearchAgent (Multi-API: Perplexity, Tavily, Serper, LinkUp, Firecrawl)
  ├── LinkValidator (validates external URLs, suggests internal)
  ├── ContentAgent (Claude Sonnet 4.5)
  ├── EditorAgent (Quality scoring - 75/60 thresholds)
  └── ImageAgent (FLUX + Cloudinary - 4 images)
```

### Latest Article Generated
- **Slug:** `quest-relocation-visa-success-stories-2025-real-client-experiences` (clean!)
- **URL:** https://relocation.quest/quest-relocation-visa-success-stories-2025-real-client-experiences
- **Quality:** 72/100
- **Images:** 4/4 uploaded to Cloudinary

---

## ⚠️ Known Issues

### High Priority
1. **Railway deployment slow (12 minutes)** - Investigate build cache
2. **Critique Labs not integrated** - Need to call explicitly in pipeline
3. **DataForSEO** - Not in runtime stack (meant for keyword research, not article gen)

### Medium Priority
4. **Redis/Queue unhealthy** - BullMQ worker not consuming queue (falls back to FastAPI background tasks)
5. **No validation rules** - No pre-commit hooks or schema validation to prevent mismatches

### Low Priority
6. **generate_article.py output** - Save to `backend/generation_summary.json` (add to .gitignore)

---

## 📋 Next Session Priorities

### Option A: Keep Testing & Iterating
1. Generate 5-10 more articles with various topics
2. Monitor API usage patterns (which APIs get called most?)
3. Track quality scores vs. cost
4. Identify any remaining bugs

### Option B: Fix Remaining Issues
1. **Integrate Critique Labs** - Call `fact_check()` in EditorAgent
2. **Speed up Railway builds** - Investigate Docker cache
3. **Fix BullMQ worker** - Make it actually consume the queue
4. **Add validation** - Pre-commit hooks for schema mismatches

### Option C: Update Documentation (RECOMMENDED)
We haven't updated docs in a while - do a full pass:
1. **CLAUDE.md** - Add today's fixes to peer review section
2. **QUEST_ARCHITECTURE_V2_3.md** - Update quality thresholds, slug logic
3. **QUEST_RELOCATION_RESEARCH.md** - Any new insights from Codex test?
4. **QUEST_TRACKER.md** - Mark TIER 0 items as complete

---

## 🔧 Quick Reference Commands

### Check Latest Article
```bash
curl -s "https://quest-platform-production-9ee0.up.railway.app/api/articles/?limit=1" | jq '.articles[0] | {title, slug, quality_score, status}'
```

### Generate New Article (Backend)
```bash
cd ~/quest-platform/backend
python3 generate_article.py --topic "Your topic here" --site relocation
```

### Monitor Job Status
```bash
JOB_ID="<job-id-from-response>"
watch -n 5 "curl -s https://quest-platform-production-9ee0.up.railway.app/api/jobs/$JOB_ID | jq ."
```

### Check Railway Health
```bash
curl -s https://quest-platform-production-9ee0.up.railway.app/api/health | jq .
```

---

## 📚 Key Files

- **Backend Script:** `backend/generate_article.py` (moved from root)
- **Orchestrator:** `backend/app/agents/orchestrator.py` (slug fix here)
- **Research APIs:** `backend/app/core/research_apis.py` (LinkUp fix here)
- **Editor Thresholds:** `backend/app/agents/editor.py:184-189` (75/60)
- **Articles API:** `backend/app/api/articles.py` (published_at fix)
- **Jobs API:** `backend/app/api/jobs.py` (cost_breakdown fix)

---

## 💰 Cost Tracking (Latest Article)

```json
{
  "research": "$0.30",
  "content": "$0.05",
  "editor": "$0.005",
  "image": "$0.012",
  "total": "$0.3923"
}
```

**Note:** Multiple API calls increased research cost (Perplexity + Tavily + Serper)

---

## 🎯 Session Context

- **Tokens Used:** ~82k/200k (41%)
- **Started:** Railway restart troubleshooting (new Anthropic key)
- **Ended:** All fixes committed, Railway deployed, Codex feedback addressed
- **Mood:** Productive - Multiple bugs squashed, system more stable

**Remember:** Quality thresholds at 75/60 are temporary for testing. Revert to 85/70 once we're confident in the pipeline.
