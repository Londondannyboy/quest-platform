# Quest Platform - Image Generation Guidelines

**Authority Document:** QUEST_IMAGE_GUIDELINES.md
**Last Updated:** October 11, 2025
**Version:** 1.0
**Applies To:** All Quest sites (relocation, placement, rainmaker)

---

## 📐 Core Philosophy

### ASPIRATION > DOCUMENTATION

Images must evoke **desire, emotion, and FOMO**, not process documentation.

**✅ CORRECT (Aspirational):**
- Colosseum at golden hour with dramatic lighting
- Paphos harbor at night with neon reflections
- Paris café terrace with Eiffel Tower in background
- Venice canal with gondola at dusk

**❌ WRONG (Process):**
- Person filling out visa application
- Someone handing documents to immigration officer
- Business person at desk with laptop
- Generic office meeting

**Why Aspiration Matters:**
- Triggers emotional connection (desire, wanderlust, ambition)
- Creates fear of missing out (FOMO)
- Inspires action (visa application, relocation, career move)
- Elevates brand perception (premium, authoritative)

---

## 🎯 Image Strategy: H2 Overlay System

### Overview

Each article generates **4 themed images** with contextual H2 overlays:
1. **Hero**: 3:1 ultra-wide banner with article title overlay
2. **Content 1-3**: 16:9 images with H2 section headings as overlays

### Why H2 Overlays?

**Benefits:**
- **Contextual**: Image matches section content
- **Navigational**: Reader knows what section they're in
- **Branded**: Consistent neon aesthetic throughout article
- **Mobile-friendly**: 1-click access to section content
- **SEO**: Alt text matches H2 headings for better indexing

### Example: Italy Digital Nomad Visa

```
Article: "Italy Digital Nomad Visa Complete Guide 2025"

Hero Image (3:1):
- Title Overlay: "Italy Digital Nomad Visa Complete Guide 2025"
- Location: Colosseum at golden hour
- Neon Style: Vibrant cyan/magenta glow

Content Image 1 (16:9):
- H2 Overlay: "Visa Requirements and Eligibility"
- Location: Venice canals at dusk
- Neon Style: Subtle purple/blue glow

Content Image 2 (16:9):
- H2 Overlay: "Application Process Step-by-Step"
- Location: Florence Duomo at sunset
- Neon Style: Warm pink/orange glow

Content Image 3 (16:9):
- H2 Overlay: "Living Costs in Italy"
- Location: Amalfi Coast village at twilight
- Neon Style: Cool teal/cyan glow
```

---

## 🚫 Absolute Rules

### Rule 1: Text Overlay Policy

**REQUESTED text overlays are REQUIRED:**
- Article title on hero image
- H2 section headings on content images
- Neon aesthetic (translucent overlay with glow)

**UNWANTED text is FORBIDDEN:**
- Random words or labels
- Watermarks or logos
- Street signs or building text
- UI elements or buttons

**Negative Prompt (Always Include):**
```
"unwanted text, random words, watermark, logo, unrelated typography,
low quality, blurry, distorted, amateur"
```

**Example Prompts:**

✅ **CORRECT:**
```
"Paphos harbor in Cyprus at night with neon overlay text:
'Cyprus Digital Nomad Visa Requirements'.
Do not include any other text in the image."
```

❌ **WRONG:**
```
"Paphos harbor in Cyprus at night"
(Missing overlay text instruction)
```

### Rule 2: Neon Aesthetic Consistency

**Brand Identity:**
- Subtle neon outline glow on key subjects
- Glowing edges and rim lighting
- Cyberpunk-inspired lighting accents
- Modern futuristic aesthetic
- **NOT** dominant or overwhelming

**Color Palette:**
- Primary: Cyan, magenta, purple
- Secondary: Teal, pink, orange
- Accent: Electric blue, neon green

**Application:**
- Text overlays: Neon glow with translucency
- Subject highlights: Rim lighting on buildings/landmarks
- Reflections: Water reflections of neon lights
- Atmosphere: Futuristic edge to aspirational scenes

### Rule 3: Themed Sequential Images

**Strategy:** Each article follows a GEOGRAPHIC or CONTEXTUAL theme with iconic landmarks ranked by recognition.

**Process:**

1. **Identify Theme** (from article topic)
   - Country article → Famous landmarks in that country
   - City article → Iconic locations in that city
   - Finance article → Financial hubs (London, NYC, Singapore)
   - Career article → Tech hubs (San Francisco, Austin, Berlin)

2. **Landmark Hierarchy** (Phase 2 - TODO)
   - Query Perplexity: "Most iconic landmarks in [Country], ranked"
   - Returns 5-10 ranked results
   - Select top 4 for images

