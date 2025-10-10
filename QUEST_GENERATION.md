# Quest Platform - Article Generation Guide

**Purpose:** Authoritative documentation for the primary article generation script
**Script:** `backend/generate_article.py`
**Last Updated:** October 10, 2025 (Evening)
**Status:** ✅ Production Ready (Haiku Model, 6-API Research)

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
# With specific topic (standard skyscraper)
python3 generate_article.py --topic "Best cafes for remote work in Lisbon 2025"

# Interactive mode (will prompt for topic)
python3 generate_article.py

# Target different site
python3 generate_article.py --topic "Career growth strategies" --site placement

# NEW (v2.5): Conversational archetype with persona
python3 generate_article.py \
  --archetype conversational \
  --persona-nationality "US citizen" \
  --persona-profession "software engineer" \
  --persona-situation "working remotely" \
  --persona-question "Can I get a Portugal digital nomad visa?" \
  --site relocation
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

# NEW (v2.5): Generate conversational articles from pattern file
python3 generate_article.py --batch conversational_patterns.csv --archetype conversational --count 100
```

---

## 🏗️ ARCHITECTURE FLOW (Updated Oct 10, 2025)

```
backend/generate_article.py
    ↓
ArticleOrchestrator (5 Agents + LinkValidator)
    ├── KeywordResearcher (DataForSEO + Perplexity)
    ├── ResearchAgent (6 APIs: Serper → Firecrawl → Perplexity + Tavily + LinkUp + DataForSEO)
    ├── LinkValidator (External URL validation)
    ├── ContentAgent (Claude Haiku - 25x cheaper!)
    ├── EditorAgent (Quality scoring + citation validation)
    └── ImageAgent (FLUX + Cloudinary - 4 images/article)
    ↓
Database (Neon PostgreSQL)
    ↓
Directus CMS (Publishing workflow)
    ↓
Frontend (relocation.quest)
```

**Major Updates:**
- ✅ Multi-API research (6 APIs integrated)
- ✅ Haiku model ($0.03 vs $0.75 Sonnet)
- ✅ Pure markdown output (no JSON wrapper)
- ✅ DataForSEO keyword validation
- ✅ Citation validation (minimum 5 required)

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

**Note:** `--concurrent` flag exists in code but is not currently implemented (planned for TIER 1).

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

## 🗣️ CONVERSATIONAL ARTICLE GENERATION (v2.5)

**New Feature:** Generate persona-specific conversational articles for long-tail queries.

### What's New in v2.5

**Conversational Archetype Support:**
- Generates 1,500-3,000 word persona-specific answers
- Targets 9-35 word conversational queries
- Cross-site support (relocation, placement, rainmaker)
- AI citation optimized (ChatGPT, Perplexity, Claude, Google AI)

### Conversational Article Examples

**relocation.quest:**
```bash
python3 generate_article.py \
  --archetype conversational \
  --persona-nationality "US citizen" \
  --persona-profession "software engineer" \
  --persona-situation "working remotely making $120k" \
  --persona-question "Can I get a Portugal digital nomad visa?" \
  --site relocation

# Generates:
# - Title: "I'm a US Citizen Software Engineer - Can I Get a Portugal Digital Nomad Visa?"
# - Word count: ~2,000 words
# - Persona-specific (US tax info, income requirements for US citizens)
# - Direct answer in first 100 words
# - Case study: US software engineer who got the visa
```

**placement.quest:**
```bash
python3 generate_article.py \
  --archetype conversational \
  --persona-profession "marketing manager" \
  --persona-situation "7 years experience in London" \
  --persona-question "How do I negotiate remote work with my employer?" \
  --site placement

# Generates:
# - Title: "I'm a Marketing Manager with 7 Years Experience - How Do I Negotiate Remote Work?"
# - Word count: ~1,800 words
# - Manager-specific tactics (not entry-level advice)
# - London market context
# - Case study: Marketing manager who successfully negotiated
```

**rainmaker.quest:**
```bash
python3 generate_article.py \
  --archetype conversational \
  --persona-profession "freelance web designer" \
  --persona-situation "making $8k/month with 5 clients" \
  --persona-question "Should I form an LLC or stay as a sole proprietor?" \
  --site rainmaker

