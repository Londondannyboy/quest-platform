# Quest Architecture - Project Structure

This document describes the organization of the Quest Architecture repository.

## 📁 Directory Structure

```
quest-architecture/
│
├── .github/                    # GitHub-specific files
│   ├── ISSUE_TEMPLATE/        # Issue templates
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   ├── workflows/             # CI/CD workflows
│   │   └── ci-cd.yml
│   └── pull_request_template.md
│
├── backend/                    # Backend Python application
│   ├── app/
│   │   ├── agents/            # AI agent implementations
│   │   │   ├── research.py    # ResearchAgent (Perplexity + cache)
│   │   │   ├── content.py     # ContentAgent (Claude)
│   │   │   ├── editor.py      # EditorAgent (quality scoring)
│   │   │   └── image.py       # ImageAgent (FLUX)
│   │   │
│   │   ├── api/               # FastAPI endpoints
│   │   │   ├── articles.py    # Article generation endpoints
│   │   │   ├── health.py      # Health checks
│   │   │   └── webhooks.py    # Webhook handlers
│   │   │
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── article.py
│   │   │   ├── research.py
│   │   │   ├── job.py
│   │   │   └── user.py
│   │   │
│   │   ├── schemas/           # Pydantic schemas
│   │   │   ├── article.py
│   │   │   └── job.py
│   │   │
│   │   ├── workers/           # BullMQ workers
│   │   │   ├── main.py        # Worker entry point
│   │   │   └── handlers.py    # Job handlers
│   │   │
│   │   ├── core/              # Core utilities
│   │   │   ├── config.py      # Configuration
│   │   │   ├── database.py    # Database connection
│   │   │   └── redis.py       # Redis connection
│   │   │
│   │   └── main.py            # FastAPI application
│   │
│   ├── migrations/            # Database migrations
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_create_users.sql
│   │   └── 003_add_indexes.sql
│   │
│   ├── tests/                 # Backend tests
│   │   ├── test_agents/
│   │   ├── test_api/
│   │   └── test_models/
│   │
│   ├── Dockerfile.api         # API Gateway Dockerfile
│   ├── Dockerfile.workers     # Workers Dockerfile
│   ├── requirements.txt       # Python dependencies
│   └── requirements-dev.txt   # Development dependencies
│
├── frontend/                  # Frontend Astro sites
│   ├── relocation.quest/      # Relocation site
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── layouts/
│   │   │   ├── pages/
│   │   │   └── lib/           # GraphQL client, utilities
│   │   ├── public/
│   │   ├── astro.config.mjs
│   │   └── package.json
│   │
│   ├── placement.quest/       # Placement site
│   │   └── [similar structure]
│   │
│   └── rainmaker.quest/       # Rainmaker site
│       └── [similar structure]
│
├── infrastructure/            # Infrastructure as Code
│   ├── railway/               # Railway configs
│   │   ├── railway.json
│   │   └── environments/
│   │
│   ├── neon/                  # Neon database configs
│   │   └── schema.sql
│   │
│   └── vercel/                # Vercel configs
│       └── vercel.json
│
├── docs/                      # Documentation
│   ├── ARCHITECTURE.md        # Full architecture spec (v2.2)
│   ├── QUICK_START.md        # Getting started guide
│   ├── DEPLOYMENT.md         # Deployment instructions
│   ├── API.md                # API reference
│   ├── COSTS.md              # Cost analysis
│   ├── MONITORING.md         # Monitoring guide
│   │
│   ├── runbooks/             # Operational procedures
│   │   ├── incident-response.md
│   │   ├── cost-breaker.md
│   │   ├── db-failover.md
│   │   └── cache-invalidation.md
│   │
│   ├── diagrams/             # Architecture diagrams
│   │   ├── system-overview.png
│   │   ├── ai-pipeline.png
│   │   └── database-schema.png
│   │
│   └── adr/                  # Architecture Decision Records
│       ├── 0001-use-neon-launch-tier.md
│       ├── 0002-4-service-architecture.md
│       └── 0003-research-cache-strategy.md
│
├── scripts/                   # Utility scripts
│   ├── smoke-tests.sh        # Smoke testing
│   ├── deploy.sh             # Deployment automation
│   └── backup.sh             # Database backups
│
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── docker-compose.yml        # Local development setup
├── CONTRIBUTING.md           # Contribution guidelines
├── LICENSE                   # MIT License
├── README.md                 # Main project README
├── SECURITY.md               # Security policy
└── PROJECT_STRUCTURE.md      # This file

```