3. **Map Landmarks to Images**
   - Hero: #1 landmark (most iconic) + article title
   - Content 1: #2 landmark + H2 section 1
   - Content 2: #3 landmark + H2 section 2
   - Content 3: #4 landmark + H2 section 3

**Current Implementation:**
- **Phase 1 (LIVE):** Uses generic "scenic location related to {topic}"
- **Phase 2 (READY):** Hardcoded landmark mappings in `landmark_mappings.json`
  - No API costs (one-time manual curation)
  - Covers all European countries + major capitals
  - Curated for aspirational value (not just "most famous")

---

## 🔧 Technical Specifications

### Model: Ideogram V2 Turbo

**Why Ideogram over FLUX?**
- ✅ **Better text rendering**: Clean, readable neon overlays
- ✅ **Magic prompt support**: Enhances simple prompts 6x
- ✅ **Faster generation**: ~7 seconds (vs 30-60s for FLUX)
- ✅ **Photorealistic**: High-quality aspirational scenes
- ⚠️ **Slightly more expensive**: $0.004 vs $0.003 per image

**API Configuration:**
```python
output = await replicate.async_run(
    "ideogram-ai/ideogram-v2-turbo",
    input={
        "prompt": prompt,  # Simple prompt (magic prompt enhances)
        "aspect_ratio": "3:1" or "16:9",
        "magic_prompt_option": "On",  # REQUIRED
        "style_type": "None",  # Photorealistic
        "style_preset": "None",
    },
)
```

### Aspect Ratios

**Hero Image: 3:1 Ultra-Wide Banner**
- Dimensions: 2048x683 (higher resolution 3:1 ratio, for premium quality)
- Use Case: Above-the-fold hero banner, search result preview, social sharing
- Mobile: Crops to center, title remains readable
- Desktop: Full ultra-wide cinematic look
- **Purpose:** Click-through optimization (CTR), not just aesthetics
- **Style:** Experimental, dynamic, people-focused when relevant

**Content Images: 16:9 Standard**
- Dimensions: 1920x1080 (Full HD)
- Use Case: In-content section images
- Mobile: Scales down proportionally
- Desktop: High-resolution display

### Cloudinary Transformations

**Hero Image:**
```python
transformation=[
    {"width": 1344, "crop": "limit"},  # Preserve 3:1 aspect ratio
    {"quality": "auto:best"},  # Highest quality
    {"fetch_format": "auto"},  # WebP for modern browsers
]
```

**Content Images:**
```python
transformation=[
    {"width": 1920, "crop": "limit"},  # Preserve 16:9 aspect ratio
    {"quality": "auto:good"},  # Standard quality
    {"fetch_format": "auto"},  # WebP for modern browsers
]
```

**Responsive URLs:**
- Cloudinary auto-transforms based on device
- Mobile: 800px width
- Tablet: 1200px width
- Desktop: 1920px width (full resolution)

---

## 📝 Prompt Engineering

### Text Overlay Styling by Article Type ✅ IMPLEMENTED

**Strategy:** Different article types use different text placement and styling for maximum CTR.

**Article Type Detection:**
```python
# Simple keyword-based detection from title
- "Italy vs Spain" → comparison
- "Top 10 Cities" → listicle
- "How to Apply" → how_to
- "Italy Digital Nomad Visa Complete Guide" → guide (default)
```

**Text Overlay Styles:**

| Article Type | Placement | Style | Use Case |
|---|---|---|---|
| **Guide** | Center | Bold, blocky, authoritative | Country guides, comprehensive content |
| **Listicle** | Top-left corner | Edgy, clickbait, provocative | Top 10, Best/Worst lists |
| **How-To** | Top banner | Clean, instructional, professional | Step-by-step guides |
| **Comparison** | Center split | Versus-style, competitive | Spain vs Portugal, A vs B |
| **News** | Bottom banner | Urgent, breaking news ticker | Updates, breaking news |

**Visual Examples:**

**Guide (Center, Bold):**
```
┌─────────────────────────┐
│   [Landmark Image]      │
│  ╔═════════════════╗    │  ← Center, authoritative
│  ║ ITALY DIGITAL   ║    │
│  ║ NOMAD VISA      ║    │
│  ╚═════════════════╝    │
└─────────────────────────┘
```

**Listicle (Corner, Edgy):**
```
┌─────────────────────────┐
│ ┏━━━━━━━━━━━━━┓        │  ← Top-left, clickbait
│ ┃ TOP 10 CITIES┃        │
│ ┗━━━━━━━━━━━━━┛        │
│   [Dynamic Scene]       │
└─────────────────────────┘
```

