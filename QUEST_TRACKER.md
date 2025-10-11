# Quest Platform - Progress Tracker

**Last Updated:** October 11, 2025 (Citation Format Milestone)
**Current Phase:** 🎉 **MILESTONE: Citation Format + AstroWind Deployment COMPLETE**
**Status:** 🟢 Operational - End-to-End Publishing Validated
**Live Example:** https://relocation.quest/iceland-digital-nomad-visa-2025

---

## 📊 Overall Progress

```
███████████████████████████░░░ 93% Complete

✅ Phase 1: Core Platform (COMPLETE)               [100%]
✅ Backend API & 7-Agent Pipeline                  [100%]
✅ Frontend Deployment (relocation.quest)          [100%]
✅ TIER 0 Critical Fixes (OPUS)                    [100%]
⏳ Phase 2: Scale & Optimize (IN PROGRESS)         [30%]
🎨 Phase 2.5: Template Intelligence (NEW)          [15%]
⏳ Phase 3: Multi-Site Expansion                   [0%]
```

---

## 🎉 MILESTONE ACHIEVED (October 11, 2025)

### First Complete Article with Inline Hyperlinks
- **Live URL:** https://relocation.quest/iceland-digital-nomad-visa-2025
- **Word Count:** 5,164 words (full article)
- **Inline Hyperlinks:** 77 using `[anchor text](url)` format
- **Images:** 4 Cloudinary images rendering correctly
- **References:** "Further Reading & Sources" section with bullets
- **Frontend:** AstroWind theme + Vercel deployment ✅
- **Status:** End-to-end workflow validated ✅

### Live Infrastructure
- **Frontend:** https://relocation.quest ✅
- **Backend API:** https://quest-platform-production-b8e3.up.railway.app ✅
- **Database:** Neon PostgreSQL 16 with pgvector ✅
- **Articles:** 4+ published, citation format working ✅
- **Cost Per Article:** $0.75 ✅ (Gemini+Sonnet chunking)
- **Generation Time:** 2-3 minutes ✅
- **Content Quality:** 5K+ words with 15-25 citations ✅

### Recent Published Articles
1. **Iceland Digital Nomad Visa 2025** (Oct 11, 2025) **← NEW MILESTONE**
   - Slug: `iceland-digital-nomad-visa-2025`
   - Quality: N/A (deployed to AstroWind)
   - Word Count: 5,164 words
   - Inline Hyperlinks: 77 ✅
   - Images: Hero + 3 content images ✅
   - URL: https://relocation.quest/iceland-digital-nomad-visa-2025

2. **Portugal Digital Nomad Visa** (Oct 9, 2025)
   - Slug: `portugal-digital-nomad-visa-2025-complete-application-guide`
   - Quality: 85/100
   - Images: Hero + 3 content images ✅
   - URL: https://relocation.quest/portugal-digital-nomad-visa-2025-complete-application-guide

3. **Best Cafes Lisbon** (Oct 9, 2025)
   - Slug: `best-cafes-for-remote-work-in-lisbon-2025`
   - Quality: 82/100
   - Images: All 4 working ✅
   - URL: https://relocation.quest/best-cafes-for-remote-work-in-lisbon-2025

4. **Best Cities Portugal** (Oct 7, 2025)
   - Slug: `best-digital-nomad-cities-portugal`
   - Quality: 85/100
   - First successful end-to-end article ✅

---

## 🏗️ PHASE 1: CORE PLATFORM (100% COMPLETE)

### Database Setup ✅
- [x] Neon PostgreSQL 16 deployed
- [x] pgvector extension installed
- [x] Production schema deployed:
  - `articles` (main content)
  - `article_research` (cached with embeddings)
  - `job_status` (background job tracking)
- [x] Connection pooling configured (asyncpg)
- [x] 40% cache hit rate achieved

### Backend API (FastAPI on Railway) ✅
- [x] Health check: `/api/health`
- [x] Articles endpoint: `/api/articles/`
- [x] Article by slug: `/api/articles/by-slug/{slug}`
- [x] Job status: `/api/jobs/{id}`
- [x] Auto-deploy on GitHub push
- [x] CORS configured for Vercel
- [x] Production URL: https://quest-platform-production-b8e3.up.railway.app

### 4-Agent Pipeline ✅
1. **ResearchAgent** ✅
   - Perplexity API integrated
   - OpenAI embeddings for cache
   - Vector similarity search
   - 30-day TTL caching
   - 40% cost savings achieved

