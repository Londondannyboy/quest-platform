#!/usr/bin/env python3
"""Check migration 006 status"""
import asyncio
import asyncpg

async def check():
    conn_string = "postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require"
    conn = await asyncpg.connect(conn_string)

    try:
        # Check content_type column exists
        result = await conn.fetchrow("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_name = 'articles' AND column_name IN ('content_type', 'country', 'new_slug')
            ORDER BY column_name
        """)

        print("✅ Columns exist:", result is not None)

        # Check content types
        types = await conn.fetch("""
            SELECT content_type, country, COUNT(*) as count
            FROM articles
            GROUP BY content_type, country
            ORDER BY count DESC
            LIMIT 10
        """)

        print("\n📊 Current content types:")
        for row in types:
            country_str = f" ({row['country']})" if row['country'] else ""
            print(f"  {row['content_type']}{country_str}: {row['count']} articles")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check())
