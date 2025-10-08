# Monitoring & Observability Guide

**Quest Platform v2.2.1 - Complete Monitoring Strategy**
**Last Updated:** October 8, 2025
**Owner:** Platform Engineering Team

---

## 📊 Overview

This guide provides comprehensive monitoring and observability setup for Quest Platform, covering infrastructure metrics, business metrics, alerting, and dashboard configuration.

### Monitoring Philosophy

- **Proactive**: Detect issues before users notice
- **Comprehensive**: Monitor all layers (infra, app, business)
- **Actionable**: Every alert has clear remediation steps
- **Cost-Effective**: Use free/low-cost tools when possible

---

## 🎯 Key Metrics Overview

### Infrastructure Metrics

| Category | Metrics | Target | Alert Threshold |
|----------|---------|--------|-----------------|
| **API Gateway** | Request rate, p95 latency, error rate | <200ms, <0.5% errors | >300ms, >1% errors |
| **Workers** | Queue depth, job latency, concurrency | <50 jobs, <60s | >100 jobs, >90s |
| **Database** | Query time, connection pool, storage | <50ms p95, <80% pool | >100ms, >90% pool |
| **Cache** | Hit rate, memory usage, eviction rate | >25%, <80% memory | <20%, >90% memory |

### Business Metrics

| Metric | Target | Tracking Method |
|--------|--------|-----------------|
| **Articles Generated/Day** | 30-50 | Database count |
| **Average Quality Score** | >85/100 | Database average |
| **Cost per Article** | <$0.60 | API usage tracking |
| **Auto-Publish Rate** | >80% | Status distribution |
| **Cache Hit Rate** | >31% | Vector similarity matches |

---

## 🔧 Monitoring Stack

### Primary Tools (Free/Included)

**1. Vercel Analytics (Frontend)**
- **Cost**: Free (included with Vercel)
- **Monitors**: Page loads, Core Web Vitals, geographic distribution
- **Access**: https://vercel.com/londondannyboys-projects/quest-platform/analytics

**Metrics Tracked:**
- Largest Contentful Paint (LCP): Target <2.5s, Actual 2.1s
- First Input Delay (FID): Target <100ms, Actual 78ms
- Cumulative Layout Shift (CLS): Target <0.1, Actual 0.08
- Time to First Byte (TTFB): Target <800ms, Actual 654ms

**2. Railway Metrics (Backend)**
- **Cost**: Free (included with Railway)
- **Monitors**: CPU, memory, network, deployment status
- **Access**: https://railway.app/project/{project_id}/metrics

**Metrics Tracked:**
- CPU Usage: Target <70%, Monitor for >85%
- Memory Usage: Target <1.5GB, Monitor for >2GB
- Network I/O: Track bandwidth usage
- Deployment Success Rate: Target 100%

**3. Neon Metrics (Database)**
- **Cost**: Free (included with Neon)
- **Monitors**: Connections, query performance, storage, replication lag
- **Access**: https://console.neon.tech/app/projects/{project_id}/monitoring

**Metrics Tracked:**
- Active Connections: Target <50, Monitor for >80
- Query Performance: p95 <50ms, Monitor for >100ms
- Storage Usage: Track growth rate
- Compute Hours: Cost tracking

**4. Upstash Metrics (Redis)**
- **Cost**: Free (included with Upstash)
- **Monitors**: Commands/sec, memory usage, latency
- **Access**: https://console.upstash.com/redis/{redis_id}

**Metrics Tracked:**
- Queue Depth: Target <50 jobs, Monitor for >100
- Memory Usage: Target <80%, Monitor for >90%
- Command Latency: Target <10ms, Monitor for >50ms
- Connection Count: Track concurrent connections

### Optional Tools (Enhanced Monitoring)

**5. Sentry (Error Tracking)**
- **Cost**: Free tier (5K errors/month)
- **Setup**:
```python
# backend/app/main.py
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("ENVIRONMENT", "production"),
    traces_sample_rate=0.1,  # 10% of transactions
)
```

**6. Plausible Analytics (Privacy-Friendly)**
- **Cost**: $9/month (optional)
- **Alternative**: Self-hosted (free)
- **Setup**: Add script tag to Astro sites

**7. Grafana (Custom Dashboards)**
- **Cost**: Free (self-hosted) or $0 (Grafana Cloud free tier)
- **Setup**: See section below

---

## 📈 Dashboard Setup

### 1. Vercel Analytics Dashboard

**Access**: Automatic (no setup needed)

**Key Pages to Monitor:**
- Homepage performance across sites
- Article page performance
- Real User Monitoring (RUM) data
- Geographic distribution
- Device breakdown

**How to Check:**
1. Go to https://vercel.com/londondannyboys-projects
2. Select project (relocation.quest, placement.quest, or rainmaker.quest)
3. Click "Analytics" tab
4. Review Core Web Vitals and page performance

### 2. Railway Metrics Dashboard

**Access**: Automatic (no setup needed)

