# Cost Optimization Strategies
**Date:** October 10, 2025
**Based on:** Claude Desktop Peer Review + Current Breakthrough

---

## 🎯 Current State (Proven Success)

**What's Working:**
- **Architecture:** 3x Gemini 2.5 Pro chunks + Sonnet 4.5 refinement
- **Output:** 5,344 words, high quality
- **Cost:** ~$0.75/article
- **Success Rate:** 95%+

**Cost Breakdown:**
```
Gemini 2.5 Pro (3 chunks):  $0.15
Gemini 2.5 Flash (weaving):  $0.01
Sonnet 4.5 (refinement):    $0.59
─────────────────────────────
Total:                      $0.75/article
```

---

## 💰 Cost Optimization Opportunities

### 1. Research API Caching (BIGGEST SAVINGS)
**Current Cost:** $0.20-0.30/article for Perplexity research
**Optimization:** Cache research at topic cluster level
**Savings:** 70-80% of research costs

**Implementation:**
```python
# backend/app/core/research_cache.py

class ClusterResearchCache:
    """
    Cache research at topic cluster level for massive savings

    Example: All "Portugal visa" articles share cluster research
    """

    TOPIC_CLUSTERS = {
        "portugal_digital_nomad": [
            "Portugal digital nomad visa",
            "Portugal D7 visa",
            "Portugal Golden visa",
            "Living in Portugal as digital nomad"
        ],
        "spain_visas": [
            "Spain digital nomad visa",
            "Spain non-lucrative visa",
            "Spain Golden visa"
        ],
        # ... etc
    }

    async def get_research(self, topic: str) -> Dict:
        """
        Check cluster cache before running expensive Perplexity
        """

        cluster_id = self._identify_cluster(topic)

        # Check if cluster research exists and is fresh (<90 days)
        cached = await self.db.get_cluster_research(
            cluster_id=cluster_id,
            max_age_days=90
        )

        if cached:
            logger.info("research_cache_hit", cluster=cluster_id, cost_saved=0.25)
            return cached

        # No cache: Run full research
        research = await self.perplexity_api.research(topic)

        # Cache for entire cluster
        await self.db.save_cluster_research(
            cluster_id=cluster_id,
            research=research,
            topics_covered=self.TOPIC_CLUSTERS[cluster_id]
        )

        return research
```

**Savings Calculation:**
- Without caching: 1000 articles × $0.25 = $250/month
- With caching: 100 clusters × $0.25 + 900 cache hits × $0 = $25/month
- **Savings: $225/month (90% reduction)**

### 2. Firecrawl URL Deduplication
**Current Cost:** $0.05/article for Firecrawl scraping
**Problem:** Scraping same competitor URLs repeatedly
**Optimization:** Cache scraped content permanently

**Implementation:**
```python
# backend/app/core/firecrawl_cache.py

class FirecrawlCache:
    """
    Cache scraped URLs permanently - content rarely changes
    """

    async def scrape_urls(self, urls: List[str]) -> List[Dict]:
        """
        Only scrape URLs we haven't seen before
        """

        results = []
        urls_to_scrape = []

        for url in urls:
            # Check if we've scraped this URL before
            cached = await self.db.get_scraped_content(url)

            if cached:
                # Check age - re-scrape if >180 days old
                if cached["age_days"] < 180:
                    logger.info("firecrawl_cache_hit", url=url, cost_saved=0.01)
                    results.append(cached["content"])
                    continue

            urls_to_scrape.append(url)

        # Only scrape new URLs
        if urls_to_scrape:
            scraped = await self.firecrawl_api.scrape(urls_to_scrape)

            # Cache all scraped content
            for url, content in zip(urls_to_scrape, scraped):
                await self.db.save_scraped_content(url, content)

            results.extend(scraped)

        return results
```

**Savings Calculation:**
- Average: 8 URLs per article
- Without caching: 1000 articles × 8 URLs × $0.001 = $8/month
- With caching: 80% cache hit rate = $1.60/month
- **Savings: $6.40/month (80% reduction)**

### 3. Image Generation Cost Reduction
**Current Cost:** $0.12/article (4 images × $0.03 each)
**Optimization:** Multiple strategies

**Strategy A: Reduce image count (EASIEST)**
```python
# Only generate 2 images instead of 4
IMAGE_STRATEGY = {
    "standard_article": {
        "hero_image": True,      # Always generate
        "content_images": 1,     # Only 1 content image
        "total_cost": 0.06       # 50% savings
    }
}
```
**Savings: $0.06/article = $60/month for 1000 articles**

**Strategy B: Use cheaper models**
```python
# Switch from FLUX Schnell to Stable Diffusion XL
IMAGE_MODELS = {
    "flux_schnell": {"cost": 0.03, "quality": "excellent"},
    "sdxl": {"cost": 0.01, "quality": "good"},          # 67% cheaper
    "dall_e_3": {"cost": 0.04, "quality": "excellent"}
}
```
**Savings: $0.08/article = $80/month for 1000 articles**

