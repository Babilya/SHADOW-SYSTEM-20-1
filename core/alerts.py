import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)

class AlertType(str, Enum):
    CRITICAL = "critical"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    EMERGENCY = "emergency"

class AlertPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

ALERT_ICONS = {
    AlertType.CRITICAL: "🚨",
    AlertType.OPERATIONAL: "⚠️",
    AlertType.FINANCIAL: "🎫",
    AlertType.EMERGENCY: "🆘"
}

ALERT_DESCRIPTIONS = {
    AlertType.CRITICAL: "Критичні: спроби зламу, падіння БД, помилки шифрування",
    AlertType.OPERATIONAL: "Оперативні: перевищення лімітів, блокування ботів, OSINT результати",
    AlertType.FINANCIAL: "Фінансові: нові заявки на оплату, створення ключів",
    AlertType.EMERGENCY: "Екстрені: миттєве сповіщення всієї команди"
}

@dataclass
class Alert:
    id: str
    timestamp: datetime
    alert_type: AlertType
    priority: AlertPriority
    title: str
    message: str
    source_user_id: Optional[int]
    target_user_ids: List[int]
    data: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False
    acknowledged_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'type': self.alert_type.value,
            'priority': self.priority.value,
            'title': self.title,
            'message': self.message,
            'source_user_id': self.source_user_id,
            'acknowledged': self.acknowledged,
            'data': self.data
        }
    
    def format_message(self) -> str:
        icon = ALERT_ICONS.get(self.alert_type, "📢")
        priority_marker = "❗" if self.priority == AlertPriority.URGENT else ""
        
        return f"""{icon} <b>{self.title}</b> {priority_marker}

{self.message}

<i>ID: {self.id}</i>
<i>Час: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</i>"""

class AlertSystem:
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.subscribers: Dict[int, List[AlertType]] = {}
        self.send_callback: Optional[Callable] = None
        self._counter = 0
    
    def set_send_callback(self, callback: Callable):
        self.send_callback = callback
    
    def _generate_id(self, alert_type: AlertType) -> str:
        self._counter += 1
        prefix = alert_type.value[:3].upper()
        return f"{prefix}-{datetime.now().strftime('%Y%m%d%H%M')}-{self._counter:04d}"
    
    def subscribe(self, user_id: int, alert_types: List[AlertType] = None):
        if alert_types is None:
            alert_types = list(AlertType)
        self.subscribers[user_id] = alert_types
        logger.info(f"User {user_id} subscribed to alerts: {[t.value for t in alert_types]}")
    
    def unsubscribe(self, user_id: int):
        if user_id in self.subscribers:
            del self.subscribers[user_id]
            logger.info(f"User {user_id} unsubscribed from alerts")
    
    async def create_alert(
        self,
        alert_type: AlertType,
        title: str,
        message: str,
        priority: AlertPriority = AlertPriority.MEDIUM,
        source_user_id: Optional[int] = None,
        target_user_ids: List[int] = None,
        data: Dict[str, Any] = None
    ) -> Alert:
        alert_id = self._generate_id(alert_type)
        
        if target_user_ids is None:
            target_user_ids = [
                uid for uid, types in self.subscribers.items()
                if alert_type in types
            ]
        
        alert = Alert(
            id=alert_id,
            timestamp=datetime.now(),
            alert_type=alert_type,
            priority=priority,
            title=title,
            message=message,
            source_user_id=source_user_id,
            target_user_ids=target_user_ids,
            data=data or {}
        )
        
        self.alerts[alert_id] = alert
        logger.info(f"Alert created: {alert_id} - {title}")
        
        if self.send_callback and target_user_ids:
            await self._send_notifications(alert)
        
        return alert
    
    async def _send_notifications(self, alert: Alert):
        for user_id in alert.target_user_ids:
            try:
                if self.send_callback:
                    await self.send_callback(user_id, alert.format_message())
            except Exception as e:
                logger.error(f"Failed to send alert to {user_id}: {e}")
    
    async def critical_alert(
        self,
        title: str,
        message: str,
        source_user_id: int = None,
        data: Dict[str, Any] = None
    ) -> Alert:
        return await self.create_alert(
            alert_type=AlertType.CRITICAL,
            title=title,
            message=message,
            priority=AlertPriority.URGENT,
            source_user_id=source_user_id,
            data=data
        )
    
    async def operational_alert(
        self,
        title: str,
        message: str,
        source_user_id: int = None,
        data: Dict[str, Any] = None
    ) -> Alert:
        return await self.create_alert(
            alert_type=AlertType.OPERATIONAL,
            title=title,
            message=message,
            priority=AlertPriority.MEDIUM,
            source_user_id=source_user_id,
            data=data
        )
    
    async def financial_alert(
        self,
        title: str,
        message: str,
        source_user_id: int = None,
        data: Dict[str, Any] = None
    ) -> Alert:
        return await self.create_alert(
            alert_type=AlertType.FINANCIAL,
            title=title,
            message=message,
            priority=AlertPriority.HIGH,
            source_user_id=source_user_id,
            data=data
        )
    
    async def emergency_alert(
        self,
        title: str,
        message: str,
        source_user_id: int = None
    ) -> Alert:
        all_admins = [
            uid for uid, types in self.subscribers.items()
            if AlertType.EMERGENCY in types
        ]
        
        return await self.create_alert(
            alert_type=AlertType.EMERGENCY,
            title=f"🆘 ЕКСТРЕНА ТРИВОГА: {title}",
            message=message,
            priority=AlertPriority.URGENT,
            source_user_id=source_user_id,
            target_user_ids=all_admins,
            data={'emergency': True, 'broadcast': True}
        )
    
    def acknowledge_alert(self, alert_id: str, user_id: int) -> bool:
        alert = self.alerts.get(alert_id)
        if alert:
            alert.acknowledged = True
            alert.acknowledged_by = user_id
            alert.acknowledged_at = datetime.now()
            logger.info(f"Alert {alert_id} acknowledged by {user_id}")
            return True
        return False
    
    def get_unacknowledged(self, user_id: int = None) -> List[Alert]:
        alerts = [a for a in self.alerts.values() if not a.acknowledged]
        if user_id:
            alerts = [a for a in alerts if user_id in a.target_user_ids]
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    def get_alerts_by_type(self, alert_type: AlertType, limit: int = 50) -> List[Alert]:
        alerts = [a for a in self.alerts.values() if a.alert_type == alert_type]
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_recent_alerts(self, limit: int = 50) -> List[Alert]:
        alerts = sorted(self.alerts.values(), key=lambda x: x.timestamp, reverse=True)
        return alerts[:limit]

alert_system = AlertSystem()
