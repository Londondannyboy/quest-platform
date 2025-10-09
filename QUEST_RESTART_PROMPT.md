# Quest Platform Restart Prompt

## TIER 0 Implementation Complete ✅
**Date:** October 9, 2025
**Model:** claude-opus-4-1 (Opus)

## Current Status
- 7-Agent Pipeline: Fully operational
- Research Quality Scoring: 60/100 threshold implemented
- APIs Working: Perplexity ($0.20), Tavily ($0.10)
- Redis Queue + BullMQ: Operational
- Frontend: relocation.quest deployed on Vercel
- Database: Neon PostgreSQL configured

## System Architecture
```
Backend: Railway (quest-platform-production-b8e3.up.railway.app)
Frontend: Vercel (relocation.quest)
Database: Neon (postgresql://neondb_owner@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb)
Queue: Redis + BullMQ
Storage: Cloudinary (images)
```

## To Restart Platform
```bash
# 1. Start Backend API
cd ~/quest-platform/backend
python3 -m app.main

# 2. Test Article Generation
python3 generate_full_article.py

# 3. Check Directus (optional)
cd ~/quest-platform/directus
npx directus@latest start
```

## Key Files
- Backend: quest-platform/backend/app/
- Config: quest-platform/backend/.env
- Tests: quest-platform/backend/test_all_apis.py

## Next Phase: Human-in-the-Loop
- Directus CMS integration for article review
- Manual video uploads via Mux
- Editorial workflow implementation
