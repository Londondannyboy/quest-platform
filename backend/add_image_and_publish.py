#!/usr/bin/env python3
"""
Add hero image to existing article and publish
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.image import ImageAgent
from app.core.database import init_db, close_db, get_db


async def main():
    """Add hero image to article and publish"""

    # Initialize database
    await init_db()
    print("✅ Database connected\n")

    # Article ID
    article_id = "7dedfa0d-ed10-44bb-99b9-42506ad71320"

    try:
        pool = get_db()

        # Fetch article
        async with pool.acquire() as conn:
            article_row = await conn.fetchrow(
                "SELECT title, slug, excerpt FROM articles WHERE id = $1",
                article_id
            )

        if not article_row:
            print(f"❌ Article {article_id} not found")
            return

        article_data = {
            "title": article_row["title"],
            "excerpt": article_row["excerpt"]
        }

        print(f"📝 Article: {article_data['title']}")
        print(f"🔗 Slug: {article_row['slug']}\n")

        # Generate hero image
        print("🖼️  Generating hero image with FLUX + Cloudinary...")
        image_agent = ImageAgent()

        result = await image_agent.generate(
            article=article_data,
            target_site="relocation",
            slug=article_row["slug"]
        )

        if result["hero_image_url"]:
            print(f"✅ Hero image generated: {result['hero_image_url']}\n")

            # Update article with image
            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    UPDATE articles
                    SET hero_image_url = $1, status = 'published', published_date = NOW()
                    WHERE id = $2
                    """,
                    result["hero_image_url"],
                    article_id
                )

            print("✅ Article published with hero image!\n")
            print(f"🌐 View at: https://relocation.quest/{article_row['slug']}")
        else:
            print("❌ Image generation failed")
            if "error" in result:
                print(f"Error: {result['error']}")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        await close_db()
        print("\n🔌 Database connection closed")


if __name__ == "__main__":
    asyncio.run(main())
