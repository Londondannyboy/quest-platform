# Technical SEO Fundamentals for AI Crawlers

**Version:** 2.3.1
**Date:** October 8, 2025
**Source:** Nathan Gotch AI SEO Insights
**Status:** Production Checklist

---

## 🎯 Overview

AI crawlers (ChatGPT, Perplexity, Claude, Google AI) have **zero tolerance** for technical issues. This guide ensures your site is crawlable, fast, and AI-friendly.

**Critical Insight from Nathan Gotch:**
> "AI platforms like ChatGPT do not render JavaScript very well. They'll ignore your website in favor of one that's easier to crawl and understand."

**Key Principles:**
1. **Crawlability:** AI bots must be able to access your content
2. **HTML-First:** Use HTML, not JavaScript frameworks
3. **Speed:** < 2.5 seconds page load (AI crawlers are intolerant)
4. **Mobile-Friendly:** Responsive design is non-negotiable
5. **Indexability:** Verify Google can index your pages

---

## 📋 Pre-Launch SEO Checklist

### **1. Crawlability Verification**

**Step 1: Check robots.txt**
```bash
# Visit your robots.txt file
https://relocation.quest/robots.txt

# Verify it allows crawlers
User-agent: *
Allow: /

# ❌ COMMON ERROR: Disallow blocks all crawlers
User-agent: *
Disallow: /  # THIS WILL KILL YOUR SEO!

# ✅ CORRECT: Allow all (or specific pages)
User-agent: *
Allow: /
```

**Step 2: Site Indexing Test**
```bash
# Google search
site:relocation.quest

# Expected: All your pages show up
# If pages are missing, check robots.txt and meta robots tags
```

**Step 3: Meta Robots Check**
```html
<!-- ❌ WRONG: Blocks indexing -->
<meta name="robots" content="noindex, nofollow">

<!-- ✅ CORRECT: Allows indexing -->
<meta name="robots" content="index, follow">

<!-- OR omit entirely (defaults to index, follow) -->
```

---

### **2. HTML vs JavaScript (CRITICAL)**

**Why This Matters:**
- **HTML:** AI crawlers can read immediately
- **JavaScript:** Most AI crawlers don't render JS well (or at all)
- **Result:** JS sites get ignored in favor of HTML competitors

**Quest Platform Status:**
- ✅ **Astro 4.x** - HTML-first by default
- ✅ **Static generation** - Pre-rendered HTML at build time
- ✅ **No client-side rendering** - Content available immediately

**Other Platforms:**

| Platform | HTML-First? | AI-Friendly? | Notes |
|----------|-------------|--------------|-------|
| **Astro** | ✅ Yes | ✅ Excellent | Static HTML generation |
| **WordPress** | ✅ Yes | ✅ Excellent | Server-rendered HTML |
| **Webflow** | ✅ Yes | ✅ Good | HTML output |
| **Next.js (SSG)** | ✅ Yes | ✅ Excellent | Static generation mode |
| **Next.js (CSR)** | ❌ No | ❌ Poor | Client-side rendering |
| **Lovable** | ❌ No | ❌ Poor | JS-heavy no-code tool |
| **Replit** | ❌ No | ❌ Poor | JS frameworks |
| **React (SPA)** | ❌ No | ❌ Poor | Client-side only |

**How to Verify Your Site:**
```bash
# Disable JavaScript in browser
# Chrome: DevTools → Cmd+Shift+P → "Disable JavaScript"

# Reload your page
# Can you see the content?
# ✅ YES = HTML-first (good for AI)
# ❌ NO = JS-required (bad for AI)
```

---

### **3. Page Speed Optimization**

**Target: < 2.5 Seconds (p95)**

**Why It Matters:**
- AI crawlers prioritize fast sites
- 1 second delay = 7% decrease in conversions
- Google's AI Overviews favor fast pages

**Measurement Tools:**
```bash
# Google PageSpeed Insights
https://pagespeed.web.dev/

# Target Scores:
- Performance: > 90
- LCP (Largest Contentful Paint): < 2.5s
- FID (First Input Delay): < 100ms
- CLS (Cumulative Layout Shift): < 0.1
```

**Optimization Checklist:**

**Images (Julian Goldie: < 150KB target):**
- [ ] Use WebP format (60-80% smaller than JPEG)
- [ ] Lazy load images below the fold
- [ ] Cloudinary auto-optimization enabled
- [ ] Responsive images with srcset
- [ ] Compress images (target: **< 150KB each** per Julian Goldie)
- [ ] Quality: 85 (balance size vs appearance)
- [ ] Dimensions: Max 1200×630 for hero images

