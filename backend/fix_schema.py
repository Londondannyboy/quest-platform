"""
Fix database schema issues
"""
import asyncio
import asyncpg
import os

async def fix_schema():
    db_url = os.getenv("NEON_CONNECTION_STRING") or os.getenv("DATABASE_URL")
    conn = await asyncpg.connect(db_url)

    try:
        print("1. Dropping and recreating job_status table...")
        await conn.execute("DROP TABLE IF EXISTS job_status CASCADE")

        await conn.execute("""
            CREATE TABLE job_status (
                job_id VARCHAR(255) PRIMARY KEY,
                article_id UUID,
                status VARCHAR(50) NOT NULL CHECK (status IN ('queued', 'processing', 'completed', 'failed')),
                progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
                current_step VARCHAR(100),
                cost_breakdown JSONB DEFAULT '{}',
                total_cost DECIMAL(10,4) DEFAULT 0,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                started_at TIMESTAMPTZ,
                completed_at TIMESTAMPTZ
            )
        """)

        await conn.execute("CREATE INDEX idx_job_status ON job_status(status, created_at DESC)")
        await conn.execute("CREATE INDEX idx_job_article ON job_status(article_id)")
        print("✅ job_status table created")

        print("\n2. Creating article_research table if not exists...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS article_research (
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

        await conn.execute("CREATE INDEX IF NOT EXISTS idx_research_topic ON article_research USING GIN(to_tsvector('english', topic_query))")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_research_embedding ON article_research USING ivfflat(embedding vector_cosine_ops) WITH (lists = 100)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_research_expires ON article_research(expires_at) WHERE expires_at > NOW()")
        print("✅ article_research table ready")

        print("\n✅ Schema fixes completed successfully!")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_schema())
