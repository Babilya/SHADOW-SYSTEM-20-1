"""
Flood Event Monitor for SHADOW SYSTEM
Monitors and alerts on Telegram flood events
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class FloodSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FloodType(Enum):
    FLOOD_WAIT = "flood_wait"
    PEER_FLOOD = "peer_flood"
    PRIVACY_RESTRICTED = "privacy_restricted"
    USER_BANNED = "user_banned"
    SESSION_EXPIRED = "session_expired"


@dataclass
class FloodEvent:
    """Represents a flood event"""
    event_id: str
    flood_type: FloodType
    session_id: str
    task_id: Optional[str]
    wait_seconds: int
    timestamp: datetime
    user_id: Optional[int] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class FloodAlert:
    """Alert generated from flood monitoring"""
    alert_id: str
    severity: FloodSeverity
    title: str
    message: str
    timestamp: datetime
    events: List[FloodEvent] = field(default_factory=list)
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[int] = None


class FloodMonitor:
    """
    Monitors flood events and generates alerts
    
    Features:
    - Track all flood events by session/task
    - Generate alerts based on thresholds
    - Auto-pause tasks on excessive floods
    - Statistics and reporting
    """
    
    def __init__(self):
        self.events: Dict[str, FloodEvent] = {}
        self.alerts: Dict[str, FloodAlert] = {}
        self.session_floods: Dict[str, List[FloodEvent]] = defaultdict(list)
        self.task_floods: Dict[str, List[FloodEvent]] = defaultdict(list)
        
        self.alert_callbacks: List[Callable] = []
        
        self.thresholds = {
            "floods_per_session_warn": 3,
            "floods_per_session_critical": 5,
            "floods_per_task_warn": 5,
            "floods_per_task_critical": 10,
            "wait_seconds_warn": 300,
            "wait_seconds_critical": 600,
            "window_minutes": 60
        }
        
        self.stats = {
            "total_events": 0,
            "total_alerts": 0,
            "sessions_paused": 0,
            "tasks_paused": 0,
            "total_wait_time": 0
        }
        
        self._event_counter = 0
        self._alert_counter = 0
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        self._event_counter += 1
        return f"FE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self._event_counter:04d}"
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID"""
        self._alert_counter += 1
        return f"FA-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self._alert_counter:04d}"
    
    def record_event(
        self,
        flood_type: FloodType,
        session_id: str,
        wait_seconds: int = 0,
        task_id: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> FloodEvent:
        """Record a new flood event"""
        event = FloodEvent(
            event_id=self._generate_event_id(),
            flood_type=flood_type,
            session_id=session_id,
            task_id=task_id,
            wait_seconds=wait_seconds,
            timestamp=datetime.now(),
            user_id=user_id
        )
        
        self.events[event.event_id] = event
        self.session_floods[session_id].append(event)
        
        if task_id:
            self.task_floods[task_id].append(event)
        
        self.stats["total_events"] += 1
        self.stats["total_wait_time"] += wait_seconds
        
        logger.warning(
            f"Flood event recorded: {flood_type.value} for session {session_id}, "
            f"wait {wait_seconds}s"
        )
        
        self._check_thresholds(event)
        
        return event
    
    def _check_thresholds(self, event: FloodEvent):
        """Check if thresholds are exceeded and generate alerts"""
        now = datetime.now()
        window = timedelta(minutes=self.thresholds["window_minutes"])
        
        recent_session_floods = [
            e for e in self.session_floods[event.session_id]
            if now - e.timestamp < window
        ]
        
        if len(recent_session_floods) >= self.thresholds["floods_per_session_critical"]:
            self._create_alert(
                FloodSeverity.CRITICAL,
                f"Критично: сесія {event.session_id}",
                f"Сесія отримала {len(recent_session_floods)} flood подій за годину. "
                f"Рекомендовано призупинити всі задачі цієї сесії.",
                recent_session_floods
            )
        elif len(recent_session_floods) >= self.thresholds["floods_per_session_warn"]:
            self._create_alert(
                FloodSeverity.MEDIUM,
                f"Увага: сесія {event.session_id}",
                f"Сесія отримала {len(recent_session_floods)} flood подій. "
                f"Можливо варто знизити швидкість.",
                recent_session_floods
            )
        
        if event.wait_seconds >= self.thresholds["wait_seconds_critical"]:
            self._create_alert(
                FloodSeverity.HIGH,
                f"Довге очікування: {event.wait_seconds}s",
                f"Telegram вимагає очікування {event.wait_seconds} секунд. "
                f"Сесія: {event.session_id}",
                [event]
            )
        
        if event.task_id:
            recent_task_floods = [
                e for e in self.task_floods[event.task_id]
                if now - e.timestamp < window
            ]
            
            if len(recent_task_floods) >= self.thresholds["floods_per_task_critical"]:
                self._create_alert(
                    FloodSeverity.CRITICAL,
                    f"Задача заблокована",
                    f"Задача {event.task_id} отримала {len(recent_task_floods)} flood подій. "
                    f"Автоматична пауза.",
                    recent_task_floods
                )
    
    def _create_alert(
        self,
        severity: FloodSeverity,
        title: str,
        message: str,
        events: List[FloodEvent]
    ) -> FloodAlert:
        """Create new alert"""
        alert = FloodAlert(
            alert_id=self._generate_alert_id(),
            severity=severity,
            title=title,
            message=message,
            timestamp=datetime.now(),
            events=events
        )
        
        self.alerts[alert.alert_id] = alert
        self.stats["total_alerts"] += 1
        
        logger.warning(f"Flood alert created: [{severity.value}] {title}")
        
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
        
        return alert
    
    def add_alert_callback(self, callback: Callable[[FloodAlert], Any]):
        """Add callback for new alerts"""
        self.alert_callbacks.append(callback)
    
    def acknowledge_alert(self, alert_id: str, user_id: int) -> bool:
        """Acknowledge an alert"""
        if alert_id not in self.alerts:
            return False
        
        alert = self.alerts[alert_id]
        alert.acknowledged = True
        alert.acknowledged_at = datetime.now()
        alert.acknowledged_by = user_id
        
        return True
    
    def resolve_event(self, event_id: str) -> bool:
        """Mark event as resolved"""
        if event_id not in self.events:
            return False
        
        event = self.events[event_id]
        event.resolved = True
        event.resolved_at = datetime.now()
        
        return True
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get flood status for a session"""
        now = datetime.now()
        window = timedelta(minutes=self.thresholds["window_minutes"])
        
        recent = [
            e for e in self.session_floods.get(session_id, [])
            if now - e.timestamp < window
        ]
        
        total_wait = sum(e.wait_seconds for e in recent)
        
        if len(recent) >= self.thresholds["floods_per_session_critical"]:
            status = "critical"
        elif len(recent) >= self.thresholds["floods_per_session_warn"]:
            status = "warning"
        else:
            status = "ok"
        
        return {
            "session_id": session_id,
            "status": status,
            "recent_floods": len(recent),
            "total_wait_seconds": total_wait,
            "last_flood": recent[-1].timestamp.isoformat() if recent else None
        }
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get flood status for a task"""
        now = datetime.now()
        window = timedelta(minutes=self.thresholds["window_minutes"])
        
        recent = [
            e for e in self.task_floods.get(task_id, [])
            if now - e.timestamp < window
        ]
        
        return {
            "task_id": task_id,
            "recent_floods": len(recent),
            "should_pause": len(recent) >= self.thresholds["floods_per_task_critical"]
        }
    
    def get_active_alerts(self, severity: Optional[FloodSeverity] = None) -> List[FloodAlert]:
        """Get unacknowledged alerts"""
        alerts = [a for a in self.alerts.values() if not a.acknowledged]
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        recent_events = [
            e for e in self.events.values()
            if e.timestamp > hour_ago
        ]
        
        return {
            **self.stats,
            "active_alerts": len(self.get_active_alerts()),
            "events_last_hour": len(recent_events),
            "avg_wait_time": (
                self.stats["total_wait_time"] / self.stats["total_events"]
                if self.stats["total_events"] > 0 else 0
            )
        }
    
    def get_report(self) -> str:
        """Generate flood monitoring report"""
        stats = self.get_stats()
        active_alerts = self.get_active_alerts()
        
        report = f"""📊 <b>FLOOD MONITOR REPORT</b>
───────────────────────
<b>📈 Статистика:</b>
├ Всього подій: {stats['total_events']}
├ Активних алертів: {stats['active_alerts']}
├ За останню годину: {stats['events_last_hour']}
└ Середній час очікування: {stats['avg_wait_time']:.0f}s

<b>⚠️ Активні алерти:</b>"""
        
        if active_alerts:
            for alert in active_alerts[:5]:
                severity_emoji = {
                    FloodSeverity.LOW: "🟢",
                    FloodSeverity.MEDIUM: "🟡",
                    FloodSeverity.HIGH: "🟠",
                    FloodSeverity.CRITICAL: "🔴"
                }
                report += f"\n{severity_emoji[alert.severity]} {alert.title}"
        else:
            report += "\n✅ Немає активних алертів"
        
        return report
    
    def update_thresholds(self, **kwargs):
        """Update monitoring thresholds"""
        for key, value in kwargs.items():
            if key in self.thresholds:
                self.thresholds[key] = value
                logger.info(f"Threshold updated: {key} = {value}")


flood_monitor = FloodMonitor()
