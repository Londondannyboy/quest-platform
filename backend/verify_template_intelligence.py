"""
Verify Template Intelligence System is deployed and operational

Usage: python3 verify_template_intelligence.py
"""

import asyncio
import asyncpg

DATABASE_URL = "postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require"


async def verify_deployment():
    """Verify Template Intelligence deployment"""
    conn = await asyncpg.connect(DATABASE_URL)

    try:
        print("=" * 70)
        print("TEMPLATE INTELLIGENCE VERIFICATION")
        print("=" * 70)

        # Check tables exist
        print("\n📊 Checking tables...")
        tables_query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('content_archetypes', 'content_templates', 'serp_intelligence', 'scraped_competitors', 'template_performance')
            ORDER BY table_name
        """
        tables = await conn.fetch(tables_query)

        if len(tables) == 5:
            print(f"✅ All 5 Template Intelligence tables exist:")
            for table in tables:
                print(f"   - {table['table_name']}")
        else:
            print(f"❌ Only {len(tables)}/5 tables found")
            return False

        # Check archetypes seeded
        print("\n🎯 Checking archetypes...")
        archetypes_query = "SELECT name, display_name, min_word_count, max_word_count FROM content_archetypes ORDER BY min_word_count DESC"
        archetypes = await conn.fetch(archetypes_query)

        if len(archetypes) >= 5:
            print(f"✅ {len(archetypes)} archetypes seeded:")
            for arch in archetypes:
                print(f"   - {arch['name']}: {arch['display_name']} ({arch['min_word_count']}-{arch['max_word_count']} words)")
        else:
            print(f"❌ Only {len(archetypes)} archetypes found (expected 5)")
            return False

        # Check templates seeded
        print("\n📐 Checking templates...")
        templates_query = "SELECT name, display_name, array_length(schema_types, 1) as schema_count FROM content_templates ORDER BY name"
        templates = await conn.fetch(templates_query)

        if len(templates) >= 5:
            print(f"✅ {len(templates)} templates seeded:")
            for template in templates:
                print(f"   - {template['name']}: {template['display_name']} ({template['schema_count']} schemas)")
        else:
            print(f"❌ Only {len(templates)} templates found (expected 5)")
            return False

        # Check articles table has new columns
        print("\n📝 Checking articles table columns...")
        columns_query = """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'articles'
            AND column_name IN ('target_archetype', 'surface_template', 'modules_used', 'eeat_score', 'content_image_1_url', 'content_image_2_url', 'content_image_3_url')
            ORDER BY column_name
        """
        columns = await conn.fetch(columns_query)

        if len(columns) == 7:
            print(f"✅ All 7 new columns exist in articles table:")
            for col in columns:
                print(f"   - {col['column_name']}")
        else:
            print(f"❌ Only {len(columns)}/7 columns found")
            return False

        # Check views exist
        print("\n👁️  Checking views...")
        views_query = """
            SELECT table_name
            FROM information_schema.views
            WHERE table_schema = 'public'
            AND table_name IN ('template_intelligence_summary', 'serp_cache_performance', 'eeat_compliance')
            ORDER BY table_name
        """
        views = await conn.fetch(views_query)

        if len(views) == 3:
            print(f"✅ All 3 monitoring views exist:")
            for view in views:
                print(f"   - {view['table_name']}")
        else:
            print(f"⚠️  Only {len(views)}/3 views found (optional)")

        print("\n" + "=" * 70)
        print("✅ TEMPLATE INTELLIGENCE SYSTEM FULLY DEPLOYED!")
        print("=" * 70)
        print("\nReady to:")
        print("  1. Implement TemplateDetector agent")
        print("  2. Update ContentAgent with archetype prompts")
        print("  3. Generate SERP-competitive articles")

        return True

    finally:
        await conn.close()


if __name__ == "__main__":
    success = asyncio.run(verify_deployment())

    if not success:
        print("\n❌ Template Intelligence not fully deployed")
        exit(1)
