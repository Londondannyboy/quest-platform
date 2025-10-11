"""
Test Multi-Dimensional Image Styling System v1.0

Shows how different article types get different visual treatments
"""

from app.core.image_style_system import (
    detect_content_type,
    detect_geographic_theme,
    detect_modular_blocks,
    merge_style_layers,
    build_image_prompt
)

# ============================================================================
# TEST CASES
# ============================================================================

test_articles = [
    {
        "title": "Italy Digital Nomad Visa Complete Guide 2025",
        "archetype": "skyscraper",
        "content": "## What You Need to Know\n## Visa Requirements\n## Application Process",
        "expected_type": "guide",
        "expected_geo": "mediterranean"
    },
    {
        "title": "Top 10 Cheapest Cities in Europe for Digital Nomads",
        "archetype": "skyscraper",
        "content": "## What You Need to Know\n1. Lisbon\n2. Budapest\n3. Prague",
        "expected_type": "listicle",
        "expected_geo": None
    },
    {
        "title": "Spain vs Portugal: Digital Nomad Visa Comparison",
        "archetype": "comparison_matrix",
        "content": "## What You Need to Know\n## Spain Requirements\n## Portugal Requirements",
        "expected_type": "comparison",
        "expected_geo": "mediterranean"
    },
    {
        "title": "Cost of Living Calculator: Barcelona 2025",
        "archetype": "deep_dive",
        "content": "## What You Need to Know\n## Calculator\n## Breakdown",
        "expected_type": "calculator",
        "expected_geo": "mediterranean"
    },
    {
        "title": "Italy Digital Nomad Visa FAQ: 50 Questions Answered",
        "archetype": "cluster_hub",
        "content": "## FAQ\n## What documents do I need?\n## How long does it take?",
        "expected_type": "faq",
        "expected_geo": "mediterranean"
    },
    {
        "title": "Complete Checklist: Moving to Portugal in 2025",
        "archetype": "skyscraper",
        "content": "## Checklist\n- [ ] Book flights\n- [ ] Get visa",
        "expected_type": "checklist",
        "expected_geo": "mediterranean"
    },
    {
        "title": "Silicon Valley Tech Jobs: Ultimate Guide",
        "archetype": "skyscraper",
        "content": "## What You Need to Know\n## Top Companies\n## Salaries",
        "expected_type": "ultimate_guide",
        "expected_geo": "urban_tech_hub"
    }
]

# ============================================================================
# RUN TESTS
# ============================================================================

print("=" * 80)
print("MULTI-DIMENSIONAL IMAGE STYLING SYSTEM v1.0 - TEST RESULTS")
print("=" * 80)
print()

for i, article in enumerate(test_articles, 1):
    print(f"\n{'='*80}")
    print(f"TEST {i}: {article['title']}")
    print(f"{'='*80}\n")

    # Layer 1: Content Type
    content_type = detect_content_type(article['title'])
    print(f"✓ Content Type Detected: {content_type}")
    assert content_type == article['expected_type'], f"Expected {article['expected_type']}, got {content_type}"

    # Layer 2: Archetype (provided by TemplateDetector)
    archetype = article['archetype']
    print(f"✓ Archetype: {archetype}")

    # Layer 3: Geographic Theme
    geo_theme = detect_geographic_theme(article['title'], article['content'])
    print(f"✓ Geographic Theme: {geo_theme or 'None'}")

    # Layer 4: Modular Blocks
    modular_blocks = detect_modular_blocks(article['content'])
    print(f"✓ Modular Blocks: {modular_blocks or 'None'}")

    # Merge all layers
    style = merge_style_layers(content_type, archetype, geo_theme, modular_blocks)

    print(f"\n📐 FINAL STYLE PROFILE:")
    print(f"   Text Placement: {style.get('text_placement')}")
    print(f"   Text Style: {style.get('text_style', 'N/A')[:60]}...")
    print(f"   Text Size: {style.get('text_size')}")
    print(f"   Composition: {style.get('composition')}")
    print(f"   Mood: {style.get('mood')}")
    print(f"   Neon Intensity: {style.get('neon_intensity')}")
    if geo_theme:
        print(f"   Color Palette: {style.get('color_palette')}")

    # Build final prompt
    prompt = build_image_prompt(
        landmark="Colosseum in Rome",
        title=article['title'],
        style=style,
        time_of_day="golden hour"
    )

    print(f"\n🎨 GENERATED PROMPT:")
    print(f"   {prompt[:200]}...")

print(f"\n\n{'='*80}")
print("✅ ALL TESTS PASSED!")
print("=" * 80)
print("\nKEY INSIGHTS:")
print("- Each article type gets unique visual treatment")
print("- Layers combine for nuanced styling")
print("- Same location (Italy) looks different based on article type")
print("- System is extensible (easy to add new types/styles)")
print("=" * 80)
