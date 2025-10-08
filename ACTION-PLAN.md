# Quest Platform - Action Plan to Go Live
**Goal:** Get relocation.quest live with great content TODAY

---

## 🎯 THE PLAN

### **Current Status:**
- ✅ Code is ready (backend + frontend structure exists)
- ✅ MCPs are working (Context7, Neon, Taskmaster, GitHub)
- ❌ No .env file (need API keys)
- ❌ Nothing deployed (Railway, Vercel)
- ❌ relocation.quest is down (404)

### **What We Need from YOU:**
1. Neon database connection string
2. API keys (Anthropic, Perplexity, OpenAI, Cloudinary)
3. Railway/Vercel account access

---

## 📋 STEP-BY-STEP PLAN

### **STEP 1: Get Credentials (YOU - 10 minutes)**

**Neon Database:**
```
1. Go to: https://console.neon.tech/
2. Find: quest-platform database (or create if doesn't exist)
3. Copy: Connection string
4. Format: postgresql://user:password@ep-xxx.neon.tech:5432/neondb?sslmode=require
```

**Anthropic (Claude):**
```
1. Go to: https://console.anthropic.com/
2. Copy: API key (starts with sk-ant-)
```

**Perplexity:**
```
1. Go to: https://www.perplexity.ai/settings/api
2. Copy: API key (starts with pplx-)
```

**OpenAI:**
```
1. Go to: https://platform.openai.com/api-keys
2. Copy: API key (starts with sk-)
```

**Cloudinary:**
```
1. Go to: https://console.cloudinary.com/
2. Copy: Cloud name, API key, API secret
```

**Once you have these, paste them here or tell me where they're stored!**

---

### **STEP 2: I Create .env File (ME - 2 minutes)**

I'll create `/Users/dankeegan/quest-platform/backend/.env` with all your credentials.

---

### **STEP 3: Test Locally (ME - 10 minutes)**

```bash
# Install dependencies
cd /Users/dankeegan/quest-platform/backend
pip install -r requirements.txt

# Start FastAPI
python -m app.main

# Test health check
curl http://localhost:8000/health
```

**Expected:** `{"status": "healthy"}`

---

### **STEP 4: Deploy to Railway (ME - 30 minutes)**

**Deploy Services:**
1. FastAPI backend (port 8000)
2. Directus CMS (port 8055)
3. Redis queue (port 6379)

**Configure Environment:**
- Add all API keys
- Set production URLs
- Enable monitoring

**Verify:**
- FastAPI: `https://quest-backend.up.railway.app/health`
- Directus: `https://quest-directus.up.railway.app`

---

### **STEP 5: Setup Directus (ME - 20 minutes)**

**Configure CMS:**
1. Access admin UI
2. Connect to Neon database
3. Verify article tables appear
4. Create admin user
5. Enable GraphQL API

**Test:**
```graphql
query {
  articles {
    id
    title
    slug
  }
}
```

---

### **STEP 6: Deploy relocation.quest to Vercel (ME - 15 minutes)**

**Deploy Frontend:**
1. Connect to Vercel
2. Configure environment variables:
   - `DIRECTUS_URL`: Railway Directus URL
   - `DIRECTUS_TOKEN`: Admin token
3. Deploy site
4. Verify: https://relocation.quest

**Expected:** Site is live (no 404)

---

### **STEP 7: Generate First Test Article (ME - 5 minutes)**

**Via API:**
```bash
curl -X POST https://quest-backend.up.railway.app/api/articles/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Best Cities for Digital Nomads in Portugal 2025",
    "target_site": "relocation",
    "target_audience": "remote_workers",
    "tone": "professional"
  }'
```

**Expected:** Job ID returned, article generates in 2-3 minutes

---

### **STEP 8: Publish to relocation.quest (ME - 5 minutes)**

**In Directus:**
1. Find the generated article
2. Review content
3. Click "Publish"

**Verify:**
- Article appears on https://relocation.quest/articles/best-cities-portugal
- Images load correctly
- SEO metadata correct
- Page loads fast

---

### **STEP 9: Generate 5 More Articles (ME - 30 minutes)**

**Topics for relocation.quest:**
1. "Complete Guide to Moving to Portugal as a Digital Nomad"
2. "Cost of Living in Lisbon vs Porto: 2025 Comparison"
3. "How to Get a Portugal Digital Nomad Visa in 2025"
4. "Best Neighborhoods in Lisbon for Remote Workers"
5. "Health Insurance for Expats in Portugal: Complete Guide"

**All articles:**
- 2000-3000 words
- SEO optimized
- High-quality images
- Ready to publish

---

## ⏱️ TIMELINE

| Time | Task | Owner |
|------|------|-------|
| **Now** | Gather credentials | YOU |
| **+10 min** | Create .env | ME |
| **+20 min** | Test locally | ME |
| **+50 min** | Deploy Railway | ME |
| **+1h 10m** | Setup Directus | ME |
| **+1h 30m** | Deploy Vercel | ME |
| **+1h 45m** | First article | ME |
| **+2h 15m** | 5 more articles | ME |
| **+2h 30m** | 🎉 LIVE! | -- |

**Total:** ~2.5 hours from when you provide credentials

---

## 🚨 WHAT CAN GO WRONG

### **If Neon Database Doesn't Exist:**
**Solution:** I'll create it via Neon MCP or web console
**Time:** +15 minutes

### **If API Keys Are Invalid:**
**Solution:** You regenerate them
**Time:** +10 minutes per key

### **If Railway Deployment Fails:**
**Solution:** Debug logs, fix configuration
**Time:** +30 minutes worst case

### **If Vercel Build Fails:**
**Solution:** Fix frontend code, redeploy
**Time:** +20 minutes

**Bottom Line:** Even with issues, we can be live in 3-4 hours!

---

## ✅ SUCCESS CRITERIA

**We're DONE when:**
- [ ] relocation.quest is live (no 404)
- [ ] Health check returns 200
- [ ] Directus admin UI accessible
- [ ] 6 articles published on relocation.quest
- [ ] Images load correctly
- [ ] SEO metadata present
- [ ] Page speed is good (LCP < 2s)
- [ ] Google can crawl the site

---

## 📞 NEXT STEPS

**Right Now - Tell Me:**

1. **Do you have these credentials ready?**
   - Neon connection string?
   - Anthropic API key?
   - Perplexity API key?
   - OpenAI API key?
   - Cloudinary credentials?

2. **Do you have Railway access?**
   - Can you create a new project?
   - Or should I guide you through signup?

3. **Do you have Vercel access?**
   - Can you import a GitHub repo?
   - Or should I guide you through setup?

4. **What's your priority?**
   - Speed (get something live fast, polish later)?
   - Quality (test everything thoroughly first)?
   - Both (reasonable testing, then go live)?

**Once you answer, I'll start immediately!** 🚀
