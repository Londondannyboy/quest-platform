# Rollback Procedures

**Quest Platform v2.2 - Deployment Rollback Guide**
**Last Updated:** October 8, 2025
**Owner:** Platform Engineering Team

---

## 🎯 Overview

This runbook provides step-by-step procedures for rolling back deployments across all Quest Platform services when issues are detected in production.

### When to Rollback

**Immediate Rollback (P0/P1):**
- API completely unavailable after deployment
- Data corruption or loss
- Security vulnerability introduced
- Critical feature completely broken
- Performance degradation >50%

**Scheduled Rollback (P2/P3):**
- Minor bugs that can wait for hotfix
- Performance issues affecting <10% of users
- Non-critical features degraded

---

## 🚀 Service Architecture

Quest Platform consists of 4 main deployable services:

```
1. Frontend Sites (Vercel)
   - relocation.quest
   - placement.quest
   - rainmaker.quest

2. API Gateway (Railway)
   - quest-api-gateway service

3. Workers (Railway)
   - quest-workers service

4. Directus CMS (Railway)
   - quest-directus service
```

---

## 📝 Pre-Rollback Checklist

Before rolling back, **always**:

- [ ] Identify which service(s) need rollback
- [ ] Verify last known good deployment (commit SHA)
- [ ] Check if database migrations were run
- [ ] Notify team in #quest-incidents Slack
- [ ] Update status page if P0/P1
- [ ] Document reason for rollback

---

## 🔄 Rollback Procedures by Service

### 1. Rollback Frontend Sites (Vercel)

**Estimated Time:** 2-5 minutes

#### Option A: Vercel Dashboard (Easiest)

```bash
1. Go to https://vercel.com/londondannyboys-projects/quest-platform
2. Click "Deployments" tab
3. Find last known good deployment (green checkmark)
4. Click three dots → "Promote to Production"
5. Confirm promotion
6. Wait 1-2 minutes for deployment
7. Verify: Visit https://relocation.quest
```

#### Option B: Vercel CLI (Faster)

```bash
# List recent deployments
vercel ls quest-platform

# Example output:
# quest-platform-abc123.vercel.app (Production) 5m ago
# quest-platform-def456.vercel.app 1h ago ← Known good
# quest-platform-ghi789.vercel.app 2h ago

# Promote previous deployment
vercel promote quest-platform-def456.vercel.app --prod

# Verify
curl -I https://relocation.quest
```

#### Option C: Git Revert + Redeploy

```bash
# Go to project directory
cd ~/quest-platform/frontend/relocation.quest

# Check recent commits
git log --oneline -5

# Revert to known good commit
git revert HEAD  # Revert last commit
# OR
git reset --hard abc123  # Reset to specific commit

# Push to trigger auto-deploy
git push origin main --force

# Vercel will auto-deploy (check GitHub Actions)
```

**Verification:**
```bash
# Check Vercel deployment status
vercel ls --prod

# Test page load
curl -s https://relocation.quest | grep "<title>"

# Check Lighthouse score
lighthouse https://relocation.quest --only-categories=performance
```

---

### 2. Rollback API Gateway (Railway)

**Estimated Time:** 3-7 minutes

#### Option A: Railway Dashboard

```bash
1. Go to https://railway.app/project/{project_id}
2. Click "quest-api-gateway" service
3. Go to "Deployments" tab
4. Find last successful deployment
5. Click "Rollback to this deployment"
6. Confirm rollback
7. Wait for redeploy (~2-3 minutes)
```

#### Option B: Railway CLI

```bash
# List deployments
railway status -s quest-api-gateway

# Redeploy previous version
railway redeploy -s quest-api-gateway --previous

# Monitor logs
railway logs -s quest-api-gateway
```

#### Option C: Git Revert + Redeploy

```bash
cd ~/quest-platform

# Check recent commits
git log backend/ --oneline -5

# Revert problematic commit
git revert HEAD

# Push to trigger Railway auto-deploy
git push origin main

# Railway will auto-deploy from GitHub
```

**Verification:**
```bash
# Health check
curl https://api.quest.com/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2025-10-08T12:00:00Z"
}

# Check version
curl https://api.quest.com/version

# Monitor error rates
railway logs -s quest-api-gateway | grep ERROR
```

---

### 3. Rollback Workers (Railway)

**Estimated Time:** 3-7 minutes

**Procedure:** Same as API Gateway, but for `quest-workers` service

```bash
# Railway Dashboard rollback
1. Go to Railway dashboard
2. Select "quest-workers" service
3. Deployments tab → Rollback

# Railway CLI rollback
railway redeploy -s quest-workers --previous

# Git revert rollback
cd ~/quest-platform
git revert HEAD  # If worker code changed
git push origin main
```

**Verification:**
```bash
# Check worker status
curl https://api.quest.com/api/workers/status

# Expected response
{
  "status": "running",
  "workers": 5,
  "queue_depth": 12
}

# Check queue processing
redis-cli -u $REDIS_URL LLEN bull:articles:wait

# Monitor worker logs
railway logs -s quest-workers
```

---

### 4. Rollback Directus CMS (Railway)

**Estimated Time:** 5-10 minutes

**⚠️ CAUTION:** Directus rollback may affect editor workflows

```bash
# Railway Dashboard rollback
1. Go to Railway dashboard
2. Select "quest-directus" service
3. Deployments tab → Rollback

# Railway CLI rollback
railway redeploy -s quest-directus --previous

# Git revert (if configuration changed)
cd ~/quest-platform/directus
git revert HEAD
git push origin main
```

**Verification:**
```bash
# Health check
curl https://directus.quest.com/server/health

# Login test
curl -X POST https://directus.quest.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@quest.com","password":"***"}'

# Check GraphQL API
curl https://directus.quest.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ articles { id } }"}'
```

