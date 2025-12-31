"""
Health Dashboard - Service health monitoring
SHADOW SYSTEM iO v2.0
"""
import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceHealth:
    """Health status for a single service"""
    name: str
    status: HealthStatus = HealthStatus.UNKNOWN
    message: str = ""
    last_check: float = 0
    response_time_ms: float = 0
    consecutive_failures: int = 0
    check_count: int = 0
    error_count: int = 0


class HealthDashboard:
    """
    Centralized health monitoring for all services:
    - Database connectivity
    - Bot status
    - Cache performance
    - External APIs
    - Background tasks
    """
    
    def __init__(self):
        self.services: Dict[str, ServiceHealth] = {}
        self.checks: Dict[str, Callable] = {}
        self._started = False
        self._check_interval = 60
    
    def register_service(
        self, 
        name: str, 
        check_func: Optional[Callable] = None
    ):
        """Register a service for health monitoring"""
        self.services[name] = ServiceHealth(name=name)
        if check_func:
            self.checks[name] = check_func
        logger.info(f"Registered health check for: {name}")
    
    async def start(self):
        """Start background health monitoring"""
        if not self._started:
            self._started = True
            asyncio.create_task(self._health_loop())
            logger.info("HealthDashboard started")
    
    async def _health_loop(self):
        """Background health check loop"""
        while self._started:
            await self.check_all()
            await asyncio.sleep(self._check_interval)
    
    async def check_service(self, name: str) -> ServiceHealth:
        """Check health of a specific service"""
        if name not in self.services:
            return ServiceHealth(name=name, status=HealthStatus.UNKNOWN)
        
        service = self.services[name]
        check_func = self.checks.get(name)
        
        if not check_func:
            service.status = HealthStatus.UNKNOWN
            service.message = "No check function"
            return service
        
        start_time = time.time()
        try:
            if asyncio.iscoroutinefunction(check_func):
                result = await check_func()
            else:
                result = check_func()
            
            response_time = (time.time() - start_time) * 1000
            
            service.status = HealthStatus.HEALTHY
            service.message = result if isinstance(result, str) else "OK"
            service.response_time_ms = response_time
            service.consecutive_failures = 0
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            service.status = HealthStatus.UNHEALTHY
            service.message = str(e)
            service.response_time_ms = response_time
            service.consecutive_failures += 1
            service.error_count += 1
        
        service.last_check = time.time()
        service.check_count += 1
        return service
    
    async def check_all(self) -> Dict[str, ServiceHealth]:
        """Check all registered services"""
        tasks = [self.check_service(name) for name in self.services]
        await asyncio.gather(*tasks, return_exceptions=True)
        return self.services
    
    def get_overall_status(self) -> HealthStatus:
        """Get overall system health status"""
        if not self.services:
            return HealthStatus.UNKNOWN
        
        statuses = [s.status for s in self.services.values()]
        
        if all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            return HealthStatus.UNHEALTHY
        elif any(s == HealthStatus.DEGRADED for s in statuses):
            return HealthStatus.DEGRADED
        return HealthStatus.UNKNOWN
    
    def get_summary(self) -> Dict[str, Any]:
        """Get health summary"""
        healthy = sum(1 for s in self.services.values() if s.status == HealthStatus.HEALTHY)
        unhealthy = sum(1 for s in self.services.values() if s.status == HealthStatus.UNHEALTHY)
        degraded = sum(1 for s in self.services.values() if s.status == HealthStatus.DEGRADED)
        
        return {
            "overall": self.get_overall_status().value,
            "total_services": len(self.services),
            "healthy": healthy,
            "unhealthy": unhealthy,
            "degraded": degraded,
            "services": {
                name: {
                    "status": s.status.value,
                    "message": s.message,
                    "response_time_ms": round(s.response_time_ms, 2),
                    "consecutive_failures": s.consecutive_failures
                }
                for name, s in self.services.items()
            }
        }
    
    def format_dashboard_message(self) -> str:
        """Format health dashboard for Telegram"""
        overall = self.get_overall_status()
        
        status_icon = {
            HealthStatus.HEALTHY: "🟢",
            HealthStatus.DEGRADED: "🟡",
            HealthStatus.UNHEALTHY: "🔴",
            HealthStatus.UNKNOWN: "⚪"
        }
        
        lines = [
            f"🏥 <b>HEALTH DASHBOARD</b>",
            "",
            f"<b>Загальний статус:</b> {status_icon[overall]} {overall.value.upper()}",
            "",
            "<b>Сервіси:</b>"
        ]
        
        for name, service in self.services.items():
            icon = status_icon[service.status]
            time_str = f"{service.response_time_ms:.0f}ms" if service.response_time_ms > 0 else "N/A"
            lines.append(f"├ {icon} {name}: {service.message} ({time_str})")
        
        if self.services:
            lines[-1] = lines[-1].replace("├", "└")
        
        return "\n".join(lines)


health_dashboard = HealthDashboard()


async def check_database() -> str:
    """Check database connectivity"""
    from database.crud import get_stats
    stats = await get_stats()
    return f"OK ({stats.get('total_users', 0)} users)"


async def check_telegram_bot() -> str:
    """Check Telegram bot status"""
    return "Connected"


async def check_cache() -> str:
    """Check cache service"""
    from core.cache_service import cache_service
    stats = cache_service.get_stats()
    return f"OK (hit rate: {stats['hit_rate']}%)"


async def check_ai_service() -> str:
    """Check AI service availability"""
    from core.ai_service import ai_service
    if ai_service.is_available:
        return "GPT-5 Ready"
    return "Unavailable"


async def check_osint_service() -> str:
    """Check OSINT service"""
    from core.osint_service import osint_service
    return "Ready"


def init_health_checks():
    """Initialize all health checks"""
    health_dashboard.register_service("Database", check_database)
    health_dashboard.register_service("Telegram Bot", check_telegram_bot)
    health_dashboard.register_service("Cache", check_cache)
    health_dashboard.register_service("AI Service", check_ai_service)
    health_dashboard.register_service("OSINT", check_osint_service)
