# JSON Schema Guide for LLM Optimization

**Version:** 2.3.0
**Date:** October 8, 2025
**Target Audience:** Developers, Content Creators
**Status:** Production Ready

---

## 🎯 Overview

This guide provides **copy-paste JSON-LD schema templates** optimized for LLM discovery and citation.

**Why This Matters:**
- LLMs read JSON schema FIRST before article body
- Google stopped prioritizing verbose schema, but **LLMs still do**
- Better schema = better LLM understanding = higher citation chances

**Key Principle:**
> Google-safe schema is minimal. LLM-optimized schema is verbose and comprehensive.

---

## 📋 Schema Templates

### **Template 1: Standard Article (Most Common)**

**Use For:** Blog posts, guides, how-tos, informational content

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Portugal Digital Nomad Visa: Complete 2025 Guide",
  "description": "Comprehensive guide to Portugal Digital Nomad Visa requirements, application process, costs, tax benefits, and best cities for remote workers in 2025",
  "articleBody": "Portugal has become one of the most popular destinations for digital nomads...",
  "url": "https://relocation.quest/portugal-digital-nomad-visa",
  "datePublished": "2025-10-08T12:00:00Z",
  "dateModified": "2025-10-08T12:00:00Z",
  "wordCount": 2847,

  "author": {
    "@type": "Organization",
    "name": "Quest Platform",
    "description": "AI-powered content intelligence platform with human verification and quality gates",
    "url": "https://relocation.quest"
  },

  "publisher": {
    "@type": "Organization",
    "name": "Quest Platform",
    "description": "Premium content intelligence platform combining AI generation with human editorial oversight",
    "logo": {
      "@type": "ImageObject",
      "url": "https://relocation.quest/logo.png"
    }
  },

  "image": {
    "@type": "ImageObject",
    "url": "https://res.cloudinary.com/quest/image/portugal-visa.jpg",
    "width": 1200,
    "height": 630
  },

  "keywords": "portugal, digital nomad, visa, remote work, 2025",

  "about": {
    "@type": "Thing",
    "name": "Portugal Digital Nomad Visa",
    "description": "Visa program allowing remote workers to live in Portugal while working for foreign employers"
  },

  "articleSection": "Relocation Guides",

  "isPartOf": {
    "@type": "WebSite",
    "name": "Quest Platform",
    "url": "https://relocation.quest"
  },

  "mentions": [
    {
      "@type": "Place",
      "name": "Portugal",
      "sameAs": "https://en.wikipedia.org/wiki/Portugal"
    },
    {
      "@type": "GovernmentOrganization",
      "name": "SEF - Portuguese Immigration Service",
      "sameAs": "https://imigrante.sef.pt"
    }
  ],

  "citation": [
    {
      "@type": "WebPage",
      "url": "https://imigrante.sef.pt"
    },
    {
      "@type": "WebPage",
      "url": "https://www.portugal.gov.pt"
    }
  ]
}
```

**Key Elements:**
- ✅ Verbose description (LLMs don't penalize this)
- ✅ Entity mentions with Wikipedia/authoritative links
- ✅ Citations to sources
- ✅ Clear about/articleSection for context
- ✅ Complete author/publisher information

---

### **Template 2: Article + FAQ (Highly Recommended)**

**Use For:** Guides with common questions, visa guides, how-to content

```json
[
  {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Portugal Digital Nomad Visa: Complete 2025 Guide",
    "description": "Comprehensive guide to Portugal Digital Nomad Visa requirements, application process, costs, tax benefits, and best cities for remote workers in 2025",
    "url": "https://relocation.quest/portugal-digital-nomad-visa",
    "datePublished": "2025-10-08T12:00:00Z",
    "dateModified": "2025-10-08T12:00:00Z",
    "wordCount": 2847,

    "author": {
      "@type": "Organization",
      "name": "Quest Platform",
      "url": "https://relocation.quest"
    },

    "publisher": {
      "@type": "Organization",
      "name": "Quest Platform",
      "logo": {
        "@type": "ImageObject",
        "url": "https://relocation.quest/logo.png"
      }
    },

    "image": {
      "@type": "ImageObject",
      "url": "https://res.cloudinary.com/quest/image/portugal-visa.jpg",
      "width": 1200,
      "height": 630
    },

    "keywords": "portugal, digital nomad, visa, remote work, 2025",

    "mentions": [
      {
        "@type": "Place",
        "name": "Portugal",
        "sameAs": "https://en.wikipedia.org/wiki/Portugal"
      }
    ],

    "citation": [
      {
        "@type": "WebPage",
        "url": "https://imigrante.sef.pt"
      }
    ]
  },
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "How much income do I need for Portugal Digital Nomad Visa?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "You must demonstrate minimum monthly income of €3,280 (approximately $3,500 USD) from remote work for a foreign employer or clients."
        }
      },
      {
        "@type": "Question",
        "name": "Can I bring my family to Portugal on a Digital Nomad Visa?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Yes, your spouse and dependent children can apply for family reunification once you have received the digital nomad visa. They will need to provide proof of relationship and financial support."
        }
      },
      {
        "@type": "Question",
        "name": "How long does it take to get approved?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Processing time is typically 2-3 months from application submission. You should apply at least 3 months before your intended move date."
        }
      },
      {
        "@type": "Question",
        "name": "What are the tax benefits?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Portugal offers the Non-Habitual Resident (NHR) tax regime with 0-20% flat tax on foreign income for the first 10 years of residency."
        }
      }
    ]
  }
]
```

**Why FAQs Work:**
- LLMs **love Q&A format** (matches how they respond to users)
- Provides quick, scannable information
- Increases chances of being cited for specific questions
- Easy to extract and reformat

---

### **Template 3: HowTo Guide (Step-by-Step)**

**Use For:** Tutorials, processes, instructional content

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to Apply for Portugal Digital Nomad Visa",
  "description": "Step-by-step guide to applying for Portugal's Digital Nomad Visa, from document preparation to approval",
  "image": {
    "@type": "ImageObject",
    "url": "https://res.cloudinary.com/quest/image/portugal-visa-process.jpg"
  },
  "totalTime": "PT3M",
  "estimatedCost": {
    "@type": "MonetaryAmount",
    "currency": "EUR",
    "value": "250"
  },
  "supply": [
    {
      "@type": "HowToSupply",
      "name": "Valid passport"
    },
    {
      "@type": "HowToSupply",
      "name": "Proof of income (bank statements, employment contract)"
    },
    {
      "@type": "HowToSupply",
      "name": "Health insurance documentation"
    }
  ],
  "step": [
    {
      "@type": "HowToStep",
      "name": "Gather Required Documents",
      "text": "Collect passport, proof of income showing €3,280/month minimum, health insurance, background check, and proof of accommodation.",
      "position": 1
    },
    {
      "@type": "HowToStep",
      "name": "Submit Online Application",
      "text": "Create account on SEF website (imigrante.sef.pt) and complete the online application form. Upload all required documents.",
      "position": 2,
      "url": "https://imigrante.sef.pt"
    },
    {
      "@type": "HowToStep",
      "name": "Pay Application Fee",
      "text": "Pay the €83 application fee online using credit card or bank transfer.",
      "position": 3
    },
    {
      "@type": "HowToStep",
      "name": "Schedule Biometrics Appointment",
      "text": "Once application is reviewed, schedule appointment at Portuguese consulate for fingerprints and photo.",
      "position": 4
    },
    {
      "@type": "HowToStep",
      "name": "Wait for Decision",
      "text": "Processing time is typically 2-3 months. You'll receive email notification when decision is made.",
      "position": 5
    },
    {
      "@type": "HowToStep",
      "name": "Collect Residence Permit",
      "text": "If approved, collect your residence permit card from SEF office in Portugal within 30 days.",
      "position": 6
    }
  ]
}
```