### Hero Image Composition (CTR-Optimized)

**Goal: Maximize click-through rate, not just visual appeal**

**What Works (Based on Italy Example):**
- ✅ **People in the scene** - 2-3 people looking aspirational/successful
- ✅ **Golden hour lighting** - Emotional warmth, FOMO trigger
- ✅ **Neon/vibrant aesthetic** - Eye-catching, modern, stands out in search results
- ✅ **City skyline context** - Shows location without being literal landmark photo
- ✅ **Dynamic composition** - People in foreground, cityscape background, depth
- ✅ **Text overlay prominent** - Title clearly readable on both desktop and mobile

**What to Avoid:**
- ❌ Static landmark photos (boring, low CTR)
- ❌ Empty scenes with no people (lacks human connection)
- ❌ Overly literal interpretations (visa document close-ups)
- ❌ Dark/moody lighting (reduces CTR)
- ❌ Text too small or hard to read

**Hero Prompt Template (People-Focused):**
```
"Two digital nomads with backpacks overlooking [landmark] in [location] at golden hour,
vibrant neon aesthetic, cinematic composition with city skyline in background,
with neon overlay text: '{title}'. Do not include any other text."
```

**Example:**
```
"Two digital nomads with backpacks overlooking Florence cityscape at golden hour,
vibrant neon aesthetic with rim lighting, cinematic depth with Duomo in background,
with bold neon overlay text: 'Italy Digital Nomad Visa Complete Guide 2025'.
Do not include any other text."
```

**Content Images: Landmark-Focused**
- Can be more literal (landmark close-ups work here)
- People optional (depends on H2 context)
- Still maintain neon aesthetic for brand consistency

### Magic Prompt Strategy

**Simple Input → Enhanced Output**

Ideogram's magic prompt enhances simple descriptions into detailed, atmospheric prompts.

**Example:**

**Input (Simple):**
```
"Paphos harbor in Cyprus at night with neon overlay text:
'Cyprus Digital Nomad Visa Requirements'.
Do not include any other text in the image."
```

**Magic Prompt Output (Enhanced):**
```
"A cinematic photograph of Paphos harbor in Cyprus at night, featuring
a picturesque view of the calm, reflective water and traditional stone
buildings. One building is dramatically illuminated with vibrant neon lights,
displaying 'Cyprus Digital Nomad Visa Requirements' in a bold, modern font
as a translucent overlay. Soft, ambient light from nearby harbor lamps
reflects on the water, creating subtle ripples, and the distant sky is a
deep indigo with a scattering of stars. The overall atmosphere is serene
and inviting, with a touch of mystery and modern flair from the neon signage."
```

**6x More Descriptive!**

### Prompt Template

```python
# Hero Image (3:1)
f"""Scenic location related to {topic} at {time_of_day} with neon overlay text: "{title}".

Do not include any other text in the image."""

# Content Images (16:9)
f"""Scenic location related to {topic} at {time_of_day} with neon overlay text: "{h2_heading}".

Do not include any other text in the image."""
```

**What to Specify:**
- ✅ Location/topic context
- ✅ Time of day (golden hour, dusk, sunset, twilight)
- ✅ Requested overlay text (title or H2)
- ✅ "Do not include any other text" (critical)

**What NOT to Specify:**
- ❌ Detailed scene descriptions (magic prompt handles this)
- ❌ Lighting details (magic prompt adds cinematic lighting)
- ❌ Composition guidance (magic prompt optimizes framing)
- ❌ Style adjectives (magic prompt adds atmosphere)

### Time of Day Variations

**For visual diversity, rotate through:**
```python
TIMES_OF_DAY = ["golden hour", "dusk", "sunset", "twilight"]
```

**Hero**: Always "golden hour" (most iconic)
**Content 1**: "dusk"
**Content 2**: "sunset"
**Content 3**: "twilight"

---

## 🗄️ Image Reusability (Phase 3 - TODO)

### Alt Text Database

**Purpose:**
1. **SEO**: Indexable image descriptions
2. **Accessibility**: Screen reader support
3. **Reusability**: Search and reuse images across articles
4. **Cost Savings**: Avoid regenerating similar images

### Database Schema

