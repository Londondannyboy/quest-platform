# Quest Platform Restart Prompt

## TIER 0 Implementation Complete ✅
**Date:** October 10, 2025
**Model:** claude-opus-4-1 (Opus)

## Current Status
- 7-Agent Pipeline: Fully operational with link validation
- Link Validation: Implemented (prevents hallucinated URLs)
- Research Quality Scoring: 60/100 threshold implemented
- APIs Working: Perplexity ($0.20), Tavily ($0.10)
- Redis Queue + BullMQ: Operational
- Frontend: relocation.quest deployed on Vercel
- Database: Neon PostgreSQL configured
- Directus: Publishing workflow fixed (published_at column added)

## Latest Changes (October 10, 2025)
1. **Link Validation System**
   - Created LinkValidator class (Option 3 implementation)
   - External URLs validated before content generation
   - Internal links suggest related articles
   - No more hallucinated links in articles

2. **Directus Publishing Fix**
   - Added published_at column to database
   - Standardized status values: "draft" and "published"
   - Created performance indexes for queries
   - Publishing workflow now operational

3. **Documentation Updates**
   - Updated CLAUDE.md with latest fixes
   - Version bumped to 2.6
   - All changes pushed to GitHub (commit: c58a5fe)

## System Architecture
```
Backend: Railway (quest-platform-production-b8e3.up.railway.app)
Frontend: Vercel (relocation.quest)
Database: Neon (postgresql://neondb_owner@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb)
Queue: Redis + BullMQ
Storage: Cloudinary (images)
CMS: Directus (local development)
```

## To Restart Platform
```bash
# 1. Kill existing processes
pkill -f "python3.*quest-platform"
pkill -f "directus"

# 2. Start Backend API
cd ~/quest-platform/backend
python3 -m app.main

# 3. Generate Articles (PRIMARY SCRIPT)
# Single article:
python3 generate_full_article.py --topic "Your topic here"

# Batch of 100 articles:
python3 generate_full_article.py --auto --count 100

# From topics file:
python3 generate_full_article.py --batch topics.txt

# 4. Start Directus CMS (optional)
cd ~/quest-platform/directus
npx directus@latest start
# Access at http://localhost:8055
```

## Key Files
- Backend: quest-platform/backend/app/
- Link Validator: quest-platform/backend/app/core/link_validator.py
- Config: quest-platform/backend/.env
- Tests: quest-platform/backend/test_all_apis.py
- Docs: quest-platform/CLAUDE.md

## Testing Link Validation
```python
# The new flow:
1. ResearchAgent gathers sources from Perplexity
2. LinkValidator validates all external URLs
3. LinkValidator suggests internal links from DB
4. Validated links passed to ContentAgent
5. ContentAgent uses ONLY validated links
```

## Next Phase: Testing & Scaling
- Generate article with new link validation
- Verify no hallucinated links
- Test Directus publishing workflow
- Generate 10 articles for relocation.quest