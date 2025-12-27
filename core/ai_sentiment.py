"""
AI Sentiment Analysis - Модуль аналізу настрою
Використовує OpenAI для глибокого аналізу емоцій та тональності повідомлень
"""

import asyncio
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import logging
import os

logger = logging.getLogger(__name__)

@dataclass
class SentimentResult:
    """Результат аналізу настрою"""
    text: str
    sentiment: str  # positive, negative, neutral, mixed
    confidence: float
    emotions: Dict[str, float] = field(default_factory=dict)
    toxicity_score: float = 0.0
    spam_probability: float = 0.0
    language: str = "uk"
    keywords: List[str] = field(default_factory=list)
    intent: str = ""
    summary: str = ""


class AISentimentAnalyzer:
    """AI-базований аналізатор настрою"""
    
    EMOTION_KEYWORDS = {
        "positive": ["дякую", "чудово", "супер", "відмінно", "класно", "радий", "щасливий", "любов", "найкращий"],
        "negative": ["поганий", "жахливо", "розчарований", "злий", "ненавиджу", "проблема", "скарга", "обман"],
        "neutral": ["добре", "ок", "зрозумів", "так", "ні", "можливо", "буде"],
        "urgent": ["терміново", "швидко", "негайно", "критично", "важливо", "термін"],
        "question": ["як", "чому", "коли", "де", "хто", "що", "скільки", "?"]
    }
    
    TOXIC_PATTERNS = [
        r'\b(ідіот|дурень|придурок|лох|урод)\b',
        r'\b(обман|шахрай|кидалово|розвод)\b',
        r'[А-ЯІЇЄ]{5,}',  # Капс
    ]
    
    def __init__(self):
        self.analysis_cache: Dict[str, SentimentResult] = {}
        self.stats = {
            "total_analyzed": 0,
            "by_sentiment": {"positive": 0, "negative": 0, "neutral": 0, "mixed": 0},
            "avg_toxicity": 0.0,
            "total_toxicity": 0.0
        }
        self._openai_client = None
    
    def _get_openai_client(self):
        """Ініціалізація OpenAI клієнта"""
        if self._openai_client is None:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
                if api_key:
                    self._openai_client = OpenAI(api_key=api_key)
            except Exception as e:
                logger.warning(f"OpenAI not available: {e}")
        return self._openai_client
    
    async def analyze_sentiment(self, text: str, use_ai: bool = True) -> SentimentResult:
        """Аналіз настрою тексту"""
        if not text or not text.strip():
            return SentimentResult(
                text="",
                sentiment="neutral",
                confidence=0.0
            )
        
        cache_key = hash(text[:100])
        if cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]
        
        basic_result = self._basic_analysis(text)
        
        if use_ai and self._get_openai_client():
            try:
                ai_result = await self._ai_analysis(text, basic_result)
                result = ai_result
            except Exception as e:
                logger.warning(f"AI analysis failed: {e}")
                result = basic_result
        else:
            result = basic_result
        
        self.analysis_cache[cache_key] = result
        self._update_stats(result)
        
        return result
    
    def _basic_analysis(self, text: str) -> SentimentResult:
        """Базовий аналіз на основі ключових слів"""
        text_lower = text.lower()
        
        scores = {"positive": 0, "negative": 0, "neutral": 0}
        keywords_found = []
        
        for sentiment, words in self.EMOTION_KEYWORDS.items():
            if sentiment in ["urgent", "question"]:
                continue
            for word in words:
                if word in text_lower:
                    scores[sentiment] += 1
                    keywords_found.append(word)
        
        toxicity = self._calculate_toxicity(text)
        spam_prob = self._calculate_spam_probability(text)
        
        total = sum(scores.values())
        if total == 0:
            sentiment = "neutral"
            confidence = 0.5
        else:
            sentiment = max(scores, key=scores.get)
            confidence = scores[sentiment] / total
        
        emotions = {
            "joy": scores["positive"] / max(total, 1),
            "anger": min(toxicity, 1.0),
            "sadness": scores["negative"] / max(total, 1) * 0.5,
            "fear": 0.0,
            "surprise": 0.0
        }
        
        intent = "question" if "?" in text or any(w in text_lower for w in self.EMOTION_KEYWORDS["question"]) else "statement"
        if any(w in text_lower for w in self.EMOTION_KEYWORDS["urgent"]):
            intent = "urgent_request"
        
        return SentimentResult(
            text=text[:200],
            sentiment=sentiment,
            confidence=round(confidence, 2),
            emotions=emotions,
            toxicity_score=round(toxicity, 2),
            spam_probability=round(spam_prob, 2),
            language="uk",
            keywords=keywords_found[:10],
            intent=intent,
            summary=f"{'Позитивний' if sentiment == 'positive' else 'Негативний' if sentiment == 'negative' else 'Нейтральний'} настрій"
        )
    
    async def _ai_analysis(self, text: str, basic: SentimentResult) -> SentimentResult:
        """AI аналіз через OpenAI"""
        client = self._get_openai_client()
        if not client:
            return basic
        
        prompt = f"""Проаналізуй настрій цього тексту українською мовою.
Текст: "{text[:500]}"

Відповідь у форматі JSON:
{{
    "sentiment": "positive/negative/neutral/mixed",
    "confidence": 0.0-1.0,
    "emotions": {{"joy": 0.0-1.0, "anger": 0.0-1.0, "sadness": 0.0-1.0}},
    "intent": "question/statement/request/complaint",
    "summary": "короткий опис"
}}"""
        
        try:
            response = await asyncio.to_thread(
                lambda: client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.3
                )
            )
            
            content = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                
                return SentimentResult(
                    text=text[:200],
                    sentiment=data.get("sentiment", basic.sentiment),
                    confidence=float(data.get("confidence", basic.confidence)),
                    emotions=data.get("emotions", basic.emotions),
                    toxicity_score=basic.toxicity_score,
                    spam_probability=basic.spam_probability,
                    language="uk",
                    keywords=basic.keywords,
                    intent=data.get("intent", basic.intent),
                    summary=data.get("summary", basic.summary)
                )
        except Exception as e:
            logger.warning(f"AI parsing error: {e}")
        
        return basic
    
    def _calculate_toxicity(self, text: str) -> float:
        """Розрахунок токсичності"""
        score = 0.0
        
        for pattern in self.TOXIC_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            score += len(matches) * 0.3
        
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.5:
            score += 0.2
        
        if text.count('!') > 3:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_spam_probability(self, text: str) -> float:
        """Розрахунок ймовірності спаму"""
        score = 0.0
        
        if re.search(r'https?://', text):
            score += 0.2
        
        if re.search(r'@\w+', text):
            score += 0.1
        
        spam_words = ["безкоштовно", "виграш", "приз", "акція", "знижка", "термінов"]
        for word in spam_words:
            if word in text.lower():
                score += 0.15
        
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F]', text))
        if emoji_count > 5:
            score += 0.1
        
        return min(score, 1.0)
    
    async def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """Пакетний аналіз"""
        results = []
        for text in texts:
            result = await self.analyze_sentiment(text, use_ai=False)
            results.append(result)
        return results
    
    def _update_stats(self, result: SentimentResult):
        """Оновлення статистики"""
        self.stats["total_analyzed"] += 1
        self.stats["by_sentiment"][result.sentiment] = self.stats["by_sentiment"].get(result.sentiment, 0) + 1
        self.stats["total_toxicity"] += result.toxicity_score
        self.stats["avg_toxicity"] = self.stats["total_toxicity"] / self.stats["total_analyzed"]
    
    def get_stats(self) -> Dict:
        """Отримання статистики"""
        return self.stats
    
    def format_result(self, result: SentimentResult) -> str:
        """Форматування результату"""
        sentiment_icons = {
            "positive": "😊",
            "negative": "😞",
            "neutral": "😐",
            "mixed": "🤔"
        }
        
        intent_icons = {
            "question": "❓",
            "statement": "💬",
            "request": "📩",
            "complaint": "⚠️",
            "urgent_request": "🚨"
        }
        
        text = f"""<b>🧠 АНАЛІЗ НАСТРОЮ</b>

<b>📝 Текст:</b> <i>{result.text[:100]}...</i>

───────────────

<b>📊 РЕЗУЛЬТАТ:</b>
├ {sentiment_icons.get(result.sentiment, '❓')} Настрій: <b>{result.sentiment.upper()}</b>
├ 📈 Впевненість: <b>{result.confidence * 100:.0f}%</b>
├ ☣️ Токсичність: <b>{result.toxicity_score * 100:.0f}%</b>
├ 📧 Спам: <b>{result.spam_probability * 100:.0f}%</b>
└ {intent_icons.get(result.intent, '💬')} Інтент: <b>{result.intent}</b>

<b>💭 ЕМОЦІЇ:</b>"""
        
        for emotion, score in result.emotions.items():
            bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
            text += f"\n├ {emotion}: {bar} {score * 100:.0f}%"
        
        text += f"\n\n<b>📌 Резюме:</b> {result.summary}"
        
        return text
    
    def format_stats_report(self) -> str:
        """Форматування звіту статистики"""
        stats = self.get_stats()
        
        text = f"""<b>🧠 AI SENTIMENT ANALYZER</b>
<i>Статистика аналізу настроїв</i>

───────────────

<b>📊 ЗАГАЛЬНА СТАТИСТИКА:</b>
├ 📝 Проаналізовано: <b>{stats['total_analyzed']}</b>
└ ☣️ Сер. токсичність: <b>{stats['avg_toxicity'] * 100:.1f}%</b>

<b>📈 ПО НАСТРОЯХ:</b>"""
        
        for sentiment, count in stats["by_sentiment"].items():
            icon = {"positive": "😊", "negative": "😞", "neutral": "😐", "mixed": "🤔"}.get(sentiment, "❓")
            text += f"\n├ {icon} {sentiment}: <b>{count}</b>"
        
        return text


ai_sentiment = AISentimentAnalyzer()
