"""
Test script to generate article with 4 images
"""
import asyncio
import os
os.environ['ENABLE_IMAGE_GENERATION'] = 'true'

from app.agents.orchestrator import Orchestrator

async def main():
    orchestrator = Orchestrator()
    
    topic = "Best Digital Nomad Hubs in Spain 2025"
    target_site = "relocation"
    
    print(f"🚀 Generating article with 4 images...")
    print(f"   Topic: {topic}")
    print(f"   Target: {target_site}")
    print(f"   Image generation: ENABLED")
    
    result = await orchestrator.generate_article(
        topic=topic,
        target_site=target_site
    )
    
    print(f"\n✅ Article generated!")
    print(f"   Article ID: {result['article_id']}")
    print(f"   Slug: {result['slug']}")
    print(f"   Status: {result['status']}")
    print(f"   Total cost: ${result['total_cost']}")
    print(f"\n🔗 View at: https://relocation.quest/{result['slug']}")

if __name__ == "__main__":
    asyncio.run(main())
