import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import random

logger = logging.getLogger(__name__)

class VirtualNumberDetector:
    VIRTUAL_PROVIDERS = [
        'TextNow', 'Google Voice', 'Burner', 'Hushed',
        'Flyp', 'Dingtone', '2ndLine', 'TextFree'
    ]
    
    VIRTUAL_PATTERNS = [
        r'^\+1\d{10}$',
        r'^\+44\d{10}$',
        r'^\+49\d{11}$',
        r'^\+380(50|66|95|99)\d{7}$',
    ]
    
    @staticmethod
    def detect_virtual_number(phone: str) -> bool:
        if not phone:
            return False
        for pattern in VirtualNumberDetector.VIRTUAL_PATTERNS:
            if re.match(pattern, phone):
                return True
        return False

class BotDetectionSystem:
    BOT_PATTERNS = [
        r'@.*bot$',
        r'Bot$',
        r'бот$',
        r'_bot$',
    ]
    
    SUSPICIOUS_KEYWORDS = ['crypt', 'vpn', 'proxy', 'spoof', 'clone', 'fake', 'anon']
    
    @classmethod
    def is_bot_username(cls, username: str) -> bool:
        if not username:
            return False
        return any(re.match(p, username, re.IGNORECASE) for p in cls.BOT_PATTERNS)
    
    @classmethod
    def has_suspicious_bio(cls, bio: str) -> bool:
        if not bio:
            return False
        bio_lower = bio.lower()
        return any(word in bio_lower for word in cls.SUSPICIOUS_KEYWORDS)
    
    @classmethod
    def analyze_user(cls, user_data: dict) -> Dict[str, Any]:
        return {
            'is_bot_username': cls.is_bot_username(user_data.get('username', '')),
            'suspicious_bio': cls.has_suspicious_bio(user_data.get('bio', '')),
            'no_photo': not user_data.get('has_photo', False),
            'virtual_number': VirtualNumberDetector.detect_virtual_number(user_data.get('phone', '')),
            'recent_account': user_data.get('days_since_creation', 999) < 7,
        }

@dataclass
class MailingTask:
    id: str
    project_id: int
    name: str
    message_template: str
    target_users: List[int] = field(default_factory=list)
    target_chats: List[int] = field(default_factory=list)
    bot_sessions: List[str] = field(default_factory=list)
    status: str = "pending"
    sent_count: int = 0
    failed_count: int = 0
    total_count: int = 0
    interval_min: float = 1.0
    interval_max: float = 3.0
    stealth_mode: bool = False
    stealth_delay: int = 60
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)

class MailingEngine:
    def __init__(self):
        self.tasks: Dict[str, MailingTask] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.session_pool: Dict[str, Any] = {}
        self.stats = {
            "total_sent": 0,
            "total_failed": 0,
            "active_sessions": 0
        }
    
    def create_task(
        self,
        task_id: str,
        project_id: int,
        name: str,
        message_template: str,
        target_users: List[int] = None,
        target_chats: List[int] = None,
        bot_sessions: List[str] = None,
        interval_min: float = 1.0,
        interval_max: float = 3.0,
        stealth_mode: bool = False,
        stealth_delay: int = 60
    ) -> MailingTask:
        task = MailingTask(
            id=task_id,
            project_id=project_id,
            name=name,
            message_template=message_template,
            target_users=target_users or [],
            target_chats=target_chats or [],
            bot_sessions=bot_sessions or [],
            total_count=len(target_users or []) + len(target_chats or []),
            interval_min=interval_min,
            interval_max=interval_max,
            stealth_mode=stealth_mode,
            stealth_delay=stealth_delay
        )
        self.tasks[task_id] = task
        logger.info(f"Mailing task created: {task_id} (Stealth: {stealth_mode})")
        return task
    
    def get_task(self, task_id: str) -> Optional[MailingTask]:
        return self.tasks.get(task_id)
    
    def get_project_tasks(self, project_id: int) -> List[MailingTask]:
        return [t for t in self.tasks.values() if t.project_id == project_id]
    
    async def start_task(self, task_id: str) -> Dict[str, Any]:
        task = self.tasks.get(task_id)
        if not task:
            return {"success": False, "error": "Task not found"}
        
        if task.status == "running":
            return {"success": False, "error": "Task already running"}
        
        task.status = "running"
        task.started_at = datetime.now()
        
        asyncio_task = asyncio.create_task(self._execute_mailing(task_id))
        self.running_tasks[task_id] = asyncio_task
        
        return {"success": True, "message": f"Mailing started: {task.name}"}
    
    async def stop_task(self, task_id: str) -> Dict[str, Any]:
        task = self.tasks.get(task_id)
        if not task:
            return {"success": False, "error": "Task not found"}
        
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            del self.running_tasks[task_id]
        
        task.status = "stopped"
        return {"success": True, "message": "Mailing stopped"}
    
    async def _execute_mailing(self, task_id: str):
        task = self.tasks.get(task_id)
        if not task:
            return
        
        logger.info(f"Starting mailing execution: {task_id}")
        
        try:
            all_targets = task.target_users + task.target_chats
            
            for i, target in enumerate(all_targets):
                if task.status != "running":
                    break
                
                try:
                    success = await self._send_message(
                        target=target,
                        message=task.message_template,
                        session=task.bot_sessions[i % len(task.bot_sessions)] if task.bot_sessions else None,
                        stealth_mode=task.stealth_mode,
                        stealth_delay=task.stealth_delay
                    )
                    
                    if success:
                        task.sent_count += 1
                        self.stats["total_sent"] += 1
                    else:
                        task.failed_count += 1
                        self.stats["total_failed"] += 1
                    
                except Exception as e:
                    task.failed_count += 1
                    task.errors.append(str(e))
                    logger.error(f"Send error: {e}")
                
                delay = random.uniform(task.interval_min, task.interval_max)
                await asyncio.sleep(delay)
            
            task.status = "completed"
            task.completed_at = datetime.now()
            logger.info(f"Mailing completed: {task_id}, sent: {task.sent_count}, failed: {task.failed_count}")
            
        except asyncio.CancelledError:
            task.status = "cancelled"
            logger.info(f"Mailing cancelled: {task_id}")
        except Exception as e:
            task.status = "failed"
            task.errors.append(str(e))
            logger.error(f"Mailing failed: {task_id}, error: {e}")
    
    async def _send_message(self, target: int, message: str, session: str = None, stealth_mode: bool = False, stealth_delay: int = 60) -> bool:
        from core.session_manager import session_manager
        
        if not session:
            available_sessions = list(session_manager.imported_sessions.keys())
            if not available_sessions:
                logger.warning("No sessions available for mailing")
                return False
            session = random.choice(available_sessions)
        
        result = await session_manager.send_message(session, str(target), message)
        
        if result.get("status") == "success":
            if stealth_mode:
                message_id = result.get("message_id")
                if message_id:
                    asyncio.create_task(self._stealth_delete(session, target, message_id, stealth_delay))
            return True
        elif result.get("status") == "flood":
            wait_time = result.get("wait_seconds", 30)
            logger.warning(f"Flood wait: sleeping {wait_time}s")
            await asyncio.sleep(wait_time)
            return False
        else:
            logger.error(f"Send failed: {result.get('message')}")
            return False
    
    async def _stealth_delete(self, session: str, target: int, message_id: int, delay: int):
        """Автоматичне видалення повідомлення через заданий час (Режим Невидимка)"""
        from core.session_manager import session_manager
        try:
            await asyncio.sleep(delay)
            # В реальному Telethon/Pyrogram клієнті через session_manager
            client = await session_manager.get_client(session)
            if client:
                await client.delete_messages(target, [message_id])
                logger.debug(f"Stealth delete: message {message_id} in {target} removed")
        except Exception as e:
            logger.error(f"Stealth delete error: {e}")

    def add_session(self, session_id: str, session_data: Any):
        self.session_pool[session_id] = session_data
        self.stats["active_sessions"] = len(self.session_pool)
        logger.info(f"Session added: {session_id}")
    
    def remove_session(self, session_id: str):
        if session_id in self.session_pool:
            del self.session_pool[session_id]
            self.stats["active_sessions"] = len(self.session_pool)
    
    def get_stats(self) -> Dict[str, Any]:
        active_tasks = sum(1 for t in self.tasks.values() if t.status == "running")
        return {
            **self.stats,
            "active_tasks": active_tasks,
            "total_tasks": len(self.tasks),
            "sessions_available": len(self.session_pool)
        }

