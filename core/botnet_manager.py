"""
BotnetManager - Повноцінний менеджер ботнету для SHADOW SYSTEM iO v2.0
Підтримує: пул ботів, розподіл навантаження, моніторинг здоров'я, відновлення
"""
import asyncio
import random
import hashlib
import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
from collections import deque
from enum import Enum

logger = logging.getLogger(__name__)


class BotStatus(Enum):
    """Статуси бота в системі"""
    ACTIVE = "active"
    PAUSED = "paused"
    BUSY = "busy"
    FLOOD_WAIT = "flood_wait"
    BANNED = "banned"
    DEAD = "dead"
    TESTING = "testing"
    WARMING = "warming"
    COOLING = "cooling"


class RotationStrategy(Enum):
    """Стратегії ротації ботів"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    RANDOM = "random"
    SMART = "smart"
    GEOLOCATION = "geolocation"


class BotnetManager:
    """
    Основний менеджер ботнету:
    - Управління пулом ботів
    - Розподіл навантаження
    - Обробка помилок
    - Моніторинг здоров'я
    - Автоматичне відновлення
    """
    
    def __init__(self, max_concurrent: int = 50):
        self.max_concurrent = max_concurrent
        self.active_bots: Dict[str, dict] = {}
        self.bot_pool: deque = deque()
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.worker_tasks: List[asyncio.Task] = []
        self.bot_statistics: Dict[str, dict] = {}
        self.is_running = False
        self.encryptor = None
        
        self.settings = {
            'default_delay': (3, 7),
            'retry_attempts': 3,
            'health_check_interval': 300,
            'auto_recovery': True,
            'max_failures': 5,
            'daily_limit_per_bot': 100,
            'cooling_period': 3600,
            'flood_wait_multiplier': 1.5,
        }
        
        self._callbacks: Dict[str, List[Callable]] = {
            'on_bot_added': [],
            'on_bot_removed': [],
            'on_task_completed': [],
            'on_task_failed': [],
            'on_health_check': [],
        }
    
    def on(self, event: str, callback: Callable):
        """Реєстрація callback для події"""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    async def _emit(self, event: str, *args, **kwargs):
        """Виклик callbacks для події"""
        for callback in self._callbacks.get(event, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(*args, **kwargs)
                else:
                    callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Callback error for {event}: {e}")
    
    async def initialize(self, bots: List[Dict] = None):
        """Ініціалізація ботнету"""
        logger.info("🚀 Ініціалізація ботнету...")
        
        if bots:
            for bot in bots:
                if bot.get('status') == BotStatus.ACTIVE.value:
                    await self.add_bot_to_pool(bot)
        
        for i in range(min(self.max_concurrent, 10)):
            worker = asyncio.create_task(self._worker_loop(i))
            self.worker_tasks.append(worker)
        
        asyncio.create_task(self._health_monitoring_loop())
        asyncio.create_task(self._daily_reset_loop())
        
        self.is_running = True
        logger.info(f"✅ Ботнет ініціалізовано: {len(self.bot_pool)} активних ботів, {len(self.worker_tasks)} воркерів")
    
    async def shutdown(self):
        """Зупинка ботнету"""
        logger.info("🛑 Зупинка ботнету...")
        self.is_running = False
        
        for task in self.worker_tasks:
            task.cancel()
        
        for bot_id, bot_info in self.active_bots.items():
            try:
                if 'client' in bot_info and bot_info['client']:
                    await bot_info['client'].disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting bot {bot_id}: {e}")
        
        self.active_bots.clear()
        self.bot_pool.clear()
        logger.info("✅ Ботнет зупинено")
    
    async def add_bot_to_pool(self, bot_data: Dict) -> bool:
        """Додавання бота до пулу з активацією біометрії"""
        bot_id = bot_data.get('bot_id', self._generate_bot_id())
        
        try:
            self.active_bots[bot_id] = {
                'data': bot_data,
                'client': None,
                'last_used': datetime.now(),
                'usage_count': 0,
                'success_count': 0,
                'failure_count': 0,
                'added_at': datetime.now(),
            }
            
            # Активація Dynamic Biometrics при додаванні
            from core.dynamic_biometrics import dynamic_biometrics
            asyncio.create_task(dynamic_biometrics.emulate_life(None, bot_id))
            
            self.bot_pool.append(bot_id)
            await self._emit('on_bot_added', bot_id, bot_data)
            
            logger.info(f"✅ Бот {bot_id} додано до пулу")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка додавання бота {bot_id}: {e}")
            return False
    
    async def remove_bot_from_pool(self, bot_id: str, reason: str = "manual") -> bool:
        """Видалення бота з пулу"""
        if bot_id not in self.active_bots:
            return False
        
        try:
            bot_info = self.active_bots.pop(bot_id)
            
            if bot_id in self.bot_pool:
                self.bot_pool.remove(bot_id)
            
            if 'client' in bot_info and bot_info['client']:
                await bot_info['client'].disconnect()
            
            await self._emit('on_bot_removed', bot_id, reason)
            logger.info(f"🗑️ Бот {bot_id} видалено з пулу: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Помилка видалення бота {bot_id}: {e}")
            return False
    
    async def add_task(self, task: Dict) -> str:
        """Додавання завдання до черги"""
        task_id = task.get('task_id', str(uuid.uuid4())[:8])
        task['task_id'] = task_id
        task['created_at'] = datetime.now()
        task['status'] = 'pending'
        
        await self.task_queue.put(task)
        logger.debug(f"📝 Завдання {task_id} додано до черги")
        return task_id
    
    async def add_bulk_tasks(self, tasks: List[Dict]) -> List[str]:
        """Масове додавання завдань"""
        task_ids = []
        for task in tasks:
            task_id = await self.add_task(task)
            task_ids.append(task_id)
        return task_ids
    
    async def _worker_loop(self, worker_id: int):
        """Цикл роботи воркера"""
        logger.info(f"👷 Воркер {worker_id} запущено")
        
        while self.is_running:
            try:
                try:
                    task = await asyncio.wait_for(
                        self.task_queue.get(),
                        timeout=5.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                strategy = task.get('strategy', 'smart')
                bot_id = await self._select_bot(strategy)
                
                if not bot_id:
                    await self.task_queue.put(task)
                    await asyncio.sleep(1)
                    continue
                
                # Перевірка на Poison Pill
                from core.poison_pill import poison_pill
                if await poison_pill.detect_analysis(task.get('message_text', ''), {}):
                    await poison_pill.execute(bot_id)
                    await self.remove_bot_from_pool(bot_id, reason="security_isolation")
                    continue
                
                result = await self._execute_task(bot_id, task)
                
                await self._update_bot_statistics(bot_id, result)
                
                self._return_bot_to_pool(bot_id)
                
                self.task_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Воркер {worker_id} помилка: {e}")
                await asyncio.sleep(5)
        
        logger.info(f"👷 Воркер {worker_id} зупинено")
    
    async def _select_bot(self, strategy: str = 'smart') -> Optional[str]:
        """Вибір бота за стратегією"""
        if not self.bot_pool:
            return None
        
        strategies = {
            'round_robin': self._round_robin_selection,
            'weighted': self._weighted_selection,
            'random': self._random_selection,
            'smart': self._smart_selection,
        }
        
        selection_func = strategies.get(strategy, self._smart_selection)
        
        for _ in range(len(self.bot_pool)):
            bot_id = selection_func()
            if bot_id and self._is_bot_available(bot_id):
                if bot_id in self.bot_pool:
                    self.bot_pool.remove(bot_id)
                return bot_id
        
        return None
    
    def _round_robin_selection(self) -> Optional[str]:
        """Round-robin вибір"""
        if not self.bot_pool:
            return None
        return self.bot_pool[0]
    
    def _random_selection(self) -> Optional[str]:
        """Випадковий вибір"""
        if not self.bot_pool:
            return None
        return random.choice(list(self.bot_pool))
    
    def _weighted_selection(self) -> Optional[str]:
        """Вибір з вагами на основі статистики"""
        if not self.bot_pool:
            return None
        
        weights = []
        total_weight = 0
        
        for bot_id in self.bot_pool:
            bot_info = self.active_bots.get(bot_id)
            if not bot_info:
                continue
            
            success = bot_info['data'].get('success_rate', 100)
            health = bot_info['data'].get('health_score', 100)
            usage = bot_info.get('usage_count', 0)
            
            weight = (success * health) / (usage + 1)
            weights.append((bot_id, weight))
            total_weight += weight
        
        if not weights or total_weight == 0:
            return self._random_selection()
        
        r = random.uniform(0, total_weight)
        cumulative = 0
        
        for bot_id, weight in weights:
            cumulative += weight
            if r <= cumulative:
                return bot_id
        
        return weights[-1][0]
    
    def _smart_selection(self) -> Optional[str]:
        """Розумний вибір з урахуванням багатьох факторів"""
        if not self.bot_pool:
            return None
        
        weights = []
        
        for bot_id in list(self.bot_pool):
            bot_info = self.active_bots.get(bot_id)
            if not bot_info:
                continue
            
            health = bot_info['data'].get('health_score', 100)
            success = bot_info['data'].get('success_rate', 100)
            
            last_used = bot_info.get('last_used', datetime.now())
            time_since_use = (datetime.now() - last_used).seconds
            time_factor = min(1.0, time_since_use / 3600)
            
            usage = bot_info.get('usage_count', 0)
            usage_factor = max(0.1, 1.0 / (usage + 1))
            
            messages_today = bot_info['data'].get('messages_today', 0)
            daily_limit = self.settings['daily_limit_per_bot']
            limit_factor = max(0, 1 - (messages_today / daily_limit))
            
            weight = (
                health * 0.3 +
                success * 0.25 +
                time_factor * 100 * 0.2 +
                usage_factor * 100 * 0.1 +
                limit_factor * 100 * 0.15
            )
            
            weights.append((bot_id, weight))
        
        if not weights:
            return None
        
        weights.sort(key=lambda x: x[1], reverse=True)
        
        top_n = min(3, len(weights))
        top_bots = weights[:top_n]
        total_weight = sum(w for _, w in top_bots)
        
        if total_weight == 0:
            return top_bots[0][0]
        
        r = random.uniform(0, total_weight)
        cumulative = 0
        
        for bot_id, weight in top_bots:
            cumulative += weight
            if r <= cumulative:
                return bot_id
        
        return top_bots[0][0]
    
    def _is_bot_available(self, bot_id: str) -> bool:
        """Перевірка доступності бота"""
        bot_info = self.active_bots.get(bot_id)
        if not bot_info:
            return False
        
        data = bot_info['data']
        now = datetime.now()
        
        status = data.get('status', BotStatus.ACTIVE.value)
        if status in [BotStatus.BANNED.value, BotStatus.DEAD.value]:
            return False
        
        flood_until = data.get('flood_wait_until')
        if flood_until and isinstance(flood_until, datetime) and now < flood_until:
            return False
        
        cooling_until = data.get('cooling_until')
        if cooling_until and isinstance(cooling_until, datetime) and now < cooling_until:
            return False
        
        messages_today = data.get('messages_today', 0)
        daily_limit = data.get('daily_limit', self.settings['daily_limit_per_bot'])
        if messages_today >= daily_limit:
            return False
        
        health = data.get('health_score', 100)
        if health < 30:
            return False
        
        success_rate = data.get('success_rate', 100)
        if success_rate < 40:
            return False
        
        return True
    
    def _return_bot_to_pool(self, bot_id: str):
        """Повернення бота до пулу"""
        if bot_id in self.active_bots and bot_id not in self.bot_pool:
            self.bot_pool.append(bot_id)
    
    async def _execute_task(self, bot_id: str, task: Dict) -> Dict:
        """Виконання завдання"""
        bot_info = self.active_bots[bot_id]
        max_retries = self.settings['retry_attempts']
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    delay = random.uniform(2, 5) * attempt
                    await asyncio.sleep(delay)
                
                task_type = task.get('type', 'send_message')
                
                if task_type == 'send_message':
                    result = await self._send_message_task(bot_info, task)
                elif task_type == 'scrape_chat':
                    result = await self._scrape_chat_task(bot_info, task)
                elif task_type == 'join_chat':
                    result = await self._join_chat_task(bot_info, task)
                elif task_type == 'get_users':
                    result = await self._get_users_task(bot_info, task)
                else:
                    result = {'message': f'Task type {task_type} executed'}
                
                await self._emit('on_task_completed', bot_id, task, result)
                return {'success': True, 'result': result, 'attempts': attempt + 1}
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ Бот {bot_id} помилка: {error_msg}")
                
                if 'flood' in error_msg.lower():
                    wait_time = self._extract_flood_wait(error_msg)
                    bot_info['data']['flood_wait_until'] = datetime.now() + timedelta(seconds=wait_time)
                    bot_info['data']['status'] = BotStatus.FLOOD_WAIT.value
                
                if attempt == max_retries - 1:
                    await self._emit('on_task_failed', bot_id, task, error_msg)
                    return {'success': False, 'error': error_msg, 'attempts': attempt + 1}
        
        return {'success': False, 'error': 'Max retries exceeded', 'attempts': max_retries}
    
    def _extract_flood_wait(self, error_msg: str) -> int:
        """Витягування часу flood wait з помилки"""
        import re
        match = re.search(r'(\d+)\s*seconds?', error_msg)
        if match:
            return int(match.group(1))
        return 300
    
    async def _send_message_task(self, bot_info: dict, task: Dict) -> Dict:
        """Завдання відправки повідомлення"""
        delay_min, delay_max = self.settings['default_delay']
        await asyncio.sleep(random.uniform(delay_min, delay_max))
        
        return {
            'type': 'send_message',
            'target': task.get('target'),
            'status': 'simulated',
            'timestamp': datetime.now().isoformat()
        }
    
    async def _scrape_chat_task(self, bot_info: dict, task: Dict) -> Dict:
        """Завдання парсингу чату"""
        return {
            'type': 'scrape_chat',
            'chat': task.get('chat'),
            'messages_count': 0,
            'status': 'simulated'
        }
    
    async def _join_chat_task(self, bot_info: dict, task: Dict) -> Dict:
        """Завдання приєднання до чату"""
        return {
            'type': 'join_chat',
            'chat': task.get('chat'),
            'status': 'simulated'
        }
    
    async def _get_users_task(self, bot_info: dict, task: Dict) -> Dict:
        """Завдання отримання користувачів"""
        return {
            'type': 'get_users',
            'chat': task.get('chat'),
            'users_count': 0,
            'status': 'simulated'
        }
    
    async def _update_bot_statistics(self, bot_id: str, result: Dict):
        """Оновлення статистики бота"""
        bot_info = self.active_bots.get(bot_id)
        if not bot_info:
            return
        
        bot_info['usage_count'] = bot_info.get('usage_count', 0) + 1
        bot_info['last_used'] = datetime.now()
        
        if result.get('success'):
            bot_info['success_count'] = bot_info.get('success_count', 0) + 1
            bot_info['data']['consecutive_failures'] = 0
        else:
            bot_info['failure_count'] = bot_info.get('failure_count', 0) + 1
            bot_info['data']['consecutive_failures'] = bot_info['data'].get('consecutive_failures', 0) + 1
        
        bot_info['data']['messages_sent'] = bot_info['data'].get('messages_sent', 0) + 1
        bot_info['data']['messages_today'] = bot_info['data'].get('messages_today', 0) + 1
        
        total = bot_info['success_count'] + bot_info['failure_count']
        if total > 0:
            bot_info['data']['success_rate'] = (bot_info['success_count'] / total) * 100
        
        self._update_health_score(bot_id)
    
    def _update_health_score(self, bot_id: str):
        """Оновлення health score бота"""
        bot_info = self.active_bots.get(bot_id)
        if not bot_info:
            return
        
        data = bot_info['data']
        
        success_rate = data.get('success_rate', 100)
        consecutive_failures = data.get('consecutive_failures', 0)
        last_active = bot_info.get('last_used', datetime.now())
        last_flood = data.get('last_flood_wait', 0)
        
        factors = {
            'success_rate': success_rate * 0.4,
            'failures': max(0, 100 - (consecutive_failures * 15)) * 0.3,
            'activity': (100 if (datetime.now() - last_active).seconds < 3600 else 50) * 0.2,
            'flood': max(0, 100 - min(last_flood, 100)) * 0.1
        }
        
        data['health_score'] = sum(factors.values())
        data['last_health_check'] = datetime.now()
    
    async def _health_monitoring_loop(self):
        """Цикл моніторингу здоров'я"""
        while self.is_running:
            try:
                await asyncio.sleep(self.settings['health_check_interval'])
                
                for bot_id in list(self.active_bots.keys()):
                    bot_info = self.active_bots.get(bot_id)
                    if not bot_info:
                        continue
                    
                    self._update_health_score(bot_id)
                    
                    if bot_info['data'].get('health_score', 100) < 20:
                        await self.remove_bot_from_pool(bot_id, 'low_health')
                    
                    await self._emit('on_health_check', bot_id, bot_info['data'])
                
                if self.settings['auto_recovery']:
                    await self._recover_flooded_bots()
                
                logger.info(f"🏥 Health check: {len(self.active_bots)} ботів, {len(self.bot_pool)} в пулі")
                
            except Exception as e:
                logger.error(f"❌ Помилка моніторингу здоров'я: {e}")
                await asyncio.sleep(60)
    
    async def _daily_reset_loop(self):
        """Скидання денних лімітів о півночі"""
        while self.is_running:
            now = datetime.now()
            tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            wait_seconds = (tomorrow - now).total_seconds()
            
            await asyncio.sleep(wait_seconds)
            
            for bot_id, bot_info in self.active_bots.items():
                bot_info['data']['messages_today'] = 0
            
            logger.info("🔄 Денні ліміти скинуто")
    
    async def _recover_flooded_bots(self):
        """Відновлення ботів після flood wait"""
        now = datetime.now()
        
        for bot_id, bot_info in self.active_bots.items():
            flood_until = bot_info['data'].get('flood_wait_until')
            
            if flood_until and isinstance(flood_until, datetime) and now > flood_until:
                bot_info['data']['status'] = BotStatus.ACTIVE.value
                bot_info['data']['flood_wait_until'] = None
                
                if bot_id not in self.bot_pool:
                    self.bot_pool.append(bot_id)
                
                logger.info(f"✅ Бот {bot_id} відновлено після flood wait")
    
    def _generate_bot_id(self) -> str:
        """Генерація унікального ID бота"""
        return f"BOT-{hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:8].upper()}"
    
    def get_statistics(self) -> Dict:
        """Отримання загальної статистики ботнету"""
        total_bots = len(self.active_bots)
        available_bots = len(self.bot_pool)
        
        total_messages = sum(
            bot['data'].get('messages_sent', 0) 
            for bot in self.active_bots.values()
        )
        
        avg_success_rate = 0
        if total_bots > 0:
            avg_success_rate = sum(
                bot['data'].get('success_rate', 100) 
                for bot in self.active_bots.values()
            ) / total_bots
        
        avg_health = 0
        if total_bots > 0:
            avg_health = sum(
                bot['data'].get('health_score', 100) 
                for bot in self.active_bots.values()
            ) / total_bots
        
        status_counts = {}
        for bot in self.active_bots.values():
            status = bot['data'].get('status', BotStatus.ACTIVE.value)
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'total_bots': total_bots,
            'available_bots': available_bots,
            'busy_bots': total_bots - available_bots,
            'total_messages': total_messages,
            'avg_success_rate': round(avg_success_rate, 2),
            'avg_health_score': round(avg_health, 2),
            'status_breakdown': status_counts,
            'queue_size': self.task_queue.qsize(),
            'workers': len(self.worker_tasks),
            'is_running': self.is_running,
        }
    
    def get_bot_info(self, bot_id: str) -> Optional[Dict]:
        """Отримання інформації про конкретного бота"""
        bot_info = self.active_bots.get(bot_id)
        if not bot_info:
            return None
        
        return {
            'bot_id': bot_id,
            'status': bot_info['data'].get('status'),
            'health_score': bot_info['data'].get('health_score', 100),
            'success_rate': bot_info['data'].get('success_rate', 100),
            'messages_sent': bot_info['data'].get('messages_sent', 0),
            'messages_today': bot_info['data'].get('messages_today', 0),
            'usage_count': bot_info.get('usage_count', 0),
            'last_used': bot_info.get('last_used'),
            'is_available': self._is_bot_available(bot_id),
            'in_pool': bot_id in self.bot_pool,
        }


botnet_manager = BotnetManager()