2. **ContentAgent** ✅
   - Claude Sonnet 4.5
   - 2000-3000 word articles
   - SEO optimization
   - Site-specific brand voice
   - ⚠️ Known issue: Returns JSON (DB expects markdown)

3. **EditorAgent** ✅
   - Quality scoring (0-100)
   - Readability checks (Flesch)
   - Grammar improvements
   - Review threshold logic

4. **ImageAgent** ✅
   - FLUX Schnell generation
   - Cloudinary storage
   - 4 images per article (hero + 3 content)
   - Parallel execution
   - Working in production

### Frontend (Astro on Vercel) ✅
- [x] relocation.quest deployed
- [x] Article listing page
- [x] Dynamic article pages `[slug].astro`
- [x] Responsive design (Tailwind CSS)
- [x] Markdown rendering with `marked`
- [x] Image display working
- [x] Auto-deploy on GitHub push

### Deployment & CI/CD ✅
- [x] Railway: Backend auto-deploy
- [x] Vercel: Frontend auto-deploy
- [x] GitHub Actions: Not needed (platform auto-deploys)
- [x] Environment variables: Securely stored
- [x] Health monitoring: `/api/health` endpoint

---

## ⏳ PHASE 2: SCALE & OPTIMIZE (15% COMPLETE)

### TIER 0: Critical Fixes (Status: October 10, 2025 - Evening)

#### 0. Research Governance Integration ❌ **[HIGHEST PRIORITY]**
**Problem:** ResearchAgent bypasses QUEST_RELOCATION_RESEARCH.md (993 topics)
**Impact:** Duplicate research costs, missing high-value topics, no SEO prioritization
**Solution:** Add pre-flight checks before Perplexity API calls
**Priority:** CRITICAL
**Est. Time:** 3-4 hours
**Files:** `backend/app/agents/research.py`, `backend/app/core/research_queue.py` (new)
**Codex Finding:** "Architecture v2.3 requires consulting research playbook before external APIs"

#### 1. Schema Mismatch (Architectural Issue) ✅ **FIXED (Oct 10)**
**Problem:** Content agent returned nested JSON, DB expects plain markdown
**Solution:** Removed JSON wrapper, outputs pure markdown now
**Fixed In:** Commit `9146343` (Haiku model update)
**Files Changed:** `backend/app/agents/content.py`
**Status:** RESOLVED - ContentAgent now returns clean markdown

#### 2. Multi-API Research Integration ✅ **COMPLETE (Oct 10)**
**Previous:** Perplexity only
**Now Integrated:**
- ✅ Perplexity (primary research)
- ✅ DataForSEO (keyword validation + SEO metrics)
- ✅ Tavily (fallback + additional research)
- ✅ LinkUp (link validation)
- ✅ Serper (SERP analysis)
- ✅ Firecrawl (web scraping - needs URLs)
**Priority:** COMPLETE
**Commit:** `feb92c8` (Multi-API research flow)
**Files:** `backend/app/agents/research.py`, `backend/app/core/research_apis.py`

#### 3. No BullMQ Queue ❌
**Current:** Jobs pushed to Redis but executed synchronously (Codex finding)
**Impact:** Won't scale past 100 articles/day
**Codex Finding:** "API enqueues jobs but immediately executes orchestrator in-process"
**Need:**
- Fix worker.py to poll Redis queue
- Deploy worker as separate Railway service
- Retry logic with exponential backoff
**Priority:** MEDIUM (After 20 articles)
**Est. Time:** 4-5 hours

#### 4. Directus CMS Not Deployed ❌
**Current:** No admin UI, no HITL workflow
**Need:**
- Deploy to Railway
- Connect to Neon (restricted user)
- Configure admin UI
- Test human review workflow
**Priority:** MEDIUM
**Est. Time:** 3-4 hours

#### 5. No Spec Kit / TaskMaster AI Validation ❌
**Problem:** Schema drift between agents and database, no task orchestration enforcement
**Need:**
- **GitHub Spec Kit** (`@github/spec-kit`): Runtime schema validation against JSON specs
- **TaskMaster AI** (`task-master-ai`): Task decomposition, dependency enforcement, cost tracking
**Priority:** HIGH
**Est. Time:** 3-4 hours (Spec Kit) + 4-5 hours (TaskMaster)
**Files:** `backend/app/core/validation.py` (new), `backend/app/core/task_manager.py` (new)
**Why Critical:**
- Spec Kit: Catches schema mismatches (like content agent JSON vs DB markdown)
- TaskMaster: Enforces TIER 0 priorities (e.g., research governance before Perplexity)
**Tools:** Already in `scripts/setup-dev-environment.sh`, needs integration

