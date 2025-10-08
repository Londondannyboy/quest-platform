# Service Level Objectives (SLOs)

**Quest Platform v2.2 - Production SLOs**
**Last Updated:** October 8, 2025
**Owner:** Platform Engineering Team

---

## 📊 Overview

This document defines Service Level Objectives (SLOs) for Quest Platform v2.2, monitoring procedures, and escalation paths.

### SLO Philosophy

- **User-Centric**: SLOs reflect actual user experience
- **Achievable**: Set at 99.5% to allow for maintenance and incidents
- **Actionable**: Breaches trigger clear remediation steps
- **Measurable**: All SLOs have automated monitoring

---

## 🎯 Core SLOs

### 1. API Availability

**Objective:** API Gateway must be reachable and respond to health checks

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Uptime** | 99.5% | Monthly basis |
| **Error Rate** | <0.5% | 5xx errors / total requests |
| **Measurement Window** | 30 days rolling | |

**Monitoring:**
```bash
# Health check endpoint
GET https://api.quest.com/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2025-10-08T12:00:00Z",
  "services": {
    "database": "connected",
    "redis": "connected",
    "workers": "running"
  }
}
```

**Alert Thresholds:**
- 🟡 **Warning**: Uptime <99.7% over 7 days
- 🔴 **Critical**: Uptime <99.5% over 7 days
- 🔴 **Critical**: Error rate >1% over 1 hour

**Breach Response:**
1. Page on-call engineer immediately
2. Check [Incident Response Runbook](./incident-response.md)
3. Investigate database/Redis connectivity
4. Review recent deployments
5. Post incident report within 24 hours

---

### 2. Page Load Performance

**Objective:** Content pages must load quickly for end users

| Metric | Target | Measurement |
|--------|--------|-------------|
| **p95 Load Time** | <3 seconds | Lighthouse CI |
| **p99 Load Time** | <5 seconds | Real User Monitoring (RUM) |
| **LCP (Largest Contentful Paint)** | <2.5s | Core Web Vitals |
| **FID (First Input Delay)** | <100ms | Core Web Vitals |
| **CLS (Cumulative Layout Shift)** | <0.1 | Core Web Vitals |

**Monitoring:**
- Vercel Analytics (automatic)
- Lighthouse CI in GitHub Actions
- Plausible Analytics (optional)

**Alert Thresholds:**
- 🟡 **Warning**: p95 >3.5s for 30 minutes
- 🔴 **Critical**: p95 >5s for 15 minutes

**Breach Response:**
1. Check Vercel deployment status
2. Review recent content changes (large images?)
3. Check CDN (Cloudinary) performance
4. Investigate database query performance
5. Consider edge caching improvements

---

### 3. Article Generation Latency

**Objective:** AI pipeline must generate articles within acceptable time

| Metric | Target | Measurement |
|--------|--------|-------------|
| **p50 Generation Time** | <45 seconds | BullMQ job completion |
| **p95 Generation Time** | <60 seconds | BullMQ job completion |
| **p99 Generation Time** | <90 seconds | BullMQ job completion |
| **Queue Depth** | <50 jobs | Redis queue length |

**Monitoring:**
```bash
# Check queue depth
redis-cli -u $REDIS_URL LLEN bull:articles:wait

# Check worker status
curl https://api.quest.com/api/workers/status
```

**Alert Thresholds:**
- 🟡 **Warning**: p95 >75s for 1 hour
- 🔴 **Critical**: p95 >90s for 30 minutes
- 🔴 **Critical**: Queue depth >100 jobs

**Breach Response:**
1. Check worker process status
2. Review AI API latencies (Perplexity, Claude, OpenAI)
3. Check for API rate limiting
4. Scale worker concurrency if needed
5. Review cost circuit breaker status

---

### 4. Database Query Performance

**Objective:** Database queries must be fast and efficient

| Metric | Target | Measurement |
|--------|--------|-------------|
| **p95 Query Time** | <50ms | pg_stat_statements |
| **p99 Query Time** | <100ms | pg_stat_statements |
| **Connection Pool Utilization** | <80% | Neon metrics |
| **Cache Hit Rate** | >80% | PostgreSQL stats |

**Monitoring:**
```sql
-- Slowest queries
SELECT
    query,
    calls,
    mean_exec_time / 1000 as avg_seconds,
    max_exec_time / 1000 as max_seconds
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**Alert Thresholds:**
- 🟡 **Warning**: p95 >75ms for 30 minutes
- 🔴 **Critical**: p95 >100ms for 15 minutes
- 🔴 **Critical**: Connection pool >90% for 5 minutes

**Breach Response:**
1. Identify slow queries with pg_stat_statements
2. Review missing indexes
3. Check for long-running transactions
4. Consider read replicas for heavy reads
5. Review connection pooling configuration

---

### 5. Cost Per Article

**Objective:** Maintain cost efficiency at scale

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Cost Per Article** | <$0.75 | Daily API usage tracking |
| **Daily Cost Cap** | $30.00 | Circuit breaker enforcement |
| **Cache Hit Rate** | >25% | pgvector similarity searches |

**Monitoring:**
```bash
# Check daily costs
curl https://api.quest.com/api/metrics/costs/daily

