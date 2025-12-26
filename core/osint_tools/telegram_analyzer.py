import logging
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class TelegramAnalyzer:
    def __init__(self, api_id: Optional[int] = None, api_hash: Optional[str] = None, session_name: str = 'osint_session'):
        self.api_id = api_id or int(os.getenv("API_ID", "0"))
        self.api_hash = api_hash or os.getenv("API_HASH", "")
        self.session_name = session_name
        self.client = None
        
    async def connect(self):
        try:
            from telethon import TelegramClient
            self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
            await self.client.connect()
            return True
        except ImportError:
            logger.warning("Telethon not installed. Some features unavailable.")
            return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    async def disconnect(self):
        if self.client:
            await self.client.disconnect()
    
    async def analyze_public_channel(self, channel_link: str, limit: int = 100) -> Dict[str, Any]:
        if not self.client:
            return {"error": "Not connected"}
        
        try:
            channel = await self.client.get_entity(channel_link)
            participants = await self.client.get_participants(channel, limit=limit)
            
            data = []
            for user in participants:
                data.append({
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': user.phone,
                    'bot': user.bot,
                    'verified': user.verified,
                    'premium': getattr(user, 'premium', False)
                })
            
            return {
                "channel": channel_link,
                "participants_count": len(data),
                "users": data,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Channel analysis error: {e}")
            return {"error": str(e)}
    
    async def get_channel_metadata(self, channel_link: str) -> Dict[str, Any]:
        if not self.client:
            return {"error": "Not connected"}
        
        try:
            channel = await self.client.get_entity(channel_link)
            return {
                'title': channel.title,
                'id': channel.id,
                'participants_count': getattr(channel, 'participants_count', 0),
                'description': getattr(channel, 'about', ''),
                'date_created': str(channel.date) if hasattr(channel, 'date') else None,
                'username': getattr(channel, 'username', None),
                'verified': getattr(channel, 'verified', False),
                'scam': getattr(channel, 'scam', False),
                'fake': getattr(channel, 'fake', False)
            }
        except Exception as e:
            logger.error(f"Metadata error: {e}")
            return {"error": str(e)}
    
    async def search_messages(self, chat_link: str, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        if not self.client:
            return [{"error": "Not connected"}]
        
        try:
            chat = await self.client.get_entity(chat_link)
            messages = []
            
            async for message in self.client.iter_messages(chat, search=keyword, limit=limit):
                messages.append({
                    'id': message.id,
                    'text': message.text,
                    'date': str(message.date),
                    'sender_id': message.sender_id,
                    'views': getattr(message, 'views', 0),
                    'forwards': getattr(message, 'forwards', 0)
                })
            
            return messages
        except Exception as e:
            logger.error(f"Search error: {e}")
            return [{"error": str(e)}]
    
    async def get_user_info(self, username: str) -> Dict[str, Any]:
        if not self.client:
            return {"error": "Not connected"}
        
        try:
            user = await self.client.get_entity(username)
            return {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'bot': user.bot,
                'verified': user.verified,
                'scam': getattr(user, 'scam', False),
                'fake': getattr(user, 'fake', False),
                'premium': getattr(user, 'premium', False),
                'restricted': getattr(user, 'restricted', False),
                'status': str(user.status) if hasattr(user, 'status') else None
            }
        except Exception as e:
            logger.error(f"User info error: {e}")
            return {"error": str(e)}
    
    async def analyze_chat_activity(self, chat_link: str, days: int = 7) -> Dict[str, Any]:
        if not self.client:
            return {"error": "Not connected"}
        
        try:
            from datetime import timedelta
            chat = await self.client.get_entity(chat_link)
            
            since = datetime.now() - timedelta(days=days)
            messages_count = 0
            users_active = set()
            hours_activity = {}
            
            async for message in self.client.iter_messages(chat, offset_date=since, limit=1000):
                messages_count += 1
                if message.sender_id:
                    users_active.add(message.sender_id)
                hour = message.date.hour
                hours_activity[hour] = hours_activity.get(hour, 0) + 1
            
            peak_hours = sorted(hours_activity.items(), key=lambda x: x[1], reverse=True)[:3]
            
            return {
                'chat': chat_link,
                'period_days': days,
                'total_messages': messages_count,
                'unique_users': len(users_active),
                'avg_messages_per_day': round(messages_count / days, 1),
                'peak_hours': [h[0] for h in peak_hours],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Activity analysis error: {e}")
            return {"error": str(e)}

telegram_analyzer = TelegramAnalyzer()
