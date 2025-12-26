import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
import uuid
from sqlalchemy import text

logger = logging.getLogger(__name__)

@dataclass
class ScheduledMailing:
    id: str
    project_id: str
    name: str
    message_text: str
    scheduled_at: datetime
    target_type: str = "all"
    target_filter: Optional[dict] = None
    media_type: Optional[str] = None
    media_id: Optional[str] = None
    ab_variants: Optional[list] = None
    status: str = "pending"
    created_by: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

class MailingScheduler:
    def __init__(self):
        self.scheduled: Dict[str, ScheduledMailing] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        self._running = True
        self._task = asyncio.create_task(self._scheduler_loop())
        await self._load_from_db()
        logger.info("MailingScheduler started")
    
    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _load_from_db(self):
        try:
            from database.db import async_session
            async with async_session() as session:
                result = await session.execute(
                    text("SELECT * FROM scheduled_mailings WHERE status = 'pending' AND scheduled_at > NOW()")
                )
                rows = result.fetchall()
                for row in rows:
                    mailing = ScheduledMailing(
                        id=str(row.id),
                        project_id=row.project_id or "",
                        name=row.name or "",
                        message_text=row.message_text or "",
                        scheduled_at=row.scheduled_at,
                        target_type=row.target_type or "all",
                        status=row.status or "pending"
                    )
                    self.scheduled[mailing.id] = mailing
                logger.info(f"Loaded {len(rows)} scheduled mailings from DB")
        except Exception as e:
            logger.error(f"Failed to load scheduled mailings: {e}")
    
    async def _scheduler_loop(self):
        while self._running:
            try:
                now = datetime.now()
                for mailing_id, mailing in list(self.scheduled.items()):
                    if mailing.status == "pending" and mailing.scheduled_at <= now:
                        await self._execute_mailing(mailing)
                
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(5)
    
    async def _execute_mailing(self, mailing: ScheduledMailing):
        try:
            mailing.status = "running"
            await self._update_status_in_db(mailing.id, "running")
            
            from core.message_queue import message_queue
            
            recipients = await self._get_recipients(mailing)
            
            await message_queue.create_mailing(
                project_id=mailing.project_id,
                name=mailing.name,
                message_text=mailing.message_text,
                recipients=recipients,
                ab_variants=mailing.ab_variants
            )
            
            mailing.status = "completed"
            await self._update_status_in_db(mailing.id, "completed")
            del self.scheduled[mailing.id]
            
            logger.info(f"Scheduled mailing {mailing.id} executed")
            
        except Exception as e:
            mailing.status = "failed"
            await self._update_status_in_db(mailing.id, "failed")
            logger.error(f"Failed to execute mailing {mailing.id}: {e}")
    
    async def _get_recipients(self, mailing: ScheduledMailing) -> list:
        try:
            from database.db import async_session
            async with async_session() as session:
                if mailing.target_type == "all":
                    result = await session.execute(
                        text("SELECT user_id FROM users WHERE is_blocked = false")
                    )
                else:
                    result = await session.execute(
                        text("SELECT user_id FROM users WHERE project_id = :pid AND is_blocked = false"),
                        {"pid": mailing.project_id}
                    )
                return [row[0] for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get recipients: {e}")
            return []
    
    async def _update_status_in_db(self, mailing_id: str, status: str):
        try:
            from database.db import async_session
            async with async_session() as session:
                await session.execute(
                    text("UPDATE scheduled_mailings SET status = :status WHERE id = :id"),
                    {"status": status, "id": int(mailing_id)}
                )
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to update mailing status: {e}")
    
    async def schedule(
        self,
        project_id: str,
        name: str,
        message_text: str,
        scheduled_at: datetime,
        target_type: str = "all",
        target_filter: Optional[dict] = None,
        ab_variants: Optional[list] = None,
        created_by: Optional[int] = None
    ) -> str:
        try:
            from database.db import async_session
            async with async_session() as session:
                result = await session.execute(
                    text("""
                        INSERT INTO scheduled_mailings 
                        (project_id, name, message_text, scheduled_at, target_type, ab_variants, status, created_by)
                        VALUES (:project_id, :name, :message_text, :scheduled_at, :target_type, :ab_variants, 'pending', :created_by)
                        RETURNING id
                    """),
                    {
                        "project_id": project_id,
                        "name": name,
                        "message_text": message_text,
                        "scheduled_at": scheduled_at,
                        "target_type": target_type,
                        "ab_variants": str(ab_variants) if ab_variants else None,
                        "created_by": created_by
                    }
                )
                row = result.fetchone()
                await session.commit()
                mailing_id = str(row[0])
            
            mailing = ScheduledMailing(
                id=mailing_id,
                project_id=project_id,
                name=name,
                message_text=message_text,
                scheduled_at=scheduled_at,
                target_type=target_type,
                target_filter=target_filter,
                ab_variants=ab_variants,
                created_by=created_by
            )
            self.scheduled[mailing_id] = mailing
            
            logger.info(f"Scheduled mailing {mailing_id} for {scheduled_at}")
            return mailing_id
            
        except Exception as e:
            logger.error(f"Failed to schedule mailing: {e}")
            raise
    
    async def cancel(self, mailing_id: str) -> bool:
        if mailing_id in self.scheduled:
            del self.scheduled[mailing_id]
            await self._update_status_in_db(mailing_id, "cancelled")
            return True
        return False
    
    def get_scheduled(self, project_id: Optional[str] = None) -> List[ScheduledMailing]:
        mailings = list(self.scheduled.values())
        if project_id:
            mailings = [m for m in mailings if m.project_id == project_id]
        return sorted(mailings, key=lambda m: m.scheduled_at)
    
    def get_mailing(self, mailing_id: str) -> Optional[ScheduledMailing]:
        return self.scheduled.get(mailing_id)

mailing_scheduler = MailingScheduler()
