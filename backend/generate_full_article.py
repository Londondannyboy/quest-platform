#!/usr/bin/env python3
"""
QUEST PLATFORM - PRIMARY ARTICLE GENERATION SCRIPT
This is the authoritative script for generating articles in production.
Supports single article, batch generation, and continuous operation.

Usage:
    # Single article with specific topic
    python3 generate_full_article.py --topic "Your topic here"

    # Batch generation from file
    python3 generate_full_article.py --batch topics.txt --count 100

    # Generate N articles with auto-topics
    python3 generate_full_article.py --auto --count 10

    # Specify target site
    python3 generate_full_article.py --topic "Topic" --site placement
"""
import asyncio
import sys
import os
import argparse
import json
from datetime import datetime
from typing import List, Optional
import uuid

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.orchestrator import ArticleOrchestrator
from app.core.config import settings
from app.core.database import init_db, close_db, get_db


def get_default_topics() -> List[str]:
    """Default high-value topics for relocation.quest"""
    return [
        "Portugal Digital Nomad Visa 2025: Complete Application Guide with Requirements and Costs",
        "Best Coworking Spaces in Lisbon for Remote Workers 2025",
        "Spain Non-Lucrative Visa Guide for Retirees and Digital Nomads 2025",
        "Cost of Living in Barcelona vs Madrid for Expats 2025",
        "Estonia e-Residency and Digital Nomad Visa Complete Guide 2025",
        "Tax Guide for US Citizens Living in Portugal 2025",
        "Best International Schools in Dubai for Expat Families 2025",
        "Healthcare in Germany for Expats: Insurance and Access Guide 2025",
        "Remote Work from Bali: Visa, Cost, and Lifestyle Guide 2025",
        "Singapore Employment Pass: Requirements and Application Process 2025"
    ]


async def generate_single_article(
    orchestrator: ArticleOrchestrator,
    topic: str,
    target_site: str = "relocation",
    show_progress: bool = True
) -> dict:
    """Generate a single article with full pipeline"""

    job_id = str(uuid.uuid4())[:8]

    if show_progress:
        print(f"\n{'='*80}")
        print(f"📝 Topic: {topic}")
        print(f"🎯 Target Site: {target_site}")
        print(f"🆔 Job ID: {job_id}")
        print(f"⏰ Started: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*80}\n")

    try:
        result = await orchestrator.generate_article(
            topic=topic,
            target_site=target_site,
            job_id=job_id,
            priority="high"
        )

        if show_progress:
            print(f"\n✅ SUCCESS: {result.get('title', 'Article')}")
            print(f"   Quality: {result.get('quality_score', 'N/A')}/100")
            print(f"   Words: {result.get('word_count', 'N/A')}")
            print(f"   Cost: ${result.get('total_cost', 0):.4f}")
            print(f"   URL: https://{target_site}.quest/{result.get('slug', '')}")

        return result

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None


