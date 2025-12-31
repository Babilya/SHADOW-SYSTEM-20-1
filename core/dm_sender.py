"""
DM Sender - Розсилка повідомлень в особисті повідомлення
"""
import asyncio
import logging
import random
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class DMStatus(str, Enum):
    PENDING = "pending"
    SENDING = "sending"
    COMPLETED = "completed"
    PAUSED = "paused"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DMTask:
    task_id: str
    name: str
    message_template: str
    target_users: List[int]
    bot_sessions: List[str] = field(default_factory=list)
    status: DMStatus = DMStatus.PENDING
    sent_count: int = 0
    failed_count: int = 0
    total_count: int = 0
    interval_min: float = 30.0
    interval_max: float = 60.0
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    errors: List[Dict[str, Any]] = field(default_factory=list)
    sent_to: List[int] = field(default_factory=list)
    skip_if_recent_chat: bool = True
    personalization: bool = True


class DMSenderService:
    def __init__(self):
        self.tasks: Dict[str, DMTask] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.blacklist: set = set()
        self.recent_sent: Dict[int, datetime] = {}
        self.stats = {
            "total_sent": 0,
            "total_failed": 0,
            "active_tasks": 0
        }
        self.cooldown_hours = 24
    
    def create_task(
        self,
        task_id: str,
        name: str,
        message_template: str,
        target_users: List[int],
        bot_sessions: List[str] = None,
        interval_min: float = 30.0,
        interval_max: float = 60.0,
        personalization: bool = True
    ) -> DMTask:
        """Створення задачі на розсилку в ЛС"""
        
        filtered_users = [
            u for u in target_users 
            if u not in self.blacklist and not self._recently_sent(u)
        ]
        
        task = DMTask(
            task_id=task_id,
            name=name,
            message_template=message_template,
            target_users=filtered_users,
            bot_sessions=bot_sessions or [],
            total_count=len(filtered_users),
            interval_min=interval_min,
            interval_max=interval_max,
            personalization=personalization
        )
        
        self.tasks[task_id] = task
        logger.info(f"Створено DM задачу '{name}' для {len(filtered_users)} користувачів")
        return task
    
    def _recently_sent(self, user_id: int) -> bool:
        if user_id not in self.recent_sent:
            return False
        last_sent = self.recent_sent[user_id]
        hours_passed = (datetime.now() - last_sent).total_seconds() / 3600
        return hours_passed < self.cooldown_hours
    
    async def start_task(self, task_id: str) -> Dict[str, Any]:
        """Запуск розсилки"""
        task = self.tasks.get(task_id)
        if not task:
            return {"error": "Задачу не знайдено"}
        
        if task.status == DMStatus.SENDING:
            return {"error": "Задача вже виконується"}
        
        task.status = DMStatus.SENDING
        task.started_at = datetime.now()
        self.stats["active_tasks"] += 1
        
        async_task = asyncio.create_task(self._execute_dm_task(task_id))
        self.running_tasks[task_id] = async_task
        
        return {
            "status": "started",
            "task_id": task_id,
            "total_users": task.total_count
        }
    
    async def stop_task(self, task_id: str) -> Dict[str, Any]:
        """Зупинка розсилки"""
        task = self.tasks.get(task_id)
        if not task:
            return {"error": "Задачу не знайдено"}
        
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            del self.running_tasks[task_id]
        
        task.status = DMStatus.PAUSED
        self.stats["active_tasks"] = max(0, self.stats["active_tasks"] - 1)
        
        return {
            "status": "stopped",
            "sent_count": task.sent_count,
            "failed_count": task.failed_count
        }
    
    async def _execute_dm_task(self, task_id: str):
        """Виконання розсилки"""
        task = self.tasks.get(task_id)
        if not task:
            return
        
        try:
            from core.session_manager import session_manager
            from telethon.errors import FloodWaitError, UserPrivacyRestrictedError, PeerFloodError
            
            available_sessions = task.bot_sessions or list(session_manager.imported_sessions.keys())
            
            if not available_sessions:
                task.status = DMStatus.FAILED
                task.errors.append({"error": "Немає доступних сесій", "time": datetime.now().isoformat()})
                return
            
            session_index = 0
            flood_wait_count = 0
            
            for user_id in task.target_users:
                if task.status != DMStatus.SENDING:
                    break
                
                if user_id in task.sent_to:
                    continue
                
                session_hash = available_sessions[session_index % len(available_sessions)]
                session_index += 1
                
                try:
                    client = await session_manager.connect_client(session_hash)
                    if not client:
                        task.errors.append({
                            "user_id": user_id,
                            "error": "Не вдалося підключити сесію",
                            "time": datetime.now().isoformat()
                        })
                        task.failed_count += 1
                        continue
                    
                    message = await self._personalize_message(client, user_id, task.message_template)
                    
                    await client.send_message(user_id, message)
                    
                    task.sent_count += 1
                    task.sent_to.append(user_id)
                    self.recent_sent[user_id] = datetime.now()
                    self.stats["total_sent"] += 1
                    flood_wait_count = 0
                    
                    logger.info(f"DM відправлено користувачу {user_id}")
                    
                except FloodWaitError as e:
                    wait_seconds = e.seconds
                    flood_wait_count += 1
                    
                    task.errors.append({
                        "user_id": user_id,
                        "error": f"FloodWait: {wait_seconds}s",
                        "time": datetime.now().isoformat()
                    })
                    
                    logger.warning(f"FloodWait: очікування {wait_seconds}s (спроба {flood_wait_count})")
                    
                    if flood_wait_count >= 3 or wait_seconds > 600:
                        task.status = DMStatus.PAUSED
                        self.stats["active_tasks"] = max(0, self.stats["active_tasks"] - 1)
                        logger.error(f"Занадто багато FloodWait, задача призупинена")
                        return
                    
                    await asyncio.sleep(min(wait_seconds + 10, 600))
                    
                except PeerFloodError:
                    flood_wait_count += 1
                    task.errors.append({
                        "user_id": user_id,
                        "error": "PeerFlood: ліміт надсилань",
                        "time": datetime.now().isoformat()
                    })
                    task.failed_count += 1
                    
                    logger.warning(f"PeerFlood: пауза 5 хвилин")
                    
                    if flood_wait_count >= 3:
                        task.status = DMStatus.PAUSED
                        self.stats["active_tasks"] = max(0, self.stats["active_tasks"] - 1)
                        logger.error(f"Занадто багато PeerFlood, задача призупинена")
                        return
                    
                    await asyncio.sleep(300)
                    
                except UserPrivacyRestrictedError:
                    self.blacklist.add(user_id)
                    task.errors.append({
                        "user_id": user_id,
                        "error": "Privacy: користувач обмежив повідомлення",
                        "time": datetime.now().isoformat()
                    })
                    task.failed_count += 1
                    self.stats["total_failed"] += 1
                    
                except Exception as e:
                    error_msg = str(e)
                    task.errors.append({
                        "user_id": user_id,
                        "error": error_msg,
                        "time": datetime.now().isoformat()
                    })
                    task.failed_count += 1
                    self.stats["total_failed"] += 1
                    
                    if "privacy" in error_msg.lower() or "blocked" in error_msg.lower():
                        self.blacklist.add(user_id)
                
                delay = random.uniform(task.interval_min, task.interval_max)
                await asyncio.sleep(delay)
            
            task.status = DMStatus.COMPLETED
            task.completed_at = datetime.now()
            self.stats["active_tasks"] = max(0, self.stats["active_tasks"] - 1)
            
            logger.info(f"DM задача '{task.name}' завершена: {task.sent_count} відправлено, {task.failed_count} помилок")
            
        except ImportError:
            task.status = DMStatus.FAILED
            task.errors.append({"error": "Telethon не встановлено", "time": datetime.now().isoformat()})
            logger.error(f"Telethon not available for DM sending")
        except asyncio.CancelledError:
            task.status = DMStatus.PAUSED
            logger.info(f"DM задача '{task.name}' призупинена")
        except Exception as e:
            task.status = DMStatus.FAILED
            task.errors.append({"error": str(e), "time": datetime.now().isoformat()})
            logger.error(f"Критична помилка DM: {e}")
    
    async def _personalize_message(self, client, user_id: int, template: str) -> str:
        """Персоналізація повідомлення"""
        message = template
        
        try:
            entity = await client.get_entity(user_id)
            
            first_name = getattr(entity, 'first_name', '') or ''
            last_name = getattr(entity, 'last_name', '') or ''
            username = getattr(entity, 'username', '') or ''
            
            message = message.replace("{name}", first_name)
            message = message.replace("{first_name}", first_name)
            message = message.replace("{last_name}", last_name)
            message = message.replace("{username}", username)
            message = message.replace("{full_name}", f"{first_name} {last_name}".strip())
            
        except Exception:
            message = message.replace("{name}", "")
            message = message.replace("{first_name}", "")
            message = message.replace("{last_name}", "")
            message = message.replace("{username}", "")
            message = message.replace("{full_name}", "")
        
        message = message.replace("{date}", datetime.now().strftime("%d.%m.%Y"))
        message = message.replace("{time}", datetime.now().strftime("%H:%M"))
        
        return message
    
    def get_task(self, task_id: str) -> Optional[DMTask]:
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        return [
            {
                "task_id": task.task_id,
                "name": task.name,
                "status": task.status.value,
                "sent_count": task.sent_count,
                "failed_count": task.failed_count,
                "total_count": task.total_count,
                "progress": round(task.sent_count / task.total_count * 100, 1) if task.total_count > 0 else 0,
                "created_at": task.created_at.isoformat()
            }
            for task in self.tasks.values()
        ]
    
    def add_to_blacklist(self, user_ids: List[int]):
        self.blacklist.update(user_ids)
        logger.info(f"Додано {len(user_ids)} користувачів до чорного списку")
    
    def remove_from_blacklist(self, user_ids: List[int]):
        for uid in user_ids:
            self.blacklist.discard(uid)
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            **self.stats,
            "blacklist_size": len(self.blacklist),
            "cooldown_cache": len(self.recent_sent),
            "pending_tasks": len([t for t in self.tasks.values() if t.status == DMStatus.PENDING]),
            "completed_tasks": len([t for t in self.tasks.values() if t.status == DMStatus.COMPLETED])
        }
    
    def format_task_status(self, task_id: str) -> str:
        task = self.tasks.get(task_id)
        if not task:
            return "❌ Задачу не знайдено"
        
        status_icons = {
            DMStatus.PENDING: "⏳",
            DMStatus.SENDING: "📤",
            DMStatus.COMPLETED: "✅",
            DMStatus.PAUSED: "⏸️",
            DMStatus.FAILED: "❌",
            DMStatus.CANCELLED: "🚫"
        }
        
        lines = []
        lines.append(f"<b>📧 DM ЗАДАЧА: {task.name}</b>")
        lines.append("═══════════════════════")
        lines.append(f"\n<b>Статус:</b> {status_icons.get(task.status, '❓')} {task.status.value}")
        lines.append(f"<b>Прогрес:</b> {task.sent_count}/{task.total_count}")
        
        if task.total_count > 0:
            progress = task.sent_count / task.total_count
            bar = "●" * int(progress * 10) + "○" * (10 - int(progress * 10))
            lines.append(f"<code>{bar}</code> {int(progress * 100)}%")
        
        lines.append(f"\n<b>✅ Відправлено:</b> {task.sent_count}")
        lines.append(f"<b>❌ Помилок:</b> {task.failed_count}")
        
        if task.started_at:
            lines.append(f"\n<b>Початок:</b> {task.started_at.strftime('%d.%m %H:%M')}")
        if task.completed_at:
            lines.append(f"<b>Завершення:</b> {task.completed_at.strftime('%d.%m %H:%M')}")
        
        return "\n".join(lines)


dm_sender = DMSenderService()