**Why HowTo Schema Works:**
- Clear step-by-step structure LLMs can easily parse
- Estimated cost and time (practical information)
- Supply list (materials needed)
- Position numbers make sequence explicit

---

### **Template 4: Comparison/Listicle**

**Use For:** "Best of" lists, comparisons, rankings

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Best Countries for Digital Nomads in 2025: Top 10 Rankings",
  "description": "Comprehensive comparison of the 10 best countries for digital nomads in 2025, including visa requirements, cost of living, internet speed, and quality of life",
  "url": "https://relocation.quest/best-countries-digital-nomads-2025",
  "datePublished": "2025-10-08T12:00:00Z",
  "wordCount": 3542,

  "author": {
    "@type": "Organization",
    "name": "Quest Platform",
    "url": "https://relocation.quest"
  },

  "publisher": {
    "@type": "Organization",
    "name": "Quest Platform",
    "logo": {
      "@type": "ImageObject",
      "url": "https://relocation.quest/logo.png"
    }
  },

  "image": {
    "@type": "ImageObject",
    "url": "https://res.cloudinary.com/quest/image/best-countries.jpg",
    "width": 1200,
    "height": 630
  },

  "keywords": "digital nomad, best countries, remote work, visa, cost of living, 2025",

  "about": {
    "@type": "Thing",
    "name": "Digital Nomad Countries",
    "description": "Countries offering favorable conditions for remote workers including visa programs, infrastructure, and cost of living"
  },

  "mentions": [
    {
      "@type": "Place",
      "name": "Portugal",
      "sameAs": "https://en.wikipedia.org/wiki/Portugal"
    },
    {
      "@type": "Place",
      "name": "Spain",
      "sameAs": "https://en.wikipedia.org/wiki/Spain"
    },
    {
      "@type": "Place",
      "name": "Thailand",
      "sameAs": "https://en.wikipedia.org/wiki/Thailand"
    },
    {
      "@type": "Place",
      "name": "Mexico",
      "sameAs": "https://en.wikipedia.org/wiki/Mexico"
    },
    {
      "@type": "Place",
      "name": "Estonia",
      "sameAs": "https://en.wikipedia.org/wiki/Estonia"
    }
  ],

  "citation": [
    {
      "@type": "WebPage",
      "url": "https://nomadlist.com"
    },
    {
      "@type": "WebPage",
      "url": "https://www.numbeo.com"
    }
  ],

  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "item": {
        "@type": "Place",
        "name": "Portugal",
        "description": "Best overall for digital nomads with dedicated visa program, excellent infrastructure, and NHR tax benefits"
      }
    },
    {
      "@type": "ListItem",
      "position": 2,
      "item": {
        "@type": "Place",
        "name": "Spain",
        "description": "New digital nomad visa, major cities with coworking spaces, excellent quality of life"
      }
    },
    {
      "@type": "ListItem",
      "position": 3,
      "item": {
        "@type": "Place",
        "name": "Thailand",
        "description": "Low cost of living, vibrant expat community, recent digital nomad visa program"
      }
    }
  ]
}
```

**Why Listicle Schema Works:**
- `itemListElement` explicitly lists rankings
- Entity mentions for each country (LLM context)
- Clear positioning (1st, 2nd, 3rd)
- Easy for LLMs to extract and cite

---

## 🛠️ Implementation Guide

### **Using SEOEnhancer (Automatic)**

Quest Platform automatically generates LLM-optimized schema via `SEOEnhancer`:

```python
from app.agents.seo import SEOEnhancer, EntityMention, FAQItem

