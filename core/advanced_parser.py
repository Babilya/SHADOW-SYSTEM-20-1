"""
Advanced Telegram Parser - Глибокий парсинг та OSINT аналіз
Модуль для комплексного парсингу чатів, учасників, повідомлень з аналізом загроз
"""
import asyncio
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ParsedMessage:
    """Структура для збереження розібраних повідомлень"""
    id: int
    date: datetime
    sender_id: int
    sender_username: Optional[str]
    text: str
    media_type: Optional[str]
    views: int
    forwards: int
    replies: Optional[int]
    edit_date: Optional[datetime]
    contains_coordinates: bool = False
    contains_keywords: List[str] = field(default_factory=list)
    threat_level: int = 0


class AdvancedTelegramParser:
    """Розширений парсер Telegram даних"""
    
    def __init__(self, client=None):
        self.client = client
        self.parsed_data = {
            'chats': {},
            'users': {},
            'messages': [],
            'statistics': defaultdict(int)
        }
        
        self.patterns = {
            'coordinates': [
                r'\b(\d{2}\.\d{4,6}),\s*(\d{2,3}\.\d{4,6})\b',
                r'\b(\d{2})°(\d{2})\'(\d{2})"[NS]\s*(\d{2})°(\d{2})\'(\d{2})"[EW]\b',
                r'\b[A-R]{2}\d{2}[a-x]{2}\b',
            ],
            'phone_numbers': r'[\+\(]?[1-9][0-9\-\(\)\.]{8,}\d',
            'crypto_wallets': r'\b(0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})\b',
            'explosives': ['тнт', 'динаміт', 'детонатор', 'запал', 'вибухівка', 'порох'],
            'weapons': ['автомат', 'гранатомет', 'снайпер', 'rpg', 'танк', 'бтр'],
            'military_terms': ['координати', 'азимут', 'зсу', 'рф', 'рота', 'взвод'],
            'threats': ['вбивство', 'теракт', 'атака', 'удар', 'бомба', 'вибух']
        }
        
        self.parse_stats = {
            'total_parsed': 0,
            'high_threat': 0,
            'with_coordinates': 0,
            'with_media': 0
        }
    
    async def parse_chat_deep(self, chat_identifier, limit: int = 5000) -> Dict:
        """Глибокий парсинг чату з повним аналізом"""
        if not self.client:
            return {'error': 'Client not initialized'}
        
        try:
            entity = await self.client.get_entity(chat_identifier)
            
            chat_data = {
                'id': entity.id,
                'title': getattr(entity, 'title', 'Unknown'),
                'username': getattr(entity, 'username', None),
                'participants_count': getattr(entity, 'participants_count', 0),
                'date_created': getattr(entity, 'date', None),
                'scam': getattr(entity, 'scam', False),
                'verified': getattr(entity, 'verified', False),
                'access_hash': getattr(entity, 'access_hash', None)
            }
            
            self.parsed_data['chats'][entity.id] = chat_data
            
            participants = await self.parse_participants(entity, limit=200)
            messages = await self.parse_messages(entity, limit=limit)
            interaction_graph = self.build_interaction_graph(messages, participants)
            activity_analysis = self.analyze_activity(messages)
            key_persons = self.identify_key_persons(interaction_graph, messages)
            
            return {
                'chat_info': chat_data,
                'participants_count': len(participants),
                'messages_count': len(messages),
                'time_range': self.get_time_range(messages),
                'activity_analysis': activity_analysis,
                'key_persons': key_persons,
                'interaction_graph': interaction_graph,
                'threat_assessment': self.assess_threat_level(messages, participants)
            }
            
        except Exception as e:
            logger.error(f"Помилка парсингу чату {chat_identifier}: {e}")
            return {'error': str(e)}
    
    async def parse_participants(self, entity, limit: int = 200) -> List[Dict]:
        """Парсинг учасників чату з детальною інформацією"""
        participants_data = []
        
        if not self.client:
            return participants_data
        
        try:
            participants = await self.client.get_participants(entity, limit=limit, aggressive=True)
            
            for user in participants:
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': user.phone,
                    'bot': user.bot,
                    'verified': user.verified,
                    'scam': user.scam,
                    'fake': getattr(user, 'fake', False),
                    'restricted': user.restricted,
                    'status': str(user.status) if user.status else None,
                    'last_seen': self.parse_last_seen(user.status),
                    'photo': bool(user.photo),
                    'premium': getattr(user, 'premium', False),
                    'risk_score': self.calculate_user_risk_score(user)
                }
                
                participants_data.append(user_data)
                self.parsed_data['users'][user.id] = user_data
                
            return participants_data
            
        except Exception as e:
            logger.error(f"Помилка парсингу учасників: {e}")
            return []
    
    async def parse_messages(self, entity, limit: int = 5000) -> List[ParsedMessage]:
        """Парсинг повідомлень з детальним аналізом"""
        messages_data = []
        
        if not self.client:
            return messages_data
        
        try:
            async for message in self.client.iter_messages(entity, limit=limit):
                parsed_msg = self.parse_single_message(message)
                messages_data.append(parsed_msg)
                
                self.parse_stats['total_parsed'] += 1
                if parsed_msg.threat_level > 50:
                    self.parse_stats['high_threat'] += 1
                if parsed_msg.contains_coordinates:
                    self.parse_stats['with_coordinates'] += 1
                if parsed_msg.media_type:
                    self.parse_stats['with_media'] += 1
                
                if self.parse_stats['total_parsed'] % 100 == 0:
                    logger.info(f"📥 Парсинг: {self.parse_stats['total_parsed']} повідомлень")
                    
        except Exception as e:
            logger.error(f"Помилка парсингу повідомлень: {e}")
        
        return messages_data
    
    def parse_single_message(self, message) -> ParsedMessage:
        """Детальний парсинг одного повідомлення"""
        text = message.message or '' if hasattr(message, 'message') else ''
        
        parsed = ParsedMessage(
            id=message.id,
            date=message.date,
            sender_id=getattr(message, 'sender_id', 0) or 0,
            sender_username=None,
            text=text,
            media_type=self.get_media_type(message.media) if hasattr(message, 'media') and message.media else None,
            views=getattr(message, 'views', 0) or 0,
            forwards=getattr(message, 'forwards', 0) or 0,
            replies=message.replies.replies if hasattr(message, 'replies') and message.replies else 0,
            edit_date=getattr(message, 'edit_date', None)
        )
        
        parsed.contains_keywords = self.find_keywords_in_text(text)
        parsed.contains_coordinates = self.find_coordinates_in_text(text)
        parsed.threat_level = self.calculate_threat_level(parsed)
        
        return parsed
    
    def get_media_type(self, media) -> Optional[str]:
        """Визначення типу медіа"""
        if not media:
            return None
        media_class = type(media).__name__
        media_types = {
            'MessageMediaPhoto': 'photo',
            'MessageMediaDocument': 'document',
            'MessageMediaVideo': 'video',
            'MessageMediaGeo': 'geo',
            'MessageMediaVenue': 'venue',
            'MessageMediaContact': 'contact',
            'MessageMediaWebPage': 'webpage'
        }
        return media_types.get(media_class, 'unknown')
    
    def find_coordinates_in_text(self, text: str) -> bool:
        """Пошук координат у тексті"""
        for pattern in self.patterns['coordinates']:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def find_keywords_in_text(self, text: str) -> List[str]:
        """Пошук ключових слів у тексті"""
        found_keywords = []
        text_lower = text.lower()
        
        for category, keywords in self.patterns.items():
            if category in ['coordinates', 'phone_numbers', 'crypto_wallets']:
                continue
            
            if isinstance(keywords, list):
                for keyword in keywords:
                    if keyword in text_lower:
                        found_keywords.append(f"{category}:{keyword}")
        
        return found_keywords
    
    def calculate_threat_level(self, message: ParsedMessage) -> int:
        """Розрахунок рівня загрози повідомлення"""
        threat_score = 0
        
        if message.contains_coordinates:
            threat_score += 50
        
        if message.contains_keywords:
            threat_score += len(message.contains_keywords) * 10
        
        if message.media_type:
            threat_score += 20
        
        if message.edit_date:
            threat_score += 15
        
        return min(threat_score, 100)
    
    def calculate_user_risk_score(self, user) -> int:
        """Розрахунок ризику користувача"""
        risk = 0
        
        if getattr(user, 'scam', False):
            risk += 50
        if getattr(user, 'fake', False):
            risk += 40
        if getattr(user, 'restricted', False):
            risk += 30
        if not getattr(user, 'username', None):
            risk += 10
        if not getattr(user, 'photo', None):
            risk += 5
        
        return min(risk, 100)
    
    def parse_last_seen(self, status) -> Optional[str]:
        """Парсинг статусу останнього входу"""
        if not status:
            return None
        
        status_class = type(status).__name__
        
        if status_class == 'UserStatusOnline':
            return 'online'
        elif status_class == 'UserStatusRecently':
            return 'recently'
        elif status_class == 'UserStatusLastWeek':
            return 'last_week'
        elif status_class == 'UserStatusLastMonth':
            return 'last_month'
        elif status_class == 'UserStatusOffline':
            if hasattr(status, 'was_online'):
                return status.was_online.isoformat()
        
        return None
    
    def build_interaction_graph(self, messages: List[ParsedMessage], participants: List[Dict]) -> Dict:
        """Побудова графа взаємодій між користувачами"""
        graph = {
            'nodes': [],
            'edges': [],
            'centrality': {}
        }
        
        for user in participants:
            graph['nodes'].append({
                'id': user['id'],
                'label': user.get('username') or user.get('first_name', str(user['id'])),
                'group': 'participant',
                'risk_score': user.get('risk_score', 0),
                'messages_count': 0,
                'influence': 0
            })
        
        user_message_counts = defaultdict(int)
        
        for msg in messages:
            sender_id = msg.sender_id
            user_message_counts[sender_id] += 1
        
        total_messages = len(messages)
        for node in graph['nodes']:
            user_id = node['id']
            msg_count = user_message_counts.get(user_id, 0)
            
            node['messages_count'] = msg_count
            node['influence'] = (msg_count / total_messages * 100) if total_messages > 0 else 0
            graph['centrality'][user_id] = node['influence']
        
        return graph
    
    def identify_key_persons(self, graph: Dict, messages: List[ParsedMessage]) -> List[Dict]:
        """Ідентифікація ключових осіб у чаті"""
        if not graph['nodes']:
            return []
        
        sorted_nodes = sorted(
            graph['nodes'],
            key=lambda x: x['influence'],
            reverse=True
        )
        
        key_persons = []
        for node in sorted_nodes[:10]:
            user_messages = [m for m in messages if m.sender_id == node['id']]
            high_threat_messages = [m for m in user_messages if m.threat_level > 50]
            
            key_persons.append({
                'user_id': node['id'],
                'username': node['label'],
                'influence_score': node['influence'],
                'messages_count': node['messages_count'],
                'high_threat_messages': len(high_threat_messages),
                'average_threat_level': sum(m.threat_level for m in user_messages) / len(user_messages) if user_messages else 0,
                'last_active': max(m.date for m in user_messages).isoformat() if user_messages else None
            })
        
        return key_persons
    
    def analyze_activity(self, messages: List[ParsedMessage]) -> Dict:
        """Аналіз активності в чаті"""
        if not messages:
            return {'error': 'No messages to analyze'}
        
        hourly = defaultdict(int)
        daily = defaultdict(int)
        
        for msg in messages:
            if msg.date:
                hourly[msg.date.hour] += 1
                daily[msg.date.strftime('%A')] += 1
        
        peak_hour = max(hourly, key=hourly.get) if hourly else 0
        peak_day = max(daily, key=daily.get) if daily else 'Unknown'
        
        return {
            'total_messages': len(messages),
            'hourly_distribution': dict(hourly),
            'daily_distribution': dict(daily),
            'peak_hour': peak_hour,
            'peak_day': peak_day,
            'avg_messages_per_day': len(messages) / max(len(daily), 1)
        }
    
    def assess_threat_level(self, messages: List[ParsedMessage], participants: List[Dict]) -> Dict:
        """Оцінка рівня загрози чату"""
        high_threat = sum(1 for m in messages if m.threat_level > 50)
        with_coords = sum(1 for m in messages if m.contains_coordinates)
        risky_users = sum(1 for u in participants if u.get('risk_score', 0) > 30)
        
        threat_score = 0
        if len(messages) > 0:
            threat_score += (high_threat / len(messages)) * 40
        if with_coords > 0:
            threat_score += min(with_coords * 5, 30)
        if len(participants) > 0:
            threat_score += (risky_users / len(participants)) * 30
        
        if threat_score > 70:
            level = 'CRITICAL'
        elif threat_score > 50:
            level = 'HIGH'
        elif threat_score > 30:
            level = 'MEDIUM'
        else:
            level = 'LOW'
        
        return {
            'threat_score': round(threat_score, 2),
            'level': level,
            'high_threat_messages': high_threat,
            'messages_with_coordinates': with_coords,
            'risky_users': risky_users,
            'recommendation': self.get_threat_recommendation(level)
        }
    
    def get_threat_recommendation(self, level: str) -> str:
        """Рекомендації на основі рівня загрози"""
        recommendations = {
            'CRITICAL': 'Терміново передати інформацію оперативникам. Увімкнути моніторинг у реальному часі.',
            'HIGH': 'Рекомендовано детальний аналіз та ідентифікацію ключових осіб.',
            'MEDIUM': 'Продовжити моніторинг. Зберегти докази.',
            'LOW': 'Чат не становить значної загрози. Періодичний моніторинг.'
        }
        return recommendations.get(level, 'Невідомий рівень загрози')
    
    def get_time_range(self, messages: List[ParsedMessage]) -> Dict:
        """Отримання часового діапазону повідомлень"""
        if not messages:
            return {'start': None, 'end': None, 'duration_days': 0}
        
        dates = [m.date for m in messages if m.date]
        if not dates:
            return {'start': None, 'end': None, 'duration_days': 0}
        
        start = min(dates)
        end = max(dates)
        duration = (end - start).days
        
        return {
            'start': start.isoformat(),
            'end': end.isoformat(),
            'duration_days': duration
        }
    
    def format_analysis_report(self, analysis: Dict) -> str:
        """Форматування звіту аналізу"""
        if 'error' in analysis:
            return f"❌ Помилка: {analysis['error']}"
        
        chat = analysis.get('chat_info', {})
        threat = analysis.get('threat_assessment', {})
        activity = analysis.get('activity_analysis', {})
        
        threat_emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(threat.get('level', ''), '⚪')
        
        report = f"""<b>📊 ЗВІТ ГЛИБОКОГО АНАЛІЗУ</b>
═══════════════════════

<b>🔍 ЧАТ:</b>
├ Назва: <code>{chat.get('title', 'N/A')}</code>
├ ID: <code>{chat.get('id', 'N/A')}</code>
├ Учасників: {analysis.get('participants_count', 0)}
└ Повідомлень: {analysis.get('messages_count', 0)}

<b>{threat_emoji} РІВЕНЬ ЗАГРОЗИ: {threat.get('level', 'N/A')}</b>
├ Бал: {threat.get('threat_score', 0)}/100
├ Загрозливих повідомлень: {threat.get('high_threat_messages', 0)}
├ З координатами: {threat.get('messages_with_coordinates', 0)}
└ Ризикових юзерів: {threat.get('risky_users', 0)}

<b>📈 АКТИВНІСТЬ:</b>
├ Пік години: {activity.get('peak_hour', 'N/A')}:00
├ Пік дня: {activity.get('peak_day', 'N/A')}
└ Середнє/день: {activity.get('avg_messages_per_day', 0):.1f}

<b>💡 РЕКОМЕНДАЦІЯ:</b>
{threat.get('recommendation', 'N/A')}"""
        
        key_persons = analysis.get('key_persons', [])[:5]
        if key_persons:
            report += "\n\n<b>👤 КЛЮЧОВІ ОСОБИ:</b>"
            for i, person in enumerate(key_persons, 1):
                report += f"\n{i}. @{person['username']} - вплив: {person['influence_score']:.1f}%"
        
        return report
    
    def get_statistics(self) -> Dict:
        """Отримання статистики парсингу"""
        return {
            'parsed_chats': len(self.parsed_data['chats']),
            'parsed_users': len(self.parsed_data['users']),
            'parsed_messages': self.parse_stats['total_parsed'],
            'high_threat_messages': self.parse_stats['high_threat'],
            'with_coordinates': self.parse_stats['with_coordinates'],
            'with_media': self.parse_stats['with_media']
        }


def initialize_parsers_with_client():
    """Ініціалізація парсерів з Telethon клієнтом"""
    import os
    from core.osint_telethon import TelethonOSINT
    
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    
    if api_id and api_hash:
        try:
            osint = TelethonOSINT(int(api_id), api_hash)
            if osint.client:
                advanced_parser.client = osint.client
                logger.info("Advanced Parser initialized with Telethon client")
                return True
        except Exception as e:
            logger.error(f"Failed to initialize parser with Telethon: {e}")
    
    logger.warning("Telethon client not available for Advanced Parser")
    return False


advanced_parser = AdvancedTelegramParser()
