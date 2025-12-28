import asyncio
import logging
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class SendStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    BLOCKED = "blocked"
    FLOOD_WAIT = "flood_wait"

@dataclass
class SendResult:
    """Результат відправки"""
    target: Any
    status: SendStatus
    message_id: Optional[int] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    retry_after: Optional[int] = None

@dataclass
class CampaignStats:
    """Статистика кампанії"""
    total: int = 0
    sent: int = 0
    failed: int = 0
    blocked: int = 0
    flood_waits: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class MassSender:
    """Система масової розсилки через Telethon"""
    
    def __init__(self, api_id: int = None, api_hash: str = None):
        self.api_id = api_id or int(os.getenv('TELEGRAM_API_ID', '0'))
        self.api_hash = api_hash or os.getenv('TELEGRAM_API_HASH', '')
        self.client = None
        
        self.delay_config = {
            'base_delay': (3, 7),
            'after_flood': 60,
            'after_error': 10,
            'batch_pause': 30,
            'batch_size': 20
        }
        
        self.rate_limits = {
            'messages_per_minute': 20,
            'messages_per_hour': 100,
            'flood_wait_threshold': 3
        }
        
        self._running = False
        self._paused = False
        self.current_campaign: Optional[str] = None
        self.stats = CampaignStats()
        self.results: List[SendResult] = []
        
        self.flood_wait_count = 0
        self.last_message_time: Optional[datetime] = None
        
        self.progress_callback: Optional[Callable] = None
    
    async def connect(self, session_name: str = 'sender_session') -> bool:
        """Підключення до Telegram"""
        try:
            from telethon import TelegramClient
            from telethon.errors import FloodWaitError, UserPrivacyRestrictedError
            
            self.client = TelegramClient(session_name, self.api_id, self.api_hash)
            await self.client.start()
            
            logger.info("✅ MassSender connected")
            return True
            
        except ImportError:
            logger.error("Telethon not installed")
            return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    async def disconnect(self):
        """Відключення"""
        if self.client:
            await self.client.disconnect()
    
    def set_progress_callback(self, callback: Callable):
        """Встановити callback для прогресу"""
        self.progress_callback = callback
    
    async def send_to_chats(
        self,
        chat_ids: List[int],
        message: str,
        media: Optional[str] = None,
        campaign_name: str = None,
        stealth_mode: bool = False,
        stealth_delay: int = 60
    ) -> Dict[str, Any]:
        """Розсилка в чати"""
        
        self.current_campaign = campaign_name or f"CHAT-{datetime.now().strftime('%H%M%S')}"
        self.stats = CampaignStats(
            total=len(chat_ids),
            started_at=datetime.now()
        )
        self.results = []
        self._running = True
        self.flood_wait_count = 0
        
        logger.info(f"Starting campaign {self.current_campaign} to {len(chat_ids)} chats (Stealth: {stealth_mode})")
        
        for i, chat_id in enumerate(chat_ids):
            if not self._running:
                break
            
            while self._paused:
                await asyncio.sleep(1)
            
            result = await self._send_message(chat_id, message, media)
            self.results.append(result)
            
            if result.status == SendStatus.SENT:
                self.stats.sent += 1
                if stealth_mode and result.message_id:
                    # Плануємо видалення повідомлення
                    asyncio.create_task(self._stealth_delete(chat_id, result.message_id, stealth_delay))
            elif result.status == SendStatus.FAILED:
                self.stats.failed += 1
            elif result.status == SendStatus.BLOCKED:
                self.stats.blocked += 1
            elif result.status == SendStatus.FLOOD_WAIT:
                self.stats.flood_waits += 1
                self.flood_wait_count += 1
                
                if self.flood_wait_count >= self.rate_limits['flood_wait_threshold']:
                    logger.warning("Too many flood waits, stopping campaign")
                    break
                
                if result.retry_after:
                    await asyncio.sleep(min(result.retry_after, 300))
            
            if self.progress_callback:
                await self.progress_callback({
                    'campaign': self.current_campaign,
                    'progress': (i + 1) / len(chat_ids) * 100,
                    'sent': self.stats.sent,
                    'failed': self.stats.failed,
                    'current': i + 1,
                    'total': len(chat_ids)
                })
            
            if (i + 1) % self.delay_config['batch_size'] == 0:
                logger.info(f"Batch pause after {i + 1} messages")
                await asyncio.sleep(self.delay_config['batch_pause'])
            else:
                delay = random.uniform(*self.delay_config['base_delay'])
                await asyncio.sleep(delay)
        
        self.stats.completed_at = datetime.now()
        self._running = False
        
        return self._get_campaign_report()
    
    async def send_to_users(
        self,
        user_ids: List[int],
        message: str,
        media: Optional[str] = None,
        campaign_name: str = None
    ) -> Dict[str, Any]:
        """Розсилка користувачам"""
        return await self.send_to_chats(user_ids, message, media, campaign_name)
    
    async def broadcast_to_subscribers(
        self,
        channel_username: str,
        message: str,
        media: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Розсилка підписникам каналу"""
        
        if not self.client:
            return {'error': 'Not connected'}
        
        try:
            channel = await self.client.get_entity(channel_username)
            participants = await self.client.get_participants(channel, limit=limit)
            
            user_ids = [p.id for p in participants if not p.bot]
            
            return await self.send_to_users(
                user_ids,
                message,
                media,
                f"BROADCAST-{channel_username}"
            )
            
        except Exception as e:
            logger.error(f"Broadcast error: {e}")
            return {'error': str(e)}
    
    async def _stealth_delete(self, chat_id: Any, message_id: int, delay: int):
        """Автоматичне видалення повідомлення через заданий час (Режим Невидимка)"""
        try:
            await asyncio.sleep(delay)
            if self.client:
                await self.client.delete_messages(chat_id, [message_id])
                logger.debug(f"Stealth delete: message {message_id} in {chat_id} removed")
        except Exception as e:
            logger.error(f"Stealth delete error for {message_id} in {chat_id}: {e}")

    async def _send_message(
        self,
        target: Any,
        message: str,
        media: Optional[str] = None
    ) -> SendResult:
        """Відправка одного повідомлення"""
        
        from telethon.errors import (
            FloodWaitError, 
            UserPrivacyRestrictedError,
            ChatWriteForbiddenError,
            PeerFloodError,
            UserBannedInChannelError
        )
        
        result = SendResult(
            target=target,
            status=SendStatus.PENDING
        )
        
        try:
            if media:
                sent = await self.client.send_file(
                    target,
                    media,
                    caption=message
                )
            else:
                sent = await self.client.send_message(
                    target,
                    message,
                    link_preview=False
                )
            
            result.status = SendStatus.SENT
            result.message_id = sent.id
            self.last_message_time = datetime.now()
            
            logger.debug(f"Sent to {target}: message_id={sent.id}")
            
        except FloodWaitError as e:
            result.status = SendStatus.FLOOD_WAIT
            result.error = f"FloodWait: {e.seconds}s"
            result.retry_after = e.seconds
            logger.warning(f"FloodWait for {target}: {e.seconds}s")
            
        except UserPrivacyRestrictedError:
            result.status = SendStatus.BLOCKED
            result.error = "Privacy restricted"
            logger.debug(f"Privacy blocked: {target}")
            
        except ChatWriteForbiddenError:
            result.status = SendStatus.BLOCKED
            result.error = "Write forbidden"
            logger.debug(f"Write forbidden: {target}")
            
        except PeerFloodError:
            result.status = SendStatus.FLOOD_WAIT
            result.error = "PeerFlood"
            result.retry_after = 60
            logger.warning(f"PeerFlood for {target}")
            
        except UserBannedInChannelError:
            result.status = SendStatus.BLOCKED
            result.error = "Banned in channel"
            
        except Exception as e:
            result.status = SendStatus.FAILED
            result.error = str(e)
            logger.error(f"Send error to {target}: {e}")
        
        return result
    
    def pause(self):
        """Пауза кампанії"""
        self._paused = True
        logger.info(f"Campaign {self.current_campaign} paused")
    
    def resume(self):
        """Відновлення кампанії"""
        self._paused = False
        logger.info(f"Campaign {self.current_campaign} resumed")
    
    def stop(self):
        """Зупинка кампанії"""
        self._running = False
        logger.info(f"Campaign {self.current_campaign} stopped")
    
    def _get_campaign_report(self) -> Dict[str, Any]:
        """Отримання звіту про кампанію"""
        
        duration = None
        if self.stats.started_at and self.stats.completed_at:
            duration = (self.stats.completed_at - self.stats.started_at).total_seconds()
        
        success_rate = 0
        if self.stats.total > 0:
            success_rate = (self.stats.sent / self.stats.total) * 100
        
        return {
            'campaign_id': self.current_campaign,
            'status': 'completed' if not self._running else 'running',
            'total': self.stats.total,
            'sent': self.stats.sent,
            'failed': self.stats.failed,
            'blocked': self.stats.blocked,
            'flood_waits': self.stats.flood_waits,
            'success_rate': round(success_rate, 2),
            'started_at': self.stats.started_at.isoformat() if self.stats.started_at else None,
            'completed_at': self.stats.completed_at.isoformat() if self.stats.completed_at else None,
            'duration_seconds': duration,
            'speed': round(self.stats.sent / duration, 2) if duration and duration > 0 else 0
        }
    
    def get_formatted_report(self) -> str:
        """Форматований звіт"""
        
        report = self._get_campaign_report()
        
        return f"""
📤 ЗВІТ РОЗСИЛКИ
───────────────═════
Кампанія: {report['campaign_id']}
Статус: {report['status']}

📊 СТАТИСТИКА:
├ Всього цілей: {report['total']}
├ Відправлено: {report['sent']}
├ Помилок: {report['failed']}
├ Заблоковано: {report['blocked']}
└ FloodWait: {report['flood_waits']}

📈 ПОКАЗНИКИ:
├ Успішність: {report['success_rate']}%
├ Тривалість: {report['duration_seconds']:.0f}с
└ Швидкість: {report['speed']:.2f} msg/s

───────────────═════
"""

class PsyOpsCampaign:
    """Кампанії психологічних операцій"""
    
    def __init__(self, sender: MassSender = None):
        self.sender = sender or MassSender()
        
        self.message_templates = {
            'alert': [
                "⚠️ УВАГА! Силам безпеки відомо про місцезнаходження групи. Рекомендовано негайна зміна позиції.",
                "🚨 Командування наказує призупинити операцію до отримання нових наказів.",
                "📡 Радіочастоти зкомпрометовані. Перейти на резервний канал зв'язку.",
                "🛑 Вибухівка виявлена сканерами. Не наближатися до схованки.",
            ],
            'disinformation': [
                "👮 Поліція отримала підкріплення. План 'Б' - евакуація через південний вихід.",
                "🔊 Контрольована радіостанція передає хибні координати.",
                "💣 Система дистанційного підриву деактивована.",
                "🆘 Надійшов сигнал тривоги з сусіднього блоку.",
            ],
            'panic': [
                "📶 Зв'язок заглушено. Використовуйте лише кур'єрів.",
                "🎯 Снайпери зайняли позиції на дахах. Не показуватися у вікнах.",
                "🚁 Над районом зафіксовано безпілотник спостереження.",
                "⏰ Терміново! Є 15 хвилин на евакуацію.",
            ]
        }
    
    async def execute_campaign(
        self,
        targets: List[int],
        campaign_type: str = 'alert',
        randomize: bool = True
    ) -> Dict[str, Any]:
        """Виконання кампанії"""
        
        templates = self.message_templates.get(campaign_type, self.message_templates['alert'])
        
        results = []
        
        for target in targets:
            message = random.choice(templates) if randomize else templates[0]
            
            result = await self.sender.send_to_chats(
                [target],
                message,
                campaign_name=f"PSYOPS-{campaign_type.upper()}"
            )
            results.append(result)
            
            await asyncio.sleep(random.uniform(15, 30))
        
        return {
            'campaign_type': campaign_type,
            'targets_count': len(targets),
            'results': results
        }
    
    async def personalized_alert(
        self,
        user_ids: List[int],
        template: str,
        personalization_data: Dict[int, Dict] = None
    ) -> Dict[str, Any]:
        """Персоналізовані сповіщення"""
        
        personalization_data = personalization_data or {}
        results = []
        
        for user_id in user_ids:
            data = personalization_data.get(user_id, {
                'time': datetime.now().strftime("%H:%M"),
                'location': 'невідомо'
            })
            
            message = template.format(**data)
            
            result = await self.sender._send_message(user_id, message)
            results.append({
                'user_id': user_id,
                'status': result.status.value,
                'error': result.error
            })
            
            await asyncio.sleep(random.uniform(3, 7))
        
        return {
            'total': len(user_ids),
            'sent': len([r for r in results if r['status'] == 'sent']),
            'results': results
        }

mass_sender = MassSender()
psyops = PsyOpsCampaign(mass_sender)
