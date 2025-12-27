import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)

class RuleType(str, Enum):
    MESSAGE_FREQUENCY = "message_frequency"
    KEYWORD_DETECTION = "keyword_detection"
    PATTERN_MATCH = "pattern_match"
    USER_JOIN_RATE = "user_join_rate"
    LINK_SPAM = "link_spam"
    MEDIA_SPAM = "media_spam"
    COORDINATE_LEAK = "coordinate_leak"
    CRYPTO_ACTIVITY = "crypto_activity"
    CUSTOM = "custom"

class ActionType(str, Enum):
    LOG = "log"
    ALERT = "alert"
    BLOCK_USER = "block_user"
    DELETE_MESSAGE = "delete_message"
    NOTIFY_ADMIN = "notify_admin"
    QUARANTINE = "quarantine"
    ESCALATE = "escalate"

@dataclass
class ThresholdRule:
    """Правило порогового значення"""
    id: str
    name: str
    rule_type: RuleType
    threshold_value: int
    time_window_minutes: int = 60
    actions: List[ActionType] = field(default_factory=list)
    enabled: bool = True
    priority: int = 5
    cooldown_minutes: int = 5
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0

@dataclass
class ThresholdViolation:
    """Порушення порогу"""
    id: str
    rule_id: str
    rule_name: str
    timestamp: datetime
    chat_id: Optional[int]
    user_id: Optional[int]
    current_value: int
    threshold_value: int
    actions_taken: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)