#### 6. Multi-Site Frontends Missing ❌ **[NEW - Codex Final Review]**
**Problem:** Only relocation.quest deployed, placement.quest and rainmaker.quest are empty directories
**Impact:** Multi-site strategy unvalidated, can't test shared packages or brand differentiation
**Solution:** Scaffold and deploy placement.quest and rainmaker.quest Astro apps
**Priority:** LOW (After 100 relocation.quest articles)
**Est. Time:** 2-3 hours per site (4-6 hours total)
**Files:** Create separate repos (per architecture), clone relocation-quest template
**Codex Finding:** "Three Astro deployments required, but only relocation.quest has source code"
**Note:** Architecture confirmed separate repos (not monorepo) - delay until relocation.quest proven at scale

### Quality Improvements

#### Testing ❌ (0% coverage)
- [ ] pytest suite
- [ ] Agent unit tests
- [ ] API integration tests
- [ ] End-to-end test automation

#### Monitoring ⏳ (Partial)
- [x] Basic health checks
- [ ] Plausible analytics on frontend
- [ ] Structured logging to external service
- [ ] Cost monitoring dashboard
- [ ] Performance metrics

#### Performance ⏳ (Partial)
- [x] Research cache (40% hit rate)
- [ ] API response caching (Redis)
- [ ] Database query optimization
- [ ] Full-text search indexes

---

## 🎨 PHASE 2.5: TEMPLATE INTELLIGENCE (15% COMPLETE)

**Status:** Design Complete, Implementation Pending
**Start Date:** October 10, 2025
**Target Completion:** November 15, 2025
**Priority:** HIGH - Competitive moat

### What is Template Intelligence?

Revolutionary content architecture that analyzes SERP winners (Serper + Firecrawl) to detect **content archetypes** (strategic depth) vs **visual templates** (user-facing structure), then generates SERP-competitive content using modular components.

**Core Innovation:** Distinguishes between:
- **ARCHETYPE** = Strategic depth (what ranks): Skyscraper, Cluster Hub, Deep Dive, Comparison Matrix, News Hub
- **TEMPLATE** = Visual structure (what users expect): Ultimate Guide, Listicle, Comparison, Location Guide, etc.

**Example:** "Top 10 Digital Nomad Visas" LOOKS like a simple listicle, but IS a 12,000-word skyscraper with 14 modules, ranking for 750+ keywords.

### Implementation Checklist

#### TIER 0.5: Foundation (Week 1-2)

**Database Schema (5 New Tables):**
- [ ] Create `content_archetypes` table - Archetype definitions (Skyscraper, Cluster Hub, etc.)
- [ ] Create `content_templates` table - Template definitions (Ultimate Guide, Listicle, etc.)
- [ ] Create `serp_intelligence` table - SERP analysis results (cached recommendations)
- [ ] Create `scraped_competitors` table - Individual competitor analysis
- [ ] Create `template_performance` table - Learning from results
- [ ] Add `target_archetype`, `surface_template`, `modules_used` columns to `articles` table
- [ ] Create indexes (archetype, template, keyword, URL)

**TemplateDetector Agent:**
- [ ] Implement `TemplateDetector` class (`backend/app/agents/template_detector.py`)
- [ ] Integrate Serper.dev API (SERP analysis)
- [ ] Integrate Firecrawl API (competitor scraping)
- [ ] Implement multi-dimensional archetype detection algorithm
  - [ ] Word count & section depth analysis
  - [ ] Module detection (FAQ, calculator, tables, etc.)
  - [ ] Internal linking patterns
  - [ ] Schema stacking detection
  - [ ] E-E-A-T signals (expert quotes, case studies, citations)
- [ ] Implement recommendation engine
  - [ ] Dominant archetype selection
  - [ ] Template recommendation
  - [ ] Required modules extraction
  - [ ] Target word count calculation
- [ ] Implement caching (30-day TTL)

**ContentAgent Enhancement:**
- [ ] Update ContentAgent to receive archetype + template guidance
- [ ] Add archetype-specific prompts (Skyscraper vs Deep Dive vs Comparison)
- [ ] Add template-specific structure instructions
- [ ] Add module assembly logic
- [ ] Add E-E-A-T requirement enforcement for YMYL content

#### TIER 0.6: Frontend Templates (Week 3-4)

