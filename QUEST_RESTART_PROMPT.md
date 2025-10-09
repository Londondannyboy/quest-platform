# Quest Platform Restart Prompt

**Last Commit:** `9146343` - "Change default to Haiku for cost efficiency"
**Status:** ✅ Production - Haiku model, pure markdown output, multi-API research
**Date:** October 10, 2025

---

## 🎯 Current State

**WORKING:**
- ✅ Multi-API research (6 APIs: Perplexity, DataForSEO, Tavily, Serper, LinkUp, Firecrawl)
- ✅ Haiku model (25x cheaper than Sonnet: $0.03/article vs $0.75)
- ✅ Pure markdown output (NO JSON wrapper)
- ✅ Citation validation (5+ citations required)
- ✅ Railway deployed and healthy
- ✅ max_tokens=8192 (API requirement, Claude stops naturally)

**Cost:** ~$0.60/article (was $0.77 with Sonnet)

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
- `QUEST_ARCHITECTURE_V2_3.md` - System architecture
- `backend/generate_article.py` - Main generation script
- `backend/app/agents/content.py` - Article generation (Haiku, pure markdown)

---

## ⚠️ Known Issues

1. **Unicode characters** - Use pre-commit hook to prevent (`.pre-commit-config.yaml`)
2. **LinkUp API** - Rate limited (429 errors expected)
3. **max_tokens** - Must be 8192 (not 16384) for Haiku/Sonnet

---

**Ready to generate articles with Haiku!** 🚀
