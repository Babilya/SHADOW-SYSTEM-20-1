"""
Anti-Ghost Recovery - Модуль відновлення видалених повідомлень
Зберігає всі повідомлення та дозволяє відновлювати видалені
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
import logging
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class GhostMessage:
    """Збережене повідомлення"""
    message_id: int
    chat_id: int
    user_id: int
    username: str
    text: str
    timestamp: datetime
    message_type: str  # text, photo, video, document, voice, sticker
    media_file_id: Optional[str] = None
    reply_to: Optional[int] = None
    forward_from: Optional[int] = None
    is_deleted: bool = False
    deletion_time: Optional[datetime] = None
    edit_history: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class AntiGhostRecovery:
    """Система відновлення видалених повідомлень"""
    
    def __init__(self, storage_path: str = "data/ghost_messages"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.messages: Dict[str, GhostMessage] = {}
        self.deleted_messages: Dict[str, GhostMessage] = {}
        self.edit_tracker: Dict[str, List[Dict]] = {}
        
        self.stats = {
            "total_captured": 0,
            "total_deleted": 0,
            "total_edited": 0,
            "total_recovered": 0,
            "by_chat": {},
            "by_user": {}
        }
        
        self._load_cache()
    
    def _get_key(self, chat_id: int, message_id: int) -> str:
        """Генерація унікального ключа"""
        return f"{chat_id}_{message_id}"
    
    def _load_cache(self):
        """Завантаження кешу з диску"""
        cache_file = self.storage_path / "ghost_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.stats = data.get("stats", self.stats)
            except Exception as e:
                logger.warning(f"Cache load error: {e}")
    
    def _save_cache(self):
        """Збереження кешу на диск"""
        cache_file = self.storage_path / "ghost_cache.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({"stats": self.stats}, f)
        except Exception as e:
            logger.warning(f"Cache save error: {e}")
    
    async def capture_message(self, message: Any) -> GhostMessage:
        """Захоплення повідомлення"""
        chat_id = message.chat.id if hasattr(message, 'chat') else 0
        message_id = message.message_id if hasattr(message, 'message_id') else 0
        user_id = message.from_user.id if hasattr(message, 'from_user') and message.from_user else 0
        username = message.from_user.username if hasattr(message, 'from_user') and message.from_user else ""
        
        if hasattr(message, 'photo') and message.photo:
            message_type = "photo"
            media_file_id = message.photo[-1].file_id
            text = message.caption or ""
        elif hasattr(message, 'video') and message.video:
            message_type = "video"
            media_file_id = message.video.file_id
            text = message.caption or ""
        elif hasattr(message, 'document') and message.document:
            message_type = "document"
            media_file_id = message.document.file_id
            text = message.caption or ""
        elif hasattr(message, 'voice') and message.voice:
            message_type = "voice"
            media_file_id = message.voice.file_id
            text = ""
        elif hasattr(message, 'sticker') and message.sticker:
            message_type = "sticker"
            media_file_id = message.sticker.file_id
            text = ""
        else:
            message_type = "text"
            media_file_id = None
            text = message.text or message.caption or ""
        
        ghost = GhostMessage(
            message_id=message_id,
            chat_id=chat_id,
            user_id=user_id,
            username=username or "",
            text=text or "",
            timestamp=datetime.now(),
            message_type=message_type,
            media_file_id=media_file_id,
            reply_to=message.reply_to_message.message_id if hasattr(message, 'reply_to_message') and message.reply_to_message else None,
            forward_from=message.forward_from.id if hasattr(message, 'forward_from') and message.forward_from else None,
            metadata={
                "entities": len(message.entities) if hasattr(message, 'entities') and message.entities else 0
            }
        )
        
        key = self._get_key(chat_id, message_id)
        self.messages[key] = ghost
        
        self.stats["total_captured"] += 1
        chat_key = str(chat_id)
        self.stats["by_chat"][chat_key] = self.stats["by_chat"].get(chat_key, 0) + 1
        user_key = str(user_id)
        self.stats["by_user"][user_key] = self.stats["by_user"].get(user_key, 0) + 1
        
        await self._save_message(ghost)
        
        return ghost
    
    async def capture_edit(self, message: Any):
        """Захоплення редагування"""
        chat_id = message.chat.id if hasattr(message, 'chat') else 0
        message_id = message.message_id if hasattr(message, 'message_id') else 0
        key = self._get_key(chat_id, message_id)
        
        if key in self.messages:
            old_message = self.messages[key]
            old_text = old_message.text
            
            new_text = message.text or message.caption or ""
            
            edit_record = {
                "old_text": old_text,
                "new_text": new_text,
                "edit_time": datetime.now().isoformat()
            }
            
            old_message.edit_history.append(edit_record)
            old_message.text = new_text
            
            if key not in self.edit_tracker:
                self.edit_tracker[key] = []
            self.edit_tracker[key].append(edit_record)
            
            self.stats["total_edited"] += 1
            
            logger.info(f"Edit captured: {key}")
    
    async def mark_deleted(self, chat_id: int, message_ids: List[int]):
        """Позначення повідомлень як видалених"""
        for message_id in message_ids:
            key = self._get_key(chat_id, message_id)
            
            if key in self.messages:
                ghost = self.messages[key]
                ghost.is_deleted = True
                ghost.deletion_time = datetime.now()
                
                self.deleted_messages[key] = ghost
                self.stats["total_deleted"] += 1
                
                logger.info(f"Message marked deleted: {key}")
    
    async def recover_message(self, chat_id: int, message_id: int) -> Optional[GhostMessage]:
        """Відновлення видаленого повідомлення"""
        key = self._get_key(chat_id, message_id)
        
        if key in self.deleted_messages:
            self.stats["total_recovered"] += 1
            return self.deleted_messages[key]
        
        if key in self.messages:
            return self.messages[key]
        
        return None
    
    async def get_deleted_messages(self, chat_id: int, limit: int = 50) -> List[GhostMessage]:
        """Отримання видалених повідомлень чату"""
        deleted = []
        for key, ghost in self.deleted_messages.items():
            if ghost.chat_id == chat_id:
                deleted.append(ghost)
                if len(deleted) >= limit:
                    break
        
        deleted.sort(key=lambda x: x.deletion_time or x.timestamp, reverse=True)
        return deleted
    
    async def get_edit_history(self, chat_id: int, message_id: int) -> List[Dict]:
        """Отримання історії редагувань"""
        key = self._get_key(chat_id, message_id)
        
        if key in self.messages:
            return self.messages[key].edit_history
        
        return self.edit_tracker.get(key, [])
    
    async def search_messages(self, chat_id: int, query: str, include_deleted: bool = True) -> List[GhostMessage]:
        """Пошук повідомлень"""
        results = []
        query_lower = query.lower()
        
        for key, ghost in self.messages.items():
            if ghost.chat_id == chat_id:
                if query_lower in ghost.text.lower():
                    if include_deleted or not ghost.is_deleted:
                        results.append(ghost)
        
        return results[:50]
    
    async def _save_message(self, ghost: GhostMessage):
        """Збереження повідомлення на диск"""
        file_path = self.storage_path / f"{ghost.chat_id}" / f"{ghost.message_id}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = asdict(ghost)
        data['timestamp'] = ghost.timestamp.isoformat()
        if ghost.deletion_time:
            data['deletion_time'] = ghost.deletion_time.isoformat()
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Save error: {e}")
    
    def get_stats(self) -> Dict:
        """Отримання статистики"""
        return {
            **self.stats,
            "in_memory": len(self.messages),
            "deleted_count": len(self.deleted_messages)
        }
    
    def format_ghost_message(self, ghost: GhostMessage) -> str:
        """Форматування повідомлення"""
        type_icons = {
            "text": "💬",
            "photo": "🖼",
            "video": "🎬",
            "document": "📎",
            "voice": "🎤",
            "sticker": "🎨"
        }
        
        status = "🗑 ВИДАЛЕНО" if ghost.is_deleted else "✅ Активне"
        
        text = f"""<b>{type_icons.get(ghost.message_type, '📝')} Повідомлення #{ghost.message_id}</b>

