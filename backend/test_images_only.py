#!/usr/bin/env python3
"""Test image generation with mock data - bypass Perplexity"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.content import ContentAgent
from app.agents.editor import EditorAgent
from app.agents.image import ImageAgent
from app.core.database import init_db, get_db

async def main():
    await init_db()
    
    # Mock research data
    mock_research = {
        "content": "Barcelona is one of Europe's top digital nomad destinations with excellent coworking spaces, reliable WiFi, vibrant culture, Mediterranean climate, and a thriving expat community."
    }
    
    print("🔬 Testing Image Pipeline (Bypassing Perplexity)")
    print("=" * 60)
    
    # Step 1: Generate content
    print("\n📝 Step 1: Generating content...")
    content_agent = ContentAgent()
    content_result = await content_agent.run(
        mock_research,
        "relocation",
        "Top Coworking Spaces in Barcelona 2025"
    )
    
    article = content_result["article"]
    print(f"✅ Content generated: {article['title']}")
    
    # Step 2: Editor scoring
    print("\n✏️  Step 2: Editor scoring...")
    editor_agent = EditorAgent()
    editor_result = await editor_agent.score(article)
    print(f"✅ Quality score: {editor_result['quality_score']}/100")
    
    # Step 3: Save to DB
    print("\n💾 Step 3: Saving to database...")
    pool = get_db()
    async with pool.acquire() as conn:
        article_id = await conn.fetchval("""
            INSERT INTO articles
            (title, slug, content, excerpt, target_site, status, quality_score, reading_time_minutes)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
        """,
        article["title"],
        "top-coworking-spaces-barcelona-2025",
        article["content"],
        article.get("excerpt", ""),
        "relocation",
        "review",
        editor_result["quality_score"],
        article.get("reading_time_minutes", 8)
        )
    
    print(f"✅ Article saved: {article_id}")
    
    # Step 4: Generate images
    print("\n🖼️  Step 4: Generating 4 images...")
    image_agent = ImageAgent()
    image_result = await image_agent.generate(
        article,
        "relocation",
        "top-coworking-spaces-barcelona-2025"
    )
    
    # Step 5: Update article with images
    print("\n📸 Step 5: Updating article with images...")
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE articles
            SET hero_image_url = $1,
                content_image_1_url = $2,
                content_image_2_url = $3,
                content_image_3_url = $4
            WHERE id = $5
        """,
        image_result.get("hero_image_url"),
        image_result.get("content_image_1_url"),
        image_result.get("content_image_2_url"),
        image_result.get("content_image_3_url"),
        article_id
        )
    
    # Verify
    async with pool.acquire() as conn:
        result = await conn.fetchrow("""
            SELECT slug, hero_image_url, content_image_1_url, content_image_2_url, content_image_3_url
            FROM articles WHERE id = $1
        """, article_id)
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETE")
    print("=" * 60)
    print(f"\n📰 Article URL: https://relocation.quest/{result['slug']}")
    print(f"\n📸 Image Status:")
    print(f"   Hero:      {'✅' if result['hero_image_url'] else '❌'}")
    print(f"   Content 1: {'✅' if result['content_image_1_url'] else '❌'}")
    print(f"   Content 2: {'✅' if result['content_image_2_url'] else '❌'}")
    print(f"   Content 3: {'✅' if result['content_image_3_url'] else '❌'}")

if __name__ == "__main__":
    asyncio.run(main())
