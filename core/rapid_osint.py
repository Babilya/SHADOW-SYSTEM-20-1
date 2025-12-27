import asyncio
import logging
import os
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class IntelligenceReport:
    """Звіт розвідки"""
    timestamp: str
    targets_scanned: int
    operators_found: List[Dict] = field(default_factory=list)
    coordinates_found: List[Dict] = field(default_factory=list)
    phones_found: List[Dict] = field(default_factory=list)
    usernames_found: List[Dict] = field(default_factory=list)
    suspicious_messages: List[Dict] = field(default_factory=list)
    crypto_wallets: List[Dict] = field(default_factory=list)
    frequencies: List[Dict] = field(default_factory=list)
    threat_score: int = 0
    summary: str = ""

class RapidOSINTParser:
    """Швидкий OSINT парсер для Telegram каналів"""
    
    def __init__(self, api_id: int = None, api_hash: str = None):
        self.api_id = api_id or int(os.getenv('TELEGRAM_API_ID', '0'))
        self.api_hash = api_hash or os.getenv('TELEGRAM_API_HASH', '')
        self.client = None
        
        self.patterns = {
            'coordinates_decimal': r'\b(\d{2}\.\d{4,}),?\s*(\d{2}\.\d{4,})\b',
            'coordinates_dms': r"(\d{1,3})°\s*(\d{1,2})['′]\s*(\d{1,2})[\"″]?\s*[NSEW]",
            'coordinates_mgrs': r'\b[A-Z]{2}\d{2}[A-Z]{2}\d{4,10}\b',
            'phones_ua': r'\+?38[\s\-\(]?0\d{2}[\s\-\)]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}',
            'phones_ru': r'\+?7[\s\-\(]?\d{3}[\s\-\)]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}',
            'phones_generic': r'[\+\(]?[1-9][0-9\-\(\)\.]{9,15}',
            'usernames': r'@[\w\d_]{5,32}',
            'crypto_btc': r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b',
            'crypto_eth': r'\b0x[a-fA-F0-9]{40}\b',
            'crypto_usdt_trc20': r'\bT[A-Za-z1-9]{33}\b',
            'frequencies_mhz': r'\b\d{2,4}[\.,]\d{1,3}\s*(MHz|МГц|mhz|мгц)\b',
            'frequencies_khz': r'\b\d{3,6}\s*(kHz|КГц|khz|кгц)\b',
            'call_signs': r'\b[A-Z]{1,3}\d{1,3}[A-Z]{0,3}\b',
            'ip_addresses': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'urls': r'https?://[^\s<>"{}|\\^`\[\]]+',
        }
        
        self.threat_keywords = {
            'critical': [
                'детонатор', 'вибухівка', 'підрив', 'замінування', 'бомба', 'сво',
                'c4', 'тнт', 'пластид', 'запал', 'таймер'
            ],
            'high': [
                'координати', 'позиція', 'локація', 'дрон', 'квадрокоптер', 'fpv',
                'мавік', 'mavic', 'частота', 'радіо', 'антена', 'глушилка',
                'реп', 'rep', 'повітряна розвідка'
            ],
            'medium': [
                'зброя', 'боєприпаси', 'патрони', 'схованка', 'закладка', 'точка',
                'збір', 'евакуація', 'маршрут', 'блокпост', 'укриття'
            ],
            'intel': [
                'операція', 'завдання', 'наказ', 'рапорт', 'звіт', 'розвідка',
                'спостереження', 'контроль', 'перевірка'
            ]
        }
        
        self.output_dir = Path("./intel_reports")
        self.output_dir.mkdir(exist_ok=True)
    
    async def connect(self, session_name: str = 'osint_session') -> bool:
        """Підключення до Telegram"""
        try:
            from telethon import TelegramClient
            
            self.client = TelegramClient(session_name, self.api_id, self.api_hash)
            await self.client.start()
            
            logger.info("✅ OSINT Parser connected")
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
    
    async def rapid_scan(
        self,
        targets: List[str],
        messages_limit: int = 100,
        time_limit_hours: int = 24
    ) -> IntelligenceReport:
        """Швидке сканування цільових каналів"""
        
        report = IntelligenceReport(
            timestamp=datetime.now().isoformat(),
            targets_scanned=0
        )
        
        if not self.client:
            logger.error("Not connected")
            return report
        
        from telethon.tl.functions.messages import GetHistoryRequest
        
        time_cutoff = datetime.now() - timedelta(hours=time_limit_hours)
        
        for target in targets:
            try:
                entity = await self.client.get_entity(target)
                report.targets_scanned += 1
                
                messages = await self.client(GetHistoryRequest(
                    peer=entity,
                    limit=messages_limit,
                    offset_date=None,
                    offset_id=0,
                    max_id=0,
                    min_id=0,
                    add_offset=0,
                    hash=0
                ))
                
                for msg in messages.messages:
                    if not msg.message:
                        continue
                    
                    if hasattr(msg, 'date') and msg.date:
                        msg_time = msg.date.replace(tzinfo=None)
                        if msg_time < time_cutoff:
                            continue
                    
                    text = msg.message
                    sender_id = getattr(msg, 'from_id', None)
                    if hasattr(sender_id, 'user_id'):
                        sender_id = sender_id.user_id
                    
                    findings = await self._analyze_message(
                        text=text,
                        message_id=msg.id,
                        sender_id=sender_id,
                        channel=target,
                        date=msg.date.isoformat() if msg.date else None
                    )
                    
                    if findings['coordinates']:
                        report.coordinates_found.extend(findings['coordinates'])
                        report.threat_score += 20 * len(findings['coordinates'])
                    
                    if findings['phones']:
                        report.phones_found.extend(findings['phones'])
                        report.threat_score += 5 * len(findings['phones'])
                    
                    if findings['usernames']:
                        report.usernames_found.extend(findings['usernames'])
                    
                    if findings['crypto']:
                        report.crypto_wallets.extend(findings['crypto'])
                        report.threat_score += 10 * len(findings['crypto'])
                    
                    if findings['frequencies']:
                        report.frequencies.extend(findings['frequencies'])
                        report.threat_score += 15 * len(findings['frequencies'])
                    
                    if findings['suspicious']:
                        report.suspicious_messages.append(findings['suspicious'])
                        report.threat_score += findings['suspicious'].get('score', 0)
                    
                    if findings['phones'] or findings['usernames']:
                        report.operators_found.append({
                            'channel': target,
                            'message_id': msg.id,
                            'phones': findings['phones'],
                            'usernames': findings['usernames'],
                            'context': text[:200]
                        })
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error scanning {target}: {e}")
                continue
        
        report.summary = self._generate_summary(report)
        
        await self._save_report(report)
        
        return report
    
    async def _analyze_message(
        self,
        text: str,
        message_id: int,
        sender_id: Any,
        channel: str,
        date: str
    ) -> Dict[str, Any]:
        """Аналіз окремого повідомлення"""
        
        findings = {
            'coordinates': [],
            'phones': [],
            'usernames': [],
            'crypto': [],
            'frequencies': [],
            'suspicious': None
        }
        
        for coord_pattern in ['coordinates_decimal', 'coordinates_dms', 'coordinates_mgrs']:
            matches = re.findall(self.patterns[coord_pattern], text, re.IGNORECASE)
            if matches:
                for match in matches:
                    findings['coordinates'].append({
                        'type': coord_pattern,
                        'value': match if isinstance(match, str) else ','.join(match),
                        'channel': channel,
                        'message_id': message_id,
                        'date': date
                    })
        
        for phone_pattern in ['phones_ua', 'phones_ru', 'phones_generic']:
            matches = re.findall(self.patterns[phone_pattern], text)
            for match in matches:
                if match not in [p['value'] for p in findings['phones']]:
                    findings['phones'].append({
                        'type': phone_pattern.replace('phones_', ''),
                        'value': match,
                        'channel': channel,
                        'message_id': message_id
                    })
        
        usernames = re.findall(self.patterns['usernames'], text)
        for username in usernames:
            findings['usernames'].append({
                'value': username,
                'channel': channel,
                'message_id': message_id
            })
        
        for crypto_pattern in ['crypto_btc', 'crypto_eth', 'crypto_usdt_trc20']:
            matches = re.findall(self.patterns[crypto_pattern], text)
            for match in matches:
                findings['crypto'].append({
                    'type': crypto_pattern.replace('crypto_', ''),
                    'value': match,
                    'channel': channel,
                    'message_id': message_id
                })
        
        for freq_pattern in ['frequencies_mhz', 'frequencies_khz']:
            matches = re.findall(self.patterns[freq_pattern], text, re.IGNORECASE)
            for match in matches:
                findings['frequencies'].append({
                    'type': freq_pattern.replace('frequencies_', ''),
                    'value': match[0] if isinstance(match, tuple) else match,
                    'channel': channel,
                    'message_id': message_id
                })
        
        text_lower = text.lower()
        threat_score = 0
        keywords_found = []
        
        for level, keywords in self.threat_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    keywords_found.append((level, keyword))
                    if level == 'critical':
                        threat_score += 30
                    elif level == 'high':
                        threat_score += 20
                    elif level == 'medium':
                        threat_score += 10
                    else:
                        threat_score += 5
        
        if threat_score > 0 or keywords_found:
            findings['suspicious'] = {
                'channel': channel,
                'message_id': message_id,
                'sender_id': sender_id,
                'text': text[:500],
                'keywords': keywords_found,
                'score': threat_score,
                'date': date
            }
        
        return findings
    
    def _generate_summary(self, report: IntelligenceReport) -> str:
        """Генерація текстового звіту"""
        
        summary = f"""
⚡ ЕКСПРЕС-РОЗВІДКА ⚡
───────────────═════
Час: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

📊 РЕЗУЛЬТАТИ СКАНУВАННЯ:
├ Проскановано каналів: {report.targets_scanned}
├ Знайдено операторів: {len(report.operators_found)}
├ Повідомлень з координатами: {len(report.coordinates_found)}
├ Телефонних номерів: {len(report.phones_found)}
├ Юзернеймів: {len(report.usernames_found)}
├ Крипто-гаманців: {len(report.crypto_wallets)}
├ Радіочастот: {len(report.frequencies)}
└ Підозрілих повідомлень: {len(report.suspicious_messages)}

⚠️ РІВЕНЬ ЗАГРОЗИ: {self._get_threat_level(report.threat_score)}
   Бал загрози: {report.threat_score}

"""
        
        if report.coordinates_found:
            summary += "📍 КООРДИНАТИ:\n"
            for coord in report.coordinates_found[:5]:
                summary += f"   • {coord['value']} ({coord['type']})\n"
            if len(report.coordinates_found) > 5:
                summary += f"   ... ще {len(report.coordinates_found) - 5}\n"
        
        if report.frequencies:
            summary += "\n📡 ЧАСТОТИ:\n"
            for freq in report.frequencies[:5]:
                summary += f"   • {freq['value']} {freq['type']}\n"
        
        if report.phones_found:
            summary += "\n📞 ТЕЛЕФОНИ:\n"
            for phone in report.phones_found[:5]:
                summary += f"   • {phone['value']}\n"
        
        if report.suspicious_messages:
            summary += "\n🚨 КРИТИЧНІ ЗНАХІДКИ:\n"
            for msg in sorted(report.suspicious_messages, key=lambda x: x['score'], reverse=True)[:3]:
                keywords = ', '.join([k[1] for k in msg['keywords'][:3]])
                summary += f"   • [{msg['score']}] {keywords}: {msg['text'][:80]}...\n"
        
        summary += "\n───────────────═════"
        
        return summary
    
    def _get_threat_level(self, score: int) -> str:
        """Визначення рівня загрози"""
        if score >= 100:
            return "🔴 КРИТИЧНИЙ"
        elif score >= 50:
            return "🟠 ВИСОКИЙ"
        elif score >= 20:
            return "🟡 СЕРЕДНІЙ"
        else:
            return "🟢 НИЗЬКИЙ"
    
    async def _save_report(self, report: IntelligenceReport):
        """Збереження звіту"""
        filename = f"intel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': report.timestamp,
                'targets_scanned': report.targets_scanned,
                'threat_score': report.threat_score,
                'coordinates': report.coordinates_found,
                'phones': report.phones_found,
                'usernames': report.usernames_found,
                'crypto_wallets': report.crypto_wallets,
                'frequencies': report.frequencies,
                'operators': report.operators_found,
                'suspicious_messages': report.suspicious_messages,
                'summary': report.summary
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Report saved: {filepath}")
    
    async def quick_user_lookup(self, username: str) -> Dict[str, Any]:
        """Швидкий пошук інформації про користувача"""
        
        if not self.client:
            return {'error': 'Not connected'}
        
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
                'premium': getattr(user, 'premium', False),
                'scam': getattr(user, 'scam', False),
                'fake': getattr(user, 'fake', False),
                'restricted': getattr(user, 'restricted', False),
                'photo': bool(user.photo),
                'status': str(user.status) if user.status else 'unknown'
            }
            
        except Exception as e:
            return {'error': str(e)}

rapid_osint = RapidOSINTParser()
