# Quest Architecture v2.6
## Multi-Site Content Intelligence Platform with AI-Assisted Production + Template Intelligence + Conversational SEO

**Version:** 2.6.0 (Chunked Content + Safety-First Publishing)
**Date:** October 10, 2025 (Evening - Chunked Content Breakthrough)
**Status:** ✅ PRODUCTION (Chunked Gemini+Sonnet, 5K+ words, Google-Safe Publishing)
**Peer Reviews:** ChatGPT 4.0 (A-), Gemini 2.0 Flash (A-), Claude Desktop (Astro+Vercel), **Codex (Oct 9, 2025: 7/10)**

**🎉 BREAKTHROUGH v2.6.0 (Oct 10, 2025 - Evening):**
- ✅ **Chunked Content System WORKING** - Gemini 2.5 Pro (chunks) + Sonnet 4.5 (refinement)
  - Gemini generates 3 chunks in parallel (1,293 words)
  - Gemini Flash weaves chunks with transitions ($0.01)
  - Sonnet expands to 5,344 words (310% growth!)
  - Cost: $0.75/article | Quality: 5K+ words with 15-25 citations
- ✅ **QUEST_CONTENT_PUBLISHING_GUIDELINES.md** - MANDATORY compliance document
  - Google spam policy matrix (prevents "Machine-Scaled Content Abuse")
  - Publication rate limits: 2/day → 10/day (based on site age)
  - Quality gates: 3000+ words, 15+ citations, References section
  - TailRide case study analysis (they got penalized at 244/day, we're 122x safer)
- ✅ **Safety-First Architecture** - Sustainable scaling prevents penalties
  - Max 200 articles/month (vs TailRide's 7,333/month penalty)
  - Year 1 target: 1,550 articles (vs TailRide's 22,000 in 3 months)
  - E-E-A-T signals, author attribution, AI disclosure
- ✅ **Cost Optimization Strategies** - 40% potential savings
  - Research caching (90% hit rate): $225/month savings
  - Firecrawl caching (80% hit rate): $6.40/month savings
  - Image optimization: $60/month savings
  - Total: $450/month savings at 1000 articles/month

**Major Changes v2.5.0 (Oct 10, 2025 - Late Evening):**
- ✅ **Conversational SEO Strategy** - Holistic long-tail optimization across all 3 sites
  - 6th archetype: Conversational Answer Hub (persona-first, 1.5-3k words)
  - Pattern generation (100 patterns per site = 300 total)
  - AI citation tracking (ChatGPT, Perplexity, Claude, Google AI)
  - Cross-site application (relocation.quest, placement.quest, rainmaker.quest)
  - Based on Hamish's insight: 9+ word queries exploding due to AI search behavior
- ✅ **Backwards-Compatible Schema** - No breaking changes to existing articles
  - Additive columns only (persona_nationality, target_archetype, etc.)
  - Existing articles continue working with default templates
  - New conversational articles use enhanced templates
- ✅ **Implementation Phasing** - Content first, optimization later
  - Priority 1: Get 20 articles live (validate publishing flow)
  - Priority 2: Deploy placement.quest
  - Priority 3: Implement Template Intelligence (TIER 0.5)
  - Priority 4: Implement Conversational SEO (TIER 0.9)

**Previous Changes v2.4.0 (Oct 10, 2025):**
- ✅ **Template Intelligence System** - Revolutionary SERP-driven content architecture
  - Archetype detection (Skyscraper, Cluster Hub, Deep Dive, Comparison Matrix, News Hub)
  - Visual template system (Ultimate Guide, Listicle, Comparison, Location Guide, etc.)
  - Modular component library (35 reusable building blocks)
  - E-E-A-T optimization for YMYL content (visa/tax/legal topics)
  - 5 new database tables for SERP intelligence and content strategy
- ✅ TemplateDetector agent (Serper + Firecrawl competitor analysis)
- ✅ Multi-schema JSON-LD stacking (Article + FAQPage + HowTo + ItemList)
- 📖 Complete documentation: QUEST_TEMPLATES.md (980 lines)

**Previous Changes (Oct 10, 2025):**
- ✅ Multi-API research complete (Perplexity + DataForSEO + Tavily + Serper + LinkUp + Firecrawl)
- ✅ Haiku model integration (25x cheaper: $0.03 vs $0.75 with Sonnet)
- ✅ Pure markdown output (removed JSON wrapper)
- ✅ All syntax errors fixed (Unicode characters, f-strings, max_tokens)
- ✅ Pre-commit hooks added (prevents future Unicode bugs)
- 🔄 Awaiting Railway deployment (commit `9146343`)
**Changes from v2.3.1:** Cloudinary-Vercel native integration for optimized image delivery, Vercel Web Analytics integration
**Changes from v2.3:** Type-safe environment variables (astro:env), Astro Content Layer for Directus, Server Islands optimization, Vitest + Container API testing
**Changes from v2.2:** Mux video integration, CSP security, modern Astro features, multi-site SEO strategy, environment variable fixes

---

## 🎯 Executive Summary

Quest v2.2 is a **database-first, AI-native content platform** designed to power three specialized publication sites: relocation.quest, placement.quest, and rainmaker.quest. This revision incorporates critical peer review feedback to ensure production reliability, realistic timelines, and cost transparency.

### Key Improvements in v2.2

**Performance:**
- ✅ Eliminated 200-800ms cold start latency (Neon Launch tier upgrade)
- ✅ Sub-3-second page load guarantee (p95)
- ✅ 4-service architecture prevents noisy-neighbor effects

**Reliability:**
- ✅ Independent scaling for API gateway vs workers
- ✅ Exponential backoff for external API retries
- ✅ Human-in-the-loop quality gate before image generation
- ✅ Cost circuit breakers prevent runaway expenses

**Operational Maturity:**
- ✅ 6-week phased implementation (not rushed 3-week timeline)
- ✅ Comprehensive monitoring and observability
- ✅ Schema governance prevents Directus/FastAPI drift
- ✅ Research cache pilot validates cost assumptions

### Architecture Grade: A-

**Strengths:**
- Database-first design ensures vendor independence
- Cost-conscious with conservative estimates
- Graceful degradation at every layer
- Production-grade operational readiness

**Addressed Concerns:**
- Cold start latency eliminated via always-on compute
- Service separation enables independent scaling
- 40% cache savings validated via pilot program
- Schema governance prevents operational surprises

---

## 💰 Cost Structure (Conservative Estimates)

### Infrastructure: $145/month

| Service | Cost | Purpose | Scaling |
|---------|------|---------|---------|
| Neon Launch Tier | $60/mo | Always-on PostgreSQL | Autoscale 0.25-2 CU |
| Railway API Gateway | $15/mo | FastAPI endpoints | 2-5 replicas |
| Railway Workers | $40/mo | AI agent processing | 1-10 replicas |
| Railway Directus | $20/mo | CMS + GraphQL | Single instance |
| Upstash Redis | $10/mo | BullMQ queue | Managed service |
| **Subtotal** | **$145/mo** | | |

### AI APIs: $455.60/month (Conservative)

| Service | Cost | Usage | Cache Benefit |
|---------|------|-------|---------------|
| Perplexity Sonar Pro | $400/mo | 2000 searches | 25% cache savings |
| Claude 3.5 Sonnet | $52.50/mo | 35M input tokens | Batch API discount |
| OpenAI Embeddings | $0.10/mo | Vector generation | One-time per article |
| Replicate FLUX | $3/mo | Image generation | 1 image/article |
| **Subtotal** | **$455.60/mo** | | |

### Total Operating Cost

```yaml
Infrastructure: $145/month
AI APIs:       $455.60/month
---------------------------------
TOTAL:         $600.60/month

Cost Per Article (1000/mo): $0.60
Cost Per Article (2000/mo): $0.30 (economies of scale)
```

### Cost Comparison vs Old Architecture

```yaml
Old Architecture (Retool + Hasura):
  Infrastructure:  $250/mo (Retool Pro, Hasura Cloud)
  AI APIs:         $275/mo (lower volume, no optimization)
  Total:           $525/mo
  
New Architecture (Quest v2.2):
  Infrastructure:  $145/mo
  AI APIs:         $455.60/mo (higher volume, better optimization)
  Total:           $600.60/mo

Difference: +$75/mo initially

BUT:
- At 2000 articles/mo: $525 old vs $445 new = $80/mo savings
- Vendor independence (no Retool/Hasura lock-in)
- Data sovereignty (schema in our PostgreSQL)
- Scales to 10x traffic without vendor price increases
```

### Why Higher AI Costs?

The new architecture **produces more content at higher quality:**

```yaml
Old Architecture:
  Volume: 500 articles/month
  Quality: Basic (single-pass generation)
  Research: Manual curation
  Cost/article: $0.55

New Architecture:
  Volume: 1000 articles/month
  Quality: Premium (4-agent pipeline)
  Research: AI-powered with caching
  Cost/article: $0.60 (but 2x volume)

Net Result:
  Total content production: 2x increase
  Quality improvement: Significant
  Cost efficiency: Better at scale
```

---

## 🔌 Vercel Native Integrations (v2.3.3)

### Immediate Integrations (Free Tier)

#### 1. Neon-Vercel Direct Integration
**Purpose:** Enable direct database queries from Astro Edge functions without Railway API proxy

**Benefits:**
- Direct PostgreSQL queries from Astro SSR pages
- Better connection pooling (bypasses Railway)
- Automatic environment variable injection
- Reduced latency for read-heavy queries (article listings, search)

**Implementation:**
```typescript
// src/pages/articles/[slug].astro
import { neon } from '@neondatabase/serverless';

export async function getStaticPaths() {
  const sql = neon(import.meta.env.DATABASE_URL);
  const articles = await sql`
    SELECT slug, title FROM articles
    WHERE status = 'published'
  `;
  return articles.map(article => ({
    params: { slug: article.slug }
  }));
}
```

**Cost:** $0 (already paying $60/mo for Neon Launch tier)

#### 2. Vercel Web Analytics
**Purpose:** Privacy-friendly analytics for all 3 .quest sites

**Benefits:**
- GDPR/CCPA compliant (no cookies, no tracking)
- Page views, unique visitors, top pages
- Core Web Vitals monitoring
- No Google Analytics dependency

**Implementation:**
```javascript
// vercel.json
{
  "analytics": {
    "enable": true
  }
}
```

**Cost:** $0 (free tier)

#### 3. Sentry Error Monitoring
**Purpose:** Production error tracking for Astro SSR applications

**Benefits:**
- 5,000 errors/month free tier
- Source map support
- Release tracking
- Performance monitoring

**Implementation:**
```typescript
// astro.config.mjs
import { defineConfig } from 'astro/config';
import sentry from '@sentry/astro';

export default defineConfig({
  integrations: [
    sentry({
      dsn: import.meta.env.SENTRY_DSN,
      tracesSampleRate: 1.0,
    })
  ]
});
```

**Cost:** $0 (5K errors/month free tier)

### Architecture Impact

**Before (v2.3.2):**
```
Browser → Astro (Vercel) → Railway API → Neon DB
```

**After (v2.3.3):**
```
Browser → Astro (Vercel) → Neon DB (direct)
              ↓
         Sentry (errors)
              ↓
    Vercel Analytics (metrics)
```

**Result:**
- 30-50ms latency reduction (no Railway hop for reads)
- Free monitoring + analytics
- Better observability without cost increase

### Rejected Integrations

**Vercel KV (Upstash Redis):** Keep Redis on Railway for centralized backend. Workers need access to BullMQ queues.

**Replicate Connection:** No value - Railway workers call Replicate API, not Vercel.

**Vercel Speed Insights:** Defer until 100+ articles published. Current free analytics sufficient.

---

## 🏗️ System Architecture

### High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         PUBLIC INTERNET                          │
└─────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
              ┌─────▼─────┐ ┌───▼────┐ ┌────▼─────┐
              │ Relocation│ │Placement│ │Rainmaker │
              │   .quest  │ │ .quest  │ │  .quest  │
              │  (Astro)  │ │ (Astro) │ │ (Astro)  │
              └─────┬─────┘ └────┬────┘ └────┬─────┘
                    │            │            │
                    └────────────┼────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   DIRECTUS CMS          │
                    │   GraphQL API Layer     │
                    │   (Railway Service 3)   │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
    ┌─────────▼─────────┐  ┌────▼─────┐  ┌───────▼────────┐
    │  FastAPI Gateway  │  │  BullMQ  │  │   Neon Launch  │
    │  (Railway Svc 1)  │◄─┤  Workers │  │   PostgreSQL   │
    │  Job Submission   │  │ (Svc 2)  │  │   (Always-On)  │
    └───────────────────┘  └────┬─────┘  └───────┬────────┘
                                 │                │
                    ┌────────────▼────────────────▼──┐
                    │      Upstash Redis             │
                    │      BullMQ Queue              │
                    │      (Railway Service 4)       │
                    └────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   EXTERNAL AI APIs      │
                    │  - Perplexity (Research)│
                    │  - Claude (Content)     │
                    │  - OpenAI (Embeddings)  │
                    │  - Replicate (Images)   │
                    └─────────────────────────┘
```

---

## 🚀 4-Service Deployment Architecture

### Service 1: FastAPI API Gateway

**Purpose:** Public HTTP endpoints for job submission and status checks

```yaml
Service: quest-api-gateway
Platform: Railway
Docker: Single container (FastAPI only)

Responsibilities:
  - Accept article generation requests
  - Enqueue jobs in BullMQ
  - Return job status via polling endpoint
  - Health checks and metrics

Scaling:
  Trigger: HTTP request volume
  Min Replicas: 2 (high availability)
  Max Replicas: 5
  Auto-scale: >80% CPU or >200ms p95 latency

Resources:
  CPU: 0.5 vCPU
  Memory: 512MB
  Network: Low bandwidth

Cost: $15/month
```

**Key Endpoints:**

```python
POST /api/articles/generate
  Body: { "topic", "target_site", "priority" }
  Response: { "job_id", "status": "queued" }

GET /api/articles/status/{job_id}
  Response: { "status", "progress", "result_url" }

GET /health
  Response: { "status": "healthy", "queue_depth", "worker_count" }
```

### Service 2: BullMQ Workers

**Purpose:** Background AI agent processing (high compute)

```yaml
Service: quest-workers
Platform: Railway
Docker: Same image as API, different start command

Responsibilities:
  - Poll BullMQ queue for jobs
  - Execute 4-agent pipeline:
    * ResearchAgent (Perplexity + pgvector cache)
    * ContentAgent (Claude Sonnet 3.5)
    * EditorAgent (Quality scoring)
    * ImageAgent (FLUX via Replicate)
  - Update article status in Neon
  - Handle retries with exponential backoff

Scaling:
  Trigger: BullMQ queue depth
  Min Replicas: 1 (idle most of the time)
  Max Replicas: 10 (burst processing)
  Auto-scale: Queue depth >20 jobs

Resources:
  CPU: 2 vCPU (LLM API calls are CPU-bound)
  Memory: 4GB (cache embeddings in memory)
  Network: High bandwidth (API calls)

Cost: $40/month (scales with load)
```

**Worker Configuration:**

```javascript
// BullMQ Worker with exponential backoff
const worker = new Worker('articles', async (job) => {
  const { topic, target_site } = job.data;
  
  // 4-agent pipeline
  const research = await ResearchAgent.run(topic);
  const content = await ContentAgent.run(research);
  const quality = await EditorAgent.score(content);
  
  if (quality.score < 70) {
    throw new Error('Quality threshold not met');
  }
  
  // HITL gate: only generate image if quality > 85
  if (quality.score > 85) {
    const image = await ImageAgent.generate(content);
    return { content, image, quality, auto_published: true };
  }
  
  return { content, quality, needs_review: true };
}, {
  connection: redis,
  concurrency: 5,  // Process 5 jobs in parallel
  limiter: {
    max: 10,       // Max 10 jobs per minute (rate limit)
    duration: 60000
  }
});

// Retry policy
const jobOptions = {
  attempts: 5,
  backoff: {
    type: 'exponential',
    delay: 2000  // 2s, 4s, 8s, 16s, 32s
  },
  removeOnComplete: 100,
  removeOnFail: 500
};
```

### Service 3: Directus CMS

**Purpose:** Content management UI and GraphQL API for Astro sites

```yaml
Service: quest-directus
Platform: Railway
Docker: Official directus/directus:latest

Responsibilities:
  - Admin UI for content editors
  - GraphQL API for Astro sites
  - Human review workflow (HITL)
  - Asset management (Cloudinary integration)

Scaling:
  Trigger: Manual (rarely needed)
  Replicas: 1 (single instance sufficient)
  Note: GraphQL queries are read-only, low load

Resources:
  CPU: 1 vCPU
  Memory: 2GB
  Storage: Stateless (data in Neon)

Cost: $20/month

Database Connection:
  User: directus_user (NO DDL permissions)
  Permissions: SELECT, INSERT, UPDATE, DELETE only
  Schema Management: DISABLED (prevents drift)
```

**Directus Configuration:**

```yaml
# docker-compose.yml
services:
  directus:
    image: directus/directus:latest
    environment:
      # Neon connection (restricted user)
      DB_CLIENT: postgres
      DB_HOST: ${NEON_HOST}
      DB_PORT: 5432
      DB_DATABASE: neondb
      DB_USER: directus_user  # NOT neondb_owner
      DB_PASSWORD: ${DIRECTUS_DB_PASSWORD}
      
      # Security
      KEY: ${DIRECTUS_KEY}
      SECRET: ${DIRECTUS_SECRET}
      ADMIN_EMAIL: ${ADMIN_EMAIL}
      ADMIN_PASSWORD: ${ADMIN_PASSWORD}
      
      # Schema Management (DISABLED)
      SCHEMA_APPLY_AFTER: false
      COLLECTIONS_ADMIN_ACCESS: read_only
      
      # Performance
      CACHE_ENABLED: true
      CACHE_STORE: redis
      REDIS: ${REDIS_URL}
      
      # Asset Storage (Cloudinary)
      STORAGE_LOCATIONS: cloudinary
      STORAGE_CLOUDINARY_CLOUD_NAME: ${CLOUDINARY_CLOUD}
      STORAGE_CLOUDINARY_API_KEY: ${CLOUDINARY_KEY}
      STORAGE_CLOUDINARY_API_SECRET: ${CLOUDINARY_SECRET}
```

**GraphQL API Usage:**

```graphql
# Astro sites query this endpoint
query GetArticles($site: String!) {
  articles(
    filter: { target_site: { _eq: $site }, status: { _eq: "published" } }
    sort: ["-published_date"]
    limit: 20
  ) {
    id
    title
    slug
    excerpt
    hero_image_url
    published_date
    author {
      name
      avatar_url
    }
  }
}
```

### Service 4: Upstash Redis (Managed)

**Purpose:** BullMQ job queue persistence

```yaml
Service: quest-redis
Platform: Upstash (managed Redis)
Plan: Pro ($10/month)

Responsibilities:
  - Store queued jobs
  - Track job status and progress
  - Enable retries and dead-letter queue
  - Provide real-time queue metrics

Features:
  - Persistent storage (jobs survive restarts)
  - Automatic backups
  - 99.99% uptime SLA
  - REST API for monitoring

Alternative: Railway Redis Add-on ($5/mo)
  - Lower cost but less features
  - No built-in backups
  - Recommended for development only
```

---

## 💾 Database Architecture (Neon PostgreSQL)

### Neon Configuration: Launch Tier (Critical)

```yaml
Plan: Launch Tier ($60/month minimum)
Why: Eliminates 200-800ms cold start latency

Critical Settings:
  auto_suspend: DISABLED ✅
  compute_size: 0.25 CU minimum (always-on)
  autoscaling: Enabled (0.25 → 2 CU on demand)
  storage: 10 GB included (scales automatically)
  
Performance Impact:
  Cold Query (Free Tier): 800ms worst case
  Hot Query (Launch Tier): 30-50ms
  Improvement: 16x faster

Reliability:
  Uptime: 99.9% SLA
  Backups: Daily automatic
  Point-in-time recovery: 7 days
  Branching: Unlimited (for testing)

Cost Scaling:
  Base: $60/month (includes 300 compute hours)
  Overage: $0.16/compute hour
  Storage: $0.000164/GB-hour ($3.69/month per 10GB)
  
  Example at 2000 articles/month:
    Compute: ~450 hours = $60 + $24 = $84/month
    Storage: 20 GB = $7.38/month
    Total: ~$90/month
```

### Schema Design

**Core Tables:**

```sql
-- 1. Articles (main content)
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    hero_image_url TEXT,
    
    -- Multi-site support
    target_site VARCHAR(50) NOT NULL, -- 'relocation', 'placement', 'rainmaker'
    
    -- Metadata
    status VARCHAR(20) DEFAULT 'draft', -- draft, review, published, archived
    quality_score INTEGER, -- 0-100 from EditorAgent
    reading_time_minutes INTEGER,
    
    -- SEO
    meta_title TEXT,
    meta_description TEXT,
    keywords TEXT[],
    
    -- Publishing
    published_date TIMESTAMPTZ,
    author_id UUID REFERENCES users(id),
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_articles_site_status ON articles(target_site, status),
    INDEX idx_articles_published ON articles(published_date DESC) WHERE status = 'published',
    INDEX idx_articles_slug ON articles(slug)
);

-- 2. Research Cache (vector similarity search)
CREATE TABLE article_research (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_query TEXT NOT NULL,
    embedding vector(1536), -- OpenAI ada-002 embeddings
    
    -- Research data
    research_json JSONB NOT NULL,
    source_urls TEXT[],
    
    -- Cache metadata
    embedding_model_version VARCHAR(50) DEFAULT 'text-embedding-ada-002',
    cache_hits INTEGER DEFAULT 0,
    last_accessed TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '30 days'),
    
    -- Indexes
    INDEX idx_research_topic ON article_research USING GIN(to_tsvector('english', topic_query)),
    INDEX idx_research_embedding ON article_research USING ivfflat(embedding vector_cosine_ops)
      WITH (lists = 100)
);

-- 3. Job Status (BullMQ tracking)
CREATE TABLE job_status (
    job_id VARCHAR(255) PRIMARY KEY,
    article_id UUID REFERENCES articles(id),
    
    status VARCHAR(50) NOT NULL, -- queued, processing, completed, failed
    progress INTEGER DEFAULT 0, -- 0-100
    current_step VARCHAR(100), -- research, content, editor, image
    
    -- Cost tracking
    cost_breakdown JSONB, -- { "research": 0.20, "content": 0.15, ... }
    total_cost DECIMAL(10,4),
    
    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    INDEX idx_job_status ON job_status(status, created_at DESC)
);

-- 4. Users (for Directus auth)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'editor', -- admin, editor, viewer
    avatar_url TEXT,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);
