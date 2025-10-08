# Incident Response Runbook

**Quest Platform v2.2 - Incident Response Procedures**
**Last Updated:** October 8, 2025
**Owner:** Platform Engineering Team

---

## 🚨 Quick Reference

### Emergency Contacts

```yaml
On-Call Engineer:
  Primary: Check PagerDuty/OpsGenie schedule
  Secondary: Check PagerDuty/OpsGenie schedule
  Escalation: Engineering Manager

Communication Channels:
  Slack: #quest-incidents (critical alerts)
  Slack: #quest-alerts (warnings)
  Email: engineering@quest.com
  PagerDuty: https://quest.pagerduty.com

Status Page:
  URL: https://status.quest.com
  Update: Post all P0/P1 incidents
```

---

## 📋 Incident Response Process

### Step 1: Detect (0-5 minutes)

**Detection Sources:**
- Automated monitoring alerts (Vercel, Railway, Neon, Upstash)
- User reports (support@quest.com, GitHub issues)
- Internal discovery (team member notices issue)
- External monitoring (uptime services)

**Initial Actions:**
1. Acknowledge the alert immediately
2. Check status page for existing incidents
3. Verify issue is real (not false positive)
4. Determine severity level (P0-P3)

---

### Step 2: Respond (5-15 minutes)

**Communication:**
1. Post in #quest-incidents Slack channel
2. Update status page if P0/P1
3. Notify on-call engineer if not already aware
4. Start incident document (Google Doc or Notion)

**Triage Checklist:**
- [ ] What is broken? (API, frontend, workers, database)
- [ ] How many users affected? (1, 10, 100, all)
- [ ] When did it start? (timestamp)
- [ ] Any recent changes? (deployments, config, data)
- [ ] Severity level? (P0, P1, P2, P3)

---

### Step 3: Mitigate (15-60 minutes)

**Immediate Actions (choose appropriate):**

#### Option A: Rollback Deployment
```bash
# If issue started after recent deployment
cd ~/quest-platform
git log -5  # Identify last known good commit
git revert HEAD  # or git reset --hard <good-commit>
vercel --prod  # Redeploy
railway up  # Redeploy backend
```

#### Option B: Scale Resources
```bash
# If performance degradation
# Railway: Increase worker concurrency
# Neon: Check connection pool, consider read replicas
# Vercel: Already auto-scaled
```

#### Option C: Circuit Breaker
```bash
# If cost runaway
# Set DAILY_COST_CAP to lower value
# Pause article generation temporarily
curl -X POST https://api.quest.com/api/admin/pause-generation
```

#### Option D: Database Issues
```sql
-- Kill long-running queries
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'active'
  AND query_start < NOW() - INTERVAL '5 minutes'
  AND query NOT LIKE '%pg_stat_activity%';

-- Check connections
SELECT count(*) FROM pg_stat_activity;
```

---

### Step 4: Monitor (During Incident)

**Key Metrics to Watch:**

```bash
# API Health
watch -n 5 "curl -s https://api.quest.com/health | jq"

# Queue Depth
watch -n 5 "redis-cli -u $REDIS_URL LLEN bull:articles:wait"

# Database Connections
watch -n 10 "psql $DATABASE_URL -c 'SELECT count(*) FROM pg_stat_activity;'"

# Error Rates
# Check Sentry/Datadog dashboard
```

**Update Frequency:**
- P0: Every 15 minutes
- P1: Every 30 minutes
- P2: Every 2 hours

---

### Step 5: Resolve (When Fixed)

**Verification Checklist:**
- [ ] All SLOs back to green
- [ ] No error spikes in last 15 minutes
- [ ] User-facing functionality working
- [ ] Queue depth normalized
- [ ] Database performance normal

**Communication:**
1. Post resolution in #quest-incidents
2. Update status page: "All systems operational"
3. Thank team members involved
4. Schedule post-mortem meeting (within 48 hours)

---