mailing_engine = MailingEngine()

class MonitoringEngine:
    def __init__(self):
        self.keywords: List[str] = []
        self.monitored_chats: List[int] = []
        self.alerts: List[Dict] = []
        self.is_running = False
    
    def set_keywords(self, keywords: List[str]):
        self.keywords = [k.lower() for k in keywords]
        logger.info(f"Keywords set: {len(keywords)}")
    
    def add_chat(self, chat_id: int):
        if chat_id not in self.monitored_chats:
            self.monitored_chats.append(chat_id)
    
    def remove_chat(self, chat_id: int):
        if chat_id in self.monitored_chats:
            self.monitored_chats.remove(chat_id)
    
    def analyze_message(self, text: str, chat_id: int, user_id: int) -> Optional[Dict]:
        if not text or not self.keywords:
            return None
        
        text_lower = text.lower()
        found_keywords = [k for k in self.keywords if k in text_lower]
        
        if found_keywords:
            alert = {
                "type": "keyword_match",
                "chat_id": chat_id,
                "user_id": user_id,
                "keywords": found_keywords,
                "text_preview": text[:200],
                "timestamp": datetime.now().isoformat()
            }
            self.alerts.append(alert)
            return alert
        
        return None
    
    def detect_military_codes(self, text: str) -> List[str]:
        patterns = {
            'grid_coords': r'\b[A-R]{2}[0-9]{2}[a-x]{2}\b',
            'zulu_time': r'\b[0-9]{6}Z\b',
            'frequency': r'\b[0-9]{3}\.[0-9]+\s?(MHz|kHz|мгц|кгц)\b',
            'callsign': r'\b[A-Z]{2,6}[0-9]{1,3}\b',
            'mgrs': r'\b[0-9]{1,2}[A-Z]{3}[0-9]{8,10}\b',
        }
        
        found = []
        for name, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                found.extend([(name, m) for m in matches])
        
        return found
    
    def detect_encrypted_data(self, text: str) -> List[str]:
        patterns = [
            r'[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}',
            r'[A-Za-z0-9+/]{20,}={0,2}',
            r'\b[0-9A-Fa-f]{32,}\b',
        ]
        
        found = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            found.extend(matches)
        
        return found
    
    def get_alerts(self, limit: int = 50) -> List[Dict]:
        return self.alerts[-limit:]
    
    def clear_alerts(self):
        self.alerts = []
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "monitored_chats": len(self.monitored_chats),
            "keywords": len(self.keywords),
            "total_alerts": len(self.alerts),
            "is_running": self.is_running
        }

monitoring_engine = MonitoringEngine()