**How to Check:**
1. Go to https://railway.app/project/{project_id}
2. Select service (quest-api-gateway, quest-workers, quest-directus)
3. Click "Metrics" tab
4. Review CPU, memory, network usage

**Alert Setup:**
1. Go to Railway project settings
2. Enable "Notifications"
3. Add Slack webhook or email
4. Configure thresholds (e.g., CPU >85% for 5 minutes)

### 3. Neon Monitoring Dashboard

**Access**: Automatic (no setup needed)

**How to Check:**
1. Go to https://console.neon.tech/app/projects/{project_id}
2. Click "Monitoring" tab
3. Review:
   - Connection count
   - Query performance (use `pg_stat_statements`)
   - Storage growth
   - Compute hours

**Query Performance Monitoring:**
```sql
-- Check slowest queries
SELECT
    query,
    calls,
    mean_exec_time / 1000 as avg_seconds,
    max_exec_time / 1000 as max_seconds
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Check most frequent queries
SELECT
    query,
    calls,
    total_exec_time / 1000 as total_seconds
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY calls DESC
LIMIT 10;
```

### 4. Custom Grafana Dashboard (Optional)

**Setup (Grafana Cloud - Free Tier):**

1. Sign up at https://grafana.com
2. Create new dashboard
3. Add data sources:
   - PostgreSQL (Neon connection)
   - Prometheus (Railway metrics)
   - JSON API (custom API metrics)

**Sample Dashboard Panels:**

**Panel 1: Article Generation Rate**
```sql
-- Query for Grafana PostgreSQL data source
SELECT
    DATE_TRUNC('hour', created_at) as time,
    COUNT(*) as articles_generated
FROM articles
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY time
ORDER BY time;
```

**Panel 2: Cache Hit Rate**
```sql
SELECT
    DATE_TRUNC('hour', created_at) as time,
    COUNT(*) FILTER (WHERE cache_hit = true) * 100.0 / COUNT(*) as hit_rate
FROM research_queries
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY time
ORDER BY time;
```

**Panel 3: Quality Score Distribution**
```sql
SELECT
    quality_score,
    COUNT(*) as count
FROM articles
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY quality_score
ORDER BY quality_score;
```

---

## 🚨 Alerting Configuration

### Critical Alerts (Page Immediately)

**1. API Gateway Down**
- **Condition**: Health check fails for 2 consecutive checks
- **Method**: Railway notifications → Slack/PagerDuty
- **Escalation**: Immediate to on-call engineer

**2. Database Connection Pool Exhausted**
- **Condition**: Connections >90% for 5 minutes
- **Method**: Custom script monitoring `pg_stat_activity`
- **Escalation**: Page immediately

**3. Cost Runaway**
- **Condition**: Daily cost >$28 (93% of $30 cap)
- **Method**: API cost tracking endpoint
- **Escalation**: Circuit breaker activates, page engineering manager

**4. Queue Backed Up**
- **Condition**: Queue depth >200 jobs for 10 minutes
- **Method**: Redis monitoring via Upstash
- **Escalation**: Page on-call engineer

### Warning Alerts (Investigate During Business Hours)

**5. Performance Degradation**
- **Condition**: p95 page load >4s for 30 minutes
- **Method**: Vercel Analytics webhook
- **Notification**: Slack #quest-alerts

**6. Cache Hit Rate Declining**
- **Condition**: Hit rate <20% for 24 hours
- **Method**: Daily cron job checking database
- **Notification**: Email to engineering team

**7. Error Rate Elevated**
- **Condition**: API error rate >2% for 15 minutes
- **Method**: Sentry alert
- **Notification**: Slack #quest-errors

---

## 📊 Monitoring Endpoints

### Health Checks

**API Gateway Health:**
```bash
GET https://api.quest.com/health

Response:
{
  "status": "healthy",
  "timestamp": "2025-10-08T12:00:00Z",
  "services": {
    "database": "connected",
    "redis": "connected",
    "workers": "running"
  },
  "version": "2.2.1"
}
```

**Worker Status:**
```bash
GET https://api.quest.com/api/workers/status

Response:
{
  "status": "running",
  "workers": 5,
  "queue_depth": 12,
  "jobs_completed_last_hour": 45,
  "average_job_time_seconds": 48
}
```

**Metrics Summary:**
```bash
GET https://api.quest.com/api/metrics/summary

Response:
{
  "articles_generated_today": 38,
  "average_quality_score": 87,
  "cost_today": 24.50,
  "cost_per_article": 0.64,
  "cache_hit_rate": 0.31,
  "api_uptime": 0.998
}
```

**Cost Breakdown:**
```bash
GET https://api.quest.com/api/metrics/costs/daily

Response:
{
  "date": "2025-10-08",
  "total_cost": 24.50,
  "breakdown": {
    "perplexity": 14.20,
    "claude": 8.80,
    "openai": 0.50,
    "replicate": 1.00
  },
  "articles_generated": 38,
  "cost_per_article": 0.64
}
```

