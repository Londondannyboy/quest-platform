"""
Run database migrations

Usage: python3 run_migrations.py
"""

import asyncio
import asyncpg
from pathlib import Path
import structlog

logger = structlog.get_logger()

DATABASE_URL = "postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require"


async def run_migration(conn, migration_file: Path):
    """
    Run a single migration file

    Args:
        conn: Database connection
        migration_file: Path to .sql file
    """
    logger.info("migration.start", file=migration_file.name)

    try:
        # Read SQL file
        sql = migration_file.read_text()

        # Execute migration
        await conn.execute(sql)

        logger.info("migration.success", file=migration_file.name)
        return True

    except Exception as e:
        logger.error(
            "migration.failed",
            file=migration_file.name,
            error=str(e)
        )
        return False


async def run_all_migrations():
    """Run all pending migrations"""
    migrations_dir = Path(__file__).parent / "migrations"

    # Get all .sql files sorted by name
    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        logger.warning("migration.none_found")
        return

    logger.info("migration.found", count=len(migration_files))

    success_count = 0
    failed_count = 0

    # Run each migration in a separate connection to avoid transaction issues
    for migration_file in migration_files:
        # Skip old migrations that might already be applied
        if migration_file.name in ["001_initial_schema.sql", "002_create_users.sql", "003_template_intelligence.sql", "004_cluster_research.sql", "seed_example_data.sql"]:
            logger.info("migration.skipped", file=migration_file.name, reason="old_migration")
            continue

        conn = await asyncpg.connect(DATABASE_URL)
        try:
            success = await run_migration(conn, migration_file)

            if success:
                success_count += 1
            else:
                failed_count += 1
        finally:
            await conn.close()

    logger.info(
        "migration.complete",
        total=len(migration_files),
        success=success_count,
        failed=failed_count
    )


if __name__ == "__main__":
    print("Running database migrations...")
    asyncio.run(run_all_migrations())
    print("Done!")
