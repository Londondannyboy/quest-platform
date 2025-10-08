#!/usr/bin/env python3
"""Generate test article with 4 images - connects to production DB"""
import asyncio
import sys
import os

# Ensure image generation is enabled
os.environ['ENABLE_IMAGE_GENERATION'] = 'true'

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.orchestrator import ArticleOrchestrator
from app.core.database import get_db

async def main():
    orchestrator = ArticleOrchestrator()
    
    topic = "Best Digital Nomad Destinations in Spain 2025"
    
    print("🚀 Generating Article with 4 Images")
    print(f"   Topic: {topic}")
    print(f"   Image Generation: ENABLED")
    print(f"   This will take ~3-4 minutes...\n")
    
    result = await orchestrator.generate_article(
        topic=topic,
        target_site="relocation"
    )
    
    print(f"\n✅ ARTICLE GENERATED!")
    print(f"   Article ID: {result['article_id']}")
    print(f"   Slug: {result['slug']}")
    print(f"   Status: {result['status']}")
    print(f"   Total Cost: ${result['total_cost']}")
    
    # Verify images in DB
    pool = get_db()
    async with pool.acquire() as conn:
        article = await conn.fetchrow(
            "SELECT hero_image_url, content_image_1_url, content_image_2_url, content_image_3_url FROM articles WHERE id = $1",
            result['article_id']
        )
        
        print(f"\n📸 IMAGE STATUS:")
        print(f"   Hero: {'✅' if article['hero_image_url'] else '❌'}")
        print(f"   Content 1: {'✅' if article['content_image_1_url'] else '❌'}")
        print(f"   Content 2: {'✅' if article['content_image_2_url'] else '❌'}")
        print(f"   Content 3: {'✅' if article['content_image_3_url'] else '❌'}")
    
    url = f"https://relocation.quest/{result['slug']}"
    print(f"\n🔗 VIEW ARTICLE:")
    print(f"   {url}")
    
    return url

if __name__ == "__main__":
    url = asyncio.run(main())
    print(f"\n{url}")
