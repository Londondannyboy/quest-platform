#!/usr/bin/env python3
"""
Seed topic_clusters table from QUEST_RELOCATION_RESEARCH.md

Parses the research document and creates topic clusters based on:
- Category distribution
- Top 20 priority topics
- CPC and search volume data
"""

import asyncio
import asyncpg
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

# Cluster definitions based on QUEST_RELOCATION_RESEARCH.md
CLUSTERS = [
    # ========================================================================
    # TIER 1: High CPC ($20+) - Premium Research (Perplexity)
    # ========================================================================
    {
        "name": "Malta Investment & Gaming",
        "slug": "malta-investment-gaming",
        "description": "Malta gaming licenses, citizenship, and investment programs",
        "priority": "high",
        "target_site": "relocation",
        "primary_keywords": [
            "malta gaming license cost",
            "malta gaming license",
            "malta permanent residence",
            "malta citizenship investment",
            "malta golden visa"
        ],
        "secondary_keywords": [
            "malta residency",
            "malta investment programs",
            "gaming license malta fees"
        ],
        "research_tier": "perplexity"
    },
    {
        "name": "Caribbean Citizenship Programs",
        "slug": "caribbean-citizenship",
        "description": "Caribbean passport and citizenship by investment programs",
        "priority": "high",
        "target_site": "relocation",
        "primary_keywords": [
            "caribbean passport comparison",
            "caribbean citizenship investment",
            "st kitts citizenship",
            "antigua citizenship",
            "dominica citizenship"
        ],
        "secondary_keywords": [
            "caribbean passport",
            "citizenship by investment caribbean",
            "second passport caribbean"
        ],
        "research_tier": "perplexity"
    },
    {
        "name": "Dubai Tax & Business",
        "slug": "dubai-tax-business",
        "description": "Dubai tax optimization and business formation",
        "priority": "high",
        "target_site": "relocation",
        "primary_keywords": [
            "dubai vs singapore taxes",
            "dubai company formation free zone",
            "dubai tax residency",
            "dubai business setup"
        ],
        "secondary_keywords": [
            "dubai taxes",
            "uae tax",
            "dubai free zone",
            "dubai company formation cost"
        ],
        "research_tier": "perplexity"
    },
    {
        "name": "Portugal Tax Optimization",
        "slug": "portugal-tax",
        "description": "Portugal NHR tax regime and tax residency",
        "priority": "high",
        "target_site": "relocation",
        "primary_keywords": [
            "portugal nhr tax regime",
            "portugal tax residency",
            "portugal non habitual resident",
            "portugal tax benefits"
        ],
        "secondary_keywords": [
            "portugal nhr",
            "portugal taxes",
            "nhr portugal requirements"
        ],
        "research_tier": "perplexity"
    },
    {
        "name": "Cyprus Tax & Investment",
        "slug": "cyprus-tax-investment",
        "description": "Cyprus non-dom tax benefits and investment programs",
        "priority": "high",
        "target_site": "relocation",
        "primary_keywords": [
            "cyprus non-dom tax benefits",
            "cyprus tax residency",
            "cyprus golden visa",
            "cyprus investment program"
        ],
        "secondary_keywords": [
            "cyprus non dom",
            "cyprus taxes",
            "cyprus residency"
        ],
        "research_tier": "perplexity"
    },
    {
        "name": "Turkey Citizenship & Investment",
        "slug": "turkey-citizenship",
        "description": "Turkey citizenship by property investment",
        "priority": "high",
        "target_site": "relocation",
        "primary_keywords": [
            "turkey citizenship property",
            "turkey citizenship investment",
            "turkey passport",
            "turkey real estate citizenship"
        ],
        "secondary_keywords": [
            "turkey citizenship",
            "turkish citizenship by investment"
        ],
        "research_tier": "perplexity"
    },
    {
        "name": "Crypto Banking Europe",
        "slug": "crypto-banking-europe",
        "description": "Crypto-friendly banks and banking in Europe",
        "priority": "high",
        "target_site": "relocation",
        "primary_keywords": [
            "crypto friendly banks europe",
            "crypto banks",
            "bitcoin friendly banks",
            "crypto banking"
        ],
        "secondary_keywords": [
            "cryptocurrency banks",
            "crypto bank account europe"
        ],
        "research_tier": "perplexity"
    },

    # ========================================================================
    # TIER 2: Medium CPC ($10-20) - Standard Research (Tavily)
    # ========================================================================
    {
        "name": "Portugal Golden Visa",
        "slug": "portugal-golden-visa",
        "description": "Portugal Golden Visa program changes and requirements",
        "priority": "medium",
        "target_site": "relocation",
        "primary_keywords": [
            "portugal golden visa 2025 changes",
            "portugal golden visa",
            "portugal golden visa requirements",
            "portugal golden visa property"
        ],
        "secondary_keywords": [
            "portugal investment visa",
            "portugal residence permit investment"
        ],
        "research_tier": "tavily"
    },
    {
        "name": "Greece Golden Visa",
        "slug": "greece-golden-visa",
        "description": "Greece Golden Visa property investment program",
        "priority": "medium",
        "target_site": "relocation",
        "primary_keywords": [
            "greece golden visa property",
            "greece golden visa",
            "greece investment visa",
            "greece residency investment"
        ],
        "secondary_keywords": [
            "greek golden visa",
            "greece residence permit"
        ],
        "research_tier": "tavily"
    },
    {
        "name": "Estonia e-Residency & Business",
        "slug": "estonia-eresidency",
        "description": "Estonia e-Residency and business setup",
        "priority": "medium",
        "target_site": "relocation",
        "primary_keywords": [
            "estonia e-residency business",
            "estonia e-residency",
            "estonia digital nomad visa",
            "estonia company formation"
        ],
        "secondary_keywords": [
            "e-residency estonia",
            "estonia business"
        ],
        "research_tier": "tavily"
    },
    {
        "name": "Malta Permanent Residence",
        "slug": "malta-residence",
        "description": "Malta permanent residence programs",
        "priority": "medium",
        "target_site": "relocation",
        "primary_keywords": [
            "malta permanent residence",
            "malta residence permit",
            "malta pr",
            "malta residency program"
        ],
        "secondary_keywords": [
            "malta permanent residency"
        ],
        "research_tier": "tavily"
    },
    {
        "name": "Global Health Insurance",
        "slug": "global-health-insurance",
        "description": "International health insurance for expats",
        "priority": "medium",
        "target_site": "relocation",
        "primary_keywords": [
            "global health insurance expats",
            "international health insurance",
            "expat health insurance",
            "worldwide health insurance"
        ],
        "secondary_keywords": [
            "international medical insurance",
            "expat insurance"
        ],
        "research_tier": "tavily"
    },
    {
        "name": "Offshore Company Formation",
        "slug": "offshore-company",
        "description": "Offshore company formation strategies",
        "priority": "medium",
        "target_site": "relocation",
        "primary_keywords": [
            "offshore company formation",
            "offshore company",
            "offshore business",
            "international company formation"
        ],
        "secondary_keywords": [
            "offshore incorporation",
            "offshore llc"
        ],
        "research_tier": "tavily"
    },
    {
        "name": "Singapore Immigration",
        "slug": "singapore-immigration",
        "description": "Singapore PR and employment pass requirements",
        "priority": "medium",
        "target_site": "relocation",
        "primary_keywords": [
            "singapore pr requirements 2025",
            "singapore employment pass",
            "singapore pr",
            "singapore immigration"
        ],
        "secondary_keywords": [
            "singapore permanent residency",
            "singapore work visa"
        ],
        "research_tier": "tavily"
    },

    # ========================================================================
    # TIER 3: Digital Nomad Visas (High Volume) - Standard Research
    # ========================================================================
    {
        "name": "Portugal Digital Nomad",
        "slug": "portugal-digital-nomad",
        "description": "Portugal digital nomad visa and D7 visa",
        "priority": "medium",
        "target_site": "relocation",
        "primary_keywords": [
            "portugal digital nomad visa",
            "portugal d7 visa",
            "portugal residence permit",
            "portugal remote work visa"
        ],
        "secondary_keywords": [
            "portugal nomad visa",
            "d7 visa portugal requirements"
        ],
        "research_tier": "tavily"
    },
    {
        "name": "Spain Digital Nomad",
        "slug": "spain-digital-nomad",
        "description": "Spain digital nomad visa and non-lucrative visa",
        "priority": "medium",
        "target_site": "relocation",
        "primary_keywords": [
            "spain digital nomad visa",
            "spain visa requirements",
            "spain non lucrative visa",
            "spain remote work visa"
        ],
        "secondary_keywords": [
            "spain nomad visa",
            "digital nomad spain"
        ],
        "research_tier": "tavily"
    },
    {
        "name": "Digital Nomad Visas Global",
        "slug": "digital-nomad-visas",
        "description": "Global digital nomad visa comparison and guides",
        "priority": "medium",
        "target_site": "relocation",
        "primary_keywords": [
            "digital nomad visa",
            "best digital nomad visas",
            "remote work visa",
            "nomad visa countries"
        ],
        "secondary_keywords": [
            "digital nomad countries",
            "remote work programs"
        ],
        "research_tier": "tavily"
    },
    {
        "name": "Barbados Welcome Stamp",
        "slug": "barbados-welcome-stamp",
        "description": "Barbados Welcome Stamp remote work program",
        "priority": "medium",
        "target_site": "relocation",
        "primary_keywords": [
            "barbados welcome stamp",
            "barbados remote work visa",
            "barbados digital nomad",
            "barbados 12 month visa"
        ],
        "secondary_keywords": [
            "barbados work from home visa"
        ],
        "research_tier": "tavily"
    },
    {
        "name": "Mexico Temporary Residence",
        "slug": "mexico-residence",
        "description": "Mexico temporary residence and digital nomad options",
        "priority": "medium",
        "target_site": "relocation",
        "primary_keywords": [
            "mexico temporary residence",
            "mexico digital nomad visa",
            "mexico residence permit",
            "mexico immigration"
        ],
        "secondary_keywords": [
            "mexico residency",
            "temporary resident mexico"
        ],
        "research_tier": "tavily"
    },

    # ========================================================================
    # TIER 4: Cost of Living & Lifestyle (Low CPC) - Lightweight Research
    # ========================================================================
    {
        "name": "Portugal Cost of Living",
        "slug": "portugal-cost-living",
        "description": "Portugal cost of living and lifestyle guides",
        "priority": "low",
        "target_site": "relocation",
        "primary_keywords": [
            "lisbon vs porto living",
            "portugal cost of living",
            "living in portugal costs",
            "portugal expenses"
        ],
        "secondary_keywords": [
            "portugal budget",
            "cost to live portugal"
        ],
        "research_tier": "haiku"
    },
    {
        "name": "Portugal Remote Work Spaces",
        "slug": "portugal-workspaces",
        "description": "Coworking spaces and cafes in Portugal",
        "priority": "low",
        "target_site": "relocation",
        "primary_keywords": [
            "best coworking spaces lisbon",
            "best cafes remote work lisbon",
            "lisbon coworking",
            "porto coworking spaces"
        ],
        "secondary_keywords": [
            "lisbon workspaces",
            "cafes work lisbon"
        ],
        "research_tier": "haiku"
    },
    {
        "name": "Spain Cost of Living",
        "slug": "spain-cost-living",
        "description": "Spain cost of living comparisons",
        "priority": "low",
        "target_site": "relocation",
        "primary_keywords": [
            "barcelona vs madrid cost",
            "spain cost of living",
            "living in spain costs",
            "barcelona expenses"
        ],
        "secondary_keywords": [
            "cost to live spain",
            "spain budget"
        ],
        "research_tier": "haiku"
    },
    {
        "name": "Dubai International Schools",
        "slug": "dubai-schools",
        "description": "International schools in Dubai",
        "priority": "low",
        "target_site": "relocation",
        "primary_keywords": [
            "international school dubai fees",
            "best international schools dubai",
            "dubai schools",
            "dubai education costs"
        ],
        "secondary_keywords": [
            "dubai school fees",
            "international education dubai"
        ],
        "research_tier": "haiku"
    },
    {
        "name": "Best Digital Nomad Cities",
        "slug": "digital-nomad-cities",
        "description": "Best cities for digital nomads by country",
        "priority": "low",
        "target_site": "relocation",
        "primary_keywords": [
            "best digital nomad cities portugal",
            "best digital nomad cities spain",
            "best cities remote work",
            "digital nomad destinations"
        ],
        "secondary_keywords": [
            "remote work cities",
            "nomad friendly cities"
        ],
        "research_tier": "haiku"
    },

    # ========================================================================
    # ADDITIONAL HIGH-VALUE CLUSTERS
    # ========================================================================
    {
        "name": "Italy Golden Visa & Residency",
        "slug": "italy-golden-visa",
        "description": "Italy investor visa and residence programs",
        "priority": "high",
        "target_site": "relocation",
        "primary_keywords": [
            "italy golden visa",
            "italy investor visa",
            "italy residence permit",
            "italy citizenship investment"
        ],
        "secondary_keywords": [
            "italy residency",
            "italian golden visa"
        ],
        "research_tier": "perplexity"
    },
    {
        "name": "Remote Work Europe General",
        "slug": "remote-work-europe",
        "description": "General European remote work content",
        "priority": "medium",
        "target_site": "relocation",
        "primary_keywords": [
            "remote work europe",
            "work from europe",
            "digital nomad europe",
            "european remote work visas"
        ],
        "secondary_keywords": [
            "remote work eu",
            "europe digital nomad"
        ],
        "research_tier": "tavily"
    },
    {
        "name": "Tax Residency Strategies",
        "slug": "tax-residency",
        "description": "Tax residency and optimization strategies",
        "priority": "high",
        "target_site": "relocation",
        "primary_keywords": [
            "tax residency",
            "tax optimization",
            "digital nomad taxes",
            "tax residency planning"
        ],
        "secondary_keywords": [
            "tax residence",
            "expat taxes",
            "international tax planning"
        ],
        "research_tier": "perplexity"
    },
    {
        "name": "Healthcare & Insurance Abroad",
        "slug": "healthcare-abroad",
        "description": "International healthcare and insurance for expats",
        "priority": "medium",
        "target_site": "relocation",
        "primary_keywords": [
            "expat healthcare",
            "international health insurance",
            "healthcare abroad",
            "expat medical insurance"
        ],
        "secondary_keywords": [
            "health insurance expats",
            "international healthcare"
        ],
        "research_tier": "tavily"
    },
]


