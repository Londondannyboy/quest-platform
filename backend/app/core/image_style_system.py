"""
Quest Platform - Multi-Dimensional Image Styling System v1.0

Evolutionary layered system that combines:
1. Content Type (title keywords)
2. Archetype (TemplateDetector)
3. Geographic Theme (location detection)
4. Modular Blocks (FAQ, Checklist, Calculator, etc.)

Each layer adds styling attributes, building a complete style profile.
"""

# ============================================================================
# LAYER 1: CONTENT TYPE STYLES (Title Keywords)
# ============================================================================

CONTENT_TYPE_STYLES = {
    "guide": {
        "text_placement": "center",
        "text_style": "bold blocky neon text, large font, centered, authoritative",
        "text_size": "large",
        "priority": 1
    },

    "ultimate_guide": {
        "text_placement": "center",
        "text_style": "massive bold neon text, extra-large font, centered, premium authoritative",
        "text_size": "extra-large",
        "composition": "epic panoramic vista",
        "priority": 1
    },

    "essentials_guide": {
        "text_placement": "top-center",
        "text_style": "clean minimal neon text, medium font, top banner, essential focus",
        "text_size": "medium",
        "composition": "focused clean",
        "priority": 1
    },

    "listicle": {
        "text_placement": "top-left",
        "text_style": "edgy clickbait neon text, bold font, corner placement, provocative",
        "text_size": "medium",
        "composition": "dynamic energetic",
        "priority": 1
    },

    "comparison": {
        "text_placement": "center-split",
        "text_style": "versus-style neon text, bold, centered with divider, competitive",
        "text_size": "large",
        "composition": "split dual elements",
        "priority": 1
    },

    "how_to": {
        "text_placement": "top",
        "text_style": "clean instructional neon text, medium font, top banner, professional",
        "text_size": "medium",
        "composition": "sequential linear",
        "priority": 1
    },

    "checklist": {
        "text_placement": "left-align",
        "text_style": "organized list-style neon text, checkbox aesthetic, left-aligned, systematic",
        "text_size": "medium",
        "composition": "organized grid",
        "priority": 1
    },

    "faq": {
        "text_placement": "center-question",
        "text_style": "conversational Q&A neon text, question mark emphasis, approachable",
        "text_size": "medium",
        "composition": "question-answer format",
        "priority": 1
    },

    "calculator": {
        "text_placement": "center-numeric",
        "text_style": "data-driven neon text with numbers, calculator aesthetic, analytical",
        "text_size": "large",
        "composition": "numeric dashboard",
        "priority": 1
    },

    "cost_of_living": {
        "text_placement": "center-price",
        "text_style": "price-tag neon text with currency symbols, financial focus",
        "text_size": "large",
        "composition": "financial dashboard",
        "priority": 1
    },

    "shopping": {
        "text_placement": "top-right",
        "text_style": "retail neon text, shopping bag aesthetic, consumer focus",
        "text_size": "medium",
        "composition": "marketplace busy",
        "priority": 1
    },

    "news": {
        "text_placement": "bottom-banner",
        "text_style": "breaking news ticker neon text, urgent font, bottom banner, dynamic",
        "text_size": "small",
        "composition": "urgent contemporary",
        "priority": 1
    }
}

# ============================================================================
# LAYER 2: ARCHETYPE STYLES (TemplateDetector)
# ============================================================================

ARCHETYPE_STYLES = {
    "skyscraper": {
        "composition": "epic panoramic vista",
        "mood": "inspirational grand",
        "lighting": "dramatic golden hour",
        "neon_intensity": "bold vibrant",
        "priority": 2
    },

    "cluster_hub": {
        "composition": "multiple focal points",
        "mood": "comprehensive diverse",
        "lighting": "bright even",
        "neon_intensity": "medium consistent",
        "priority": 2
    },

    "deep_dive": {
        "composition": "intimate close-up detail",
        "mood": "contemplative focused",
        "lighting": "moody dramatic",
        "neon_intensity": "subtle refined",
        "priority": 2
    },

    "comparison_matrix": {
        "composition": "split dual elements",
        "mood": "analytical contrasting",
        "lighting": "day and night contrast",
        "neon_intensity": "dual-tone cyan magenta",
        "priority": 2
    },

    "news_hub": {
        "composition": "modern dynamic",
        "mood": "contemporary urgent",
        "lighting": "sharp high-contrast",
        "neon_intensity": "electric sharp",
        "priority": 2
    }
}

# ============================================================================
# LAYER 3: GEOGRAPHIC THEME STYLES (Location-Specific)
# ============================================================================

GEO_THEME_STYLES = {
    "mediterranean": {
        "color_palette": "warm terracotta, azure blue, golden yellow",
        "atmosphere": "sunny relaxed coastal",
        "priority": 3
    },

    "northern_europe": {
        "color_palette": "cool blue, gray, muted green",
        "atmosphere": "crisp modern minimalist",
        "priority": 3
    },

    "urban_tech_hub": {
        "color_palette": "electric blue, neon purple, chrome",
        "atmosphere": "modern dynamic tech",
        "priority": 3
    },

    "financial_district": {
        "color_palette": "gold, dark blue, metallic silver",
        "atmosphere": "premium authoritative wealth",
        "priority": 3
    },

    "tropical": {
        "color_palette": "vibrant green, turquoise, coral",
        "atmosphere": "lush vibrant paradise",
        "priority": 3
    }
}

# ============================================================================
# LAYER 4: MODULAR BLOCK STYLES (Content Structure)
# ============================================================================

