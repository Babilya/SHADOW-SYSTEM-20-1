"""
GroupParserService - Парсинг учасників з груп/каналів для розсилок
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ParserFilter(str, Enum):
    ALL = "all"
    ACTIVE_RECENTLY = "active_recently"
    WITH_USERNAME = "with_username"
    WITH_PHONE = "with_phone"
    NOT_BOTS = "not_bots"
    PREMIUM_ONLY = "premium_only"
    NO_PHOTO = "no_photo"


@dataclass
class ParsedUser:
    user_id: int
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    phone: Optional[str]
    is_bot: bool
    is_premium: bool
    has_photo: bool
    last_seen: Optional[str]
    status: str
    source_chat_id: int
    source_chat_title: str
    parsed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "is_bot": self.is_bot,
            "is_premium": self.is_premium,
            "has_photo": self.has_photo,
            "last_seen": self.last_seen,
            "status": self.status,
            "source_chat_id": self.source_chat_id,
            "source_chat_title": self.source_chat_title,
            "parsed_at": self.parsed_at.isoformat()
        }


@dataclass
class ParseJob:
    job_id: str
    chat_identifier: str
    chat_title: str
    status: str = "pending"
    total_members: int = 0
    parsed_count: int = 0
    filters: List[ParserFilter] = field(default_factory=list)
    users: List[ParsedUser] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class GroupParserService:
    def __init__(self):
        self.jobs: Dict[str, ParseJob] = {}
        self.parsed_users_db: Dict[int, ParsedUser] = {}
        self.user_lists: Dict[str, List[int]] = {}
        self.stats = {
            "total_parsed": 0,
            "total_groups": 0,
            "total_users": 0
        }
    
    async def parse_group(
        self,
        chat_identifier: str,
        limit: int = 500,
        filters: List[ParserFilter] = None,
        job_id: str = None
    ) -> Dict[str, Any]:
        """Парсинг учасників групи/каналу"""
        from core.session_manager import session_manager
        import uuid
        
        job_id = job_id or str(uuid.uuid4())[:8]
        filters = filters or [ParserFilter.NOT_BOTS]
        
        job = ParseJob(
            job_id=job_id,
            chat_identifier=chat_identifier,
            chat_title="",
            filters=filters,
            started_at=datetime.now()
        )
        self.jobs[job_id] = job
        
        try:
            available_sessions = list(session_manager.imported_sessions.keys())
            
            if not available_sessions:
                job.status = "error"
                job.error = "Немає активних сесій"
                return {"error": job.error, "job_id": job_id}
            
            session_hash = available_sessions[0]
            client = await session_manager.connect_client(session_hash)
            
            if not client:
                job.status = "error"
                job.error = "Не вдалося підключитися"
                return {"error": job.error, "job_id": job_id}
            
            job.status = "parsing"
            
            entity = await client.get_entity(chat_identifier)
            job.chat_title = getattr(entity, 'title', chat_identifier)
            job.total_members = getattr(entity, 'participants_count', 0) or 0
            
            participants = await client.get_participants(entity, limit=limit, aggressive=True)
            
            for user in participants:
                if self._should_skip_user(user, filters):
                    continue
                
                parsed_user = ParsedUser(
                    user_id=user.id,
                    username=user.username,
                    first_name=user.first_name or "",
                    last_name=user.last_name,
                    phone=user.phone,
                    is_bot=user.bot or False,
                    is_premium=getattr(user, 'premium', False) or False,
                    has_photo=bool(user.photo),
                    last_seen=self._parse_last_seen(user.status),
                    status=str(user.status) if user.status else "unknown",
                    source_chat_id=entity.id,
                    source_chat_title=job.chat_title
                )
                
                job.users.append(parsed_user)
                job.parsed_count += 1
                self.parsed_users_db[user.id] = parsed_user
            
            job.status = "completed"
            job.completed_at = datetime.now()
            
            self.stats["total_parsed"] += job.parsed_count
            self.stats["total_groups"] += 1
            self.stats["total_users"] = len(self.parsed_users_db)
            
            logger.info(f"Парсинг завершено: {job.parsed_count} користувачів з {job.chat_title}")
            
            return {
                "job_id": job_id,
                "status": "completed",
                "chat_title": job.chat_title,
                "total_members": job.total_members,
                "parsed_count": job.parsed_count,
                "users": [u.to_dict() for u in job.users[:20]]
            }
            
        except Exception as e:
            logger.error(f"Помилка парсингу: {e}")
            job.status = "error"
            job.error = str(e)
            return {"error": str(e), "job_id": job_id}
    
    def _should_skip_user(self, user, filters: List[ParserFilter]) -> bool:
        if ParserFilter.NOT_BOTS in filters and (user.bot or False):
            return True
        
        if ParserFilter.WITH_USERNAME in filters and not user.username:
            return True
        
        if ParserFilter.WITH_PHONE in filters and not user.phone:
            return True
        
        if ParserFilter.PREMIUM_ONLY in filters and not getattr(user, 'premium', False):
            return True
        
        if ParserFilter.NO_PHOTO in filters and user.photo:
            return True
        
        if ParserFilter.ACTIVE_RECENTLY in filters:
            last_seen = self._parse_last_seen(user.status)
            if last_seen == "давно" or last_seen == "невідомо":
                return True
        
        return False
    
    def _parse_last_seen(self, status) -> str:
        if not status:
            return "невідомо"
        
        status_name = type(status).__name__
        
        if status_name == "UserStatusOnline":
            return "онлайн"
        elif status_name == "UserStatusOffline":
            return "нещодавно"
        elif status_name == "UserStatusRecently":
            return "нещодавно"
        elif status_name == "UserStatusLastWeek":
            return "цього тижня"
        elif status_name == "UserStatusLastMonth":
            return "цього місяця"
        else:
            return "давно"
    
    def get_job(self, job_id: str) -> Optional[ParseJob]:
        return self.jobs.get(job_id)
    
    def get_all_jobs(self) -> List[Dict[str, Any]]:
        return [
            {
                "job_id": job.job_id,
                "chat_title": job.chat_title,
                "status": job.status,
                "parsed_count": job.parsed_count,
                "total_members": job.total_members,
                "started_at": job.started_at.isoformat() if job.started_at else None
            }
            for job in self.jobs.values()
        ]
    
    def save_user_list(self, list_name: str, user_ids: List[int]):
        self.user_lists[list_name] = user_ids
        logger.info(f"Збережено список '{list_name}' з {len(user_ids)} користувачів")
    
    def get_user_list(self, list_name: str) -> List[int]:
        return self.user_lists.get(list_name, [])
    
    def get_all_user_lists(self) -> Dict[str, int]:
        return {name: len(ids) for name, ids in self.user_lists.items()}
    
    def get_parsed_users(self, limit: int = 100) -> List[Dict[str, Any]]:
        users = list(self.parsed_users_db.values())[:limit]
        return [u.to_dict() for u in users]
    
    def get_user_ids_for_mailing(self, filters: Dict[str, Any] = None) -> List[int]:
        users = list(self.parsed_users_db.values())
        
        if filters:
            if filters.get("only_with_username"):
                users = [u for u in users if u.username]
            if filters.get("only_premium"):
                users = [u for u in users if u.is_premium]
            if filters.get("only_active"):
                users = [u for u in users if u.last_seen in ["онлайн", "нещодавно"]]
        
        return [u.user_id for u in users]
    
    def clear_parsed_users(self):
        self.parsed_users_db.clear()
        logger.info("База спарсених користувачів очищена")
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            **self.stats,
            "active_jobs": len([j for j in self.jobs.values() if j.status == "parsing"]),
            "completed_jobs": len([j for j in self.jobs.values() if j.status == "completed"]),
            "saved_lists": len(self.user_lists)
        }
    
    def format_parse_result(self, result: Dict[str, Any]) -> str:
        lines = []
        lines.append("<b>📊 РЕЗУЛЬТАТИ ПАРСИНГУ</b>")
        lines.append("═══════════════════════")
        
        if "error" in result:
            lines.append(f"\n❌ <b>Помилка:</b> {result['error']}")
            return "\n".join(lines)
        
        lines.append(f"\n<b>💬 Група:</b> {result.get('chat_title', 'Невідома')}")
        lines.append(f"<b>👥 Всього учасників:</b> {result.get('total_members', 0)}")
        lines.append(f"<b>✅ Спарсено:</b> {result.get('parsed_count', 0)}")
        lines.append("")
        
        users = result.get("users", [])
        if users:
            lines.append("<b>📋 Приклад користувачів:</b>")
            for i, user in enumerate(users[:10], 1):
                name = user.get("first_name", "")
                username = f"@{user['username']}" if user.get("username") else ""
                premium = " 💎" if user.get("is_premium") else ""
                lines.append(f"{i}. {name} {username}{premium}")
        
        return "\n".join(lines)


group_parser = GroupParserService()
