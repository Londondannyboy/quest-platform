"""
Run complete database migration for Quest Platform
"""
import asyncio
import asyncpg
import os

async def run_migration():
    db_url = os.getenv("NEON_CONNECTION_STRING") or os.getenv("DATABASE_URL")
    conn = await asyncpg.connect(db_url)

    try:
        print("Installing extensions...")
        await conn.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
        await conn.execute("CREATE EXTENSION IF NOT EXISTS \"pg_trgm\"")
        await conn.execute("CREATE EXTENSION IF NOT EXISTS \"vector\"")
        print("✅ Extensions installed")

        print("\nCreating articles table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                title TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                excerpt TEXT,
                hero_image_url TEXT,
                target_site VARCHAR(50) NOT NULL CHECK (target_site IN ('relocation', 'placement', 'rainmaker')),
                status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'review', 'approved', 'published', 'archived')),
                quality_score INTEGER CHECK (quality_score >= 0 AND quality_score <= 100),
                reading_time_minutes INTEGER,
                meta_title TEXT,
                meta_description TEXT,
                keywords TEXT[],
                published_date TIMESTAMPTZ,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_articles_site_status ON articles(target_site, status)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_articles_slug ON articles(slug)")
        print("✅ Articles table created")

        print("\nCreating article_research table...")
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
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_research_expires ON article_research(expires_at)")
        print("✅ Article research table created")

        print("\nCreating job_status table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS job_status (
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
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_job_status ON job_status(status, created_at DESC)")
        print("✅ Job status table created")

        # Verify tables created
        tables = await conn.fetch("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)

        print("\n✅ Migration complete! Created tables:")
        for table in tables:
            print(f"  - {table['tablename']}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migration())
