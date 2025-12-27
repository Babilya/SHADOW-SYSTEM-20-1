import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import os

logger = logging.getLogger(__name__)

class ActionCategory(str, Enum):
    AUTH = "auth"
    CAMPAIGN = "campaign"
    OSINT = "osint"
    BOTNET = "botnet"
    TEAM = "team"
    PAYMENT = "payment"
    SYSTEM = "system"
    SECURITY = "security"

class ActionSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class AuditEntry:
    id: str
    timestamp: datetime
    user_id: int
    username: Optional[str]
    role: str
    action: str
    category: ActionCategory
    severity: ActionSeverity
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'username': self.username,
            'role': self.role,
            'action': self.action,
            'category': self.category.value,
            'severity': self.severity.value,
            'details': self.details,
            'ip_address': self.ip_address,
            'success': self.success,
            'error_message': self.error_message
        }

class AuditLogger:
    def __init__(self, log_file: str = "audit.log", max_entries: int = 10000):
        self.log_file = log_file
        self.max_entries = max_entries
        self.entries: List[AuditEntry] = []
        self._counter = 0
    
    def _generate_id(self) -> str:
        self._counter += 1
        return f"AUD-{datetime.now().strftime('%Y%m%d')}-{self._counter:06d}"
    
    async def log(
        self,
        user_id: int,
        action: str,
        category: ActionCategory,
        severity: ActionSeverity = ActionSeverity.INFO,
        username: Optional[str] = None,
        role: str = "guest",
        details: Dict[str, Any] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> AuditEntry:
        entry = AuditEntry(
            id=self._generate_id(),
            timestamp=datetime.now(),
            user_id=user_id,
            username=username,
            role=role,
            action=action,
            category=category,
            severity=severity,
            details=details or {},
            success=success,
            error_message=error_message
        )
        
        self.entries.append(entry)
        
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
        
        log_msg = f"[{entry.severity.value.upper()}] {entry.action} | User: {user_id} | Role: {role}"
        if severity == ActionSeverity.CRITICAL:
            logger.critical(log_msg)
        elif severity == ActionSeverity.WARNING:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)
        
        await self._write_to_file(entry)
        
        return entry
    
    async def _write_to_file(self, entry: AuditEntry):
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
        
        await self._save_to_db(entry)
    
    async def _save_to_db(self, entry: AuditEntry):
        try:
            from database.db import engine
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(
                    text("""
                        INSERT INTO audit_logs 
                        (user_id, action, category, severity, details, ip_address, action_type, actor_id, payload, created_at)
                        VALUES (:user_id, :action, :category, :severity, :details, :ip_address, :action_type, :actor_id, :payload, :created_at)
                    """),
                    {
                        "user_id": str(entry.user_id),
                        "action": entry.action,
                        "category": entry.category.value,
                        "severity": entry.severity.value,
                        "details": json.dumps(entry.details, ensure_ascii=False) if entry.details else None,
                        "ip_address": entry.ip_address,
                        "action_type": entry.action,
                        "actor_id": entry.user_id,
                        "payload": json.dumps(entry.to_dict(), ensure_ascii=False),
                        "created_at": entry.timestamp
                    }
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save audit log to DB: {e}")
    
    async def log_auth(self, user_id: int, action: str, success: bool = True, **kwargs):
        return await self.log(
            user_id=user_id,
            action=action,
            category=ActionCategory.AUTH,
            severity=ActionSeverity.WARNING if not success else ActionSeverity.INFO,
            success=success,
            **kwargs
        )
    
    async def log_campaign(self, user_id: int, action: str, campaign_id: str = None, **kwargs):
        details = kwargs.pop('details', {})
        if campaign_id:
            details['campaign_id'] = campaign_id
        return await self.log(
            user_id=user_id,
            action=action,
            category=ActionCategory.CAMPAIGN,
            details=details,
            **kwargs
        )
    
    async def log_osint(self, user_id: int, action: str, target: str = None, **kwargs):
        details = kwargs.pop('details', {})
        if target:
            details['target'] = target
        return await self.log(
            user_id=user_id,
            action=action,
            category=ActionCategory.OSINT,
            details=details,
            **kwargs
        )
    
    async def log_security(self, user_id: int, action: str, severity: ActionSeverity = ActionSeverity.CRITICAL, **kwargs):
        return await self.log(
            user_id=user_id,
            action=action,
            category=ActionCategory.SECURITY,
            severity=severity,
            **kwargs
        )
    
    async def log_payment(self, user_id: int, action: str, amount: float = None, **kwargs):
        details = kwargs.pop('details', {})
        if amount:
            details['amount'] = amount
        return await self.log(
            user_id=user_id,
            action=action,
            category=ActionCategory.PAYMENT,
            details=details,
            **kwargs
        )
    
    def get_user_logs(self, user_id: int, limit: int = 100) -> List[AuditEntry]:
        user_entries = [e for e in self.entries if e.user_id == user_id]
        return user_entries[-limit:]
    
    def get_logs_by_category(self, category: ActionCategory, limit: int = 100) -> List[AuditEntry]:
        cat_entries = [e for e in self.entries if e.category == category]
        return cat_entries[-limit:]
    
    def get_critical_logs(self, limit: int = 50) -> List[AuditEntry]:
        critical = [e for e in self.entries if e.severity == ActionSeverity.CRITICAL]
        return critical[-limit:]
    
    def get_recent_logs(self, limit: int = 100) -> List[AuditEntry]:
        return self.entries[-limit:]
    
    def search_logs(self, action_contains: str = None, user_id: int = None, 
                   category: ActionCategory = None, since: datetime = None) -> List[AuditEntry]:
        results = self.entries
        
        if action_contains:
            results = [e for e in results if action_contains.lower() in e.action.lower()]
        if user_id:
            results = [e for e in results if e.user_id == user_id]
        if category:
            results = [e for e in results if e.category == category]
        if since:
            results = [e for e in results if e.timestamp >= since]
        
        return results
    
    def generate_report(self, user_id: int = None, days: int = 7) -> Dict[str, Any]:
        from datetime import timedelta
        since = datetime.now() - timedelta(days=days)
        
        logs = self.search_logs(user_id=user_id, since=since)
        
        report = {
            'period_days': days,
            'total_actions': len(logs),
            'by_category': {},
            'by_severity': {},
            'success_rate': 0,
            'critical_events': 0
        }
        
        for entry in logs:
            cat = entry.category.value
            sev = entry.severity.value
            report['by_category'][cat] = report['by_category'].get(cat, 0) + 1
            report['by_severity'][sev] = report['by_severity'].get(sev, 0) + 1
            if entry.severity == ActionSeverity.CRITICAL:
                report['critical_events'] += 1
        
        success_count = sum(1 for e in logs if e.success)
        if logs:
            report['success_rate'] = round(success_count / len(logs) * 100, 1)
        
        return report

audit_logger = AuditLogger()