**Astro Template Components (12 Templates):**
- [ ] UltimateGuide.astro (most common wrapper)
- [ ] Listicle.astro (numbered rankings)
- [ ] Comparison.astro (X vs Y)
- [ ] LocationGuide.astro (country/city-specific)
- [ ] DeepDiveTutorial.astro (how-to)
- [ ] CategoryPillar.astro (topic overview)
- [ ] ProblemSolution.astro
- [ ] NewsUpdate.astro
- [ ] CaseStudy.astro
- [ ] DataStudy.astro
- [ ] ToolCalculator.astro
- [ ] Interview.astro

**Modular Component Library (35 Components):**

_Content Modules (15):_
- [ ] TldrSection.astro
- [ ] KeyTakeaways.astro
- [ ] StatsCallout.astro
- [ ] ProsConsList.astro
- [ ] StepByStep.astro
- [ ] FaqAccordion.astro
- [ ] ComparisonTable.astro
- [ ] ExpertQuote.astro
- [ ] CaseStudyCard.astro
- [ ] ResourceGrid.astro
- [ ] GlossaryTerms.astro
- [ ] VideoEmbed.astro
- [ ] Infographic.astro
- [ ] Timeline.astro
- [ ] Checklist.astro

_Interactive Modules (10):_
- [ ] Calculator.astro (JS-powered computation)
- [ ] Quiz.astro (assessment with results)
- [ ] InteractiveMap.astro (Google Maps embed)
- [ ] FilterSystem.astro (refine table/grid)
- [ ] ComparisonCheckbox.astro (select items)
- [ ] CostEstimator.astro (multi-variable calculator)
- [ ] ProgressTracker.astro (save user's place)
- [ ] BookmarkTool.astro (save for later)
- [ ] EmailCapture.astro (newsletter signup)
- [ ] LiveData.astro (real-time stats)

_Schema Modules (10):_
- [ ] ArticleSchema.ts
- [ ] HowToSchema.ts
- [ ] FaqSchema.ts
- [ ] ReviewSchema.ts
- [ ] BreadcrumbSchema.ts
- [ ] TableSchema.ts
- [ ] VideoSchema.ts
- [ ] EventSchema.ts
- [ ] PersonSchema.ts
- [ ] OrganizationSchema.ts

**Dynamic Template Routing:**
- [ ] Update `src/pages/[slug].astro` for dynamic template selection
- [ ] Add template component mapping logic
- [ ] Add fallback to UltimateGuide template

#### TIER 0.7: Integration & Testing (Week 5-6)

**Orchestrator Updates:**
- [ ] Add TemplateDetector to article generation pipeline
- [ ] Update flow: Research → TemplateDetector → Content → Editor → Image
- [ ] Add SchemaGenerator for multi-schema JSON-LD stacking
- [ ] Store archetype/template/modules in `template_performance` table

**Content Strategy:**
- [ ] Reclassify 993 topics in `QUEST_RELOCATION_RESEARCH.md` by archetype
  - 40% Skyscraper (foundation content)
  - 20% Deep Dive Specialist (specific processes)
  - 20% Comparison Matrix (decision content)
  - 15% Cluster Hub (category overviews)
  - 5% News Hub (timely updates)
- [ ] Add `recommended_archetype` column to topic queue

**Testing & Validation:**
- [ ] Generate first 10 template-driven articles
  - 5 Skyscraper articles (8000+ words, 12+ modules)
  - 3 Deep Dive articles (3500+ words, 9+ modules)
  - 2 Comparison Matrix articles (3500+ words, 10+ modules)
- [ ] Validate archetype detection accuracy (target: >85%)
- [ ] Validate E-E-A-T requirements for YMYL content
- [ ] Manual review: Archetype matches SERP analysis
- [ ] Performance test: Latency impact of TemplateDetector

### Success Metrics

**Template Detection:**
- Archetype detection accuracy: >85%
- SERP analysis cache hit rate: >50%
- Template recommendation confidence: >80%

**Content Quality:**
- Skyscraper articles: 8000+ words, 12+ modules, 85+ quality score
- Deep Dive articles: 3500+ words, 9+ modules, 85+ quality score
- E-E-A-T signals present in 100% of YMYL content

**Performance:**
- Template detection latency: <30 seconds
- Total generation time: <90 seconds per article
- Cost per article: <$0.70 (including Template Intelligence premium)

### Documentation

**Complete Documentation:**
- ✅ `QUEST_TEMPLATES.md` (980 lines) - Authority document
  - 5 content archetypes with specifications
  - 12 visual templates with structure
  - 35 modular components library
  - Multi-dimensional archetype detection algorithm
  - E-E-A-T optimization framework
  - SERP intelligence workflow

**Related Updates:**
- ✅ `QUEST_ARCHITECTURE_V2_4.md` - Template Intelligence System architecture
- ⏳ `QUEST_SEO.md` - Archetype-first SEO strategy
- ⏳ `QUEST_RELOCATION_RESEARCH.md` - Topics reclassified by archetype
- ⏳ `QUEST_PEER_REVIEW.md` - Template Intelligence review criteria

### Cost Analysis (Template Intelligence Premium)

**Added Costs:**
- Serper.dev (SERP analysis): ~$50/month (1000 articles) = $0.05/article
- Firecrawl (competitor scraping): ~$30/month (1000 articles) = $0.03/article
- **Template Intelligence Premium:** $0.08/article

**Total Cost Per Article:**
- Previous: $0.60/article (6-API research + Haiku)
- With Template Intelligence: $0.68/article
- **ROI:** $0.08 investment → Ranks 10+ positions higher (SERP-competitive content)

**Break-Even Analysis:**
- Position #15 → Position #5 = 3x traffic increase
- $0.08 premium per article pays for itself in increased organic reach

---

## 🌐 PHASE 3: MULTI-SITE EXPANSION (0%)

### Additional Sites ❌
- [ ] placement.quest (career content) - Separate repo + Vercel deployment
- [ ] rainmaker.quest (business content) - Separate repo + Vercel deployment
- [ ] Site-specific branding
- [ ] Cross-site content recommendations

**Architecture Note:** Using **separate repos** per frontend (not Turborepo monorepo)
- ✅ Simpler at current scale (3 articles)
- ✅ Vercel free tier: 3 projects = free
- ✅ Independent deploy cycles
- ⏳ Turborepo: Consider after 500+ articles across all sites

### Separate-Repo Architecture (Current Model)
```
# Backend (single repo)
~/quest-platform/                  ← Backend monorepo
└── backend/                       ← FastAPI + agents

# Frontends (separate repos, separate Vercel deployments)
~/relocation-quest/                ← GitHub: Londondannyboy/relocation-quest (LIVE)
~/placement-quest/                 ← Clone when ready (after 100 articles)
~/rainmaker-quest/                 ← Clone when ready (after 100 articles)
```

**Why NOT Turborepo (at current scale):**
- Vercel model: 1 repo = 1 deployment
- No shared component library yet (3 articles total)
- Independent scaling per site
- Simpler CI/CD

### GraphQL Migration (Planned)
**Current:** Direct Neon queries from Astro (via Railway API)
**Target:** Directus GraphQL → Apollo Client
**Benefits:** Type safety, better caching, query efficiency
**Timeline:** After Directus deployment + 50 articles published

---

## 📈 METRICS & KPIs

### Current Performance (October 9, 2025)
```yaml
Articles Published: 3
Success Rate: 100% (3/3)
Average Generation Time: 2m 30s
Average Cost: $0.44/article
Cache Hit Rate: 40%
Quality Score Average: 84/100

Image Pipeline:
  Success Rate: 100%
  Images Per Article: 4 (hero + 3 content)
  Average Time: 60s (parallel)

API Endpoints:
  Health Check: 100% uptime
  Article Generation: 100% success
  Article Retrieval: 100% success
```

### Cost Breakdown (Per 1000 Articles - Updated Oct 10, 2025)
```yaml
Infrastructure ($80/month):
  Neon PostgreSQL: $50
  Railway (FastAPI): $30
  Vercel (Astro): $0 (free tier)
  Cloudinary: $0 (free tier)

AI APIs ($600/month with 6-API research):
  Multi-API Research: $450
    - Perplexity: $200 (with cache)
    - DataForSEO: $100 (keyword validation)
    - Tavily: $50
    - Serper: $50
    - LinkUp: $30
    - Firecrawl: $20

  Content Generation: $30 (Haiku - 25x cheaper than Sonnet!)
  OpenAI Embeddings: $0.10
  Replicate FLUX (Images): $3

Total: $680/month = $0.68/article
(Previous with Sonnet: $0.77/article)
Cost Savings: 25x on content generation ($0.75 → $0.03)
```

### Target KPIs (Phase 2)
- [ ] 100+ articles published
- [ ] <2 minute avg generation time
- [ ] <$0.50 avg cost per article
- [ ] >50% cache hit rate
- [ ] >85 avg quality score
- [ ] 99.9% API uptime

---

## 🐛 KNOWN ISSUES (Updated Oct 10, 2025)

### High Priority
1. **✅ FIXED: Schema Mismatch** - Content agent now returns pure markdown
   - Previously: Returned JSON wrapper
   - Now: Returns clean markdown directly
   - Fixed in commit `9146343`

2. **✅ FIXED: Missing Research APIs** - All 6 APIs integrated
   - Perplexity ✅
   - DataForSEO ✅
   - Tavily ✅
   - Serper ✅
   - LinkUp ✅
   - Firecrawl ✅ (needs URLs)

3. **⚠️ REMAINING: No Runtime Validation** - Schema drift possible
   - Need GitHub Spec Kit (@github/spec-kit) for schema validation
   - Need TaskMaster AI (task-master-ai) for task orchestration enforcement

### Medium Priority
4. **No Queue System** - Synchronous execution limits scale
5. **No CMS Deployed** - No human review workflow
6. **No Test Coverage** - 0% automated testing

### Low Priority
7. **Redis Connection** - Made optional but limits features
8. **No Rate Limiting** - API open to abuse
9. **No Authentication** - Open API endpoints

---

## 📅 TIMELINE & MILESTONES

### Completed Milestones
- ✅ **Oct 7, 2025** - First article published end-to-end
- ✅ **Oct 9, 2025** - Image pipeline working (4 images/article)
- ✅ **Oct 9, 2025** - Markdown rendering fixed
- ✅ **Oct 9, 2025** - Documentation consolidated
- ✅ **Oct 10, 2025** - Multi-API research (6 APIs integrated)
- ✅ **Oct 10, 2025** - Haiku model integration (25x cost savings)
- ✅ **Oct 10, 2025** - Pure markdown output (no JSON wrapper)
- ✅ **Oct 10, 2025** - Syntax errors fixed (Unicode, f-strings)

### Upcoming Milestones
- 🔄 **Oct 11, 2025** - Deploy Haiku model to Railway (`9146343`)
- ⏳ **Week of Oct 14** - Generate first test article with Haiku
- ⏳ **Week of Oct 14** - Research governance pre-flight checks
- ⏳ **Week of Oct 21** - 10+ articles published
- ⏳ **Week of Oct 28** - Directus CMS deployed
- ⏳ **Week of Nov 11** - BullMQ queue operational

---

## 🔗 QUICK LINKS

### Production
- Frontend: https://relocation.quest
- Backend: https://quest-platform-production-b8e3.up.railway.app
- Health Check: https://quest-platform-production-b8e3.up.railway.app/api/health

### GitHub
- Backend: https://github.com/Londondannyboy/quest-platform
- Frontend: https://github.com/Londondannyboy/relocation-quest

### Dashboards
- Railway: https://railway.app/
- Vercel: https://vercel.com/londondannyboys-projects/relocation-quest
- Neon: https://console.neon.tech/
- Cloudinary: https://cloudinary.com/console

### Documentation
- Architecture: QUEST_ARCHITECTURE_V2_3.md
- SEO Strategy: QUEST_SEO.md (LLM-first optimization, technical fundamentals, content tactics)
- Content Strategy: QUEST_RELOCATION_RESEARCH.md (operational)
- Technical Docs: CLAUDE.md
- Restart Guide: QUEST_RESTART_PROMPT.md
- Peer Review: QUEST_PEER_REVIEW.md
- This Tracker: QUEST_TRACKER.md (you are here)

---

## 📞 DEPLOYMENT COMMANDS

### Generate Test Article
```bash
cd ~/quest-platform/backend
python3 generate_full_article.py
```

### Check Latest Articles
```bash
NEON_CONNECTION_STRING="postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require" \
psql -c "SELECT id, title, slug, status, quality_score FROM articles ORDER BY created_at DESC LIMIT 5;"
```

### Deploy Backend (Auto)
```bash
cd ~/quest-platform
git add . && git commit -m "Update" && git push origin main
# Railway auto-deploys in ~2 minutes
```

### Deploy Frontend (Auto)
```bash
cd ~/relocation-quest
git add . && git commit -m "Update" && git push origin main
# Vercel auto-deploys in ~1 minute
```

---

**Last Updated:** October 10, 2025 (Evening Session)
**Next Review:** October 14, 2025 (Research governance + Haiku validation)
