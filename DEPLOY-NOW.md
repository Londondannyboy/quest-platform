# Quest Platform - Deploy to Production NOW

**Status:** Ready for deployment (all bugs fixed)
**Time Required:** 15 minutes
**Date:** December 8, 2024

---

## ✅ Pre-Flight Check

- [x] Backend code tested locally
- [x] Database schema fixed (job_status table)
- [x] JSON parsing bugs fixed (content + editor agents)
- [x] Article generation working end-to-end
- [x] All deployment files ready (Procfile, railway.json, worker.py)

---

## 🚀 Deployment Steps

### Step 1: Deploy Backend to Railway (5 minutes)

1. **Go to Railway Dashboard**
   - Visit: https://railway.app/new
   - Click "Deploy from GitHub repo"

2. **Connect Repository**
   - Select `Londondannyboy/quest-platform`
   - Set **Root Directory:** `backend`
   - Railway will auto-detect Python + Procfile

3. **Configure Environment Variables**

```bash
# Database
NEON_CONNECTION_STRING=postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require

# Redis
UPSTASH_REDIS_URL=redis://default:AcLLAAIjcDE5ZTg2MTg0ODBmNGY0ZDRkYTEwZjU3ZDFmNGI0YWNhZXAxMA@humorous-gibbon-10467.upstash.io:6379

# AI APIs
PERPLEXITY_API_KEY=<your-perplexity-key>
ANTHROPIC_API_KEY=<your-anthropic-key>
OPENAI_API_KEY=<your-openai-key>
REPLICATE_API_TOKEN=<your-replicate-token>

# Cloudinary
CLOUDINARY_CLOUD_NAME=<your-cloud-name>
CLOUDINARY_API_KEY=<your-api-key>
CLOUDINARY_API_SECRET=<your-api-secret>

# App Config
ENVIRONMENT=production
PORT=8000
```

4. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes for build
   - Get your Railway domain (e.g., `quest-backend-production.up.railway.app`)

5. **Test Health Check**
```bash
curl https://your-railway-domain.up.railway.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-12-08T17:15:00Z",
  "database": "connected",
  "redis": "connected"
}
```

---

### Step 2: Deploy Directus CMS (5 minutes)

1. **Add New Service in Railway**
   - Same project, click "+ New Service"
   - Select "Docker Image"
   - Image: `directus/directus:latest`

2. **Configure Environment Variables**

```bash
# Database (same Neon instance)
DB_CLIENT=postgres
DB_HOST=ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech
DB_PORT=5432
DB_DATABASE=neondb
DB_USER=neondb_owner
DB_PASSWORD=npg_Q9VMTIX2eHws
DB_SSL=true

# Admin
ADMIN_EMAIL=keegan.dan@gmail.com
ADMIN_PASSWORD=QuestAdmin2024!

# Security (generate with: openssl rand -base64 32)
KEY=VyJT8QnMlR6Dx2ZpK3Nh4Aw9Gu5Cv7Bm
SECRET=Pz0Xl8Ty4Qw6Rs3Nv2Mk9Ju7Ht5Gf1Cd

# API
PUBLIC_URL=${{RAILWAY_PUBLIC_DOMAIN}}
GRAPHQL_ENABLED=true
REST_ENABLED=true
CACHE_ENABLED=false

# Cloudinary (same as backend)
STORAGE_LOCATIONS=cloudinary
STORAGE_CLOUDINARY_DRIVER=cloudinary
STORAGE_CLOUDINARY_CLOUD_NAME=dxm7w6nqj
STORAGE_CLOUDINARY_API_KEY=726914825374812
STORAGE_CLOUDINARY_API_SECRET=XHrx0sB-c8bBRhB3l3n3n3n3n3n3n
```

3. **Deploy**
   - Railway will pull image and start
   - Get Directus domain (e.g., `quest-directus.up.railway.app`)

4. **Test Directus**
```bash
open https://your-directus-domain.up.railway.app
```

Login with:
- Email: `keegan.dan@gmail.com`
- Password: `QuestAdmin2024!`

---

### Step 3: Test Production Article Generation (5 minutes)

1. **Generate Test Article**
```bash
curl -X POST https://your-railway-domain.up.railway.app/api/articles/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Best Cities for Digital Nomads in Spain 2025",
    "target_site": "relocation"
  }'
```

Expected response:
```json
{
  "job_id": "uuid-here",
  "status": "queued",
  "poll_url": "/api/jobs/uuid-here"
}
```

2. **Check Job Status**
```bash
# Wait 2-3 minutes, then:
curl https://your-railway-domain.up.railway.app/api/jobs/{job_id}
```

Expected response (when complete):
```json
{
  "status": "completed",
  "article_id": "uuid-here",
  "progress": 100
}
```

3. **View in Directus**
   - Go to Directus dashboard
   - Navigate to "Articles" collection
   - See your new article

---

## 📊 Production Checklist

- [ ] Backend deployed to Railway
- [ ] Backend health check passing
- [ ] Directus deployed to Railway
- [ ] Directus login working
- [ ] Test article generated successfully
- [ ] Article visible in Directus
- [ ] All 4 agents working (Research → Content → Editor → Image)

---

## 🔗 Production URLs

After deployment, save these URLs:

```
Backend API: https://your-railway-domain.up.railway.app
Directus CMS: https://your-directus-domain.up.railway.app
GitHub Repo: https://github.com/Londondannyboy/quest-platform
```

---

## 🐛 Troubleshooting

### Backend Not Starting
- Check Railway logs for errors
- Verify all environment variables are set
- Check database connection string

### Directus Not Connecting
- Verify DB credentials match Neon
- Check KEY and SECRET are generated
- Ensure PUBLIC_URL is set to Railway domain

### Article Generation Failing
- Check agent logs in Railway
- Verify API keys are correct
- Check Redis connection

---

## 📈 Next Steps After Deployment

1. **Create Astro Frontend** (Manual - User task)
   - Initialize Astro project for relocation.quest
   - Connect to Directus GraphQL API
   - Deploy to Vercel

2. **Generate Content Pipeline**
   - Generate 10 articles for relocation.quest
   - Generate 10 articles for placement.quest
   - Generate 10 articles for rainmaker.quest

3. **Monitor Costs**
   - Check Railway usage
   - Monitor API costs (Perplexity, Claude)
   - Set up budget alerts

---

## 💰 Monthly Cost Estimate

```
Railway (Backend + Directus): $30/month
Neon Database: $50/month
Vercel (Frontend): $0 (free tier)
AI APIs (1000 articles): ~$350/month

Total: ~$430/month = $0.43 per article
```

---

**Ready to deploy? Let's go! 🚀**