# Generates:
# - Title: "I'm a Freelance Web Designer Making $8k/Month - Should I Form an LLC?"
# - Word count: ~2,500 words
# - $8k/month tax bracket analysis
# - 5-client business structure considerations
# - Case study: Freelancer at this revenue level
```

### Pattern Generation Workflow

**Step 1: Generate Patterns (One-Time Setup)**

```bash
# Generate 100 conversational patterns per site (300 total)
cd ~/quest-platform/backend
python3 scripts/generate_conversational_patterns.py \
  --site relocation \
  --count 100

python3 scripts/generate_conversational_patterns.py \
  --site placement \
  --count 100

python3 scripts/generate_conversational_patterns.py \
  --site rainmaker \
  --count 100

# Stores patterns in conversational_patterns table
# Each pattern includes: persona dimensions + question + priority score
```

**Step 2: Generate Articles from Patterns**

```bash
# Generate first 10 conversational articles (validation)
python3 generate_article.py \
  --archetype conversational \
  --from-patterns \
  --count 10 \
  --site relocation

# If validation successful (40%+ AI citation rate), scale to 100
python3 generate_article.py \
  --archetype conversational \
  --from-patterns \
  --count 100 \
  --site relocation
```

**Step 3: AI Citation Testing**

```bash
# Test AI citation rate for conversational articles
python3 scripts/test_ai_citations.py \
  --archetype conversational \
  --count 10

# Output: {chatgpt: 4/10, perplexity: 5/10, claude: 3/10, google_ai: 2/10}
# Citation rate: 50% (5/10 articles cited by at least 1 AI)
```

### Command-Line Arguments (Extended for v2.5)

**New Arguments:**

| Argument | Description | Example |
|----------|-------------|---------|
| `--archetype` | Content archetype (skyscraper, conversational, etc.) | `--archetype conversational` |
| `--persona-nationality` | Persona nationality (for conversational) | `--persona-nationality "US citizen"` |
| `--persona-profession` | Persona profession/role | `--persona-profession "software engineer"` |
| `--persona-situation` | Persona situation/context | `--persona-situation "working remotely"` |
| `--persona-question` | The exact conversational question | `--persona-question "Can I get a visa?"` |
| `--from-patterns` | Generate from conversational_patterns table | `--from-patterns` |

**Existing Arguments (Still Supported):**

| Argument | Description | Example |
|----------|-------------|---------|
| `--topic` | Single article topic (standard) | `--topic "Portugal visa guide"` |
| `--batch` | File with topics (one per line) | `--batch topics.txt` |
| `--auto` | Use default high-value topics | `--auto` |
| `--count` | Number of articles to generate | `--count 100` |
| `--site` | Target site (relocation/placement/rainmaker) | `--site relocation` |

### Cost Analysis (v2.5)

**Conversational Article Cost:**
- Research (6 APIs): $0.44
- Template Intelligence: $0.08
- Content Generation (Haiku): $0.03 (same as skyscraper)
- Images: $0.12
- **Total: $0.67/article (same as standard articles)**

**AI Citation Testing (Optional):**
- 4 platforms × $0.01/query = $0.04/article
- **Total with testing: $0.71/article**

**Batch Generation (100 conversational articles):**
- Generation: 100 × $0.67 = $67
- AI testing: 100 × $0.04 = $4
- **Total: $71 for 100 articles**

### Implementation Status

**Current (v2.5 Design):**
- ✅ Conversational archetype documented
- ✅ Pattern generation strategy designed
- ✅ Database schema defined (backwards compatible)
- ✅ Command-line arguments specified
- ⏳ Implementation: TIER 0.9 (Week 9-12)

**Pending Implementation:**
- ⏳ Add `--archetype` argument to generate_article.py
- ⏳ Add persona arguments (--persona-nationality, etc.)
- ⏳ Create scripts/generate_conversational_patterns.py
- ⏳ Create scripts/test_ai_citations.py
- ⏳ Update ContentAgent with CONVERSATIONAL_PROMPT
- ⏳ Deploy conversational_patterns table to Neon

**Timeline:**
- Week 1-4: Get 20 standard articles live (current priority)
- Week 5-8: Implement Template Intelligence (TIER 0.5)
- Week 9-12: Implement Conversational SEO (TIER 0.9)
- Week 13+: Scale to 300 conversational articles (100 per site)

---

**Last Updated:** October 10, 2025 (Late Evening)
**Version:** 1.1 (v2.5 - Conversational Archetype Support)