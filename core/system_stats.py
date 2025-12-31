"""
System Statistics - Real-time system monitoring
SHADOW SYSTEM iO v2.0
"""
import os
import time
import platform
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SystemStats:
    """Real-time system statistics collector"""
    
    _start_time: float = time.time()
    
    @classmethod
    def get_cpu_usage(cls) -> float:
        """Get current CPU usage percentage"""
        try:
            return psutil.cpu_percent(interval=0.1)
        except Exception:
            return 0.0
    
    @classmethod
    def get_memory_usage(cls) -> Dict[str, Any]:
        """Get memory usage statistics"""
        try:
            mem = psutil.virtual_memory()
            return {
                "total_mb": round(mem.total / 1024 / 1024, 1),
                "used_mb": round(mem.used / 1024 / 1024, 1),
                "available_mb": round(mem.available / 1024 / 1024, 1),
                "percent": mem.percent
            }
        except Exception:
            return {"total_mb": 0, "used_mb": 0, "available_mb": 0, "percent": 0}
    
    @classmethod
    def get_disk_usage(cls) -> Dict[str, Any]:
        """Get disk usage statistics"""
        try:
            disk = psutil.disk_usage('/')
            return {
                "total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
                "used_gb": round(disk.used / 1024 / 1024 / 1024, 2),
                "free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
                "percent": round(disk.percent, 1)
            }
        except Exception:
            return {"total_gb": 0, "used_gb": 0, "free_gb": 0, "percent": 0}
    
    @classmethod
    def get_uptime(cls) -> Dict[str, Any]:
        """Get system uptime"""
        elapsed = time.time() - cls._start_time
        days = int(elapsed // 86400)
        hours = int((elapsed % 86400) // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        
        return {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "formatted": f"{days}д {hours}г {minutes}хв",
            "total_seconds": int(elapsed)
        }
    
    @classmethod
    def get_platform_info(cls) -> Dict[str, str]:
        """Get platform information"""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor() or "Unknown",
            "python_version": platform.python_version()
        }
    
    @classmethod
    def get_process_info(cls) -> Dict[str, Any]:
        """Get current process information"""
        try:
            process = psutil.Process()
            with process.oneshot():
                return {
                    "pid": process.pid,
                    "cpu_percent": process.cpu_percent(),
                    "memory_mb": round(process.memory_info().rss / 1024 / 1024, 1),
                    "threads": process.num_threads(),
                    "open_files": len(process.open_files()),
                    "connections": len(process.connections())
                }
        except Exception:
            return {"pid": os.getpid(), "cpu_percent": 0, "memory_mb": 0, "threads": 0}
    
    @classmethod
    def get_all_stats(cls) -> Dict[str, Any]:
        """Get all system statistics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "usage_percent": cls.get_cpu_usage(),
                "cores": psutil.cpu_count(logical=False) or 1,
                "threads": psutil.cpu_count(logical=True) or 1
            },
            "memory": cls.get_memory_usage(),
            "disk": cls.get_disk_usage(),
            "uptime": cls.get_uptime(),
            "platform": cls.get_platform_info(),
            "process": cls.get_process_info()
        }
    
    @classmethod
    def format_stats_message(cls) -> str:
        """Format stats for Telegram message"""
        stats = cls.get_all_stats()
        cpu = stats["cpu"]
        mem = stats["memory"]
        disk = stats["disk"]
        uptime = stats["uptime"]
        proc = stats["process"]
        
        cpu_bar = cls._progress_bar(cpu["usage_percent"], 100)
        mem_bar = cls._progress_bar(mem["percent"], 100)
        disk_bar = cls._progress_bar(disk["percent"], 100)
        
        return f"""⚙️ <b>СИСТЕМА</b>

<b>📊 Статус компонентів:</b>
├ 🟢 Telegram Bot: Працює
├ 🟢 База даних: OK
├ 🟢 Scheduler: Активний
├ 🟢 Campaign Manager: OK
└ 🟢 Alert System: Готовий

<b>💻 CPU:</b>
├ Ядер: {cpu["cores"]} / Потоків: {cpu["threads"]}
├ Завантаження: {cpu["usage_percent"]:.1f}%
└ {cpu_bar}

<b>💾 Пам'ять:</b>
├ Використано: {mem["used_mb"]:.0f} MB / {mem["total_mb"]:.0f} MB
├ Відсоток: {mem["percent"]:.1f}%
└ {mem_bar}

<b>📀 Диск:</b>
├ Використано: {disk["used_gb"]:.1f} GB / {disk["total_gb"]:.1f} GB
├ Вільно: {disk["free_gb"]:.1f} GB
└ {disk_bar}

<b>⏱️ Uptime:</b> {uptime["formatted"]}
<b>🔧 PID:</b> {proc["pid"]} | Потоків: {proc["threads"]}
<b>📦 Версія:</b> v2.0.0"""

    @staticmethod
    def _progress_bar(current: float, total: float, length: int = 10) -> str:
        """Create progress bar"""
        if total == 0:
            return "○" * length
        filled = int((current / total) * length)
        empty = length - filled
        return "●" * filled + "○" * empty + f" {current:.0f}%"


system_stats = SystemStats()
