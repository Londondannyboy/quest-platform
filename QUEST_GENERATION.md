# Quest Platform - Article Generation Guide

**Purpose:** Authoritative documentation for the primary article generation script
**Script:** `generate_article.py` (at root level)
**Created:** October 10, 2025
**Status:** Production Ready

---

## 🎯 PRIMARY GENERATION SCRIPT

**`generate_article.py` (at root) is the SINGLE SOURCE OF TRUTH for article generation in Quest Platform.**

This script:
- Uses the full 7-agent orchestrator pipeline
- Includes LinkValidator for preventing hallucinated URLs
- Supports Directus publishing workflow
- Can scale to generate 100+ articles
- Tracks costs and quality metrics

---

## 📖 USAGE EXAMPLES

### Single Article Generation

```bash
# With specific topic
python3 generate_article.py --topic "Best cafes for remote work in Lisbon 2025"

# Interactive mode (will prompt for topic)
python3 generate_article.py

# Target different site
python3 generate_article.py --topic "Career growth strategies" --site placement
```

### Batch Generation

```bash
# Generate 10 articles with default topics
python3 generate_article.py --auto --count 10

# Generate 100 articles for production
python3 generate_article.py --auto --count 100

# Generate from topics file (one topic per line)
python3 generate_article.py --batch topics.txt

# Limit batch size
python3 generate_article.py --batch topics.txt --count 50
```

---

## 🏗️ ARCHITECTURE FLOW

```
generate_full_article.py
    ↓
ArticleOrchestrator (7 Agents)
    ├── ResearchAgent (Perplexity + fallbacks)
    ├── LinkValidator (External URL validation)
    ├── ContentAgent (Claude Sonnet 4.5)
    ├── EditorAgent (Quality scoring)
    ├── ImageAgent (FLUX + Cloudinary)
    ├── SEOAgent (Meta optimization)
    └── PDFAgent (Export capability)
    ↓
Database (Neon PostgreSQL)
    ↓
Directus CMS (Publishing workflow)
    ↓
Frontend (relocation.quest)
```

---

## 📊 OUTPUT FILES

The script generates summary files for tracking:

### Single Article: `generation_summary.json`
```json
{
  "timestamp": "2025-10-10T14:30:00",
  "articles_generated": 1,
  "total_cost": 0.3456,
  "article": {
    "id": "uuid",
    "title": "Article Title",
    "slug": "article-slug",
    "quality": 85,
    "url": "https://relocation.quest/article-slug"
  }
}
```

### Batch Generation: `batch_generation_summary.json`
```json
{
  "timestamp": "2025-10-10T14:30:00",
  "articles_requested": 100,
  "articles_generated": 98,
  "success_rate": "98.0%",
  "total_cost": 34.56,
  "average_quality": 83.5,
  "articles": [...]
}
```

---

## ⚙️ COMMAND LINE ARGUMENTS

| Argument | Description | Example |
|----------|-------------|---------|
| `--topic` | Single article topic | `--topic "Portugal visa guide"` |
| `--batch` | File with topics (one per line) | `--batch topics.txt` |
| `--auto` | Use default high-value topics | `--auto` |
| `--count` | Number of articles to generate | `--count 100` |
| `--site` | Target site (relocation/placement/rainmaker) | `--site relocation` |
| `--concurrent` | Max concurrent generations | `--concurrent 1` |

---

## 🔍 KEY FEATURES

### 1. Link Validation
- All external URLs are validated before inclusion
- Internal links suggest related articles
- No more hallucinated links (Option 3 implementation)

### 2. Progress Tracking
- Real-time progress updates
- Cost tracking per article
- Quality score reporting
- Success rate monitoring

### 3. Error Recovery
- Graceful error handling
- Partial batch completion
- Detailed error logging
- Resume capability via summaries

### 4. Cost Management
- Per-article cost tracking
- Total batch cost calculation
- Cost breakdown by agent
- Average cost metrics

---

## 📈 PRODUCTION USAGE

### Daily Article Generation
```bash
# Generate 20 articles per day
python3 generate_full_article.py --auto --count 20
```

### Topic Research Pipeline
```bash
# 1. Create topics file from research
echo "Portugal Digital Nomad Visa 2025" > topics.txt
echo "Best Coworking Spaces Lisbon" >> topics.txt
echo "Tax Guide US Citizens Portugal" >> topics.txt

# 2. Generate articles
python3 generate_full_article.py --batch topics.txt
```

### Quality Testing
```bash
# Generate single article for quality check
python3 generate_full_article.py --topic "Test topic for quality check"

# Review in Directus
# Publish if quality > 80
```

---

## 🚨 IMPORTANT NOTES

1. **This is the ONLY script for article generation** - Do not create test scripts
2. **Always includes full pipeline** - All 7 agents, link validation, image generation
3. **Production database** - Directly writes to Neon PostgreSQL
4. **Cost implications** - Each article costs ~$0.35-$0.45
5. **Rate limiting** - 10-second pause between batch articles

---

## 🐛 TROUBLESHOOTING

### Database Connection Error
```bash
# Ensure backend is running
cd ~/quest-platform/backend
python3 -m app.main
```

### API Key Issues
```bash
# Check .env file has all keys
cat ~/quest-platform/backend/.env | grep API_KEY
```

### Memory Issues with Large Batches
```bash
# Split into smaller batches
python3 generate_full_article.py --batch topics.txt --count 25
```

---

## 📝 MAINTENANCE

### Cleaning Test Articles
```sql
-- Connect to database
DELETE FROM articles WHERE quality_score < 60;
```

### Monitoring Generation
```bash
# Watch log in real-time
tail -f generation_summary.json
```

### Cost Analysis
```bash
# Parse batch summary for costs
cat batch_generation_summary.json | jq '.total_cost'
```

---

**Last Updated:** October 10, 2025
**Version:** 1.0 (Production Ready)