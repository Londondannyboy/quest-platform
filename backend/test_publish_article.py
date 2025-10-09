#!/usr/bin/env python3
"""
Test 2: Generate article and PUBLISH directly
This bypasses human review and publishes immediately.
Useful for automated content when quality threshold is met.
"""
import asyncio
import sys
import os
from datetime import datetime
import uuid

# Ensure image generation is enabled
os.environ['ENABLE_IMAGE_GENERATION'] = 'true'

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.orchestrator import ArticleOrchestrator
from app.core.database import get_db, init_db, close_db

async def main():
    # Initialize database connection
    await init_db()

    orchestrator = ArticleOrchestrator()

    topic = "Digital Nomad Tax Guide for Portugal 2025"
    job_id = str(uuid.uuid4())

    print("╔═══════════════════════════════════════════════════════════╗")
    print("║   TEST 2: DIRECT PUBLISH (NO REVIEW)                     ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"\n📝 Topic: {topic}")
    print(f"🎯 Target Site: relocation.quest")
    print(f"📋 Status: PUBLISHED (bypassing review)")
    print(f"🖼️  Images: 4 strategic placements")
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "="*60 + "\n")

    try:
        # Generate article
        print("🔄 Running 7-agent orchestration...")
        result = await orchestrator.generate_article(
            topic=topic,
            target_site="relocation",
            job_id=job_id
        )

        print("\n" + "="*60)
        print("✅ ARTICLE PUBLISHED!")
        print("="*60)

        # Get article details from database
        pool = get_db()
        async with pool.acquire() as conn:
            # Update status to published and set published_date
            await conn.execute("""
                UPDATE articles
                SET
                    status = 'published',
                    published_date = NOW()
                WHERE id = $1
            """, result['article_id'])

            article = await conn.fetchrow("""
                SELECT
                    title,
                    slug,
                    status,
                    quality_score,
                    word_count,
                    hero_image_url,
                    content_image_1_url,
                    content_image_2_url,
                    content_image_3_url,
                    keywords,
                    content,
                    published_date
                FROM articles
                WHERE id = $1
            """, result['article_id'])

            print(f"\n📊 ARTICLE DETAILS:")
            print(f"   Title: {article['title']}")
            print(f"   Slug: {article['slug']}")
            print(f"   Status: {article['status']} ✅ (live)")
            print(f"   Quality Score: {article['quality_score']}/100")
            print(f"   Word Count: {article['word_count']}")
            print(f"   Published: {article['published_date'].strftime('%Y-%m-%d %H:%M:%S')}")

            print(f"\n📸 IMAGE STATUS:")
            print(f"   Hero Image: {'✅' if article['hero_image_url'] else '❌'}")
            if article['hero_image_url']:
                print(f"      URL: {article['hero_image_url'][:60]}...")

            print(f"   Content Image 1: {'✅' if article['content_image_1_url'] else '❌'}")
            if article['content_image_1_url']:
                print(f"      URL: {article['content_image_1_url'][:60]}...")

            print(f"   Content Image 2: {'✅' if article['content_image_2_url'] else '❌'}")
            if article['content_image_2_url']:
                print(f"      URL: {article['content_image_2_url'][:60]}...")

            print(f"   Content Image 3: {'✅' if article['content_image_3_url'] else '❌'}")
            if article['content_image_3_url']:
                print(f"      URL: {article['content_image_3_url'][:60]}...")

            # Check for image placeholders in content
            content = article['content']
            placeholders = [
                'IMAGE_PLACEHOLDER_HERO',
                'IMAGE_PLACEHOLDER_1',
                'IMAGE_PLACEHOLDER_2',
                'IMAGE_PLACEHOLDER_3'
            ]

            print(f"\n📝 CONTENT ANALYSIS:")
            has_placeholders = False
            for placeholder in placeholders:
                if placeholder in content:
                    print(f"   ⚠️ {placeholder} still present (needs replacement)")
                    has_placeholders = True
                else:
                    print(f"   ✅ {placeholder} replaced with image")

            if not has_placeholders:
                print("\n   🎉 All image placeholders successfully replaced!")

            print(f"\n🔍 KEYWORDS: {', '.join(article['keywords'][:5]) if article['keywords'] else 'None'}")

        # Cost breakdown
        print(f"\n💰 COST BREAKDOWN:")
        print(f"   Total: ${result['total_cost']:.4f}")
        if 'cost_breakdown' in result:
            for agent, cost in result['cost_breakdown'].items():
                print(f"   - {agent}: ${cost:.4f}")

        # Live URL
        live_url = f"https://relocation.quest/{article['slug']}"
        print(f"\n🌍 LIVE ARTICLE:")
        print(f"   URL: {live_url}")
        print(f"   Status: Published and live!")

        print(f"\n📊 COMPARISON WITH DRAFT APPROACH:")
        print(f"   Draft Approach:")
        print(f"   - ✅ Human review ensures quality")
        print(f"   - ✅ Can add custom insights")
        print(f"   - ❌ Slower time to publish")
        print(f"   - ❌ Requires manual intervention")
        print(f"\n   Direct Publish:")
        print(f"   - ✅ Instant publishing")
        print(f"   - ✅ Fully automated")
        print(f"   - ⚠️ Relies on AI quality score")
        print(f"   - ❌ No human oversight")

        return live_url

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
        print(f"\n✨ Article published successfully!")
        print(f"   View at: {url}")
    else:
        print("\n⚠️ Article generation failed. Check logs for details.")