MODULAR_BLOCK_STYLES = {
    "faq_section": {
        "content_image_style": "question mark iconography, conversational",
        "composition_override": "Q&A format",
        "priority": 4
    },

    "checklist_section": {
        "content_image_style": "checkbox aesthetics, organized list",
        "composition_override": "systematic grid",
        "priority": 4
    },

    "calculator_section": {
        "content_image_style": "numeric dashboard, data visualization",
        "composition_override": "financial calculator",
        "priority": 4
    },

    "map_section": {
        "content_image_style": "geographic map pins, navigation",
        "composition_override": "map view",
        "priority": 4
    },

    "timeline_section": {
        "content_image_style": "sequential timeline, chronological",
        "composition_override": "linear timeline",
        "priority": 4
    }
}

# ============================================================================
# DETECTION FUNCTIONS
# ============================================================================

def detect_content_type(title: str) -> str:
    """
    Detect content type from title keywords

    Priority order matters - more specific types first
    """
    title_lower = title.lower()

    # Specific types first
    if "faq" in title_lower or "questions" in title_lower:
        return "faq"
    elif "checklist" in title_lower:
        return "checklist"
    elif "calculator" in title_lower or "cost breakdown" in title_lower:
        return "calculator"
    elif "cost of living" in title_lower or "prices in" in title_lower:
        return "cost_of_living"
    elif "shopping" in title_lower or "where to buy" in title_lower:
        return "shopping"
    elif "vs" in title_lower or "versus" in title_lower:
        return "comparison"
    elif any(word in title_lower for word in ["top", "best", "worst", "cheapest", "most"]):
        return "listicle"
    elif title_lower.startswith("how to"):
        return "how_to"
    elif "ultimate guide" in title_lower:
        return "ultimate_guide"
    elif "essentials" in title_lower or "essential" in title_lower:
        return "essentials_guide"
    elif "breaking" in title_lower or "news" in title_lower:
        return "news"
    else:
        return "guide"  # Default

def detect_geographic_theme(article_title: str, article_content: str) -> str:
    """
    Detect geographic theme from location mentions
    """
    combined_text = (article_title + " " + article_content[:500]).lower()

    # Mediterranean
    med_countries = ["italy", "spain", "greece", "portugal", "croatia", "malta", "cyprus"]
    if any(country in combined_text for country in med_countries):
        return "mediterranean"

    # Northern Europe
    north_countries = ["sweden", "norway", "denmark", "finland", "iceland", "netherlands"]
    if any(country in combined_text for country in north_countries):
        return "northern_europe"

    # Tech Hubs
    tech_hubs = ["silicon valley", "san francisco", "austin", "seattle", "berlin", "london tech"]
    if any(hub in combined_text for hub in tech_hubs):
        return "urban_tech_hub"

    # Financial Districts
    finance_keywords = ["wall street", "canary wharf", "city of london", "financial district"]
    if any(keyword in combined_text for keyword in finance_keywords):
        return "financial_district"

    # Tropical
    tropical_keywords = ["bali", "thailand", "vietnam", "caribbean", "costa rica", "tropical"]
    if any(keyword in combined_text for keyword in tropical_keywords):
        return "tropical"

    return None  # No specific geo theme

def detect_modular_blocks(content: str) -> list:
    """
    Detect modular blocks in content structure
    Returns list of detected block types
    """
    blocks = []
    content_lower = content.lower()

    if "## faq" in content_lower or "frequently asked questions" in content_lower:
        blocks.append("faq_section")

    if "## checklist" in content_lower or "- [ ]" in content:
        blocks.append("checklist_section")

    if "calculator" in content_lower or "cost breakdown" in content_lower:
        blocks.append("calculator_section")

    if "## map" in content_lower or "location:" in content_lower:
        blocks.append("map_section")

    if "timeline" in content_lower or "## step 1" in content_lower:
        blocks.append("timeline_section")

    return blocks

# ============================================================================
# STYLE MERGER (Combines All Layers)
# ============================================================================

def merge_style_layers(
    content_type: str,
    archetype: str,
    geo_theme: str = None,
    modular_blocks: list = None
) -> dict:
    """
    Merge all style layers into final style profile

    Priority order (higher number = higher priority):
    1. Content Type (base layer)
    2. Archetype (content strategy)
    3. Geographic Theme (location flavor)
    4. Modular Blocks (content structure)
    """
    style = {}

    # Layer 1: Content Type (base)
    if content_type in CONTENT_TYPE_STYLES:
        style.update(CONTENT_TYPE_STYLES[content_type])

    # Layer 2: Archetype
    if archetype in ARCHETYPE_STYLES:
        style.update(ARCHETYPE_STYLES[archetype])

    # Layer 3: Geographic Theme
    if geo_theme and geo_theme in GEO_THEME_STYLES:
        style.update(GEO_THEME_STYLES[geo_theme])

    # Layer 4: Modular Blocks (highest priority)
    if modular_blocks:
        for block in modular_blocks:
            if block in MODULAR_BLOCK_STYLES:
                style.update(MODULAR_BLOCK_STYLES[block])

    return style

# ============================================================================
# PROMPT BUILDER (Uses Style Profile)
# ============================================================================

def build_image_prompt(
    landmark: str,
    title: str,
    style: dict,
    time_of_day: str = "golden hour"
) -> str:
    """
    Build final image prompt from style profile
    """
    prompt = f"""{landmark} at {time_of_day},
{style.get('composition', 'standard composition')},
{style.get('mood', 'aspirational')} atmosphere,
{style.get('lighting', 'natural professional lighting')},
{style.get('color_palette', 'vibrant neon colors')},
with {style.get('text_style', 'bold neon text')}: "{title}".

Text placement: {style.get('text_placement', 'center')}
Text should be {style.get('text_size', 'large')} and clearly readable.
Neon intensity: {style.get('neon_intensity', 'medium vibrant')}

Do not include any other text in the image."""

    return prompt
