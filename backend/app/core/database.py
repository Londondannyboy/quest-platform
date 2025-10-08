"""
Quest Platform v2.2 - Database Connection Management
Async PostgreSQL connection pool using asyncpg
"""

import asyncpg
from typing import Optional
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Global connection pool
_pool: Optional[asyncpg.Pool] = None


async def init_db() -> asyncpg.Pool:
    """
    Initialize database connection pool
    """
    global _pool

    if _pool is not None:
        logger.warning("quest.database.already_initialized")
        return _pool

    try:
        _pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=settings.DB_POOL_SIZE // 2,
            max_size=settings.DB_POOL_SIZE,
            max_inactive_connection_lifetime=300,
            command_timeout=60,
        )

        # Test connection
        async with _pool.acquire() as conn:
            version = await conn.fetchval("SELECT version()")
            logger.info("quest.database.connected", version=version[:50])

        return _pool

    except Exception as e:
        logger.error("quest.database.connection_failed", error=str(e), exc_info=e)
        raise


async def close_db():
    """
    Close database connection pool
    """
    global _pool

    if _pool is None:
        return

    try:
        await _pool.close()
        logger.info("quest.database.closed")
        _pool = None
    except Exception as e:
        logger.error("quest.database.close_failed", error=str(e), exc_info=e)


def get_db() -> asyncpg.Pool:
    """
    Get database connection pool

    Raises:
        RuntimeError: If database not initialized
    """
    if _pool is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _pool


async def execute_query(query: str, *args):
    """
    Execute a query and return results

    Args:
        query: SQL query
        *args: Query parameters

    Returns:
        Query results
    """
    pool = get_db()

    async with pool.acquire() as conn:
        return await conn.fetch(query, *args)


async def execute_one(query: str, *args):
    """
    Execute a query and return a single row

    Args:
        query: SQL query
        *args: Query parameters

    Returns:
        Single row result or None
    """
    pool = get_db()

    async with pool.acquire() as conn:
        return await conn.fetchrow(query, *args)


async def execute_value(query: str, *args):
    """
    Execute a query and return a single value

    Args:
        query: SQL query
        *args: Query parameters

    Returns:
        Single value result or None
    """
    pool = get_db()

    async with pool.acquire() as conn:
        return await conn.fetchval(query, *args)


async def execute_mutation(query: str, *args):
    """
    Execute an INSERT/UPDATE/DELETE query

    Args:
        query: SQL query
        *args: Query parameters

    Returns:
        Status message
    """
    pool = get_db()

    async with pool.acquire() as conn:
        return await conn.execute(query, *args)
