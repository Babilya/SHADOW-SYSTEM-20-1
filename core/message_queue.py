import asyncio
import logging
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class MailingTask:
    id: str
    project_id: str
    name: str
    message_text: str
    recipients: list
    status: TaskStatus = TaskStatus.PENDING
    sent_count: int = 0
    failed_count: int = 0
    total_count: int = 0
    current_index: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    ab_variants: Optional[list] = None
    interval_min: float = 1.0
    interval_max: float = 3.0

class MessageQueue:
    def __init__(self):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.tasks: Dict[str, MailingTask] = {}
        self.active_workers: Dict[str, asyncio.Task] = {}
        self.progress_callbacks: Dict[str, Callable] = {}
        self._running = False
        self._workers: list = []
        self.max_workers = 3
    
    async def start(self, num_workers: int = 3):
        self.max_workers = num_workers
        self._running = True
        self._workers = [
            asyncio.create_task(self._worker(i)) 
            for i in range(num_workers)
        ]
        logger.info(f"MessageQueue started with {num_workers} workers")
    
    async def stop(self):
        self._running = False
        for worker in self._workers:
            worker.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        logger.info("MessageQueue stopped")
    
    async def _worker(self, worker_id: int):
        while self._running:
            try:
                task_id = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                if task_id in self.tasks:
                    await self._process_task(task_id, worker_id)
                self.queue.task_done()
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
    
    async def _process_task(self, task_id: str, worker_id: int):
        task = self.tasks.get(task_id)
        if not task:
            return
        
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        try:
            from core.rate_limiter import rate_limiter
            import random
            
            for i, recipient in enumerate(task.recipients[task.current_index:], task.current_index):
                if task.status == TaskStatus.PAUSED:
                    task.current_index = i
                    return
                if task.status == TaskStatus.CANCELLED:
                    return
                
                await rate_limiter.wait_for_slot(recipient, f"worker_{worker_id}")
                
                text = task.message_text
                if task.ab_variants:
                    text = random.choice(task.ab_variants)
                
                success = await self._send_message(recipient, text)
                
                if success:
                    task.sent_count += 1
                else:
                    task.failed_count += 1
                
                task.current_index = i + 1
                await self._notify_progress(task_id)
                
                delay = random.uniform(task.interval_min, task.interval_max)
                await asyncio.sleep(delay)
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            logger.error(f"Task {task_id} failed: {e}")
        
        await self._notify_progress(task_id)
    
    async def _send_message(self, recipient: int, text: str) -> bool:
        try:
            return True
        except Exception as e:
            logger.error(f"Failed to send to {recipient}: {e}")
            return False
    
    async def _notify_progress(self, task_id: str):
        if task_id in self.progress_callbacks:
            task = self.tasks[task_id]
            await self.progress_callbacks[task_id]({
                "task_id": task_id,
                "status": task.status.value,
                "sent": task.sent_count,
                "failed": task.failed_count,
                "total": task.total_count,
                "progress": (task.current_index / task.total_count * 100) if task.total_count > 0 else 0
            })
    
    async def add_task(self, task: MailingTask, progress_callback: Optional[Callable] = None) -> str:
        task.total_count = len(task.recipients)
        self.tasks[task.id] = task
        if progress_callback:
            self.progress_callbacks[task.id] = progress_callback
        await self.queue.put(task.id)
        logger.info(f"Task {task.id} added to queue")
        return task.id
    
    async def create_mailing(
        self,
        project_id: str,
        name: str,
        message_text: str,
        recipients: list,
        ab_variants: Optional[list] = None,
        interval_min: float = 1.0,
        interval_max: float = 3.0,
        progress_callback: Optional[Callable] = None
    ) -> str:
        task = MailingTask(
            id=str(uuid.uuid4()),
            project_id=project_id,
            name=name,
            message_text=message_text,
            recipients=recipients,
            ab_variants=ab_variants,
            interval_min=interval_min,
            interval_max=interval_max
        )
        return await self.add_task(task, progress_callback)
    
    def pause_task(self, task_id: str) -> bool:
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.PAUSED
            return True
        return False
    
    def resume_task(self, task_id: str) -> bool:
        if task_id in self.tasks and self.tasks[task_id].status == TaskStatus.PAUSED:
            self.tasks[task_id].status = TaskStatus.PENDING
            asyncio.create_task(self.queue.put(task_id))
            return True
        return False
    
    def cancel_task(self, task_id: str) -> bool:
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.CANCELLED
            return True
        return False
    
    def get_task(self, task_id: str) -> Optional[MailingTask]:
        return self.tasks.get(task_id)
    
    def get_all_tasks(self, project_id: Optional[str] = None) -> list:
        tasks = list(self.tasks.values())
        if project_id:
            tasks = [t for t in tasks if t.project_id == project_id]
        return tasks
    
    def get_progress(self, task_id: str) -> Optional[dict]:
        task = self.tasks.get(task_id)
        if not task:
            return None
        return {
            "task_id": task_id,
            "name": task.name,
            "status": task.status.value,
            "sent": task.sent_count,
            "failed": task.failed_count,
            "total": task.total_count,
            "progress": (task.current_index / task.total_count * 100) if task.total_count > 0 else 0,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        }

message_queue = MessageQueue()
