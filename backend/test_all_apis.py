#!/usr/bin/env python3
"""
Test all research APIs individually to validate configuration
Tests each API with the same query to compare responses
"""
import asyncio
import os
import sys
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.research_apis import (
    PerplexityProvider,
    TavilyProvider,
    FirecrawlProvider,
    SerperProvider,
    LinkUpProvider,
    CritiqueLabsProvider
)

# Test query - same for all APIs
TEST_QUERY = "What are the requirements for Portugal Golden Visa in 2025?"

async def test_api(name: str, provider):
    """Test a single API provider"""
    print(f"\n{'='*60}")
    print(f"Testing {name.upper()}")
    print(f"{'='*60}")

    if not provider.is_available():
        print(f"❌ {name} - No API key configured")
        return {
            "name": name,
            "status": "not_configured",
            "error": "No API key"
        }

    try:
        start = datetime.now()
        result = await provider.search(TEST_QUERY)
        duration = (datetime.now() - start).total_seconds()

        if result and result.get("content"):
            content = result["content"]
            sources = result.get("sources", [])
            cost = result.get("cost", 0)

            print(f"✅ {name} - Success!")
            print(f"   Response time: {duration:.2f}s")
            print(f"   Content length: {len(content)} chars")
            print(f"   Sources found: {len(sources)}")
            print(f"   Cost: ${cost}")
            print(f"   First 200 chars: {content[:200]}...")

            return {
                "name": name,
                "status": "success",
                "duration": duration,
                "content_length": len(content),
                "sources_count": len(sources),
                "cost": float(cost)
            }
        else:
            print(f"⚠️ {name} - Empty response")
            return {
                "name": name,
                "status": "empty_response"
            }

    except Exception as e:
        print(f"❌ {name} - Error: {str(e)}")
        return {
            "name": name,
            "status": "error",
            "error": str(e)
        }

async def main():
    """Test all APIs"""
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║           QUEST PLATFORM - API VALIDATION TEST           ║
╚═══════════════════════════════════════════════════════════╝

Test Query: "{TEST_QUERY}"
Started: {datetime.now().isoformat()}
    """)

    # Initialize all providers
    providers = {
        "perplexity": PerplexityProvider(),
        "tavily": TavilyProvider(),
        "firecrawl": FirecrawlProvider(),
        "serper": SerperProvider(),
        "linkup": LinkUpProvider(),
        "critique_labs": CritiqueLabsProvider()
    }

    # Test each provider
    results = []
    for name, provider in providers.items():
        result = await test_api(name, provider)
        results.append(result)
        await asyncio.sleep(1)  # Be nice to APIs

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}\n")

    working = [r for r in results if r["status"] == "success"]
    configured = [r for r in results if r["status"] != "not_configured"]

    print(f"APIs Tested: {len(results)}")
    print(f"APIs Configured: {len(configured)}/{len(results)}")
    print(f"APIs Working: {len(working)}/{len(configured)}")

    print("\nStatus by API:")
    for r in results:
        status_emoji = {
            "success": "✅",
            "not_configured": "🔧",
            "error": "❌",
            "empty_response": "⚠️"
        }.get(r["status"], "❓")

        extra = ""
        if r["status"] == "success":
            extra = f" - {r['content_length']} chars, {r['sources_count']} sources, ${r['cost']}"
        elif r["status"] == "error":
            extra = f" - {r.get('error', 'Unknown error')[:50]}"

        print(f"  {status_emoji} {r['name']:15} {extra}")

    # Test parallel execution
    print(f"\n{'='*60}")
    print("TESTING PARALLEL EXECUTION")
    print(f"{'='*60}\n")

    # Test multiple APIs simultaneously
    working_providers = [(name, p) for name, p in providers.items()
                        if p.is_available()][:3]  # Test up to 3

    if len(working_providers) >= 2:
        print(f"Running {len(working_providers)} APIs in parallel...")
        start = datetime.now()

        tasks = [provider.search(TEST_QUERY)
                for name, provider in working_providers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        duration = (datetime.now() - start).total_seconds()
        successful = sum(1 for r in results if not isinstance(r, Exception) and r)

        print(f"✅ Parallel execution completed in {duration:.2f}s")
        print(f"   Successful: {successful}/{len(working_providers)}")
    else:
        print("⚠️ Not enough configured APIs to test parallel execution")

    print(f"\n{'='*60}")
    print("TEST COMPLETE")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(main())