**Code:**
- [ ] Minify CSS and JavaScript
- [ ] Remove unused CSS (PurgeCSS)
- [ ] Bundle and compress assets
- [ ] Use code splitting (load only what's needed)

**Fonts:**
- [ ] Use system fonts OR
- [ ] Self-host Google Fonts (avoid external requests)
- [ ] Use font-display: swap
- [ ] Subset fonts (include only needed characters)

**Caching:**
- [ ] Enable browser caching (1 year for static assets)
- [ ] Use CDN (Vercel, Cloudinary)
- [ ] Enable gzip/brotli compression

**Server:**
- [ ] Use Vercel Edge Network (automatic)
- [ ] Enable HTTP/2 or HTTP/3
- [ ] Minimize redirects (each adds latency)

**Astro-Specific (Julian Goldie Image Optimization):**
```javascript
// astro.config.mjs
import { defineConfig } from 'astro/config';
import { squooshImageService } from 'astro/assets';

export default defineConfig({
  build: {
    inlineStylesheets: 'auto', // Inline critical CSS
  },
  image: {
    service: squooshImageService(), // Optimize images at build
    // Julian Goldie recommendations
    formats: ['webp'], // WebP format
    quality: 85, // Balance quality vs size
  },
  vite: {
    build: {
      cssCodeSplit: true, // Split CSS per page
      minify: 'terser', // Aggressive minification
    },
  },
});
```

**Astro Image Component (Julian Goldie Optimized):**
```astro
---
import { Image } from 'astro:assets';
import heroImage from '../assets/hero.jpg';
---

<!-- Julian Goldie: WebP, quality 85, lazy loading, < 150KB -->
<Image
  src={heroImage}
  alt="Portugal Digital Nomad Visa Guide"
  format="webp"
  quality={85}
  loading="lazy"
  width={1200}
  height={630}
/>

<!-- Result: Optimized image < 150KB, fast loading -->
```

---

### **4. Mobile Responsiveness**

**Why It Matters:**
- Google uses mobile-first indexing
- Most AI searches happen on mobile
- Responsive design is ranking factor

**Testing:**
```bash
# Google Mobile-Friendly Test
https://search.google.com/test/mobile-friendly

# Expected: "Page is mobile-friendly"
```

**Checklist:**
- [ ] Viewport meta tag present
- [ ] Text readable without zooming (min 16px)
- [ ] Touch targets at least 48x48px
- [ ] No horizontal scrolling
- [ ] Fast mobile load time (< 3s)

**Astro Implementation:**
```html
<!-- layouts/BaseLayout.astro -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<!-- Tailwind CSS responsive design -->
<div class="container mx-auto px-4 sm:px-6 lg:px-8">
  <h1 class="text-2xl sm:text-3xl lg:text-4xl">
    <!-- Auto-scales on mobile -->
  </h1>
</div>
```

---

### **5. Indexing Verification**

**Google Search Console Setup:**
```bash
1. Go to https://search.google.com/search-console
2. Add property (relocation.quest, placement.quest, rainmaker.quest)
3. Verify ownership (DNS or HTML file)
4. Submit sitemap (https://relocation.quest/sitemap.xml)
5. Monitor coverage report
```

**Sitemap Requirements:**
```xml
<!-- public/sitemap.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <!-- Articles -->
  <url>
    <loc>https://relocation.quest/portugal-digital-nomad-visa</loc>
    <lastmod>2025-10-08</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>

  <!-- PDFs -->
  <url>
    <loc>https://res.cloudinary.com/.../portugal-nomad-visa.pdf</loc>
    <lastmod>2025-10-08</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
</urlset>
```

**Astro Sitemap Plugin:**
```javascript
// astro.config.mjs
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://relocation.quest',
  integrations: [
    sitemap({
      filter: (page) => !page.includes('/admin'), // Exclude admin pages
      changefreq: 'monthly',
      priority: 0.8,
    }),
  ],
});
```

---

## 🚨 Common Technical Issues

### **Issue 1: Slow Page Speed**

**Symptoms:**
- PageSpeed score < 70
- LCP > 2.5 seconds
- Pages feel sluggish

**Diagnosis:**
```bash
# Run PageSpeed Insights
https://pagespeed.web.dev/

# Look for:
- Large images (> 200KB)
- Render-blocking resources
- Unused CSS/JavaScript
- Slow server response
```

**Fix:**
1. Compress images (WebP format)
2. Enable lazy loading
3. Inline critical CSS
4. Defer non-critical JavaScript
5. Use CDN (Vercel/Cloudinary)

---

### **Issue 2: Robots.txt Blocking**

**Symptoms:**
- `site:` search shows no results
- Google Search Console shows "Blocked by robots.txt"
- AI crawlers not finding content

**Diagnosis:**
```bash
# Check robots.txt
curl https://relocation.quest/robots.txt

# Look for "Disallow: /"
```

**Fix:**
```txt
# ✅ CORRECT robots.txt
User-agent: *
Allow: /

# Block only admin areas
User-agent: *
Disallow: /admin/
Disallow: /api/

Sitemap: https://relocation.quest/sitemap.xml
```

---

### **Issue 3: JavaScript-Heavy Site**

**Symptoms:**
- Content not visible with JS disabled
- AI crawlers ignoring your site
- Competitors ranking instead

**Diagnosis:**
```bash
# Disable JavaScript in browser
# Reload page
# Can you see content?
```

**Fix:**
- **Option 1:** Rebuild with HTML-first framework (Astro, Next.js SSG)
- **Option 2:** Add server-side rendering (SSR)
- **Option 3:** Use static site generation (SSG)

**Quest Platform:** Already using Astro (HTML-first) ✅

---

### **Issue 4: Mobile Unfriendly**

**Symptoms:**
- Google warns "Not mobile-friendly"
- Text too small to read
- Buttons too small to tap
- Horizontal scrolling required

**Fix:**
```html
<!-- Add viewport meta tag -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<!-- Use responsive CSS -->
<style>
  body {
    font-size: 16px; /* Minimum for readability */
  }

  button {
    min-width: 48px;  /* Minimum touch target */
    min-height: 48px;
  }

  img {
    max-width: 100%; /* Prevent horizontal scroll */
    height: auto;
  }
</style>
```

---

## ✅ Pre-Launch Checklist

Run this checklist **before every site launch:**

### **Crawlability:**
- [ ] robots.txt allows crawlers
- [ ] No meta robots noindex tags
- [ ] Sitemap generated and submitted
- [ ] All pages show in `site:` search

### **Performance:**
- [ ] PageSpeed score > 90
- [ ] LCP < 2.5 seconds
- [ ] Images compressed (< 200KB)
- [ ] CSS/JS minified
- [ ] CDN enabled

### **HTML-First:**
- [ ] Content visible with JS disabled
- [ ] Using HTML-first framework (Astro)
- [ ] No client-side rendering for content

### **Mobile:**
- [ ] Viewport meta tag present
- [ ] Mobile-friendly test passes
- [ ] Text readable (min 16px)
- [ ] Touch targets > 48px

### **Indexing:**
- [ ] Google Search Console verified
- [ ] Sitemap submitted
- [ ] No indexing errors
- [ ] Coverage report shows pages indexed

---

## 📊 Monitoring and Maintenance

**Weekly Checks:**
- [ ] PageSpeed Insights (performance trends)
- [ ] Google Search Console (indexing status)
- [ ] Site search (verify pages appear)

**Monthly Checks:**
- [ ] Technical SEO audit (Screaming Frog or similar)
- [ ] Mobile-friendly test
- [ ] Broken link check
- [ ] Sitemap validation

**Quarterly Checks:**
- [ ] Full performance audit
- [ ] Competitor technical analysis
- [ ] Update technical SEO best practices

---

## 🔗 Tools and Resources

**Testing Tools:**
- PageSpeed Insights: https://pagespeed.web.dev/
- Mobile-Friendly Test: https://search.google.com/test/mobile-friendly
- Google Search Console: https://search.google.com/search-console
- GTmetrix: https://gtmetrix.com/

**Technical Audit:**
- Screaming Frog: https://www.screamingfrog.co.uk/
- Ahrefs Site Audit: https://ahrefs.com/site-audit
- Semrush Site Audit: https://www.semrush.com/

**Performance:**
- WebPageTest: https://www.webpagetest.org/
- Lighthouse: Built into Chrome DevTools

---

## 📚 Related Documentation

- [LLM Optimization Guide](./LLM-OPTIMIZATION.md) - Complete AI SEO strategy
- [JSON Schema Guide](./JSON-SCHEMA-GUIDE.md) - Schema optimization
- [PDF Strategy](./PDF-STRATEGY.md) - PDF generation for LLM SEO
- [Topic Domination](./TOPIC-DOMINATION.md) - Content volume strategy

---

**Document Owner:** Platform Engineering & SEO Team
**Last Review:** October 8, 2025
**Next Review:** November 8, 2025
**Status:** Production Checklist ✅

---

**Technical excellence = AI crawler happiness. Fix the foundation before optimizing content.** 🚀
