# Quest Content Intelligence Platform v2.2

**Database-First AI-Powered Content Generation at Scale**

## Overview

Quest is a multi-site content intelligence platform that generates, manages, and publishes high-quality articles across three specialized publications:

- **relocation.quest** - Relocation and expat content
- **placement.quest** - Career placement and job market data
- **rainmaker.quest** - Entrepreneurship and business growth

## Architecture

### 4-Service Design

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Astro     │────▶│   Directus   │────▶│    Neon     │
│   Sites     │     │  CMS/GraphQL │     │ PostgreSQL  │
└─────────────┘     └──────────────┘     └─────────────┘
                                                 ▲
                                                 │
┌──────────────┐    ┌──────────────┐            │
│  FastAPI     │───▶│   BullMQ     │────────────┘
│   Gateway    │    │   Workers    │
└──────────────┘    └──────────────┘
```

### Tech Stack

- **Database**: Neon PostgreSQL 16 (Launch tier, always-on)
- **Backend**: FastAPI + BullMQ + Redis
- **CMS**: Directus (self-hosted, database-first)
- **Frontend**: Astro + Tailwind CSS
- **AI**: Claude Sonnet 4.5, Perplexity Sonar Pro, FLUX Schnell
- **Hosting**: Railway (backend), Vercel (frontend)

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL client (psql)
- Docker & Docker Compose
- Railway CLI
- Vercel CLI

### 1. Database Setup

```bash
# Install Neon CLI
npm install -g neonctl

# Create Neon project (Launch tier)
neon projects create --name quest-production --plan launch

# Set DATABASE_URL environment variable
export DATABASE_URL="postgresql://..."

# Run migrations
psql $DATABASE_URL -f migrations/001_initial_schema.sql
psql $DATABASE_URL -f migrations/002_create_users.sql
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# Then start services

# Terminal 1: API Gateway
uvicorn app.main:app --reload --port 8000

# Terminal 2: Workers
python -m app.workers.queue_worker
```

### 3. Directus Setup

```bash
cd directus

# Start Directus with Docker Compose
docker-compose up -d

# Access admin UI at http://localhost:8055
# Login with credentials from .env
```

### 4. Frontend Setup

```bash
# Setup relocation.quest
cd frontend/relocation.quest
npm install
npm run dev

# Repeat for placement.quest and rainmaker.quest
```

## Project Structure

```
quest-platform/
├── backend/
│   ├── app/
│   │   ├── agents/          # 4-agent AI pipeline
│   │   │   ├── research.py
│   │   │   ├── content.py
│   │   │   ├── editor.py
│   │   │   └── image.py
│   │   ├── api/             # FastAPI endpoints
│   │   │   ├── articles.py
│   │   │   ├── jobs.py
│   │   │   └── health.py
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── core/            # Config, database, cache
│   │   ├── workers/         # BullMQ workers
│   │   └── main.py          # FastAPI app
│   ├── migrations/          # SQL migrations
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── relocation.quest/    # Astro site 1
│   ├── placement.quest/     # Astro site 2
│   └── rainmaker.quest/     # Astro site 3
├── directus/
│   ├── docker-compose.yml
│   └── .env.example
├── docs/
│   ├── architecture.md
│   ├── runbook-*.md         # Operational runbooks
│   └── api-reference.md
└── README.md
```

## Environment Variables

### Backend (.env)

```bash
# Neon Database
DATABASE_URL=postgresql://fastapi_user:password@ep-xxx.neon.tech/neondb?sslmode=require

# Redis (Upstash)
REDIS_URL=redis://default:password@redis.upstash.io:6379

# AI APIs
PERPLEXITY_API_KEY=pplx-...
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
REPLICATE_API_KEY=r8_...

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...

# Cost Limits
DAILY_COST_CAP=30.00
PER_JOB_COST_CAP=0.75
```

### Directus (.env)

```bash
# Database (restricted user)
DB_CLIENT=postgres
DB_HOST=ep-xxx.neon.tech
DB_PORT=5432
DB_DATABASE=neondb
DB_USER=directus_user
DB_PASSWORD=...
DB_SSL=true

# Admin
ADMIN_EMAIL=admin@quest.com
ADMIN_PASSWORD=...