```sql
CREATE TABLE image_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cloudinary_url TEXT NOT NULL UNIQUE,
    alt_text TEXT NOT NULL,
    description TEXT,

    -- Thematic categorization
    theme VARCHAR(100),  -- 'italy', 'paris', 'finance', etc.
    landmark VARCHAR(200),  -- 'Colosseum', 'Eiffel Tower', etc.
    h2_text TEXT,  -- H2 overlay text (NULL for hero)

    -- Visual attributes
    time_of_day VARCHAR(50),  -- 'golden hour', 'sunset', 'night'
    aspect_ratio VARCHAR(10),  -- '3:1', '16:9'
    has_text_overlay BOOLEAN DEFAULT true,

    -- Reusability tracking
    usage_count INTEGER DEFAULT 1,
    last_used_at TIMESTAMPTZ,

    -- Search optimization
    keywords TEXT[],
    embedding VECTOR(1536),  -- For semantic search

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_image_theme ON image_library(theme);
CREATE INDEX idx_image_landmark ON image_library(landmark);
CREATE INDEX idx_image_h2 ON image_library(h2_text);
CREATE INDEX idx_image_embedding ON image_library USING ivfflat (embedding);
```

### Reuse Strategy

**Before Generating New Image:**
```python
# Check for existing match
existing = await db.fetch_one("""
    SELECT cloudinary_url
    FROM image_library
    WHERE theme = $1
    AND landmark = $2
    AND h2_text = $3
    AND aspect_ratio = $4
""", theme, landmark, h2_text, aspect_ratio)

if existing:
    # Reuse existing image
    await db.execute("""
        UPDATE image_library
        SET usage_count = usage_count + 1,
            last_used_at = NOW()
        WHERE cloudinary_url = $1
    """, existing['cloudinary_url'])

    return existing['cloudinary_url']  # Cost savings: $0.004
else:
    # Generate new image
    url = await generate_via_ideogram(prompt)
    await save_to_library(url, alt_text, metadata)
    return url
```

**Expected Reuse Rate:**
- Italy articles: 60-70% (limited landmarks)
- General topics: 20-30% (more variety)
- **Cost Savings**: $0.02-$0.03 per article on average

---

## 📊 Cost Analysis

### Per Article Cost

```python
COST_BREAKDOWN = {
    "hero_image": 0.004,  # 3:1 Ideogram V2 Turbo
    "content_1": 0.004,   # 16:9 Ideogram V2 Turbo
    "content_2": 0.004,   # 16:9 Ideogram V2 Turbo
    "content_3": 0.004,   # 16:9 Ideogram V2 Turbo
    "total": 0.016        # 4 images total
}
```

**With 50% Reuse (Phase 3):**
```python
OPTIMIZED_COST = {
    "new_images": 0.008,  # 2 images × $0.004
    "reused_images": 0.00,  # 2 images reused (free)
    "total": 0.008        # 50% savings
}
```

**Monthly Cost (1000 articles/month):**
- Current (Phase 1): $16/month
- Optimized (Phase 3): $8/month with reuse
- vs FLUX: $12/month (but worse text rendering)

---

## 🎨 Site-Specific Styles

### relocation.quest
**Theme**: International travel, visa/immigration, expat lifestyle
**Style**: "Modern professional international cityscape with subtle neon outline glow accents"
**Landmarks**: Country-specific (Colosseum, Eiffel Tower, etc.)
**Mood**: Aspirational wanderlust, FOMO, desire for adventure

### placement.quest (Future)
**Theme**: Career development, job search, professional growth
**Style**: "Professional office data visualization with neon outline highlighting"
**Landmarks**: Tech hubs (Silicon Valley, Austin, Berlin, London)
**Mood**: Career aspiration, success imagery, ambition

### rainmaker.quest (Future)
**Theme**: Entrepreneurship, revenue generation, business growth
**Style**: "Entrepreneurial dynamic aspirational scene with premium neon accents"
**Landmarks**: Financial districts (Wall Street, Canary Wharf, Singapore Marina Bay)
**Mood**: Wealth indicators, luxury lifestyle, business success

---

## 🚀 Implementation Checklist

### Phase 1: H2 Overlay System ✅ COMPLETE
- [x] Switch from FLUX to Ideogram V2 Turbo
- [x] Add H2 extraction from article content
- [x] Generate prompts with H2 overlay text
- [x] Support 3:1 (hero) and 16:9 (content) aspect ratios
- [x] Update Cloudinary transformations
- [x] Deploy to production

### Phase 2: Themed Landmark Detection (READY - Not Yet Integrated)
- [x] Create `landmark_mappings.json` with 12 European countries
- [ ] Add `_load_landmark_mappings()` method in ImageAgent
- [ ] Add `_detect_country_from_title()` method
- [ ] Update `_create_all_prompts()` to use specific landmarks
- [ ] Test with Italy article (Colosseum, Venice, Florence, Amalfi)
- [ ] Expand mappings to 50+ countries (via Claude Desktop/Perplexity)

