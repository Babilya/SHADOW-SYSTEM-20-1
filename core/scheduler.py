import logging
import asyncio
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskType(str, Enum):
    ONCE = "once"
    INTERVAL = "interval"
    CRON = "cron"
    DAILY = "daily"

@dataclass
class ScheduledTask:
    id: str
    name: str
    task_type: TaskType
    callback: Callable
    status: TaskStatus = TaskStatus.PENDING
    interval_seconds: Optional[int] = None
    run_at: Optional[datetime] = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    max_runs: Optional[int] = None
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

class CampaignScheduler:
    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self._running = False
        self._main_task: Optional[asyncio.Task] = None
        self._check_interval = 5
    
    def schedule_once(
        self,
        name: str,
        callback: Callable,
        run_at: datetime,
        *args,
        **kwargs
    ) -> str:
        task_id = str(uuid.uuid4())[:8]
        
        task = ScheduledTask(
            id=task_id,
            name=name,
            task_type=TaskType.ONCE,
            callback=callback,
            run_at=run_at,
            next_run=run_at,
            max_runs=1,
            args=args,
            kwargs=kwargs
        )
        
        self.tasks[task_id] = task
        logger.info(f"Scheduled once: {name} at {run_at}")
        return task_id
    
    def schedule_interval(
        self,
        name: str,
        callback: Callable,
        interval_seconds: int,
        max_runs: Optional[int] = None,
        start_immediately: bool = False,
        *args,
        **kwargs
    ) -> str:
        task_id = str(uuid.uuid4())[:8]
        
        next_run = datetime.now()
        if not start_immediately:
            next_run += timedelta(seconds=interval_seconds)
        
        task = ScheduledTask(
            id=task_id,
            name=name,
            task_type=TaskType.INTERVAL,
            callback=callback,
            interval_seconds=interval_seconds,
            next_run=next_run,
            max_runs=max_runs,
            args=args,
            kwargs=kwargs
        )
        
        self.tasks[task_id] = task
        logger.info(f"Scheduled interval: {name} every {interval_seconds}s")
        return task_id
    
    def schedule_daily(
        self,
        name: str,
        callback: Callable,
        hour: int,
        minute: int = 0,
        *args,
        **kwargs
    ) -> str:
        task_id = str(uuid.uuid4())[:8]
        
        now = datetime.now()
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
        
        task = ScheduledTask(
            id=task_id,
            name=name,
            task_type=TaskType.DAILY,
            callback=callback,
            next_run=next_run,
            interval_seconds=86400,
            args=args,
            kwargs=kwargs
        )
        
        self.tasks[task_id] = task
        logger.info(f"Scheduled daily: {name} at {hour:02d}:{minute:02d}")
        return task_id
    
    def cancel_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if task:
            task.status = TaskStatus.CANCELLED
            logger.info(f"Task cancelled: {task.name}")
            return True
        return False
    
    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        return self.tasks.get(task_id)
    
    def get_pending_tasks(self) -> List[ScheduledTask]:
        return [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
    
    async def start_scheduler(self):
        if self._running:
            return
        
        self._running = True
        logger.info("Scheduler started")
        
        while self._running:
            try:
                await self._check_and_run_tasks()
                await asyncio.sleep(self._check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(self._check_interval)
        
        logger.info("Scheduler stopped")
    
    async def stop(self):
        self._running = False
        if self._main_task:
            self._main_task.cancel()
    
    async def _check_and_run_tasks(self):
        now = datetime.now()
        
        for task in list(self.tasks.values()):
            if task.status != TaskStatus.PENDING:
                continue
            
            if task.next_run and task.next_run <= now:
                await self._run_task(task)
    
    async def _run_task(self, task: ScheduledTask):
        try:
            task.status = TaskStatus.RUNNING
            task.last_run = datetime.now()
            
            if asyncio.iscoroutinefunction(task.callback):
                await task.callback(*task.args, **task.kwargs)
            else:
                task.callback(*task.args, **task.kwargs)
            
            task.run_count += 1
            logger.info(f"Task executed: {task.name} (run #{task.run_count})")
            
            if task.task_type == TaskType.ONCE:
                task.status = TaskStatus.COMPLETED
            elif task.max_runs and task.run_count >= task.max_runs:
                task.status = TaskStatus.COMPLETED
            else:
                task.status = TaskStatus.PENDING
                if task.interval_seconds:
                    task.next_run = datetime.now() + timedelta(seconds=task.interval_seconds)
                    
        except Exception as e:
            task.status = TaskStatus.FAILED
            logger.error(f"Task failed: {task.name} - {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        stats = {
            'total_tasks': len(self.tasks),
            'pending': 0,
            'running': 0,
            'completed': 0,
            'failed': 0,
            'cancelled': 0
        }
        
        for task in self.tasks.values():
            stats[task.status.value] += 1
        
        return stats

scheduler = CampaignScheduler()
