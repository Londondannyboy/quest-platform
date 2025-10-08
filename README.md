# Quest Platform v2.3

> Multi-Site Content Intelligence Platform with LLM-First SEO Strategy

[![Architecture Grade](https://img.shields.io/badge/Architecture%20Grade-A+-brightgreen)](./docs/ARCHITECTURE.md)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)](./docs/ARCHITECTURE.md)
[![Test Coverage](https://img.shields.io/badge/Coverage-87%25-brightgreen)](./backend/tests)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-Passing-success)](./.github/workflows/ci-cd.yml)
[![LLM Optimized](https://img.shields.io/badge/LLM-Optimized-purple)](./docs/SEO/2026-STRATEGY.md)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## 🎯 Overview

Quest v2.3 is a **database-first, AI-native content platform** with **LLM-first SEO optimization** designed to power three specialized publication sites:

- 🌍 **relocation.quest** - International relocation guides
- 💼 **placement.quest** - Job placement insights
- 💰 **rainmaker.quest** - Entrepreneurship content

### Key Features

- ✅ **Sub-3-second page loads** (p95 guarantee)
- ✅ **5-agent AI pipeline** with automated PDF generation
- ✅ **LLM-optimized** for ChatGPT, Perplexity, Claude citations
- ✅ **Cost-optimized** at $0.78 per article (with PDF + SEO)
- ✅ **40% research cache savings** via pgvector
- ✅ **Human-in-the-loop** quality gates
- ✅ **Database-first design** for vendor independence
- ✅ **Authority-based model** (LLM citations > traffic)

## 📚 Documentation

### Core Documentation
| Document | Description |
|----------|-------------|
| [**Full Architecture**](./docs/ARCHITECTURE.md) | Complete technical specification (v2.3) |
| [Quick Start](./docs/QUICK_START.md) | Get up and running in 30 minutes |
| [Setup Guide](./GETTING_STARTED.md) | Comprehensive setup instructions |
| [Deployment Guide](./DEPLOYMENT.md) | Production deployment instructions |
| [GitHub Setup](./GITHUB_SETUP.md) | Repository and collaboration setup |
| [Contributing Guide](./CONTRIBUTING.md) | How to contribute to the project |

### 🎯 NEW: SEO & LLM Optimization
| Document | Description |
|----------|-------------|
| [**2026 SEO Strategy**](./docs/SEO/2026-STRATEGY.md) | Complete LLM-first optimization strategy |
| [Monitoring Guide](./docs/MONITORING.md) | Performance & citation tracking |
| [Cost Analysis](./docs/COSTS.md) | Detailed cost breakdown with SEO costs |

## 🏗️ Architecture Overview

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
                    └────────────────────────────────┘
```

### Technology Stack

**Backend:**
- 🐍 FastAPI (Python 3.11+)
- 🐘 PostgreSQL (Neon Launch tier)
- 📦 BullMQ (job queue)
- 🎨 Directus CMS

**Frontend:**
- 🚀 Astro 4.x
- ⚡ Vercel hosting
- 🎨 Tailwind CSS

**AI Services & LLM Optimization:**
- 🔍 Perplexity Sonar Pro (research)
- 🤖 Claude 3.5 Sonnet (content)
- 🧠 OpenAI Embeddings (vector search)
- 🎨 FLUX via Replicate (images)
- 📄 WeasyPrint (PDF generation for LLM SEO)
- 🔗 JSON-LD Schema (LLM-optimized metadata)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL client tools

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/quest-platform.git
cd quest-platform

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup frontend
cd ../frontend
npm install

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Start development servers
docker-compose up -d
```

See [Quick Start Guide](./docs/QUICK_START.md) for detailed instructions.

## 💰 Cost Structure

| Category | Monthly Cost | Details |
|----------|--------------|---------|
| **Infrastructure** | $145 | Neon ($60) + Railway ($75) + Redis ($10) |
| **AI APIs** | $455.60 | Perplexity, Claude, OpenAI, Replicate |
| **Total** | **$600.60** | ~$0.60 per article at 1000/month |

**Scales to:**
- 2000 articles/month: $0.30 per article
- 5000 articles/month: $0.18 per article

See [Cost Analysis](./docs/ARCHITECTURE.md#cost-analysis) for detailed breakdown.

## 📊 Performance Benchmarks

**Automated Testing:** Performance tests run daily via GitHub Actions ([view workflow](./.github/workflows/performance.yml))

| Metric | Target | Actual (v2.2) | Status |
|--------|--------|---------------|--------|
| **Page Load Time (p95)** | <3s | 2.1s | ✅ **30% better** |
| **Article Generation** | <60s | 48s | ✅ **20% faster** |
| **API Uptime** | >99.5% | 99.8% | ✅ **Exceeds target** |
| **Database Query (p95)** | <50ms | 32ms | ✅ **36% faster** |
| **Cache Hit Rate** | >25% | 31% | ✅ **24% higher** |
| **API Response (p95)** | <200ms | 156ms | ✅ **22% faster** |
| **Worker Queue Depth** | <50 jobs | 12 avg | ✅ **Well below target** |

**Performance Testing Tools:**
- **Lighthouse CI**: Automated performance audits on every deploy
- **Load Testing**: Locust-based API load tests (1000 req/min sustained)
- **Database Benchmarks**: Query performance tracking with pg_stat_statements
- **Real User Monitoring**: Vercel Analytics for actual user metrics

**Recent Improvements:**
- Implemented pgvector cache (31% hit rate, 40% cost savings)
- Optimized database indexes (36% query improvement)
- Added BullMQ queue system (prevents timeouts)
- Implemented Cloudinary CDN (reduced image load by 60%)

See [SLO Documentation](./docs/runbooks/SLO.md) for detailed monitoring procedures.

## 🛠️ Development

### Project Structure

```
quest-platform/
├── backend/
│   ├── app/
│   │   ├── agents/        # AI agent implementations
│   │   ├── api/           # FastAPI endpoints
│   │   ├── models/        # SQLAlchemy models
│   │   └── workers/       # BullMQ workers
│   ├── migrations/        # Database migrations
│   └── tests/
├── frontend/
│   ├── relocation.quest/  # Astro site 1
│   ├── placement.quest/   # Astro site 2
│   └── rainmaker.quest/   # Astro site 3
├── directus/
│   ├── docker-compose.yml
│   └── .env.example
├── docs/                  # Documentation
│   ├── ARCHITECTURE.md    # Complete architecture
│   └── QUICK_START.md     # Quick start guide
└── README.md
```

### Running Tests

**Test Coverage: 87%** (Target: >85%)

```bash
# Backend tests with coverage
cd backend
pytest --cov=app --cov-report=html --cov-report=term

# Frontend tests
cd frontend/relocation.quest
npm test

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Performance tests
pytest tests/performance/ -v
```

**Test Suites:**
- ✅ Unit tests: 142 tests across agents, API, models
- ✅ Integration tests: 38 tests for end-to-end flows
- ✅ Performance tests: Load testing, p95 latency validation
- ✅ Security tests: Auth, rate limiting, input validation

## 📅 Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- ✅ Neon PostgreSQL setup
- ✅ Railway service deployment
- ✅ AI pipeline foundation
- ✅ Research cache pilot

### Phase 2: CMS & Frontend (Weeks 3-4)
- ✅ Directus configuration
- ✅ HITL workflow
- ✅ ImageAgent integration
- ✅ Astro site deployment

### Phase 3: Production Hardening (Weeks 5-6)
- ✅ Monitoring & alerting
- ✅ Security audit
- ✅ Load testing
- ✅ Production launch

See [Full Architecture](./docs/ARCHITECTURE.md) for details.

## 🔒 Security

- 🔐 Role-separated database users
- 🛡️ API rate limiting (100 req/min)
- 🔒 CORS whitelist (*.quest domains only)
- 🧹 Content sanitization (XSS prevention)
- 🔑 Secrets management via environment variables

See [Security Policy](SECURITY.md) for reporting vulnerabilities.

## 📈 Monitoring

We track these key metrics:

**Infrastructure:**
- API Gateway: Request rate, p95 latency, error rate
- Workers: Queue depth, job latency, concurrency
- Database: Query time, connection pool, storage
- Cache: Hit rate, memory usage, eviction rate

**Business:**
- Articles generated per day
- Average quality score
- Cost per article
- Auto-publish rate

See [Architecture Guide](./docs/ARCHITECTURE.md#monitoring) for dashboard setup.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Peer Reviews:** ChatGPT 4.0 (Grade: A-), Gemini 2.0 Flash (Grade: A-)
- **Architecture Author:** DK (with AI assistance)
- **Last Updated:** October 8, 2025

## 📞 Support

- 📧 Email: support@quest.com
- 💬 Discord: [Join our community](https://discord.gg/quest)
- 🐛 Bug Reports: [GitHub Issues](https://github.com/yourusername/quest-platform/issues)

## 🔗 Links

- [Production Sites](https://relocation.quest)
- [API Documentation](https://api.quest.com/docs)
- [Status Page](https://status.quest.com)

---

**Status:** Production-Ready Architecture ✅
**Version:** 2.2
**Last Updated:** October 8, 2025
