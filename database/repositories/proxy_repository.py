import logging
from typing import List, Optional
from sqlmodel import Session, select, func
from database.models import Proxy
from datetime import datetime
from .base import BaseRepository

logger = logging.getLogger(__name__)


class ProxyRepository(BaseRepository[Proxy]):
    """Repository for Proxy model operations"""
    
    def __init__(self, session: Session):
        super().__init__(session, Proxy)
    
    async def get_user_proxies(self, user_id: int, is_active: Optional[bool] = None, skip: int = 0, limit: int = 100) -> List[Proxy]:
        """Get user's proxies"""
        try:
            statement = select(Proxy).where(Proxy.owner_id == user_id)
            if is_active is not None:
                statement = statement.where(Proxy.is_active == is_active)
            statement = statement.offset(skip).limit(limit)
            result = self.session.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"Error getting proxies for user {user_id}: {e}")
            raise
    
    async def get_available_proxy(self, user_id: int) -> Optional[Proxy]:
        """Get best available proxy for user"""
        try:
            statement = select(Proxy).where(
                Proxy.owner_id == user_id,
                Proxy.is_active == True,
                Proxy.failures_count < 5
            ).order_by(Proxy.response_time, Proxy.failures_count).limit(1)
            result = self.session.exec(statement)
            return result.first()
        except Exception as e:
            logger.error(f"Error getting available proxy for user {user_id}: {e}")
            raise
    
    async def update_proxy_performance(self, proxy_id: int, success: bool, response_time: float) -> Optional[Proxy]:
        """Update proxy performance metrics"""
        try:
            proxy = self.get_by_id(proxy_id)
            if proxy:
                if success:
                    proxy.success_rate = (proxy.success_rate * 0.9) + (100 * 0.1)
                    proxy.failures_count = 0
                else:
                    proxy.success_rate = (proxy.success_rate * 0.9) + (0 * 0.1)
                    proxy.failures_count += 1
                    if proxy.failures_count >= 10:
                        proxy.is_active = False
                
                proxy.response_time = (proxy.response_time + response_time) / 2
                proxy.last_check = datetime.utcnow()
                return self.update(proxy)
            return None
        except Exception as e:
            logger.error(f"Error updating proxy performance {proxy_id}: {e}")
            raise
