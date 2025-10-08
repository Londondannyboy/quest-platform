# Quest Platform - Environment Variables Guide
**Where to Put Each API Key**

---

## 🎯 THREE DIFFERENT PLACES FOR CREDENTIALS

### **1. BACKEND (.env file) - FastAPI on Railway**
**Location:** `/Users/dankeegan/quest-platform/backend/.env`
**Purpose:** Article generation, AI agents, database access

### **2. VERCEL - Frontend Sites**
**Location:** Vercel Dashboard → Project Settings → Environment Variables
**Purpose:** Frontend database access, image URLs

### **3. RAILWAY - Backend Deployment**
**Location:** Railway Dashboard → Service → Variables
**Purpose:** Same as backend .env, but for production

---

## 📋 COMPLETE ENVIRONMENT VARIABLES BREAKDOWN

### **BACKEND (.env) - All AI & Database Keys**

```bash
# =============================================================================
# DATABASE (Neon PostgreSQL)
# =============================================================================
DATABASE_URL="postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-jolly-sun-a5swy3pz.us-east-2.aws.neon.tech/neondb?sslmode=require"
NEON_CONNECTION_STRING="postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-jolly-sun-a5swy3pz.us-east-2.aws.neon.tech/neondb?sslmode=require"

# =============================================================================
# REDIS (Upstash - Queue System)
# =============================================================================
REDIS_URL="redis://default:ASjjAAIncDI5ZTQ5YTUzOTQ4ZTI0NTYwYTQxOTFmYmZiMmI3ZGY1ZnAyMTA0Njc@humorous-gibbon-10467.upstash.io:6379"
UPSTASH_REDIS_REST_URL="https://humorous-gibbon-10467.upstash.io"
UPSTASH_REDIS_REST_TOKEN="ASjjAAIncDI5ZTQ5YTUzOTQ4ZTI0NTYwYTQxOTFmYmZiMmI3ZGY1ZnAyMTA0Njc"

# =============================================================================
# AI API KEYS (⚠️ YOU NEED TO PROVIDE THESE)
# =============================================================================

# Anthropic Claude (Content + Editor Agents)
ANTHROPIC_API_KEY="[YOU PROVIDE - Get from https://console.anthropic.com/]"
ANTHROPIC_MODEL="claude-sonnet-4-20250514"

# Perplexity (Research Agent)
PERPLEXITY_API_KEY="[YOU PROVIDE - Get from https://www.perplexity.ai/settings/api]"
PERPLEXITY_MODEL="sonar-pro"

# OpenAI (Embeddings for vector cache)
OPENAI_API_KEY="[YOU PROVIDE - Get from https://platform.openai.com/api-keys]"
OPENAI_EMBEDDING_MODEL="text-embedding-3-small"

# Replicate (Image Generation - FLUX)
REPLICATE_API_KEY="[YOU PROVIDE - Get from https://replicate.com/account]"
REPLICATE_MODEL="black-forest-labs/flux-schnell"

# =============================================================================
# CLOUDINARY (Image CDN)
# =============================================================================
CLOUDINARY_CLOUD_NAME="[YOU PROVIDE - From https://console.cloudinary.com/]"
CLOUDINARY_API_KEY="[YOU PROVIDE - From Cloudinary dashboard]"
CLOUDINARY_API_SECRET="[YOU PROVIDE - From Cloudinary dashboard]"

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================
APP_ENV="production"
DEBUG="false"
LOG_LEVEL="INFO"
API_PORT="8000"

# CORS allowed origins (your frontend sites)
CORS_ORIGINS="https://relocation.quest,https://placement.quest,https://rainmaker.quest,http://localhost:4321"

# =============================================================================
# DIRECTUS INTEGRATION
# =============================================================================
DIRECTUS_URL="[WILL BE SET AFTER RAILWAY DEPLOYMENT]"
DIRECTUS_API_TOKEN="[WILL BE GENERATED AFTER DIRECTUS SETUP]"

# =============================================================================
# COST CONTROLS
# =============================================================================
DAILY_COST_CAP="30.00"
PER_JOB_COST_CAP="0.75"
ENABLE_COST_CIRCUIT_BREAKER="true"
```

---

## 🌐 VERCEL ENVIRONMENT VARIABLES (Frontend)

**For:** relocation.quest, placement.quest, rainmaker.quest

### **Method 1: Vercel Dashboard**
Go to: https://vercel.com/dashboard → Your Project → Settings → Environment Variables

