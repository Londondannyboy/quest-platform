# Quest Platform v2.2 - Deployment Guide

Complete deployment instructions for production environment.

---

## Prerequisites

### Required Accounts

1. **Neon** (PostgreSQL database)
   - Sign up: https://neon.tech
   - Plan: Launch tier ($60/mo minimum)

2. **Railway** (Backend hosting)
   - Sign up: https://railway.app
   - Plan: Pro ($30/mo estimated)

3. **Vercel** (Frontend hosting)
   - Sign up: https://vercel.com
   - Plan: Free tier (3 sites)

4. **Upstash** (Redis/Queue)
   - Sign up: https://upstash.com
   - Plan: Pro ($10/mo)

5. **Cloudinary** (Image CDN)
   - Sign up: https://cloudinary.com
   - Plan: Free tier

### Required CLI Tools

```bash
# Neon CLI
npm install -g neonctl

# Railway CLI
npm install -g @railway/cli

# Vercel CLI
npm install -g vercel

# PostgreSQL client
brew install postgresql  # macOS
# or
sudo apt-get install postgresql-client  # Ubuntu
```

---

## Part 1: Database Setup (Neon)

### Step 1: Create Neon Project

```bash
# Login to Neon
neon auth login

# Create project (IMPORTANT: Launch tier with always-on compute)
neon projects create \
  --name quest-production \
  --plan launch \
  --region us-east-1

# Get connection string
neon connection-string quest-production
```

**Example output:**
```
postgresql://neondb_owner:AbC123...@ep-cool-frost-123456.us-east-1.aws.neon.tech/neondb?sslmode=require
```

**CRITICAL:** Disable auto-suspend to eliminate cold starts:

```bash
# Via Neon dashboard:
# 1. Go to project settings
# 2. Compute settings
# 3. Set "Suspend compute after" to "Never"
# 4. Confirm minimum compute: 0.25 CU
```

### Step 2: Run Database Migrations

```bash
# Export connection string
export DATABASE_URL="postgresql://neondb_owner:...@ep-xxx.neon.tech/neondb?sslmode=require"

# Run initial schema
psql $DATABASE_URL -f backend/migrations/001_initial_schema.sql

# Create database users (edit passwords first!)
# Open backend/migrations/002_create_users.sql
# Replace ${FASTAPI_DB_PASSWORD}, ${DIRECTUS_DB_PASSWORD}, ${READONLY_DB_PASSWORD}

psql $DATABASE_URL -f backend/migrations/002_create_users.sql
```

### Step 3: Verify Setup

```bash
# Check extensions
psql $DATABASE_URL -c "SELECT extname FROM pg_extension;"

# Should see: uuid-ossp, pg_trgm, vector, pg_stat_statements, btree_gin, pg_cron

# Check tables
psql $DATABASE_URL -c "\dt"

# Should see: articles, article_research, job_status, users

# Test vector search
psql $DATABASE_URL -c "SELECT COUNT(*) FROM article_research;"
```

---

## Part 2: Redis Setup (Upstash)

### Step 1: Create Redis Database

1. Go to https://console.upstash.com/redis
2. Click "Create Database"
3. Name: `quest-production`
4. Region: `us-east-1` (same as Neon)
5. Plan: Pro ($10/mo)
6. TLS: Enabled

### Step 2: Get Connection String

```bash
# Copy Redis URL from Upstash dashboard
# Format: redis://default:password@region.upstash.io:6379

export REDIS_URL="redis://default:AbC123...@us1-sought-mantis-12345.upstash.io:6379"
```

---

## Part 3: Backend Deployment (Railway)

### Step 1: Login to Railway

```bash
railway login
```

### Step 2: Create Project

```bash
cd quest-platform/backend

# Initialize Railway project
railway init

# Enter project name: quest-production
```

### Step 3: Set Environment Variables

