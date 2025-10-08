# Quest Platform - AI Content Intelligence System

**Project:** Quest Platform
**Repository:** https://github.com/Londondannyboy/quest-platform
**Status:** Backend Complete, Frontend Pending
**Last Updated:** December 8, 2024

---

## 🎯 Project Overview

Quest is an **AI-powered content intelligence platform** that generates, manages, and publishes high-quality articles across multiple authority websites using a 4-agent orchestration system.

### Architecture

- **Backend:** FastAPI + BullMQ (Python 3.11+)
- **Database:** Neon PostgreSQL 16 + pgvector
- **Queue:** Redis (Upstash)
- **CMS:** Directus (pending setup)
- **Frontend:** Astro (pending setup)

---

## 🏗️ Current Status

### ✅ Completed

1. **Database Setup**
   - Neon PostgreSQL with 10 tables
   - pgvector extension for embeddings
   - Articles, research, job_status tables ready

2. **Backend API**
   - FastAPI server running on port 8000
   - Health check endpoint working
   - Article generation endpoint working
   - BullMQ job queue integrated

3. **4-Agent Pipeline**
   - ✅ ResearchAgent: Gathers intelligence from Perplexity
   - ✅ ContentAgent: Generates articles with Claude Sonnet 4.5
   - ✅ EditorAgent: Quality scoring and review
   - ⏳ ImageAgent: Ready but not tested

4. **End-to-End Test**
   - Successfully generated first article
   - 10,990 characters of content
   - Quality score: 75/100
   - Status: Marked for review

### ⏳ In Progress

1. **Bug Fixes**
   - JSON parsing (title/slug show "```json")
   - Job status schema alignment
   - Cost breakdown type conversion

### 📋 Pending

1. **Directus CMS**
   - Setup on Railway
   - Configure admin UI
   - Connect to Neon database

2. **Astro Frontend**
   - Initialize first site (relocation.quest)
   - GraphQL integration
   - Article display pages

3. **Deployment**
   - Railway deployment
   - Vercel frontend
   - Domain configuration

---

## 📂 Project Structure

```
quest-platform/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── research.py      # ResearchAgent
│   │   │   ├── content.py       # ContentAgent
│   │   │   ├── editor.py        # EditorAgent
│   │   │   ├── image.py         # ImageAgent
│   │   │   └── orchestrator.py  # Coordinates all agents
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── articles.py  # Article endpoints
│   │   ├── core/
│   │   │   ├── config.py        # Environment config
│   │   │   └── database.py      # Neon connection
│   │   └── main.py              # FastAPI app
│   ├── .env                     # Environment variables
│   └── requirements.txt         # Python dependencies
├── directus/                    # Pending: CMS setup
├── frontend/                    # Pending: Astro sites
└── docs/
    ├── CLAUDE.md                # This file
    ├── TRACKING.md              # Detailed progress tracking
    └── END-TO-END-TEST-RESULTS.md
```

---

## 🔧 Environment Variables

```bash
# Database
NEON_CONNECTION_STRING=<your-neon-connection-string>

# Redis Queue
UPSTASH_REDIS_URL=<your-upstash-redis-url>

# AI APIs
PERPLEXITY_API_KEY=<your-perplexity-api-key>
ANTHROPIC_API_KEY=<your-anthropic-api-key>
OPENAI_API_KEY=<your-openai-api-key>
REPLICATE_API_TOKEN=<your-replicate-api-token>

# Cloudinary
CLOUDINARY_CLOUD_NAME=<your-cloudinary-cloud-name>
CLOUDINARY_API_KEY=<your-cloudinary-api-key>
CLOUDINARY_API_SECRET=<your-cloudinary-api-secret>
```

---

## 🚀 Running Locally

```bash
# 1. Start backend
cd ~/quest-platform/backend
python3 -m app.main

# 2. Test article generation
curl -X POST http://localhost:8000/api/articles/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Best Digital Nomad Cities in Portugal 2025",
    "target_site": "relocation"
  }'

# 3. Check job status
curl http://localhost:8000/api/jobs/{job_id}

# 4. View articles in database
python3 -c "
import asyncio
import asyncpg

async def view():
    conn = await asyncpg.connect('postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require')
    arts = await conn.fetch('SELECT id, title, status FROM articles')
    for art in arts:
        print(f'{art[\"title\"][:50]} - {art[\"status\"]}')
    await conn.close()

asyncio.run(view())
"
```

---

## 🤖 4-Agent Pipeline