### Step 6: Post-Mortem (Within 48 hours)

**Required Attendees:**
- Incident responder(s)
- Engineering manager
- Product owner (if user-facing)

**Post-Mortem Template:**

```markdown
# Incident Post-Mortem: [INCIDENT-YYYY-MM-DD]

## Summary
- **Date**: 2025-10-08
- **Duration**: 45 minutes
- **Severity**: P1
- **Impact**: 15% of API requests failing
- **Root Cause**: Database connection pool exhaustion

## Timeline
- 10:00 AM: Alert triggered (API 5xx errors)
- 10:05 AM: On-call engineer acknowledged
- 10:15 AM: Root cause identified (connection pool)
- 10:25 AM: Mitigation applied (increased pool size)
- 10:45 AM: Incident resolved

## Root Cause
Database connection pool set to 20 connections, but traffic spike caused 35+ concurrent requests.

## Impact
- API error rate: 15% for 30 minutes
- Estimated affected users: ~50
- Lost article generations: 3
- Revenue impact: Minimal ($0)

## Action Items
- [ ] Increase connection pool to 50 (@engineer, by 2025-10-10)
- [ ] Add connection pool utilization alert (@engineer, by 2025-10-10)
- [ ] Load test connection pool limits (@engineer, by 2025-10-15)
- [ ] Document connection pool tuning (@tech-writer, by 2025-10-15)

## Lessons Learned
- **What went well**: Fast detection, clear communication
- **What needs improvement**: Connection pool not monitored
- **Preventive measures**: Add alerts before exhaustion (>80%)
```

---

## 🔥 Common Incidents & Solutions

### Incident Type 1: API Unavailable (P0)

**Symptoms:**
- Health check returns 500 or timeouts
- Vercel/Railway shows service down
- All requests failing

**Diagnosis:**
```bash
# Check service status
curl -I https://api.quest.com/health

# Check Railway logs
railway logs -s quest-api-gateway

# Check database connectivity
psql $DATABASE_URL -c "SELECT 1;"
```

**Solutions:**
1. **Database down**: Check Neon status, restart connection pool
2. **Railway service crashed**: Check logs, restart service, rollback if needed
3. **Environment variables**: Verify all secrets are set correctly
4. **Network issue**: Check external status pages (Neon, Railway, Vercel)

**Prevention:**
- Multi-region deployment (future)
- Database replica for failover (future)
- Health check monitoring with auto-restart

---

### Incident Type 2: Slow Page Loads (P1)

**Symptoms:**
- Vercel Analytics shows p95 >5s
- Users report slow page loads
- Lighthouse scores dropping

**Diagnosis:**
```bash
# Run Lighthouse audit
lighthouse https://relocation.quest --view

# Check Cloudinary CDN
curl -I https://res.cloudinary.com/[cloud]/image/[id]

# Check GraphQL API latency
time curl -X POST https://directus.quest.com/graphql \
  -d '{"query":"{ articles { id title } }"}'
```

**Solutions:**
1. **Large images**: Compress, optimize, use WebP format
2. **Slow API**: Check database query performance, add indexes
3. **CDN issue**: Check Cloudinary status, consider cache refresh
4. **JavaScript bloat**: Audit bundle size, lazy load components

**Prevention:**
- Automated Lighthouse CI checks
- Image optimization pipeline
- Regular performance audits

---

### Incident Type 3: Queue Backed Up (P1)

**Symptoms:**
- Queue depth >100 jobs
- Article generation taking hours
- Users reporting delays

**Diagnosis:**
```bash
# Check queue depth
redis-cli -u $REDIS_URL LLEN bull:articles:wait

# Check worker status
curl https://api.quest.com/api/workers/status

# Check worker logs
railway logs -s quest-workers
```

**Solutions:**
1. **Workers crashed**: Restart worker service
2. **API rate limits**: Check AI API quotas (Perplexity, Claude)
3. **Slow jobs**: Identify stuck jobs, kill and retry
4. **Insufficient workers**: Increase concurrency temporarily

