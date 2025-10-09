#!/usr/bin/env python3
"""
Test 1: Generate article as DRAFT for Directus human review
This follows the human-in-the-loop architecture where articles
are created as drafts and reviewed before publishing.
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

    topic = "Relocation Services Grenada - Complete Guide 2025"
    job_id = str(uuid.uuid4())

    print("╔═══════════════════════════════════════════════════════════╗")
    print("║   TEST 1: DRAFT ARTICLE FOR DIRECTUS REVIEW              ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"\n📝 Topic: {topic}")
    print(f"🎯 Target Site: relocation.quest")
    print(f"📋 Status: DRAFT (for human review)")
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
        print("✅ DRAFT ARTICLE GENERATED!")
        print("="*60)

        # Get article details from database
        pool = get_db()
        async with pool.acquire() as conn:
            # Update status to draft (orchestrator sets as published by default)
            await conn.execute("""
                UPDATE articles
                SET status = 'draft'
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
                    content
                FROM articles
                WHERE id = $1
            """, result['article_id'])

            print(f"\n📊 ARTICLE DETAILS:")
            print(f"   Title: {article['title']}")
            print(f"   Slug: {article['slug']}")
            print(f"   Status: {article['status']} ⚠️ (awaiting review)")
            print(f"   Quality Score: {article['quality_score']}/100")
            print(f"   Word Count: {article['word_count']}")

            print(f"\n📸 IMAGE STATUS:")
            print(f"   Hero Image: {'✅' if article['hero_image_url'] else '❌'}")
            print(f"   Content Image 1: {'✅' if article['content_image_1_url'] else '❌'}")
            print(f"   Content Image 2: {'✅' if article['content_image_2_url'] else '❌'}")
            print(f"   Content Image 3: {'✅' if article['content_image_3_url'] else '❌'}")

            # Check for image placeholders in content
            content = article['content']
            placeholders = [
                'IMAGE_PLACEHOLDER_HERO',
                'IMAGE_PLACEHOLDER_1',
                'IMAGE_PLACEHOLDER_2',
                'IMAGE_PLACEHOLDER_3'
            ]

            print(f"\n📝 CONTENT ANALYSIS:")
            for placeholder in placeholders:
                if placeholder in content:
                    print(f"   ⚠️ {placeholder} still present (needs replacement)")
                else:
                    print(f"   ✅ {placeholder} replaced with image")

            print(f"\n🔍 KEYWORDS: {', '.join(article['keywords'][:5]) if article['keywords'] else 'None'}")

        # Cost breakdown
        print(f"\n💰 COST BREAKDOWN:")
        print(f"   Total: ${result['total_cost']:.4f}")
        if 'cost_breakdown' in result:
            for agent, cost in result['cost_breakdown'].items():
                print(f"   - {agent}: ${cost:.4f}")

        print(f"\n⏳ NEXT STEPS:")
        print(f"   1. Article is in DRAFT status")
        print(f"   2. Review in Directus admin panel")
        print(f"   3. Edit/enhance content as needed")
        print(f"   4. Approve and publish when ready")
        print(f"\n🔗 Directus URL: http://localhost:8055")
        print(f"   Article ID: {result['article_id']}")

        return result['article_id']

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # Clean up database connection
        await close_db()

if __name__ == "__main__":
    article_id = asyncio.run(main())
    if article_id:
        print(f"\n✨ Draft article created successfully!")
        print(f"   ID: {article_id}")
    else:
        print("\n⚠️ Article generation failed. Check logs for details.")