```

**PostgreSQL Extensions:**

```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- UUID generation
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- Fuzzy text search
CREATE EXTENSION IF NOT EXISTS "vector";         -- pgvector for embeddings
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements"; -- Query performance monitoring
CREATE EXTENSION IF NOT EXISTS "btree_gin";      -- GIN indexes for arrays
CREATE EXTENSION IF NOT EXISTS "pg_cron";        -- Scheduled tasks (cache cleanup)
```

### Database User Roles (Least Privilege)

```sql
-- 1. neondb_owner (DBA - emergency use only)
-- Already exists, has ALL PRIVILEGES

-- 2. fastapi_user (application role)
CREATE USER fastapi_user WITH PASSWORD '${FASTAPI_DB_PASSWORD}';
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO fastapi_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO fastapi_user;
-- NO DDL permissions (no CREATE, ALTER, DROP)

-- 3. directus_user (CMS role - restricted)
CREATE USER directus_user WITH PASSWORD '${DIRECTUS_DB_PASSWORD}';
GRANT SELECT, INSERT, UPDATE, DELETE ON articles, users IN SCHEMA public TO directus_user;
GRANT USAGE ON SEQUENCE articles_id_seq TO directus_user;
-- NO DDL permissions (prevents schema drift)
-- NO access to article_research, job_status (security)

