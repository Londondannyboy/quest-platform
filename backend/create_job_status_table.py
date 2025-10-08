"""
Create job_status table in Neon database
"""
import asyncio
import asyncpg
import os

async def create_table():
    # Get database URL from environment
    db_url = os.getenv("NEON_CONNECTION_STRING") or os.getenv("DATABASE_URL")

    if not db_url:
        raise ValueError("No database URL found in environment")

    # Connect to database
    conn = await asyncpg.connect(db_url)

    try:
        # Create job_status table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS job_status (
                job_id UUID PRIMARY KEY,
                status VARCHAR(50) NOT NULL,
                progress INTEGER DEFAULT 0,
                current_stage VARCHAR(100),
                result JSONB,
                error TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        # Create index
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_job_status_created
            ON job_status(created_at DESC);
        """)

        print("✅ job_status table created successfully!")

        # Verify it exists
        result = await conn.fetchrow("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name = 'job_status'
        """)

        if result:
            print(f"✅ Verified: {result['table_name']} table exists")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(create_table())
