#!/usr/bin/env python3
"""
TIER 0 Implementation Test Suite
Tests all critical fixes: Research Governance, Multi-API, Queue System, Worker
"""
import asyncio
import sys
import os
from datetime import datetime
import json

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.research_queue import ResearchGovernance
from app.core.research_apis import MultiAPIResearch
from app.core.queue import QuestQueue
from app.agents.research import ResearchAgent
from app.core.database import get_db
from app.core.config import settings

# Test results collector
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

async def test_research_governance():
    """Test Research Governance Module"""
    print("\n" + "="*60)
    print("1. TESTING RESEARCH GOVERNANCE")
    print("="*60)

    governance = ResearchGovernance()

    # Test 1: Load completed topics
    try:
        await governance.load_completed_topics()
        print("✅ Loaded completed topics from database")
        test_results["passed"].append("Research Governance: Load completed topics")
    except Exception as e:
        print(f"❌ Failed to load completed topics: {e}")
        test_results["failed"].append(f"Research Governance: Load completed - {str(e)}")

    # Test 2: High priority topic detection
    golden_visa_topic = "Portugal golden visa requirements 2025"
    validation = governance.validate_research_request(golden_visa_topic)

    if validation["approved"] and validation["priority_score"] >= 90:
        print(f"✅ Golden visa topic recognized as high priority: {validation['priority_score']}/100")
        test_results["passed"].append("Research Governance: Priority scoring")
    else:
        print(f"❌ Golden visa topic not properly prioritized: {validation}")
        test_results["failed"].append("Research Governance: Priority scoring failed")

    # Test 3: Duplicate detection
    duplicate_topic = "How to get Portugal digital nomad visa"  # Should be similar to existing
    is_dup = governance.is_duplicate(duplicate_topic)
    print(f"ℹ️  Duplicate detection for '{duplicate_topic}': {is_dup}")

    # Test 4: Topic suggestion
    suggestion = governance.suggest_next_topic()
    if suggestion:
        print(f"✅ Next topic suggestion: {suggestion}")
        test_results["passed"].append("Research Governance: Topic suggestion")
    else:
        print("⚠️  No topic suggestions available")
        test_results["warnings"].append("Research Governance: No suggestions")

    # Test 5: Off-topic rejection
    off_topic = "Best pizza recipes in Rome"
    validation = governance.validate_research_request(off_topic)

    if not validation["approved"] and validation["reason"] == "off_topic":
        print(f"✅ Off-topic correctly rejected: {off_topic}")
        test_results["passed"].append("Research Governance: Off-topic rejection")
    else:
        print(f"❌ Off-topic not rejected: {validation}")
        test_results["failed"].append("Research Governance: Off-topic rejection failed")

    return governance


async def test_multi_api_research():
    """Test Multi-API Research Module"""
    print("\n" + "="*60)
    print("2. TESTING MULTI-API RESEARCH")
    print("="*60)

    multi_api = MultiAPIResearch()

    # Check which APIs are available
    available_apis = []
    for name, provider in multi_api.providers.items():
        if provider.is_available():
            available_apis.append(name)
            print(f"✅ {name.upper()} API configured")
        else:
            print(f"⚠️  {name.upper()} API not configured")
            test_results["warnings"].append(f"API not configured: {name}")

    if len(available_apis) >= 2:
        test_results["passed"].append(f"Multi-API: {len(available_apis)} APIs available")
    else:
        test_results["failed"].append(f"Multi-API: Only {len(available_apis)} APIs available")

    # Test API fallback chain (if at least one API available)
    if available_apis:
        test_query = "Portugal D7 visa requirements 2025"
        print(f"\n🔍 Testing research with query: {test_query}")

        try:
            result = await multi_api.research(
                query=test_query,
                use_all=False,  # Test fallback chain
                fact_check=False
            )

            if result.get("content"):
                print(f"✅ Research successful using: {result.get('providers_used', [])}")
                print(f"   Content length: {len(result['content'])} chars")
                print(f"   Sources found: {len(result.get('sources', []))}")
                print(f"   Total cost: ${result.get('total_cost', 0)}")
                test_results["passed"].append("Multi-API: Research with fallback")
            else:
                print("❌ Research returned no content")
                test_results["failed"].append("Multi-API: No content returned")

        except Exception as e:
            print(f"❌ Research failed: {e}")
            test_results["failed"].append(f"Multi-API: Research error - {str(e)}")

    return multi_api