**Strategy C: Image reuse library**
```python
class ImageLibrary:
    """
    Build library of generic hero images to reuse
    """

    GENERIC_IMAGES = {
        "visa_application": [
            "passport_documents_desk.jpg",
            "visa_stamp_closeup.jpg",
            "application_form_laptop.jpg"
        ],
        "digital_nomad": [
            "laptop_beach.jpg",
            "coworking_space.jpg",
            "remote_worker_cafe.jpg"
        ]
    }

    async def get_hero_image(self, topic: str) -> str:
        """
        Use library image 70% of time, generate new 30%
        """

        category = self._categorize_topic(topic)

        if random.random() < 0.7:
            # Use existing image from library
            return random.choice(self.GENERIC_IMAGES[category])
        else:
            # Generate new image, add to library
            new_image = await self.flux_api.generate(topic)
            self.GENERIC_IMAGES[category].append(new_image)
            return new_image
```
**Savings: 70% reuse rate = $0.084/article = $84/month for 1000 articles**

### 4. Dynamic Chunking (ADVANCED)
**Current:** Fixed 3 chunks for all articles
**Optimization:** Adapt chunk count to topic complexity

**Implementation:**
```python
class AdaptiveChunkingStrategy:
    """
    Use fewer chunks for simple topics = lower cost
    """

    async def analyze_complexity(self, topic: str) -> Dict:
        """
        Quick Gemini Flash analysis to determine complexity
        """

        analysis_prompt = f"""
        Rate topic complexity (1-10): {topic}

        Consider:
        - Number of subtopics
        - Required depth
        - Research needed
        - Target length

        Return JSON: {{"complexity": 7, "recommended_chunks": 3, "word_target": 3500}}
        """

        # Use cheap Flash for analysis ($0.001)
        analysis = await self.gemini_flash.generate(analysis_prompt)
        return json.loads(analysis)

    async def execute_generation(self, topic: str):
        """
        Generate with optimal chunk count
        """

        strategy = await self.analyze_complexity(topic)

        if strategy["complexity"] <= 4:
            # Simple topic: 2 chunks
            return await self._simple_generation(topic, chunks=2)
            # Cost: $0.10 (Gemini) + $0.59 (Sonnet) = $0.69

        elif strategy["complexity"] <= 7:
            # Medium topic: 3 chunks (your proven method)
            return await self._standard_generation(topic, chunks=3)
            # Cost: $0.15 (Gemini) + $0.59 (Sonnet) = $0.74

        else:
            # Complex topic: 4-5 chunks
            return await self._complex_generation(topic, chunks=4)
            # Cost: $0.20 (Gemini) + $0.59 (Sonnet) = $0.79
```

**Savings:**
- 30% simple topics: Save $0.05/article
- 50% medium topics: Current cost
- 20% complex topics: Add $0.05/article
- **Net savings: $0.015/article = $15/month for 1000 articles**

### 5. Tiered Quality System (BIGGEST OPPORTUNITY)
**Idea:** Not all content needs premium quality

**Implementation:**
```python
class TieredContentGeneration:
    """
    Offer different quality tiers at different price points
    """

    TIERS = {
        "economy": {
            "model_stack": ["gemini-2.5-flash"],  # Single pass
            "chunks": 1,
            "word_target": 2000,
            "cost": 0.05,
            "use_case": "High-volume, SEO fodder, link building"
        },

        "standard": {
            "model_stack": ["gemini-2.5-pro", "sonnet-4.5"],  # Your method
            "chunks": 3,
            "word_target": 5000,
            "cost": 0.75,
            "use_case": "Main content, authority building"
        },

        "premium": {
            "model_stack": ["opus-4", "gemini-2.5-pro", "perplexity", "sonnet-4.5"],
            "chunks": 5,
            "word_target": 8000,
            "cost": 1.50,
            "use_case": "Flagship content, cornerstone articles"
        }
    }

    async def generate(self, topic: str, tier: str = "standard"):
        """
        Generate at specified tier
        """

        config = self.TIERS[tier]

        if tier == "economy":
            # Single Gemini Flash pass (super cheap)
            return await self._economy_generation(topic)

        elif tier == "standard":
            # Your proven 3-chunk method
            return await self._standard_generation(topic)

        else:
            # Premium multi-model pipeline
            return await self._premium_generation(topic)
```

**Usage Strategy:**
```python
CONTENT_MIX = {
    "economy": 0.30,    # 300 articles × $0.05 = $15
    "standard": 0.60,   # 600 articles × $0.75 = $450
    "premium": 0.10     # 100 articles × $1.50 = $150
}

# Total for 1000 articles: $615
# vs. All standard: $750
# Savings: $135/month (18% reduction)
```

---

## 📊 Combined Optimization Impact

