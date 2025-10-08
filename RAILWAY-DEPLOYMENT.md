# Railway Deployment Guide - Quest Platform

## Quick Deploy (5 minutes)

### 1. Backend (FastAPI + Worker)

**Via Railway Dashboard:**
1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select `Londondannyboy/quest-platform`
4. Choose `backend` as root directory
5. Railway auto-detects Python + Procfile

**Environment Variables (Required):**
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
ENABLE_BATCH_API=false
```

### 2. Directus (CMS)

**Add as second service in same project:**
1. Railway Dashboard → "New Service"
2. Select "Docker Image"
3. Image: `directus/directus:latest`
4. Environment variables (same as backend + Directus-specific)

**Directus Environment Variables:**
```bash
# Database (same Neon)
DB_CLIENT=postgres
DB_HOST=<your-neon-host>
DB_PORT=5432
DB_DATABASE=neondb
DB_USER=<your-db-user>
DB_PASSWORD=<your-db-password>
DB_SSL=true

# Admin
ADMIN_EMAIL=<your-email>
ADMIN_PASSWORD=<strong-password>

# Security (generate with: openssl rand -base64 32)
KEY=<generated-key>
SECRET=<generated-secret>

# API
PUBLIC_URL=${{RAILWAY_PUBLIC_DOMAIN}}
GRAPHQL_ENABLED=true
REST_ENABLED=true
CACHE_ENABLED=false

# Cloudinary (same as backend)
STORAGE_LOCATIONS=cloudinary
STORAGE_CLOUDINARY_DRIVER=cloudinary
STORAGE_CLOUDINARY_CLOUD_NAME=<your-cloud-name>
STORAGE_CLOUDINARY_API_KEY=<your-api-key>
STORAGE_CLOUDINARY_API_SECRET=<your-api-secret>
```

### 3. Test Deployment

```bash
# Test backend
curl https://your-railway-domain.up.railway.app/api/health

# Test Directus
open https://your-directus-domain.up.railway.app

# Generate test article
curl -X POST https://your-railway-domain.up.railway.app/api/articles/generate \
  -H "Content-Type: application/json" \
  -d '{"topic":"Test Article","target_site":"relocation"}'
```

---

## Deployment Checklist

- [ ] Backend deployed to Railway
- [ ] Directus deployed to Railway
- [ ] Environment variables configured
- [ ] Health check passing
- [ ] Test article generated
- [ ] Directus accessible
- [ ] Collections visible in Directus

---

## Next Steps

After Railway deployment:
1. Create Astro frontend (you're doing this manually)
2. Deploy Astro to Vercel
3. Connect Astro to Directus GraphQL
4. Test end-to-end article publishing

---

## Estimated Costs

- **Railway:** ~$30/month (backend + Directus + worker)
- **Neon:** $50/month (already provisioned)
- **Total:** $80/month infrastructure

**Note:** No Railway CLI installation required - deploy via GitHub integration!
