import asyncpg
import redis.asyncio as redis
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class Database:
    _pool = None
    _redis = None

    @classmethod
    async def get_pool(cls):
        if cls._pool is None:
            try:
                cls._pool = await asyncpg.create_pool(
                    host=settings.POSTGRES_HOST,
                    port=settings.POSTGRES_PORT,
                    user=settings.POSTGRES_USER,
                    password=settings.POSTGRES_PASSWORD,
                    database=settings.POSTGRES_DB,
                    min_size=5,
                    max_size=20
                )
                logger.info("PostgreSQL pool created")
            except Exception as e:
                logger.error(f"Failed to create pool: {e}")
                raise
        return cls._pool

    @classmethod
    async def get_redis(cls):
        if cls._redis is None:
            try:
                cls._redis = await redis.from_url(
                    f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                    decode_responses=True
                )
                logger.info("Redis connected")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Using mock redis.")
                cls._redis = None
        return cls._redis

    @classmethod
    async def close(cls):
        if cls._pool:
            await cls._pool.close()
        if cls._redis:
            await cls._redis.close()

async def execute_query(query: str, *args):
    pool = await Database.get_pool()
    async with pool.acquire() as conn:
        await conn.execute(query, *args)

async def fetchrow_query(query: str, *args):
    pool = await Database.get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, *args)

async def fetch_query(query: str, *args):
    pool = await Database.get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(query, *args)
