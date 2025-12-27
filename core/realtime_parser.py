"""
RealTime Parser - Парсинг та моніторинг в реальному часі
Модуль для інкрементальних оновлень та сповіщень про загрози
"""
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from collections import defaultdict
import logging

from core.advanced_parser import AdvancedTelegramParser, ParsedMessage

logger = logging.getLogger(__name__)


class RealTimeParser:
    """Парсинг з реальним часом та інкрементальними оновленнями"""
    
    def __init__(self, client=None):
        self.client = client
        self.parser = AdvancedTelegramParser(client)
        self.last_parsed: Dict[int, int] = {}
        self.message_hashes: set = set()
        self.is_monitoring = False
        self.monitored_chats: List = []
        self.alert_callbacks: List[Callable] = []
        
        self.stats = {
            'total_monitored': 0,
            'alerts_triggered': 0,
            'messages_processed': 0,
            'uptime_start': None
        }
        
        self.settings = {
            'check_interval': 30,
            'threat_threshold': 30,
            'max_hash_cache': 10000,
            'batch_size': 50
        }
    
    def set_client(self, client):
        """Встановлення клієнта"""
        self.client = client
        self.parser.client = client
    
    def add_alert_callback(self, callback: Callable):
        """Додавання callback для сповіщень"""
        self.alert_callbacks.append(callback)
    
    async def start_realtime_monitoring(self, chat_identifiers: List[str]):
        """Запуск моніторингу в реальному часі"""
        if not self.client:
            logger.error("Client not initialized")
            return False
        
        logger.info(f"📡 Запуск реального моніторингу для {len(chat_identifiers)} чатів")
        self.is_monitoring = True
        self.monitored_chats = chat_identifiers
        self.stats['uptime_start'] = datetime.now()
        
        for chat_id in chat_identifiers:
            try:
                entity = await self.client.get_entity(chat_id)
                
                messages = await self.client.get_messages(entity, limit=1)
                if messages:
                    self.last_parsed[entity.id] = messages[0].id
                
                logger.info(f"✅ Моніторинг чату {chat_id} активовано")
                self.stats['total_monitored'] += 1
                
            except Exception as e:
                logger.error(f"❌ Помилка ініціалізації {chat_id}: {e}")
        
        asyncio.create_task(self.monitoring_loop())
        return True
    
    async def stop_monitoring(self):
        """Зупинка моніторингу"""
        self.is_monitoring = False
        logger.info("⏹️ Моніторинг зупинено")
    
    async def monitoring_loop(self):
        """Основний цикл моніторингу"""
        while self.is_monitoring:
            try:
                for chat_id, last_msg_id in list(self.last_parsed.items()):
                    await self.check_new_messages(chat_id, last_msg_id)
                
                await asyncio.sleep(self.settings['check_interval'])
                
            except Exception as e:
                logger.error(f"Помилка моніторингу: {e}")
                await asyncio.sleep(60)
    
    async def check_new_messages(self, chat_id: int, last_msg_id: int):
        """Перевірка нових повідомлень з останнього парсингу"""
        if not self.client:
            return
        
        try:
            entity = await self.client.get_input_entity(chat_id)
            
            messages = await self.client.get_messages(
                entity,
                limit=self.settings['batch_size'],
                min_id=last_msg_id
            )
            
            if not messages:
                return
            
            for msg in reversed(messages):
                msg_hash = self.calculate_message_hash(msg)
                
                if msg_hash in self.message_hashes:
                    continue
                
                parsed = self.parser.parse_single_message(msg)
                self.stats['messages_processed'] += 1
                
                if parsed.threat_level > self.settings['threat_threshold']:
                    await self.trigger_real_time_alert(parsed, chat_id)
                
                self.last_parsed[chat_id] = max(self.last_parsed.get(chat_id, 0), msg.id)
                self.message_hashes.add(msg_hash)
            
            if len(self.message_hashes) > self.settings['max_hash_cache']:
                self.message_hashes = set(list(self.message_hashes)[-self.settings['max_hash_cache'] // 2:])
                
        except Exception as e:
            logger.error(f"Помилка перевірки нових повідомлень для {chat_id}: {e}")
    
    def calculate_message_hash(self, message) -> str:
        """Розрахунок унікального хешу повідомлення"""
        text = message.message or '' if hasattr(message, 'message') else ''
        content = f"{message.id}-{text}-{message.date.timestamp() if message.date else 0}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def trigger_real_time_alert(self, message: ParsedMessage, chat_id: int):
        """Тригер сповіщення в реальному часі"""
        self.stats['alerts_triggered'] += 1
        
        alert_data = {
            'timestamp': datetime.now().isoformat(),
            'chat_id': chat_id,
            'message_id': message.id,
            'sender_id': message.sender_id,
            'threat_level': message.threat_level,
            'keywords': message.contains_keywords,
            'has_coordinates': message.contains_coordinates,
            'text_preview': message.text[:200] if message.text else ''
        }
        
        logger.warning(f"🚨 РЕАЛЬНИЙ ЧАС: Загроза рівня {message.threat_level} в чаті {chat_id}")
        
        for callback in self.alert_callbacks:
            try:
                await callback(alert_data)
            except Exception as e:
                logger.error(f"Помилка виклику callback: {e}")
        
        return alert_data
    
    def get_monitoring_status(self) -> Dict:
        """Отримання статусу моніторингу"""
        uptime = None
        if self.stats['uptime_start']:
            uptime = str(datetime.now() - self.stats['uptime_start'])
        
        return {
            'is_active': self.is_monitoring,
            'monitored_chats': self.stats['total_monitored'],
            'messages_processed': self.stats['messages_processed'],
            'alerts_triggered': self.stats['alerts_triggered'],
            'uptime': uptime,
            'settings': self.settings
        }
    
    def format_status_report(self) -> str:
        """Форматування звіту статусу"""
        status = self.get_monitoring_status()
        
        status_emoji = "🟢" if status['is_active'] else "🔴"
        
        return f"""<b>📡 СТАТУС МОНІТОРИНГУ</b>
═══════════════════════

{status_emoji} <b>Стан:</b> {'Активний' if status['is_active'] else 'Зупинений'}

<b>📊 СТАТИСТИКА:</b>
├ Чатів під моніторингом: {status['monitored_chats']}
├ Оброблено повідомлень: {status['messages_processed']}
├ Спрацювань тривоги: {status['alerts_triggered']}
└ Час роботи: {status['uptime'] or 'N/A'}

<b>⚙️ НАЛАШТУВАННЯ:</b>
├ Інтервал перевірки: {status['settings']['check_interval']} сек
├ Поріг загрози: {status['settings']['threat_threshold']}
└ Розмір кешу: {status['settings']['max_hash_cache']}"""
    
    def update_settings(self, **kwargs):
        """Оновлення налаштувань"""
        for key, value in kwargs.items():
            if key in self.settings:
                self.settings[key] = value
                logger.info(f"Налаштування {key} оновлено: {value}")


def initialize_realtime_with_client(client=None):
    """Ініціалізація realtime парсера з клієнтом"""
    if client:
        realtime_parser.set_client(client)
        logger.info("RealTime Parser initialized with Telethon client")
        return True
    
    import os
    from core.osint_telethon import TelethonOSINT
    
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    
    if api_id and api_hash:
        try:
            osint = TelethonOSINT(int(api_id), api_hash)
            if osint.client:
                realtime_parser.set_client(osint.client)
                logger.info("RealTime Parser initialized with Telethon client")
                return True
        except Exception as e:
            logger.error(f"Failed to initialize realtime parser: {e}")
    
    logger.warning("Telethon client not available for RealTime Parser")
    return False


realtime_parser = RealTimeParser()