<b>📊 Статус:</b> {status}
<b>👤 Від:</b> @{ghost.username or ghost.user_id}
<b>📅 Час:</b> {ghost.timestamp.strftime('%d.%m.%Y %H:%M')}
"""
        
        if ghost.is_deleted and ghost.deletion_time:
            text += f"<b>🗑 Видалено:</b> {ghost.deletion_time.strftime('%d.%m.%Y %H:%M')}\n"
        
        if ghost.text:
            text += f"\n<b>📝 Текст:</b>\n<i>{ghost.text[:500]}</i>"
        
        if ghost.edit_history:
            text += f"\n\n<b>✏️ Редагувань:</b> {len(ghost.edit_history)}"
        
        return text
    
    def format_stats_report(self) -> str:
        """Форматування звіту статистики"""
        stats = self.get_stats()
        
        text = f"""<b>👻 ANTI-GHOST RECOVERY</b>
<i>Відновлення видалених повідомлень</i>

───────────────

<b>📊 СТАТИСТИКА:</b>
├ 📨 Захоплено: <b>{stats['total_captured']}</b>
├ 🗑 Видалено: <b>{stats['total_deleted']}</b>
├ ✏️ Редагувань: <b>{stats['total_edited']}</b>
├ 🔄 Відновлено: <b>{stats['total_recovered']}</b>
└ 💾 В пам'яті: <b>{stats['in_memory']}</b>

<b>📁 ПО ЧАТАХ:</b>"""
        
        for chat_id, count in list(stats.get("by_chat", {}).items())[:5]:
            text += f"\n├ {chat_id}: <b>{count}</b>"
        
        if not stats.get("by_chat"):
            text += "\n<i>Немає даних</i>"
        
        return text


anti_ghost = AntiGhostRecovery()
