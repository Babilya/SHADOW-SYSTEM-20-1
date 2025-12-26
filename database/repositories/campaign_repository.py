import logging
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, func
from database.models import Campaign, CampaignStatus
from datetime import datetime
from .base import BaseRepository

logger = logging.getLogger(__name__)


class CampaignRepository(BaseRepository[Campaign]):
    """Repository for Campaign model operations"""
    
    def __init__(self, session: Session):
        super().__init__(session, Campaign)
    
    async def get_user_campaigns(self, user_id: int, status: Optional[CampaignStatus] = None, skip: int = 0, limit: int = 100) -> List[Campaign]:
        """Get user's campaigns"""
        try:
            statement = select(Campaign).where(Campaign.owner_id == user_id)
            if status:
                statement = statement.where(Campaign.status == status)
            statement = statement.offset(skip).limit(limit)
            result = self.session.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"Error getting campaigns for user {user_id}: {e}")
            raise
    
    async def get_running_campaigns(self) -> List[Campaign]:
        """Get all running campaigns"""
        try:
            statement = select(Campaign).where(Campaign.status == CampaignStatus.RUNNING)
            result = self.session.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"Error getting running campaigns: {e}")
            raise
    
    async def update_campaign_stats(self, campaign_id: int, sent_count: int, success_count: int, failed_count: int) -> Optional[Campaign]:
        """Update campaign statistics"""
        try:
            campaign = self.get_by_id(campaign_id)
            if campaign:
                campaign.sent_count = sent_count
                campaign.success_count = success_count
                campaign.failed_count = failed_count
                campaign.updated_at = datetime.utcnow()
                return self.update(campaign)
            return None
        except Exception as e:
            logger.error(f"Error updating campaign stats {campaign_id}: {e}")
            raise
