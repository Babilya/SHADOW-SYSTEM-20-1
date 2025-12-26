import logging
import os
from typing import AsyncGenerator
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from database.models import Base

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///shadow_security.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def prepare_async_url(url: str) -> str:
    """Convert URL to asyncpg-compatible format by removing sslmode parameter"""
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

if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = prepare_async_url(DATABASE_URL)
    SYNC_DATABASE_URL = DATABASE_URL
else:
    ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite:", "sqlite+aiosqlite:", 1) if "sqlite" in DATABASE_URL else DATABASE_URL
    SYNC_DATABASE_URL = DATABASE_URL

sync_engine = create_engine(SYNC_DATABASE_URL)
SessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
)

async_session = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database initialized")

def get_sync_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

class DBManager:
    def __init__(self):
        self.engine = async_engine
        self.session = async_session
    
    def add_user(self, telegram_id, username, first_name):
        db = SessionLocal()
        try:
            from database.models import User
            user = db.query(User).filter(User.telegram_id == str(telegram_id)).first()
            if not user:
                user = User(telegram_id=str(telegram_id), username=username, first_name=first_name)
                db.add(user)
                db.commit()
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            db.rollback()
        finally:
            db.close()

db = DBManager()
