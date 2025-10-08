"""
Run initial database migration
"""
import asyncio
import asyncpg
import os

async def run_migration():
    # Get database URL from environment
    db_url = os.getenv("NEON_CONNECTION_STRING") or os.getenv("DATABASE_URL")

    if not db_url:
        raise ValueError("No database URL found in environment")

    # Read migration file
    with open("migrations/001_initial_schema.sql") as f:
        migration_sql = f.read()

    # Connect to database
    conn = await asyncpg.connect(db_url)

    try:
        # Run migration (split by semicolon and run each statement)
        statements = [s.strip() for s in migration_sql.split(';') if s.strip()]

        for i, statement in enumerate(statements):
            # Skip comments and empty statements
            if not statement or statement.startswith('--'):
                continue

            try:
                print(f"Running statement {i+1}/{len(statements)}...")
                await conn.execute(statement)
            except Exception as e:
                # Ignore "already exists" errors
                if "already exists" in str(e) or "duplicate" in str(e).lower():
                    print(f"  ⚠️  Skipping (already exists): {str(e)[:100]}")
                else:
                    print(f"  ❌ Error: {e}")
                    raise

        print("\n✅ Migration completed successfully!")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migration())
