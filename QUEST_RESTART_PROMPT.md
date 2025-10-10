# Quest Platform Restart Prompt

**Last Commit:** `9146343` - "Change default to Haiku for cost efficiency"
**Status:** ✅ Production - Haiku model, pure markdown output, multi-API research + 🎨 Template Intelligence Design Complete
**Date:** October 10, 2025 (Evening)

---

## 🎯 Current State

**WORKING (Production):**
- ✅ Multi-API research (6 APIs: Perplexity, DataForSEO, Tavily, Serper, LinkUp, Firecrawl)
- ✅ Haiku model (25x cheaper than Sonnet: $0.03/article vs $0.75)
- ✅ Pure markdown output (NO JSON wrapper)
- ✅ Citation validation (5+ citations required)
- ✅ Railway deployed and healthy
- ✅ max_tokens=8192 (API requirement, Claude stops naturally)

**Cost:** ~$0.60/article (production) | ~$0.68/article (with Template Intelligence)

**DESIGN COMPLETE (Oct 10, 2025):**
- 🎨 Template Intelligence System (QUEST_TEMPLATES.md - 980 lines)
  - 5 content archetypes (Skyscraper, Cluster Hub, Deep Dive, Comparison Matrix, News Hub)
  - 12 visual templates (Ultimate Guide, Listicle, Comparison, Location Guide, etc.)
  - 35 modular components (TldrSection, Calculator, FaqAccordion, etc.)
  - TemplateDetector agent (Serper + Firecrawl SERP analysis)
  - E-E-A-T optimization for YMYL content
  - 5 new database tables (serp_intelligence, scraped_competitors, etc.)
- ✅ Architecture updated to v2.4.0
- ✅ Phase 2.5 added to QUEST_TRACKER.md (implementation checklist ready)

---

## 🚀 Quick Start

### Generate Article
```bash
cd ~/quest-platform/backend
python3 generate_article.py --topic "Your topic" --site relocation
```

### Check Health
```bash
curl https://quest-platform-production-9ee0.up.railway.app/api/health
```

---

## ⚙️ Configuration

**Model:** Haiku (default) - Set `CONTENT_MODEL=claude-3-5-sonnet-20241022` in Railway for Sonnet

**DataForSEO Credentials** (in Railway):
```
DATAFORSEO_LOGIN=dan@predeploy.ai
DATAFORSEO_PASSWORD=9090d2e4183d704a
```

---

## 📚 Key Files

- `CLAUDE.md` - Full technical reference
- **`QUEST_TEMPLATES.md`** - Template Intelligence System (NEW - authority document)
- `QUEST_ARCHITECTURE_V2_4.md` - System architecture (v2.4.0 - Template Intelligence)
- `QUEST_TRACKER.md` - Phase 2.5 implementation checklist
- `backend/generate_article.py` - Main generation script
- `backend/app/agents/content.py` - Article generation (Haiku, pure markdown)

---

## ⚠️ Known Issues

1. **Unicode characters** - Use pre-commit hook to prevent (`.pre-commit-config.yaml`)
2. **LinkUp API** - Rate limited (429 errors expected)
3. **max_tokens** - Must be 8192 (not 16384) for Haiku/Sonnet

---

**Ready to generate articles with Haiku!** 🚀