enhancer = SEOEnhancer()

# Generate article schema
schema = enhancer.generate_article_schema(
    title=article.title,
    description=article.seo_description,
    content=article.content,
    url=f"https://relocation.quest/{article.slug}",
    image_url=article.featured_image_url,
    keywords=article.keywords,
    entities=article.entities,  # Extracted automatically
    faqs=article.faqs,          # Generated by ContentAgent
    citations=article.sources,
    word_count=article.word_count
)

# Embed in <head> tag
# <script type="application/ld+json">{schema}</script>
```

### **Manual Schema Generation**

For custom pages or special content:

**Step 1: Choose Template**
- Standard article → Template 1
- Guide with FAQs → Template 2
- Step-by-step → Template 3
- Ranking/list → Template 4

**Step 2: Fill in Values**
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "[YOUR ARTICLE TITLE]",
  "description": "[COMPREHENSIVE DESCRIPTION, BE VERBOSE]",
  "url": "[FULL URL]",
  "datePublished": "[ISO 8601 DATE]",
  ...
}
```

**Step 3: Add Entity Mentions**
```json
"mentions": [
  {
    "@type": "[Place|Organization|Person]",
    "name": "[ENTITY NAME]",
    "sameAs": "[WIKIPEDIA OR AUTHORITATIVE URL]"
  }
]
```