```bash
# Database (fastapi_user connection)
railway variables set DATABASE_URL="postgresql://fastapi_user:password@ep-xxx.neon.tech/neondb?sslmode=require"

# Redis
railway variables set REDIS_URL="redis://default:password@us1-xxx.upstash.io:6379"

# AI APIs
railway variables set PERPLEXITY_API_KEY="pplx-..."
railway variables set ANTHROPIC_API_KEY="sk-ant-..."
railway variables set OPENAI_API_KEY="sk-..."
railway variables set REPLICATE_API_KEY="r8_..."

# Cloudinary
railway variables set CLOUDINARY_CLOUD_NAME="your-cloud"
railway variables set CLOUDINARY_API_KEY="..."
railway variables set CLOUDINARY_API_SECRET="..."

# Application settings
railway variables set APP_ENV="production"
railway variables set DEBUG="false"
railway variables set LOG_LEVEL="INFO"

# Cost controls
railway variables set DAILY_COST_CAP="30.00"
railway variables set PER_JOB_COST_CAP="0.75"
railway variables set ENABLE_COST_CIRCUIT_BREAKER="true"

# CORS
railway variables set CORS_ORIGINS="https://relocation.quest,https://placement.quest,https://rainmaker.quest"
```

### Step 4: Deploy FastAPI

```bash
# Create Dockerfile if not exists (Railway auto-detects)
# Deploy
railway up

# Check logs
railway logs

# Get public URL
railway domain
```

**Expected output:**
```
✓ Deployment successful
→ https://quest-production.up.railway.app
```

### Step 5: Verify Deployment

```bash
# Health check
curl https://quest-production.up.railway.app/api/health

# Should return:
# {"status":"healthy","version":"2.2.0","environment":"production","checks":{...}}
```

---

## Part 4: Directus Deployment (Railway)

### Step 1: Create Directus Service

```bash
cd quest-platform/directus

# Create new Railway service
railway init --name quest-directus

# Set environment variables
railway variables set DB_CLIENT="postgres"
railway variables set DB_HOST="ep-xxx.neon.tech"
railway variables set DB_PORT="5432"
railway variables set DB_DATABASE="neondb"
railway variables set DB_USER="directus_user"
railway variables set DB_PASSWORD="your-directus-password"
railway variables set DB_SSL="true"

railway variables set ADMIN_EMAIL="admin@quest.com"
railway variables set ADMIN_PASSWORD="your-admin-password"

railway variables set KEY="$(openssl rand -base64 32)"
railway variables set SECRET="$(openssl rand -base64 32)"

railway variables set REDIS="$REDIS_URL"

railway variables set CLOUDINARY_CLOUD_NAME="your-cloud"
railway variables set CLOUDINARY_API_KEY="..."
railway variables set CLOUDINARY_API_SECRET="..."

# Deploy
railway up --dockerfile Dockerfile.directus
```

### Step 2: Verify Directus

```bash
# Get Directus URL
railway domain

# Open in browser
open https://quest-directus.up.railway.app

# Login with ADMIN_EMAIL and ADMIN_PASSWORD
```

### Step 3: Configure Directus

1. **Verify Schema Auto-Discovery:**
   - Go to Settings > Data Model
   - Should see: `articles`, `users`, `article_research`, `job_status`
   - Fields should match database schema exactly

2. **Set Permissions:**
   - Go to Settings > Roles & Permissions
   - Create role: `Editor`
   - Grant permissions:
     - `articles`: Create, Read, Update (no Delete)
     - `users`: Read only

3. **Create GraphQL API Token:**
   - Go to Settings > Access Tokens
   - Create token: `astro-sites`
   - Copy token for frontend deployment

---

## Part 5: Frontend Deployment (Vercel)

### Step 1: Deploy Relocation.Quest

```bash
cd quest-platform/frontend/relocation.quest

# Install dependencies
npm install

# Create .env.local
cat > .env.local << EOF
DIRECTUS_URL=https://quest-directus.up.railway.app
DIRECTUS_API_TOKEN=your-graphql-token-here
EOF

# Test locally
npm run dev
# Open http://localhost:4321

# Deploy to Vercel
vercel --prod

# Set custom domain (in Vercel dashboard)
# Domain: relocation.quest
```

### Step 2: Deploy Placement.Quest

```bash
cd quest-platform/frontend/placement.quest

npm install
# Copy .env.local from relocation.quest
vercel --prod

# Domain: placement.quest
```

### Step 3: Deploy Rainmaker.Quest

```bash
cd quest-platform/frontend/rainmaker.quest

npm install
# Copy .env.local
vercel --prod

# Domain: rainmaker.quest
```

---

## Part 6: DNS Configuration