async def generate_batch(
    orchestrator: ArticleOrchestrator,
    topics: List[str],
    target_site: str = "relocation",
    max_concurrent: int = 1
) -> List[dict]:
    """Generate multiple articles with progress tracking"""

    results = []
    total = len(topics)

    print(f"\n{'='*80}")
    print(f"🚀 BATCH GENERATION: {total} articles")
    print(f"🎯 Target Site: {target_site}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    for i, topic in enumerate(topics, 1):
        print(f"\n[{i}/{total}] Generating article {i}...")

        result = await generate_single_article(
            orchestrator,
            topic,
            target_site,
            show_progress=True
        )

        if result:
            results.append(result)
            success_rate = (len(results) / i) * 100
            print(f"\n📊 Progress: {i}/{total} ({success_rate:.1f}% success rate)")

        # Brief pause between articles to avoid rate limits
        if i < total:
            await asyncio.sleep(10)

    return results


async def main():
    """Main entry point with CLI argument handling"""

    parser = argparse.ArgumentParser(
        description='Quest Platform Article Generator - Production Script'
    )
    parser.add_argument('--topic', type=str, help='Single article topic')
    parser.add_argument('--batch', type=str, help='File containing topics (one per line)')
    parser.add_argument('--auto', action='store_true', help='Use default topics')
    parser.add_argument('--count', type=int, default=1, help='Number of articles to generate')
    parser.add_argument('--site', type=str, default='relocation',
                       choices=['relocation', 'placement', 'rainmaker'],
                       help='Target site for articles')
    parser.add_argument('--concurrent', type=int, default=1,
                       help='Max concurrent generations (default=1)')

    args = parser.parse_args()

    # Initialize database
    await init_db()
    print("✅ Database connected\n")

    orchestrator = ArticleOrchestrator()

    try:
        # Determine topics to generate
        topics = []

        if args.topic:
            # Single topic from command line
            topics = [args.topic]
        elif args.batch:
            # Topics from file
            with open(args.batch, 'r') as f:
                topics = [line.strip() for line in f if line.strip()]
        elif args.auto:
            # Use default topics
            default_topics = get_default_topics()
            topics = default_topics[:min(args.count, len(default_topics))]
        else:
            # Interactive mode - ask for topic
            topic = input("Enter article topic: ").strip()
            if topic:
                topics = [topic]
            else:
                print("❌ No topic provided. Use --topic, --batch, or --auto")
                return

        # Limit topics by count
        if args.count and len(topics) > args.count:
            topics = topics[:args.count]

        # Generate articles
        if len(topics) == 1:
            # Single article
            result = await generate_single_article(
                orchestrator,
                topics[0],
                args.site
            )

            if result:
                print(f"\n{'='*80}")
                print("✅ GENERATION COMPLETE")
                print(f"{'='*80}")

                # Save summary
                summary = {
                    'timestamp': datetime.now().isoformat(),
                    'articles_generated': 1,
                    'total_cost': result.get('total_cost', 0),
                    'article': {
                        'id': result.get('article_id'),
                        'title': result.get('title'),
                        'slug': result.get('slug'),
                        'quality': result.get('quality_score'),
                        'url': f"https://{args.site}.quest/{result.get('slug', '')}"
                    }
                }

                with open('generation_summary.json', 'w') as f:
                    json.dump(summary, f, indent=2)
                print("\n📄 Summary saved to generation_summary.json")

        else:
            # Batch generation
            results = await generate_batch(
                orchestrator,
                topics,
                args.site,
                args.concurrent
            )

            print(f"\n{'='*80}")
            print(f"✅ BATCH COMPLETE: {len(results)}/{len(topics)} successful")
            print(f"{'='*80}")

            # Calculate totals
            total_cost = sum(r.get('total_cost', 0) for r in results)
            avg_quality = sum(r.get('quality_score', 0) for r in results) / len(results) if results else 0

            print(f"\n📊 STATISTICS:")
            print(f"   Articles Generated: {len(results)}")
            print(f"   Success Rate: {(len(results)/len(topics)*100):.1f}%")
            print(f"   Average Quality: {avg_quality:.1f}/100")
            print(f"   Total Cost: ${total_cost:.2f}")
            print(f"   Cost per Article: ${total_cost/len(results):.4f}" if results else "N/A")

            # Save summary
            summary = {
                'timestamp': datetime.now().isoformat(),
                'articles_requested': len(topics),
                'articles_generated': len(results),
                'success_rate': f"{(len(results)/len(topics)*100):.1f}%",
                'total_cost': total_cost,
                'average_quality': avg_quality,
                'articles': [
                    {
                        'id': r.get('article_id'),
                        'title': r.get('title'),
                        'slug': r.get('slug'),
                        'quality': r.get('quality_score'),
                        'cost': r.get('total_cost'),
                        'url': f"https://{args.site}.quest/{r.get('slug', '')}"
                    }
                    for r in results
                ]
            }

            with open('batch_generation_summary.json', 'w') as f:
                json.dump(summary, f, indent=2)
            print("\n📄 Summary saved to batch_generation_summary.json")

    except KeyboardInterrupt:
        print("\n\n⚠️ Generation interrupted by user")

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # Clean up
        await close_db()
        print("\n🔌 Database connection closed")


if __name__ == "__main__":
    asyncio.run(main())