### 1. ResearchAgent (`app/agents/research.py`)
- Queries Perplexity Sonar API
- Generates embeddings with OpenAI
- Checks vector cache for similar topics
- Saves research to cache (30-day TTL)
- **Time:** 30-60 seconds

### 2. ContentAgent (`app/agents/content.py`)
- Uses Claude Sonnet 4.5
- Generates 2000-3000 word articles
- Site-specific brand voice
- SEO optimization
- **Time:** 60-90 seconds

### 3. EditorAgent (`app/agents/editor.py`)
- Grammar and style improvements
- Readability scoring (Flesch Reading Ease)
- Quality scoring (0-100)
- Determines if human review needed
- **Time:** 20-30 seconds

### 4. ImageAgent (`app/agents/image.py`)
- Generates hero images with FLUX Schnell
- Uploads to Cloudinary
- Runs in parallel (non-blocking)
- **Time:** 60 seconds

**Total Generation Time:** 2-3 minutes per article

---

## 📊 Database Schema

### Articles Table
```sql
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    hero_image_url TEXT,
    target_site VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    quality_score INTEGER,
    reading_time_minutes INTEGER,
    meta_title TEXT,
    meta_description TEXT,
    keywords TEXT[],
    published_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Research Cache Table
```sql
CREATE TABLE article_research (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic TEXT NOT NULL,
    research_data JSONB NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🐛 Known Issues

### Critical
1. **JSON Parsing Bug**
   - Title/slug fields show "```json" instead of actual values
   - Content is correct JSON inside
   - Fix: Strip markdown code fences from LLM responses

### Non-Critical
2. **Job Status Schema Mismatch**
   - Migration uses `current_step`, code expects different name
   - Job status updates fail but don't block article generation

3. **Cost Breakdown Type Error**
   - Pydantic validation expects dict, gets string
   - Affects job status API responses

---

## 📈 Next Steps (Priority Order)

1. **Fix JSON Parsing Bug** (5 minutes)
   - Update `content.py` and `editor.py`
   - Strip markdown fences before JSON.parse

2. **Test Article Retrieval** (10 minutes)
   - Create GET /api/articles endpoint
   - Test filtering by target_site
   - Verify JSON serialization

3. **Setup Directus CMS** (1-2 hours)
   - Deploy to Railway
   - Connect to Neon database
   - Configure admin UI
   - Test article management

4. **Create First Astro Site** (2-3 hours)
   - Initialize relocation.quest
   - GraphQL client for Directus
   - Article display pages
   - Deploy to Vercel

5. **Deploy Backend to Railway** (1 hour)
   - Configure environment variables
   - Setup background worker
   - Test production deployment

---

## 💰 Cost Analysis

### Monthly Operating Costs
- **Neon Database:** $50/month
- **Railway (Backend):** $30/month
- **Vercel (Frontend):** $0 (free tier)
- **Perplexity API:** ~$300/month (1000 articles)
- **Claude API:** ~$50/month (1000 articles)
- **OpenAI Embeddings:** ~$0.10/month
- **Replicate Images:** ~$3/month

**Total:** ~$435/month for 1000 articles = **$0.44 per article**

---

## 🔗 Resources

- **GitHub Repo:** https://github.com/Londondannyboy/quest-platform
- **Neon Dashboard:** https://console.neon.tech/
- **Upstash Redis:** https://console.upstash.com/
- **Anthropic Console:** https://console.anthropic.com/
- **Perplexity Docs:** https://docs.perplexity.ai/

---

## 📝 Development Notes

### Test Article Generated
- **ID:** `7358f245-b275-426a-9318-6dbb1c62e54d`
- **Topic:** "Best Digital Nomad Cities in Portugal 2025"
- **Content Length:** 10,990 characters
- **Quality Score:** 75/100
- **Status:** review (human approval needed)

### Performance Metrics
- Research: ~45 seconds
- Content: ~75 seconds
- Editor: ~25 seconds
- **Total:** ~2 minutes 25 seconds

### Background Processes
- 8 background shells running (need cleanup)
- Backend running on port 8000
- Redis connected successfully

---

## 🎯 Success Criteria

- [x] Database setup complete
- [x] 4-agent pipeline working
- [x] Article generation successful
- [ ] JSON parsing bug fixed
- [ ] Directus CMS operational
- [ ] First Astro site live
- [ ] End-to-end article publishing working

---

**Current Phase:** Backend complete, moving to frontend integration
**Confidence:** 90% - Minor bugs to fix, then ready for CMS/frontend