async def seed_clusters():
    """Seed topic_clusters table with production data"""

    conn = await asyncpg.connect(settings.DATABASE_URL)

    try:
        print(f"\n{'='*80}")
        print("📦 Seeding Topic Clusters from QUEST_RELOCATION_RESEARCH.md")
        print(f"{'='*80}\n")

        # Check existing clusters
        existing_count = await conn.fetchval("SELECT COUNT(*) FROM topic_clusters")
        print(f"ℹ️  Existing clusters: {existing_count}")

        if existing_count > 0:
            # Auto-delete if running non-interactively
            import sys
            if len(sys.argv) > 1 and sys.argv[1] == '--force':
                await conn.execute("DELETE FROM topic_clusters")
                print("✅ Cleared existing clusters (--force)\n")
            else:
                try:
                    response = input(f"\n⚠️  Found {existing_count} existing clusters. Delete and reseed? (yes/no): ")
                    if response.lower() == 'yes':
                        await conn.execute("DELETE FROM topic_clusters")
                        print("✅ Cleared existing clusters\n")
                    else:
                        print("❌ Cancelled seeding")
                        return
                except EOFError:
                    print("\n❌ Non-interactive mode detected. Use --force flag to auto-delete.")
                    return

        # Insert clusters
        inserted = 0
        high_priority = 0
        medium_priority = 0
        low_priority = 0

        for cluster in CLUSTERS:
            await conn.execute("""
                INSERT INTO topic_clusters (
                    name, slug, description, priority, target_site,
                    primary_keywords, secondary_keywords, research_tier
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
                cluster["name"],
                cluster["slug"],
                cluster["description"],
                cluster["priority"],
                cluster["target_site"],
                cluster["primary_keywords"],
                cluster.get("secondary_keywords", []),
                cluster["research_tier"]
            )

            inserted += 1
            if cluster["priority"] == "high":
                high_priority += 1
                emoji = "🔥"
            elif cluster["priority"] == "medium":
                medium_priority += 1
                emoji = "⚡"
            else:
                low_priority += 1
                emoji = "📝"

            print(f"{emoji} {cluster['name']:40} [{cluster['priority']:6}] {cluster['research_tier']:11} ({len(cluster['primary_keywords'])} keywords)")

        print(f"\n{'='*80}")
        print(f"✅ Seeding Complete!")
        print(f"{'='*80}\n")

        print(f"📊 Summary:")
        print(f"   Total Clusters: {inserted}")
        print(f"   High Priority (Perplexity): {high_priority} clusters")
        print(f"   Medium Priority (Tavily): {medium_priority} clusters")
        print(f"   Low Priority (Haiku): {low_priority} clusters\n")

        # Verify seeding
        clusters_by_priority = await conn.fetch("""
            SELECT priority, COUNT(*) as count, array_agg(name) as names
            FROM topic_clusters
            GROUP BY priority
            ORDER BY
                CASE priority
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 3
                END
        """)

        print(f"📈 Clusters by Priority:\n")
        for row in clusters_by_priority:
            print(f"   {row['priority'].upper():8} {row['count']:2} clusters")
            for name in row['names'][:3]:
                print(f"            - {name}")
            if len(row['names']) > 3:
                print(f"            ... and {len(row['names']) - 3} more")
            print()

        # Show keyword coverage
        total_keywords = await conn.fetchval("""
            SELECT SUM(array_length(primary_keywords, 1))
            FROM topic_clusters
        """)
        print(f"🔑 Total Keywords Mapped: {total_keywords}\n")

        print(f"{'='*80}")
        print("✅ Topic clusters ready for Research Governance!")
        print(f"{'='*80}\n")

    except Exception as e:
        print(f"❌ Error seeding clusters: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(seed_clusters())
