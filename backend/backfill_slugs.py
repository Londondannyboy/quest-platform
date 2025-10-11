#!/usr/bin/env python3
"""
Backfill existing article slugs with site + content_type prefix
Converts: italy-digital-nomad-visa → relocation/guide/italy-digital-nomad-visa
"""
import asyncio
import asyncpg

async def backfill_slugs():
    """Add site + content_type prefix to existing article slugs"""
    conn_string = "postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require"
    conn = await asyncpg.connect(conn_string)

    try:
        # Get all articles that don't have site prefix
        articles = await conn.fetch("""
            SELECT id, slug, target_site, content_type
            FROM articles
            WHERE slug NOT LIKE '%/%'  -- No slashes = old format
            ORDER BY created_at DESC
        """)

        print(f"📊 Found {len(articles)} articles to update\n")

        for article in articles:
            old_slug = article['slug']
            target_site = article['target_site']
            content_type = article['content_type'] or 'guide'  # Default to guide

            # Generate new slug with site + content_type prefix
            new_slug = f"{target_site}/{content_type}/{old_slug}"

            # Update the article
            await conn.execute("""
                UPDATE articles
                SET slug = $1
                WHERE id = $2
            """, new_slug, article['id'])

            print(f"✅ Updated: {old_slug} → {new_slug}")

        print(f"\n🎉 Backfill complete! Updated {len(articles)} articles")

        # Verify results
        print("\n📊 Checking slug formats...")
        result = await conn.fetch("""
            SELECT
                CASE
                    WHEN slug LIKE '%/%/%' THEN '3-part (site/type/slug)'
                    WHEN slug LIKE '%/%' THEN '2-part (needs update)'
                    ELSE 'old format (no slashes)'
                END as slug_format,
                COUNT(*) as count
            FROM articles
            GROUP BY slug_format
            ORDER BY count DESC
        """)

        for row in result:
            print(f"  {row['slug_format']}: {row['count']} articles")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(backfill_slugs())
