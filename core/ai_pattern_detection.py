"""
AI-Enhanced Pattern Detection - Розширений аналіз загроз
Виявлення координат, кодів, шифрів та загроз з AI
"""
import re
import base64
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available for AI pattern detection")


class AIPatternDetector:
    """AI модель для виявлення прихованих загроз"""
    
    COORDINATE_PATTERNS = [
        (r'(\d{1,3})[°◦](\d{1,2})[\'\′](\d{1,2}(?:\.\d+)?)[″\"]\s*([NS])\s*(\d{1,3})[°◦](\d{1,2})[\'\′](\d{1,2}(?:\.\d+)?)[″\"]\s*([EW])', 'DMS'),
        (r'(-?\d{1,3}\.\d{4,})[,\s]+(-?\d{1,3}\.\d{4,})', 'Decimal'),
        (r'maps\.google\.com.*@(-?\d+\.\d+),(-?\d+\.\d+)', 'Google Maps'),
        (r'goo\.gl/maps/\w+', 'Google Maps Short'),
        (r'(\d{2}[A-Z])\s*([A-Z]{2})\s*(\d{5})\s*(\d{5})', 'MGRS'),
        (r'[A-Z]{2}\d{4}[A-Z]{2}', 'Military Grid'),
        (r'N\s*(\d{2})\s*(\d{2})\.\d+\s*E\s*(\d{2,3})\s*(\d{2})\.\d+', 'NMEA'),
    ]
    
    THREAT_KEYWORDS = {
        'critical': [
            'бомба', 'вибухівка', 'теракт', 'замінування', 'снаряд',
            'координати', 'позиція', 'дислокація', 'розташування'
        ],
        'high': [
            'зброя', 'набої', 'боєприпаси', 'ракета', 'дрон',
            'артилерія', 'танк', 'бтр', 'військовий'
        ],
        'medium': [
            'блокпост', 'патруль', 'техніка', 'колона', 'конвой',
            'база', 'склад', 'казарма', 'штаб'
        ],
        'low': [
            'солдат', 'військовослужбовець', 'офіцер', 'командир'
        ]
    }
    
    CRYPTO_PATTERNS = [
        (r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b', 'BTC'),
        (r'\b0x[a-fA-F0-9]{40}\b', 'ETH'),
        (r'\bT[A-Za-z1-9]{33}\b', 'USDT-TRC20'),
    ]
    
    PHONE_PATTERNS = [
        (r'\+380\d{9}', 'Ukraine'),
        (r'\+7\d{10}', 'Russia'),
        (r'\+375\d{9}', 'Belarus'),
        (r'\+48\d{9}', 'Poland'),
    ]
    
    def __init__(self):
        self.client = None
        if OPENAI_AVAILABLE:
            try:
                self.client = OpenAI()
            except Exception as e:
                logger.warning(f"Failed to init OpenAI client: {e}")
    
    def detect_all_patterns(self, text: str) -> Dict[str, Any]:
        """Повний аналіз тексту на всі паттерни"""
        return {
            'coordinates': self.detect_hidden_coordinates(text),
            'threats': self.detect_threat_keywords(text),
            'crypto': self.detect_crypto_addresses(text),
            'phones': self.detect_phone_numbers(text),
            'encoded': self.detect_encoded_data(text),
            'urls': self.detect_suspicious_urls(text),
            'risk_score': self.calculate_risk_score(text),
            'timestamp': datetime.now().isoformat()
        }
    
    def detect_hidden_coordinates(self, text: str) -> List[Dict]:
        """Виявлення прихованих координат"""
        found = []
        for pattern, name in self.COORDINATE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for match in matches:
                    found.append({
                        'type': name,
                        'raw': match if isinstance(match, str) else ' '.join(match),
                        'parsed': self._parse_coordinates(match, name)
                    })
        return found
    
    def _parse_coordinates(self, match, coord_type: str) -> Optional[Dict]:
        """Парсинг координат у десяткову форму"""
        try:
            if coord_type == 'Decimal' and len(match) >= 2:
                return {'lat': float(match[0]), 'lon': float(match[1])}
            elif coord_type == 'DMS' and len(match) >= 8:
                lat = float(match[0]) + float(match[1])/60 + float(match[2])/3600
                if match[3] == 'S':
                    lat = -lat
                lon = float(match[4]) + float(match[5])/60 + float(match[6])/3600
                if match[7] == 'W':
                    lon = -lon
                return {'lat': lat, 'lon': lon}
        except (ValueError, IndexError):
            pass
        return None
    
    def detect_threat_keywords(self, text: str) -> Dict[str, List[str]]:
        """Виявлення ключових слів загроз"""
        text_lower = text.lower()
        found = {level: [] for level in self.THREAT_KEYWORDS}
        
        for level, keywords in self.THREAT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found[level].append(keyword)
        
        return found
    
    def detect_crypto_addresses(self, text: str) -> List[Dict]:
        """Виявлення криптовалютних адрес"""
        found = []
        for pattern, crypto_type in self.CRYPTO_PATTERNS:
            matches = re.findall(pattern, text)
            for match in matches:
                found.append({'type': crypto_type, 'address': match})
        return found
    
    def detect_phone_numbers(self, text: str) -> List[Dict]:
        """Виявлення телефонних номерів"""
        found = []
        for pattern, country in self.PHONE_PATTERNS:
            matches = re.findall(pattern, text)
            for match in matches:
                found.append({'country': country, 'number': match})
        return found
    
    def detect_encoded_data(self, text: str) -> List[Dict]:
        """Виявлення закодованих даних"""
        found = []
        
        base64_pattern = r'[A-Za-z0-9+/]{20,}={0,2}'
        b64_matches = re.findall(base64_pattern, text)
        for match in b64_matches:
            try:
                decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                if decoded and len(decoded) > 5:
                    found.append({
                        'type': 'Base64',
                        'encoded': match[:50] + '...' if len(match) > 50 else match,
                        'decoded_preview': decoded[:100] if len(decoded) > 100 else decoded
                    })
            except:
                pass
        
        hex_pattern = r'\b[0-9a-fA-F]{32,}\b'
        hex_matches = re.findall(hex_pattern, text)
        for match in hex_matches:
            found.append({'type': 'Hex', 'value': match[:50]})
        
        return found
    
    def detect_suspicious_urls(self, text: str) -> List[Dict]:
        """Виявлення підозрілих URL"""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        
        suspicious = []
        suspicious_domains = ['bit.ly', 't.me/joinchat', 'tinyurl', 'is.gd']
        
        for url in urls:
            is_suspicious = any(d in url.lower() for d in suspicious_domains)
            if is_suspicious or 'maps' in url.lower():
                suspicious.append({
                    'url': url,
                    'type': 'map' if 'maps' in url.lower() else 'shortened'
                })
        
        return suspicious
    
    def calculate_risk_score(self, text: str) -> int:
        """Розрахунок рівня ризику (0-100)"""
        score = 0
        
        threats = self.detect_threat_keywords(text)
        score += len(threats.get('critical', [])) * 25
        score += len(threats.get('high', [])) * 15
        score += len(threats.get('medium', [])) * 8
        score += len(threats.get('low', [])) * 3
        
        coords = self.detect_hidden_coordinates(text)
        score += len(coords) * 20
        
        phones = self.detect_phone_numbers(text)
        score += len(phones) * 5
        
        crypto = self.detect_crypto_addresses(text)
        score += len(crypto) * 10
        
        return min(100, score)
    
    async def analyze_with_ai(self, text: str) -> Dict[str, Any]:
        """AI аналіз тексту через GPT"""
        if not self.client:
            return {'error': 'AI not available', 'fallback': self.detect_all_patterns(text)}
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """Ти - експерт з аналізу загроз та OSINT. 
                        Проаналізуй текст на наявність:
                        1. Прихованих координат (в будь-якому форматі)
                        2. Військового жаргону або кодових слів
                        3. Потенційних загроз безпеці
                        4. Шифрованих або закодованих даних
                        5. Підозрілих патернів поведінки
                        
                        Відповідай українською. Будь лаконічним."""
                    },
                    {"role": "user", "content": f"Проаналізуй:\n\n{text[:3000]}"}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            ai_analysis = response.choices[0].message.content
            
            return {
                'ai_analysis': ai_analysis,
                'pattern_detection': self.detect_all_patterns(text),
                'model': 'gpt-4o',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return {
                'error': str(e),
                'fallback': self.detect_all_patterns(text)
            }
    
    def generate_threat_report(self, analysis: Dict) -> str:
        """Генерація звіту про загрози"""
        report = ["<b>🔍 АНАЛІЗ ЗАГРОЗ</b>", "═══════════════════════"]
        
        patterns = analysis.get('pattern_detection', analysis)
        
        if patterns.get('coordinates'):
            report.append("\n<b>📍 Координати:</b>")
            for coord in patterns['coordinates'][:5]:
                report.append(f"├ {coord['type']}: {coord['raw']}")
        
        threats = patterns.get('threats', {})
        critical = threats.get('critical', [])
        high = threats.get('high', [])
        if critical or high:
            report.append("\n<b>⚠️ Загрози:</b>")
            for kw in critical:
                report.append(f"├ 🔴 {kw}")
            for kw in high[:3]:
                report.append(f"├ 🟠 {kw}")
        
        if patterns.get('phones'):
            report.append("\n<b>📱 Телефони:</b>")
            for phone in patterns['phones'][:3]:
                report.append(f"├ {phone['country']}: {phone['number']}")
        
        if patterns.get('crypto'):
            report.append("\n<b>💰 Криптовалюта:</b>")
            for crypto in patterns['crypto'][:3]:
                report.append(f"├ {crypto['type']}: {crypto['address'][:20]}...")
        
        risk = patterns.get('risk_score', 0)
        report.append(f"\n<b>📊 Рівень ризику:</b> {risk}/100")
        
        if risk >= 70:
            report.append("⛔️ КРИТИЧНИЙ РІВЕНЬ ЗАГРОЗИ")
        elif risk >= 40:
            report.append("⚠️ Підвищений рівень загрози")
        else:
            report.append("✅ Низький рівень загрози")
        
        if analysis.get('ai_analysis'):
            report.append("\n<b>🤖 AI Висновок:</b>")
            report.append(analysis['ai_analysis'][:500])
        
        return '\n'.join(report)


ai_pattern_detector = AIPatternDetector()
