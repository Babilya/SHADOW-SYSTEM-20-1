import asyncio
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Set
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class ThreatLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class MonitoringThresholds:
    """Порогові значення для моніторингу"""
    messages_per_minute: int = 10
    messages_per_hour: int = 100
    coordinate_messages: int = 3
    new_users_per_hour: int = 20
    suspicious_keywords_per_hour: int = 5
    flood_messages: int = 50
    links_per_message: int = 5
    mentions_per_minute: int = 10

@dataclass
class ActivityRecord:
    """Запис активності"""
    user_id: int
    chat_id: int
    message_id: int
    text: str
    timestamp: datetime
    flags: List[str] = field(default_factory=list)
    patterns_found: Dict[str, List] = field(default_factory=dict)
    threat_score: int = 0

@dataclass
class MonitoringAlert:
    """Алерт моніторингу"""
    id: str
    timestamp: datetime
    alert_type: str
    threat_level: ThreatLevel
    chat_id: int
    user_id: Optional[int]
    description: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    auto_action_taken: Optional[str] = None

class RealTimeMonitor:
    """Моніторинг активності в реальному часі через Telethon events"""
    
    def __init__(self, api_id: int = None, api_hash: str = None):
        self.api_id = api_id or int(os.getenv('TELEGRAM_API_ID', '0'))
        self.api_hash = api_hash or os.getenv('TELEGRAM_API_HASH', '')
        
        self.thresholds = MonitoringThresholds()
        self.client = None
        self._running = False
        self._alert_counter = 0
        
        self.user_activity: Dict[int, List[ActivityRecord]] = defaultdict(list)
        self.chat_activity: Dict[int, List[ActivityRecord]] = defaultdict(list)
        self.new_users: Dict[int, List[Dict]] = defaultdict(list)
        
        self.alerts: List[MonitoringAlert] = []
        self.blocked_users: Set[int] = set()
        self.watched_chats: Set[int] = set()
        
        self.alert_callbacks: List[Callable] = []
        
        self.patterns = {
            'coordinates_decimal': r'\b(\d{2}\.\d{4,}),\s*(\d{2}\.\d{4,})\b',
            'coordinates_dms': r'\b(\d{1,3})°(\d{1,2})\'(\d{1,2})"[NSEW]\s*(\d{1,3})°(\d{1,2})\'(\d{1,2})"[NSEW]\b',
            'coordinates_mgrs': r'\b[A-R]{2}\d{2}[a-x]{2}\d{4,10}\b',
            'phone_numbers': r'[\+\(]?[1-9][0-9\-\(\)\.]{9,15}',
            'usernames': r'@[\w\d_]{5,32}',
            'urls': r'https?://[^\s<>"{}|\\^`\[\]]+',
            'crypto_btc': r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b',
            'crypto_eth': r'\b0x[a-fA-F0-9]{40}\b',
            'ip_addresses': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'frequencies': r'\b\d{2,3}[\.,]\d{1,3}\s*(MHz|МГц|mhz|мгц)\b',
        }
        
        self.threat_keywords = {
            'critical': ['детонатор', 'вибухівка', 'c4', 'тнт', 'підрив', 'замінування'],
            'high': ['координати', 'позиція', 'дрон', 'квадрокоптер', 'fpv', 'частота', 'радіо'],
            'medium': ['зброя', 'боєприпаси', 'схованка', 'закладка', 'точка', 'збір'],
            'low': ['операція', 'завдання', 'маршрут', 'час', 'місце']
        }
        
        self.auto_actions = {
            'block_user': True,
            'delete_message': False,
            'alert_admins': True,
            'log_evidence': True,
            'screenshot': False
        }
    
    async def start(self, session_name: str = 'monitor_session'):
        """Запуск моніторингу"""
        try:
            from telethon import TelegramClient, events
            from telethon.tl.types import PeerChannel, PeerChat, PeerUser
            
            self.client = TelegramClient(session_name, self.api_id, self.api_hash)
            await self.client.start()
            
            @self.client.on(events.NewMessage())
            async def handle_new_message(event):
                await self._process_message(event)
            
            @self.client.on(events.ChatAction())
            async def handle_chat_action(event):
                await self._process_chat_action(event)
            
            @self.client.on(events.MessageEdited())
            async def handle_edit(event):
                await self._process_message(event, is_edit=True)
            
            self._running = True
            logger.info("🔍 RealTimeMonitor started")
            
            asyncio.create_task(self._cleanup_old_records())
            asyncio.create_task(self._periodic_analysis())
            
            return True
            
        except ImportError:
            logger.error("Telethon not installed")
            return False
        except Exception as e:
            logger.error(f"Monitor start error: {e}")
            return False
    
    async def stop(self):
        """Зупинка моніторингу"""
        self._running = False
        if self.client:
            await self.client.disconnect()
        logger.info("🛑 RealTimeMonitor stopped")
    
    async def add_watched_chat(self, chat_id: int):
        """Додати чат до моніторингу"""
        self.watched_chats.add(chat_id)
        logger.info(f"Added chat {chat_id} to monitoring")
    
    async def remove_watched_chat(self, chat_id: int):
        """Видалити чат з моніторингу"""
        self.watched_chats.discard(chat_id)
    
    def add_alert_callback(self, callback: Callable):
        """Додати callback для алертів"""
        self.alert_callbacks.append(callback)
    
    async def _process_message(self, event, is_edit: bool = False):
        """Обробка нового повідомлення"""
        try:
            if not event.message or not event.message.text:
                return
            
            chat_id = event.chat_id
            user_id = event.sender_id
            text = event.message.text
            
            if self.watched_chats and chat_id not in self.watched_chats:
                return
            
            if user_id in self.blocked_users:
                return
            
            record = ActivityRecord(
                user_id=user_id,
                chat_id=chat_id,
                message_id=event.message.id,
                text=text,
                timestamp=datetime.now()
            )
            
            for pattern_name, pattern in self.patterns.items():
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    record.patterns_found[pattern_name] = matches
                    record.flags.append(f"PATTERN_{pattern_name.upper()}")
            
            for level, keywords in self.threat_keywords.items():
                text_lower = text.lower()
                for keyword in keywords:
                    if keyword in text_lower:
                        record.flags.append(f"KEYWORD_{level.upper()}_{keyword}")
                        
                        if level == 'critical':
                            record.threat_score += 50
                        elif level == 'high':
                            record.threat_score += 30
                        elif level == 'medium':
                            record.threat_score += 15
                        else:
                            record.threat_score += 5
            
            if record.patterns_found.get('coordinates_decimal') or \
               record.patterns_found.get('coordinates_dms') or \
               record.patterns_found.get('coordinates_mgrs'):
                record.threat_score += 40
                record.flags.append("COORDINATES_DETECTED")
            
            self.user_activity[user_id].append(record)
            self.chat_activity[chat_id].append(record)
            
            await self._check_thresholds(record)
            
            if record.threat_score >= 50:
                await self._generate_alert(record, is_edit)
                
        except Exception as e:
            logger.error(f"Message processing error: {e}")
    
    async def _process_chat_action(self, event):
        """Обробка дій в чаті (вхід/вихід користувачів)"""
        try:
            if event.user_joined or event.user_added:
                chat_id = event.chat_id
                user_id = event.user_id
                
                self.new_users[chat_id].append({
                    'user_id': user_id,
                    'timestamp': datetime.now(),
                    'action': 'joined'
                })
                
                hour_ago = datetime.now() - timedelta(hours=1)
                recent_joins = [
                    u for u in self.new_users[chat_id]
                    if u['timestamp'] > hour_ago
                ]
                
                if len(recent_joins) > self.thresholds.new_users_per_hour:
                    await self._create_alert(
                        alert_type="MASS_JOIN",
                        threat_level=ThreatLevel.HIGH,
                        chat_id=chat_id,
                        user_id=None,
                        description=f"Масовий вхід користувачів: {len(recent_joins)} за годину",
                        evidence={'recent_users': [u['user_id'] for u in recent_joins[-10:]]}
                    )
                    
        except Exception as e:
            logger.error(f"Chat action processing error: {e}")
    
    async def _check_thresholds(self, record: ActivityRecord):
        """Перевірка порогових значень"""
        user_id = record.user_id
        chat_id = record.chat_id
        now = datetime.now()
        
        minute_ago = now - timedelta(minutes=1)
        user_messages_minute = [
            r for r in self.user_activity[user_id]
            if r.timestamp > minute_ago
        ]
        
        if len(user_messages_minute) > self.thresholds.messages_per_minute:
            await self._create_alert(
                alert_type="FLOOD_DETECTED",
                threat_level=ThreatLevel.MEDIUM,
                chat_id=chat_id,
                user_id=user_id,
                description=f"Флуд: {len(user_messages_minute)} повідомлень за хвилину",
                evidence={'message_count': len(user_messages_minute)}
            )
        
        hour_ago = now - timedelta(hours=1)
        coord_messages = [
            r for r in self.chat_activity[chat_id]
            if r.timestamp > hour_ago and 'COORDINATES_DETECTED' in r.flags
        ]
        
        if len(coord_messages) >= self.thresholds.coordinate_messages:
            await self._create_alert(
                alert_type="COORDINATE_LEAK",
                threat_level=ThreatLevel.CRITICAL,
                chat_id=chat_id,
                user_id=user_id,
                description=f"Виявлено {len(coord_messages)} повідомлень з координатами",
                evidence={
                    'coordinates': [
                        r.patterns_found.get('coordinates_decimal', [])
                        for r in coord_messages
                    ]
                }
            )
        
        keyword_messages = [
            r for r in self.user_activity[user_id]
            if r.timestamp > hour_ago and any('KEYWORD_' in f for f in r.flags)
        ]
        
        if len(keyword_messages) >= self.thresholds.suspicious_keywords_per_hour:
            await self._create_alert(
                alert_type="SUSPICIOUS_ACTIVITY",
                threat_level=ThreatLevel.HIGH,
                chat_id=chat_id,
                user_id=user_id,
                description=f"Підозріла активність: {len(keyword_messages)} повідомлень з ключовими словами",
                evidence={'flags': [r.flags for r in keyword_messages[-5:]]}
            )
    
    async def _generate_alert(self, record: ActivityRecord, is_edit: bool = False):
        """Генерація алерту для критичного повідомлення"""
        
        if record.threat_score >= 80:
            threat_level = ThreatLevel.CRITICAL
        elif record.threat_score >= 50:
            threat_level = ThreatLevel.HIGH
        elif record.threat_score >= 30:
            threat_level = ThreatLevel.MEDIUM
        else:
            threat_level = ThreatLevel.LOW
        
        await self._create_alert(
            alert_type="THREAT_MESSAGE" if not is_edit else "THREAT_EDIT",
            threat_level=threat_level,
            chat_id=record.chat_id,
            user_id=record.user_id,
            description=f"Загроза (score: {record.threat_score}): {record.text[:100]}...",
            evidence={
                'message_id': record.message_id,
                'patterns': record.patterns_found,
                'flags': record.flags,
                'full_text': record.text[:500]
            }
        )
    
    async def _create_alert(
        self,
        alert_type: str,
        threat_level: ThreatLevel,
        chat_id: int,
        user_id: Optional[int],
        description: str,
        evidence: Dict[str, Any] = None
    ):
        """Створення та обробка алерту"""
        
        self._alert_counter += 1
        alert_id = f"MON-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self._alert_counter:04d}"
        
        alert = MonitoringAlert(
            id=alert_id,
            timestamp=datetime.now(),
            alert_type=alert_type,
            threat_level=threat_level,
            chat_id=chat_id,
            user_id=user_id,
            description=description,
            evidence=evidence or {}
        )
        
        self.alerts.append(alert)
        
        if self.auto_actions['log_evidence']:
            await self._log_evidence(alert)
        
        if threat_level == ThreatLevel.CRITICAL and self.auto_actions['block_user']:
            if user_id:
                self.blocked_users.add(user_id)
                alert.auto_action_taken = "USER_BLOCKED"
        
        for callback in self.alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
        
        logger.warning(f"🚨 ALERT [{threat_level.value.upper()}]: {description}")
        
        return alert
    
    async def _log_evidence(self, alert: MonitoringAlert):
        """Логування доказів"""
        from pathlib import Path
        import json
        
        evidence_dir = Path("./evidence/realtime")
        evidence_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{alert.id}.json"
        filepath = evidence_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'id': alert.id,
                'timestamp': alert.timestamp.isoformat(),
                'type': alert.alert_type,
                'level': alert.threat_level.value,
                'chat_id': alert.chat_id,
                'user_id': alert.user_id,
                'description': alert.description,
                'evidence': alert.evidence,
                'auto_action': alert.auto_action_taken
            }, f, ensure_ascii=False, indent=2)
    
    async def _cleanup_old_records(self):
        """Очищення старих записів"""
        while self._running:
            await asyncio.sleep(300)
            
            cutoff = datetime.now() - timedelta(hours=24)
            
            for user_id in list(self.user_activity.keys()):
                self.user_activity[user_id] = [
                    r for r in self.user_activity[user_id]
                    if r.timestamp > cutoff
                ]
                if not self.user_activity[user_id]:
                    del self.user_activity[user_id]
            
            for chat_id in list(self.chat_activity.keys()):
                self.chat_activity[chat_id] = [
                    r for r in self.chat_activity[chat_id]
                    if r.timestamp > cutoff
                ]
                if not self.chat_activity[chat_id]:
                    del self.chat_activity[chat_id]
            
            for chat_id in list(self.new_users.keys()):
                self.new_users[chat_id] = [
                    u for u in self.new_users[chat_id]
                    if u['timestamp'] > cutoff
                ]
    
    async def _periodic_analysis(self):
        """Періодичний аналіз активності"""
        while self._running:
            await asyncio.sleep(60)
            
            for chat_id, records in self.chat_activity.items():
                hour_ago = datetime.now() - timedelta(hours=1)
                recent = [r for r in records if r.timestamp > hour_ago]
                
                if len(recent) > self.thresholds.messages_per_hour:
                    logger.info(f"Chat {chat_id}: {len(recent)} messages/hour")
    
    def get_stats(self) -> Dict[str, Any]:
        """Отримання статистики моніторингу"""
        return {
            'running': self._running,
            'watched_chats': len(self.watched_chats),
            'tracked_users': len(self.user_activity),
            'tracked_chats': len(self.chat_activity),
            'blocked_users': len(self.blocked_users),
            'total_alerts': len(self.alerts),
            'alerts_by_level': {
                level.value: len([a for a in self.alerts if a.threat_level == level])
                for level in ThreatLevel
            }
        }
    
    def get_recent_alerts(self, limit: int = 20) -> List[Dict]:
        """Отримання останніх алертів"""
        recent = sorted(self.alerts, key=lambda x: x.timestamp, reverse=True)[:limit]
        return [
            {
                'id': a.id,
                'timestamp': a.timestamp.isoformat(),
                'type': a.alert_type,
                'level': a.threat_level.value,
                'description': a.description
            }
            for a in recent
        ]

realtime_monitor = RealTimeMonitor()