# Keys
KEY=random-key-32-chars
SECRET=random-secret-32-chars

# Redis Cache
CACHE_ENABLED=true
CACHE_STORE=redis
REDIS=redis://...
```

## Deployment

### Railway (Backend)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy services
railway up --service quest-api-gateway
railway up --service quest-workers
railway up --service quest-directus
```

### Vercel (Frontend)

```bash
# Deploy each site
cd frontend/relocation.quest
vercel --prod

cd frontend/placement.quest
vercel --prod

cd frontend/rainmaker.quest
vercel --prod
```

## Cost Structure

### Monthly Operating Costs

| Component | Cost | Purpose |
|-----------|------|---------|
| Neon Launch Tier | $60/mo | Always-on PostgreSQL |
| Railway (3 services) | $75/mo | API + Workers + Directus |
| Upstash Redis | $10/mo | BullMQ queue |
| Perplexity API | $400/mo | Research (2000 searches) |
| Claude API | $52.50/mo | Content generation |
| Replicate FLUX | $3/mo | Images |
| **Total** | **$600.60/mo** | |

**Cost per article (1000/mo)**: $0.60
**Cost per article (2000/mo)**: $0.30 (economies of scale)

## Key Features

### 4-Agent AI Pipeline

1. **ResearchAgent**: Perplexity + pgvector cache (40% cost savings)
2. **ContentAgent**: Claude Sonnet 4.5 generation
3. **EditorAgent**: Quality scoring (0-100) + HITL gate
4. **ImageAgent**: FLUX Schnell hero images

### Database-First Architecture

- **Schema lives in Neon** (YOU own it)
- **Directus reads schema** (auto-generates UI + GraphQL)
- **No sync conflicts** (Directus = window into database)
- **Vendor independence** (can remove Directus anytime)

### Production Features

- ✅ Sub-3-second page loads (p95)
- ✅ 2-3 minute article generation
- ✅ Vector similarity cache (25-40% savings)
- ✅ Human-in-the-loop quality gate
- ✅ Cost circuit breakers
- ✅ Comprehensive monitoring

## Development Workflow

### Generate an Article

```bash
# Via API
curl -X POST http://localhost:8000/api/articles/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Portugal digital nomad visa guide",
    "target_site": "relocation",
    "priority": "high"
  }'

# Response
{
  "job_id": "abc123",
  "status": "queued",
  "poll_url": "/api/jobs/abc123"
}

# Check status
curl http://localhost:8000/api/jobs/abc123

# Via Directus UI
# 1. Login to http://localhost:8055
# 2. Go to Articles collection
# 3. Click "Generate Article" flow
# 4. Fill in topic and site
# 5. Monitor progress in real-time
```

### Run Migrations

```bash
# Create new migration
psql $DATABASE_URL -f migrations/003_add_reading_time.sql

# Verify schema
psql $DATABASE_URL -c "\d articles"

# Directus auto-discovers new columns
# FastAPI needs model updates (see docs/schema-governance.md)
```

## Monitoring

### Health Checks

```bash
# API Gateway
curl http://localhost:8000/health

# Workers
curl http://localhost:8000/api/workers/status

# Queue depth
redis-cli -u $REDIS_URL LLEN bull:articles:wait
```

### Metrics Dashboard

- **Grafana**: http://localhost:3000 (if self-hosted)
- **Datadog**: https://app.datadoghq.com (if using free tier)

Key metrics:
- Article generation rate
- Cache hit rate (target: >25%)
- Quality score distribution
- Cost per article

## Documentation

- [Architecture Guide](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [Schema Governance](docs/schema-governance.md)
- [Incident Response](docs/runbook-incident-response.md)
- [Cost Management](docs/runbook-cost-breaker.md)

## Testing

```bash
cd backend

# Run all tests
pytest

# Run specific test suite
pytest tests/agents/test_research.py -v

# Run with coverage
pytest --cov=app tests/
```

## License

MIT

## Support

- **Documentation**: See `/docs` directory
- **Issues**: GitHub Issues
- **Email**: support@quest.com

---

**Version**: 2.2
**Last Updated**: October 7, 2025
**Status**: Production Ready ✅
