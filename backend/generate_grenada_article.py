#!/usr/bin/env python3
"""
Generate article about Relocation Services Grenada
Tests new image placement logic with 4 strategic images
"""
import asyncio
import sys
import os
from datetime import datetime

# Ensure image generation is enabled
os.environ['ENABLE_IMAGE_GENERATION'] = 'true'

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.orchestrator import ArticleOrchestrator
from app.core.database import get_db, init_db, close_db
import uuid

async def main():
    # Initialize database connection
    await init_db()

    orchestrator = ArticleOrchestrator()

    topic = "Relocation Services Grenada"
    job_id = str(uuid.uuid4())

    print("╔═══════════════════════════════════════════════════════════╗")
    print("║     QUEST PLATFORM - ARTICLE GENERATION WITH IMAGES      ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"\n📝 Topic: {topic}")
    print(f"🎯 Target Site: relocation.quest")
    print(f"🖼️  Image Generation: ENABLED (4 strategic placements)")
    print(f"⏱️  Estimated Time: 3-4 minutes")
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "="*60 + "\n")

    try:
        # Generate article with orchestrator
        print("🔄 Starting 7-agent orchestration...")
        print("   1. Research Agent: Gathering data about Grenada relocation")
        print("   2. Content Agent: Writing comprehensive article")
        print("   3. Editor Agent: Refining and fact-checking")
        print("   4. Image Agent: Generating 4 custom images")
        print("   5. SEO Agent: Optimizing for search engines")
        print("\n")

        result = await orchestrator.generate_article(
            topic=topic,
            target_site="relocation",
            job_id=job_id
        )

        print("\n" + "="*60)
        print("✅ ARTICLE SUCCESSFULLY GENERATED!")
        print("="*60)

        # Display results
        print(f"\n📊 GENERATION SUMMARY:")
        print(f"   Article ID: {result['article_id']}")
        print(f"   Slug: {result['slug']}")
        print(f"   Status: {result['status']}")
        print(f"   Quality Score: {result.get('quality_score', 'N/A')}/100")
        print(f"   Word Count: {result.get('word_count', 'N/A')}")
        print(f"   Total Cost: ${result['total_cost']:.4f}")

        # Verify images in database
        pool = get_db()
        async with pool.acquire() as conn:
            article = await conn.fetchrow("""
                SELECT
                    title,
                    hero_image_url,
                    content_image_1_url,
                    content_image_2_url,
                    content_image_3_url,
                    keywords,
                    quality_score,
                    word_count
                FROM articles
                WHERE id = $1
            """, result['article_id'])

            print(f"\n📸 IMAGE GENERATION STATUS:")
            print(f"   Hero Image: {'✅ Generated' if article['hero_image_url'] else '❌ Missing'}")
            if article['hero_image_url']:
                print(f"      URL: {article['hero_image_url'][:60]}...")

            print(f"   Content Image 1: {'✅ Generated' if article['content_image_1_url'] else '❌ Missing'}")
            if article['content_image_1_url']:
                print(f"      URL: {article['content_image_1_url'][:60]}...")

            print(f"   Content Image 2: {'✅ Generated' if article['content_image_2_url'] else '❌ Missing'}")
            if article['content_image_2_url']:
                print(f"      URL: {article['content_image_2_url'][:60]}...")

            print(f"   Content Image 3: {'✅ Generated' if article['content_image_3_url'] else '❌ Missing'}")
            if article['content_image_3_url']:
                print(f"      URL: {article['content_image_3_url'][:60]}...")

            # Check content for image placeholders
            content_check = await conn.fetchrow("""
                SELECT content FROM articles WHERE id = $1
            """, result['article_id'])

            content = content_check['content']
            has_placeholders = 'IMAGE_PLACEHOLDER' in content

            print(f"\n📝 CONTENT ANALYSIS:")
            print(f"   Title: {article['title']}")
            print(f"   Keywords: {', '.join(article['keywords'][:5]) if article['keywords'] else 'None'}")
            print(f"   Quality Score: {article['quality_score']}/100")
            print(f"   Word Count: {article['word_count']}")
            print(f"   Image Placeholders Replaced: {'❌ Still present' if has_placeholders else '✅ All replaced'}")

        # Generate URL
        url = f"https://relocation.quest/{result['slug']}"
        print(f"\n🔗 ARTICLE URL:")
        print(f"   {url}")

        print(f"\n🕐 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Cost breakdown if available
        if 'cost_breakdown' in result:
            print(f"\n💰 COST BREAKDOWN:")
            for agent, cost in result['cost_breakdown'].items():
                print(f"   {agent}: ${cost:.4f}")

        return url

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # Clean up database connection
        await close_db()

if __name__ == "__main__":
    url = asyncio.run(main())
    if url:
        print(f"\n✨ View your article at: {url}")
    else:
        print("\n⚠️ Article generation failed. Check logs for details.")