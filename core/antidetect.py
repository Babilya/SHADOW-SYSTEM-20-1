"""
AntiDetectSystem - Система уникнення виявлення для SHADOW SYSTEM iO v2.0
Маскування пристроїв, емуляція поведінки, унікальні fingerprint
"""
import random
import hashlib
import uuid
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class AntiDetectSystem:
    """
    Система уникнення виявлення:
    - Маскування під різні пристрої
    - Емуляція людської поведінки
    - Унікальні fingerprint для кожного бота
    - Ротація профілів
    """
    
    DEVICE_PROFILES = {
        'android_samsung_s21': {
            'device_model': 'SM-G991B',
            'system_version': 'Android 12',
            'app_version': '9.6.3',
            'lang_code': 'uk',
            'system_lang_code': 'uk-UA',
            'tz_offset': 7200,
            'screen_width': 1080,
            'screen_height': 2400,
        },
        'android_samsung_a52': {
            'device_model': 'SM-A525F',
            'system_version': 'Android 11',
            'app_version': '9.5.1',
            'lang_code': 'uk',
            'system_lang_code': 'uk-UA',
            'tz_offset': 7200,
            'screen_width': 1080,
            'screen_height': 2400,
        },
        'android_xiaomi': {
            'device_model': 'Redmi Note 10',
            'system_version': 'Android 11',
            'app_version': '9.4.8',
            'lang_code': 'uk',
            'system_lang_code': 'uk-UA',
            'tz_offset': 7200,
            'screen_width': 1080,
            'screen_height': 2400,
        },
        'android_pixel': {
            'device_model': 'Pixel 6',
            'system_version': 'Android 13',
            'app_version': '9.6.5',
            'lang_code': 'en',
            'system_lang_code': 'en-US',
            'tz_offset': 7200,
            'screen_width': 1080,
            'screen_height': 2400,
        },
        'iphone_13': {
            'device_model': 'iPhone 13 Pro',
            'system_version': 'iOS 16.2',
            'app_version': '9.6.3',
            'lang_code': 'uk',
            'system_lang_code': 'uk-UA',
            'tz_offset': 7200,
            'screen_width': 1170,
            'screen_height': 2532,
        },
        'iphone_12': {
            'device_model': 'iPhone 12',
            'system_version': 'iOS 15.6',
            'app_version': '9.5.5',
            'lang_code': 'uk',
            'system_lang_code': 'uk-UA',
            'tz_offset': 7200,
            'screen_width': 1170,
            'screen_height': 2532,
        },
        'desktop_windows': {
            'device_model': 'Windows Desktop',
            'system_version': 'Windows 10',
            'app_version': '4.6.1',
            'lang_code': 'uk',
            'system_lang_code': 'uk-UA',
            'tz_offset': 7200,
            'screen_width': 1920,
            'screen_height': 1080,
        },
        'desktop_macos': {
            'device_model': 'MacBook Pro',
            'system_version': 'macOS 13.1',
            'app_version': '9.6.2',
            'lang_code': 'uk',
            'system_lang_code': 'uk-UA',
            'tz_offset': 7200,
            'screen_width': 2560,
            'screen_height': 1600,
        },
        'desktop_linux': {
            'device_model': 'Linux Desktop',
            'system_version': 'Ubuntu 22.04',
            'app_version': '4.5.3',
            'lang_code': 'uk',
            'system_lang_code': 'uk-UA',
            'tz_offset': 7200,
            'screen_width': 1920,
            'screen_height': 1080,
        },
    }
    
    BEHAVIOR_PATTERNS = {
        'casual_user': {
            'typing_speed': (100, 300),
            'typing_variation': 0.3,
            'online_times': [(9, 12), (18, 23)],
            'message_length': (10, 100),
            'reaction_time': (2, 10),
            'pause_between_actions': (3, 15),
            'typo_probability': 0.05,
        },
        'active_user': {
            'typing_speed': (50, 150),
            'typing_variation': 0.2,
            'online_times': [(8, 24)],
            'message_length': (5, 50),
            'reaction_time': (1, 5),
            'pause_between_actions': (1, 5),
            'typo_probability': 0.02,
        },
        'business_user': {
            'typing_speed': (80, 200),
            'typing_variation': 0.15,
            'online_times': [(9, 18)],
            'message_length': (20, 200),
            'reaction_time': (5, 30),
            'pause_between_actions': (5, 20),
            'typo_probability': 0.01,
        },
        'night_owl': {
            'typing_speed': (80, 250),
            'typing_variation': 0.25,
            'online_times': [(0, 4), (20, 24)],
            'message_length': (5, 80),
            'reaction_time': (3, 15),
            'pause_between_actions': (5, 25),
            'typo_probability': 0.04,
        },
        'early_bird': {
            'typing_speed': (90, 220),
            'typing_variation': 0.2,
            'online_times': [(5, 10), (19, 22)],
            'message_length': (15, 120),
            'reaction_time': (2, 8),
            'pause_between_actions': (3, 12),
            'typo_probability': 0.03,
        },
    }
    
    def __init__(self):
        self.generated_fingerprints: Dict[str, dict] = {}
        from core.poison_pill import poison_pill
        from core.dynamic_biometrics import dynamic_biometrics
        self.poison_pill = poison_pill
        self.dynamic_biometrics = dynamic_biometrics
    
    def generate_device_fingerprint(
        self, 
        profile_type: str = None,
        bot_id: str = None
    ) -> Dict:
        """Генерація унікального fingerprint пристрою"""
        if not profile_type:
            profile_type = random.choice(list(self.DEVICE_PROFILES.keys()))
        
        profile = self.DEVICE_PROFILES.get(profile_type, 
                                           self.DEVICE_PROFILES['android_samsung_s21']).copy()
        
        unique_id = bot_id or str(uuid.uuid4())
        
        fingerprint = {
            **profile,
            'device_id': f"{profile_type}_{hashlib.md5(unique_id.encode()).hexdigest()[:8]}",
            'app_build': random.randint(100000, 999999),
            'created': datetime.now().isoformat(),
            'session_id': str(uuid.uuid4()),
            'profile_type': profile_type,
            'fingerprint_hash': hashlib.sha256(
                f"{unique_id}{profile_type}{datetime.now().isoformat()}".encode()
            ).hexdigest()[:32],
        }
        
        fingerprint['screen_resolution'] = self._generate_screen_resolution(profile_type)
        fingerprint['canvas_hash'] = self._generate_canvas_hash()
        fingerprint['webgl_hash'] = self._generate_webgl_hash()
        fingerprint['audio_hash'] = self._generate_audio_hash()
        fingerprint['font_hash'] = self._generate_font_hash()
        
        if bot_id:
            self.generated_fingerprints[bot_id] = fingerprint
        
        return fingerprint
    
    def _generate_screen_resolution(self, profile_type: str) -> str:
        """Генерація роздільної здатності екрану"""
        if 'android' in profile_type or 'iphone' in profile_type:
            resolutions = [
                '1080x2400', '1080x2340', '1170x2532', 
                '1440x3200', '1080x2280', '1080x1920'
            ]
        else:
            resolutions = [
                '1920x1080', '2560x1440', '1366x768',
                '2560x1600', '1680x1050', '3840x2160'
            ]
        
        return random.choice(resolutions)
    
    def _generate_canvas_hash(self) -> str:
        """Генерація хешу canvas fingerprint"""
        return hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()
    
    def _generate_webgl_hash(self) -> str:
        """Генерація хешу WebGL fingerprint"""
        return hashlib.sha1(str(uuid.uuid4()).encode()).hexdigest()[:24]
    
    def _generate_audio_hash(self) -> str:
        """Генерація хешу Audio fingerprint"""
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:16]
    
    def _generate_font_hash(self) -> str:
        """Генерація хешу встановлених шрифтів"""
        return hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:12]
    
    def get_behavior_pattern(self, pattern_type: str = None) -> Dict:
        """Отримання патерну поведінки"""
        if not pattern_type:
            pattern_type = random.choice(list(self.BEHAVIOR_PATTERNS.keys()))
        
        return self.BEHAVIOR_PATTERNS.get(
            pattern_type, 
            self.BEHAVIOR_PATTERNS['casual_user']
        ).copy()
    
    async def emulate_typing(
        self, 
        text: str, 
        pattern_type: str = 'casual_user'
    ) -> float:
        """Емуляція набору тексту - повертає загальний час"""
        behavior = self.get_behavior_pattern(pattern_type)
        speed_min, speed_max = behavior['typing_speed']
        variation = behavior['typing_variation']
        
        total_time = 0
        
        for char in text:
            base_speed = random.uniform(speed_min, speed_max)
            actual_speed = base_speed * random.uniform(1 - variation, 1 + variation)
            
            if char == ' ':
                actual_speed *= 0.7
            elif char in '.,!?':
                actual_speed *= 1.5
            
            total_time += actual_speed / 1000
        
        return total_time
    
    async def emulate_thinking(self, pattern_type: str = 'casual_user') -> float:
        """Емуляція "думання" перед відповіддю"""
        behavior = self.get_behavior_pattern(pattern_type)
        think_min, think_max = behavior['reaction_time']
        return random.uniform(think_min, think_max)
    
    async def emulate_pause(self, pattern_type: str = 'casual_user') -> float:
        """Емуляція паузи між діями"""
        behavior = self.get_behavior_pattern(pattern_type)
        pause_min, pause_max = behavior['pause_between_actions']
        return random.uniform(pause_min, pause_max)
    
    def is_online_time(self, pattern_type: str = 'casual_user') -> bool:
        """Перевірка чи зараз час онлайну для патерну"""
        behavior = self.get_behavior_pattern(pattern_type)
        current_hour = datetime.now().hour
        
        for online_start, online_end in behavior['online_times']:
            if online_start <= current_hour < online_end:
                return True
        
        return False
    
    def generate_realistic_message(
        self, 
        base_message: str, 
        pattern_type: str = 'casual_user'
    ) -> str:
        """Генерація реалістичного повідомлення з можливими помилками"""
        behavior = self.get_behavior_pattern(pattern_type)
        typo_prob = behavior.get('typo_probability', 0.03)
        
        if random.random() > typo_prob:
            return base_message
        
        typo_types = [
            self._add_typo,
            self._swap_chars,
            self._double_char,
        ]
        
        typo_func = random.choice(typo_types)
        return typo_func(base_message)
    
    def _add_typo(self, text: str) -> str:
        """Додавання друкарської помилки"""
        if len(text) < 3:
            return text
        
        pos = random.randint(1, len(text) - 1)
        typos = {
            'а': 'с', 'о': 'п', 'е': 'р', 'і': 'и',
            'н': 'м', 'т': 'р', 'к': 'л', 'в': 'а'
        }
        
        char = text[pos].lower()
        if char in typos:
            return text[:pos] + typos[char] + text[pos+1:]
        return text
    
    def _swap_chars(self, text: str) -> str:
        """Заміна місцями сусідніх символів"""
        if len(text) < 4:
            return text
        
        pos = random.randint(1, len(text) - 2)
        return text[:pos] + text[pos+1] + text[pos] + text[pos+2:]
    
    def _double_char(self, text: str) -> str:
        """Подвоєння символу"""
        if len(text) < 3:
            return text
        
        pos = random.randint(1, len(text) - 1)
        return text[:pos] + text[pos] + text[pos:]
    
    def get_random_profile_type(self) -> str:
        """Отримання випадкового типу профілю"""
        weights = {
            'android_samsung_s21': 20,
            'android_samsung_a52': 15,
            'android_xiaomi': 25,
            'android_pixel': 5,
            'iphone_13': 10,
            'iphone_12': 10,
            'desktop_windows': 8,
            'desktop_macos': 4,
            'desktop_linux': 3,
        }
        
        profiles = list(weights.keys())
        probs = [weights[p] for p in profiles]
        total = sum(probs)
        probs = [p/total for p in probs]
        
        return random.choices(profiles, weights=probs, k=1)[0]
    
    def get_fingerprint(self, bot_id: str) -> Optional[Dict]:
        """Отримання збереженого fingerprint для бота"""
        return self.generated_fingerprints.get(bot_id)
    
    def update_fingerprint(self, bot_id: str, updates: Dict):
        """Оновлення fingerprint бота"""
        if bot_id in self.generated_fingerprints:
            self.generated_fingerprints[bot_id].update(updates)
    
    def rotate_fingerprint(self, bot_id: str) -> Dict:
        """Ротація fingerprint бота"""
        old_profile = None
        if bot_id in self.generated_fingerprints:
            old_profile = self.generated_fingerprints[bot_id].get('profile_type')
        
        available_profiles = [
            p for p in self.DEVICE_PROFILES.keys() 
            if p != old_profile
        ]
        
        new_profile = random.choice(available_profiles)
        return self.generate_device_fingerprint(new_profile, bot_id)
    
    def format_fingerprint_report(self, fingerprint: Dict) -> str:
        """Форматування звіту fingerprint"""
        return (
            f"<b>📱 DEVICE FINGERPRINT</b>\n"
            f"═══════════════════════\n\n"
            f"├ <b>Profile:</b> {fingerprint.get('profile_type', 'N/A')}\n"
            f"├ <b>Device:</b> {fingerprint.get('device_model', 'N/A')}\n"
            f"├ <b>OS:</b> {fingerprint.get('system_version', 'N/A')}\n"
            f"├ <b>App:</b> {fingerprint.get('app_version', 'N/A')}\n"
            f"├ <b>Lang:</b> {fingerprint.get('lang_code', 'N/A')}\n"
            f"├ <b>Screen:</b> {fingerprint.get('screen_resolution', 'N/A')}\n"
            f"├ <b>Device ID:</b> <code>{fingerprint.get('device_id', 'N/A')}</code>\n"
            f"└ <b>Hash:</b> <code>{fingerprint.get('fingerprint_hash', 'N/A')[:16]}...</code>"
        )


antidetect_system = AntiDetectSystem()
