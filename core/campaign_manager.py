import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

class CampaignType(str, Enum):
    BROADCAST = "broadcast"
    TARGETED = "targeted"
    DRIP = "drip"
    SEQUENTIAL = "sequential"

@dataclass
class Campaign:
    id: str
    project_id: int
    name: str
    type: CampaignType
    status: CampaignStatus
    message_template: str
    target_chats: List[str] = field(default_factory=list)
    target_users: List[str] = field(default_factory=list)
    bot_ids: List[int] = field(default_factory=list)
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    messages_sent: int = 0
    messages_failed: int = 0
    messages_total: int = 0
    interval_seconds: int = 30
    created_at: datetime = field(default_factory=datetime.now)
    settings: Dict[str, Any] = field(default_factory=dict)

class CampaignManager:
    def __init__(self):
        self.campaigns: Dict[str, Campaign] = {}
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self._running = False
    
    def create_campaign(
        self,
        project_id: int,
        name: str,
        campaign_type: CampaignType,
        message_template: str,
        target_chats: List[str] = None,
        target_users: List[str] = None,
        bot_ids: List[int] = None,
        scheduled_at: Optional[datetime] = None,
        interval_seconds: int = 30,
        settings: Dict[str, Any] = None
    ) -> Campaign:
        campaign_id = str(uuid.uuid4())[:8]
        
        campaign = Campaign(
            id=campaign_id,
            project_id=project_id,
            name=name,
            type=campaign_type,
            status=CampaignStatus.DRAFT,
            message_template=message_template,
            target_chats=target_chats or [],
            target_users=target_users or [],
            bot_ids=bot_ids or [],
            scheduled_at=scheduled_at,
            interval_seconds=interval_seconds,
            settings=settings or {}
        )
        
        self.campaigns[campaign_id] = campaign
        logger.info(f"Campaign created: {campaign_id} - {name}")
        return campaign
    
    def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        return self.campaigns.get(campaign_id)
    
    def get_project_campaigns(self, project_id: int) -> List[Campaign]:
        return [c for c in self.campaigns.values() if c.project_id == project_id]
    
    def update_campaign_status(self, campaign_id: str, status: CampaignStatus) -> bool:
        campaign = self.campaigns.get(campaign_id)
        if campaign:
            campaign.status = status
            if status == CampaignStatus.RUNNING:
                campaign.started_at = datetime.now()
            elif status in [CampaignStatus.COMPLETED, CampaignStatus.CANCELLED]:
                campaign.completed_at = datetime.now()
            logger.info(f"Campaign {campaign_id} status: {status}")
            return True
        return False
    
    async def start_campaign(self, campaign_id: str) -> Dict[str, Any]:
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return {"success": False, "error": "Campaign not found"}
        
        if campaign.status == CampaignStatus.RUNNING:
            return {"success": False, "error": "Campaign already running"}
        
        campaign.status = CampaignStatus.RUNNING
        campaign.started_at = datetime.now()
        
        task = asyncio.create_task(self._run_campaign(campaign_id))
        self.active_tasks[campaign_id] = task
        
        logger.info(f"Campaign started: {campaign_id}")
        return {"success": True, "message": "Campaign started"}
    
    async def pause_campaign(self, campaign_id: str) -> Dict[str, Any]:
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return {"success": False, "error": "Campaign not found"}
        
        if campaign.status != CampaignStatus.RUNNING:
            return {"success": False, "error": "Campaign not running"}
        
        if campaign_id in self.active_tasks:
            self.active_tasks[campaign_id].cancel()
            del self.active_tasks[campaign_id]
        
        campaign.status = CampaignStatus.PAUSED
        logger.info(f"Campaign paused: {campaign_id}")
        return {"success": True, "message": "Campaign paused"}
    
    async def stop_campaign(self, campaign_id: str) -> Dict[str, Any]:
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return {"success": False, "error": "Campaign not found"}
        
        if campaign_id in self.active_tasks:
            self.active_tasks[campaign_id].cancel()
            del self.active_tasks[campaign_id]
        
        campaign.status = CampaignStatus.CANCELLED
        campaign.completed_at = datetime.now()
        logger.info(f"Campaign stopped: {campaign_id}")
        return {"success": True, "message": "Campaign stopped"}
    
    async def _run_campaign(self, campaign_id: str):
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return
        
        try:
            total_targets = len(campaign.target_users) + len(campaign.target_chats)
            campaign.messages_total = total_targets
            
            for target in campaign.target_users:
                if campaign.status != CampaignStatus.RUNNING:
                    break
                
                success = await self._send_message(campaign, target)
                if success:
                    campaign.messages_sent += 1
                else:
                    campaign.messages_failed += 1
                
                await asyncio.sleep(campaign.interval_seconds)
            
            for chat in campaign.target_chats:
                if campaign.status != CampaignStatus.RUNNING:
                    break
                
                success = await self._send_to_chat(campaign, chat)
                if success:
                    campaign.messages_sent += 1
                else:
                    campaign.messages_failed += 1
                
                await asyncio.sleep(campaign.interval_seconds)
            
            if campaign.status == CampaignStatus.RUNNING:
                campaign.status = CampaignStatus.COMPLETED
                campaign.completed_at = datetime.now()
                logger.info(f"Campaign completed: {campaign_id}")
                
        except asyncio.CancelledError:
            logger.info(f"Campaign {campaign_id} cancelled")
        except Exception as e:
            campaign.status = CampaignStatus.FAILED
            logger.error(f"Campaign {campaign_id} failed: {e}")
    
    async def _send_message(self, campaign: Campaign, target: str) -> bool:
        try:
            await asyncio.sleep(0.1)
            logger.debug(f"Message sent to {target}")
            return True
        except Exception as e:
            logger.error(f"Send error: {e}")
            return False
    
    async def _send_to_chat(self, campaign: Campaign, chat: str) -> bool:
        try:
            await asyncio.sleep(0.1)
            logger.debug(f"Message sent to chat {chat}")
            return True
        except Exception as e:
            logger.error(f"Chat send error: {e}")
            return False
    
    def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return {"error": "Campaign not found"}
        
        progress = 0
        if campaign.messages_total > 0:
            progress = round((campaign.messages_sent + campaign.messages_failed) / campaign.messages_total * 100, 1)
        
        success_rate = 0
        total_processed = campaign.messages_sent + campaign.messages_failed
        if total_processed > 0:
            success_rate = round(campaign.messages_sent / total_processed * 100, 1)
        
        return {
            'id': campaign.id,
            'name': campaign.name,
            'status': campaign.status.value,
            'type': campaign.type.value,
            'messages_sent': campaign.messages_sent,
            'messages_failed': campaign.messages_failed,
            'messages_total': campaign.messages_total,
            'progress': progress,
            'success_rate': success_rate,
            'started_at': str(campaign.started_at) if campaign.started_at else None,
            'completed_at': str(campaign.completed_at) if campaign.completed_at else None
        }
    
    def delete_campaign(self, campaign_id: str) -> bool:
        if campaign_id in self.campaigns:
            if campaign_id in self.active_tasks:
                self.active_tasks[campaign_id].cancel()
                del self.active_tasks[campaign_id]
            del self.campaigns[campaign_id]
            return True
        return False

campaign_manager = CampaignManager()