### For Each Domain (relocation.quest, placement.quest, rainmaker.quest)

1. **Go to your domain registrar** (e.g., Namecheap, GoDaddy)

2. **Add Vercel DNS records:**
   ```
   Type: A
   Host: @
   Value: 76.76.21.21

   Type: CNAME
   Host: www
   Value: cname.vercel-dns.com
   ```

3. **Verify in Vercel:**
   - Go to project settings > Domains
   - Add custom domain
   - Wait for DNS propagation (5-60 minutes)

---

## Part 7: Post-Deployment Validation

### 7.1 Test Article Generation

```bash
# Generate test article via API
curl -X POST https://quest-production.up.railway.app/api/articles/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Portugal digital nomad visa 2025",
    "target_site": "relocation",
    "priority": "high"
  }'

# Should return:
# {"job_id":"abc-123","status":"queued","poll_url":"/api/jobs/abc-123"}

# Poll job status
curl https://quest-production.up.railway.app/api/jobs/abc-123

# Wait for completion (2-3 minutes)
```

### 7.2 Verify in Directus

1. Login to Directus admin
2. Go to Articles collection
3. Should see new article with:
   - Status: `review` or `approved`
   - Quality score: 70-100
   - Content, title, excerpt populated

### 7.3 Check Frontend

```bash
# Open site
open https://relocation.quest

# Should see article (if published)
```

### 7.4 Monitor Costs

```bash
# Check daily costs
psql $DATABASE_URL -c "SELECT * FROM daily_costs WHERE date = CURRENT_DATE;"

# Check cache performance
psql $DATABASE_URL -c "SELECT * FROM cache_performance WHERE date = CURRENT_DATE;"
```

---

## Part 8: Monitoring Setup

### 8.1 Enable Prometheus (Optional)

```bash
# In Railway, create monitoring service
railway init --name quest-prometheus

# Deploy Prometheus + Grafana
# Import dashboard from docs/grafana-dashboard.json
```

### 8.2 Enable Sentry (Error Tracking)

```bash
# Sign up at https://sentry.io
# Create project: quest-platform

# Set environment variable in Railway
railway variables set SENTRY_DSN="https://xxx@sentry.io/123456"
railway variables set SENTRY_ENVIRONMENT="production"
```

### 8.3 Setup Alerts

```bash
# Email alerts for:
# - Daily cost >$30
# - Queue depth >100
# - API error rate >5%

# Configure in monitoring dashboard
```

---

## Troubleshooting

### Database Connection Issues

```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1;"

# Check Neon compute status (should be "Active", not "Idle")
neon projects list

# If suspended, disable auto-suspend in dashboard
```

### Redis Connection Issues

```bash
# Test Redis
redis-cli -u $REDIS_URL PING

# Should return: PONG
```

### Directus Schema Not Showing

```bash
# Verify database user has correct permissions
psql $DATABASE_URL -c "\dp articles"

# Should show directus_user has SELECT, INSERT, UPDATE, DELETE

# Restart Directus service in Railway
railway restart
```

### Cost Overruns

```bash
# Check if circuit breaker is enabled
railway variables get ENABLE_COST_CIRCUIT_BREAKER

# If articles rejecting with cost errors, increase cap
railway variables set PER_JOB_COST_CAP="1.00"
```

---

## Success Checklist

- [ ] Neon database created (Launch tier, always-on)
- [ ] Upstash Redis created
- [ ] Backend deployed to Railway
- [ ] Directus deployed to Railway
- [ ] 3 Astro sites deployed to Vercel
- [ ] DNS configured for all 3 domains
- [ ] Test article generated successfully
- [ ] Article visible in Directus
- [ ] Article published on frontend
- [ ] Monitoring and alerts configured
- [ ] Cost tracking working

---

## Next Steps

1. **Generate first 30 articles** (10 per site)
2. **Monitor performance** for 48 hours
3. **Tune cache similarity threshold** based on hit rate
4. **Adjust cost caps** based on actual usage
5. **Scale workers** if queue depth >50

---

**Deployment Complete!** 🚀

For ongoing operations, see:
- [Operational Runbooks](docs/runbooks/)
- [Schema Governance](docs/schema-governance.md)
- [Cost Optimization](docs/cost-optimization.md)