-- 4. readonly_user (analytics/monitoring)
CREATE USER readonly_user WITH PASSWORD '${READONLY_DB_PASSWORD}';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
```

### Schema Governance: Preventing Directus/FastAPI Drift

**The Risk:**
If Directus has DDL permissions, editors could add columns via the UI, causing FastAPI to be out of sync with the database schema.

**The Solution (3-Layer Defense):**

```yaml
Layer_1_Database_Permissions:
  # Physical barrier to schema changes
  directus_user:
    permissions: [SELECT, INSERT, UPDATE, DELETE]
    ddl_blocked: [CREATE, ALTER, DROP]
    
  result: "Directus CANNOT execute ALTER TABLE even if it tries"

Layer_2_Directus_Configuration:
  # UI barrier to schema management
  SCHEMA_APPLY_AFTER: false
  COLLECTIONS_ADMIN_ACCESS: read_only
  
  result: "Schema management section hidden in Directus UI"

Layer_3_Organizational_Process:
  # Human barrier via code review
  all_schema_changes:
    1. Propose via GitHub issue
    2. Write SQL migration file (migrations/YYYY_MM_DD_description.sql)
    3. Update FastAPI models (app/models/*.py)
    4. Update Pydantic schemas (app/schemas/*.py)
    5. Code review required
    6. Deploy order: SQL → FastAPI → Astro
    7. Directus auto-discovers (no action needed)
  
  result: "Controlled, predictable, safe schema evolution"
```

**Migration Example:**

```sql
-- migrations/2025_10_15_add_reading_time.sql
BEGIN;

ALTER TABLE articles 
ADD COLUMN reading_time_minutes INTEGER;

-- Backfill existing articles
UPDATE articles 
SET reading_time_minutes = (LENGTH(content) / 1000)
WHERE reading_time_minutes IS NULL;

COMMIT;
```

```python
# app/models/article.py (update SQLAlchemy model)
class Article(Base):
    __tablename__ = "articles"
    
    # ... existing fields ...
    reading_time_minutes: Mapped[Optional[int]] = mapped_column(Integer)

# app/schemas/article.py (update Pydantic schema)
class ArticleResponse(BaseModel):
    # ... existing fields ...
    reading_time_minutes: Optional[int] = None
```

**Deployment Sequence:**

```bash
# Step 1: Run migration on Neon
psql $DATABASE_URL -f migrations/2025_10_15_add_reading_time.sql

# Step 2: Verify Directus auto-discovers
# (Directus introspects schema, sees new column automatically)

# Step 3: Deploy FastAPI with updated models
railway up --service quest-api-gateway
railway up --service quest-workers

# Step 4: Deploy Astro with updated GraphQL queries (if needed)
vercel deploy --prod
```

---

## 🤖 AI Agent Pipeline

### 4-Agent Architecture

```yaml
Pipeline_Flow:
  0. Check QUEST_RELOCATION_RESEARCH.md (topic validation)
  1. ResearchAgent → 2. ContentAgent → 3. EditorAgent → 4. ImageAgent

Total_Latency: 45-60 seconds per article
Cost_Per_Article: $0.45 (with 25% research cache hit rate)
```

**Operational Document Integration:**
All agents reference `QUEST_RELOCATION_RESEARCH.md` as the single source of truth for:
- Topic priority queue (993 pending topics)
- Content quality standards (2000+ words, 5+ citations, etc.)
- SEO data (search volume, CPC, difficulty)
- Completed topics tracking (avoid duplication)
- Category distribution strategy (200 digital nomad visas, 150 golden visas, etc.)

### Agent 1: ResearchAgent (Perplexity + pgvector Cache)

**Purpose:** Gather factual information about the topic

**⚠️ CRITICAL:** Before any research, ResearchAgent MUST:
1. Check `QUEST_RELOCATION_RESEARCH.md` for topic priority and existing coverage
2. Avoid duplicate topics already published
3. Follow content quality standards defined in the research document
4. Use SEO data (search volume, CPC, difficulty) to inform research depth

**📋 Task Orchestration Enhancement (TIER 1 Priority):**
Integrate **TaskMaster AI** (`task-master-ai` npm package) to enforce these prerequisites:
- Define task DAG (Directed Acyclic Graph) for article generation workflow
- Enforce research governance as mandatory prerequisite before Perplexity API calls
- Automatic cost tracking per task
- Prevents "skipped prerequisite" bugs

```yaml
Tools:
  - Perplexity Sonar Pro API (primary research)
  - pgvector similarity search (cache lookup)
  - OpenAI Embeddings (query vectorization)
  - QUEST_RELOCATION_RESEARCH.md reference (operational guidance)

Cost:
  Cache Hit: $0.00 (free)
  Cache Miss: $0.20 (Perplexity search)
  Embedding: $0.000016 (negligible)

Workflow:
  1. User requests article on "Cyprus digital nomad visa"
  2. Generate embedding for query (OpenAI ada-002)
  3. Search article_research for similar topics (cosine similarity > 0.75)
  4. IF cache hit:
     - Return cached research
     - Increment cache_hits counter
     - Update last_accessed timestamp
  5. IF cache miss:
     - Query Perplexity Sonar Pro
     - Store research + embedding in database
     - Set expires_at = NOW() + 30 days
  6. Return research data to ContentAgent
```

**Schema Validation Enhancement (TIER 1 Priority):**
Integrate **GitHub Spec Kit** (`@github/spec-kit` npm package) for runtime validation:
- Create `schemas/article_output.json` specification
- Validate all agent outputs against schema before database insertion
- Catches schema mismatches automatically (e.g., JSON vs markdown content field)
- Self-documenting schemas reduce documentation burden

**Implementation:**

```python
# agents/research.py
from openai import OpenAI
from anthropic import Anthropic
import asyncpg

class ResearchAgent:
    def __init__(self, db_pool, openai_client, perplexity_client):
        self.db = db_pool
        self.openai = openai_client
        self.perplexity = perplexity_client
        
    async def run(self, topic: str) -> dict:
        # 1. Generate embedding
        embedding = await self.openai.embeddings.create(
            model="text-embedding-ada-002",
            input=topic
        )
        vector = embedding.data[0].embedding
        
        # 2. Check cache (pgvector similarity search)
        cache_hit = await self.db.fetchrow("""
            SELECT research_json, cache_hits, id
            FROM article_research
            WHERE 1 - (embedding <=> $1::vector) > 0.75  -- cosine similarity
            AND expires_at > NOW()
            ORDER BY 1 - (embedding <=> $1::vector) DESC
            LIMIT 1
        """, vector)
        
        if cache_hit:
            # Cache hit! Update stats and return
            await self.db.execute("""
                UPDATE article_research
                SET cache_hits = cache_hits + 1,
                    last_accessed = NOW()
                WHERE id = $1
            """, cache_hit['id'])
            
            return cache_hit['research_json']
        
        # 3. Cache miss - query Perplexity
        research = await self.perplexity.chat.completions.create(
            model="sonar-pro",
            messages=[{
                "role": "user",
                "content": f"Research: {topic}. Provide factual information, statistics, and expert insights."
            }]
        )
        
        # 4. Store in cache
        research_data = {
            "topic": topic,
            "content": research.choices[0].message.content,
            "citations": research.citations,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.db.execute("""
            INSERT INTO article_research 
            (topic_query, embedding, research_json, expires_at)
            VALUES ($1, $2, $3, NOW() + INTERVAL '30 days')
        """, topic, vector, research_data)
        
        return research_data
```

**Cache Performance Tuning:**

```sql
-- IVFFlat index tuning
CREATE INDEX idx_research_embedding 
ON article_research 
USING ivfflat(embedding vector_cosine_ops)
WITH (lists = 100);  -- SQRT(total_rows), tune as data grows

-- Query performance settings
SET ivfflat.probes = 10;  -- Higher = better recall, slower queries
-- Target: <200ms for similarity search
```

**Cache Maintenance:**

```sql
-- Scheduled cleanup (via pg_cron)
SELECT cron.schedule(
  'cache-cleanup',
  '0 2 * * *',  -- Daily at 2 AM
  $$
    DELETE FROM article_research 
    WHERE expires_at < NOW() 
    AND cache_hits < 3;  -- Remove unused entries
  $$
);
```

### Agent 2: ContentAgent (Claude 3.5 Sonnet)

**Purpose:** Generate high-quality article content from research

```yaml
Model: Claude 3.5 Sonnet
Cost: $3/M input tokens, $15/M output tokens
Batch API: 50% discount
Average Cost: $0.15 per article

Input Token Budget:
  Research data: 3,000 tokens
  System prompt: 1,000 tokens
  Article structure: 500 tokens
  Total: ~4,500 input tokens = $0.0135

Output Token Budget:
  Article content: 2,500 tokens (1500-word article)
  Metadata: 200 tokens
  Total: ~2,700 output tokens = $0.0405
  
  With Batch API 50% discount: $0.02025

Total Per Article: $0.034 (round to $0.04)

Workflow:
  1. Receive research data from ResearchAgent
  2. Generate article outline (structure)
  3. Write full article content (long-context, streaming)
  4. Extract metadata (title, excerpt, keywords)
  5. Return structured content to EditorAgent
```

**Implementation:**

```python
# agents/content.py
from anthropic import Anthropic

class ContentAgent:
    def __init__(self, client: Anthropic):
        self.client = client
        
    async def run(self, research: dict, target_site: str) -> dict:
        # Site-specific writing style
        style_guides = {
            "relocation": "Practical, expat-focused, conversational",
            "placement": "Data-driven, analytical, professional",
            "rainmaker": "Entrepreneurial, action-oriented, motivational"
        }
        
        prompt = f"""You are a content writer for {target_site}.quest.

Research Data:
{research['content']}

Task: Write a comprehensive 1500-word article based on this research.

Style: {style_guides[target_site]}

Requirements:
- Engaging introduction with hook
- 5-7 main sections with headers
- Data-driven insights from research
- Actionable takeaways
- SEO-optimized (natural keyword placement)
- Cite sources from research

Format: Return JSON with:
{{
  "title": "...",
  "excerpt": "150-character summary",
  "content": "Full article in Markdown",
  "keywords": ["keyword1", "keyword2", ...],
  "reading_time_minutes": X
}}
"""
        
        # Use Batch API for 50% discount (not urgent, process overnight)
        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return json.loads(response.content[0].text)
```

### Agent 3: EditorAgent (Quality Gating)

**Purpose:** Score article quality and determine publication workflow

```yaml
Model: Claude 3.5 Sonnet (fast inference)
Cost: $0.005 per article (small prompt)

Quality Scoring:
  0-100 scale across dimensions:
    - Factual accuracy (research citations)
    - Writing quality (readability, grammar)
    - SEO optimization (keywords, structure)
    - Engagement potential (hooks, CTAs)

Workflow Decision Tree (UPDATED Oct 9, 2025 - Testing Mode):
  Score ≥ 75: Auto-publish → ImageAgent (was ≥85)
  Score 60-74: Human review → HITL queue (was 70-84)
  Score < 60: Reject → retry or discard (was <70)

  Note: Thresholds temporarily lowered for testing. Will revert to 85/70 once pipeline validated.

Average Distribution:
  Auto-publish: 60% (saves human time)
  Human review: 30% (catches edge cases)
  Reject: 10% (prevents low-quality content)
```

**Implementation:**

```python
# agents/editor.py
from anthropic import Anthropic

class EditorAgent:
    def __init__(self, client: Anthropic):
        self.client = client
        
    async def score(self, article: dict) -> dict:
        prompt = f"""You are a content quality analyst.

Article Title: {article['title']}
Article Content: {article['content'][:1000]}... (truncated)
Keywords: {article['keywords']}

Evaluate this article on a 0-100 scale across these dimensions:
1. Factual Accuracy (citations, data correctness)
2. Writing Quality (grammar, readability, flow)
3. SEO Optimization (keyword usage, structure)
4. Engagement (hooks, actionable insights, CTAs)

Return JSON:
{{
  "overall_score": X,
  "dimensions": {{
    "accuracy": X,
    "writing": X,
    "seo": X,
    "engagement": X
  }},
  "feedback": "Brief explanation of score",
  "decision": "publish" | "review" | "reject"
}}
"""
        
        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return json.loads(response.content[0].text)
```

**HITL (Human-in-the-Loop) Integration:**

```javascript
// BullMQ Flow with human review checkpoint
const articleFlow = new FlowProducer({ connection: redis });

await articleFlow.add({
  name: 'generate-article',
  queueName: 'articles',
  data: { topic, target_site },
  children: [
    {
      name: 'research',
      queueName: 'research-queue',
      data: { topic }
    },
    {
      name: 'content',
      queueName: 'content-queue',
      data: {},
      children: [
        {
          name: 'editor',
          queueName: 'editor-queue',
          data: {},
          children: [
            {
              name: 'human-review',  // ← HITL checkpoint
              queueName: 'human-review-queue',
              data: {},
              opts: {
                // Block here until human approves/rejects
                waitForChildren: true,
                delay: 0  // Process immediately
              },
              children: [
                {
                  name: 'image',  // Only runs if approved
                  queueName: 'image-queue',
                  data: {}
                }
              ]
            }
          ]
        }
      ]
    }
  ]
});
```

**Directus HITL UI:**

```yaml
Workflow in Directus:
  1. EditorAgent creates article with status = "review"
  2. Human editor receives notification in Directus
  3. Editor reviews article in admin UI
  4. Editor can:
     - Approve → status = "approved", triggers ImageAgent
     - Edit & Approve → make changes, then approve
     - Reject → status = "rejected", job ends
  5. Approved articles proceed to image generation
```

### Agent 4: ImageAgent (FLUX via Replicate)

**Purpose:** Generate hero images for articles

```yaml
Model: FLUX.1 Schnell (via Replicate)
Cost: $0.003 per image
Quality: Photorealistic, suitable for hero images

Workflow:
  1. Receive approved article from EditorAgent
  2. Extract image prompt from article title + excerpt
  3. Generate image via Replicate FLUX API
  4. Upload to Cloudinary (CDN)
  5. Return image URL to article record
  6. Mark article as "published"

Prompt Engineering:
  Template: "Professional photograph of {topic}, {style}, high quality, editorial style"
  Example: "Professional photograph of Lisbon Portugal digital nomad workspace, modern aesthetic, high quality, editorial style"
```

**Implementation:**

```python
# agents/image.py
import replicate
import cloudinary.uploader

class ImageAgent:
    def __init__(self, replicate_token: str, cloudinary_config: dict):
        self.replicate = replicate
        self.cloudinary = cloudinary_config
        
    async def generate(self, article: dict) -> str:
        # Craft image prompt from article
        prompt = self._create_prompt(
            title=article['title'],
            excerpt=article['excerpt'],
            site=article['target_site']
        )
        
        # Generate via FLUX
        output = await replicate.run(
            "black-forest-labs/flux-schnell",
            input={
                "prompt": prompt,
                "num_outputs": 1,
                "aspect_ratio": "16:9",  # Hero image format
                "output_format": "jpg",
                "output_quality": 90
            }
        )
        
        image_url = output[0]
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            image_url,
            folder=f"quest/{article['target_site']}",
            public_id=article['slug'],
            transformation=[
                {"width": 1200, "height": 675, "crop": "fill"},
                {"quality": "auto"},
                {"fetch_format": "auto"}
            ]
        )
        
        return result['secure_url']
    
    def _create_prompt(self, title: str, excerpt: str, site: str) -> str:
        # Site-specific image styles
        styles = {
            "relocation": "modern, professional, international",
            "placement": "data visualization, charts, infographic style",
            "rainmaker": "entrepreneurial, dynamic, aspirational"
        }
        
        return f"Professional editorial photograph: {title}. {excerpt[:100]}. Style: {styles[site]}, high quality, photorealistic, 16:9 aspect ratio"
```

---

## 🎨 Template Intelligence System (v2.4.0)

### Overview

**The Template Intelligence System** is Quest's revolutionary content architecture that analyzes SERP winners to understand what actually ranks, then combines strategic depth (archetype) with user-facing structure (template) to generate optimized content.

**Core Innovation:** Distinguishes between **ARCHETYPE** (strategic depth - what ranks) and **TEMPLATE** (visual structure - what users expect).

**Example:**
- Surface: "Top 10 Digital Nomad Visas" (looks like a simple listicle)
- Reality: 12,000-word skyscraper with 14 modules, ranking for 750+ keywords

### The Problem We're Solving

**Naive approach:**
1. See "Top 10 Visas" ranking #1
2. Classify: "It's a listicle"
3. Generate: 2000-word listicle
4. Result: Ranks #15 (not competitive)

**Template Intelligence approach:**
1. See "Top 10 Visas" ranking #1
2. Analyze with Serper + Firecrawl: "Surface = listicle, Depth = skyscraper"
3. Detect: 12k words, 14 modules, 4 schemas, 45 internal links
4. Generate: Skyscraper disguised as listicle
5. Result: Ranks #1-3 (competitive)

### Architecture Components

**1. SERP Intelligence Pipeline**
```
User requests topic → Check serp_intelligence cache
↓
If no cache → Serper.dev (top 10 results)
↓
Firecrawl scrapes top 3-5 competitors
↓
TemplateDetector analyzes:
  - Word count & section depth
  - Module detection (FAQ, calculator, tables)
  - Internal linking patterns
  - Schema stacking
  - E-E-A-T signals (expert quotes, case studies, citations)
↓
Recommendation engine → {archetype, template, modules, word_count, module_count}
↓
Store in serp_intelligence + scraped_competitors tables
```

**2. Content Archetypes (5 Strategic Approaches)**

| Archetype | Word Count | Modules | Keywords | Use Case |
|-----------|------------|---------|----------|----------|
| **Skyscraper** | 8,000-15,000 | 12-20 | 500-2000 | Comprehensive domain authority hub |
| **Cluster Hub** | 4,000-6,000 | 8-12 | 200-500 | Topic navigation center |
| **Deep Dive Specialist** | 3,000-5,000 | 8-12 | 50-200 | Definitive answer to ONE specific question |
| **Comparison Matrix** | 3,000-4,000 | 9-12 | 100-300 | Interactive decision engine |
| **News Hub** | 2,000-3,000 | 7-10 | 50-150 | Living document tracking changes |

**3. Visual Templates (12 User-Facing Structures)**

- Ultimate Guide (most common wrapper)
- Listicle (numbered rankings)
- Comparison (X vs Y)
- Location Guide (country/city-specific)
- Deep Dive Tutorial (how-to)
- Category Pillar (topic overview)
- Problem-Solution
- News/Update
- Case Study
- Data Study
- Tool/Calculator
- Interview/Q&A

**4. Modular Components Library (35 Building Blocks)**

- Content modules (15): TldrSection, KeyTakeaways, StatsCallout, ProsConsList, FaqAccordion, etc.
- Interactive modules (10): Calculator, Quiz, InteractiveMap, FilterSystem, CostEstimator, etc.
- Schema modules (10): ArticleSchema, HowToSchema, FaqSchema, ReviewSchema, BreadcrumbSchema, etc.

### Database Schema (5 New Tables)

```sql
-- 1. Content Archetypes
CREATE TABLE content_archetypes (
    archetype_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    word_count_min INTEGER NOT NULL,
    word_count_max INTEGER NOT NULL,
    module_count_min INTEGER NOT NULL,
    module_count_max INTEGER NOT NULL,
    keyword_target_min INTEGER NOT NULL,
    keyword_target_max INTEGER NOT NULL,
    schema_stack TEXT[], -- ['Article', 'FAQPage', 'HowTo', 'ItemList']
    requires_expert_quotes BOOLEAN DEFAULT false,
    requires_case_studies BOOLEAN DEFAULT false,
    requires_calculator BOOLEAN DEFAULT false,
    eeat_level VARCHAR(20), -- 'maximum', 'high', 'medium'
    ymyl_suitable BOOLEAN DEFAULT false,
    description TEXT
);

-- 2. Content Templates
CREATE TABLE content_templates (
    template_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    visual_pattern TEXT NOT NULL, -- "Top N [Topic]", "Complete Guide to [Topic]"
    compatible_archetypes TEXT[], -- ['skyscraper', 'cluster_hub']
    required_modules TEXT[], -- ['tldr', 'faq', 'calculator']
    optional_modules TEXT[],
    astro_component VARCHAR(100) NOT NULL, -- 'UltimateGuide.astro'
    schema_types TEXT[], -- ['Article', 'HowTo', 'FAQPage']
    description TEXT
);

-- 3. SERP Intelligence (Cached Analysis)
CREATE TABLE serp_intelligence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    keyword TEXT NOT NULL UNIQUE,
    analyzed_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '30 days'),

    -- Recommendations
    dominant_archetype VARCHAR(50), -- 'skyscraper'
    recommended_template VARCHAR(50), -- 'ultimate-guide'
    target_word_count INTEGER,
    target_module_count INTEGER,
    required_modules TEXT[],

    -- SERP Analysis
    top_10_urls TEXT[],
    featured_snippet_url TEXT,
    people_also_ask TEXT[],
    avg_word_count INTEGER,
    avg_module_count INTEGER,
    common_schemas TEXT[],

    -- Metadata
    confidence_score DECIMAL(3,2), -- 0.85
    analysis_notes JSONB
);

-- 4. Scraped Competitors
CREATE TABLE scraped_competitors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    serp_intelligence_id UUID REFERENCES serp_intelligence(id),
    url TEXT NOT NULL,
    position INTEGER, -- 1-10
    scraped_at TIMESTAMPTZ DEFAULT NOW(),

    -- Detected Properties
    detected_archetype VARCHAR(50),
    surface_template VARCHAR(50),
    word_count INTEGER,
    section_count INTEGER,
    modules_detected TEXT[],
    internal_links_count INTEGER,
    schemas_found TEXT[],

    -- E-E-A-T Signals
    has_expert_quotes BOOLEAN,
    has_case_studies BOOLEAN,
    has_citations BOOLEAN,
    citations_count INTEGER,
    has_author_bio BOOLEAN,
    update_date TIMESTAMPTZ,

    -- Raw Data
    html_content TEXT,
    markdown_content TEXT,
    metadata JSONB
);

-- 5. Template Performance (Learning)
CREATE TABLE template_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES articles(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Strategy Used
    target_archetype VARCHAR(50),
    surface_template VARCHAR(50),
    modules_used TEXT[],
    word_count INTEGER,
    module_count INTEGER,

    -- Quality Metrics
    quality_score INTEGER,
    eeat_score JSONB, -- {'experience': 8, 'expertise': 9, ...}

    -- Future: SERP Performance (to be added)
    -- keyword_rankings JSONB,
    -- citations_count INTEGER,
    -- avg_position DECIMAL(4,2)
);

-- 6. Add archetype/template fields to existing articles table
ALTER TABLE articles ADD COLUMN target_archetype VARCHAR(50);
ALTER TABLE articles ADD COLUMN surface_template VARCHAR(50);
ALTER TABLE articles ADD COLUMN modules_used TEXT[];

CREATE INDEX idx_articles_archetype ON articles(target_archetype);
CREATE INDEX idx_articles_template ON articles(surface_template);
CREATE INDEX idx_serp_keyword ON serp_intelligence(keyword);
CREATE INDEX idx_scraped_url ON scraped_competitors(url);
```

### Enhanced Agent Pipeline

**Updated 7-Agent Flow:**

```yaml
Pipeline_Flow:
  0. Check QUEST_RELOCATION_RESEARCH.md (topic validation)
  1. ResearchAgent (gather intelligence)

  NEW → 1.5. TemplateDetector (SERP intelligence)
           - Query serp_intelligence cache
           - If no cache: Run Serper + Firecrawl analysis
           - Detect: archetype, template, modules, word count
           - Store recommendations

  2. ContentAgent (generate with archetype + template guidance)
     - Receives: research data + archetype requirements + template structure
     - Generates: markdown following archetype depth + template style

  3. EditorAgent (quality scoring)
  4. ImageAgent (FLUX + Cloudinary)

  NEW → 4.5. SchemaGenerator (multi-schema JSON-LD)
           - Load schema templates for archetype
           - Stack multiple schemas (Article + FAQPage + HowTo + ItemList)
           - Inject into <head>

Total_Latency: 60-90 seconds per article (added 15-30s for template detection)
Cost_Per_Article: $0.50-0.65 (added Serper + Firecrawl: ~$0.05-0.10)
```

**TemplateDetector Agent Details:**

```python
# agents/template_detector.py

class TemplateDetector:
    """
    Analyzes SERP winners to detect content archetypes and recommend templates
    """

    def __init__(self, serper_client, firecrawl_client, db_pool):
        self.serper = serper_client
        self.firecrawl = firecrawl_client
        self.db = db_pool

    async def analyze(self, keyword: str) -> dict:
        """
        Main analysis workflow
        """
        # 1. Check cache
        cached = await self._check_cache(keyword)
        if cached and not self._is_expired(cached):
            return cached

        # 2. Get SERP results
        serp_results = await self.serper.search(keyword)
        top_urls = serp_results['organic'][:5]

        # 3. Scrape competitors
        scraped_pages = await self._scrape_competitors(top_urls)

        # 4. Detect archetypes
        detected_archetypes = [
            self._detect_archetype(page) for page in scraped_pages
        ]

        # 5. Determine dominant archetype
        dominant = self._get_dominant_archetype(detected_archetypes)

        # 6. Recommend template
        template = self._recommend_template(dominant, scraped_pages)

        # 7. Identify required modules
        modules = self._extract_common_modules(scraped_pages)

        # 8. Calculate targets
        avg_word_count = sum(p['word_count'] for p in scraped_pages) / len(scraped_pages)
        avg_module_count = sum(len(p['modules']) for p in scraped_pages) / len(scraped_pages)

        # 9. Store in cache
        recommendations = {
            'keyword': keyword,
            'dominant_archetype': dominant,
            'recommended_template': template,
            'target_word_count': int(avg_word_count * 1.1),  # Aim 10% higher
            'target_module_count': int(avg_module_count * 1.1),
            'required_modules': modules,
            'confidence_score': self._calculate_confidence(detected_archetypes)
        }

        await self._store_cache(recommendations, serp_results, scraped_pages)

        return recommendations

    def _detect_archetype(self, page: dict) -> str:
        """
        Multi-dimensional archetype detection
        """
        word_count = page['word_count']
        module_count = len(page['modules'])
        internal_links = page['internal_links_count']
        has_eeat = page['has_expert_quotes'] or page['has_case_studies']

        # Scoring algorithm
        scores = {
            'skyscraper': self._score_skyscraper(word_count, module_count, internal_links, has_eeat),
            'cluster_hub': self._score_cluster_hub(word_count, internal_links),
            'deep_dive': self._score_deep_dive(word_count, module_count),
            'comparison_matrix': self._score_comparison(page),
            'news_hub': self._score_news(page)
        }

        return max(scores, key=scores.get)
```

### E-E-A-T Optimization for YMYL

**Quest's entire niche is YMYL-heavy:**
- Visa/immigration = YMYL (life-changing decisions)
- Tax advice = YMYL (financial impact)
- Legal processes = YMYL (legal consequences)

**Archetype E-E-A-T Requirements:**

| Archetype | Experience | Expertise | Authoritativeness | Trustworthiness |
|-----------|-----------|-----------|-------------------|-----------------|
| **Skyscraper** | 2-3 case studies | Lawyer quotes, data tables | .gov sources, expert bios | Update dates, fact-checking |
| **Deep Dive** | 1 case study | Expert quotes, official docs | .gov sources | Accuracy disclaimer |
| **Comparison Matrix** | Optional | Transparent criteria | Fair assessment | Affiliate disclosure |
| **Cluster Hub** | Optional | Topic expertise | Hub authority | Accurate overview |
| **News Hub** | Optional | Understanding changes | Official sources | Timely updates |

**Implementation in ContentAgent:**
- Skyscraper articles MUST include expert quotes + case studies
- YMYL topics MUST have E-E-A-T level = "maximum" or "high"
- EditorAgent validates E-E-A-T requirements before approval
- Quality gate: E-E-A-T score < 80 → requires human review

### Frontend Integration (Astro Templates)

**Template-Driven Rendering:**

```typescript
// src/pages/[slug].astro

import { getArticle } from '../lib/api';
import UltimateGuide from '../templates/UltimateGuide.astro';
import Listicle from '../templates/Listicle.astro';
import Comparison from '../templates/Comparison.astro';
import LocationGuide from '../templates/LocationGuide.astro';
// ... import all 12 templates

const { slug } = Astro.params;
const article = await getArticle(slug);

// Dynamic template selection based on surface_template
const TemplateComponent = {
  'ultimate-guide': UltimateGuide,
  'listicle': Listicle,
  'comparison': Comparison,
  'location-guide': LocationGuide,
  // ... map all templates
}[article.surface_template] || UltimateGuide;

// Render with selected template
---

<TemplateComponent article={article} />
```

**Template Example (UltimateGuide.astro):**

```astro
---
// src/templates/UltimateGuide.astro
import Layout from '../layouts/Layout.astro';
import TldrSection from '../components/TldrSection.astro';
import KeyTakeaways from '../components/KeyTakeaways.astro';
import FaqAccordion from '../components/FaqAccordion.astro';
import Calculator from '../components/Calculator.astro';
// ... import all modular components

const { article } = Astro.props;
---

<Layout
  title={article.title}
  description={article.excerpt}
  schema={article.json_ld_schemas}
>
  <!-- Hero Section -->
  <article class="max-w-4xl mx-auto">
    <header>
      <nav aria-label="Breadcrumb">{/* Breadcrumbs */}</nav>
      <h1>{article.title}</h1>
      <div class="meta">
        <span>Last updated: {article.updated_at}</span>
        <span>Reading time: {article.reading_time_minutes} min</span>
      </div>
    </header>

    <!-- Sticky TOC -->
    <aside class="sticky-toc">{/* Table of contents */}</aside>

    <!-- Content with Modules -->
    <TldrSection content={article.tldr} />
    <KeyTakeaways items={article.key_takeaways} />

    {/* Main content markdown */}
    <div class="prose" set:html={article.content} />

    {/* Conditional modules based on article.modules_used */}
    {article.modules_used.includes('calculator') && (
      <Calculator type={article.calculator_type} />
    )}

    {article.modules_used.includes('faq') && (
      <FaqAccordion questions={article.faq} />
    )}

    <!-- References -->
    <section class="references">
      <h2>References</h2>
      <ol>
        {article.citations.map(cite => (
          <li><a href={cite.url}>{cite.title}</a></li>
        ))}
      </ol>
    </section>
  </article>
