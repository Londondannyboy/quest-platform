"""
Test Citation Verifier with Italy article
"""
import asyncio
import asyncpg
from app.agents.citation_verifier import CitationVerifierAgent

async def test_verifier():
    """Test citation verifier on Italy article"""

    # Connect to database
    conn = await asyncpg.connect(
        'postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require'
    )

    try:
        # Fetch Italy article
        article_record = await conn.fetchrow('''
            SELECT id, title, content
            FROM articles
            WHERE id = '47ef167b-6683-451a-9445-bc4087bf0dd0'::uuid
        ''')

        if not article_record:
            print("❌ Article not found")
            return

        article = {
            "id": str(article_record["id"]),
            "title": article_record["title"],
            "content": article_record["content"]
        }

        print(f"📄 Testing article: {article['title']}")
        print(f"   Word count: {len(article['content'].split())} words")
        print()

        # Initialize verifier
        verifier = CitationVerifierAgent()

        # Run verification (with empty research sources for now)
        result = await verifier.verify_citations(
            article=article,
            research_sources=[]
        )

        # Print results
        print("=" * 70)
        print("CITATION VERIFICATION RESULTS")
        print("=" * 70)
        print()
        print(f"✅ Verification Passed: {result['verification_passed']}")
        print(f"📊 Confidence Score: {result['confidence_score']:.2%}")
        print()
        print(f"📝 Total Inline Citations: {result['total_citations']}")
        print(f"📚 Total References (Further Reading): {result['total_references']}")
        print(f"✓  Verified URLs: {result['verified_urls']}")
        print(f"✓  Verified Claims: {result['verified_claims']}")
        print()
        print(f"⚠️  Unverified References: {len(result['unverified_references'])}")
        print(f"❌ Fake URLs: {len(result['fake_urls'])}")
        print(f"🔍 Suspicious Claims: {len(result['suspicious_claims'])}")
        print()
        print(f"💰 Cost: ${result['cost']:.4f}")
        print()

        if result['unverified_references']:
            print("Unverified URLs (first 5):")
            for url in result['unverified_references'][:5]:
                print(f"  - {url}")
            print()

        if result['fake_urls']:
            print("Fake URLs:")
            for url in result['fake_urls']:
                print(f"  - {url}")
            print()

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(test_verifier())
