#!/usr/bin/env python3
"""
Quick script to check research data size from Neon database
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
import json

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require")

async def check_research():
    engine = create_async_engine(DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"))

    async with engine.connect() as conn:
        result = await conn.execute("""
            SELECT
                topic,
                LENGTH(research_data::text) as research_chars,
                (LENGTH(research_data::text) / 5) as approx_words,
                created_at
            FROM article_research
            WHERE topic ILIKE '%Portugal%'
               OR topic ILIKE '%Test%'
               OR topic ILIKE '%Gemini%'
            ORDER BY created_at DESC
            LIMIT 5
        """)

        rows = result.fetchall()

        print("\n" + "="*80)
        print("RESEARCH DATA SIZE - RECENT ARTICLES")
        print("="*80 + "\n")

        for row in rows:
            topic = row[0]
            chars = row[1]
            words = row[2]
            created = row[3]

            print(f"Topic: {topic[:60]}...")
            print(f"  Characters: {chars:,}")
            print(f"  Approx Words: {words:,}")
            print(f"  Created: {created}")
            print()

        # Also check the latest article's actual research data
        result2 = await conn.execute("""
            SELECT research_data
            FROM article_research
            ORDER BY created_at DESC
            LIMIT 1
        """)

        latest = result2.fetchone()
        if latest:
            research_data = latest[0]
            print("\nLATEST ARTICLE RESEARCH BREAKDOWN:")
            print("="*80)

            if isinstance(research_data, str):
                research_data = json.loads(research_data)

            # Count content from each source
            for key, value in research_data.items():
                if isinstance(value, str):
                    print(f"  {key}: {len(value):,} chars, ~{len(value)//5:,} words")
                elif isinstance(value, list):
                    total_chars = sum(len(str(item)) for item in value)
                    print(f"  {key}: {len(value)} items, {total_chars:,} chars total")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_research())