</Layout>
```

### Success Metrics

**Template Detection Accuracy:**
- Target: >85% archetype detection accuracy
- Validation: Manual review of first 50 template-driven articles

**Content Quality:**
- Skyscraper articles: 8000+ words, 12+ modules, 85+ quality score
- Deep Dive articles: 3500+ words, 9+ modules, 85+ quality score
- E-E-A-T signals present in 100% of YMYL content

**System Learning:**
- Continuously update archetype recommendations based on template_performance data
- Refine module requirements as patterns emerge
- Evolve templates as SERP patterns change

### Documentation

**Primary Authority Document:**
- `QUEST_TEMPLATES.md` (980 lines) - Complete system documentation
  - 5 content archetypes with specifications
  - 12 visual templates with structure
  - 35 modular components library
  - Multi-dimensional archetype detection algorithm
  - E-E-A-T optimization framework
  - SERP intelligence workflow
  - Archetype + template compatibility matrix

**Related Documents:**
- `QUEST_ARCHITECTURE_V2_4.md` (this file) - System architecture
- `QUEST_SEO.md` - Archetype-first SEO strategy
- `QUEST_RELOCATION_RESEARCH.md` - Topics reclassified by archetype

### Implementation Status

**Design Phase (Oct 10, 2025):**
- ✅ 5 content archetypes defined
- ✅ 12 visual templates specified
- ✅ 35 modular components cataloged
- ✅ Database schema designed (5 new tables)
- ✅ TemplateDetector agent designed
- ✅ E-E-A-T framework established
- ✅ Complete documentation (QUEST_TEMPLATES.md)

**Implementation Phase (TIER 0.5 - Upcoming):**
- ⏳ Create 5 database tables (SQL migration)
- ⏳ Implement TemplateDetector agent
- ⏳ Integrate Serper + Firecrawl APIs
- ⏳ Build Astro template components (12 templates)
- ⏳ Build modular component library (35 components)
- ⏳ Update ContentAgent to receive archetype + template
- ⏳ Implement multi-schema JSON-LD generator
- ⏳ Reclassify 993 topics in QUEST_RELOCATION_RESEARCH.md
- ⏳ Generate first 10 template-driven articles
- ⏳ Validate archetype detection accuracy

---

## 🗣️ Conversational SEO Strategy (v2.5.0)

### Overview

**The Conversational Revolution** - Based on insights from SEO expert Hamish (Income Stream Surfers), search behavior is fundamentally changing due to AI:

**Key Insight:**
- **Before AI Overviews:** 19 impressions for 9+ word queries
- **After AI Overviews:** 425 impressions for 9+ word queries (22x increase)
- **Why:** People now search in complete sentences, trained by ChatGPT/AI interactions

**Example Queries:**
- "I'm a US citizen working remotely. Can I get a Portugal digital nomad visa?" (14 words)
- "I'm a marketing manager with 7 years experience. How do I negotiate remote work with my employer?" (17 words)
- "I'm a freelance designer making $8k/month. Should I form an LLC in Delaware or Wyoming?" (16 words)

**Strategic Opportunity:**
- These queries have ZERO historical search volume (too new)
- No competitors targeting them (too specific)
- First-mover advantage: Be the ONLY result

### Holistic Application Across All Sites

**Conversational SEO isn't site-specific - it's platform-wide:**

**relocation.quest (Visa/Tax/Relocation YMYL):**
```
Pattern: "I'm a {nationality} {profession} {situation}. {visa/tax question}?"

