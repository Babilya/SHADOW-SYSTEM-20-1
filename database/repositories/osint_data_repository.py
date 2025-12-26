import logging
from typing import List, Optional
from sqlmodel import Session, select, delete
from database.models import OSINTData
from datetime import datetime, timedelta
from .base import BaseRepository

logger = logging.getLogger(__name__)


class OSINTDataRepository(BaseRepository[OSINTData]):
    """Repository for OSINTData model operations"""
    
    def __init__(self, session: Session):
        super().__init__(session, OSINTData)
    
    async def get_user_osint_data(self, telegram_id: int, data_type: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[OSINTData]:
        """Get OSINT data for user"""
        try:
            # Match the telegram_id stored in OSINTData.user_id
            statement = select(OSINTData).where(OSINTData.user_id == str(telegram_id))
            if data_type:
                statement = statement.where(OSINTData.data_type == data_type)
            statement = statement.order_by(OSINTData.created_at.desc()).offset(skip).limit(limit)
            result = await self.session.execute(statement)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting OSINT data for user {telegram_id}: {e}")
            raise
    
    async def cleanup_expired_data(self, retention_days: int = 30) -> int:
        """Delete expired OSINT data"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            statement = delete(OSINTData).where(OSINTData.expires_at <= cutoff_date)
            result = await self.session.exec(statement)
            await self.session.commit()
            deleted_count = result.rowcount
            logger.info(f"Cleaned up {deleted_count} expired OSINT entries")
            return deleted_count
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error cleaning expired OSINT data: {e}")
            raise
