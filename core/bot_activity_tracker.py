import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class ActivityType(str, Enum):
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    REACTION_ADDED = "reaction_added"
    CHAT_JOINED = "chat_joined"
    CHAT_LEFT = "chat_left"
    USER_CONTACTED = "user_contacted"
    COMMAND_EXECUTED = "command_executed"
    ERROR = "error"


@dataclass
class ConversationRecord:
    bot_id: str
    user_id: int
    user_username: Optional[str]
    user_name: Optional[str]
    first_contact: datetime
    last_message: datetime
    messages_sent: int = 0
    messages_received: int = 0
    is_incoming: bool = False
    chat_type: str = "private"
    last_message_preview: str = ""


@dataclass
class ActivityEvent:
    event_id: str
    bot_id: str
    activity_type: ActivityType
    timestamp: datetime
    target_id: Optional[int] = None
    target_username: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    success: bool = True


@dataclass
class BotActivityReport:
    bot_id: str
    bot_phone: str
    bot_username: Optional[str]
    period_start: datetime
    period_end: datetime
    total_messages_sent: int = 0
    total_messages_received: int = 0
    unique_conversations: int = 0
    active_chats: int = 0
    reactions_added: int = 0
    errors_count: int = 0
    health_score: int = 100
    conversations: List[ConversationRecord] = field(default_factory=list)
    activity_timeline: List[ActivityEvent] = field(default_factory=list)
    top_contacts: List[Dict[str, Any]] = field(default_factory=list)