Examples:
- "I'm a US software engineer working remotely. Can I get a Portugal digital nomad visa?"
- "I'm a Canadian family with two kids. How do we relocate to Spain with our pets?"
- "I'm a UK lawyer 30 years old. What are the tax implications of moving to Dubai?"

Persona Dimensions:
- Nationalities: US, UK, Canadian, Australian, Irish, EU citizens
- Professions: Software engineer, consultant, designer, lawyer, teacher, retiree
- Situations: Remote work, retirement, family relocation, digital nomad, job relocation

Questions:
- Visa eligibility, tax implications, costs, timeline, family/pets, healthcare
```

**placement.quest (Career/Job/Salary):**
```
Pattern: "I'm a {role} {experience level} {situation}. {career question}?"

Examples:
- "I'm a software engineer with 5 years experience. How do I negotiate a $150k salary?"
- "I'm a marketing manager in London. How do I transition to full-time remote work?"
- "I'm a recent computer science graduate. Should I take a bootcamp or get a master's degree?"

Persona Dimensions:
- Roles: Software engineer, marketing manager, product manager, designer, analyst, consultant
- Experience: Entry-level, 2-3 years, 5-7 years, 10+ years, executive
- Situations: Job search, salary negotiation, remote work, career transition, promotion

Questions:
- Salary negotiation, resume tips, interview prep, remote work, career change, skill development
```

**rainmaker.quest (Business/Entrepreneurship/Finance YMYL):**
```
Pattern: "I'm a {business type} {revenue level} {situation}. {business question}?"

Examples:
- "I'm a freelance web designer making $8k/month. Should I form an LLC or S-Corp?"
- "I'm a SaaS founder with 100 paying users. How do I raise pre-seed funding?"
- "I'm a solopreneur selling courses making $15k/month. What's the best payment processor?"

Persona Dimensions:
- Business Types: Freelancer, solopreneur, SaaS founder, agency owner, e-commerce, consultant
- Revenue: <$5k/month, $5-20k/month, $20-100k/month, $100k+/month
- Situations: Starting out, first clients, scaling, hiring, fundraising, exiting

Questions:
- Business structure, tax optimization, funding, hiring, scaling, tools, pricing
```

### The 6th Archetype: Conversational Answer Hub

**Specifications:**

```yaml
Archetype: Conversational Answer Hub

Trigger Pattern:
  - Query length: 9-35 words
  - Contains persona markers: "I'm a {nationality/role/business type}"
  - Contains situation: "working remotely", "with 5 years experience", "making $X/month"
  - Contains direct question: "Can I?", "How do I?", "Should I?", "What are?"

