"""
Install pgvector extension
"""
import asyncio
import asyncpg
import os

async def install_pgvector():
    db_url = os.getenv("NEON_CONNECTION_STRING") or os.getenv("DATABASE_URL")
    conn = await asyncpg.connect(db_url)

    try:
        print("Installing pgvector extension...")
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        print("✅ pgvector extension installed!")

        print("\nNow creating article_research table...")
        await conn.execute("DROP TABLE IF EXISTS article_research CASCADE")

        await conn.execute("""
            CREATE TABLE article_research (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                topic_query TEXT NOT NULL,
                embedding vector(1536),
                research_json JSONB NOT NULL,
                source_urls TEXT[],
                embedding_model_version VARCHAR(50) DEFAULT 'text-embedding-3-small',
                cache_hits INTEGER DEFAULT 0,
                last_accessed TIMESTAMPTZ DEFAULT NOW(),
                expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '30 days'),
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        await conn.execute("CREATE INDEX idx_research_topic ON article_research USING GIN(to_tsvector('english', topic_query))")
        await conn.execute("CREATE INDEX idx_research_embedding ON article_research USING ivfflat(embedding vector_cosine_ops) WITH (lists = 100)")
        await conn.execute("CREATE INDEX idx_research_expires ON article_research(expires_at)")

        print("✅ article_research table created successfully!")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(install_pgvector())