## 📝 Key Files

### Root Level

- **README.md**: Project overview, quick links, badges
- **CONTRIBUTING.md**: How to contribute to the project
- **LICENSE**: MIT License
- **SECURITY.md**: Security policy and vulnerability reporting
- **.env.example**: Template for environment variables
- **docker-compose.yml**: Local development environment

### Backend

- **app/main.py**: FastAPI application entry point
- **app/agents/**: AI agent implementations (4-agent pipeline)
- **app/api/**: REST API endpoints
- **app/models/**: Database models (SQLAlchemy)
- **app/workers/**: Background job processors (BullMQ)
- **migrations/**: SQL migration files
- **tests/**: Test suite (pytest)

### Frontend

- **src/components/**: Reusable Astro components
- **src/layouts/**: Page layouts
- **src/pages/**: Route pages
- **src/lib/**: Utilities (GraphQL client, helpers)
- **astro.config.mjs**: Astro configuration

### Infrastructure

- **railway/**: Railway deployment configs
- **neon/**: Database schema and configs
- **vercel/**: Vercel deployment configs

### Documentation

- **docs/ARCHITECTURE.md**: Complete technical specification
- **docs/runbooks/**: Operational procedures
- **docs/diagrams/**: Visual architecture diagrams
- **docs/adr/**: Architecture Decision Records

## 🔄 Workflow

### Development Workflow

1. Clone repository
2. Set up environment (see QUICK_START.md)
3. Create feature branch
4. Make changes
5. Run tests
6. Submit PR (see CONTRIBUTING.md)

### Deployment Workflow

1. Merge to `develop` → deploys to staging
2. Test in staging
3. Merge to `main` → deploys to production
4. GitHub Actions handles CI/CD

## 📦 Module Organization

### Backend Modules

```python
# app/agents/research.py
from app.core.database import get_db_pool
from app.core.config import settings

class ResearchAgent:
    def __init__(self, db_pool, openai_client, perplexity_client):
        ...
    
    async def run(self, topic: str) -> dict:
        ...
```

### Frontend Modules

```typescript
// src/lib/directus.ts
import { ApolloClient } from '@apollo/client';

export const client = new ApolloClient({ ... });

export async function getArticles(site: string) {
    ...
}
```

## 🧪 Testing Structure

```
tests/
├── test_agents/
│   ├── test_research_agent.py
│   ├── test_content_agent.py
│   └── test_editor_agent.py
├── test_api/
│   ├── test_articles_endpoint.py
│   └── test_health_checks.py
└── test_models/
    ├── test_article_model.py
    └── test_research_model.py
```

## 📚 Documentation Standards

### Code Comments

- Use docstrings for all public functions
- Include type hints
- Document complex logic

### Markdown Docs

- Use descriptive headers
- Include code examples
- Add diagrams where helpful
- Keep up to date

### API Documentation

- Auto-generated via FastAPI
- Available at `/docs` endpoint
- Include request/response examples

## 🔐 Security Considerations

### Sensitive Files (Never Commit)

- `.env` (environment variables)
- `*.key`, `*.pem` (certificates)
- `secrets/` directory
- Any file with API keys or passwords

### Protected Directories

- `/backend/app/core/` - Core configuration
- `/migrations/` - Database migrations (review carefully)
- `/infrastructure/` - Deployment configs

## 🚀 Deployment Targets

### Services

- **API Gateway**: Railway Service 1
- **Workers**: Railway Service 2
- **Directus**: Railway Service 3
- **Redis**: Railway Service 4 (Upstash)
- **Database**: Neon PostgreSQL
- **Frontend**: Vercel (3 sites)

### Environments

- **Development**: Local (docker-compose)
- **Staging**: Railway + Vercel preview
- **Production**: Railway + Vercel production

## 📊 Monitoring & Logs

### Log Locations

- **API**: Railway logs for quest-api-gateway
- **Workers**: Railway logs for quest-workers
- **Database**: Neon console
- **Frontend**: Vercel analytics

### Metrics

- Prometheus/Grafana or Datadog
- Custom dashboards in docs/MONITORING.md

## 🔗 Related Resources

- [Full Architecture](./docs/ARCHITECTURE.md)
- [Quick Start Guide](./docs/QUICK_START.md)
- [Contributing Guide](./CONTRIBUTING.md)
- [Security Policy](./SECURITY.md)

---

**Last Updated**: October 7, 2025  
**Version**: 2.2
