import logging
from typing import List, Optional
from sqlmodel import Session, select, func
from database.models import BotSession, BotStatus
from datetime import datetime
from .base import BaseRepository

logger = logging.getLogger(__name__)


class BotSessionRepository(BaseRepository[BotSession]):
    """Repository for BotSession model operations"""
    
    def __init__(self, session: Session):
        super().__init__(session, BotSession)
    
    async def get_by_phone(self, phone: str) -> Optional[BotSession]:
        """Get bot session by phone"""
        try:
            statement = select(BotSession).where(BotSession.phone == phone)
            result = self.session.exec(statement)
            return result.first()
        except Exception as e:
            logger.error(f"Error getting bot session by phone {phone}: {e}")
            raise
    
    async def get_active_bots_for_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[BotSession]:
        """Get active bots for user"""
        try:
            statement = select(BotSession).where(
                BotSession.owner_id == user_id,
                BotSession.status == BotStatus.ACTIVE
            ).offset(skip).limit(limit)
            result = self.session.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"Error getting active bots for user {user_id}: {e}")
            raise
    
    async def count_by_status_for_user(self, user_id: int, status: Optional[BotStatus] = None) -> int:
        """Count bots by status for user"""
        try:
            if status:
                statement = select(func.count(BotSession.id)).where(
                    BotSession.owner_id == user_id,
                    BotSession.status == status
                )
            else:
                statement = select(func.count(BotSession.id)).where(BotSession.owner_id == user_id)
            
            result = self.session.exec(statement)
            return result.scalar_one_or_none() or 0
        except Exception as e:
            logger.error(f"Error counting bots for user {user_id}: {e}")
            raise
    
    async def update_bot_status(self, bot_id: int, new_status: BotStatus) -> Optional[BotSession]:
        """Update bot status"""
        try:
            bot = self.get_by_id(bot_id)
            if bot:
                bot.status = new_status
                bot.updated_at = datetime.utcnow()
                return self.update(bot)
            return None
        except Exception as e:
            logger.error(f"Error updating bot status {bot_id}: {e}")
            raise
