"""
Drip Campaign Manager - Каскадні кампанії з тригерами
Послідовні повідомлення з умовами та затримками
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class TriggerType(Enum):
    TIME = "time"
    MESSAGE_OPENED = "message_opened"
    LINK_CLICKED = "link_clicked"
    REPLY_RECEIVED = "reply_received"
    NO_RESPONSE = "no_response"
    POSITIVE_RESPONSE = "positive_response"
    NEGATIVE_RESPONSE = "negative_response"
    KEYWORD = "keyword"


class StepStatus(Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    SENT = "sent"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass
class DripStep:
    step_id: int
    message_text: str
    delay_hours: float = 0
    trigger: TriggerType = TriggerType.TIME
    conditions: List[str] = field(default_factory=list)
    media_url: Optional[str] = None
    buttons: List[Dict] = field(default_factory=list)


@dataclass
class UserProgress:
    user_id: int
    campaign_id: str
    current_step: int = 0
    status: str = "active"
    started_at: datetime = field(default_factory=datetime.now)
    last_action_at: Optional[datetime] = None
    responses: List[Dict] = field(default_factory=list)


class DripCampaignManager:
    """Управління каскадними кампаніями"""
    
    def __init__(self):
        self.campaigns: Dict[str, List[DripStep]] = {}
        self.user_progress: Dict[str, Dict[int, UserProgress]] = {}
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self._trigger_handlers: Dict[TriggerType, Callable] = {}
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Налаштування обробників за замовчуванням"""
        self._trigger_handlers = {
            TriggerType.TIME: self._handle_time_trigger,
            TriggerType.NO_RESPONSE: self._handle_no_response,
            TriggerType.REPLY_RECEIVED: self._handle_reply,
            TriggerType.KEYWORD: self._handle_keyword,
        }
    
    def create_campaign(
        self, 
        campaign_id: str, 
        steps: List[Dict]
    ) -> Dict[str, Any]:
        """Створення нової каскадної кампанії"""
        drip_steps = []
        
        for i, step_data in enumerate(steps):
            step = DripStep(
                step_id=i,
                message_text=step_data['text'],
                delay_hours=step_data.get('delay_hours', 24),
                trigger=TriggerType(step_data.get('trigger', 'time')),
                conditions=step_data.get('conditions', []),
                media_url=step_data.get('media_url'),
                buttons=step_data.get('buttons', [])
            )
            drip_steps.append(step)
        
        self.campaigns[campaign_id] = drip_steps
        self.user_progress[campaign_id] = {}
        
        return {
            'campaign_id': campaign_id,
            'steps_count': len(drip_steps),
            'total_duration_hours': sum(s.delay_hours for s in drip_steps),
            'status': 'created'
        }
    
    async def start_for_user(
        self, 
        campaign_id: str, 
        user_id: int
    ) -> Optional[Dict]:
        """Запуск кампанії для користувача"""
        if campaign_id not in self.campaigns:
            logger.error(f"Campaign {campaign_id} not found")
            return None
        
        progress = UserProgress(
            user_id=user_id,
            campaign_id=campaign_id,
            current_step=0,
            started_at=datetime.now()
        )
        
        self.user_progress[campaign_id][user_id] = progress
        
        first_step = self.campaigns[campaign_id][0]
        await self._schedule_step(campaign_id, user_id, first_step)
        
        return {
            'user_id': user_id,
            'campaign_id': campaign_id,
            'started_at': progress.started_at.isoformat(),
            'total_steps': len(self.campaigns[campaign_id])
        }
    
    async def _schedule_step(
        self, 
        campaign_id: str, 
        user_id: int, 
        step: DripStep
    ):
        """Планування виконання кроку"""
        task_id = f"{campaign_id}_{user_id}_{step.step_id}"
        
        if step.trigger == TriggerType.TIME:
            delay_seconds = step.delay_hours * 3600
            
            async def delayed_send():
                await asyncio.sleep(delay_seconds)
                await self._execute_step(campaign_id, user_id, step)
            
            task = asyncio.create_task(delayed_send())
            self.active_tasks[task_id] = task
            
            logger.info(f"Scheduled step {step.step_id} for user {user_id} in {step.delay_hours}h")
    
    async def _execute_step(
        self, 
        campaign_id: str, 
        user_id: int, 
        step: DripStep
    ) -> bool:
        """Виконання кроку кампанії"""
        try:
            progress = self.user_progress[campaign_id].get(user_id)
            if not progress or progress.status != 'active':
                return False
            
            if step.conditions:
                if not self._check_conditions(step.conditions, progress):
                    logger.info(f"Conditions not met for step {step.step_id}")
                    await self._move_to_next_step(campaign_id, user_id)
                    return False
            
            logger.info(f"Executing step {step.step_id} for user {user_id}")
            
            progress.current_step = step.step_id
            progress.last_action_at = datetime.now()
            
            await self._move_to_next_step(campaign_id, user_id)
            return True
            
        except Exception as e:
            logger.error(f"Error executing step: {e}")
            return False
    
    async def _move_to_next_step(self, campaign_id: str, user_id: int):
        """Перехід до наступного кроку"""
        progress = self.user_progress[campaign_id].get(user_id)
        if not progress:
            return
        
        steps = self.campaigns[campaign_id]
        next_step_idx = progress.current_step + 1
        
        if next_step_idx < len(steps):
            next_step = steps[next_step_idx]
            await self._schedule_step(campaign_id, user_id, next_step)
        else:
            progress.status = 'completed'
            logger.info(f"Campaign {campaign_id} completed for user {user_id}")
    
    def _check_conditions(self, conditions: List[str], progress: UserProgress) -> bool:
        """Перевірка умов для кроку"""
        for condition in conditions:
            if condition == 'has_replied':
                if not progress.responses:
                    return False
            elif condition == 'no_replies':
                if progress.responses:
                    return False
        return True
    
    async def handle_user_action(
        self, 
        campaign_id: str, 
        user_id: int, 
        action: str,
        data: Optional[Dict] = None
    ):
        """Обробка дії користувача"""
        progress = self.user_progress.get(campaign_id, {}).get(user_id)
        if not progress or progress.status != 'active':
            return
        
        if action == 'reply':
            progress.responses.append({
                'type': 'reply',
                'timestamp': datetime.now().isoformat(),
                'data': data
            })
            await self._trigger_handlers.get(TriggerType.REPLY_RECEIVED, lambda *a: None)(
                campaign_id, user_id, data
            )
        
        elif action == 'link_click':
            progress.responses.append({
                'type': 'link_click',
                'timestamp': datetime.now().isoformat(),
                'url': data.get('url') if data else None
            })
    
    async def _handle_time_trigger(self, campaign_id: str, user_id: int, data: Dict):
        pass
    
    async def _handle_no_response(self, campaign_id: str, user_id: int, data: Dict):
        progress = self.user_progress.get(campaign_id, {}).get(user_id)
        if progress and not progress.responses:
            await self._move_to_next_step(campaign_id, user_id)
    
    async def _handle_reply(self, campaign_id: str, user_id: int, data: Dict):
        pass
    
    async def _handle_keyword(self, campaign_id: str, user_id: int, data: Dict):
        pass
    
    def stop_for_user(self, campaign_id: str, user_id: int) -> bool:
        """Зупинка кампанії для користувача"""
        progress = self.user_progress.get(campaign_id, {}).get(user_id)
        if progress:
            progress.status = 'stopped'
            
            for task_id, task in list(self.active_tasks.items()):
                if task_id.startswith(f"{campaign_id}_{user_id}_"):
                    task.cancel()
                    del self.active_tasks[task_id]
            
            return True
        return False
    
    def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        """Отримання статистики кампанії"""
        if campaign_id not in self.campaigns:
            return {'error': 'Campaign not found'}
        
        progress_data = self.user_progress.get(campaign_id, {})
        
        stats = {
            'campaign_id': campaign_id,
            'total_users': len(progress_data),
            'active': sum(1 for p in progress_data.values() if p.status == 'active'),
            'completed': sum(1 for p in progress_data.values() if p.status == 'completed'),
            'stopped': sum(1 for p in progress_data.values() if p.status == 'stopped'),
            'total_responses': sum(len(p.responses) for p in progress_data.values()),
            'steps_count': len(self.campaigns[campaign_id])
        }
        
        if stats['total_users'] > 0:
            stats['completion_rate'] = round(
                stats['completed'] / stats['total_users'] * 100, 1
            )
            stats['response_rate'] = round(
                sum(1 for p in progress_data.values() if p.responses) / 
                stats['total_users'] * 100, 1
            )
        else:
            stats['completion_rate'] = 0
            stats['response_rate'] = 0
        
        return stats
    
    def format_stats_report(self, stats: Dict) -> str:
        """Форматування звіту статистики"""
        return f"""<b>📊 СТАТИСТИКА КАМПАНІЇ</b>
═══════════════════════
ID: <code>{stats['campaign_id']}</code>
Кроків: {stats['steps_count']}

<b>Користувачі:</b>
├ Всього: {stats['total_users']}
├ Активні: {stats['active']}
├ Завершили: {stats['completed']}
└ Зупинені: {stats['stopped']}

<b>Метрики:</b>
├ Завершення: {stats.get('completion_rate', 0)}%
├ Відповіді: {stats.get('response_rate', 0)}%
└ Всього відповідей: {stats['total_responses']}"""


drip_campaign_manager = DripCampaignManager()
