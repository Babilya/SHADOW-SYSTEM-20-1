"""
Profile Service - управління профілями та паролями
SHADOW SYSTEM iO v2.0
"""
import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from database.models import UserProfile, UserSession
from utils.db import async_session

logger = logging.getLogger(__name__)
ph = PasswordHasher()


class ProfileService:
    """Сервіс управління профілями користувачів"""
    
    async def get_profile(self, telegram_id: str) -> Optional[UserProfile]:
        """Отримати профіль за telegram_id"""
        async with async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(UserProfile).where(UserProfile.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()
    
    async def create_profile(self, telegram_id: str, **kwargs) -> UserProfile:
        """Створити новий профіль"""
        async with async_session() as session:
            profile = UserProfile(telegram_id=telegram_id, **kwargs)
            session.add(profile)
            await session.commit()
            await session.refresh(profile)
            logger.info(f"Created profile for {telegram_id}")
            return profile
    
    async def get_or_create_profile(self, telegram_id: str, **defaults) -> UserProfile:
        """Отримати або створити профіль"""
        profile = await self.get_profile(telegram_id)
        if not profile:
            profile = await self.create_profile(telegram_id, **defaults)
        return profile
    
    async def update_profile(self, telegram_id: str, **kwargs) -> Optional[UserProfile]:
        """Оновити профіль"""
        async with async_session() as session:
            from sqlalchemy import select, update
            await session.execute(
                update(UserProfile)
                .where(UserProfile.telegram_id == telegram_id)
                .values(**kwargs, updated_at=datetime.now())
            )
            await session.commit()
            result = await session.execute(
                select(UserProfile).where(UserProfile.telegram_id == telegram_id)
            )
            profile = result.scalar_one_or_none()
            if profile:
                logger.info(f"Updated profile for {telegram_id}")
            return profile
    
    def hash_password(self, password: str) -> str:
        """Хешувати пароль (Argon2)"""
        return ph.hash(password)
    
    def verify_password(self, password_hash: str, password: str) -> bool:
        """Перевірити пароль"""
        try:
            ph.verify(password_hash, password)
            return True
        except VerifyMismatchError:
            return False
    
    async def set_password(self, telegram_id: str, password: str) -> bool:
        """Встановити пароль для профілю"""
        password_hash = self.hash_password(password)
        result = await self.update_profile(
            telegram_id,
            password_hash=password_hash,
            password_enabled=True
        )
        if result:
            logger.info(f"Password set for {telegram_id}")
        return result is not None
    
    async def disable_password(self, telegram_id: str) -> bool:
        """Вимкнути пароль"""
        result = await self.update_profile(
            telegram_id,
            password_hash=None,
            password_enabled=False
        )
        return result is not None
    
    async def check_password(self, telegram_id: str, password: str) -> bool:
        """Перевірити пароль користувача"""
        profile = await self.get_profile(telegram_id)
        if not profile or not profile.password_hash:
            return True
        return self.verify_password(profile.password_hash, password)
    
    async def create_session(self, telegram_id: str) -> UserSession:
        """Створити нову сесію"""
        async with async_session() as session:
            from sqlalchemy import delete
            await session.execute(
                delete(UserSession).where(UserSession.telegram_id == telegram_id)
            )
            
            user_session = UserSession(
                telegram_id=telegram_id,
                session_token=secrets.token_hex(32),
                last_activity=datetime.now(),
                last_password_check=datetime.now(),
                is_authenticated=True
            )
            session.add(user_session)
            await session.commit()
            await session.refresh(user_session)
            return user_session
    
    async def get_session(self, telegram_id: str) -> Optional[UserSession]:
        """Отримати активну сесію"""
        async with async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(UserSession).where(UserSession.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()
    
    async def update_activity(self, telegram_id: str) -> None:
        """Оновити час останньої активності"""
        async with async_session() as session:
            from sqlalchemy import update
            await session.execute(
                update(UserSession)
                .where(UserSession.telegram_id == telegram_id)
                .values(last_activity=datetime.now())
            )
            await session.commit()
    
    async def needs_password_check(self, telegram_id: str) -> bool:
        """Перевірити чи потрібна повторна автентифікація"""
        profile = await self.get_profile(telegram_id)
        if not profile or not profile.password_enabled:
            return False
        
        user_session = await self.get_session(telegram_id)
        if not user_session or not user_session.last_password_check:
            return True
        
        timeout_hours = profile.session_timeout_hours or 6
        elapsed = datetime.now() - user_session.last_password_check
        return elapsed > timedelta(hours=timeout_hours)
    
    async def authenticate(self, telegram_id: str, password: str) -> bool:
        """Автентифікувати користувача"""
        if not await self.check_password(telegram_id, password):
            return False
        
        async with async_session() as session:
            from sqlalchemy import update
            await session.execute(
                update(UserSession)
                .where(UserSession.telegram_id == telegram_id)
                .values(
                    last_password_check=datetime.now(),
                    is_authenticated=True
                )
            )
            await session.commit()
        return True
    
    async def get_managers_by_leader(self, leader_id: str) -> list:
        """Отримати менеджерів лідера"""
        async with async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(UserProfile).where(UserProfile.leader_id == leader_id)
            )
            return result.scalars().all()
    
    async def link_manager_to_leader(self, manager_telegram_id: str, leader_telegram_id: str) -> bool:
        """Прив'язати менеджера до лідера"""
        result = await self.update_profile(manager_telegram_id, leader_id=leader_telegram_id)
        if result:
            logger.info(f"Linked manager {manager_telegram_id} to leader {leader_telegram_id}")
        return result is not None
    
    def format_profile(self, profile: UserProfile) -> str:
        """Форматувати профіль для відображення"""
        password_status = "🔐 Увімкнено" if profile.password_enabled else "🔓 Вимкнено"
        timeout = f"{profile.session_timeout_hours}г" if profile.password_enabled else "—"
        
        return f"""👤 <b>МІЙ ПРОФІЛЬ</b>

<b>📋 Основні дані:</b>
├ Ім'я: <code>{profile.display_name or '—'}</code>
├ Email: <code>{profile.email or '—'}</code>
├ Проект: <code>{profile.project_name or '—'}</code>
└ Цілі: <code>{profile.project_goals or '—'}</code>

<b>🔒 Безпека:</b>
├ Пароль: {password_status}
└ Таймаут сесії: {timeout}

<b>⚙️ Налаштування:</b>
├ Часовий пояс: {profile.timezone}
├ Мова: {profile.language.upper()}
└ Сповіщення: {'✅' if profile.notifications_enabled else '❌'}"""


profile_service = ProfileService()
