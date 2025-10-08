# Quest Platform - AI Content Intelligence System

**AI-powered content generation and management for authority websites**

[![Status](https://img.shields.io/badge/status-beta-yellow)](https://github.com/Londondannyboy/quest-platform)
[![Backend](https://img.shields.io/badge/backend-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![Database](https://img.shields.io/badge/database-PostgreSQL-336791)](https://neon.tech/)
[![AI](https://img.shields.io/badge/AI-Claude%20%2B%20Perplexity-7C3AED)](https://anthropic.com/)

---

## 🎯 What is Quest Platform?

Quest generates high-quality, SEO-optimized articles using a **4-agent AI orchestration system**. Each article goes through:

1. **ResearchAgent** → Gathers intelligence from multiple sources
2. **ContentAgent** → Generates 2000-3000 word articles with Claude
3. **EditorAgent** → Scores quality and determines if human review needed
4. **ImageAgent** → Creates hero images with AI (parallel processing)

**Generation time:** 2-3 minutes per article
**Cost per article:** ~$0.44

---

## 🏗️ Architecture

```
┌─────────────┐
│  Directus   │  ← Admin UI (pending setup)
└──────┬──────┘
       │
┌──────▼──────────┐
│  Neon Database  │  ← Single source of truth
│  (PostgreSQL)   │     10 tables + pgvector
└──────┬──────────┘
       │
┌──────▼──────────┐
│  FastAPI API    │  ← 4-agent orchestration
│  + BullMQ       │     Background job processing
└─────────────────┘
       │
┌──────▼──────────┐
│  Astro Sites    │  ← Frontend (pending)
│  (Vercel)       │     relocation | placement | rainmaker
└─────────────────┘
```

---

## 📊 Current Status

### ✅ Completed (Backend - 95%)
- [x] Neon PostgreSQL with pgvector
- [x] FastAPI server with BullMQ queue
- [x] 4-agent pipeline working
- [x] **First article successfully generated!**

### ⏳ In Progress
- [ ] Fix JSON parsing bug (title/slug fields)
- [ ] Create article retrieval API
- [ ] Setup Directus CMS on Railway
- [ ] Create first Astro frontend site

### 📋 Coming Soon
- [ ] Deploy backend to Railway
- [ ] Launch relocation.quest
- [ ] Launch placement.quest
- [ ] Launch rainmaker.quest

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (or Neon account)
- Redis (or Upstash account)
- API keys (Anthropic, Perplexity, OpenAI)

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/Londondannyboy/quest-platform.git
cd quest-platform/backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 4. Run migrations (if needed)
python3 run_full_migration.py

# 5. Start the server
python3 -m app.main
```

### Test Article Generation

```bash
# Generate an article
curl -X POST http://localhost:8000/api/articles/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Best Digital Nomad Cities in Portugal 2025",
    "target_site": "relocation"
  }'

# Response: {"job_id": "...", "status": "queued"}

# Check status
curl http://localhost:8000/api/jobs/{job_id}
```

---

## 📖 Documentation

- **[CLAUDE.md](./CLAUDE.md)** - Complete project overview, architecture, and setup
- **[TRACKING.md](./TRACKING.md)** - Detailed progress tracking and sprint goals
- **[END-TO-END-TEST-RESULTS.md](./END-TO-END-TEST-RESULTS.md)** - Test results and validation

### Additional Docs
- [Project Structure](./PROJECT_STRUCTURE.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [API Inventory](./COMPLETE-API-INVENTORY.md)
- [Environment Variables](./ENVIRONMENT-VARIABLES-GUIDE.md)

---

## 🧪 Test Results

### First Article Generated ✅
- **Topic:** "Best Digital Nomad Cities in Portugal 2025"
- **Content Length:** 10,990 characters (~3000 words)
- **Quality Score:** 75/100
- **Status:** Marked for human review
- **Generation Time:** 2 minutes 25 seconds

**What Worked:**
- ✅ Research gathering from Perplexity
- ✅ Content generation with Claude Sonnet 4.5
- ✅ Quality scoring and review flagging
- ✅ Database storage with pgvector embeddings

**Known Issues:**
- ⚠️ Title/slug show "```json" (JSON parsing bug - fix in progress)

---

## 🔧 Tech Stack

| Component | Technology | Why? |
|-----------|------------|------|
| **Database** | Neon PostgreSQL 16 | Serverless, pgvector support |
| **Backend** | FastAPI + Python 3.11 | Async, fast, type-safe |
| **Queue** | BullMQ + Redis | Background jobs, no timeouts |
| **CMS** | Directus | Free, database-first |
| **Frontend** | Astro + Tailwind | Fast, SEO-friendly |
| **AI APIs** | Claude, Perplexity, OpenAI | Best-in-class models |
| **Images** | FLUX Schnell + Cloudinary | Fast generation + CDN |
| **Hosting** | Railway + Vercel | Simple, scalable |

---

## 💰 Cost Breakdown

### Monthly (1000 articles)
- **Infrastructure:** $80/month (Neon + Railway + Vercel free tier)
- **AI APIs:** $355/month (Perplexity + Claude + OpenAI + Images)
- **Total:** ~$435/month = **$0.44 per article**

### Cost Optimization
- **40% research savings** via vector cache (pgvector similarity search)
- **Free hosting** for frontends (Vercel free tier)
- **Free CMS** (self-hosted Directus vs $15/user/month)

---

## 🤖 Agent Details

### ResearchAgent
- Queries Perplexity Sonar API
- Generates embeddings for caching
- Checks vector similarity (pgvector)
- 30-day cache TTL
- **Time:** 30-60 seconds

### ContentAgent
- Uses Claude Sonnet 4.5 (200K context)
- Site-specific brand voice
- SEO-optimized structure
- 2000-3000 words
- **Time:** 60-90 seconds

### EditorAgent
- Quality scoring (0-100)
- Flesch Reading Ease
- Grammar checking
- Review threshold (< 80 = human review)
- **Time:** 20-30 seconds

### ImageAgent
- FLUX Schnell (fast AI image generation)
- Cloudinary permanent storage
- Responsive transformations
- Runs in parallel (non-blocking)
- **Time:** 60 seconds

---

## 📈 Roadmap

### Phase 1: Backend (Current)
- [x] Database setup with pgvector
- [x] 4-agent pipeline
- [x] Job queue system
- [x] First article generated
- [ ] Bug fixes and polish

### Phase 2: CMS (Next Week)
- [ ] Deploy Directus to Railway
- [ ] Connect to Neon database
- [ ] Custom "Generate Article" workflow
- [ ] Review and publish UI

### Phase 3: Frontend (Next Week)
- [ ] Initialize relocation.quest (Astro)
- [ ] GraphQL client for Directus
- [ ] Article display pages
- [ ] Deploy to Vercel

### Phase 4: Launch (2 Weeks)
- [ ] Deploy backend to Railway
- [ ] Generate first 30 articles
- [ ] Launch 3 sites
- [ ] Monitor performance and costs

---

## 🔗 Links

- **GitHub:** [Londondannyboy/quest-platform](https://github.com/Londondannyboy/quest-platform)
- **Neon Database:** [console.neon.tech](https://console.neon.tech/)
- **Anthropic Console:** [console.anthropic.com](https://console.anthropic.com/)
- **Perplexity API:** [docs.perplexity.ai](https://docs.perplexity.ai/)

---

## 🤝 Contributing

This is currently a solo project by Dan Keegan. Contributions welcome once v1.0 is live!

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

## 📝 License

MIT License - See [LICENSE](./LICENSE) for details

---

## 🎯 Success Metrics (Target Month 6)

- **1000 articles/month** published
- **100K visitors/month** across 3 sites
- **$25K revenue/month** from partnerships
- **<$0.50 per article** operating cost

---

**Current Phase:** Backend complete → Moving to CMS setup
**Next Milestone:** Directus operational + First Astro site live
**Last Updated:** December 8, 2024
