import asyncpg
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Database:
    _pool: Optional[asyncpg.Pool] = None

    @classmethod
    async def connect(cls, database_url: Optional[str] = None):
        if cls._pool is not None:
            return cls._pool

        db_url = database_url or os.getenv(
            "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/attendance"
        )

        cls._pool = await asyncpg.create_pool(
            db_url, min_size=5, max_size=20, command_timeout=60
        )
        logger.info("Database connection pool created")
        return cls._pool

    @classmethod
    async def disconnect(cls):
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
            logger.info("Database connection pool closed")

    @classmethod
    def get_pool(cls) -> Optional[asyncpg.Pool]:
        return cls._pool


async def get_db() -> asyncpg.Pool:
    pool = Database.get_pool()
    if pool is None:
        pool = await Database.connect()
    return pool