### Phase 3: Image Reusability (TODO)
- [ ] Create `image_library` database table
- [ ] Add alt text generation method
- [ ] Implement reuse check before generation
- [ ] Save metadata after image upload
- [ ] Track usage count and cost savings

### Phase 4: Quality Improvements (TODO)
- [ ] A/B test different neon styles
- [ ] Optimize prompt templates per site
- [ ] Add landmark diversity scoring
- [ ] Implement image quality validation
- [ ] Monitor Cloudinary bandwidth usage

---

## 📖 Documentation Cross-References

**Read These First:**
- `QUEST_CONTENT_PUBLISHING_GUIDELINES.md` - Content quality standards
- `QUEST_ARCHITECTURE.md` - System design and agent pipeline

**Related Documents:**
- `CLAUDE.md` - Technical implementation details
- `QUEST_TRACKER.md` - Progress tracking and metrics

**ImageAgent Code:**
- `backend/app/agents/image.py` - Main implementation
- `backend/app/agents/orchestrator.py` - Pipeline integration

---

## 📍 Expanding Landmark Mappings

### Current Coverage (12 Countries)

**European Countries:**
- Italy, Spain, Portugal, France, Greece
- Cyprus, Croatia, Malta
- Germany, Netherlands, United Kingdom, Ireland

### How to Add New Countries

**Using Claude Desktop or Perplexity (One-Time):**

1. **Query Template:**
```
"List the 4 most iconic, aspirational landmarks for [Country].
Format: Name, Location, Brief Description.
Prioritize visual appeal and emotional resonance over pure fame."
```

2. **Manual Curation:**
- Review results for aspirational value
- Ensure diversity (not all same city)
- Check image searchability (can Ideogram generate this?)
- Rank by emotional impact (FOMO factor)

3. **Add to JSON:**
```json
"[country_slug]": {
  "country": "[Country Name]",
  "landmarks": [
    {
      "name": "[Landmark Name]",
      "location": "[City/Region]",
      "rank": 1,
      "description": "[Brief description]"
    },
    ...
  ]
}
```

### Expansion Priorities

**Phase 2A (Next 20 Countries):**
- Rest of Europe: Poland, Czech Republic, Austria, Switzerland, Belgium, Denmark, Sweden, Norway, Finland, Iceland
- Popular nomad destinations: Thailand, Indonesia, Vietnam, Philippines, Taiwan, Japan, South Korea, Singapore, Malaysia, UAE

**Phase 2B (Next 20 Countries):**
- Americas: USA, Canada, Mexico, Colombia, Costa Rica, Argentina, Chile, Brazil
- Oceania: Australia, New Zealand
- Africa: South Africa, Morocco, Kenya, Tanzania
- Additional Asia: India, Sri Lanka, Nepal, Georgia, Turkey

**Total Target: 50+ Countries** (covers 95% of digital nomad destinations)

**Estimated Time:**
- 10 minutes per country (query + curate + add to JSON)
- 50 countries × 10 min = 500 minutes (~8 hours total)
- Can be done incrementally as articles are written

---

## 🐛 Troubleshooting

### Issue: Text overlay not rendering
**Cause**: Magic prompt might be filtering out text request
**Fix**: Make text overlay instruction more explicit:
```python
"...with bold neon overlay text displaying: '{text}'.
The text MUST be visible and readable."
```

### Issue: Wrong aspect ratio
**Cause**: Ideogram API parameter incorrect
**Fix**: Verify `aspect_ratio` parameter matches expected:
- Hero: `"3:1"` (not `"3/1"` or `"3-1"`)
- Content: `"16:9"` (not `"16/9"` or `"1920x1080"`)

### Issue: Image quality too low
**Cause**: Cloudinary transformation too aggressive
**Fix**: Increase quality setting in `_upload_to_cloudinary()`:
```python
{"quality": "auto:best"}  # Instead of "auto:good"
```

### Issue: H2 extraction returns empty list
**Cause**: Article content doesn't have H2 headings
**Fix**: Check markdown format - ensure headings use `## ` (not `**bold**`)

### Issue: Cloudinary timeout
**Cause**: Large image upload exceeds 5-second timeout
**Fix**: Increase timeout in `_upload_to_cloudinary()`:
```python
timeout=10  # Instead of 5
```

---

**Last Updated:** October 11, 2025
**Version:** 1.0
**Status:** Phase 1 Complete, Phase 2-4 Planned
**Authority:** This document supersedes all previous image generation guidelines

