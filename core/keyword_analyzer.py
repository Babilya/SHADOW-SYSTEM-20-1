"""
Keyword Analyzer - Аналіз ключових слів та трендів
Хмари слів та сентимент-аналіз
"""
import re
import logging
from typing import Dict, List, Any, Optional
from collections import Counter
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class KeywordAnalyzer:
    """Аналіз та візуалізація ключових слів"""
    
    STOP_WORDS_UA = {
        'і', 'та', 'в', 'на', 'з', 'у', 'до', 'від', 'за', 'про',
        'що', 'як', 'це', 'той', 'ця', 'для', 'при', 'по', 'не',
        'так', 'але', 'або', 'чи', 'ні', 'він', 'вона', 'воно',
        'ми', 'ви', 'вони', 'їх', 'його', 'її', 'наш', 'ваш',
        'який', 'яка', 'яке', 'які', 'цей', 'ця', 'це', 'ці',
        'той', 'та', 'те', 'ті', 'все', 'всі', 'кожен', 'кожна'
    }
    
    STOP_WORDS_RU = {
        'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со',
        'как', 'а', 'то', 'все', 'она', 'так', 'его', 'но', 'да',
        'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только',
        'её', 'мне', 'было', 'вот', 'от', 'меня', 'ещё', 'нет',
        'о', 'из', 'ему', 'теперь', 'когда', 'уже', 'вам', 'ни'
    }
    
    SENTIMENT_POSITIVE = [
        'добре', 'чудово', 'відмінно', 'супер', 'клас', 'круто',
        'дякую', 'вдячний', 'радий', 'задоволений', 'любов',
        'хорошо', 'отлично', 'класс', 'спасибо', 'благодарю'
    ]
    
    SENTIMENT_NEGATIVE = [
        'погано', 'жахливо', 'огидно', 'ненавиджу', 'злий',
        'поганий', 'жах', 'біда', 'горе', 'страх', 'проблема',
        'плохо', 'ужасно', 'ненавижу', 'злой', 'проблема'
    ]
    
    def __init__(self):
        self.all_stop_words = self.STOP_WORDS_UA | self.STOP_WORDS_RU
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Повний аналіз тексту"""
        words = self._extract_words(text)
        filtered = self._filter_words(words)
        
        return {
            'total_words': len(words),
            'unique_words': len(set(words)),
            'filtered_words': len(filtered),
            'word_frequency': self._get_word_frequency(filtered),
            'top_keywords': self._get_top_keywords(filtered, 20),
            'sentiment': self._analyze_sentiment(text),
            'language': self._detect_language(text),
            'readability': self._calculate_readability(text)
        }
    
    def analyze_messages(self, messages: List[Dict]) -> Dict[str, Any]:
        """Аналіз списку повідомлень"""
        all_text = ' '.join(msg.get('text', '') for msg in messages)
        
        basic_analysis = self.analyze_text(all_text)
        
        time_analysis = self._analyze_time_distribution(messages)
        trending = self._identify_trending(messages)
        
        return {
            **basic_analysis,
            'message_count': len(messages),
            'time_distribution': time_analysis,
            'trending_words': trending
        }
    
    def _extract_words(self, text: str) -> List[str]:
        """Витяг слів з тексту"""
        text = text.lower()
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#\w+', '', text)
        words = re.findall(r'[\w\']+', text)
        return [w for w in words if len(w) > 2 and not w.isdigit()]
    
    def _filter_words(self, words: List[str]) -> List[str]:
        """Фільтрація стоп-слів"""
        return [w for w in words if w not in self.all_stop_words]
    
    def _get_word_frequency(self, words: List[str]) -> Dict[str, int]:
        """Підрахунок частоти слів"""
        return dict(Counter(words))
    
    def _get_top_keywords(self, words: List[str], n: int = 20) -> List[Dict]:
        """Отримання топ ключових слів"""
        counter = Counter(words)
        total = len(words)
        
        return [
            {
                'word': word,
                'count': count,
                'percentage': round(count / total * 100, 2) if total > 0 else 0
            }
            for word, count in counter.most_common(n)
        ]
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Аналіз сентименту тексту"""
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.SENTIMENT_POSITIVE if word in text_lower)
        negative_count = sum(1 for word in self.SENTIMENT_NEGATIVE if word in text_lower)
        
        total_sentiment = positive_count + negative_count
        if total_sentiment == 0:
            score = 0
            label = 'neutral'
        else:
            score = (positive_count - negative_count) / total_sentiment
            if score > 0.2:
                label = 'positive'
            elif score < -0.2:
                label = 'negative'
            else:
                label = 'neutral'
        
        return {
            'score': round(score, 2),
            'label': label,
            'positive_words': positive_count,
            'negative_words': negative_count
        }
    
    def _detect_language(self, text: str) -> str:
        """Визначення мови тексту"""
        ua_chars = len(re.findall(r'[іїєґ]', text.lower()))
        ru_chars = len(re.findall(r'[ыэъё]', text.lower()))
        
        if ua_chars > ru_chars:
            return 'uk'
        elif ru_chars > ua_chars:
            return 'ru'
        
        cyrillic = len(re.findall(r'[а-яА-Я]', text))
        latin = len(re.findall(r'[a-zA-Z]', text))
        
        if cyrillic > latin:
            return 'uk'
        return 'en'
    
    def _calculate_readability(self, text: str) -> Dict[str, Any]:
        """Розрахунок читабельності"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = self._extract_words(text)
        
        if not sentences or not words:
            return {'score': 0, 'level': 'unknown'}
        
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(w) for w in words) / len(words)
        
        score = 100 - (avg_sentence_length * 2) - (avg_word_length * 10)
        score = max(0, min(100, score))
        
        if score >= 70:
            level = 'easy'
        elif score >= 40:
            level = 'medium'
        else:
            level = 'hard'
        
        return {
            'score': round(score, 1),
            'level': level,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'avg_word_length': round(avg_word_length, 1)
        }
    
    def _analyze_time_distribution(self, messages: List[Dict]) -> Dict[str, int]:
        """Аналіз розподілу за часом"""
        hour_counts = Counter()
        
        for msg in messages:
            timestamp = msg.get('timestamp')
            if timestamp:
                if isinstance(timestamp, str):
                    try:
                        timestamp = datetime.fromisoformat(timestamp)
                    except:
                        continue
                if isinstance(timestamp, datetime):
                    hour_counts[timestamp.hour] += 1
        
        return dict(sorted(hour_counts.items()))
    
    def _identify_trending(self, messages: List[Dict]) -> List[Dict]:
        """Ідентифікація трендових слів"""
        if len(messages) < 10:
            return []
        
        mid_point = len(messages) // 2
        
        older = messages[:mid_point]
        newer = messages[mid_point:]
        
        older_words = Counter(self._filter_words(self._extract_words(
            ' '.join(m.get('text', '') for m in older)
        )))
        newer_words = Counter(self._filter_words(self._extract_words(
            ' '.join(m.get('text', '') for m in newer)
        )))
        
        trending = []
        for word, new_count in newer_words.most_common(50):
            old_count = older_words.get(word, 0)
            if old_count == 0:
                growth = new_count * 100
            else:
                growth = (new_count - old_count) / old_count * 100
            
            if growth > 50:
                trending.append({
                    'word': word,
                    'new_count': new_count,
                    'old_count': old_count,
                    'growth': round(growth, 1)
                })
        
        return sorted(trending, key=lambda x: x['growth'], reverse=True)[:10]
    
    def format_analysis_report(self, analysis: Dict) -> str:
        """Форматування звіту аналізу"""
        report = [
            "<b>📊 АНАЛІЗ КЛЮЧОВИХ СЛІВ</b>",
            "═══════════════════════",
            f"Всього слів: {analysis['total_words']}",
            f"Унікальних: {analysis['unique_words']}",
            f"Мова: {analysis['language'].upper()}",
            ""
        ]
        
        sentiment = analysis.get('sentiment', {})
        emoji = {'positive': '😊', 'negative': '😞', 'neutral': '😐'}
        report.append(f"<b>Сентимент:</b> {emoji.get(sentiment.get('label', 'neutral'), '❓')} {sentiment.get('label', 'N/A')}")
        report.append(f"Оцінка: {sentiment.get('score', 0)}")
        report.append("")
        
        report.append("<b>ТОП-10 слів:</b>")
        for kw in analysis.get('top_keywords', [])[:10]:
            report.append(f"├ {kw['word']}: {kw['count']} ({kw['percentage']}%)")
        
        readability = analysis.get('readability', {})
        if readability:
            report.append("")
            report.append(f"<b>Читабельність:</b> {readability.get('level', 'N/A')}")
            report.append(f"├ Бал: {readability.get('score', 0)}/100")
            report.append(f"├ Сер. довжина речення: {readability.get('avg_sentence_length', 0)}")
            report.append(f"└ Сер. довжина слова: {readability.get('avg_word_length', 0)}")
        
        trending = analysis.get('trending_words', [])
        if trending:
            report.append("")
            report.append("<b>📈 Тренди:</b>")
            for tw in trending[:5]:
                report.append(f"├ {tw['word']}: +{tw['growth']}%")
        
        return '\n'.join(report)


keyword_analyzer = KeywordAnalyzer()
