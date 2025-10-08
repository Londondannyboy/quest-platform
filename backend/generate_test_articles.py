#!/usr/bin/env python3
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.orchestrator import ArticleOrchestrator
from app.core.database import init_db, get_db

async def main():
    # Initialize database
    await init_db()
    
    orchestrator = ArticleOrchestrator()
    
    print("=" * 80)
    print("ARTICLE #1: HERO IMAGE ONLY (Medium Quality)")
    print("=" * 80)
    
    result1 = await orchestrator.generate_article(
        topic="Digital Nomad Visa Guide for Spain 2025",
        target_site="relocation",
        job_id="test-hero-1"
    )
    
    pool = get_db()
    async with pool.acquire() as conn:
        art1 = await conn.fetchrow("""
            SELECT slug, status, quality_score, hero_image_url, content_image_1_url 
            FROM articles WHERE id = $1
        """, result1['article_id'])
    
    print(f"\n✅ ARTICLE #1:")
    print(f"   Quality: {art1['quality_score']}/100 | Status: {art1['status']}")
    print(f"   URL: https://relocation.quest/{art1['slug']}")
    print(f"   Hero: {'✅' if art1['hero_image_url'] else '❌'} | Content: {'✅' if art1['content_image_1_url'] else '❌'}")
    
    print("\n" + "=" * 80)
    print("ARTICLE #2: ALL 4 IMAGES (High Quality - waiting 10s...)")
    print("=" * 80)
    await asyncio.sleep(10)
    
    result2 = await orchestrator.generate_article(
        topic="Best Coworking Spaces in Lisbon for Remote Workers 2025",
        target_site="relocation",
        job_id="test-hero-2"
    )
    
    async with pool.acquire() as conn:
        art2 = await conn.fetchrow("""
            SELECT slug, status, quality_score, hero_image_url, content_image_1_url, content_image_2_url, content_image_3_url 
            FROM articles WHERE id = $1
        """, result2['article_id'])
    
    print(f"\n✅ ARTICLE #2:")
    print(f"   Quality: {art2['quality_score']}/100 | Status: {art2['status']}")
    print(f"   URL: https://relocation.quest/{art2['slug']}")
    print(f"   Hero: {'✅' if art2['hero_image_url'] else '❌'}")
    print(f"   Content 1: {'✅' if art2['content_image_1_url'] else '❌'}")
    print(f"   Content 2: {'✅' if art2['content_image_2_url'] else '❌'}")
    print(f"   Content 3: {'✅' if art2['content_image_3_url'] else '❌'}")
    
    print("\n" + "=" * 80)
    print("✅ BOTH ARTICLES GENERATED!")
    print("=" * 80)
    print(f"\n📰 Article #1: https://relocation.quest/{art1['slug']}")
    print(f"📰 Article #2: https://relocation.quest/{art2['slug']}")

if __name__ == "__main__":
    asyncio.run(main())