**Step 4: Add Citations**
```json
"citation": [
  {
    "@type": "WebPage",
    "url": "[SOURCE URL]"
  }
]
```

**Step 5: Embed in HTML**
```html
<head>
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Article",
    ...
  }
  </script>
</head>
```

---

## ✅ Schema Checklist

For **every schema**, include:

- [ ] Verbose description (100+ words)
- [ ] Full URL (canonical)
- [ ] Publication and modified dates
- [ ] Word count
- [ ] Complete author/publisher info
- [ ] Featured image with dimensions
- [ ] Keywords (5-10 relevant terms)
- [ ] About/articleSection for context

For **LLM optimization**, add:

- [ ] Entity mentions (3-10 per article)
- [ ] Wikipedia or authoritative links for entities
- [ ] Citations to sources (3-10 per article)
- [ ] FAQ section (4-10 Q&A pairs)

For **special content**, consider:

- [ ] HowTo schema for step-by-step guides
- [ ] ListItem schema for rankings/comparisons
- [ ] Multiple schema types (Article + FAQ)

---

## 📊 Schema Testing

### **Validation Tools**

**1. Schema.org Validator**
- URL: https://validator.schema.org/
- Paste your JSON-LD
- Check for syntax errors

**2. Google Rich Results Test**
- URL: https://search.google.com/test/rich-results
- Enter article URL
- Check what Google sees (but remember: LLMs see more)

**3. Manual LLM Testing**
- Test in ChatGPT: "What are Portugal digital nomad visa requirements?"
- Test in Perplexity: Same query
- Test in Claude: Same query
- Check if your content is cited

### **Common Errors**

**Error 1: Missing @context**
```json
// ❌ WRONG
{
  "@type": "Article",
  "headline": "..."
}

// ✅ CORRECT
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "..."
}
```

**Error 2: Invalid Date Format**
```json
// ❌ WRONG
"datePublished": "10/8/2025"

// ✅ CORRECT
"datePublished": "2025-10-08T12:00:00Z"
```

**Error 3: Missing Required Fields**
```json
// ❌ MINIMAL (Google-safe but LLM-weak)
{
  "@type": "Article",
  "headline": "Portugal Visa Guide"
}

// ✅ LLM-OPTIMIZED
{
  "@type": "Article",
  "headline": "Portugal Digital Nomad Visa: Complete 2025 Guide",
  "description": "Comprehensive guide...",
  "author": {...},
  "publisher": {...},
  "datePublished": "...",
  "mentions": [...],
  "citation": [...]
}
```

---

## 🎯 Best Practices Summary

**DO:**
- ✅ Be verbose (LLMs don't penalize this)
- ✅ Include entity mentions with Wikipedia links
- ✅ Add citations to authoritative sources
- ✅ Use FAQ schema whenever possible
- ✅ Provide complete metadata
- ✅ Test in multiple LLMs

**DON'T:**
- ❌ Copy Google-minimal schema templates
- ❌ Skip entity mentions to save space
- ❌ Forget publication dates
- ❌ Use relative URLs
- ❌ Ignore FAQ opportunities
- ❌ Assume Google validator = LLM optimized

---

## 📚 Related Documentation

- [LLM Optimization Guide](./LLM-OPTIMIZATION.md) - Complete LLM ranking strategies
- [2026 SEO Strategy](./2026-STRATEGY.md) - Strategic overview
- [PDF Strategy](./PDF-STRATEGY.md) - PDF generation for LLM SEO
- [Press Release Workflow](./PRESS-RELEASE-WORKFLOW.md) - Press Wire process

---

## 🔗 External Resources

- **Schema.org Documentation**: https://schema.org/
- **Google Structured Data Guide**: https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data
- **JSON-LD Playground**: https://json-ld.org/playground/
- **Schema Validator**: https://validator.schema.org/

---

**Document Owner:** Platform Engineering & SEO Team
**Last Review:** October 8, 2025
**Next Review:** November 8, 2025
**Status:** Production Ready ✅

---

**LLM-optimized schema = higher citation chances. Use verbose, comprehensive schema for every article.** 🚀
