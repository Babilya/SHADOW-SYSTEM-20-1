"""
Spam Analyzer - Аналіз тексту на спам перед розсилкою
Розрахунок спам-рейтингу та рекомендації
"""
import re
from typing import Dict, List
from collections import Counter


class SpamAnalyzer:
    """Аналіз тексту на спам"""
    
    SPAM_KEYWORDS = [
        'безкоштовно', 'акція', 'знижка', 'терміново', 'виграш',
        'приз', 'подарунок', 'переможець', 'вітаємо', 'бонус',
        'гроші', 'заробіток', 'інвестиції', 'криптовалюта'
    ]
    
    STOP_WORDS_UA = [
        'і', 'та', 'в', 'на', 'з', 'у', 'до', 'від', 'за', 'про',
        'що', 'як', 'це', 'той', 'ця', 'для', 'при', 'по', 'не'
    ]
    
    def calculate_spam_score(self, message_text: str) -> Dict:
        """Розрахунок спам-рейтингу"""
        scores = {
            'caps_ratio': self._check_caps_ratio(message_text),
            'link_density': self._check_link_density(message_text),
            'keyword_density': self._check_keyword_density(message_text),
            'length_score': self._check_length(message_text),
            'special_chars': self._check_special_chars(message_text),
            'emoji_density': self._check_emoji_density(message_text)
        }
        
        weights = {
            'caps_ratio': 0.2,
            'link_density': 0.25,
            'keyword_density': 0.2,
            'length_score': 0.1,
            'special_chars': 0.1,
            'emoji_density': 0.15
        }
        
        total_score = sum(scores[k] * weights[k] for k in scores) * 100
        
        recommendations = self._generate_recommendations(scores)
        
        return {
            'score': round(total_score, 1),
            'breakdown': scores,
            'recommendations': recommendations,
            'risk_level': self._get_risk_level(total_score)
        }
    
    def _check_caps_ratio(self, text: str) -> float:
        """Перевірка співвідношення великих літер"""
        letters = [c for c in text if c.isalpha()]
        if not letters:
            return 0
        caps = sum(1 for c in letters if c.isupper())
        return caps / len(letters)
    
    def _check_link_density(self, text: str) -> float:
        """Перевірка щільності посилань"""
        url_pattern = r'https?://\S+'
        urls = re.findall(url_pattern, text)
        words = text.split()
        if not words:
            return 0
        return min(1.0, len(urls) / len(words) * 10)
    
    def _check_keyword_density(self, text: str) -> float:
        """Перевірка щільності спам-слів"""
        text_lower = text.lower()
        found = sum(1 for kw in self.SPAM_KEYWORDS if kw in text_lower)
        words = len(text.split())
        if not words:
            return 0
        return min(1.0, found / words * 5)
    
    def _check_length(self, text: str) -> float:
        """Перевірка довжини повідомлення"""
        length = len(text)
        if length < 50:
            return 0.3
        elif length > 2000:
            return 0.8
        elif length > 1000:
            return 0.4
        return 0.1
    
    def _check_special_chars(self, text: str) -> float:
        """Перевірка спеціальних символів"""
        special = sum(1 for c in text if c in '!?$€₴%&*#@')
        if not text:
            return 0
        return min(1.0, special / len(text) * 10)
    
    def _check_emoji_density(self, text: str) -> float:
        """Перевірка щільності емодзі"""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", 
            flags=re.UNICODE
        )
        emojis = emoji_pattern.findall(text)
        words = len(text.split())
        if not words:
            return 0
        return min(1.0, len(emojis) / words * 3)
    
    def _generate_recommendations(self, scores: Dict) -> List[str]:
        """Генерація рекомендацій"""
        recs = []
        
        if scores['caps_ratio'] > 0.3:
            recs.append("⚠️ Зменшіть кількість ВЕЛИКИХ ЛІТЕР")
        if scores['link_density'] > 0.2:
            recs.append("⚠️ Зменшіть кількість посилань")
        if scores['keyword_density'] > 0.15:
            recs.append("⚠️ Уникайте спам-слів (безкоштовно, акція)")
        if scores['special_chars'] > 0.3:
            recs.append("⚠️ Зменшіть кількість спецсимволів (!?$)")
        if scores['emoji_density'] > 0.4:
            recs.append("⚠️ Зменшіть кількість емодзі")
        if scores['length_score'] > 0.6:
            recs.append("⚠️ Скоротіть повідомлення")
        
        if not recs:
            recs.append("✅ Текст виглядає добре")
        
        return recs
    
    def _get_risk_level(self, score: float) -> str:
        """Визначення рівня ризику"""
        if score >= 70:
            return 'HIGH'
        elif score >= 40:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def pre_send_analysis(self, campaign_data: Dict) -> List[Dict]:
        """Аналіз перед відправкою кампанії"""
        warnings = []
        
        messages = campaign_data.get('messages', [])
        for i, message in enumerate(messages):
            text = message.get('text', '')
            spam_result = self.calculate_spam_score(text)
            
            if spam_result['risk_level'] in ['HIGH', 'MEDIUM']:
                warnings.append({
                    'message_index': i,
                    'text_preview': text[:50] + '...' if len(text) > 50 else text,
                    'spam_score': spam_result['score'],
                    'risk_level': spam_result['risk_level'],
                    'recommendations': spam_result['recommendations']
                })
        
        frequency = campaign_data.get('sending_frequency', 0)
        if frequency > 10:
            warnings.append({
                'type': 'frequency',
                'issue': 'Занадто висока частота відправки',
                'recommendation': f'Зменшити з {frequency} до 5 повідомлень/годину'
            })
        
        return warnings
    
    def format_analysis_report(self, result: Dict) -> str:
        """Форматування звіту аналізу"""
        risk_emoji = {
            'HIGH': '🔴',
            'MEDIUM': '🟡',
            'LOW': '🟢'
        }
        
        report = [
            "<b>📊 АНАЛІЗ СПАМУ</b>",
            "═══════════════════════",
            f"Загальний бал: {result['score']}/100",
            f"Рівень ризику: {risk_emoji.get(result['risk_level'], '⚪')} {result['risk_level']}",
            "",
            "<b>Деталі:</b>"
        ]
        
        breakdown = result['breakdown']
        report.append(f"├ Великі літери: {int(breakdown['caps_ratio']*100)}%")
        report.append(f"├ Посилання: {int(breakdown['link_density']*100)}%")
        report.append(f"├ Спам-слова: {int(breakdown['keyword_density']*100)}%")
        report.append(f"├ Спецсимволи: {int(breakdown['special_chars']*100)}%")
        report.append(f"└ Емодзі: {int(breakdown['emoji_density']*100)}%")
        
        if result['recommendations']:
            report.append("")
            report.append("<b>Рекомендації:</b>")
            for rec in result['recommendations']:
                report.append(rec)
        
        return '\n'.join(report)


spam_analyzer = SpamAnalyzer()