---

## 🗄️ Database Rollback (High Risk)

### When to Rollback Database

**⚠️ ONLY in these scenarios:**
- Migration caused data corruption
- Schema change broke application
- Performance catastrophically degraded

### Neon Branch Strategy (Recommended)

Neon supports database branching for safe rollback:

```bash
# Create branch before risky migration
neon branches create --name pre-migration-backup

# If migration fails, switch to branch
neon branches switch pre-migration-backup

# Update DATABASE_URL to point to branch
railway variables set DATABASE_URL=postgresql://...branch...

# Redeploy services
railway redeploy -s quest-api-gateway
railway redeploy -s quest-workers
```

### Manual Migration Rollback (Last Resort)

```bash
# Connect to database
psql $DATABASE_URL

# List recent migrations
SELECT * FROM schema_migrations ORDER BY version DESC LIMIT 5;

# Rollback migration (if down migration exists)
# Example: rolling back migration 003
\i migrations/003_add_reading_time_down.sql

# Verify schema
\d articles

# Test application
curl https://api.quest.com/health
```

**⚠️ Database Rollback Risks:**
- Data loss if schema incompatible
- Downtime during rollback
- Potential for split-brain if services not restarted

**Always:**
1. Backup database before rollback
2. Test in staging first
3. Coordinate with entire team
4. Document all steps

---

## 🔍 Post-Rollback Verification

### Complete Checklist

After any rollback, **verify all systems**:

#### Frontend Verification
```bash
# Check all sites load
curl -I https://relocation.quest
curl -I https://placement.quest
curl -I https://rainmaker.quest

# Run Lighthouse audit
lighthouse https://relocation.quest --view

# Check recent article pages
curl https://relocation.quest/portugal-nomad-visa
```

#### API Verification
```bash
# Health check
curl https://api.quest.com/health

# Generate test article (staging only)
curl -X POST https://api.quest.com/api/articles/generate \
  -H "Content-Type: application/json" \
  -d '{"topic":"test rollback","target_site":"relocation"}'

# Check metrics
curl https://api.quest.com/api/metrics/summary
```

#### Workers Verification
```bash
# Worker status
curl https://api.quest.com/api/workers/status

# Queue depth (should be processing)
redis-cli -u $REDIS_URL LLEN bull:articles:wait

# Recent job completions
redis-cli -u $REDIS_URL LRANGE bull:articles:completed 0 5
```

#### Database Verification
```sql
-- Connection test
SELECT 1;

-- Check recent data
SELECT id, title, created_at
FROM articles
ORDER BY created_at DESC
LIMIT 5;

-- Check query performance
EXPLAIN ANALYZE SELECT * FROM articles WHERE status = 'published' LIMIT 10;
```

---

## 📊 Rollback Decision Matrix

| Issue Type | Affected Users | Rollback? | Timeline |
|------------|----------------|-----------|----------|
| API completely down | 100% | ✅ Immediate | <5 min |
| Critical feature broken | 100% | ✅ Immediate | <10 min |
| Security vulnerability | All | ✅ Immediate | <5 min |
| Performance degraded >50% | >50% | ✅ Immediate | <10 min |
| Minor bug | <10% | ❌ Hotfix instead | Next sprint |
| Performance degraded <20% | <20% | ❌ Optimize instead | Next sprint |
| UI glitch | <5% | ❌ Hotfix instead | 24 hours |

---

## 🚨 Emergency Rollback (All Services)

If catastrophic failure across all services:

```bash
# 1. Rollback all Railway services
railway redeploy -s quest-api-gateway --previous
railway redeploy -s quest-workers --previous
railway redeploy -s quest-directus --previous

# 2. Rollback Vercel (via dashboard, fastest)
# Visit Vercel dashboard → Promote last good deployment

# 3. Verify all services
./scripts/verify-deployment.sh

# 4. Notify team
# Post in #quest-incidents with rollback status

# 5. Update status page
# "We experienced an issue and rolled back to stable version"
```

**Estimated Total Time:** 10-15 minutes

---

## 📚 Related Documentation

- [Incident Response](./incident-response.md) - When and how to respond to incidents
- [SLO Document](./SLO.md) - Service Level Objectives
- [Deployment Guide](../../DEPLOY_TO_GITHUB.md) - Standard deployment process
- [Architecture Guide](../ARCHITECTURE.md) - System architecture

---

## 📝 Rollback Log Template

**Create incident document for each rollback:**

```markdown
# Rollback: [Service Name] - [Date]

## Rollback Decision
- **Date/Time**: 2025-10-08 14:30 UTC
- **Service**: quest-api-gateway
- **Reason**: API returning 500 errors after v2.3.0 deploy
- **Severity**: P0 (API completely unavailable)
- **Decision Maker**: [Name]

## Rollback Execution
- **Previous Version**: v2.2.0 (commit abc123)
- **Rollback Method**: Railway CLI redeploy
- **Start Time**: 14:35 UTC
- **Completion Time**: 14:42 UTC
- **Duration**: 7 minutes

## Verification Results
- [x] Health check passing
- [x] Error rate <0.1%
- [x] All services connected
- [x] Recent article generation successful

## Post-Rollback Actions
- [ ] Schedule post-mortem (2025-10-09 10:00 AM)
- [ ] Investigate root cause (@engineer)
- [ ] Fix issue in develop branch (@engineer)
- [ ] Test fix in staging (@qa)
- [ ] Plan re-deployment (@manager)

## Lessons Learned
- What went wrong: Database connection pool config invalid in v2.3.0
- Prevention: Add integration test for DB connection pool
```

---

**Document Owner:** Platform Engineering
**Last Review:** October 8, 2025
**Next Review:** November 8, 2025
**Status:** Active ✅
