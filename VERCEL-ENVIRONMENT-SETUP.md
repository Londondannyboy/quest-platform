# Vercel Environment Variables Setup Guide

**Why Environment Variables in Vercel?**
- ✅ **Best Practice:** Never commit secrets to git (`.env` is in `.gitignore`)
- ✅ **Security:** Secrets stay on Vercel's secure platform
- ✅ **Multiple Environments:** Different values for production, preview, development
- ✅ **Easy Updates:** Change secrets without redeploying code

---

## 🎯 Projects That Need Environment Variables

Based on your Quest ecosystem, you should have these Vercel projects:
1. **relocation-quest** (relocation.quest)
2. **placement-quest** (placement.quest)
3. **rainmaker-quest** (rainmaker.quest)

---

## 📋 Environment Variables to Add

### **Required for ALL Projects:**

```bash
# Database Connection (for Astro to query articles)
NEON_CONNECTION_STRING="postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Cloudinary (for image optimization)
CLOUDINARY_CLOUD_NAME="dc7btom12"
CLOUDINARY_API_KEY="653994623498835"
CLOUDINARY_API_SECRET="MQQ61lBHOeaZsIopjOPlWX1ITBw"
```

### **After Railway Deployment (Directus):**

```bash
# Directus GraphQL API
DIRECTUS_URL="https://quest-directus.up.railway.app"
DIRECTUS_TOKEN="[GENERATED_AFTER_DIRECTUS_SETUP]"
```

---

## 🖱️ Method 1: Via Vercel Dashboard (Recommended)

### **Step-by-Step:**

1. **Go to Vercel Dashboard:**
   - Visit: https://vercel.com/dashboard
   - Login with your account

2. **For Each Project (relocation-quest, placement-quest, rainmaker-quest):**

   a. **Navigate to Project:**
      - Click on the project name

   b. **Go to Settings:**
      - Click "Settings" tab at the top

   c. **Go to Environment Variables:**
      - Click "Environment Variables" in the left sidebar

   d. **Add Each Variable:**
      - Click "Add New" button
      - **Name:** `NEON_CONNECTION_STRING`
      - **Value:** `postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require`
      - **Environments:** Check all three (Production, Preview, Development)
      - Click "Save"

   e. **Repeat for:**
      - `CLOUDINARY_CLOUD_NAME` = `dc7btom12`
      - `CLOUDINARY_API_KEY` = `653994623498835`
      - `CLOUDINARY_API_SECRET` = `MQQ61lBHOeaZsIopjOPlWX1ITBw`

3. **Redeploy (if projects already deployed):**
   - Go to "Deployments" tab
   - Click "..." menu on the latest deployment
   - Click "Redeploy"
   - This will pick up the new environment variables

---

## 🖥️ Method 2: Via Vercel CLI (Alternative)

If you want to use CLI (requires proper scope access):

```bash
# Set your token
export VERCEL_TOKEN="Kfe6nzU819uPFWE6AZ2I9nBl"

# For each project, cd into the project directory first
cd /path/to/relocation-quest

# Add environment variables
npx vercel env add NEON_CONNECTION_STRING production
# When prompted, paste: postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require

npx vercel env add CLOUDINARY_CLOUD_NAME production
# When prompted, paste: dc7btom12

npx vercel env add CLOUDINARY_API_KEY production
# When prompted, paste: 653994623498835

npx vercel env add CLOUDINARY_API_SECRET production
# When prompted, paste: MQQ61lBHOeaZsIopjOPlWX1ITBw
```

---

## 🔒 Security Best Practices

### **What's in Git (.env files):**
```
backend/.env          ← In .gitignore (NOT committed)
backend/.env.example  ← Template only (safe to commit)
```

### **How It Works:**

1. **Local Development:**
   - You use `/Users/dankeegan/quest-platform/backend/.env`
   - Never committed to git
   - Lives only on your machine

2. **Production (Railway):**
   - Environment variables set in Railway dashboard
   - Or deployed via Railway CLI
   - Railway reads them at runtime

3. **Frontend (Vercel):**
   - Environment variables set in Vercel dashboard
   - Vercel injects them at build time
   - Never in your git repository

---

## ✅ Verification Checklist

After adding environment variables:

### **For relocation.quest:**
- [ ] NEON_CONNECTION_STRING added
- [ ] CLOUDINARY_CLOUD_NAME added
- [ ] CLOUDINARY_API_KEY added
- [ ] CLOUDINARY_API_SECRET added
- [ ] Redeployed (if already deployed)
- [ ] Visit https://relocation.quest to verify it's working

### **For placement.quest:**
- [ ] Same environment variables added
- [ ] Redeployed
- [ ] Visit https://placement.quest to verify

### **For rainmaker.quest:**
- [ ] Same environment variables added
- [ ] Redeployed
- [ ] Visit https://rainmaker.quest to verify

---

## 🆘 If Projects Don't Exist Yet

If you don't have these projects deployed to Vercel yet:

1. **Create Projects:**
   - Go to https://vercel.com/new
   - Import from GitHub:
     - `relocation-quest` repository
     - `placement-quest` repository
     - `rainmaker-quest` repository

2. **Add Environment Variables:**
   - Follow Method 1 above

3. **Deploy:**
   - Vercel will auto-deploy on first import

---

## 🎯 What Happens Next?

After environment variables are set:

1. **Astro Frontend** can query Neon database for articles
2. **Cloudinary** will optimize and serve images
3. **Directus GraphQL** (after Railway deployment) will provide CMS data
4. **No secrets in git** = secure and proper

---

## 📝 After Railway Deployment

Once Directus is deployed to Railway, come back and add:

```bash
DIRECTUS_URL="https://quest-directus.up.railway.app"
DIRECTUS_TOKEN="[token from Directus admin]"
```

To all three Vercel projects.

---

## 💡 Pro Tip: Bulk Update Script

If you want to update all projects at once via CLI:

```bash
#!/bin/bash
# save as: update-vercel-envs.sh

PROJECTS=("relocation-quest" "placement-quest" "rainmaker-quest")

for project in "${PROJECTS[@]}"; do
  echo "Updating $project..."
  cd /path/to/$project

  echo "NEON_CONNECTION_STRING" | npx vercel env add production --yes
  echo "CLOUDINARY_CLOUD_NAME" | npx vercel env add production --yes
  # ... repeat for each variable
done
```

---

**Recommendation:** Use the **Dashboard method (Method 1)** - it's visual, clear, and less error-prone! 🎯
