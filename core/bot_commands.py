import logging
import asyncio
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class CommandType(str, Enum):
    ADD_REACTION = "add_reaction"
    REMOVE_REACTION = "remove_reaction"
    WATCH_USER = "watch_user"
    UNWATCH_USER = "unwatch_user"
    WATCH_CHAT = "watch_chat"
    SEND_MESSAGE = "send_message"
    JOIN_CHAT = "join_chat"
    LEAVE_CHAT = "leave_chat"


class WatchEventType(str, Enum):
    USERNAME_CHANGED = "username_changed"
    NAME_CHANGED = "name_changed"
    PHOTO_CHANGED = "photo_changed"
    BIO_CHANGED = "bio_changed"
    STATUS_CHANGED = "status_changed"
    ONLINE_STATUS = "online_status"
    NEW_MESSAGE = "new_message"
    DELETED_MESSAGE = "deleted_message"


@dataclass
class BotCommand:
    command_id: str
    bot_id: str
    command_type: CommandType
    target_id: Optional[int] = None
    target_username: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class WatchTarget:
    target_id: int
    target_username: Optional[str]
    target_name: Optional[str]
    watch_events: Set[WatchEventType]
    added_at: datetime
    last_check: Optional[datetime] = None
    snapshot: Dict[str, Any] = field(default_factory=dict)
    notify_user_id: int = 0


@dataclass
class WatchAlert:
    alert_id: str
    event_type: WatchEventType
    target_id: int
    target_username: Optional[str]
    old_value: Any
    new_value: Any
    detected_at: datetime
    notified: bool = False


