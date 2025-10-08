#!/usr/bin/env python3
"""
Generate Full-Featured Article
- Multi-API research (Perplexity + additional sources)
- Claude Sonnet 4.5 content generation
- Image generation with FLUX + Cloudinary
- Internal/external links
- Publish to database
"""
import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.orchestrator import ArticleOrchestrator
from app.core.config import settings
from app.core.database import init_db, close_db


async def main():
    """Generate a high-quality article with all features"""

    # Initialize database connection pool
    await init_db()
    print("✅ Database connected")
    print()

    print("=" * 80)
    print("🚀 QUEST PLATFORM - FULL-FEATURED ARTICLE GENERATION")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Topic for generation
    topic = "Portugal Digital Nomad Visa 2025: Complete Application Guide with Requirements and Costs"
    target_site = "relocation"

    print(f"📝 Topic: {topic}")
    print(f"🎯 Target Site: {target_site}")
    print(f"🖼️  Image Generation: ENABLED")
    print(f"🔗 Links: Internal + External")
    print()
    print("-" * 80)
    print()

    # Initialize orchestrator
    orchestrator = ArticleOrchestrator()

    # Generate article with progress updates
    try:
        # Generate a job ID
        import uuid
        job_id = str(uuid.uuid4())[:8]  # Short ID for easier tracking

        print(f"🆔 Job ID: {job_id}")
        print()
        print("🔬 Stage 1/4: Research Agent (Perplexity + Multi-source)")
        print("   Gathering intelligence from research APIs...")
        print()

        result = await orchestrator.generate_article(
            topic=topic,
            target_site=target_site,
            job_id=job_id,
            priority="high"
        )

        print()
        print("=" * 80)
        print("✅ ARTICLE GENERATED SUCCESSFULLY")
        print("=" * 80)
        print()

        # Print results
        print(f"📰 Title: {result.get('title', 'N/A')}")
        print(f"🔗 Slug: {result.get('slug', 'N/A')}")
        print(f"📊 Quality Score: {result.get('quality_score', 'N/A')}/100")
        print(f"📏 Word Count: {result.get('word_count', 'N/A')} words")
        print(f"⏱️  Reading Time: {result.get('reading_time_minutes', 'N/A')} minutes")
        print(f"🆔 Article ID: {result.get('article_id', 'N/A')}")
        print()

        # Image URLs
        if result.get('hero_image_url'):
            print(f"🖼️  Hero Image: {result['hero_image_url']}")

        if result.get('featured_image_url'):
            print(f"🖼️  Featured Image: {result['featured_image_url']}")

        if result.get('content_images'):
            print(f"🖼️  Content Images: {len(result['content_images'])} images")
            for i, img in enumerate(result['content_images'][:3], 1):
                print(f"     {i}. {img}")

        print()

        # Cost breakdown
        if result.get('cost_breakdown'):
            print("💰 Cost Breakdown:")
            for agent, cost in result['cost_breakdown'].items():
                print(f"   {agent}: ${cost:.4f}")
            print(f"   TOTAL: ${result.get('total_cost', 0):.4f}")

        print()

        # View URLs
        print("🌐 View Article:")
        slug = result.get('slug', '')
        print(f"   Frontend: https://relocation.quest/{slug}")
        print(f"   API: https://quest-platform-production-b8e3.up.railway.app/api/articles/{result.get('article_id', '')}")

        print()
        print("=" * 80)
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        return result

    except Exception as e:
        print()
        print("=" * 80)
        print("❌ ERROR DURING GENERATION")
        print("=" * 80)
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        # Clean up database connection
        await close_db()
        print()
        print("🔌 Database connection closed")


if __name__ == "__main__":
    asyncio.run(main())
