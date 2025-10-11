#!/usr/bin/env python3
"""
Run database migration 006: Content-Type-Based URL Structure
"""
import asyncio
import asyncpg
from pathlib import Path

async def run_migration():
    """Execute migration 006"""
    conn_string = "postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require"

    # Read migration file
    migration_path = Path(__file__).parent / "migrations" / "006_content_type_url_structure.sql"
    with open(migration_path, 'r') as f:
        sql = f.read()

    print("🔄 Connecting to Neon PostgreSQL...")
    conn = await asyncpg.connect(conn_string)

    try:
        print("📝 Running migration 006...")
        await conn.execute(sql)
        print("✅ Migration 006 complete!")

        # Query results
        print("\n📊 Checking migration results...")
        result = await conn.fetch("""
            SELECT
                content_type,
                COUNT(*) as count
            FROM articles
            GROUP BY content_type
            ORDER BY count DESC
        """)

        print("\nContent Types:")
        for row in result:
            print(f"  {row['content_type']}: {row['count']} articles")

    finally:
        await conn.close()
        print("\n🔌 Database connection closed")

if __name__ == "__main__":
    asyncio.run(run_migration())
