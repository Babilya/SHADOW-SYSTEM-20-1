import logging
from typing import AsyncGenerator, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./shadow_system.db")

def prepare_async_url(url: str) -> str:
    if not url.startswith("postgresql://"):
        return url.replace("sqlite:", "sqlite+aiosqlite:", 1) if "sqlite" in url else url
    
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    query_params.pop('sslmode', None)
    new_query = urlencode(query_params, doseq=True)
    new_parsed = parsed._replace(
        scheme='postgresql+asyncpg',
        query=new_query
    )
    return urlunparse(new_parsed)

ASYNC_DATABASE_URL = prepare_async_url(DATABASE_URL)

# Async engine for async operations
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True
)

# Create session factory
async_session = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def init_db():
    """Initialize database tables"""
    from database.models import Base
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database initialized")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session"""
    async with async_session() as session:
        yield session


@asynccontextmanager
async def get_db():
    """Context manager for database session"""
    async with async_session() as session:
        yield session


sync_engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)

def get_sync_session() -> Session:
    """Get sync database session (for Celery tasks)"""
    return SessionLocal()


class DBManager:
    """Database manager for common operations"""
    
    def __init__(self):
        self.async_engine = async_engine
        self.async_session = async_session
    
    async def health_check(self) -> bool:
        """Check database connection"""
        try:
            async with async_session() as session:
                await session.exec("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


db_manager = DBManager()
