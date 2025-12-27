"""
Enhanced Monitoring - Покращена система моніторингу
Комплексний моніторинг каналів, чатів та користувачів
"""

import asyncio
import json
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
import logging
import re

logger = logging.getLogger(__name__)

@dataclass
class MonitoringTarget:
    """Ціль моніторингу"""
    target_id: int
    target_type: str  # channel, chat, user
    name: str
    username: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_check: Optional[datetime] = None
    settings: Dict = field(default_factory=dict)
    stats: Dict = field(default_factory=dict)


@dataclass
class MonitoringEvent:
    """Подія моніторингу"""
    event_id: str
    target_id: int
    event_type: str  # new_message, new_member, member_left, message_deleted, message_edited
    timestamp: datetime
    data: Dict = field(default_factory=dict)
    processed: bool = False


@dataclass
class MonitoringAlert:
    """Сповіщення моніторингу"""
    alert_id: str
    target_id: int
    alert_type: str  # keyword, spam, suspicious, activity_spike
    severity: str  # low, medium, high, critical
    message: str
    timestamp: datetime
    data: Dict = field(default_factory=dict)
    acknowledged: bool = False


class EnhancedMonitoring:
    """Покращена система моніторингу"""
    
    def __init__(self):
        self.targets: Dict[int, MonitoringTarget] = {}
        self.events: List[MonitoringEvent] = []
        self.alerts: List[MonitoringAlert] = []
        
        self.keyword_triggers: Dict[int, List[str]] = defaultdict(list)
        self.regex_triggers: Dict[int, List[str]] = defaultdict(list)
        
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        self.stats = {
            "total_targets": 0,
            "active_targets": 0,
            "total_events": 0,
            "total_alerts": 0,
            "events_today": 0,
            "alerts_today": 0,
            "by_event_type": {},
            "by_alert_type": {}
        }
        
        self._event_counter = 0
        self._alert_counter = 0
    
    async def add_target(self, target_id: int, target_type: str,
                        name: str, username: str = "",
                        settings: Dict = None) -> MonitoringTarget:
        """Додавання цілі моніторингу"""
        target = MonitoringTarget(
            target_id=target_id,
            target_type=target_type,
            name=name,
            username=username,
            settings=settings or {}
        )
        
        self.targets[target_id] = target
        
        self.stats["total_targets"] += 1
        self.stats["active_targets"] += 1
        
        logger.info(f"Added monitoring target: {target_id} ({target_type})")
        return target
    
    async def remove_target(self, target_id: int) -> bool:
        """Видалення цілі моніторингу"""
        if target_id in self.targets:
            del self.targets[target_id]
            self.stats["total_targets"] -= 1
            self.stats["active_targets"] -= 1
            return True
        return False
    
    async def toggle_target(self, target_id: int) -> bool:
        """Увімкнення/вимкнення моніторингу"""
        if target_id in self.targets:
            target = self.targets[target_id]
            target.is_active = not target.is_active
            
            if target.is_active:
                self.stats["active_targets"] += 1
            else:
                self.stats["active_targets"] -= 1
            
            return target.is_active
        return False
    
    async def add_keyword_trigger(self, target_id: int, keyword: str):
        """Додавання тригера за ключовим словом"""
        self.keyword_triggers[target_id].append(keyword.lower())
    
    async def add_regex_trigger(self, target_id: int, pattern: str):
        """Додавання тригера за регулярним виразом"""
        self.regex_triggers[target_id].append(pattern)
    
    async def process_message(self, target_id: int, message: Any) -> List[MonitoringAlert]:
        """Обробка повідомлення"""
        if target_id not in self.targets:
            return []
        
        target = self.targets[target_id]
        if not target.is_active:
            return []
        
        text = ""
        if hasattr(message, 'text') and message.text:
            text = message.text
        elif hasattr(message, 'caption') and message.caption:
            text = message.caption
        
        user_id = message.from_user.id if hasattr(message, 'from_user') and message.from_user else 0
        message_id = message.message_id if hasattr(message, 'message_id') else 0
        
        event = await self._create_event(
            target_id=target_id,
            event_type="new_message",
            data={
                "message_id": message_id,
                "user_id": user_id,
                "text": text[:500],
                "has_media": bool(hasattr(message, 'photo') and message.photo)
            }
        )
        
        alerts = []
        
        for keyword in self.keyword_triggers.get(target_id, []):
            if keyword in text.lower():
                alert = await self._create_alert(
                    target_id=target_id,
                    alert_type="keyword",
                    severity="medium",
                    message=f"Знайдено ключове слово: {keyword}",
                    data={
                        "keyword": keyword,
                        "message_id": message_id,
                        "text_preview": text[:100]
                    }
                )
                alerts.append(alert)
        
        for pattern in self.regex_triggers.get(target_id, []):
            try:
                if re.search(pattern, text, re.IGNORECASE):
                    alert = await self._create_alert(
                        target_id=target_id,
                        alert_type="keyword",
                        severity="medium",
                        message=f"Знайдено паттерн: {pattern}",
                        data={
                            "pattern": pattern,
                            "message_id": message_id
                        }
                    )
                    alerts.append(alert)
            except re.error:
                pass
        
        spam_alerts = await self._check_spam_patterns(target_id, text, user_id)
        alerts.extend(spam_alerts)
        
        target.last_check = datetime.now()
        target.stats["messages"] = target.stats.get("messages", 0) + 1
        
        for handler in self.event_handlers.get("new_message", []):
            try:
                await handler(event, alerts)
            except Exception as e:
                logger.warning(f"Handler error: {e}")
        
        return alerts
    
    async def process_member_join(self, target_id: int, user_id: int, 
                                 username: str = "") -> MonitoringEvent:
        """Обробка нового учасника"""
        event = await self._create_event(
            target_id=target_id,
            event_type="new_member",
            data={
                "user_id": user_id,
                "username": username
            }
        )
        
        if target_id in self.targets:
            target = self.targets[target_id]
            target.stats["members_joined"] = target.stats.get("members_joined", 0) + 1
        
        return event
    
    async def process_member_left(self, target_id: int, user_id: int) -> MonitoringEvent:
        """Обробка виходу учасника"""
        event = await self._create_event(
            target_id=target_id,
            event_type="member_left",
            data={"user_id": user_id}
        )
        
        if target_id in self.targets:
            target = self.targets[target_id]
            target.stats["members_left"] = target.stats.get("members_left", 0) + 1
        
        return event
    
    async def process_message_deleted(self, target_id: int, message_ids: List[int]) -> MonitoringEvent:
        """Обробка видалення повідомлень"""
        event = await self._create_event(
            target_id=target_id,
            event_type="message_deleted",
            data={
                "message_ids": message_ids,
                "count": len(message_ids)
            }
        )
        
        if target_id in self.targets:
            target = self.targets[target_id]
            target.stats["deleted"] = target.stats.get("deleted", 0) + len(message_ids)
        
        return event
    
    async def _create_event(self, target_id: int, event_type: str, 
                           data: Dict = None) -> MonitoringEvent:
        """Створення події"""
        self._event_counter += 1
        event_id = f"evt_{self._event_counter}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        event = MonitoringEvent(
            event_id=event_id,
            target_id=target_id,
            event_type=event_type,
            timestamp=datetime.now(),
            data=data or {}
        )
        
        self.events.append(event)
        
        if len(self.events) > 10000:
            self.events = self.events[-5000:]
        
        self.stats["total_events"] += 1
        self.stats["events_today"] += 1
        self.stats["by_event_type"][event_type] = self.stats["by_event_type"].get(event_type, 0) + 1
        
        return event
    
    async def _create_alert(self, target_id: int, alert_type: str,
                           severity: str, message: str,
                           data: Dict = None) -> MonitoringAlert:
        """Створення сповіщення"""
        self._alert_counter += 1
        alert_id = f"alrt_{self._alert_counter}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        alert = MonitoringAlert(
            alert_id=alert_id,
            target_id=target_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            timestamp=datetime.now(),
            data=data or {}
        )
        
        self.alerts.append(alert)
        
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-500:]
        
        self.stats["total_alerts"] += 1
        self.stats["alerts_today"] += 1
        self.stats["by_alert_type"][alert_type] = self.stats["by_alert_type"].get(alert_type, 0) + 1
        
        for handler in self.event_handlers.get("alert", []):
            try:
                await handler(alert)
            except Exception as e:
                logger.warning(f"Alert handler error: {e}")
        
        return alert
    
    async def _check_spam_patterns(self, target_id: int, text: str, 
                                  user_id: int) -> List[MonitoringAlert]:
        """Перевірка на спам"""
        alerts = []
        
        spam_indicators = [
            (r'https?://\S+', 'URL_SPAM', 'Виявлено посилання'),
            (r'[А-ЯІЇЄ]{20,}', 'CAPS_SPAM', 'Забагато великих літер'),
            (r'(.)\1{5,}', 'REPEAT_SPAM', 'Повторювані символи'),
            (r'безкоштовно|виграш|приз|акція|знижка 90%', 'PROMO_SPAM', 'Промо-спам'),
        ]
        
        for pattern, spam_type, description in spam_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                alert = await self._create_alert(
                    target_id=target_id,
                    alert_type="spam",
                    severity="low",
                    message=f"Спам: {description}",
                    data={
                        "spam_type": spam_type,
                        "user_id": user_id
                    }
                )
                alerts.append(alert)
        
        return alerts
    
    def register_handler(self, event_type: str, handler: Callable):
        """Реєстрація обробника подій"""
        self.event_handlers[event_type].append(handler)
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Підтвердження сповіщення"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False
    
    def get_target_stats(self, target_id: int) -> Dict:
        """Отримання статистики цілі"""
        if target_id not in self.targets:
            return {}
        
        target = self.targets[target_id]
        
        target_events = [e for e in self.events if e.target_id == target_id]
        target_alerts = [a for a in self.alerts if a.target_id == target_id]
        
        return {
            "target": {
                "id": target.target_id,
                "type": target.target_type,
                "name": target.name,
                "is_active": target.is_active,
                "last_check": target.last_check.isoformat() if target.last_check else None
            },
            "stats": target.stats,
            "events_count": len(target_events),
            "alerts_count": len(target_alerts),
            "unacknowledged_alerts": len([a for a in target_alerts if not a.acknowledged])
        }
    
    def get_recent_events(self, target_id: int = None, limit: int = 50) -> List[MonitoringEvent]:
        """Отримання останніх подій"""
        events = self.events
        if target_id:
            events = [e for e in events if e.target_id == target_id]
        
        return sorted(events, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_recent_alerts(self, target_id: int = None, 
                         unacknowledged_only: bool = False,
                         limit: int = 50) -> List[MonitoringAlert]:
        """Отримання останніх сповіщень"""
        alerts = self.alerts
        if target_id:
            alerts = [a for a in alerts if a.target_id == target_id]
        if unacknowledged_only:
            alerts = [a for a in alerts if not a.acknowledged]
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_stats(self) -> Dict:
        """Отримання загальної статистики"""
        return {
            **self.stats,
            "targets_list": len(self.targets),
            "pending_alerts": len([a for a in self.alerts if not a.acknowledged])
        }
    
    def format_target_info(self, target: MonitoringTarget) -> str:
        """Форматування інформації про ціль"""
        type_icons = {
            "channel": "📢",
            "chat": "💬",
            "user": "👤"
        }
        
        status = "🟢 Активний" if target.is_active else "🔴 Вимкнено"
        
        text = f"""{type_icons.get(target.target_type, '📝')} <b>{target.name}</b>
├ ID: <code>{target.target_id}</code>
├ Тип: {target.target_type}
├ Статус: {status}
└ Username: @{target.username or 'N/A'}

<b>📊 Статистика:</b>"""
        
        for key, value in target.stats.items():
            text += f"\n├ {key}: <b>{value}</b>"
        
        if target.last_check:
            text += f"\n\n<b>⏰ Остання перевірка:</b> {target.last_check.strftime('%d.%m.%Y %H:%M')}"
        
        return text
    
    def format_alert(self, alert: MonitoringAlert) -> str:
        """Форматування сповіщення"""
        severity_icons = {
            "low": "🟡",
            "medium": "🟠",
            "high": "🔴",
            "critical": "⚫"
        }
        
        status = "✅" if alert.acknowledged else "⚠️"
        
        text = f"""{severity_icons.get(alert.severity, '⚪')} <b>{alert.alert_type.upper()}</b> {status}

<b>📋 Повідомлення:</b>
{alert.message}

<b>📅 Час:</b> {alert.timestamp.strftime('%d.%m.%Y %H:%M:%S')}
<b>🎯 Ціль:</b> {alert.target_id}
<b>🔖 ID:</b> <code>{alert.alert_id}</code>"""
        
        return text
    
    def format_stats_report(self) -> str:
        """Форматування звіту статистики"""
        stats = self.get_stats()
        
        text = f"""<b>📡 ENHANCED MONITORING</b>
<i>Покращена система моніторингу</i>

───────────────

<b>🎯 ЦІЛІ:</b>
├ Всього: <b>{stats['total_targets']}</b>
└ Активних: <b>{stats['active_targets']}</b>

<b>📊 ПОДІЇ:</b>
├ Всього: <b>{stats['total_events']}</b>
└ Сьогодні: <b>{stats['events_today']}</b>

<b>⚠️ СПОВІЩЕННЯ:</b>
├ Всього: <b>{stats['total_alerts']}</b>
├ Сьогодні: <b>{stats['alerts_today']}</b>
└ Очікують: <b>{stats['pending_alerts']}</b>

<b>📁 ПО ТИПАХ ПОДІЙ:</b>"""
        
        for event_type, count in stats.get("by_event_type", {}).items():
            text += f"\n├ {event_type}: <b>{count}</b>"
        
        if not stats.get("by_event_type"):
            text += "\n<i>Немає даних</i>"
        
        return text


enhanced_monitoring = EnhancedMonitoring()
