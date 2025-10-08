# Quest Platform - Peer Review Guide

**Date:** October 8, 2025
**Status:** Production (End-to-End Working)
**Reviewer:** [Your Name]

---

## 🎯 Quick Start

**What Works Right Now:**
- ✅ Live article: https://relocation.quest/best-digital-nomad-cities-portugal
- ✅ Backend API: https://quest-platform-production-b8e3.up.railway.app/api/health
- ✅ Database: Neon PostgreSQL with 2 published articles

**What to Review:**
1. Code quality and architecture
2. Missing API integrations (Tavily, Firecrawl, SERP, Critique Labs, Link Up)
3. Image pipeline (untested)
4. Suggestions for Phase 2

---

## 📋 Review Checklist

### 1. Live System Testing (5 minutes)

**Frontend (Vercel/Astro)**
```bash
# Test article listing
curl -s https://relocation.quest/articles | grep "Best Cities"

# Test individual article page
curl -s https://relocation.quest/best-digital-nomad-cities-portugal | grep "<h1"

# Verify no deployment errors
open https://vercel.com/londondannyboys-projects/relocation-quest
```

**Backend (Railway/FastAPI)**
```bash
# Health check
curl https://quest-platform-production-b8e3.up.railway.app/api/health | jq

# List articles
curl https://quest-platform-production-b8e3.up.railway.app/api/articles/ | jq

# Get specific article
curl https://quest-platform-production-b8e3.up.railway.app/api/articles/by-slug/best-digital-nomad-cities-portugal | jq
```

**Expected Results:**
- Health check: `"status": "unhealthy"` (Redis optional, DB healthy)
- Articles endpoint: Returns 2 articles (1 good, 1 broken with JSON bug)
- Article page: Renders full HTML with content

---

### 2. Code Review (GitHub)

**Backend Repository:** https://github.com/Londondannyboy/quest-platform

#### Key Files to Review:

**1. Agent Architecture (`backend/app/agents/`)**

Files to inspect:
- `orchestrator.py` - Coordinates 4-agent flow
- `research.py` - Multi-source research (Perplexity primary)
- `content.py` - Claude Sonnet 4.5 generation
- `editor.py` - Quality control
- `image.py` - FLUX + Cloudinary (untested)

Questions for reviewer:
- Is the agent coordination logic clean and maintainable?
- Are there race conditions in the async orchestration?
- Should ImageAgent run in parallel or sequential?
- Error handling sufficient for production?

**2. API Endpoints (`backend/app/api/`)**

Files:
- `articles.py:136-175` - GET `/api/articles/by-slug/{slug}`
- `articles.py:220-286` - GET `/api/articles/` (list with filters)
- `articles.py:51-133` - POST `/api/articles/generate` (background job)

Review points:
- RESTful design appropriate?
- Query parameter validation?
- Should we add pagination headers?
- Rate limiting needed?

**3. Database Layer (`backend/app/core/database.py`)**

```python
# Connection pooling setup
async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(
        settings.NEON_CONNECTION_STRING,
        min_size=2,
        max_size=10,
        command_timeout=60,
    )
```

Questions:
- Pool size appropriate for Railway?
- Should we add query logging?
- Transaction handling correct in agents?

**4. Known Bugs to Address**

Issue 1: JSON Parsing Bug
- Location: `content.py` and `editor.py`
- Problem: LLM responses wrapped in ```json code fences
- Evidence: Article with title "```json" in database
- Fix needed: Strip markdown before JSON.parse

Issue 2: Trailing Slash Redirects
- Location: FastAPI router mounting
- Problem: `/api/articles` → 307 redirect to `/api/articles/`
- Current workaround: Frontend uses trailing slash
- Better fix: Configure FastAPI `redirect_slashes=False`?

---

### 3. Local Development Setup (15 minutes)

**Backend:**
```bash
# Clone and setup
git clone https://github.com/Londondannyboy/quest-platform.git
cd quest-platform/backend

# Install dependencies
pip3 install -r requirements.txt

# Copy environment template
cp .env.example .env
# Add your API keys to .env

# Run locally
python3 -m app.main

# Test generation endpoint
curl -X POST http://localhost:8000/api/articles/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Test Article Generation",
    "target_site": "relocation",
    "priority": "normal"
  }'
```

**Frontend:**
```bash
# Clone
git clone https://github.com/Londondannyboy/relocation-quest.git
cd relocation-quest

# Install
npm install

# Setup env
echo 'PUBLIC_API_URL=http://localhost:8000' > .env

# Run dev server
npm run dev

# Test
open http://localhost:4321/articles
```

---

