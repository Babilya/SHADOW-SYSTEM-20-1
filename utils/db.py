import logging
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from database.models import Base

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///shadow_security.db")
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL", "sqlite+aiosqlite:///shadow_security.db")

# Sync engine
sync_engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)

# Async engine
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    future=True,
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

async def get_db():
    async with async_session() as session:
        yield session

class DBManager:
    def __init__(self):
        self.engine = async_engine
        self.session = async_session
    
    def add_user(self, telegram_id, username, first_name):
        db = SessionLocal()
        from database.models import User
        user = db.query(User).filter(User.telegram_id == str(telegram_id)).first()
        if not user:
            user = User(telegram_id=str(telegram_id), username=username, first_name=first_name)
            db.add(user)
            db.commit()
        db.close()

db = DBManager()
