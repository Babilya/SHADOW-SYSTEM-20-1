import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from collections import defaultdict
from sqlalchemy import text

logger = logging.getLogger(__name__)

@dataclass
class UserSegment:
    user_id: int
    tags: Set[str]
    scores: Dict[str, float]
    last_updated: datetime

class SegmentationService:
    def __init__(self):
        self.user_segments: Dict[int, UserSegment] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
        self.tag_rules = {
            "active": {"action_count": 10, "days": 7},
            "power_user": {"action_count": 50, "days": 7},
            "inactive": {"no_actions_days": 14},
            "new_user": {"registered_days": 7},
            "paying": {"has_payment": True},
            "leader": {"role": "leader"},
            "manager": {"role": "manager"},
            "mailing_user": {"campaign_count": 1},
            "osint_user": {"osint_count": 1}
        }
    
    async def start(self):
        self._running = True
        self._task = asyncio.create_task(self._analysis_loop())
        logger.info("SegmentationService started")
    
    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
    
    async def _analysis_loop(self):
        while self._running:
            try:
                await self._analyze_all_users()
                await asyncio.sleep(3600)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Segmentation error: {e}")
                await asyncio.sleep(300)
    
    async def _analyze_all_users(self):
        try:
            from database.db import async_session
            async with async_session() as session:
                result = await session.execute(
                    text("SELECT user_id, role, created_at FROM users WHERE is_blocked = false")
                )
                users = result.fetchall()
            
            analyzed = 0
            for user in users:
                try:
                    await self._analyze_user(user.user_id, user.role, user.created_at)
                    analyzed += 1
                except Exception as e:
                    logger.debug(f"Failed to analyze user {user.user_id}: {e}")
            
            logger.info(f"Analyzed {analyzed}/{len(users)} users for segmentation")
        except Exception as e:
            logger.error(f"Failed to analyze users: {e}")
    
    async def _analyze_user(self, user_id: int, role: str, created_at: datetime):
        from database.db import async_session
        
        tags = set()
        scores = {}
        
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        
        if role == "leader":
            tags.add("leader")
        elif role == "manager":
            tags.add("manager")
        elif role == "admin":
            tags.add("admin")
        
        if created_at and (now - created_at).days <= 7:
            tags.add("new_user")
        
        user_id_int = int(user_id) if isinstance(user_id, str) else user_id
        
        async with async_session() as session:
            try:
                result = await session.execute(
                    text("SELECT COUNT(*) as cnt FROM audit_logs WHERE user_id = :user_id AND created_at > :since"),
                    {"user_id": user_id_int, "since": week_ago}
                )
                action_count = result.fetchone().cnt or 0
                
                if action_count >= 50:
                    tags.add("power_user")
                    scores["activity"] = 1.0
                elif action_count >= 10:
                    tags.add("active")
                    scores["activity"] = 0.6
                elif action_count == 0:
                    tags.add("inactive")
                    scores["activity"] = 0.0
            except Exception:
                pass
            
            try:
                result = await session.execute(
                    text("SELECT COUNT(*) as cnt FROM payments WHERE user_id = :user_id AND status = 'confirmed'"),
                    {"user_id": str(user_id)}
                )
                if result.fetchone().cnt > 0:
                    tags.add("paying")
                    scores["value"] = 1.0
            except Exception:
                pass
        
        async with async_session() as session:
            for tag in tags:
                try:
                    await session.execute(
                        text("""
                            INSERT INTO behavior_tags (user_id, tag, score, created_at, updated_at)
                            VALUES (:user_id, :tag, :score, NOW(), NOW())
                            ON CONFLICT (user_id, tag) DO UPDATE SET score = :score, updated_at = NOW()
                        """),
                        {"user_id": user_id_int, "tag": tag, "score": scores.get(tag.split("_")[0], 1.0)}
                    )
                    await session.commit()
                except Exception:
                    await session.rollback()
        
        self.user_segments[user_id] = UserSegment(
            user_id=user_id,
            tags=tags,
            scores=scores,
            last_updated=now
        )
    
    async def get_user_tags(self, user_id: int) -> List[str]:
        if user_id in self.user_segments:
            return list(self.user_segments[user_id].tags)
        
        try:
            from database.db import async_session
            async with async_session() as session:
                result = await session.execute(
                    text("SELECT tag, score FROM behavior_tags WHERE user_id = :user_id"),
                    {"user_id": user_id}
                )
                return [row.tag for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get user tags: {e}")
            return []
    
    async def get_users_by_tag(self, tag: str) -> List[int]:
        try:
            from database.db import async_session
            async with async_session() as session:
                result = await session.execute(
                    text("SELECT DISTINCT user_id FROM behavior_tags WHERE tag = :tag"),
                    {"tag": tag}
                )
                return [row.user_id for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get users by tag: {e}")
            return []
    
    async def add_manual_tag(self, user_id: int, tag: str, score: float = 1.0) -> bool:
        try:
            from database.db import async_session
            async with async_session() as session:
                await session.execute(
                    text("""
                        INSERT INTO behavior_tags (user_id, tag, score, created_at, updated_at)
                        VALUES (:user_id, :tag, :score, NOW(), NOW())
                    """),
                    {"user_id": user_id, "tag": tag, "score": score}
                )
                await session.commit()
            
            if user_id in self.user_segments:
                self.user_segments[user_id].tags.add(tag)
            
            return True
        except Exception as e:
            logger.error(f"Failed to add manual tag: {e}")
            return False
    
    async def remove_tag(self, user_id: int, tag: str) -> bool:
        try:
            from database.db import async_session
            async with async_session() as session:
                await session.execute(
                    text("DELETE FROM behavior_tags WHERE user_id = :user_id AND tag = :tag"),
                    {"user_id": user_id, "tag": tag}
                )
                await session.commit()
            
            if user_id in self.user_segments:
                self.user_segments[user_id].tags.discard(tag)
            
            return True
        except Exception as e:
            logger.error(f"Failed to remove tag: {e}")
            return False
    
    async def get_segment_stats(self) -> Dict[str, int]:
        try:
            from database.db import async_session
            async with async_session() as session:
                result = await session.execute(
                    text("SELECT tag, COUNT(DISTINCT user_id) as cnt FROM behavior_tags GROUP BY tag")
                )
                return {row.tag: row.cnt for row in result.fetchall()}
        except Exception as e:
            logger.error(f"Failed to get segment stats: {e}")
            return {}

segmentation_service = SegmentationService()