### 4. Missing API Integrations (Critical Gap)

**Current State:**
- ✅ Perplexity Sonar (working)
- ✅ Claude Sonnet 4.5 (working)
- ✅ OpenAI embeddings (working)
- ⏳ **ALL other APIs pending**

**What Needs Integration:**

1. **Tavily API** (Research enhancement)
   - Purpose: Additional research source, Perplexity fallback
   - Priority: HIGH
   - Files: `backend/app/agents/research.py`
   - Estimated time: 1-2 hours

2. **Firecrawl** (Web scraping)
   - Purpose: Extract content from competitor articles
   - Priority: MEDIUM
   - Files: `backend/app/agents/research.py`
   - Estimated time: 2 hours

3. **SERP.dev** (Search results)
   - Purpose: Analyze SERP features for SEO
   - Priority: MEDIUM
   - Files: `backend/app/agents/research.py`
   - Estimated time: 1 hour

4. **Critique Labs** (Fact-checking)
   - Purpose: Validate claims for high-risk content
   - Priority: HIGH
   - Files: `backend/app/agents/editor.py`
   - Estimated time: 2-3 hours

5. **Link Up** (Link validation)
   - Purpose: Ensure outbound links are valid
   - Priority: LOW
   - Files: `backend/app/agents/editor.py`
   - Estimated time: 1 hour

**Review Question:**
Should we integrate all 5 APIs now, or prioritize Tavily + Critique Labs first?

---

### 5. Image Pipeline Testing (Untested Code)

**Current State:**
- ✅ Code exists in `backend/app/agents/image.py`
- ⏳ Never tested in production
- ⏳ No articles have images yet

**Test Plan:**
```python
# Manual test of ImageAgent
from app.agents.image import ImageAgent
from app.core.config import settings

agent = ImageAgent()

# Test image generation
result = await agent.generate_and_store(
    article_id="test-id",
    title="Best Digital Nomad Cities in Portugal",
    description="Lisbon, Porto, and Madeira"
)

# Expected result
{
    "hero_image_url": "https://res.cloudinary.com/...",
    "status": "completed",
    "generation_time": 45.2
}
```

**Review Points:**
- Is FLUX Schnell the right model? (vs FLUX Pro)
- Cloudinary free tier limits?
- Should images be generated in parallel or block article save?
- Error handling if image gen fails?

---

### 6. Architecture Decisions to Review

**1. FastAPI vs. Alternative Frameworks**
- Current: FastAPI
- Pros: Modern, async, auto-docs
- Cons: Trailing slash redirects, less mature ecosystem
- Alternative: Django REST Framework?

**2. Astro vs. Next.js for Frontend**
- Current: Astro SSR
- Pros: Fast, simple, server-side rendering
- Cons: Smaller ecosystem, fewer UI libs
- Alternative: Next.js with App Router?

**3. Direct API Call vs. GraphQL**
- Current: REST API directly from Astro
- Pros: Simple, no GraphQL overhead
- Cons: Skipped Directus GraphQL layer
- Should we add Directus back in?

**4. Job Queue: BullMQ vs. Celery**
- Current: BullMQ (Redis-based)
- Status: Partially implemented, Redis optional
- Cons: Redis connection issues on Railway
- Alternative: Celery with PostgreSQL backend?

---

### 7. Production Deployment Review

**Railway (Backend)**
- Auto-deploy: ✅ Working
- Health checks: ✅ Configured
- Environment vars: ✅ Set
- Logs: ⏳ Review needed
- Cost: $30/month projected

**Review:**
```bash
# Check Railway deployment logs
# (Manual review in Railway dashboard required)

# Verify environment variables set:
# - NEON_CONNECTION_STRING
# - PERPLEXITY_API_KEY
# - ANTHROPIC_API_KEY
# - OPENAI_API_KEY
# - REPLICATE_API_TOKEN
# - CLOUDINARY_* (3 vars)
```

**Vercel (Frontend)**
- Auto-deploy: ✅ Working
- Environment vars: ✅ PUBLIC_API_URL set
- Build time: ~2 minutes
- Cost: $0 (free tier)

---

### 8. Code Quality Metrics

**Backend Complexity:**
```bash
# Run radon for cyclomatic complexity
cd ~/quest-platform/backend
pip install radon
radon cc app/agents/ -a -nb

# Expected: Most functions < 10 complexity
```

**Type Coverage:**
```bash
# Check type hints
mypy app/ --ignore-missing-imports

# Expected: ~80% coverage
```

