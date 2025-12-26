import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import text

logger = logging.getLogger(__name__)

class KeyNotificationService:
    def __init__(self):
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self.bot = None
    
    def set_bot(self, bot):
        self.bot = bot
    
    async def start(self):
        self._running = True
        self._task = asyncio.create_task(self._notification_loop())
        logger.info("KeyNotificationService started")
    
    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _notification_loop(self):
        while self._running:
            try:
                await self._check_expiring_keys()
                await asyncio.sleep(3600)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Key notification error: {e}")
                await asyncio.sleep(60)
    
    async def _check_expiring_keys(self):
        try:
            from database.db import async_session
            async with async_session() as session:
                now = datetime.now()
                in_3_days = now + timedelta(days=3)
                in_7_days = now + timedelta(days=7)
                
                result = await session.execute(
                    text("""
                        SELECT k.id, k.code, k.user_id, k.expires_at, k.expires_notified_3d, k.expires_notified_7d,
                               p.leader_id, p.leader_username
                        FROM keys k
                        LEFT JOIN projects p ON k.id = p.key_id
                        WHERE k.is_used = true 
                        AND k.expires_at IS NOT NULL
                        AND k.expires_at > :now
                        AND (
                            (k.expires_at <= :in_7_days AND (k.expires_notified_7d IS NULL OR k.expires_notified_7d = false))
                            OR
                            (k.expires_at <= :in_3_days AND (k.expires_notified_3d IS NULL OR k.expires_notified_3d = false))
                        )
                    """),
                    {"now": now, "in_3_days": in_3_days, "in_7_days": in_7_days}
                )
                
                rows = result.fetchall()
                for row in rows:
                    days_left = (row.expires_at - now).days
                    await self._send_notification(row, days_left, session)
                
                await session.commit()
                
                if rows:
                    logger.info(f"Sent {len(rows)} key expiration notifications")
                    
        except Exception as e:
            logger.error(f"Failed to check expiring keys: {e}")
    
    async def _send_notification(self, key_row, days_left: int, session):
        try:
            user_id = key_row.leader_id or key_row.user_id
            if not user_id:
                return
            
            if days_left <= 3:
                message = (
                    f"⚠️ <b>ТЕРМІНОВО!</b>\n\n"
                    f"Ваш ключ <code>{key_row.code}</code> закінчується через <b>{days_left}</b> дні!\n\n"
                    f"📅 Дата закінчення: {key_row.expires_at.strftime('%d.%m.%Y %H:%M')}\n\n"
                    f"Продовжіть підписку, щоб не втратити доступ до системи."
                )
                await session.execute(
                    text("UPDATE keys SET expires_notified_3d = true WHERE id = :id"),
                    {"id": key_row.id}
                )
            else:
                message = (
                    f"📢 <b>Нагадування</b>\n\n"
                    f"Ваш ключ <code>{key_row.code}</code> закінчується через <b>{days_left}</b> днів.\n\n"
                    f"📅 Дата закінчення: {key_row.expires_at.strftime('%d.%m.%Y %H:%M')}\n\n"
                    f"Рекомендуємо продовжити підписку заздалегідь."
                )
                await session.execute(
                    text("UPDATE keys SET expires_notified_7d = true WHERE id = :id"),
                    {"id": key_row.id}
                )
            
            if self.bot:
                try:
                    await self.bot.send_message(int(user_id), message, parse_mode="HTML")
                except Exception as e:
                    logger.warning(f"Failed to send notification to {user_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to send key notification: {e}")
    
    async def check_key_expiry(self, key_id: int) -> Optional[dict]:
        try:
            from database.db import async_session
            async with async_session() as session:
                result = await session.execute(
                    text("SELECT * FROM keys WHERE id = :id"),
                    {"id": key_id}
                )
                row = result.fetchone()
                if row and row.expires_at:
                    days_left = (row.expires_at - datetime.now()).days
                    return {
                        "key_id": key_id,
                        "expires_at": row.expires_at,
                        "days_left": days_left,
                        "is_expired": days_left < 0,
                        "is_expiring_soon": days_left <= 7
                    }
                return None
        except Exception as e:
            logger.error(f"Failed to check key expiry: {e}")
            return None

key_notification_service = KeyNotificationService()