Strategic Goal:
  - Capture long-tail conversational queries BEFORE they appear in GSC
  - Rank in AI Overviews (Google, ChatGPT, Perplexity, Claude)
  - First-mover advantage (be the ONLY result for ultra-specific queries)
  - Holistic coverage across all 3 Quest sites

Content Specifications:
  Word Count: 1,500-3,000 (shorter than Skyscraper, focused)
  Module Count: 6-8 (lean, conversational)
  Keyword Target: 1-10 variations (highly specific, not broad)

  Schema Stack:
    - QAPage (primary) - Individual Q&A format
    - Person - Persona schema (nationality, role, business type)
    - SpeakableSpecification - Voice search optimization
    - BreadcrumbList - Navigation

  Tone Requirements:
    - 2nd person ("you") - Not 3rd person ("applicants")
    - Empathetic opening - "Let me make sure I understand your situation"
    - Direct answer first - No preamble, answer in first 100 words
    - Anticipate follow-ups - "You might also be wondering..."

  E-E-A-T Requirements:
    - Experience: 1-2 persona-specific case studies (e.g., US software engineers who did this)
    - Expertise: Quote relevant to THIS persona (not generic expert)
    - Authoritativeness: Link to .gov/.official sources specific to persona
    - Trustworthiness: Update date, "Last verified: [date]", persona-specific accuracy

  Required Modules:
    - PersonaSummary - "Your Situation" recap
    - DirectAnswer - Immediate yes/no/depends answer (first 100 words)
    - PersonaSpecificDetails - Nationality/role/business-specific info (not generic)
    - AnticipatedFollowUps - "You might also be wondering..."
    - PersonaCaseStudy - Real story matching this persona
    - PersonaChecklist - Action steps for THIS persona
    - ReferencesPersonaSpecific - Sources relevant to this persona

  Visual Templates Compatible:
    - ConversationalQA.astro (NEW)
    - PersonaGuide.astro (NEW)
    - DirectAnswer.astro (NEW)

  Site-Specific Application:
    - relocation.quest: YMYL suitability ✅ REQUIRED (visa/tax = maximum E-E-A-T)
    - placement.quest: YMYL suitability ⚠️ HIGH (career decisions = important)
    - rainmaker.quest: YMYL suitability ✅ REQUIRED (business/finance = maximum E-E-A-T)
```

### Pattern Generation Strategy (No GSC Data Needed)

**Goal:** Generate 300 conversational patterns (100 per site) BEFORE these queries exist in search data.

**Method:**
```python
# Universal pattern formula
pattern = f"I'm a {persona} {situation}. {question}?"

# Site-specific dimensions
relocation_personas = ["US citizen", "UK citizen", "Canadian", "Australian", "Irish"]
relocation_professions = ["software engineer", "consultant", "designer", "lawyer", "teacher"]
relocation_situations = ["working remotely", "retiring", "relocating with family"]
relocation_questions = [
    "Can I get a {country} digital nomad visa?",
    "What are the tax implications of moving to {country}?",
    "How long does the visa process take?",
    "Can my spouse and kids come with me?",
    "Do I need health insurance?"
]

# Generate combinations
# 5 nationalities × 5 professions × 5 questions = 125 patterns
# Filter to top 100 most likely (US/UK citizens prioritized)
```

**Validation:**
- Cross-reference with Reddit r/expats, r/digitalnomad actual questions
- Validate persona dimensions match largest expat demographics
- Ensure questions match actual pain points (not guesses)

### Backwards-Compatible Schema Design

**Critical Principle: NO BREAKING CHANGES**

**Existing Articles (Keep Working):**
```yaml
Current State:
  - Have: title, slug, content, hero_image_url, status
  - Missing: persona fields, archetype, template
  - Behavior: Render with default UltimateGuide.astro template
  - Result: NO BREAKAGE
```

**New Conversational Articles (Enhanced):**
```yaml
Enhanced State:
  - Have: ALL fields (persona_nationality, target_archetype, etc.)
  - Behavior: Render with ConversationalQA.astro template
  - Result: Enhanced conversational experience
```

**Schema Changes (Additive Only):**

```sql
-- ADD columns (IF NOT EXISTS = safe for existing articles)
ALTER TABLE articles ADD COLUMN IF NOT EXISTS persona_nationality VARCHAR(50);
ALTER TABLE articles ADD COLUMN IF NOT EXISTS persona_profession VARCHAR(100);
ALTER TABLE articles ADD COLUMN IF NOT EXISTS persona_income VARCHAR(50);
ALTER TABLE articles ADD COLUMN IF NOT EXISTS persona_family VARCHAR(100);
ALTER TABLE articles ADD COLUMN IF NOT EXISTS persona_situation TEXT;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS persona_question TEXT;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS direct_answer TEXT;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS answer_confidence VARCHAR(20); -- 'yes', 'no', 'depends'
ALTER TABLE articles ADD COLUMN IF NOT EXISTS answer_context TEXT;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS followup_questions JSONB; -- [{question, answer, link}]
ALTER TABLE articles ADD COLUMN IF NOT EXISTS case_study JSONB; -- {person, situation, outcome, timeline, quote}

-- Existing archetype/template columns (from v2.4)
ALTER TABLE articles ADD COLUMN IF NOT EXISTS target_archetype VARCHAR(50) DEFAULT 'skyscraper';
ALTER TABLE articles ADD COLUMN IF NOT EXISTS surface_template VARCHAR(50) DEFAULT 'ultimate-guide';
ALTER TABLE articles ADD COLUMN IF NOT EXISTS modules_used TEXT[] DEFAULT ARRAY['tldr', 'content', 'faq'];

CREATE INDEX IF NOT EXISTS idx_articles_persona ON articles(persona_nationality, persona_profession);
CREATE INDEX IF NOT EXISTS idx_articles_archetype ON articles(target_archetype);

-- NEW table: conversational_patterns (doesn't affect existing articles)
CREATE TABLE IF NOT EXISTS conversational_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Pattern template
    pattern_template TEXT NOT NULL, -- "I'm a {nationality} {profession}. Can I {action}?"

    -- Persona dimensions
    persona_nationality VARCHAR(50),
    persona_profession VARCHAR(100),
    persona_income VARCHAR(50),
    persona_family VARCHAR(100),
    persona_situation TEXT,

    -- Question
    action_question TEXT, -- "get a Portugal visa", "negotiate remote work", etc.

    -- Target site
    target_site VARCHAR(50) NOT NULL, -- 'relocation', 'placement', 'rainmaker'

    -- Generated article
    article_id UUID REFERENCES articles(id),

    -- Performance tracking (when data emerges)
    gsc_impressions INTEGER DEFAULT 0,
    gsc_clicks INTEGER DEFAULT 0,
    ai_citations JSONB, -- {chatgpt: true, perplexity: false, claude: true, google_ai: false}

    -- Priority
    priority_score INTEGER DEFAULT 50, -- 0-100, higher = generate first

    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_patterns_site ON conversational_patterns(target_site);
CREATE INDEX idx_patterns_priority ON conversational_patterns(priority_score DESC);
CREATE INDEX idx_patterns_article ON conversational_patterns(article_id);
```

**Frontend Template Router (Backwards Compatible):**

```typescript
// src/pages/[slug].astro

// Dynamic template selection
function selectTemplate(article) {
  // NEW: Conversational articles
  if (article.target_archetype === 'conversational') {
    return ConversationalQA;
  }

  // OLD: Existing articles (no archetype field = NULL)
  if (!article.target_archetype || article.target_archetype === 'skyscraper') {
    return UltimateGuide; // Default, keeps working
  }

  // FUTURE: Template-driven articles (v2.4 Template Intelligence)
  const templateMap = {
    'ultimate-guide': UltimateGuide,
    'listicle': Listicle,
    'comparison': Comparison,
    'location-guide': LocationGuide,
    // ... other templates
  };

  return templateMap[article.surface_template] || UltimateGuide; // Fallback
}

const TemplateComponent = selectTemplate(article);
```

**Result:**
- ✅ 4 existing articles keep working (default to UltimateGuide)
- ✅ New conversational articles use ConversationalQA
- ✅ Future template-driven articles use dynamic templates
- ✅ Zero risk, zero downtime

### AI Citation Tracking

**The New SEO Metric: AI Citation Rate**

Traditional SEO: Track rankings in Google (positions 1-10)
Conversational SEO: Track citations in AI platforms (ChatGPT, Perplexity, Claude, Google AI)

**Method:**

```python
# scripts/test_ai_citations.py

import openai
import anthropic
from perplexity import PerplexityAPI  # New Search API (Oct 2025)

def test_article_citations(article):
    query = article.persona_question  # The exact conversational query

    # Test 1: ChatGPT Search (via API)
    chatgpt_result = openai.ChatCompletion.create(
        model="gpt-4-search",
        messages=[{"role": "user", "content": query}]
    )
    chatgpt_cited = article.url in str(chatgpt_result.choices[0].message)

    # Test 2: Perplexity Search (NEW API, October 2025)
    perplexity_result = PerplexityAPI.search(query)
    perplexity_cited = article.url in perplexity_result.citations

    # Test 3: Claude (via Anthropic API with web search)
    claude_result = anthropic.Anthropic().messages.create(
        model="claude-3-5-sonnet-20241022",
        messages=[{"role": "user", "content": query}],
        tools=[{"type": "web_search"}]
    )
    claude_cited = article.url in str(claude_result.content)

    # Test 4: Google AI Overview (manual check - no API)
    google_ai_cited = False  # Requires manual verification

    # Store results
    return {
        'chatgpt': chatgpt_cited,
        'perplexity': perplexity_cited,
        'claude': claude_cited,
        'google_ai': google_ai_cited
    }

# Cost: 4 platforms × $0.01/query = $0.04 per article test
```

**Success Metrics:**
- **Target: 40% AI citation rate** (40% of articles cited by at least 1 AI platform)
- **Stretch: 60% citation rate** by Month 6
- **Measurement: Test all articles monthly**

### Implementation Roadmap (Phased)

**Phase 0: Content First (Current - Week 1-4)**
```yaml
Priority: Get 20 articles live, validate publishing flow
Status: IN PROGRESS (4/20 articles published)

Tasks:
  - Generate 16 more relocation.quest articles (existing pipeline)
  - Validate: Hero images working, links working, content rendering
  - Deploy: placement.quest with initial 5 articles
  - NO CHANGES to existing 4 articles

Blocker Removal: Establish baseline before adding complexity
```

**Phase 1: Template Intelligence (TIER 0.5 - Week 5-8)**
```yaml
Priority: Implement SERP-driven archetype detection
Status: DESIGNED, not implemented

Tasks:
  - Deploy 5 new tables (serp_intelligence, content_archetypes, etc.)
  - Implement TemplateDetector agent (Serper + Firecrawl)
  - Build first 6 Astro templates
  - NO CHANGES to existing articles (backwards compatible)

Validation: Generate 10 test articles, validate archetype detection accuracy
```

**Phase 2: Conversational SEO (TIER 0.9 - Week 9-12)**
```yaml
Priority: Implement conversational pattern generation + AI citation tracking
Status: DESIGNED, not implemented

Tasks:
  - Generate 100 conversational patterns per site (300 total)
  - Build ConversationalQA template + 4 persona components
  - Enhance ContentAgent with CONVERSATIONAL_PROMPT
  - Generate first 10 conversational articles
  - Test AI citation rate across 4 platforms

Validation: If ≥40% citation rate → Scale to 100 articles. If <40% → Refine approach.
```

**Phase 3: Scale (Week 13+)**
```yaml
Priority: Generate 300 conversational articles, track performance
Status: FUTURE

Tasks:
  - Generate 100 articles per site (relocation, placement, rainmaker)
  - Monthly AI citation testing (300 articles × 4 platforms × $0.01 = $12/month)
  - GSC validation when data emerges (regex method: 9+ word queries)
  - Pattern refinement based on actual GSC data

Learning Loop: GSC shows which patterns work → Generate more variations
```

### Future Vision: Conversational Agent Handoff

**The Endgame: Full-Stack Conversational Experience**

```
User Journey:

Step 1: Conversational Search
  → Google: "I'm a UK lawyer, how do I get a work visa in the UK"

Step 2: Conversational SEO Ranking
  → Google AI Overview cites relocation.quest
  → User clicks: https://relocation.quest/uk-lawyer-work-visa-guide

Step 3: Conversational Landing Page
  → Page Title: "I'm a UK Lawyer - How Do I Get a Work Visa in the UK?"
  → PersonaSummary: "Your situation: You're a UK lawyer..."
  → DirectAnswer: "✅ Yes, UK lawyers can get work visas under several routes..."
  → Content: Persona-specific guide

Step 4: Conversational Agent Handoff (FUTURE)
  → [Chat widget at bottom of page]
  → Agent: "Hi! I see you're a UK lawyer interested in work visas.
             I already know:
             - You're based in the UK
             - You're a lawyer
             - You're researching work visa options

             What specific situation are you in?"
  → [Conversation continues, pre-seeded with persona context from page]
```

**This creates a seamless conversational experience from Google → Landing Page → AI Agent.**

**Implementation:** After 100 conversational articles published, integrate conversational agent (ChatGPT API, Claude API, or custom) with persona context from article metadata.

---

## 🌐 Frontend: Astro Multi-Site

### Site Deployment Strategy

```yaml
Platform: Vercel (Free Tier)
Framework: Astro 4.x (static site generation)
Sites:
  - relocation.quest (relocation guides)
  - placement.quest (job placement data)
  - rainmaker.quest (entrepreneurship)

Build Process:
  1. Query Directus GraphQL for published articles
  2. Generate static pages at build time
  3. Deploy to Vercel CDN (global edge network)
  4. Incremental Static Regeneration (ISR) every 5 minutes

Cost: $0/month (Vercel Free Tier)
Performance: <1s page loads (static content from CDN)
```

### Astro Configuration

```typescript
// astro.config.mjs
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  integrations: [tailwind()],
  output: 'static',
  
  // ISR configuration
  experimental: {
    contentCollectionCache: true,
  },
  
  // Site-specific environment
  site: process.env.SITE_URL, // relocation.quest, placement.quest, etc.
  
  // Performance optimizations
  vite: {
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor': ['@apollo/client', 'graphql'],
          },
        },
      },
    },
  },
});
```

### Astro 5.13+ Modern Features (Phase 1)

**Framework Version:** Astro 5.14+ with production security & performance optimizations

#### Content Security Policy (CSP)

**Purpose:** XSS protection + SEO ranking boost

```typescript
// astro.config.mjs - ADD THIS
export default defineConfig({
  security: {
    contentSecurityPolicy: {
      directives: {
        'default-src': ["'self'"],
        'img-src': ["'self'", 'cloudinary.com', 'res.cloudinary.com'],
        'media-src': ["'self'", 'mux.com', 'stream.mux.com'],  // Phase 2: Video
        'script-src': ["'self'", "'unsafe-inline'"],  // Analytics
        'style-src': ["'self'", "'unsafe-inline'"],   // Tailwind
      }
    }
  },
  // ... rest of config
});
```

**Benefits:** +5-10% SEO score, prevents script injection in AI content

#### Raw Environment Variables

**Fixes:** `ENABLE_IMAGE_GENERATION="true"` deployment bugs

```typescript
// astro.config.mjs
export default defineConfig({
  experimental: {
    rawEnvValues: true  // Prevents "true" → boolean coercion
  }
});
```

**Critical:** Becomes default in Astro 6.0 - prepare now

---

### GraphQL Integration

```typescript
// src/lib/directus.ts
import { ApolloClient, InMemoryCache, gql } from '@apollo/client';

