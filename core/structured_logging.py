"""
Structured Logging for SHADOW SYSTEM
Provides enhanced logging with context, metrics, and alerting
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(Enum):
    SECURITY = "security"
    CAMPAIGN = "campaign"
    OSINT = "osint"
    BOT = "bot"
    DM = "dm"
    PARSER = "parser"
    FLOOD = "flood"
    SYSTEM = "system"
    AUTH = "auth"
    API = "api"


@dataclass
class StructuredLog:
    """Structured log entry with metadata"""
    timestamp: str
    level: str
    category: str
    message: str
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    task_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, default=str)


class StructuredLogger:
    """Enhanced logger with structured output and metrics"""
    
    def __init__(self):
        self.logs: list = []
        self.metrics: Dict[str, int] = {
            "total_logs": 0,
            "errors": 0,
            "warnings": 0,
            "flood_events": 0,
            "security_events": 0
        }
        self.max_logs = 10000
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging format and attach handler"""
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        
        if not logger.handlers:
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)
    
    def _create_log(
        self,
        level: LogLevel,
        category: LogCategory,
        message: str,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        task_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None
    ) -> StructuredLog:
        """Create structured log entry"""
        return StructuredLog(
            timestamp=datetime.now().isoformat(),
            level=level.value,
            category=category.value,
            message=message,
            user_id=user_id,
            session_id=session_id,
            task_id=task_id,
            details=details,
            duration_ms=duration_ms
        )
    
    def _store_log(self, log: StructuredLog):
        """Store log and update metrics"""
        self.logs.append(log)
        self.metrics["total_logs"] += 1
        
        if log.level == LogLevel.ERROR.value:
            self.metrics["errors"] += 1
        elif log.level == LogLevel.WARNING.value:
            self.metrics["warnings"] += 1
        
        if log.category == LogCategory.FLOOD.value:
            self.metrics["flood_events"] += 1
        elif log.category == LogCategory.SECURITY.value:
            self.metrics["security_events"] += 1
        
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]
    
    def debug(self, category: LogCategory, message: str, **kwargs):
        """Log debug message"""
        log = self._create_log(LogLevel.DEBUG, category, message, **kwargs)
        self._store_log(log)
        logger.debug(message, extra={"category": category.value})
    
    def info(self, category: LogCategory, message: str, **kwargs):
        """Log info message"""
        log = self._create_log(LogLevel.INFO, category, message, **kwargs)
        self._store_log(log)
        logger.info(message, extra={"category": category.value})
    
    def warning(self, category: LogCategory, message: str, **kwargs):
        """Log warning message"""
        log = self._create_log(LogLevel.WARNING, category, message, **kwargs)
        self._store_log(log)
        logger.warning(message, extra={"category": category.value})
    
    def error(self, category: LogCategory, message: str, **kwargs):
        """Log error message"""
        log = self._create_log(LogLevel.ERROR, category, message, **kwargs)
        self._store_log(log)
        logger.error(message, extra={"category": category.value})
    
    def critical(self, category: LogCategory, message: str, **kwargs):
        """Log critical message"""
        log = self._create_log(LogLevel.CRITICAL, category, message, **kwargs)
        self._store_log(log)
        logger.critical(message, extra={"category": category.value})
    
    def log_flood_event(
        self,
        session_id: str,
        wait_seconds: int,
        task_id: Optional[str] = None,
        user_id: Optional[int] = None
    ):
        """Log flood wait event"""
        self.warning(
            LogCategory.FLOOD,
            f"FloodWait: {wait_seconds}s for session {session_id}",
            session_id=session_id,
            task_id=task_id,
            user_id=user_id,
            details={"wait_seconds": wait_seconds}
        )
    
    def log_dm_sent(
        self,
        task_id: str,
        target_user_id: int,
        session_id: str,
        duration_ms: float
    ):
        """Log DM sent event"""
        self.info(
            LogCategory.DM,
            f"DM sent to {target_user_id}",
            task_id=task_id,
            session_id=session_id,
            duration_ms=duration_ms,
            details={"target_user_id": target_user_id}
        )
    
    def log_dm_failed(
        self,
        task_id: str,
        target_user_id: int,
        error: str,
        session_id: Optional[str] = None
    ):
        """Log DM failure"""
        self.error(
            LogCategory.DM,
            f"DM failed to {target_user_id}: {error}",
            task_id=task_id,
            session_id=session_id,
            details={"target_user_id": target_user_id, "error": error}
        )
    
    def log_parser_complete(
        self,
        group_id: int,
        users_count: int,
        duration_ms: float,
        user_id: Optional[int] = None
    ):
        """Log parser completion"""
        self.info(
            LogCategory.PARSER,
            f"Parsed {users_count} users from group {group_id}",
            user_id=user_id,
            duration_ms=duration_ms,
            details={"group_id": group_id, "users_count": users_count}
        )
    
    def log_security_event(
        self,
        event_type: str,
        user_id: int,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log security event"""
        self.warning(
            LogCategory.SECURITY,
            f"Security event: {event_type} for user {user_id}",
            user_id=user_id,
            details={"event_type": event_type, **(details or {})}
        )
    
    def get_recent_logs(
        self,
        category: Optional[LogCategory] = None,
        level: Optional[LogLevel] = None,
        limit: int = 100
    ) -> list:
        """Get recent logs with optional filtering"""
        filtered = self.logs
        
        if category:
            filtered = [l for l in filtered if l.category == category.value]
        
        if level:
            filtered = [l for l in filtered if l.level == level.value]
        
        return filtered[-limit:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get logging metrics"""
        return {
            **self.metrics,
            "logs_stored": len(self.logs)
        }
    
    def export_logs_json(self, limit: int = 1000) -> str:
        """Export recent logs as JSON"""
        logs = self.get_recent_logs(limit=limit)
        return json.dumps([l.to_dict() for l in logs], ensure_ascii=False, indent=2)


structured_logger = StructuredLogger()
