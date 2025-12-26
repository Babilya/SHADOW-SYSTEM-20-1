import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = None
        self._available = False
        self._init_client()
    
    def _init_client(self):
        try:
            from openai import OpenAI
            import os
            
            api_key = os.getenv("AI_INTEGRATIONS_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
            base_url = os.getenv("AI_INTEGRATIONS_OPENAI_BASE_URL")
            
            if api_key:
                if base_url:
                    self.client = OpenAI(api_key=api_key, base_url=base_url)
                    logger.info("AI Service initialized with Replit AI Integrations")
                else:
                    self.client = OpenAI(api_key=api_key)
                    logger.info("AI Service initialized with OpenAI API key")
                self._available = True
            else:
                logger.warning("OpenAI API key not found. AI features disabled.")
        except ImportError:
            logger.warning("OpenAI package not installed. AI features disabled.")
        except Exception as e:
            logger.error(f"AI Service init error: {e}")
    
    @property
    def is_available(self) -> bool:
        return self._available and self.client is not None
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        if not self.is_available:
            return self._fallback_sentiment(text)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Analyze the sentiment of the text. Return JSON with: sentiment (positive/negative/neutral), score (0-100), keywords (list of 5), summary (1 sentence in Ukrainian)."},
                    {"role": "user", "content": text}
                ],
                max_tokens=200
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            result['ai_powered'] = True
            result['timestamp'] = datetime.now().isoformat()
            return result
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return self._fallback_sentiment(text)
    
    def _fallback_sentiment(self, text: str) -> Dict[str, Any]:
        positive_words = ['добре', 'чудово', 'відмінно', 'дякую', 'супер', 'клас', 'топ', 'круто']
        negative_words = ['погано', 'жахливо', 'ні', 'відмова', 'скарга', 'проблема', 'помилка']
        
        text_lower = text.lower()
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        
        if pos_count > neg_count:
            sentiment = "positive"
            score = min(50 + pos_count * 10, 100)
        elif neg_count > pos_count:
            sentiment = "negative"
            score = max(50 - neg_count * 10, 0)
        else:
            sentiment = "neutral"
            score = 50
        
        return {
            'sentiment': sentiment,
            'score': score,
            'keywords': [],
            'summary': 'Базовий аналіз без AI',
            'ai_powered': False,
            'timestamp': datetime.now().isoformat()
        }
    
    async def generate_campaign_text(self, topic: str, style: str = "professional") -> str:
        if not self.is_available:
            return self._fallback_campaign_text(topic, style)
        
        try:
            styles = {
                "professional": "Напиши професійний маркетинговий текст",
                "friendly": "Напиши дружній та неформальний текст",
                "urgent": "Напиши терміновий та закликаючий до дії текст",
                "informative": "Напиши інформативний та детальний текст"
            }
            
            prompt = f"{styles.get(style, styles['professional'])} українською мовою на тему: {topic}. Максимум 200 символів."
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ви - експерт з копірайтингу для Telegram маркетингу."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Campaign text generation error: {e}")
            return self._fallback_campaign_text(topic, style)
    
    def _fallback_campaign_text(self, topic: str, style: str) -> str:
        templates = {
            "professional": f"🎯 {topic}\n\nОтримайте найкраще рішення для вашого бізнесу. Зв'яжіться з нами!",
            "friendly": f"Привіт! 👋\n\n{topic} - це саме те, що вам потрібно! Давайте поговоримо?",
            "urgent": f"⏰ ТЕРМІНОВО!\n\n{topic} - не пропустіть цю можливість! Діє обмежений час.",
            "informative": f"📌 {topic}\n\nДетальна інформація та консультація. Пишіть для деталей."
        }
        return templates.get(style, templates["professional"])
    
    async def analyze_audience(self, users_data: List[Dict]) -> Dict[str, Any]:
        if not users_data:
            return {'error': 'No data provided'}
        
        total = len(users_data)
        
        analysis = {
            'total_users': total,
            'demographics': {
                'with_username': sum(1 for u in users_data if u.get('username')),
                'with_phone': sum(1 for u in users_data if u.get('phone')),
                'bots': sum(1 for u in users_data if u.get('bot')),
                'premium': sum(1 for u in users_data if u.get('premium'))
            },
            'engagement_potential': 'high' if total > 1000 else 'medium' if total > 100 else 'low',
            'recommendations': [],
            'timestamp': datetime.now().isoformat()
        }
        
        if analysis['demographics']['bots'] / max(total, 1) > 0.1:
            analysis['recommendations'].append("⚠️ Високий відсоток ботів - рекомендуємо фільтрацію")
        
        if analysis['demographics']['premium'] / max(total, 1) > 0.05:
            analysis['recommendations'].append("✅ Хороший відсоток Premium користувачів")
        
        if not analysis['recommendations']:
            analysis['recommendations'].append("📊 Стандартна аудиторія для розсилки")
        
        return analysis
    
    async def suggest_best_time(self, timezone: str = "Europe/Kyiv") -> Dict[str, Any]:
        from datetime import datetime
        
        return {
            'recommended_times': [
                {'time': '09:00-10:00', 'engagement': 'high', 'reason': 'Початок робочого дня'},
                {'time': '12:00-13:00', 'engagement': 'medium', 'reason': 'Обідня перерва'},
                {'time': '18:00-19:00', 'engagement': 'high', 'reason': 'Кінець робочого дня'},
                {'time': '21:00-22:00', 'engagement': 'medium', 'reason': 'Вечірній час'}
            ],
            'avoid_times': ['03:00-07:00', '23:00-03:00'],
            'best_days': ['Tuesday', 'Wednesday', 'Thursday'],
            'timezone': timezone,
            'timestamp': datetime.now().isoformat()
        }
    
    async def generate_osint_report(self, target_info: Dict[str, Any]) -> str:
        if not self.is_available:
            return self._fallback_osint_report(target_info)
        
        try:
            prompt = f"""Проаналізуй інформацію про ціль та створи структурований OSINT звіт українською мовою:
Дані: {target_info}

Формат звіту:
1. Загальний профіль
2. Ризики та червоні прапорці  
3. Можливі зв'язки
4. Рекомендації для подальшого аналізу"""
            
            # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": "Ти - експерт з OSINT аналізу. Надавай структуровані звіти українською."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OSINT report generation error: {e}")
            return self._fallback_osint_report(target_info)
    
    def _fallback_osint_report(self, target_info: Dict[str, Any]) -> str:
        username = target_info.get('username', 'N/A')
        user_id = target_info.get('user_id', 'N/A')
        return f"""📊 OSINT ЗВІТ (базовий)

👤 Ціль: {username}
🆔 ID: {user_id}

⚠️ AI аналіз недоступний
Використовуйте ручний аналіз для детальних даних."""
    
    async def rewrite_message(self, text: str, style: str = "formal") -> str:
        if not self.is_available:
            return text
        
        try:
            styles_map = {
                "formal": "формально та професійно",
                "casual": "неформально та дружньо",
                "creative": "креативно з емоджі",
                "short": "коротко та лаконічно",
                "persuasive": "переконливо з закликом до дії"
            }
            
            style_desc = styles_map.get(style, styles_map["formal"])
            
            # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": f"Перепиши текст {style_desc}. Збережи головну думку. Українською мовою."},
                    {"role": "user", "content": text}
                ],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Message rewrite error: {e}")
            return text
    
    async def generate_funnel_step(self, funnel_name: str, step_number: int, goal: str) -> Dict[str, str]:
        if not self.is_available:
            return {
                "content": f"Крок {step_number} для воронки '{funnel_name}'",
                "button_text": "Далі ➡️"
            }
        
        try:
            # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": "Ти - експерт з маркетингових воронок. Генеруй контент для Telegram. Відповідай ТІЛЬКИ у форматі JSON."},
                    {"role": "user", "content": f"Створи крок #{step_number} для воронки '{funnel_name}' з метою: {goal}. Поверни JSON: {{\"content\": \"...\", \"button_text\": \"...\"}}"}
                ],
                max_tokens=300
            )
            
            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Funnel step generation error: {e}")
            return {
                "content": f"Крок {step_number} для воронки '{funnel_name}'",
                "button_text": "Далі ➡️"
            }
    
    async def analyze_chat_history(self, messages: List[str]) -> Dict[str, Any]:
        if not self.is_available or not messages:
            return {"summary": "AI аналіз недоступний", "topics": [], "sentiment": "neutral"}
        
        try:
            text = "\n".join(messages[:50])
            
            # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": "Проаналізуй історію чату. Відповідай ТІЛЬКИ у форматі JSON: {\"summary\": \"...\", \"topics\": [...], \"sentiment\": \"positive/negative/neutral\", \"key_insights\": [...]}"},
                    {"role": "user", "content": text}
                ],
                max_tokens=500
            )
            
            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Chat analysis error: {e}")
            return {"summary": "Помилка аналізу", "topics": [], "sentiment": "neutral"}
    
    async def generate_response_template(self, context: str, tone: str = "helpful") -> str:
        if not self.is_available:
            return "Дякуємо за ваше звернення! Ми зв'яжемося з вами найближчим часом."
        
        try:
            # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": f"Згенеруй шаблон відповіді для Telegram бота. Тон: {tone}. Українською мовою. Коротко."},
                    {"role": "user", "content": f"Контекст: {context}"}
                ],
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Response template error: {e}")
            return "Дякуємо за ваше звернення! Ми зв'яжемося з вами найближчим часом."

ai_service = AIService()