### **Method 2: Vercel CLI**
```bash
# Add each variable for production
npx vercel env add NEON_CONNECTION_STRING production
npx vercel env add DIRECTUS_URL production
npx vercel env add DIRECTUS_TOKEN production
```

### **Variables Needed:**

```bash
# Database Connection (for Astro to query articles)
NEON_CONNECTION_STRING="postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-jolly-sun-a5swy3pz.us-east-2.aws.neon.tech/neondb?sslmode=require"

# Directus GraphQL API (after Railway deployment)
DIRECTUS_URL="https://quest-directus.up.railway.app"
DIRECTUS_TOKEN="[GENERATED AFTER DIRECTUS SETUP]"

# Optional: Cloudinary for image optimization
CLOUDINARY_CLOUD_NAME="[SAME AS BACKEND]"
```

---

## 🚂 RAILWAY ENVIRONMENT VARIABLES (Backend Production)

**Location:** Railway Dashboard → quest-platform → Service → Variables

### **Copy ALL backend .env variables to Railway:**
- Same as backend .env file above
- Railway will use these for production deployment
- No local .env file is deployed to Railway

### **Method:**
1. Go to: https://railway.app/dashboard
2. Find your quest-platform project
3. Click on the FastAPI service
4. Go to "Variables" tab
5. Add each variable from the backend .env list above

---

## 🎯 WHAT YOU NEED TO PROVIDE

### **Priority 1: CRITICAL (Can't generate content without)**
```
ANTHROPIC_API_KEY     = "sk-ant-api03-..."     [https://console.anthropic.com/]
PERPLEXITY_API_KEY    = "pplx-..."             [https://www.perplexity.ai/settings/api]
OPENAI_API_KEY        = "sk-..."               [https://platform.openai.com/api-keys]
```

### **Priority 2: HIGH (Image generation)**
```
REPLICATE_API_KEY     = "r8_..."               [https://replicate.com/account]
CLOUDINARY_CLOUD_NAME = "your-cloud-name"      [https://console.cloudinary.com/]
CLOUDINARY_API_KEY    = "123456789012345"      [Cloudinary dashboard]
CLOUDINARY_API_SECRET = "abcdefghijklmnop"     [Cloudinary dashboard]
```

### **Priority 3: LOW (Generated automatically)**
```
DIRECTUS_URL          = [I'll provide after deployment]
DIRECTUS_TOKEN        = [I'll provide after setup]
```

---

## 📝 HOW TO GIVE ME THE KEYS

### **Option 1: Paste Here (Preferred)**
Just paste them in this format:
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
PERPLEXITY_API_KEY=pplx-xxxxx
OPENAI_API_KEY=sk-xxxxx
REPLICATE_API_KEY=r8_xxxxx
CLOUDINARY_CLOUD_NAME=your-name
CLOUDINARY_API_KEY=123456
CLOUDINARY_API_SECRET=abcdef
```

### **Option 2: Tell Me Where They Are**
"They're in my password manager" → I'll wait
"Check the MCP config" → I'll look there
"In another file" → Tell me the path

---

## ✅ WHAT I ALREADY HAVE

These are ready to use:
- ✅ NEON_CONNECTION_STRING
- ✅ REDIS_URL
- ✅ UPSTASH_REDIS_REST_URL
- ✅ UPSTASH_REDIS_REST_TOKEN
- ✅ RAILWAY_TOKEN (for deployment)

---

## 🚀 ONCE YOU PROVIDE KEYS, I WILL:

1. **Create backend/.env** with all keys
2. **Test locally** (FastAPI + Neon connection)
3. **Deploy to Railway** (FastAPI + Directus + Redis)
4. **Setup Directus** and get DIRECTUS_URL + DIRECTUS_TOKEN
5. **Add to Vercel** environment variables
6. **Deploy relocation.quest** to Vercel
7. **Generate first article** to test end-to-end
8. **🎉 YOU'RE LIVE!**

**Timeline:** ~2 hours after you provide the API keys!

---

## 💡 TIP: Where to Find Each Key

| Service | Where to Find Key | Free Tier? |
|---------|------------------|------------|
| **Anthropic** | console.anthropic.com → API Keys | ✅ $5 free credit |
| **Perplexity** | perplexity.ai → Settings → API | ✅ 5 free requests/day |
| **OpenAI** | platform.openai.com → API Keys | ✅ $5 free credit (new accounts) |
| **Replicate** | replicate.com → Account → API Tokens | ✅ Free tier available |
| **Cloudinary** | console.cloudinary.com → Dashboard | ✅ 25GB free storage |

**Ready when you are!** 🎯