### Current Costs (1000 articles/month):
```
Research (Perplexity):     $250
Content Generation:        $750
Images (4 per article):    $120
Firecrawl Scraping:        $8
─────────────────────────────
Total:                     $1,128/month
Per Article:               $1.13
```

### Optimized Costs (with all strategies):
```
Research (cached 90%):     $25      (-$225)
Content (tiered mix):      $615     (-$135)
Images (2 per, reuse):     $36      (-$84)
Firecrawl (cached 80%):    $1.60    (-$6.40)
─────────────────────────────
Total:                     $677.60/month
Per Article:               $0.68
Savings:                   $450.40/month (40% reduction)
```

### At Scale (5000 articles/month):
```
Without optimization:      $5,640/month
With optimization:         $3,388/month
Annual savings:            $27,024/year
```

---

## 🎯 Implementation Roadmap

### Phase 1: Quick Wins (Week 1)
1. ✅ Implement Firecrawl URL caching (80% hit rate)
2. ✅ Reduce images from 4 → 2 per article
3. ✅ Add weaving function (already done!)

**Immediate Savings: ~$150/month**

### Phase 2: Research Optimization (Week 2-3)
4. ✅ Build topic cluster taxonomy
5. ✅ Implement cluster research caching
6. ✅ Test cache hit rates

**Additional Savings: ~$225/month**

### Phase 3: Tiered System (Week 4-6)
7. ✅ Implement economy tier (Gemini Flash only)
8. ✅ Test premium tier (Opus + multi-model)
9. ✅ Define content mix strategy

**Additional Savings: ~$135/month**

### Phase 4: Advanced (Month 2-3)
10. ✅ Implement adaptive chunking
11. ✅ Build image reuse library
12. ✅ Add quality feedback loop

**Additional Savings: ~$50/month**

**Total Optimized Savings: $450/month (40% reduction)**

---

## 🔬 A/B Testing Framework

Test optimizations scientifically:

```python
class CostOptimizationTester:
    """
    A/B test cost optimizations against quality metrics
    """

    async def run_experiment(self, topic: str):
        """
        Generate same article with different strategies
        """

        variants = await asyncio.gather(
            # Control: Current method
            self.chunked_agent.generate(topic, tier="standard"),

            # Variant A: Economy tier
            self.chunked_agent.generate(topic, tier="economy"),

            # Variant B: 2 chunks instead of 3
            self.chunked_agent.generate(topic, chunks=2),

            # Variant C: Flash weaving only (no Sonnet)
            self.chunked_agent.generate(topic, refine=False)
        )

        # Score all variants
        scores = await asyncio.gather(*[
            self.editor_agent.score(v) for v in variants
        ])

        # Calculate cost vs quality tradeoff
        analysis = {
            "control": {
                "cost": variants[0]["cost"],
                "quality": scores[0],
                "words": len(variants[0]["content"].split())
            },
            "economy": {
                "cost": variants[1]["cost"],
                "quality": scores[1],
                "cost_per_quality_point": variants[1]["cost"] / scores[1]
            },
            "2_chunks": {
                "cost": variants[2]["cost"],
                "quality": scores[2],
                "savings": variants[0]["cost"] - variants[2]["cost"]
            },
            "no_refinement": {
                "cost": variants[3]["cost"],
                "quality": scores[3],
                "quality_drop": scores[0] - scores[3]
            }
        }

        return analysis
```

---

## 💡 Strategic Recommendations

### For Your Current Scale (100-500 articles/month):
**Priority: Implement Phase 1 + 2**
- Quick wins: $150/month savings
- Research caching: $225/month savings
- **Total savings: $375/month**

### For Scale Target (1000-2000 articles/month):
**Priority: Implement all phases**
- Full optimization: $450-900/month savings
- Pay for itself in <1 week
- **ROI: 300-400%**

### For Enterprise Scale (5000+ articles/month):
**Priority: Build custom infrastructure**
- Dedicated research database
- ML-based quality prediction
- Auto-optimization based on feedback
- **Potential savings: $27K+/year**

---

## ⚠️ Quality vs Cost Tradeoffs

**What to optimize:**
- ✅ Research caching (no quality impact)
- ✅ Firecrawl caching (no quality impact)
- ✅ Image count reduction (minimal impact)
- ✅ Tiered system (intentional quality tiers)

**What NOT to optimize:**
- ❌ Sonnet refinement (core quality driver)
- ❌ Citation count (E-E-A-T requirement)
- ❌ Word count below 3000 (SEO minimum)
- ❌ Human review process (safety net)

---

## 🎯 Next Actions

1. **This Week:** Implement Firecrawl caching + reduce images to 2
2. **Next Week:** Build topic cluster taxonomy for research caching
3. **Month 1:** Test tiered content generation with 10 articles each
4. **Month 2:** Roll out full optimization stack
5. **Month 3:** Measure results, iterate on feedback

---

**Bottom Line:** You can reduce costs by 40% ($450/month at 1000 articles) while maintaining or improving quality through smart caching and tiered generation.