const client = new ApolloClient({
  uri: import.meta.env.DIRECTUS_GRAPHQL_URL,
  cache: new InMemoryCache(),
  headers: {
    Authorization: `Bearer ${import.meta.env.DIRECTUS_API_TOKEN}`,
  },
});

export async function getArticles(site: string, limit = 20) {
  const { data } = await client.query({
    query: gql`
      query GetArticles($site: String!, $limit: Int!) {
        articles(
          filter: { 
            target_site: { _eq: $site }, 
            status: { _eq: "published" } 
          }
          sort: ["-published_date"]
          limit: $limit
        ) {
          id
          title
          slug
          excerpt
          hero_image_url
          reading_time_minutes
          published_date
          author {
            first_name
            last_name
            avatar_url
          }
        }
      }
    `,
    variables: { site, limit },
  });
  
  return data.articles;
}
```

### Fallback Strategy (if Directus Down)

```typescript
// src/lib/fallback.ts
import postgres from 'postgres';

// Direct Neon query as fallback
const sql = postgres(import.meta.env.DATABASE_URL);

export async function getArticlesFallback(site: string, limit = 20) {
  try {
    // Try Directus first
    return await getArticles(site, limit);
  } catch (error) {
    console.warn('Directus unavailable, using direct Neon query');
    
    // Fallback to direct database query
    return await sql`
      SELECT 
        id, title, slug, excerpt, hero_image_url,
        reading_time_minutes, published_date
      FROM articles
      WHERE target_site = ${site} 
      AND status = 'published'
      ORDER BY published_date DESC
      LIMIT ${limit}
    `;
  }
}
```

---

## 📊 Monitoring & Observability

### Metrics Dashboard

```yaml
Platform: Grafana + Prometheus (self-hosted) or Datadog (free tier)

Critical Metrics:
  
  Infrastructure:
    - API Gateway: Request rate, p95 latency, error rate
    - Workers: Queue depth, job latency, concurrency
    - Neon: Query time, connection pool usage, storage
    - Redis: Memory usage, queue size, eviction rate
  
  Business:
    - Articles generated per day
    - Cache hit rate (target: >25%)
    - Average quality score
    - Cost per article (target: <$0.60)
  
  Quality:
    - Auto-publish rate (target: >60%)
    - Human review queue depth
    - Article rejection rate
    - Average reading time

Alerts:
  - Queue depth >100 jobs (scale workers)
  - API error rate >5% (investigate)
  - Daily cost >$30 (circuit breaker)
  - Neon storage >80% (scale up)
  - Cache hit rate <15% (tune similarity threshold)
```

### Cost Monitoring

```sql
-- Daily cost tracking query
CREATE VIEW daily_costs AS
SELECT 
  DATE(created_at) as date,
  COUNT(*) as articles_generated,
  SUM((cost_breakdown->>'research')::decimal) as research_cost,
  SUM((cost_breakdown->>'content')::decimal) as content_cost,
  SUM((cost_breakdown->>'image')::decimal) as image_cost,
  SUM(total_cost) as total_cost,
  AVG(total_cost) as avg_cost_per_article
FROM job_status
WHERE status = 'completed'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Cache performance
CREATE VIEW cache_performance AS
SELECT 
  DATE(last_accessed) as date,
  COUNT(*) as total_lookups,
  SUM(cache_hits) as total_hits,
  ROUND(100.0 * SUM(cache_hits) / COUNT(*), 2) as hit_rate_pct,
  ROUND(SUM(cache_hits) * 0.20, 2) as estimated_savings
FROM article_research
WHERE last_accessed > NOW() - INTERVAL '30 days'
GROUP BY DATE(last_accessed)
ORDER BY date DESC;
```

### Health Checks

```python
# Health check endpoints
from fastapi import APIRouter, status

router = APIRouter()

@router.get("/health")
async def health_check():
    checks = {
        "api": "healthy",
        "database": await check_neon(),
        "redis": await check_redis(),
        "queue": await check_queue_depth(),
        "workers": await check_worker_count(),
    }
    
    all_healthy = all(v == "healthy" for v in checks.values())
    status_code = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(status_code=status_code, content=checks)

async def check_neon():
    try:
        await db.fetchval("SELECT 1")
        return "healthy"
    except:
        return "unhealthy"

async def check_queue_depth():
    depth = await redis.llen("bull:articles:wait")
    if depth > 100:
        return f"warning: {depth} jobs queued"
    return "healthy"
```

---

## 🚨 Operational Readiness Checklist

### Pre-Launch Validation

```yaml
Research Cache Pilot (Week 1):
  - ❌ Generate 200 test articles in staging
  - ❌ Measure cache hit rate (target: >20% week 1)
  - ❌ Validate cost savings (conservative: 20-25%)
  - ❌ Tune similarity threshold (0.70-0.80 range)
  - ❌ Adjust TTL based on topic popularity

Performance Benchmarks (Week 2):
  - ❌ Load test: 50 concurrent article generations
  - ❌ Database: <100ms article queries (p95)
  - ❌ Vector search: <200ms similarity lookups
  - ❌ GraphQL API: <200ms p95 latency
  - ❌ Worker throughput: 20 articles/hour minimum
  - ❌ End-to-end: <60s from submission to completion

Cost Controls (Week 3):
  - ❌ Per-job cost cap ($0.75 max)
  - ❌ Daily cost cap ($30 max)
  - ❌ Budget alerts at 80% threshold
  - ❌ Graceful degradation (skip expensive APIs if cap hit)
  - ❌ Cost dashboard (real-time tracking)

Security (Week 4):
  - ❌ Role-separated DB credentials (fastapi_user, directus_user, readonly_user)
  - ❌ API rate limiting (100 req/min per IP)
  - ❌ CORS whitelist configured (only *.quest domains)
  - ❌ Content sanitization (XSS prevention)
  - ❌ API key rotation procedure documented
  - ❌ Secrets stored in env vars, not code

Monitoring (Week 5):
  - ❌ Health checks (API, Workers, Directus, Neon)
  - ❌ Queue depth alerts (>100 jobs)
  - ❌ Error rate alerts (>5% failures)
  - ❌ Cost anomaly detection
  - ❌ Slack/email notifications configured
  - ❌ On-call rotation defined (if team >1)

Data Integrity (Week 6):
  - ❌ Foreign key constraints validated
  - ❌ Migration rollback tested
  - ❌ Backup restore tested (Neon point-in-time recovery)
  - ❌ Data loss scenarios documented
  - ❌ Disaster recovery plan written
```

---

## 📅 Implementation Roadmap: 6 Weeks

### Phase 1: Foundation (Weeks 1-2)

**Week 1: Infrastructure Setup**

```yaml
Day 1-2: Neon Configuration
  - ✅ Create Neon project (Launch tier)
  - ✅ Disable auto-suspend
  - ✅ Run schema migrations (tables, indexes, extensions)
  - ✅ Create role-separated users (fastapi, directus, readonly)
  - ✅ Enable pg_stat_statements monitoring

Day 3-4: Railway Deployment
  - ✅ Deploy 4 services (API Gateway, Workers, Directus, Redis)
  - ✅ Configure environment variables
  - ✅ Setup inter-service communication
  - ✅ Configure auto-scaling rules

Day 5: Validation
  - ✅ Load test Neon (1000 concurrent queries)
  - ✅ Verify no cold starts (<50ms query time)
  - ✅ Test service-to-service communication
  - ✅ Health check endpoints working
```

**Week 2: AI Pipeline Foundation**

```yaml
Day 1-2: ResearchAgent
  - ✅ Integrate Perplexity Sonar Pro
  - ✅ Implement pgvector cache
  - ✅ OpenAI embeddings integration
  - ✅ Test cache hit/miss logic

Day 3-4: ContentAgent + EditorAgent
  - ✅ Claude 3.5 Sonnet integration
  - ✅ Implement quality scoring
  - ✅ Test batch API for cost savings

Day 5: Pilot Program
  - ✅ Generate 200 test articles
  - ✅ Measure cache hit rate
  - ✅ Calculate actual costs
  - ✅ Tune similarity threshold
```

### Phase 2: CMS & Frontend (Weeks 3-4)

**Week 3: Directus Setup**

```yaml
Day 1-2: Directus Configuration
  - ✅ Deploy Directus service
  - ✅ Connect to Neon (restricted user)
  - ✅ Configure permissions (no DDL)
  - ✅ Setup GraphQL API

Day 3-4: HITL Workflow
  - ✅ Implement BullMQ Flows
  - ✅ Create review queue in Directus
  - ✅ Test human approval/rejection
  - ✅ Integrate ImageAgent trigger

Day 5: Testing
  - ✅ End-to-end article generation
  - ✅ GraphQL contract tests
  - ✅ Permission boundary tests
```

**Week 4: ImageAgent + Astro Sites**

```yaml
Day 1-2: ImageAgent
  - ✅ Replicate FLUX integration
  - ✅ Cloudinary CDN setup
  - ✅ Prompt engineering for hero images
  - ✅ Cost tracking per image

