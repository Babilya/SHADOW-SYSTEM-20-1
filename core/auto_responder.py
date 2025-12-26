import asyncio
import logging
import re
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from sqlalchemy import text

logger = logging.getLogger(__name__)

@dataclass
class AutoResponse:
    id: int
    project_id: str
    keyword: str
    response_text: str
    match_type: str = "contains"
    cooldown_seconds: int = 60
    is_active: bool = True
    priority: int = 0

class AutoResponder:
    def __init__(self):
        self.responses: Dict[str, List[AutoResponse]] = {}
        self.cooldowns: Dict[str, datetime] = {}
        self._loaded = False
    
    async def load_responses(self, project_id: Optional[str] = None):
        try:
            from database.db import async_session
            async with async_session() as session:
                if project_id:
                    result = await session.execute(
                        text("SELECT * FROM auto_responses WHERE project_id = :pid AND is_active = true ORDER BY priority DESC"),
                        {"pid": project_id}
                    )
                else:
                    result = await session.execute(
                        text("SELECT * FROM auto_responses WHERE is_active = true ORDER BY priority DESC")
                    )
                
                rows = result.fetchall()
                for row in rows:
                    response = AutoResponse(
                        id=row.id,
                        project_id=row.project_id or "global",
                        keyword=row.keyword,
                        response_text=row.response_text,
                        match_type=row.match_type or "contains",
                        cooldown_seconds=row.cooldown_seconds or 60,
                        is_active=row.is_active,
                        priority=row.priority or 0
                    )
                    if response.project_id not in self.responses:
                        self.responses[response.project_id] = []
                    self.responses[response.project_id].append(response)
                
                self._loaded = True
                logger.info(f"Loaded {len(rows)} auto-responses")
        except Exception as e:
            logger.error(f"Failed to load auto-responses: {e}")
    
    def _check_cooldown(self, user_id: int, response_id: int) -> bool:
        key = f"{user_id}:{response_id}"
        if key in self.cooldowns:
            if datetime.now() < self.cooldowns[key]:
                return False
        return True
    
    def _set_cooldown(self, user_id: int, response: AutoResponse):
        key = f"{user_id}:{response.id}"
        self.cooldowns[key] = datetime.now() + timedelta(seconds=response.cooldown_seconds)
    
    def _match_keyword(self, text: str, keyword: str, match_type: str) -> bool:
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        
        if match_type == "exact":
            return text_lower == keyword_lower
        elif match_type == "starts":
            return text_lower.startswith(keyword_lower)
        elif match_type == "ends":
            return text_lower.endswith(keyword_lower)
        elif match_type == "regex":
            try:
                return bool(re.search(keyword, text, re.IGNORECASE))
            except re.error:
                return False
        else:
            return keyword_lower in text_lower
    
    async def get_response(self, user_id: int, message_text: str, project_id: str = "global") -> Optional[str]:
        if not self._loaded:
            await self.load_responses()
        
        all_responses = self.responses.get("global", []) + self.responses.get(project_id, [])
        all_responses.sort(key=lambda r: r.priority, reverse=True)
        
        for response in all_responses:
            if not self._check_cooldown(user_id, response.id):
                continue
            
            if self._match_keyword(message_text, response.keyword, response.match_type):
                self._set_cooldown(user_id, response)
                return response.response_text
        
        return None
    
    async def add_response(
        self,
        project_id: str,
        keyword: str,
        response_text: str,
        match_type: str = "contains",
        cooldown_seconds: int = 60,
        priority: int = 0
    ) -> int:
        try:
            from database.db import async_session
            async with async_session() as session:
                result = await session.execute(
                    text("""
                        INSERT INTO auto_responses (project_id, keyword, response_text, match_type, cooldown_seconds, priority, is_active)
                        VALUES (:project_id, :keyword, :response_text, :match_type, :cooldown_seconds, :priority, true)
                        RETURNING id
                    """),
                    {
                        "project_id": project_id,
                        "keyword": keyword,
                        "response_text": response_text,
                        "match_type": match_type,
                        "cooldown_seconds": cooldown_seconds,
                        "priority": priority
                    }
                )
                row = result.fetchone()
                await session.commit()
                
                response = AutoResponse(
                    id=row[0],
                    project_id=project_id,
                    keyword=keyword,
                    response_text=response_text,
                    match_type=match_type,
                    cooldown_seconds=cooldown_seconds,
                    priority=priority
                )
                if project_id not in self.responses:
                    self.responses[project_id] = []
                self.responses[project_id].append(response)
                
                logger.info(f"Added auto-response {row[0]} for keyword '{keyword}'")
                return row[0]
        except Exception as e:
            logger.error(f"Failed to add auto-response: {e}")
            raise
    
    async def remove_response(self, response_id: int) -> bool:
        try:
            from database.db import async_session
            async with async_session() as session:
                await session.execute(
                    text("UPDATE auto_responses SET is_active = false WHERE id = :id"),
                    {"id": response_id}
                )
                await session.commit()
            
            for project_id in self.responses:
                self.responses[project_id] = [
                    r for r in self.responses[project_id] if r.id != response_id
                ]
            
            return True
        except Exception as e:
            logger.error(f"Failed to remove auto-response: {e}")
            return False
    
    async def get_all_responses(self, project_id: Optional[str] = None) -> List[AutoResponse]:
        if not self._loaded:
            await self.load_responses()
        
        if project_id:
            return self.responses.get(project_id, [])
        
        all_responses = []
        for responses in self.responses.values():
            all_responses.extend(responses)
        return all_responses

auto_responder = AutoResponder()
