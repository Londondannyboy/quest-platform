#!/usr/bin/env python3
import asyncio
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.orchestrator import ArticleOrchestrator
from app.core.database import init_db, get_db

async def main():
    await init_db()
    
    orchestrator = ArticleOrchestrator()
    
    print("🚀 Generating test article with hero image...")
    
    result = await orchestrator.generate_article(
        topic="Best Coworking Spaces in Barcelona 2025",
        target_site="relocation",
        job_id="quick-test-1"
    )
    
    pool = get_db()
    async with pool.acquire() as conn:
        article = await conn.fetchrow("""
            SELECT slug, hero_image_url FROM articles WHERE id = $1
        """, result['article_id'])
    
    print(f"\n✅ ARTICLE CREATED!")
    print(f"   Hero Image: {'✅' if article['hero_image_url'] else '❌'}")
    print(f"   URL: https://relocation.quest/{article['slug']}")

if __name__ == "__main__":
    asyncio.run(main())
