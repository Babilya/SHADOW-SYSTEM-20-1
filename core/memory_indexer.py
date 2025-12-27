"""
Memory Indexer - Модуль індексації в оперативній пам'яті
Швидкий пошук та індексація повідомлень, користувачів, медіа
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
import logging
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class IndexedItem:
    """Індексований елемент"""
    item_id: str
    item_type: str  # message, user, media, channel
    content: str
    tokens: Set[str] = field(default_factory=set)
    metadata: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    relevance_score: float = 1.0


@dataclass
class SearchResult:
    """Результат пошуку"""
    item: IndexedItem
    score: float
    highlights: List[str] = field(default_factory=list)


class MemoryIndexer:
    """Система індексації в пам'яті"""
    
    STOP_WORDS = {
        'і', 'в', 'на', 'з', 'до', 'від', 'за', 'при', 'про', 'над', 'під',
        'що', 'як', 'це', 'та', 'або', 'але', 'ще', 'вже', 'там', 'тут',
        'не', 'ні', 'так', 'він', 'вона', 'вони', 'ми', 'ви', 'я', 'ти',
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'can'
    }
    
    def __init__(self, max_items: int = 100000):
        self.max_items = max_items
        
        self.items: Dict[str, IndexedItem] = {}
        
        self.inverted_index: Dict[str, Set[str]] = defaultdict(set)
        
        self.type_index: Dict[str, Set[str]] = defaultdict(set)
        
        self.time_index: Dict[str, Set[str]] = defaultdict(set)
        
        self.user_index: Dict[int, Set[str]] = defaultdict(set)
        
        self.chat_index: Dict[int, Set[str]] = defaultdict(set)
        
        self.stats = {
            "total_indexed": 0,
            "total_tokens": 0,
            "total_searches": 0,
            "avg_search_time_ms": 0.0,
            "by_type": {}
        }
    
    def _tokenize(self, text: str) -> Set[str]:
        """Токенізація тексту"""
        text = text.lower()
        text = re.sub(r'[^\w\s@#]', ' ', text)
        tokens = text.split()
        tokens = [t for t in tokens if len(t) >= 2 and t not in self.STOP_WORDS]
        return set(tokens)
    
    def _generate_id(self, item_type: str, **kwargs) -> str:
        """Генерація унікального ID"""
        data = f"{item_type}_{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(data.encode()).hexdigest()[:16]
    
    async def index_message(self, message: Any) -> str:
        """Індексація повідомлення"""
        chat_id = message.chat.id if hasattr(message, 'chat') else 0
        message_id = message.message_id if hasattr(message, 'message_id') else 0
        user_id = message.from_user.id if hasattr(message, 'from_user') and message.from_user else 0
        text = message.text or message.caption or ""
        
        item_id = self._generate_id("message", chat_id=chat_id, message_id=message_id)
        
        tokens = self._tokenize(text)
        
        username = message.from_user.username if hasattr(message, 'from_user') and message.from_user else ""
        if username:
            tokens.add(f"@{username.lower()}")
        
        item = IndexedItem(
            item_id=item_id,
            item_type="message",
            content=text[:500],
            tokens=tokens,
            metadata={
                "chat_id": chat_id,
                "message_id": message_id,
                "user_id": user_id,
                "username": username
            },
            timestamp=datetime.now()
        )
        
        await self._add_to_index(item)
        
        if user_id:
            self.user_index[user_id].add(item_id)
        if chat_id:
            self.chat_index[chat_id].add(item_id)
        
        return item_id
    
    async def index_user(self, user_id: int, username: str = "", 
                        first_name: str = "", last_name: str = "",
                        bio: str = "", metadata: Dict = None) -> str:
        """Індексація користувача"""
        item_id = self._generate_id("user", user_id=user_id)
        
        content = f"{username} {first_name} {last_name} {bio}"
        tokens = self._tokenize(content)
        
        if username:
            tokens.add(f"@{username.lower()}")
        
        item = IndexedItem(
            item_id=item_id,
            item_type="user",
            content=content[:200],
            tokens=tokens,
            metadata={
                "user_id": user_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                **(metadata or {})
            },
            timestamp=datetime.now()
        )
        
        await self._add_to_index(item)
        self.user_index[user_id].add(item_id)
        
        return item_id
    
    async def index_media(self, file_id: str, file_type: str,
                         caption: str = "", user_id: int = 0,
                         chat_id: int = 0, metadata: Dict = None) -> str:
        """Індексація медіа"""
        item_id = self._generate_id("media", file_id=file_id)
        
        tokens = self._tokenize(caption)
        tokens.add(file_type.lower())
        
        item = IndexedItem(
            item_id=item_id,
            item_type="media",
            content=caption[:200],
            tokens=tokens,
            metadata={
                "file_id": file_id,
                "file_type": file_type,
                "user_id": user_id,
                "chat_id": chat_id,
                **(metadata or {})
            },
            timestamp=datetime.now()
        )
        
        await self._add_to_index(item)
        
        if user_id:
            self.user_index[user_id].add(item_id)
        if chat_id:
            self.chat_index[chat_id].add(item_id)
        
        return item_id
    
    async def _add_to_index(self, item: IndexedItem):
        """Додавання елемента до індексу"""
        if len(self.items) >= self.max_items:
            await self._cleanup_old_items()
        
        self.items[item.item_id] = item
        
        for token in item.tokens:
            self.inverted_index[token].add(item.item_id)
        
        self.type_index[item.item_type].add(item.item_id)
        
        time_key = item.timestamp.strftime("%Y-%m-%d")
        self.time_index[time_key].add(item.item_id)
        
        self.stats["total_indexed"] += 1
        self.stats["total_tokens"] += len(item.tokens)
        self.stats["by_type"][item.item_type] = self.stats["by_type"].get(item.item_type, 0) + 1
    
    async def _cleanup_old_items(self):
        """Очищення старих елементів"""
        if not self.items:
            return
        
        sorted_items = sorted(self.items.values(), key=lambda x: x.timestamp)
        
        to_remove = len(self.items) - int(self.max_items * 0.8)
        
        for item in sorted_items[:to_remove]:
            await self._remove_from_index(item.item_id)
    
    async def _remove_from_index(self, item_id: str):
        """Видалення елемента з індексу"""
        if item_id not in self.items:
            return
        
        item = self.items[item_id]
        
        for token in item.tokens:
            self.inverted_index[token].discard(item_id)
        
        self.type_index[item.item_type].discard(item_id)
        
        time_key = item.timestamp.strftime("%Y-%m-%d")
        self.time_index[time_key].discard(item_id)
        
        user_id = item.metadata.get("user_id")
        if user_id:
            self.user_index[user_id].discard(item_id)
        
        chat_id = item.metadata.get("chat_id")
        if chat_id:
            self.chat_index[chat_id].discard(item_id)
        
        del self.items[item_id]
    
    async def search(self, query: str, item_type: str = None,
                    user_id: int = None, chat_id: int = None,
                    limit: int = 50) -> List[SearchResult]:
        """Пошук в індексі"""
        start_time = datetime.now()
        
        tokens = self._tokenize(query)
        
        if not tokens:
            return []
        
        candidate_ids = None
        for token in tokens:
            token_ids = self.inverted_index.get(token, set())
            if candidate_ids is None:
                candidate_ids = token_ids.copy()
            else:
                candidate_ids &= token_ids
        
        if not candidate_ids:
            return []
        
        if item_type:
            candidate_ids &= self.type_index.get(item_type, set())
        
        if user_id:
            candidate_ids &= self.user_index.get(user_id, set())
        
        if chat_id:
            candidate_ids &= self.chat_index.get(chat_id, set())
        
        results = []
        for item_id in candidate_ids:
            if item_id in self.items:
                item = self.items[item_id]
                score = self._calculate_relevance(item, tokens)
                
                highlights = self._get_highlights(item.content, tokens)
                
                results.append(SearchResult(
                    item=item,
                    score=score,
                    highlights=highlights
                ))
        
        results.sort(key=lambda x: x.score, reverse=True)
        
        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        self.stats["total_searches"] += 1
        self.stats["avg_search_time_ms"] = (
            (self.stats["avg_search_time_ms"] * (self.stats["total_searches"] - 1) + elapsed)
            / self.stats["total_searches"]
        )
        
        return results[:limit]
    
    def _calculate_relevance(self, item: IndexedItem, query_tokens: Set[str]) -> float:
        """Розрахунок релевантності"""
        if not item.tokens:
            return 0.0
        
        matched = len(query_tokens & item.tokens)
        score = matched / len(query_tokens)
        
        age_days = (datetime.now() - item.timestamp).days
        if age_days < 1:
            score *= 1.2
        elif age_days < 7:
            score *= 1.1
        elif age_days > 30:
            score *= 0.9
        
        score *= item.relevance_score
        
        return round(score, 3)
    
    def _get_highlights(self, content: str, tokens: Set[str]) -> List[str]:
        """Отримання виділених фрагментів"""
        highlights = []
        content_lower = content.lower()
        
        for token in tokens:
            pos = content_lower.find(token)
            if pos != -1:
                start = max(0, pos - 20)
                end = min(len(content), pos + len(token) + 20)
                snippet = content[start:end]
                highlights.append(f"...{snippet}...")
        
        return highlights[:3]
    
    async def get_user_items(self, user_id: int, item_type: str = None, 
                            limit: int = 50) -> List[IndexedItem]:
        """Отримання елементів користувача"""
        item_ids = self.user_index.get(user_id, set())
        
        items = []
        for item_id in item_ids:
            if item_id in self.items:
                item = self.items[item_id]
                if item_type is None or item.item_type == item_type:
                    items.append(item)
        
        items.sort(key=lambda x: x.timestamp, reverse=True)
        return items[:limit]
    
    async def get_chat_items(self, chat_id: int, item_type: str = None,
                            limit: int = 50) -> List[IndexedItem]:
        """Отримання елементів чату"""
        item_ids = self.chat_index.get(chat_id, set())
        
        items = []
        for item_id in item_ids:
            if item_id in self.items:
                item = self.items[item_id]
                if item_type is None or item.item_type == item_type:
                    items.append(item)
        
        items.sort(key=lambda x: x.timestamp, reverse=True)
        return items[:limit]
    
    def get_stats(self) -> Dict:
        """Отримання статистики"""
        return {
            **self.stats,
            "items_in_memory": len(self.items),
            "unique_tokens": len(self.inverted_index),
            "indexed_users": len(self.user_index),
            "indexed_chats": len(self.chat_index)
        }
    
    def format_stats_report(self) -> str:
        """Форматування звіту"""
        stats = self.get_stats()
        
        text = f"""<b>🧠 MEMORY INDEXER</b>
<i>Індексація в оперативній пам'яті</i>

───────────────

<b>📊 ІНДЕКС:</b>
├ 📝 Елементів: <b>{stats['items_in_memory']}</b> / {self.max_items}
├ 🔤 Токенів: <b>{stats['unique_tokens']}</b>
├ 👥 Користувачів: <b>{stats['indexed_users']}</b>
└ 💬 Чатів: <b>{stats['indexed_chats']}</b>

<b>🔍 ПОШУК:</b>
├ Запитів: <b>{stats['total_searches']}</b>
└ Сер. час: <b>{stats['avg_search_time_ms']:.2f} мс</b>

<b>📁 ПО ТИПАХ:</b>"""
        
        for item_type, count in stats.get("by_type", {}).items():
            text += f"\n├ {item_type}: <b>{count}</b>"
        
        if not stats.get("by_type"):
            text += "\n<i>Немає даних</i>"
        
        return text
    
    def format_search_result(self, result: SearchResult) -> str:
        """Форматування результату пошуку"""
        item = result.item
        
        type_icons = {
            "message": "💬",
            "user": "👤",
            "media": "🖼",
            "channel": "📢"
        }
        
        text = f"""{type_icons.get(item.item_type, '📝')} <b>{item.item_type.upper()}</b>
├ Score: {result.score * 100:.0f}%
├ ID: <code>{item.item_id}</code>
└ Контент: <i>{item.content[:100]}...</i>"""
        
        if result.highlights:
            text += "\n\n<b>Знайдено:</b>"
            for h in result.highlights:
                text += f"\n• <i>{h}</i>"
        
        return text


memory_indexer = MemoryIndexer()
