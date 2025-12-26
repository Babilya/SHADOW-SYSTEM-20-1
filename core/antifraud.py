import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from collections import defaultdict
from sqlalchemy import text

logger = logging.getLogger(__name__)

@dataclass
class SuspiciousActivity:
    user_id: int
    activity_type: str
    count: int
    first_seen: datetime
    last_seen: datetime
    details: Optional[str] = None

class AntiFraudService:
    def __init__(self):
        self.activity_tracker: Dict[int, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
        self.blocked_users: set = set()
        self.warnings: Dict[int, int] = defaultdict(int)
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
        self.thresholds = {
            "failed_login": {"count": 5, "window": 300, "action": "block"},
            "rapid_messages": {"count": 50, "window": 60, "action": "warn"},
            "key_attempts": {"count": 10, "window": 600, "action": "block"},
            "role_changes": {"count": 3, "window": 60, "action": "alert"},
            "api_abuse": {"count": 100, "window": 60, "action": "block"}
        }
    
    async def start(self):
        self._running = True
        self._task = asyncio.create_task(self._cleanup_loop())
        await self._load_blocked_users()
        logger.info("AntiFraudService started")
    
    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
    
    async def _load_blocked_users(self):
        try:
            from database.db import async_session
            async with async_session() as session:
                result = await session.execute(
                    text("SELECT user_id FROM security_blocks WHERE is_active = true AND block_type = 'antifraud'")
                )
                for row in result.fetchall():
                    self.blocked_users.add(int(row[0]))
                logger.info(f"Loaded {len(self.blocked_users)} blocked users")
        except Exception as e:
            logger.error(f"Failed to load blocked users: {e}")
    
    async def _cleanup_loop(self):
        while self._running:
            try:
                now = datetime.now()
                for user_id in list(self.activity_tracker.keys()):
                    for activity_type in list(self.activity_tracker[user_id].keys()):
                        threshold = self.thresholds.get(activity_type, {})
                        window = threshold.get("window", 300)
                        cutoff = now - timedelta(seconds=window)
                        
                        self.activity_tracker[user_id][activity_type] = [
                            t for t in self.activity_tracker[user_id][activity_type]
                            if t > cutoff
                        ]
                        
                        if not self.activity_tracker[user_id][activity_type]:
                            del self.activity_tracker[user_id][activity_type]
                    
                    if not self.activity_tracker[user_id]:
                        del self.activity_tracker[user_id]
                
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Antifraud cleanup error: {e}")
    
    async def track_activity(self, user_id: int, activity_type: str, details: Optional[str] = None) -> dict:
        if user_id in self.blocked_users:
            return {"allowed": False, "reason": "blocked"}
        
        now = datetime.now()
        self.activity_tracker[user_id][activity_type].append(now)
        
        threshold = self.thresholds.get(activity_type)
        if not threshold:
            return {"allowed": True}
        
        window = threshold["window"]
        max_count = threshold["count"]
        action = threshold["action"]
        
        cutoff = now - timedelta(seconds=window)
        recent_count = len([t for t in self.activity_tracker[user_id][activity_type] if t > cutoff])
        
        if recent_count > max_count:
            if action == "block":
                await self._block_user(user_id, activity_type, recent_count, details)
                return {"allowed": False, "reason": "blocked", "activity": activity_type}
            elif action == "warn":
                self.warnings[user_id] += 1
                if self.warnings[user_id] >= 3:
                    await self._block_user(user_id, activity_type, recent_count, details)
                    return {"allowed": False, "reason": "blocked_after_warnings"}
                return {"allowed": True, "warning": True, "warnings_count": self.warnings[user_id]}
            elif action == "alert":
                await self._send_alert(user_id, activity_type, recent_count, details)
                return {"allowed": True, "alert_sent": True}
        
        return {"allowed": True}
    
    async def _block_user(self, user_id: int, activity_type: str, count: int, details: Optional[str] = None):
        self.blocked_users.add(user_id)
        
        try:
            from database.db import async_session
            async with async_session() as session:
                await session.execute(
                    text("""
                        INSERT INTO security_blocks (user_id, block_type, reason, blocked_by, is_active, created_at)
                        VALUES (:user_id, 'antifraud', :reason, 'system', true, NOW())
                    """),
                    {
                        "user_id": str(user_id),
                        "reason": f"Автоблокування: {activity_type} ({count} дій). {details or ''}"
                    }
                )
                await session.commit()
            
            logger.warning(f"User {user_id} auto-blocked for {activity_type}")
        except Exception as e:
            logger.error(f"Failed to block user {user_id}: {e}")
    
    async def _send_alert(self, user_id: int, activity_type: str, count: int, details: Optional[str] = None):
        try:
            from database.db import async_session
            async with async_session() as session:
                await session.execute(
                    text("""
                        INSERT INTO audit_logs (user_id, action, category, severity, details, action_type, created_at)
                        VALUES (:user_id, :action, 'security', 'warning', :details, 'antifraud_alert', NOW())
                    """),
                    {
                        "user_id": str(user_id),
                        "action": f"Підозріла активність: {activity_type}",
                        "details": f"Кількість: {count}. {details or ''}"
                    }
                )
                await session.commit()
            
            logger.warning(f"Security alert for user {user_id}: {activity_type} ({count})")
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
    
    async def unblock_user(self, user_id: int) -> bool:
        self.blocked_users.discard(user_id)
        self.warnings[user_id] = 0
        
        try:
            from database.db import async_session
            async with async_session() as session:
                await session.execute(
                    text("UPDATE security_blocks SET is_active = false WHERE user_id = :user_id AND block_type = 'antifraud'"),
                    {"user_id": str(user_id)}
                )
                await session.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to unblock user {user_id}: {e}")
            return False
    
    def is_blocked(self, user_id: int) -> bool:
        return user_id in self.blocked_users
    
    def get_user_stats(self, user_id: int) -> dict:
        return {
            "user_id": user_id,
            "is_blocked": user_id in self.blocked_users,
            "warnings": self.warnings.get(user_id, 0),
            "activity": {
                k: len(v) for k, v in self.activity_tracker.get(user_id, {}).items()
            }
        }

antifraud_service = AntiFraudService()
