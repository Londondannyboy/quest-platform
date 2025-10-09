#!/usr/bin/env python3
"""
Fix Directus publishing workflow by adding proper columns and updating status values
"""
import asyncio
import asyncpg
from datetime import datetime

async def fix_publishing():
    conn = await asyncpg.connect('postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require')

    print("🔧 Fixing Directus Publishing Workflow")
    print("="*60)

    # 1. Check current schema
    print("\n1. Checking current articles schema...")
    columns = await conn.fetch("""
        SELECT column_name, data_type, column_default
        FROM information_schema.columns
        WHERE table_name = 'articles'
        ORDER BY ordinal_position
    """)

    has_published_at = False
    has_published_date = False

    for col in columns:
        print(f"   - {col['column_name']}: {col['data_type']}")
        if col['column_name'] == 'published_at':
            has_published_at = True
        if col['column_name'] == 'published_date':
            has_published_date = True

    # 2. Add published_at column if missing
    if not has_published_at and not has_published_date:
        print("\n2. Adding published_at column...")
        await conn.execute("""
            ALTER TABLE articles
            ADD COLUMN IF NOT EXISTS published_at TIMESTAMPTZ
        """)
        print("   ✅ published_at column added")
    elif has_published_date and not has_published_at:
        print("\n2. Renaming published_date to published_at...")
        await conn.execute("""
            ALTER TABLE articles
            RENAME COLUMN published_date TO published_at
        """)
        print("   ✅ Renamed published_date to published_at")
    else:
        print("\n2. published_at column already exists ✅")

    # 3. Check and update status values
    print("\n3. Checking current article statuses...")
    statuses = await conn.fetch("""
        SELECT DISTINCT status, COUNT(*) as count
        FROM articles
        GROUP BY status
        ORDER BY status
    """)

    for status in statuses:
        print(f"   - {status['status']}: {status['count']} articles")

    # 4. Update status values to standard ones
    print("\n4. Standardizing status values...")

    # Update any 'review' or 'approved' to 'draft'
    updated = await conn.execute("""
        UPDATE articles
        SET status = 'draft'
        WHERE status IN ('review', 'approved')
        RETURNING id
    """)

    # Get count from the UPDATE result
    count = int(updated.split()[-1]) if updated else 0
    if count > 0:
        print(f"   ✅ Updated {count} articles from review/approved to draft")

    # 5. Set published_at for published articles
    print("\n5. Setting published_at for published articles...")
    result = await conn.execute("""
        UPDATE articles
        SET published_at = created_at
        WHERE status = 'published' AND published_at IS NULL
        RETURNING id
    """)

    count = int(result.split()[-1]) if result else 0
    if count > 0:
        print(f"   ✅ Set published_at for {count} published articles")

    # 6. Create indexes for better Directus performance
    print("\n6. Creating indexes for Directus...")

    # Check if indexes exist
    indexes = await conn.fetch("""
        SELECT indexname
        FROM pg_indexes
        WHERE tablename = 'articles'
    """)

    index_names = [idx['indexname'] for idx in indexes]

    if 'idx_articles_status' not in index_names:
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_articles_status
            ON articles(status)
        """)
        print("   ✅ Created index on status")

    if 'idx_articles_published_at' not in index_names:
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_articles_published_at
            ON articles(published_at)
        """)
        print("   ✅ Created index on published_at")

    if 'idx_articles_created_at' not in index_names:
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_articles_created_at
            ON articles(created_at)
        """)
        print("   ✅ Created index on created_at")

    # 7. Show final status
    print("\n7. Final article status summary:")
    final_statuses = await conn.fetch("""
        SELECT
            status,
            COUNT(*) as count,
            COUNT(CASE WHEN published_at IS NOT NULL THEN 1 END) as has_publish_date
        FROM articles
        GROUP BY status
        ORDER BY status
    """)

    for status in final_statuses:
        print(f"   - {status['status']}: {status['count']} articles ({status['has_publish_date']} with publish date)")

    # 8. Show sample articles
    print("\n8. Sample articles:")
    articles = await conn.fetch("""
        SELECT id, title, slug, status, published_at, created_at
        FROM articles
        ORDER BY created_at DESC
        LIMIT 3
    """)

    for article in articles:
        print(f"\n   📄 {article['title'][:50]}...")
        print(f"      ID: {article['id']}")
        print(f"      Status: {article['status']}")
        print(f"      Published: {article['published_at'] or 'Not published'}")
        print(f"      Created: {article['created_at']}")

    await conn.close()

    print("\n✅ PUBLISHING WORKFLOW FIXED!")
    print("\n📝 Instructions for Directus:")
    print("   1. Refresh your browser at http://localhost:8055")
    print("   2. Go to Articles collection")
    print("   3. You should now see:")
    print("      - Status dropdown with 'draft' and 'published' options")
    print("      - Published At date field")
    print("   4. To publish an article:")
    print("      - Change status from 'draft' to 'published'")
    print("      - Set the Published At date")
    print("      - Save the article")

if __name__ == "__main__":
    asyncio.run(fix_publishing())