class AlertThresholdsSystem:
    """Система динамічних порогових правил"""
    
    def __init__(self):
        self.rules: Dict[str, ThresholdRule] = {}
        self.violations: List[ThresholdViolation] = []
        self.violation_counter = 0
        
        self.metrics: Dict[str, Dict] = defaultdict(lambda: defaultdict(list))
        
        self.action_handlers: Dict[ActionType, Callable] = {}
        
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Ініціалізація стандартних правил"""
        
        default_rules = [
            ThresholdRule(
                id="msg_flood",
                name="Флуд повідомленнями",
                rule_type=RuleType.MESSAGE_FREQUENCY,
                threshold_value=15,
                time_window_minutes=1,
                actions=[ActionType.ALERT, ActionType.LOG],
                priority=7
            ),
            ThresholdRule(
                id="msg_hour",
                name="Надмірна активність за годину",
                rule_type=RuleType.MESSAGE_FREQUENCY,
                threshold_value=200,
                time_window_minutes=60,
                actions=[ActionType.ALERT, ActionType.NOTIFY_ADMIN],
                priority=5
            ),
            ThresholdRule(
                id="coord_leak",
                name="Витік координат",
                rule_type=RuleType.COORDINATE_LEAK,
                threshold_value=2,
                time_window_minutes=60,
                actions=[ActionType.ALERT, ActionType.NOTIFY_ADMIN, ActionType.ESCALATE],
                priority=10
            ),
            ThresholdRule(
                id="user_flood",
                name="Масовий вхід користувачів",
                rule_type=RuleType.USER_JOIN_RATE,
                threshold_value=30,
                time_window_minutes=60,
                actions=[ActionType.ALERT, ActionType.QUARANTINE],
                priority=8
            ),
            ThresholdRule(
                id="link_spam",
                name="Спам посиланнями",
                rule_type=RuleType.LINK_SPAM,
                threshold_value=10,
                time_window_minutes=5,
                actions=[ActionType.ALERT, ActionType.BLOCK_USER],
                priority=6
            ),
            ThresholdRule(
                id="keyword_critical",
                name="Критичні ключові слова",
                rule_type=RuleType.KEYWORD_DETECTION,
                threshold_value=1,
                time_window_minutes=1,
                actions=[ActionType.ALERT, ActionType.NOTIFY_ADMIN, ActionType.ESCALATE],
                priority=10,
                metadata={'keywords': ['детонатор', 'вибухівка', 'координати']}
            ),
            ThresholdRule(
                id="crypto_activity",
                name="Криптовалютна активність",
                rule_type=RuleType.CRYPTO_ACTIVITY,
                threshold_value=3,
                time_window_minutes=60,
                actions=[ActionType.ALERT, ActionType.LOG],
                priority=5
            ),
        ]
        
        for rule in default_rules:
            self.rules[rule.id] = rule
    
    def add_rule(self, rule: ThresholdRule):
        """Додати нове правило"""
        self.rules[rule.id] = rule
        logger.info(f"Added rule: {rule.id} - {rule.name}")
    
    def remove_rule(self, rule_id: str):
        """Видалити правило"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Removed rule: {rule_id}")
    
    def update_rule(self, rule_id: str, **kwargs):
        """Оновити правило"""
        if rule_id in self.rules:
            rule = self.rules[rule_id]
            for key, value in kwargs.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            logger.info(f"Updated rule: {rule_id}")
    
    def enable_rule(self, rule_id: str):
        """Увімкнути правило"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
    
    def disable_rule(self, rule_id: str):
        """Вимкнути правило"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
    
    def register_action_handler(self, action_type: ActionType, handler: Callable):
        """Реєстрація обробника дій"""
        self.action_handlers[action_type] = handler
    
    async def record_metric(
        self,
        metric_type: str,
        entity_id: str,
        value: Any = 1,
        metadata: Dict = None
    ):
        """Запис метрики"""
        
        record = {
            'timestamp': datetime.now(),
            'value': value,
            'metadata': metadata or {}
        }
        
        self.metrics[metric_type][entity_id].append(record)
        
        await self._check_thresholds(metric_type, entity_id)
    
    async def _check_thresholds(self, metric_type: str, entity_id: str):
        """Перевірка порогів для метрики"""
        
        now = datetime.now()
        
        for rule_id, rule in self.rules.items():
            if not rule.enabled:
                continue
            
            if not self._rule_matches_metric(rule, metric_type):
                continue
            
            if rule.last_triggered:
                cooldown_end = rule.last_triggered + timedelta(minutes=rule.cooldown_minutes)
                if now < cooldown_end:
                    continue
            
            window_start = now - timedelta(minutes=rule.time_window_minutes)
            
            records = self.metrics[metric_type][entity_id]
            recent_records = [r for r in records if r['timestamp'] > window_start]
            
            current_value = len(recent_records)
            
            if current_value >= rule.threshold_value:
                await self._trigger_violation(rule, entity_id, current_value, recent_records)
    
    def _rule_matches_metric(self, rule: ThresholdRule, metric_type: str) -> bool:
        """Перевірка відповідності правила метриці"""
        
        mapping = {
            RuleType.MESSAGE_FREQUENCY: 'messages',
            RuleType.KEYWORD_DETECTION: 'keywords',
            RuleType.PATTERN_MATCH: 'patterns',
            RuleType.USER_JOIN_RATE: 'user_joins',
            RuleType.LINK_SPAM: 'links',
            RuleType.MEDIA_SPAM: 'media',
            RuleType.COORDINATE_LEAK: 'coordinates',
            RuleType.CRYPTO_ACTIVITY: 'crypto',
        }
        
        expected_metric = mapping.get(rule.rule_type)
        return metric_type == expected_metric or rule.rule_type == RuleType.CUSTOM
    
    async def _trigger_violation(
        self,
        rule: ThresholdRule,
        entity_id: str,
        current_value: int,
        records: List[Dict]
    ):
        """Обробка порушення порогу"""
        
        self.violation_counter += 1
        violation_id = f"VIO-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self.violation_counter:04d}"
        
        chat_id = None
        user_id = None
        
        if entity_id.startswith('chat_'):
            chat_id = int(entity_id.replace('chat_', ''))
        elif entity_id.startswith('user_'):
            user_id = int(entity_id.replace('user_', ''))
        
        violation = ThresholdViolation(
            id=violation_id,
            rule_id=rule.id,
            rule_name=rule.name,
            timestamp=datetime.now(),
            chat_id=chat_id,
            user_id=user_id,
            current_value=current_value,
            threshold_value=rule.threshold_value,
            evidence={
                'records_count': len(records),
                'sample_records': [
                    {'timestamp': r['timestamp'].isoformat(), 'value': r['value']}
                    for r in records[-5:]
                ]
            }
        )
        
        for action in rule.actions:
            action_result = await self._execute_action(action, violation, rule)
            violation.actions_taken.append(f"{action.value}: {action_result}")
        
        self.violations.append(violation)
        
        rule.last_triggered = datetime.now()
        rule.trigger_count += 1
        
        logger.warning(f"🚨 Violation {violation_id}: {rule.name} - {current_value}/{rule.threshold_value}")
        
        return violation
    
    async def _execute_action(
        self,
        action: ActionType,
        violation: ThresholdViolation,
        rule: ThresholdRule
    ) -> str:
        """Виконання дії"""
        
        if action in self.action_handlers:
            try:
                result = await self.action_handlers[action](violation, rule)
                return str(result)
            except Exception as e:
                logger.error(f"Action handler error for {action}: {e}")
                return f"error: {e}"
        
        if action == ActionType.LOG:
            logger.info(f"[LOG] {violation.rule_name}: {violation.current_value}")
            return "logged"
        
        elif action == ActionType.ALERT:
            logger.warning(f"[ALERT] {violation.rule_name}: {violation.current_value}/{violation.threshold_value}")
            return "alerted"
        
        elif action == ActionType.NOTIFY_ADMIN:
            logger.info(f"[NOTIFY] Would notify admins about: {violation.rule_name}")
            return "notification_queued"
        
        elif action == ActionType.ESCALATE:
            logger.critical(f"[ESCALATE] Critical violation: {violation.rule_name}")
            return "escalated"
        
        return "no_handler"
    
    def get_active_rules(self) -> List[Dict]:
        """Отримання активних правил"""
        return [
            {
                'id': r.id,
                'name': r.name,
                'type': r.rule_type.value,
                'threshold': r.threshold_value,
                'window_minutes': r.time_window_minutes,
                'actions': [a.value for a in r.actions],
                'enabled': r.enabled,
                'priority': r.priority,
                'trigger_count': r.trigger_count
            }
            for r in sorted(self.rules.values(), key=lambda x: x.priority, reverse=True)
        ]
    
    def get_recent_violations(self, limit: int = 50) -> List[Dict]:
        """Отримання останніх порушень"""
        recent = sorted(self.violations, key=lambda x: x.timestamp, reverse=True)[:limit]
        return [
            {
                'id': v.id,
                'rule': v.rule_name,
                'timestamp': v.timestamp.isoformat(),
                'chat_id': v.chat_id,
                'user_id': v.user_id,
                'value': v.current_value,
                'threshold': v.threshold_value,
                'actions': v.actions_taken
            }
            for v in recent
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Статистика системи"""
        return {
            'total_rules': len(self.rules),
            'enabled_rules': len([r for r in self.rules.values() if r.enabled]),
            'total_violations': len(self.violations),
            'violations_by_rule': {
                rule_id: len([v for v in self.violations if v.rule_id == rule_id])
                for rule_id in self.rules.keys()
            },
            'violations_last_hour': len([
                v for v in self.violations
                if v.timestamp > datetime.now() - timedelta(hours=1)
            ])
        }
    
    async def cleanup_old_metrics(self, hours: int = 24):
        """Очищення старих метрик"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        for metric_type in self.metrics:
            for entity_id in self.metrics[metric_type]:
                self.metrics[metric_type][entity_id] = [
                    r for r in self.metrics[metric_type][entity_id]
                    if r['timestamp'] > cutoff
                ]
        
        logger.info(f"Cleaned up metrics older than {hours} hours")

alert_thresholds = AlertThresholdsSystem()