class BotCommandsManager:
    def __init__(self):
        self.pending_commands: Dict[str, List[BotCommand]] = defaultdict(list)
        self.command_history: List[BotCommand] = []
        self.watched_users: Dict[str, Dict[int, WatchTarget]] = defaultdict(dict)
        self.watched_chats: Dict[str, Set[int]] = defaultdict(set)
        self.alerts: List[WatchAlert] = []
        self._command_counter = 0
        self._alert_counter = 0
        
        self.available_reactions = [
            "👍", "👎", "❤️", "🔥", "🥰", "👏", "😁", "🤔", 
            "🤯", "😱", "🤬", "😢", "🎉", "🤩", "🤮", "💩",
            "🙏", "👌", "🕊", "🤡", "🥱", "🥴", "😍", "🐳",
            "❤️‍🔥", "🌚", "🌭", "💯", "🤣", "⚡️", "🍌", "🏆",
            "💔", "🤨", "😐", "🍓", "🍾", "💋", "🖕", "😈",
            "😴", "😭", "🤓", "👻", "👨‍💻", "👀", "🎃", "🙈",
            "😇", "😨", "🤝", "✍️", "🤗", "🫡", "🎅", "🎄",
            "☃️", "💅", "🤪", "🗿", "🆒", "💘", "🙉", "🦄"
        ]
        
        self.settings = {
            "max_pending_per_bot": 100,
            "watch_check_interval": 60,
            "max_watched_per_bot": 50,
            "alert_retention_hours": 168
        }
    
    def _generate_command_id(self) -> str:
        self._command_counter += 1
        return f"cmd_{self._command_counter}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def _generate_alert_id(self) -> str:
        self._alert_counter += 1
        return f"alert_{self._alert_counter}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    async def queue_command(
        self,
        bot_id: str,
        command_type: CommandType,
        target_id: int = None,
        target_username: str = None,
        params: Dict[str, Any] = None
    ) -> BotCommand:
        command = BotCommand(
            command_id=self._generate_command_id(),
            bot_id=bot_id,
            command_type=command_type,
            target_id=target_id,
            target_username=target_username,
            params=params or {}
        )
        
        self.pending_commands[bot_id].append(command)
        
        if len(self.pending_commands[bot_id]) > self.settings["max_pending_per_bot"]:
            self.pending_commands[bot_id] = self.pending_commands[bot_id][-self.settings["max_pending_per_bot"]:]
        
        logger.info(f"Queued command {command.command_id} for bot {bot_id}")
        return command
    
    async def add_reaction(
        self,
        bot_id: str,
        chat_id: int,
        message_id: int,
        reaction: str
    ) -> BotCommand:
        return await self.queue_command(
            bot_id=bot_id,
            command_type=CommandType.ADD_REACTION,
            target_id=chat_id,
            params={
                "message_id": message_id,
                "reaction": reaction
            }
        )
    
    async def remove_reaction(
        self,
        bot_id: str,
        chat_id: int,
        message_id: int
    ) -> BotCommand:
        return await self.queue_command(
            bot_id=bot_id,
            command_type=CommandType.REMOVE_REACTION,
            target_id=chat_id,
            params={"message_id": message_id}
        )
    
    async def watch_user(
        self,
        bot_id: str,
        user_id: int,
        username: str = None,
        name: str = None,
        events: List[WatchEventType] = None,
        notify_user_id: int = 0
    ) -> WatchTarget:
        if events is None:
            events = [
                WatchEventType.USERNAME_CHANGED,
                WatchEventType.NAME_CHANGED,
                WatchEventType.PHOTO_CHANGED,
                WatchEventType.STATUS_CHANGED
            ]
        
        if len(self.watched_users[bot_id]) >= self.settings["max_watched_per_bot"]:
            oldest = min(self.watched_users[bot_id].values(), key=lambda x: x.added_at)
            del self.watched_users[bot_id][oldest.target_id]
        
        target = WatchTarget(
            target_id=user_id,
            target_username=username,
            target_name=name,
            watch_events=set(events),
            added_at=datetime.now(),
            notify_user_id=notify_user_id,
            snapshot={
                "username": username,
                "name": name,
                "photo_id": None,
                "bio": None,
                "last_seen": None
            }
        )
        
        self.watched_users[bot_id][user_id] = target
        
        await self.queue_command(
            bot_id=bot_id,
            command_type=CommandType.WATCH_USER,
            target_id=user_id,
            target_username=username,
            params={"events": [e.value for e in events]}
        )
        
        logger.info(f"Added watch target {user_id} for bot {bot_id}")
        return target
    
    async def unwatch_user(self, bot_id: str, user_id: int) -> bool:
        if user_id in self.watched_users[bot_id]:
            del self.watched_users[bot_id][user_id]
            await self.queue_command(
                bot_id=bot_id,
                command_type=CommandType.UNWATCH_USER,
                target_id=user_id
            )
            return True
        return False
    
    async def check_user_changes(
        self,
        bot_id: str,
        user_id: int,
        current_data: Dict[str, Any]
    ) -> List[WatchAlert]:
        if user_id not in self.watched_users[bot_id]:
            return []
        
        target = self.watched_users[bot_id][user_id]
        alerts = []
        snapshot = target.snapshot
        
        if WatchEventType.USERNAME_CHANGED in target.watch_events:
            if current_data.get("username") != snapshot.get("username"):
                alert = WatchAlert(
                    alert_id=self._generate_alert_id(),
                    event_type=WatchEventType.USERNAME_CHANGED,
                    target_id=user_id,
                    target_username=target.target_username,
                    old_value=snapshot.get("username"),
                    new_value=current_data.get("username"),
                    detected_at=datetime.now()
                )
                alerts.append(alert)
                self.alerts.append(alert)
        
        if WatchEventType.NAME_CHANGED in target.watch_events:
            current_name = f"{current_data.get('first_name', '')} {current_data.get('last_name', '')}".strip()
            if current_name != snapshot.get("name"):
                alert = WatchAlert(
                    alert_id=self._generate_alert_id(),
                    event_type=WatchEventType.NAME_CHANGED,
                    target_id=user_id,
                    target_username=target.target_username,
                    old_value=snapshot.get("name"),
                    new_value=current_name,
                    detected_at=datetime.now()
                )
                alerts.append(alert)
                self.alerts.append(alert)
        
        if WatchEventType.PHOTO_CHANGED in target.watch_events:
            if current_data.get("photo_id") != snapshot.get("photo_id"):
                alert = WatchAlert(
                    alert_id=self._generate_alert_id(),
                    event_type=WatchEventType.PHOTO_CHANGED,
                    target_id=user_id,
                    target_username=target.target_username,
                    old_value=snapshot.get("photo_id"),
                    new_value=current_data.get("photo_id"),
                    detected_at=datetime.now()
                )
                alerts.append(alert)
                self.alerts.append(alert)
        
        if WatchEventType.BIO_CHANGED in target.watch_events:
            if current_data.get("bio") != snapshot.get("bio"):
                alert = WatchAlert(
                    alert_id=self._generate_alert_id(),
                    event_type=WatchEventType.BIO_CHANGED,
                    target_id=user_id,
                    target_username=target.target_username,
                    old_value=snapshot.get("bio"),
                    new_value=current_data.get("bio"),
                    detected_at=datetime.now()
                )
                alerts.append(alert)
                self.alerts.append(alert)
        
        target.snapshot = {
            "username": current_data.get("username"),
            "name": f"{current_data.get('first_name', '')} {current_data.get('last_name', '')}".strip(),
            "photo_id": current_data.get("photo_id"),
            "bio": current_data.get("bio"),
            "last_seen": current_data.get("last_seen")
        }
        target.last_check = datetime.now()
        
        return alerts
    
    async def get_pending_commands(self, bot_id: str) -> List[BotCommand]:
        return self.pending_commands.get(bot_id, [])
    
    async def mark_command_executed(
        self,
        command_id: str,
        bot_id: str,
        success: bool = True,
        result: Dict[str, Any] = None,
        error: str = None
    ):
        commands = self.pending_commands.get(bot_id, [])
        for cmd in commands:
            if cmd.command_id == command_id:
                cmd.executed_at = datetime.now()
                cmd.status = "completed" if success else "failed"
                cmd.result = result
                cmd.error = error
                
                self.command_history.append(cmd)
                self.pending_commands[bot_id].remove(cmd)
                break
    
    async def get_watched_users(self, bot_id: str) -> List[WatchTarget]:
        return list(self.watched_users.get(bot_id, {}).values())
    
    async def get_all_watched_users(self) -> Dict[str, List[WatchTarget]]:
        return {
            bot_id: list(targets.values())
            for bot_id, targets in self.watched_users.items()
        }
    
    async def get_unread_alerts(self) -> List[WatchAlert]:
        return [a for a in self.alerts if not a.notified]
    
    async def mark_alerts_notified(self, alert_ids: List[str]):
        for alert in self.alerts:
            if alert.alert_id in alert_ids:
                alert.notified = True
    
    async def cleanup_old_alerts(self):
        cutoff = datetime.now() - timedelta(hours=self.settings["alert_retention_hours"])
        self.alerts = [a for a in self.alerts if a.detected_at >= cutoff]
    
    def get_stats(self) -> Dict[str, Any]:
        total_pending = sum(len(cmds) for cmds in self.pending_commands.values())
        total_watched = sum(len(targets) for targets in self.watched_users.values())
        unread_alerts = len([a for a in self.alerts if not a.notified])
        
        return {
            "bots_with_commands": len(self.pending_commands),
            "total_pending_commands": total_pending,
            "total_watched_users": total_watched,
            "total_alerts": len(self.alerts),
            "unread_alerts": unread_alerts,
            "command_history_size": len(self.command_history),
            "timestamp": datetime.now().isoformat()
        }
    
    def format_command_queue(self, bot_id: str) -> str:
        commands = self.pending_commands.get(bot_id, [])
        
        lines = []
        lines.append("<b>📋 ЧЕРГА КОМАНД</b>")
        lines.append("═══════════════════════")
        lines.append(f"<b>Бот:</b> <code>{bot_id[:20]}</code>")
        lines.append(f"<b>Команд в черзі:</b> {len(commands)}")
        lines.append("")
        
        if not commands:
            lines.append("<i>Черга порожня</i>")
        else:
            for i, cmd in enumerate(commands[:10], 1):
                status_icon = "⏳" if cmd.status == "pending" else "✅" if cmd.status == "completed" else "❌"
                lines.append(f"{i}. {status_icon} <b>{cmd.command_type.value}</b>")
                if cmd.target_username:
                    lines.append(f"   └ @{cmd.target_username}")
                elif cmd.target_id:
                    lines.append(f"   └ ID: {cmd.target_id}")
        
        return "\n".join(lines)
    
    def format_watched_list(self, bot_id: str) -> str:
        targets = list(self.watched_users.get(bot_id, {}).values())
        
        lines = []
        lines.append("<b>👁 ВІДСТЕЖУВАНІ ЮЗЕРИ</b>")
        lines.append("═══════════════════════")
        lines.append(f"<b>Бот:</b> <code>{bot_id[:20]}</code>")
        lines.append(f"<b>Всього:</b> {len(targets)}")
        lines.append("")
        
        if not targets:
            lines.append("<i>Список порожній</i>")
        else:
            for i, target in enumerate(targets[:15], 1):
                name = target.target_username or target.target_name or str(target.target_id)
                events = ", ".join([e.value for e in list(target.watch_events)[:3]])
                lines.append(f"{i}. <b>{name}</b>")
                lines.append(f"   ├ ID: <code>{target.target_id}</code>")
                lines.append(f"   └ 👁 {events}")
        
        return "\n".join(lines)
    
    def format_alerts(self, alerts: List[WatchAlert]) -> str:
        lines = []
        lines.append("<b>🔔 СПОВІЩЕННЯ</b>")
        lines.append("═══════════════════════")
        lines.append(f"<b>Всього:</b> {len(alerts)}")
        lines.append("")
        
        if not alerts:
            lines.append("<i>Немає нових сповіщень</i>")
        else:
            event_icons = {
                WatchEventType.USERNAME_CHANGED: "👤",
                WatchEventType.NAME_CHANGED: "📝",
                WatchEventType.PHOTO_CHANGED: "🖼",
                WatchEventType.BIO_CHANGED: "📄",
                WatchEventType.STATUS_CHANGED: "🔵",
                WatchEventType.ONLINE_STATUS: "🟢"
            }
            
            for alert in alerts[:10]:
                icon = event_icons.get(alert.event_type, "📌")
                name = alert.target_username or str(alert.target_id)
                time_str = alert.detected_at.strftime("%d.%m %H:%M")
                
                lines.append(f"{icon} <b>{name}</b> — {alert.event_type.value}")
                lines.append(f"   ├ Було: <code>{alert.old_value or 'N/A'}</code>")
                lines.append(f"   ├ Стало: <code>{alert.new_value or 'N/A'}</code>")
                lines.append(f"   └ 🕐 {time_str}")
        
        return "\n".join(lines)


bot_commands = BotCommandsManager()