---

## 🔍 Performance Monitoring Queries

### Database Performance

**Check Connection Pool:**
```sql
SELECT
    count(*) as total_connections,
    count(*) FILTER (WHERE state = 'active') as active,
    count(*) FILTER (WHERE state = 'idle') as idle
FROM pg_stat_activity;
```

**Check Query Performance:**
```sql
SELECT
    query,
    calls,
    mean_exec_time / 1000 as avg_seconds,
    max_exec_time / 1000 as max_seconds
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY mean_exec_time DESC
LIMIT 5;
```

**Check Cache Effectiveness:**
```sql
SELECT
    COUNT(*) FILTER (WHERE cache_hit = true) * 100.0 / COUNT(*) as hit_rate,
    AVG(similarity_score) as avg_similarity
FROM research_queries
WHERE created_at > NOW() - INTERVAL '24 hours';
```

### Queue Monitoring

**Check Queue Depth:**
```bash
redis-cli -u $REDIS_URL LLEN bull:articles:wait
```

**Check Recent Job Completions:**
```bash
redis-cli -u $REDIS_URL LRANGE bull:articles:completed 0 9
```

**Check Failed Jobs:**
```bash
redis-cli -u $REDIS_URL LLEN bull:articles:failed
```

---

## 📅 Monitoring Cadence

### Daily (Automated)
- Performance test suite runs (GitHub Actions)
- Cost tracking and alerting
- Error rate monitoring
- Queue depth checks

### Weekly (15-minute review)
- Review SLO dashboard
- Check for warning trends
- Analyze error patterns
- Review cost efficiency
- Plan optimization work

### Monthly (1-hour review)
- Comprehensive SLO analysis
- Review incident post-mortems
- Adjust monitoring thresholds
- Update alerting rules
- Cost optimization review

### Quarterly (2-hour review)
- Architecture performance assessment
- Scaling planning
- Tool evaluation (consider upgrades)
- Monitoring strategy updates

---

## 🛠️ Monitoring Tools Setup Scripts

### Script 1: Health Check Monitor

```bash
#!/bin/bash
# health-check-monitor.sh
# Run this as a cron job every 5 minutes

API_URL="https://api.quest.com"
SLACK_WEBHOOK="$SLACK_WEBHOOK_URL"

# Check API health
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" $API_URL/health)

if [ "$HEALTH" != "200" ]; then
    curl -X POST $SLACK_WEBHOOK \
        -H 'Content-Type: application/json' \
        -d "{\"text\":\"🚨 API Health Check Failed: HTTP $HEALTH\"}"
fi
```

### Script 2: Cost Monitor

```bash
#!/bin/bash
# cost-monitor.sh
# Run this hourly

API_URL="https://api.quest.com"
COST_CAP=28.00

COST=$(curl -s $API_URL/api/metrics/costs/daily | jq -r '.total_cost')

if (( $(echo "$COST > $COST_CAP" | bc -l) )); then
    curl -X POST $SLACK_WEBHOOK_URL \
        -H 'Content-Type: application/json' \
        -d "{\"text\":\"🚨 Cost Alert: $COST exceeds cap of $COST_CAP\"}"
fi
```

### Script 3: Queue Depth Monitor

```bash
#!/bin/bash
# queue-monitor.sh
# Run this every 10 minutes

REDIS_URL="$REDIS_URL"
ALERT_THRESHOLD=100

DEPTH=$(redis-cli -u $REDIS_URL LLEN bull:articles:wait)

if [ "$DEPTH" -gt "$ALERT_THRESHOLD" ]; then
    curl -X POST $SLACK_WEBHOOK_URL \
        -H 'Content-Type: application/json' \
        -d "{\"text\":\"⚠️ Queue Depth Alert: $DEPTH jobs pending\"}"
fi
```

---

## 📚 Related Documentation

- [SLO Document](./runbooks/SLO.md) - Service Level Objectives
- [Incident Response](./runbooks/incident-response.md) - Incident procedures
- [Performance Testing](../.github/workflows/performance.yml) - Automated testing
- [Architecture Guide](./ARCHITECTURE.md) - System architecture

---

**Document Owner:** Platform Engineering
**Last Review:** October 8, 2025
**Next Review:** November 8, 2025
**Status:** Active ✅

---

## 🎯 Quick Start Checklist

To get monitoring running:

- [ ] Enable Vercel Analytics (automatic)
- [ ] Configure Railway notifications (Slack webhook)
- [ ] Setup Neon monitoring alerts
- [ ] Create custom metrics endpoints in API
- [ ] Setup Sentry for error tracking (optional)
- [ ] Create health check cron jobs
- [ ] Configure cost monitoring alerts
- [ ] Setup Grafana dashboard (optional)
- [ ] Test all alert channels
- [ ] Document on-call rotation

**Estimated Setup Time:** 2-4 hours for complete monitoring stack