**Test Coverage:**
```bash
# Currently: NO TESTS
# Priority: Add pytest suite

# Suggested test structure:
tests/
├── test_agents/
│   ├── test_research.py
│   ├── test_content.py
│   ├── test_editor.py
│   └── test_image.py
├── test_api/
│   ├── test_articles.py
│   └── test_jobs.py
└── test_integration/
    └── test_end_to_end.py
```

---

### 9. Security Review

**Environment Variables:**
- ✅ Stored in Railway/Vercel securely
- ✅ Not committed to Git
- ⏳ Should add `.env.example` to both repos

**Database Access:**
- ✅ Using connection pooling
- ✅ Parameterized queries (asyncpg)
- ⏳ Consider read replicas for scaling

**API Security:**
- ⏳ No authentication currently
- ⏳ No rate limiting
- ⏳ CORS configured but permissive

**Suggested Additions:**
```python
# Add to main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/articles/generate")
@limiter.limit("5/minute")  # Limit article generation
async def generate_article(...):
    ...
```

---

### 10. Database Schema Review

**Current Schema:**
```sql
-- Review these tables
\dt articles
\dt article_research
\dt job_status

-- Check indexes
\di

-- Verify pgvector extension
SELECT * FROM pg_extension WHERE extname = 'vector';
```

**Questions:**
- Should we add full-text search indexes?
- Is `vector(1536)` the right embedding dimension?
- Should we partition articles by `target_site`?
- Add audit logging table?

---

## 🔥 Critical Issues Needing Attention

### Priority 1: API Integrations
**Impact:** Medium
**Effort:** 6-8 hours
**Blockers:** None

Missing: Tavily, Firecrawl, SERP, Critique Labs, Link Up

### Priority 2: Image Pipeline Testing
**Impact:** Medium
**Effort:** 2-3 hours
**Blockers:** None

Need to generate first article with images

### Priority 3: JSON Parsing Bug
**Impact:** Low (workaround exists)
**Effort:** 30 minutes
**Blockers:** None

Strip markdown code fences from LLM responses

### Priority 4: Add Tests
**Impact:** High (for long-term)
**Effort:** 8-12 hours
**Blockers:** None

Current coverage: 0%

---

## 📊 Suggested Improvements

### Quick Wins (< 1 hour each)

1. **Add request logging**
   - Log all API calls to articles endpoint
   - Track popular slugs
   - Monitor response times

2. **Add health check for each API**
   - Perplexity: Check API key validity
   - Cloudinary: Check upload quota
   - Database: Check connection count

3. **Improve error messages**
   - Return structured error responses
   - Add error codes for different failure types
   - Log errors to external service (Sentry?)

4. **Add API documentation**
   - FastAPI auto-docs already at `/docs`
   - Add examples for each endpoint
   - Document expected response times

### Medium Effort (2-4 hours each)

5. **Implement caching**
   - Cache article listings for 5 minutes
   - Cache individual articles for 1 hour
   - Use Redis or in-memory cache

6. **Add monitoring**
   - Setup Plausible for frontend analytics
   - Add structured logging to backend
   - Create cost monitoring dashboard

7. **Optimize database queries**
   - Add indexes on `target_site` + `status`
   - Add full-text search on `title` + `content`
   - Implement query result caching

### Large Effort (1-2 days each)

8. **Add Directus CMS**
   - Deploy to Railway
   - Connect to Neon database
   - Setup MCP server for Claude Code

9. **Create placement.quest and rainmaker.quest**
   - Clone relocation-quest template
   - Customize branding per site
   - Deploy to Vercel

10. **Implement proper job queue**
    - Fix Redis connection issues
    - Add job retry logic
    - Create admin dashboard for queue monitoring

---

## 🎯 Reviewer Action Items

**After reviewing, please provide feedback on:**

1. **Code Quality (1-10):** How maintainable is the codebase?
2. **Architecture (1-10):** Is the tech stack appropriate?
3. **Critical Issues:** Any showstoppers you found?
4. **Priority Ranking:** What should we build next?
5. **Estimated Timeline:** How long to complete Phase 1?

**Please review specifically:**
- [ ] Agent orchestration logic (`backend/app/agents/orchestrator.py`)
- [ ] API endpoint design (`backend/app/api/articles.py`)
- [ ] Database schema efficiency (Neon dashboard)
- [ ] Frontend rendering performance (Vercel analytics)
- [ ] Missing API integrations priority order

---

## 📝 Reviewer Notes

[Space for your notes and feedback]

### Code Quality:
-

### Architecture:
-

### Critical Issues Found:
-

### Recommended Next Steps:
1.
2.
3.

### Questions for the Team:
-

---

**Review Completed By:** _______________
**Date:** _______________
**Overall Assessment:** _______________