class BotActivityTracker:
    def __init__(self):
        self.activities: Dict[str, List[ActivityEvent]] = defaultdict(list)
        self.conversations: Dict[str, Dict[int, ConversationRecord]] = defaultdict(dict)
        self.bot_stats: Dict[str, Dict[str, Any]] = {}
        self._event_counter = 0
        
        self.settings = {
            "max_events_per_bot": 10000,
            "max_conversations_per_bot": 1000,
            "retention_days": 30
        }
    
    def _generate_event_id(self) -> str:
        self._event_counter += 1
        return f"evt_{self._event_counter}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    async def log_activity(
        self,
        bot_id: str,
        activity_type: ActivityType,
        target_id: int = None,
        target_username: str = None,
        details: Dict[str, Any] = None,
        success: bool = True
    ) -> ActivityEvent:
        event = ActivityEvent(
            event_id=self._generate_event_id(),
            bot_id=bot_id,
            activity_type=activity_type,
            timestamp=datetime.now(),
            target_id=target_id,
            target_username=target_username,
            details=details or {},
            success=success
        )
        
        self.activities[bot_id].append(event)
        
        if len(self.activities[bot_id]) > self.settings["max_events_per_bot"]:
            self.activities[bot_id] = self.activities[bot_id][-self.settings["max_events_per_bot"]:]
        
        if bot_id not in self.bot_stats:
            self.bot_stats[bot_id] = self._init_bot_stats(bot_id)
        
        stats = self.bot_stats[bot_id]
        
        if activity_type == ActivityType.MESSAGE_SENT:
            stats["messages_sent"] += 1
            stats["messages_today"] += 1
        elif activity_type == ActivityType.MESSAGE_RECEIVED:
            stats["messages_received"] += 1
        elif activity_type == ActivityType.REACTION_ADDED:
            stats["reactions_added"] += 1
        elif activity_type == ActivityType.ERROR:
            stats["errors_count"] += 1
        
        stats["last_activity"] = datetime.now()
        
        if target_id and activity_type in [ActivityType.MESSAGE_SENT, ActivityType.MESSAGE_RECEIVED]:
            await self._update_conversation(bot_id, target_id, target_username, event)
        
        return event
    
    def _init_bot_stats(self, bot_id: str) -> Dict[str, Any]:
        return {
            "bot_id": bot_id,
            "messages_sent": 0,
            "messages_received": 0,
            "messages_today": 0,
            "reactions_added": 0,
            "errors_count": 0,
            "first_activity": datetime.now(),
            "last_activity": datetime.now(),
            "health_score": 100
        }
    
    async def _update_conversation(
        self,
        bot_id: str,
        user_id: int,
        username: str,
        event: ActivityEvent
    ):
        if user_id not in self.conversations[bot_id]:
            self.conversations[bot_id][user_id] = ConversationRecord(
                bot_id=bot_id,
                user_id=user_id,
                user_username=username,
                user_name=event.details.get("user_name"),
                first_contact=datetime.now(),
                last_message=datetime.now(),
                is_incoming=event.activity_type == ActivityType.MESSAGE_RECEIVED
            )
        
        conv = self.conversations[bot_id][user_id]
        conv.last_message = datetime.now()
        
        if event.activity_type == ActivityType.MESSAGE_SENT:
            conv.messages_sent += 1
        elif event.activity_type == ActivityType.MESSAGE_RECEIVED:
            conv.messages_received += 1
            conv.is_incoming = True
        
        if "message_preview" in event.details:
            conv.last_message_preview = event.details["message_preview"][:100]
        
        if len(self.conversations[bot_id]) > self.settings["max_conversations_per_bot"]:
            oldest = min(self.conversations[bot_id].values(), key=lambda x: x.last_message)
            del self.conversations[bot_id][oldest.user_id]
    
    async def get_bot_report(
        self,
        bot_id: str,
        period_hours: int = 24
    ) -> BotActivityReport:
        now = datetime.now()
        period_start = now - timedelta(hours=period_hours)
        
        stats = self.bot_stats.get(bot_id, self._init_bot_stats(bot_id))
        
        activities = [
            e for e in self.activities.get(bot_id, [])
            if e.timestamp >= period_start
        ]
        
        conversations = list(self.conversations.get(bot_id, {}).values())
        conversations.sort(key=lambda x: x.last_message, reverse=True)
        
        top_contacts = []
        for conv in conversations[:10]:
            top_contacts.append({
                "user_id": conv.user_id,
                "username": conv.user_username,
                "name": conv.user_name,
                "messages_sent": conv.messages_sent,
                "messages_received": conv.messages_received,
                "last_message": conv.last_message.isoformat(),
                "is_incoming": conv.is_incoming
            })
        
        messages_sent = sum(1 for e in activities if e.activity_type == ActivityType.MESSAGE_SENT)
        messages_received = sum(1 for e in activities if e.activity_type == ActivityType.MESSAGE_RECEIVED)
        reactions = sum(1 for e in activities if e.activity_type == ActivityType.REACTION_ADDED)
        errors = sum(1 for e in activities if e.activity_type == ActivityType.ERROR)
        
        return BotActivityReport(
            bot_id=bot_id,
            bot_phone=stats.get("phone", "Unknown"),
            bot_username=stats.get("username"),
            period_start=period_start,
            period_end=now,
            total_messages_sent=messages_sent,
            total_messages_received=messages_received,
            unique_conversations=len(conversations),
            active_chats=len([c for c in conversations if c.last_message >= period_start]),
            reactions_added=reactions,
            errors_count=errors,
            health_score=stats.get("health_score", 100),
            conversations=conversations[:20],
            activity_timeline=activities[-50:],
            top_contacts=top_contacts
        )
    
    async def get_all_bots_summary(self) -> List[Dict[str, Any]]:
        summaries = []
        
        for bot_id, stats in self.bot_stats.items():
            last_activity = stats.get("last_activity")
            is_active = False
            if last_activity:
                is_active = (datetime.now() - last_activity).seconds < 3600
            
            summaries.append({
                "bot_id": bot_id,
                "phone": stats.get("phone", "Unknown"),
                "username": stats.get("username"),
                "messages_sent": stats.get("messages_sent", 0),
                "messages_received": stats.get("messages_received", 0),
                "conversations": len(self.conversations.get(bot_id, {})),
                "health_score": stats.get("health_score", 100),
                "is_active": is_active,
                "last_activity": last_activity.isoformat() if last_activity else None
            })
        
        summaries.sort(key=lambda x: x["messages_sent"], reverse=True)
        return summaries
    
    async def get_incoming_contacts(self, bot_id: str) -> List[ConversationRecord]:
        conversations = self.conversations.get(bot_id, {})
        incoming = [c for c in conversations.values() if c.is_incoming]
        incoming.sort(key=lambda x: x.last_message, reverse=True)
        return incoming
    
    async def get_outgoing_conversations(self, bot_id: str) -> List[ConversationRecord]:
        conversations = self.conversations.get(bot_id, {})
        outgoing = [c for c in conversations.values() if not c.is_incoming]
        outgoing.sort(key=lambda x: x.last_message, reverse=True)
        return outgoing
    
    def format_report(self, report: BotActivityReport) -> str:
        lines = []
        lines.append(f"📊 <b>ЗВІТ БОТА</b>")
        lines.append("═══════════════════════")
        lines.append(f"<b>ID:</b> <code>{report.bot_id}</code>")
        if report.bot_username:
            lines.append(f"<b>Username:</b> @{report.bot_username}")
        lines.append(f"<b>Телефон:</b> <code>{report.bot_phone}</code>")
        lines.append("")
        
        health_icon = "🟢" if report.health_score >= 80 else "🟡" if report.health_score >= 50 else "🔴"
        lines.append(f"<b>Здоров'я:</b> {health_icon} {report.health_score}%")
        lines.append("")
        
        lines.append(f"<b>📈 Статистика (24 год):</b>")
        lines.append(f"├ Відправлено: {report.total_messages_sent}")
        lines.append(f"├ Отримано: {report.total_messages_received}")
        lines.append(f"├ Реакцій: {report.reactions_added}")
        lines.append(f"├ Помилок: {report.errors_count}")
        lines.append(f"├ Унікальних діалогів: {report.unique_conversations}")
        lines.append(f"└ Активних чатів: {report.active_chats}")
        lines.append("")
        
        if report.top_contacts:
            lines.append(f"<b>👤 Топ контакти:</b>")
            for i, contact in enumerate(report.top_contacts[:5], 1):
                name = contact.get("username") or contact.get("name") or str(contact.get("user_id"))
                incoming_icon = "📩" if contact.get("is_incoming") else "📤"
                lines.append(f"{i}. {incoming_icon} {name}")
                lines.append(f"   └ ↑{contact['messages_sent']} ↓{contact['messages_received']}")
        
        return "\n".join(lines)
    
    def format_conversations_list(self, conversations: List[ConversationRecord], title: str) -> str:
        lines = []
        lines.append(f"<b>{title}</b>")
        lines.append("═══════════════════════")
        
        if not conversations:
            lines.append("<i>Немає даних</i>")
            return "\n".join(lines)
        
        for i, conv in enumerate(conversations[:15], 1):
            name = conv.user_username or conv.user_name or str(conv.user_id)
            time_ago = self._time_ago(conv.last_message)
            
            lines.append(f"<b>{i}. {name}</b>")
            lines.append(f"   ├ ID: <code>{conv.user_id}</code>")
            lines.append(f"   ├ ↑{conv.messages_sent} ↓{conv.messages_received}")
            lines.append(f"   └ {time_ago}")
            
            if conv.last_message_preview:
                preview = conv.last_message_preview[:50]
                lines.append(f"   💬 <i>{preview}...</i>")
        
        return "\n".join(lines)
    
    def _time_ago(self, dt: datetime) -> str:
        diff = datetime.now() - dt
        
        if diff.days > 0:
            return f"{diff.days} дн. тому"
        elif diff.seconds >= 3600:
            return f"{diff.seconds // 3600} год. тому"
        elif diff.seconds >= 60:
            return f"{diff.seconds // 60} хв. тому"
        else:
            return "Щойно"
    
    async def cleanup_old_data(self):
        cutoff = datetime.now() - timedelta(days=self.settings["retention_days"])
        
        for bot_id in list(self.activities.keys()):
            self.activities[bot_id] = [
                e for e in self.activities[bot_id]
                if e.timestamp >= cutoff
            ]
        
        for bot_id in list(self.conversations.keys()):
            for user_id in list(self.conversations[bot_id].keys()):
                if self.conversations[bot_id][user_id].last_message < cutoff:
                    del self.conversations[bot_id][user_id]
    
    def get_stats(self) -> Dict[str, Any]:
        total_events = sum(len(events) for events in self.activities.values())
        total_conversations = sum(len(convs) for convs in self.conversations.values())
        
        return {
            "bots_tracked": len(self.bot_stats),
            "total_events": total_events,
            "total_conversations": total_conversations,
            "timestamp": datetime.now().isoformat()
        }


bot_activity_tracker = BotActivityTracker()