Day 3-5: Astro Sites
  - ✅ Deploy relocation.quest (Vercel)
  - ✅ Deploy placement.quest
  - ✅ Deploy rainmaker.quest
  - ✅ Integrate Directus GraphQL
  - ✅ Test ISR (Incremental Static Regeneration)
```

### Phase 3: Production Hardening (Weeks 5-6)

**Week 5: Monitoring & Security**

```yaml
Day 1-2: Observability
  - ✅ Setup Grafana + Prometheus (or Datadog)
  - ✅ Configure alerts (queue depth, error rate, cost)
  - ✅ Create cost tracking dashboard
  - ✅ Performance metrics visualization

Day 3-4: Security Audit
  - ✅ API rate limiting (100 req/min)
  - ✅ CORS whitelist (*.quest only)
  - ✅ Content sanitization (XSS prevention)
  - ✅ Secrets audit (no hardcoded keys)
  - ✅ DB permission verification

Day 5: Load Testing
  - ✅ Simulate 50 concurrent generations
  - ✅ Measure: DB connections, Redis memory, API latency
  - ✅ Identify bottlenecks
  - ✅ Document scaling thresholds
```

**Week 6: Launch Preparation**

```yaml
Day 1-2: Data Migration (if applicable)
  - ✅ Migrate existing content from old system
  - ✅ Validate foreign keys
  - ✅ Test rollback procedures

Day 3-4: Staging → Production
  - ✅ Final smoke tests
  - ✅ Backup verification
  - ✅ Disaster recovery test
  - ✅ Production cutover

Day 5: Post-Launch Monitoring
  - ✅ Watch metrics for 24 hours
  - ✅ Fix any hot issues
  - ✅ Adjust scaling if needed
  - ✅ Document lessons learned
```

---

## 🔒 Security Best Practices

### Database Security

```yaml
Principle: Least Privilege Access

User Roles:
  neondb_owner:
    permissions: ALL PRIVILEGES
    usage: Emergency DBA access only
    rotation: Never used in production
  
  fastapi_user:
    permissions: SELECT, INSERT, UPDATE, DELETE
    tables: ALL tables in public schema
    usage: Application layer (API + Workers)
    rotation: Quarterly
  
  directus_user:
    permissions: SELECT, INSERT, UPDATE, DELETE
    tables: articles, users ONLY
    ddl_blocked: YES (no CREATE, ALTER, DROP)
    usage: CMS layer
    rotation: Quarterly
  
  readonly_user:
    permissions: SELECT only
    tables: ALL tables (for analytics)
    usage: Monitoring, dashboards, reports
    rotation: Quarterly

Connection Security:
  - SSL/TLS required for all connections
  - IP whitelist (Railway IPs only)
  - Connection pooling (max 20 connections per service)
```

### API Security

```yaml
Rate Limiting:
  per_ip: 100 requests/minute
  per_api_key: 1000 requests/hour
  burst: 20 requests/second
  
  implementation:
    - Redis-based rate limiter
    - Return 429 Too Many Requests if exceeded
    - Include Retry-After header

CORS Configuration:
  allowed_origins:
    - https://relocation.quest
    - https://placement.quest
    - https://rainmaker.quest
    - https://admin.quest (Directus)
  
  allowed_methods: [GET, POST]
  allowed_headers: [Content-Type, Authorization]
  credentials: true

API Keys:
  format: "quest_live_" + 32-char random string
  storage: PostgreSQL (hashed with bcrypt)
  rotation: Quarterly or on suspected compromise
  scopes: ["read:articles", "write:articles", "admin"]
```

### Content Security

```yaml
XSS Prevention:
  - Sanitize all user inputs (DOMPurify)
  - Escape HTML in article content
  - Content-Security-Policy header
  - No inline scripts in Astro

SQL Injection Prevention:
  - Always use parameterized queries
  - Never concatenate user input into SQL
  - Use SQLAlchemy ORM (prevents injection)

Secrets Management:
  - Store in environment variables
  - Never commit to git
  - Use Railway secrets (encrypted at rest)
  - Rotate quarterly
```

---

## 📈 Scaling Strategy

### Traffic Growth Projections

```yaml
Month 1-3 (MVP):
  Articles: 1,000/month
  Pageviews: 10,000/month
  Cost: $600/month
  
Month 4-6 (Growth):
  Articles: 2,000/month
  Pageviews: 50,000/month
  Cost: $530/month (better cache hit rate)
  
Month 7-12 (Scale):
  Articles: 5,000/month
  Pageviews: 200,000/month
  Cost: $450/month (economies of scale, 40% cache hits)
```

### Scaling Thresholds

```yaml
Infrastructure_Scaling:
  
  Neon_PostgreSQL:
    threshold: 80% CPU utilization
    action: Increase compute units (0.25 → 0.5 → 1 → 2 CU)
    cost_impact: +$10/mo per doubling
  
  API_Gateway:
    threshold: p95 latency >500ms
    action: Add replica (2 → 3 → 5)
    cost_impact: +$7.50/mo per replica
  
  Workers:
    threshold: Queue depth >50 jobs for >5 minutes
    action: Add worker replica (1 → 2 → 5 → 10)
    cost_impact: +$4/mo per replica
  
  Redis:
    threshold: Memory >80%
    action: Upgrade Upstash plan (Pro → Premium)
    cost_impact: +$10/mo

Cache_Optimization:
  
  If_hit_rate_<20%:
    action: Lower similarity threshold (0.75 → 0.70)
    impact: More cache hits, slight quality trade-off
  
  If_hit_rate_>50%:
    action: Extend TTL (30 → 60 days)
    impact: Longer-lasting cache, more savings
```

---

## 🎓 Lessons Learned from Peer Reviews

### ChatGPT (GPT-4) Feedback

**Key Concerns:**
1. ✅ Directus operational risk (schema evolution)
2. ✅ 40% cache savings needs validation
3. ✅ Service separation for scaling

**Actions Taken:**
- Restricted Directus DB user (no DDL permissions)
- Conservative 25% cache estimate until pilot validates 40%
- 4-service architecture (API, Workers, Directus, Redis)

### Gemini (2.0 Flash) Feedback

**Key Concerns:**
1. ✅ Neon cold starts (200-800ms latency)
2. ✅ 3-week timeline unrealistic
3. ✅ Exponential backoff for LLM retries

**Actions Taken:**
- Upgraded to Neon Launch tier (always-on compute)
- Extended timeline to 6 weeks (phased approach)
- Implemented BullMQ exponential backoff (2s → 32s)

### Consensus Improvements

Both reviewers agreed on:
- ✅ Need for HITL quality gate
- ✅ Cost circuit breakers essential
- ✅ Embedding versioning prevents drift
- ✅ Operational readiness checklist critical

---

## 📊 Success Metrics (30-Day Review)

```yaml
Technical_KPIs:
  - Page load time: <3 seconds (p95)
  - Article generation time: <60 seconds (p95)
  - API uptime: >99.5%
  - Database query time: <50ms (p95)
  - Cache hit rate: >25% (target: 40% by month 3)

Business_KPIs:
  - Articles published: >1,000/month
  - Auto-publish rate: >60%
  - Average quality score: >80/100
  - Cost per article: <$0.60 (target: $0.45 by month 3)

Quality_KPIs:
  - Human review queue depth: <10 articles
  - Article rejection rate: <10%
  - User engagement: >3 min average session
  - SEO ranking: 50+ keywords in top 100
```

---

## 🚀 Deployment Commands

### Initial Setup

```bash
# 1. Create Neon project
neon projects create --name quest-production --plan launch

# 2. Run schema migrations
psql $DATABASE_URL -f migrations/001_initial_schema.sql

# 3. Create database users
psql $DATABASE_URL -f migrations/002_create_users.sql

# 4. Deploy Railway services
railway up --service quest-api-gateway
railway up --service quest-workers
railway up --service quest-directus

# 5. Deploy Astro sites to Vercel
cd sites/relocation.quest && vercel --prod
cd sites/placement.quest && vercel --prod
cd sites/rainmaker.quest && vercel --prod
```

### Daily Operations

```bash
# Check queue depth
redis-cli -u $REDIS_URL LLEN bull:articles:wait

# Monitor costs
psql $DATABASE_URL -c "SELECT * FROM daily_costs WHERE date = CURRENT_DATE;"

# Check cache hit rate
psql $DATABASE_URL -c "SELECT * FROM cache_performance WHERE date = CURRENT_DATE;"

# View recent errors
railway logs --service quest-workers --filter "ERROR" --tail 100
```

---

## 📞 Support & Escalation

### On-Call Rotation

```yaml
Primary: Developer 1 (Week 1, 3, 5)
Secondary: Developer 2 (Week 2, 4, 6)

Escalation Levels:
  Level 1 (Warning): Slack notification
    - Queue depth >50
    - Cache hit rate <15%
    - Cost >80% of daily cap
  
  Level 2 (Critical): PagerDuty alert
    - API error rate >5%
    - Database unreachable
    - Worker failure rate >20%
    - Cost >100% of daily cap
  
  Level 3 (Emergency): Phone call + Slack @channel
    - Complete service outage
    - Data corruption detected
    - Security breach suspected
```

### Runbook Links

- [Incident Response Playbook](./docs/runbook-incident-response.md)
- [Cost Circuit Breaker Activation](./docs/runbook-cost-breaker.md)
- [Database Failover Procedure](./docs/runbook-db-failover.md)
- [Cache Invalidation Guide](./docs/runbook-cache-invalidation.md)

---

## 🎯 Conclusion

Quest v2.2 represents a **production-ready, cost-conscious, and operationally mature** architecture for AI-native content generation at scale. By incorporating peer review feedback from both ChatGPT and Gemini, we've addressed critical concerns around performance, reliability, and cost management.

**Key Achievements:**
- ✅ Sub-3-second page loads guaranteed
- ✅ 4-service architecture enables independent scaling
- ✅ Conservative cost estimates prevent budget surprises
- ✅ 6-week phased timeline ensures quality over speed
- ✅ Comprehensive monitoring and alerting

**Ready for Production:**
- Database-first design ensures vendor independence
- Schema governance prevents operational drift
- Cost circuit breakers prevent runaway expenses
- HITL quality gate maintains content standards

**Next Steps:**
1. Complete Week 1 infrastructure setup
2. Run research cache pilot (validate 25-40% savings)
3. Deploy 4-service architecture to Railway
4. Begin 6-week phased rollout

---

## 📚 Appendix

### Architecture Versioning

- **v1.0**: Initial Retool + Hasura architecture (deprecated)
- **v2.0**: Database-first with Directus (October 2025)
- **v2.1**: Peer review candidate (October 2025)
- **v2.2**: Production-ready with corrections (October 7, 2025) ← Current

### Change Log v2.1 → v2.2

```yaml
Infrastructure:
  - Upgraded Neon to Launch tier ($60/mo, always-on)
  - Separated API and Workers into 4 services
  - Added Upstash Redis for BullMQ persistence

Cost Estimates:
  - Conservative 25% cache savings (not 40%)
  - Infrastructure increased to $145/mo (from $80/mo)
  - Total monthly cost: $600/mo (from $435/mo)

Timeline:
  - Extended to 6 weeks (from 3 weeks)
  - Phased wave-based rollout
  - Added pilot program in Week 2

Operational:
  - Added exponential backoff for LLM retries
  - Implemented HITL quality gate
  - Added cost circuit breakers
  - Enhanced monitoring and alerting

Security:
  - Role-separated database users
  - Schema governance process
  - API rate limiting
  - Content sanitization
```

### References

- [Neon PostgreSQL Documentation](https://neon.tech/docs)
- [BullMQ Documentation](https://docs.bullmq.io/)
- [Directus Documentation](https://docs.directus.io/)
- [Astro Documentation](https://docs.astro.build/)
- [Claude API Reference](https://docs.anthropic.com/)
- [Perplexity API Documentation](https://docs.perplexity.ai/)

---

**Architecture Author:** DK (with AI assistance)  
**Peer Reviewers:** ChatGPT 4.0, Gemini 2.0 Flash  
**Last Updated:** October 7, 2025  
**Status:** Ready for Implementation ✅
