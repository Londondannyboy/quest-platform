# Getting Started with Quest Platform v2.2

**Quick start guide to get the platform running locally in 15 minutes.**

---

## What You'll Build

By the end of this guide, you'll have:

- ✅ PostgreSQL database with pgvector for AI caching
- ✅ FastAPI backend with 4-agent AI pipeline
- ✅ Directus CMS with auto-generated GraphQL API
- ✅ Astro frontend site
- ✅ Ability to generate AI articles in 2-3 minutes

---

## Prerequisites (5 minutes)

### Required Software

```bash
# macOS (using Homebrew)
brew install python@3.11 node postgresql docker

# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3-pip nodejs npm postgresql-client docker.io

# Verify installations
python3 --version  # Should be 3.11+
node --version     # Should be 18+
docker --version   # Should be 20+
psql --version     # Should be 14+
```

### Required Accounts (Free Tiers Available)

1. **Neon PostgreSQL** - https://neon.tech (Free tier with pgvector)
2. **Upstash Redis** - https://upstash.com (Free tier)
3. **Anthropic Claude** - https://console.anthropic.com (Pay-as-you-go)
4. **OpenAI** - https://platform.openai.com (Pay-as-you-go)
5. **Perplexity** - https://www.perplexity.ai/settings/api (Optional)
6. **Replicate** - https://replicate.com (Optional, for images)
7. **Cloudinary** - https://cloudinary.com (Free tier)

---

## Step 1: Clone and Setup (3 minutes)

```bash
# Navigate to quest-platform directory
cd ~/quest-platform

# Run automated setup script
chmod +x setup.sh
./setup.sh
```

This script will:
- Create Python virtual environment
- Install Python dependencies
- Setup Directus configuration
- Install npm dependencies for frontend sites
- Generate secure keys

---

## Step 2: Database Setup (3 minutes)

### Option A: Neon (Recommended - Free Tier)

1. **Create Neon account** at https://neon.tech

2. **Create database:**
   ```bash
   # Install Neon CLI
   npm install -g neonctl

   # Login
   neon auth login

   # Create project
   neon projects create --name quest-dev

   # Get connection string
   neon connection-string quest-dev
   ```

3. **Run migrations:**
   ```bash
   export DATABASE_URL="postgresql://neondb_owner:password@ep-xxx.neon.tech/neondb?sslmode=require"

   psql $DATABASE_URL -f backend/migrations/001_initial_schema.sql
   ```

### Option B: Local PostgreSQL

```bash
# Start PostgreSQL
brew services start postgresql  # macOS
# or
sudo service postgresql start   # Ubuntu

# Create database
createdb quest_dev

# Install pgvector extension
psql quest_dev -c "CREATE EXTENSION vector;"

# Run migrations
export DATABASE_URL="postgresql://localhost/quest_dev"
psql $DATABASE_URL -f backend/migrations/001_initial_schema.sql
```

---

## Step 3: Configure Environment Variables (2 minutes)

### Backend Configuration

Edit `backend/.env`:

```bash
# Required
DATABASE_URL=postgresql://...  # From Step 2
REDIS_URL=redis://...          # From Upstash or local

# AI APIs (at least one required)
ANTHROPIC_API_KEY=sk-ant-...   # Claude for content generation
OPENAI_API_KEY=sk-...          # For embeddings (required for cache)

# Optional (for full functionality)
PERPLEXITY_API_KEY=pplx-...    # For research
REPLICATE_API_KEY=r8_...       # For images
CLOUDINARY_CLOUD_NAME=...      # For image CDN
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...

# Cost limits (for safety)
DAILY_COST_CAP=5.00            # Start small for testing
PER_JOB_COST_CAP=0.50
```

### Directus Configuration

Edit `directus/.env`:

```bash
# Use same Neon database (different user)
NEON_HOST=ep-xxx.neon.tech
NEON_DATABASE=neondb
DIRECTUS_DB_PASSWORD=your-password

# Admin credentials
ADMIN_EMAIL=admin@quest.local
ADMIN_PASSWORD=your-secure-password

# Redis (same as backend)
REDIS_URL=redis://...

# Cloudinary (same as backend)
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
```

---

## Step 4: Start Services (2 minutes)

### Terminal 1: Directus CMS

```bash
cd directus
docker-compose up

# Wait for: "Server started at http://0.0.0.0:8055"
# Open http://localhost:8055
# Login with ADMIN_EMAIL and ADMIN_PASSWORD
```

### Terminal 2: FastAPI Backend

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload

# Wait for: "Application startup complete"
# Open http://localhost:8000/docs (API documentation)
```

### Terminal 3: Astro Frontend (Optional)

```bash
cd frontend/relocation.quest
npm run dev

# Wait for: "Local: http://localhost:4321"
# Open http://localhost:4321
```

---

## Step 5: Generate Your First Article (2 minutes)

### Via API (Command Line)

```bash
# Generate article
curl -X POST http://localhost:8000/api/articles/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Best digital nomad cities in Portugal 2025",
    "target_site": "relocation",
    "priority": "normal"
  }'

# Response:
# {
#   "job_id": "abc-123-def-456",
#   "status": "queued",
#   "poll_url": "/api/jobs/abc-123-def-456"
# }

# Check status (repeat every 30s)
curl http://localhost:8000/api/jobs/abc-123-def-456