# Response
{
  "date": "2025-10-08",
  "total_cost": 24.50,
  "articles_generated": 45,
  "cost_per_article": 0.54,
  "cache_hit_rate": 0.31
}
```

**Alert Thresholds:**
- 🟡 **Warning**: Cost per article >$0.65
- 🔴 **Critical**: Cost per article >$0.75
- 🔴 **Critical**: Daily cost >$28 (93% of cap)

**Breach Response:**
1. Review cost breakdown by AI service
2. Check cache effectiveness
3. Investigate API usage anomalies
4. Consider adjusting generation parameters
5. Review circuit breaker configuration

---

### 6. Research Cache Effectiveness

**Objective:** Maximize cost savings through intelligent caching

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Cache Hit Rate** | >25% | Vector similarity matches |
| **Cache TTL** | 30 days | Expiration policy |
| **Similarity Threshold** | <0.30 | pgvector cosine distance |
| **Cost Savings** | >40% | vs. no caching |

**Monitoring:**
```sql
-- Cache performance
SELECT
    COUNT(*) FILTER (WHERE cache_hit = true) * 100.0 / COUNT(*) as hit_rate,
    AVG(similarity_score) as avg_similarity
FROM research_queries
WHERE created_at > NOW() - INTERVAL '7 days';
```

**Alert Thresholds:**
- 🟡 **Warning**: Hit rate <20% for 24 hours
- 🟢 **Optimization**: Hit rate >40% (tune threshold)

**Breach Response:**
1. Review similarity threshold tuning
2. Check embedding quality
3. Analyze query patterns
4. Consider cache prewarming
5. Review TTL policy

---

## 📈 SLO Dashboard

### Recommended Tools

**Primary (Free/Low-Cost):**
- **Vercel Analytics** - Frontend performance (automatic)
- **Railway Metrics** - Backend infrastructure (automatic)
- **Neon Metrics** - Database performance (automatic)
- **Upstash Metrics** - Redis queue depth (automatic)

**Optional (Enhanced Monitoring):**
- **Grafana** - Custom dashboards (self-hosted)
- **Datadog** - APM and logs (free tier available)
- **Sentry** - Error tracking (free tier)
- **Plausible** - Privacy-friendly analytics

### Key Metrics URLs

```yaml
Production Dashboards:
  - Vercel: https://vercel.com/londondannyboys-projects/quest-platform
  - Railway: https://railway.app/project/{project_id}
  - Neon: https://console.neon.tech/app/projects/{project_id}
  - Upstash: https://console.upstash.com/redis/{redis_id}

Health Checks:
  - API Gateway: https://api.quest.com/health
  - Workers: https://api.quest.com/api/workers/status
  - Database: psql $DATABASE_URL -c "SELECT 1;"
```

---

## 🚨 Incident Severity Levels

### P0 - Critical (Page Immediately)
- API completely unavailable
- Data loss or corruption
- Security breach
- Cost runaway (>$50/day)

**Response Time:** 15 minutes
**Escalation:** Immediate to senior engineer

### P1 - High (Alert On-Call)
- SLO breach (99.5% uptime violated)
- Performance degradation affecting >50% users
- Queue backed up >500 jobs
- Cost approaching daily cap

**Response Time:** 1 hour
**Escalation:** 2 hours if unresolved

### P2 - Medium (Investigate During Business Hours)
- SLO warning threshold reached
- Non-critical feature degraded
- Cache hit rate declining
- Slow queries detected

**Response Time:** 4 hours
**Escalation:** 24 hours if unresolved

### P3 - Low (Schedule for Next Sprint)
- Optimization opportunities
- Documentation gaps
- Non-urgent improvements

**Response Time:** Next business day
**Escalation:** Monthly review

---

## 📞 Escalation Path

```
Incident Detected
    ↓
On-Call Engineer (P0/P1)
    ↓ (2 hours unresolved)
Senior Engineer / Tech Lead
    ↓ (4 hours unresolved)
Engineering Manager + CEO
    ↓ (8 hours unresolved)
War Room + External Support
```

**On-Call Rotation:**
- Primary: Week 1-2
- Secondary: Week 3-4
- Backup: Engineering Manager (always available)

---

## 🔄 SLO Review Process

### Weekly Review (15 minutes)
- Review SLO dashboard
- Check for warning trends
- Update incident log
- Plan optimization work

### Monthly Review (1 hour)
- Analyze SLO achievement rates
- Review incident post-mortems
- Adjust SLO targets if needed
- Update runbooks based on learnings

### Quarterly Review (2 hours)
- Comprehensive SLO assessment
- Architecture improvements
- Cost optimization review
- Update monitoring strategy

---

## 📚 Related Documentation

- [Incident Response Runbook](./incident-response.md)
- [Rollback Procedures](./rollback-procedures.md)
- [Performance Testing Guide](./performance-testing.md)
- [Cost Management](./cost-management.md)
- [Architecture Guide](../ARCHITECTURE.md)

---

**Document Owner:** Platform Engineering
**Last Review:** October 8, 2025
**Next Review:** November 8, 2025
**Status:** Active ✅
