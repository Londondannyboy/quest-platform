#!/usr/bin/env python3
"""Check what APIs ran for Grenada research"""
import asyncio
import asyncpg
import json

async def check():
    conn = await asyncpg.connect('postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require')

    # Get the Grenada research
    research = await conn.fetchrow('''
        SELECT topic_query, research_json
        FROM article_research
        WHERE topic_query = 'Relocation Services Grenada'
        ORDER BY created_at DESC
        LIMIT 1
    ''')

    if research:
        data = research['research_json']

        print(f"\n🔍 RESEARCH FOR: {research['topic_query']}")
        print("="*60)

        # Parse the research data
        if 'results' in data:
            for i, result in enumerate(data['results'], 1):
                print(f'\n📊 API #{i}: {result.get("provider", "Unknown")}')
                print(f'   Content Length: {len(result.get("content", ""))} chars')
                print(f'   Sources: {len(result.get("sources", []))}')

                # Show first 200 chars of content
                content = result.get("content", "")[:200]
                print(f'   Content Preview: {content}...')

                if result.get('sources'):
                    print('   Source URLs:')
                    for j, source in enumerate(result.get('sources', [])[:5], 1):
                        if isinstance(source, str):
                            print(f'     {j}. {source[:80]}')
                        elif isinstance(source, dict):
                            print(f'     {j}. {source.get("url", "No URL")[:80]}')

        # Check what was used
        print(f'\n✅ SUMMARY:')
        print(f'   Total APIs Used: {len(data.get("providers_used", []))}')
        print(f'   Providers: {data.get("providers_used", [])}')
        print(f'   Total Cost: ${data.get("total_cost", 0)}')
    else:
        print("No research found for Grenada")

    await conn.close()

if __name__ == "__main__":
    asyncio.run(check())