async def test_queue_system():
    """Test Queue System"""
    print("\n" + "="*60)
    print("3. TESTING QUEUE SYSTEM")
    print("="*60)

    queue = QuestQueue()

    # Test connection
    connected = await queue.connect()
    if connected:
        print("✅ Connected to Redis queue")
        test_results["passed"].append("Queue: Redis connection")
    else:
        print("⚠️  Redis not available - using in-memory fallback")
        test_results["warnings"].append("Queue: Using in-memory fallback")

    # Test enqueue/dequeue
    test_job_data = {
        "topic": "Test article about Malta residency",
        "target_site": "relocation",
        "timestamp": datetime.now().isoformat()
    }

    # Enqueue test job
    job_id = await queue.enqueue(
        job_type="test_job",
        data=test_job_data,
        priority=1
    )

    if job_id:
        print(f"✅ Job enqueued: {job_id}")
        test_results["passed"].append("Queue: Job enqueue")

        # Try to dequeue
        job = await queue.dequeue()
        if job and job.get("id") == job_id:
            print(f"✅ Job dequeued successfully")
            test_results["passed"].append("Queue: Job dequeue")

            # Complete the job
            await queue.complete_job(job_id, {"status": "test_complete"})
            print("✅ Job marked as complete")
            test_results["passed"].append("Queue: Job completion")
        else:
            print("❌ Failed to dequeue job")
            test_results["failed"].append("Queue: Job dequeue failed")
    else:
        print("⚠️  Job enqueue returned None (fallback mode)")
        test_results["warnings"].append("Queue: In fallback mode")

    # Test queue stats
    stats = await queue.get_stats()
    print(f"ℹ️  Queue stats: {stats}")

    await queue.disconnect()
    return queue


async def test_research_agent_integration():
    """Test ResearchAgent with all integrations"""
    print("\n" + "="*60)
    print("4. TESTING RESEARCH AGENT INTEGRATION")
    print("="*60)

    agent = ResearchAgent()

    # Test with a high-priority topic
    test_topic = "Cyprus permanent residency investment options 2025"
    print(f"\n🔍 Testing integrated research for: {test_topic}")

    try:
        result = await agent.run(test_topic)

        if result.get("research"):
            print(f"✅ Research completed successfully")
            print(f"   Cache hit: {result.get('cache_hit', False)}")
            print(f"   Cost: ${result.get('cost', 0)}")

            research_data = result["research"]
            if isinstance(research_data, dict):
                print(f"   Content length: {len(research_data.get('content', ''))} chars")
                print(f"   Sources: {len(research_data.get('sources', []))}")
                print(f"   Providers used: {research_data.get('providers_used', ['unknown'])}")

            test_results["passed"].append("ResearchAgent: Integrated research")
        else:
            print("❌ Research returned no data")
            test_results["failed"].append("ResearchAgent: No data returned")

    except Exception as e:
        print(f"❌ Research agent failed: {e}")
        test_results["failed"].append(f"ResearchAgent: Error - {str(e)}")

    return agent


async def test_database_schema():
    """Test database schema for TIER 0 tables"""
    print("\n" + "="*60)
    print("5. TESTING DATABASE SCHEMA")
    print("="*60)

    pool = get_db()

    try:
        async with pool.acquire() as conn:
            # Check job_status table
            job_status_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables
                    WHERE table_name = 'job_status'
                )
            """)

            if job_status_exists:
                print("✅ job_status table exists")
                test_results["passed"].append("Database: job_status table")
            else:
                print("❌ job_status table missing")
                test_results["failed"].append("Database: job_status table missing")

            # Check article_research table (for cache)
            research_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables
                    WHERE table_name = 'article_research'
                )
            """)

            if research_exists:
                print("✅ article_research table exists")
                test_results["passed"].append("Database: article_research table")

                # Check for vector extension
                vector_exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT 1 FROM pg_extension WHERE extname = 'vector'
                    )
                """)

                if vector_exists:
                    print("✅ pgvector extension installed")
                    test_results["passed"].append("Database: pgvector extension")
                else:
                    print("⚠️  pgvector extension not installed")
                    test_results["warnings"].append("Database: pgvector missing")
            else:
                print("❌ article_research table missing")
                test_results["failed"].append("Database: article_research table missing")

    except Exception as e:
        print(f"❌ Database check failed: {e}")
        test_results["failed"].append(f"Database: Error - {str(e)}")


async def main():
    """Run all TIER 0 tests"""
    print("\n" + "="*60)
    print("🚀 TIER 0 IMPLEMENTATION TEST SUITE")
    print("="*60)
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Environment: {'Production' if 'railway' in os.environ.get('HOSTNAME', '').lower() else 'Local'}")

    # Run all tests
    governance = await test_research_governance()
    multi_api = await test_multi_api_research()
    queue = await test_queue_system()
    agent = await test_research_agent_integration()
    await test_database_schema()

    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)

    print(f"\n✅ PASSED: {len(test_results['passed'])}")
    for test in test_results["passed"]:
        print(f"   • {test}")

    if test_results["warnings"]:
        print(f"\n⚠️  WARNINGS: {len(test_results['warnings'])}")
        for warning in test_results["warnings"]:
            print(f"   • {warning}")

    if test_results["failed"]:
        print(f"\n❌ FAILED: {len(test_results['failed'])}")
        for failure in test_results["failed"]:
            print(f"   • {failure}")

    # Overall status
    print("\n" + "="*60)
    if not test_results["failed"]:
        print("🎉 ALL TIER 0 CRITICAL FIXES VALIDATED!")
        print("   Research Governance: ✅")
        print("   Multi-API Research: ✅")
        print("   Queue System: ✅")
        print("   Database Schema: ✅")
        return 0
    else:
        print("⚠️  SOME TIER 0 TESTS FAILED - Review required")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)