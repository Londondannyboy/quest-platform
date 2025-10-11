"""
Run Template Intelligence migration (003_template_intelligence.sql)

Usage: python3 run_template_intelligence_migration.py
"""

import asyncio
import asyncpg
from pathlib import Path
import structlog

logger = structlog.get_logger()

DATABASE_URL = "postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require"


async def run_migration():
    """Run Template Intelligence migration"""
    migration_file = Path(__file__).parent / "migrations" / "003_template_intelligence.sql"

    if not migration_file.exists():
        logger.error("migration.not_found", file=str(migration_file))
        print(f"ERROR: Migration file not found: {migration_file}")
        return False

    logger.info("migration.start", file=migration_file.name)
    print(f"\n🚀 Running migration: {migration_file.name}")

    try:
        # Read SQL file
        sql = migration_file.read_text()

        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)

        try:
            # Execute migration (this is a multi-statement transaction)
            await conn.execute(sql)

            logger.info("migration.success", file=migration_file.name)
            print(f"✅ Migration successful: {migration_file.name}")

            # Verify tables were created
            tables_query = """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('content_archetypes', 'content_templates', 'serp_intelligence', 'scraped_competitors', 'template_performance')
                ORDER BY table_name
            """
            tables = await conn.fetch(tables_query)

            print(f"\n📊 Verified {len(tables)} tables created:")
            for table in tables:
                print(f"  - {table['table_name']}")

            # Verify archetypes were seeded
            archetypes_query = "SELECT name, display_name FROM content_archetypes ORDER BY min_word_count DESC"
            archetypes = await conn.fetch(archetypes_query)

            print(f"\n🎯 Verified {len(archetypes)} archetypes seeded:")
            for archetype in archetypes:
                print(f"  - {archetype['name']}: {archetype['display_name']}")

            # Verify templates were seeded
            templates_query = "SELECT name, display_name FROM content_templates ORDER BY name"
            templates = await conn.fetch(templates_query)

            print(f"\n📐 Verified {len(templates)} templates seeded:")
            for template in templates:
                print(f"  - {template['name']}: {template['display_name']}")

            return True

        finally:
            await conn.close()

    except Exception as e:
        logger.error(
            "migration.failed",
            file=migration_file.name,
            error=str(e)
        )
        print(f"\n❌ Migration failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("TEMPLATE INTELLIGENCE MIGRATION")
    print("=" * 70)

    success = asyncio.run(run_migration())

    if success:
        print("\n" + "=" * 70)
        print("✅ Template Intelligence System deployed successfully!")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("❌ Migration failed. Check logs above for details.")
        print("=" * 70)