**Prevention:**
- Worker auto-restart on crash
- Job timeout enforcement (max 5 minutes)
- Queue depth alerts

---

### Incident Type 4: Cost Runaway (P0)

**Symptoms:**
- Daily cost >$50 (vs $30 cap)
- Circuit breaker triggered
- Excessive API calls

**Diagnosis:**
```bash
# Check daily costs
curl https://api.quest.com/api/metrics/costs/daily

# Check API usage breakdown
curl https://api.quest.com/api/metrics/costs/breakdown

# Review recent job history
redis-cli -u $REDIS_URL LRANGE bull:articles:completed 0 100
```

**Solutions:**
1. **API abuse**: Identify source, block if malicious
2. **Circuit breaker**: Lower cap temporarily (e.g., $20)
3. **Failed retries**: Stop retrying failed jobs
4. **Cache bypass**: Fix cache logic to prevent unnecessary API calls

**Prevention:**
- Strict per-job cost limits
- Rate limiting on job submission
- Monitoring alerts at 80% daily cap

---

### Incident Type 5: Database Connection Issues (P1)

**Symptoms:**
- "Too many connections" errors
- API timeouts
- Slow queries

**Diagnosis:**
```sql
-- Check current connections
SELECT count(*), state FROM pg_stat_activity GROUP BY state;

-- Check connection pool
SELECT * FROM pg_stat_database WHERE datname = 'neondb';

-- Find blocking queries
SELECT * FROM pg_stat_activity WHERE wait_event_type = 'Lock';
```

**Solutions:**
1. **Pool exhaustion**: Increase pool size, close idle connections
2. **Long transactions**: Kill long-running transactions
3. **Deadlocks**: Identify and fix application logic
4. **Neon compute scale**: Upgrade to higher tier if needed

**Prevention:**
- Connection pool monitoring
- Query timeout enforcement
- Regular vacuum and analyze

---

## 📊 Incident Tracking

### Incident Log

**Location:** Google Sheets or Notion database

**Required Fields:**
- Incident ID (INC-YYYY-MM-DD-XX)
- Date/Time
- Severity (P0-P3)
- Duration
- Root Cause
- Impact (users, revenue, reputation)
- Responder(s)
- Post-Mortem Link

**Monthly Review:**
- MTTR (Mean Time To Resolve)
- MTBF (Mean Time Between Failures)
- Incident trends by type
- Action item completion rate

---

## 🛠️ Tools & Access

### Required Access

```yaml
Production Access:
  - Railway: Admin access to quest-api-gateway, quest-workers, quest-directus
  - Neon: Database admin credentials
  - Vercel: Deployment access to all sites
  - Cloudinary: Admin access
  - GitHub: Write access to main branch

Monitoring Access:
  - Vercel Analytics: Viewer
  - Railway Metrics: Viewer
  - Neon Metrics: Viewer
  - Sentry: Admin (if configured)

Emergency Credentials:
  - Stored in 1Password (team vault)
  - Railway CLI tokens
  - Neon connection strings
  - API admin tokens
```

---

## 📚 Related Documentation

- [SLO Document](./SLO.md) - Service Level Objectives
- [Rollback Procedures](./rollback-procedures.md) - Deployment rollback steps
- [Performance Testing](./performance-testing.md) - Load testing guide
- [Architecture Guide](../ARCHITECTURE.md) - System architecture overview

---

**Document Owner:** Platform Engineering
**Last Review:** October 8, 2025
**Next Review:** November 8, 2025
**Status:** Active ✅

---

## 📞 Emergency Contacts

**Critical Escalation (24/7):**
- Engineering Manager: [phone]
- CTO/CEO: [phone]
- External Support: Railway, Neon (check respective status pages)

**Status Page:**
https://status.quest.com (update within 15 minutes of P0/P1)