# When status = "completed", you'll get article_id
```

### Via Directus UI

1. **Go to http://localhost:8055**
2. **Login** with admin credentials
3. **Go to Articles collection**
4. **Click "+" to create new**
5. **Fill in:**
   - Topic: "Best digital nomad cities in Portugal 2025"
   - Target Site: relocation
6. **Click Save**
7. **Wait 2-3 minutes** for article to appear

### Via API Documentation

1. **Go to http://localhost:8000/docs**
2. **Expand** `POST /api/articles/generate`
3. **Click** "Try it out"
4. **Enter JSON:**
   ```json
   {
     "topic": "Best digital nomad cities in Portugal 2025",
     "target_site": "relocation",
     "priority": "normal"
   }
   ```
5. **Click** "Execute"
6. **Copy job_id** from response
7. **Use** `GET /api/jobs/{job_id}` to poll status

---

## What Happens Behind the Scenes?

### 4-Agent Pipeline (2-3 minutes total)

```
1. ResearchAgent (30-60s)
   ↓ Queries Perplexity API or checks pgvector cache
   ↓ Returns: Research data with citations

2. ContentAgent (60-90s)
   ↓ Sends research to Claude Sonnet 4.5
   ↓ Returns: Full article (1500-2000 words)

3. EditorAgent (20-30s)
   ↓ Scores article quality (0-100)
   ↓ Decision: publish (≥85), review (70-84), reject (<70)

4. ImageAgent (60s, parallel)
   ↓ Generates hero image with FLUX Schnell
   ↓ Uploads to Cloudinary CDN
```

### Cost Breakdown (Per Article)

```
Research:  $0.00-0.20 (cache hit vs miss)
Content:   $0.04 (Claude Sonnet 4.5)
Editor:    $0.005 (quality scoring)
Image:     $0.003 (FLUX Schnell)
────────────────────────────────────
Total:     $0.05-0.25 per article
```

---

## Verify Everything Works

### ✅ Database Check

```bash
psql $DATABASE_URL -c "SELECT COUNT(*) FROM articles;"
# Should return count (0 initially)

psql $DATABASE_URL -c "SELECT title, status, quality_score FROM articles LIMIT 5;"
# Should show your generated articles
```

### ✅ API Health Check

```bash
curl http://localhost:8000/api/health

# Should return:
# {
#   "status": "healthy",
#   "checks": {
#     "api": "healthy",
#     "database": "healthy",
#     "redis": "healthy",
#     "queue": "healthy"
#   }
# }
```

### ✅ Cache Performance

```bash
# Check if research cache is working
psql $DATABASE_URL -c "SELECT COUNT(*), AVG(cache_hits) FROM article_research;"

# Generate similar topic twice - second should be faster and cheaper
```

### ✅ Cost Tracking

```bash
# Check costs for today
psql $DATABASE_URL -c "SELECT * FROM daily_costs WHERE date = CURRENT_DATE;"

# Example output:
# date       | articles | total_cost | avg_cost
# -----------+----------+------------+----------
# 2025-10-07 |    5     |   0.65     |   0.13
```

---

## Common Issues & Solutions

### "Database connection failed"

```bash
# Verify DATABASE_URL
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1;"

# If Neon: Check if compute is active (not suspended)
```

### "Redis connection failed"

```bash
# Test Redis
redis-cli -u $REDIS_URL PING

# Should return: PONG

# If local Redis not running:
brew services start redis  # macOS
sudo service redis-server start  # Ubuntu
```

### "AI API rate limit"

```bash
# Check API key is valid
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'

# Should not return 401/403
```

### "Directus schema not showing"

```bash
# Restart Directus
cd directus
docker-compose restart

# Verify database user has permissions
psql $DATABASE_URL -c "\dp articles"

# Should show directus_user with SELECT, INSERT, UPDATE, DELETE
```

---

## Next Steps

### 🚀 Development

1. **Customize Agents:**
   - Edit `backend/app/agents/content.py` for writing style
   - Edit `backend/app/agents/research.py` for research depth
   - Edit `backend/app/agents/editor.py` for quality thresholds

2. **Add Features:**
   - Create custom Directus flows
   - Add new article fields
   - Customize Astro templates

3. **Test at Scale:**
   - Generate 50+ articles
   - Measure cache hit rate (target: >25%)
   - Monitor costs with circuit breakers

### 📊 Monitoring

```bash
# Real-time metrics
curl http://localhost:8000/metrics

# Queue depth
redis-cli -u $REDIS_URL LLEN quest:jobs:queued

# Database performance
psql $DATABASE_URL -c "
  SELECT query, calls, mean_exec_time
  FROM pg_stat_statements
  ORDER BY mean_exec_time DESC
  LIMIT 10;
"
```

### 🌐 Production Deployment

When ready for production:

1. **Read DEPLOYMENT.md** for full instructions
2. **Upgrade to Neon Launch tier** (always-on, no cold starts)
3. **Deploy to Railway** (API + Directus + Workers)
4. **Deploy to Vercel** (Astro sites)
5. **Configure monitoring** (Sentry, Prometheus)

---

## Learning Resources

### Understand the Architecture

- **CLAUDE.md** - Complete architecture v2.2 specification
- **README.md** - Project overview and features
- **DEPLOYMENT.md** - Production deployment guide

### API Documentation

- **FastAPI Docs:** http://localhost:8000/docs
- **Directus API:** http://localhost:8055/admin/settings/api
- **GraphQL Playground:** http://localhost:8055/graphql

### Database Schema

```bash
# View all tables
psql $DATABASE_URL -c "\dt"

# View table schema
psql $DATABASE_URL -c "\d articles"
psql $DATABASE_URL -c "\d article_research"
```

---

## Get Help

- **GitHub Issues:** Report bugs and request features
- **Documentation:** Check `/docs` directory
- **API Logs:** Check terminal output for errors
- **Database Logs:** Check Neon dashboard

---

**You're all set! 🎉**

Generate your first 10 articles and watch the magic happen.

For questions, see documentation or check API logs for detailed error messages.

Happy building! 🚀
