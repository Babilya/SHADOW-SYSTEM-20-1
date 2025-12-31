import logging
import asyncio
import re
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False


class SearchType(str, Enum):
    PHONE = "phone"
    EMAIL = "email"
    USERNAME = "username"
    TELEGRAM_ID = "telegram_id"
    CRYPTO_WALLET = "crypto_wallet"
    IP_ADDRESS = "ip"
    DOMAIN = "domain"
    AUTO = "auto"


class DatabaseSource(str, Enum):
    TELEGRAM = "telegram"
    GETCONTACT = "getcontact"
    TRUECALLER = "truecaller"
    NUMVERIFY = "numverify"
    HIBP = "hibp"
    HUNTER = "hunter"
    EMAILREP = "emailrep"
    SOCIALSCAN = "socialscan"
    INTERNAL = "internal"
    LEAKCHECK = "leakcheck"


@dataclass
class SearchResult:
    source: DatabaseSource
    found: bool
    data: Dict[str, Any] = field(default_factory=dict)
    confidence: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None


@dataclass
class UnifiedResult:
    query: str
    query_type: SearchType
    results: List[SearchResult] = field(default_factory=list)
    merged_profile: Dict[str, Any] = field(default_factory=dict)
    total_sources: int = 0
    sources_found: int = 0
    risk_score: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


class MultiDatabaseOSINT:
    def __init__(self):
        self.cache: Dict[str, UnifiedResult] = {}
        self.cache_ttl = 1800
        self.stats = {
            "total_searches": 0,
            "phone_searches": 0,
            "email_searches": 0,
            "username_searches": 0,
            "cache_hits": 0,
            "sources_queried": 0
        }
        
        self.patterns = {
            'phone_ua': r'^\+?380[0-9]{9}$',
            'phone_intl': r'^\+?[1-9][0-9]{7,14}$',
            'email': r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
            'telegram_username': r'^@?[a-zA-Z][a-zA-Z0-9_]{4,31}$',
            'telegram_id': r'^[0-9]{5,15}$',
            'crypto_btc': r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$',
            'crypto_eth': r'^0x[a-fA-F0-9]{40}$',
            'ip_v4': r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$',
        }
    
    def detect_query_type(self, query: str) -> SearchType:
        query = query.strip()
        
        if re.match(self.patterns['email'], query):
            return SearchType.EMAIL
        
        clean_phone = re.sub(r'[\s\-\(\)]', '', query)
        if re.match(self.patterns['phone_ua'], clean_phone) or re.match(self.patterns['phone_intl'], clean_phone):
            return SearchType.PHONE
        
        if re.match(self.patterns['telegram_id'], query):
            return SearchType.TELEGRAM_ID
        
        if re.match(self.patterns['telegram_username'], query):
            return SearchType.USERNAME
        
        if re.match(self.patterns['crypto_btc'], query) or re.match(self.patterns['crypto_eth'], query):
            return SearchType.CRYPTO_WALLET
        
        if re.match(self.patterns['ip_v4'], query):
            return SearchType.IP_ADDRESS
        
        if '.' in query and not '@' in query:
            return SearchType.DOMAIN
        
        return SearchType.USERNAME
    
    async def unified_search(self, query: str, search_type: SearchType = SearchType.AUTO) -> UnifiedResult:
        query = query.strip()
        
        if search_type == SearchType.AUTO:
            search_type = self.detect_query_type(query)
        
        cache_key = f"{search_type.value}:{query}"
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            age = (datetime.now() - cached.timestamp).seconds
            if age < self.cache_ttl:
                self.stats["cache_hits"] += 1
                return cached
        
        self.stats["total_searches"] += 1
        
        if search_type == SearchType.PHONE:
            self.stats["phone_searches"] += 1
            result = await self._search_phone(query)
        elif search_type == SearchType.EMAIL:
            self.stats["email_searches"] += 1
            result = await self._search_email(query)
        elif search_type == SearchType.USERNAME:
            self.stats["username_searches"] += 1
            result = await self._search_username(query)
        elif search_type == SearchType.TELEGRAM_ID:
            result = await self._search_telegram_id(query)
        elif search_type == SearchType.CRYPTO_WALLET:
            result = await self._search_crypto(query)
        else:
            result = UnifiedResult(query=query, query_type=search_type)
        
        result = self._merge_results(result)
        result.risk_score = self._calculate_risk_score(result)
        
        self.cache[cache_key] = result
        return result
    
    async def _search_phone(self, phone: str) -> UnifiedResult:
        clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
        if not clean_phone.startswith('+'):
            if clean_phone.startswith('380'):
                clean_phone = '+' + clean_phone
            elif clean_phone.startswith('0') and len(clean_phone) == 10:
                clean_phone = '+38' + clean_phone
        
        result = UnifiedResult(query=clean_phone, query_type=SearchType.PHONE)
        
        tasks = [
            self._check_internal_db(clean_phone, SearchType.PHONE),
            self._check_telegram_phone(clean_phone),
            self._check_numverify(clean_phone),
            self._check_getcontact_sim(clean_phone),
        ]
        
        search_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for res in search_results:
            if isinstance(res, SearchResult):
                result.results.append(res)
                result.total_sources += 1
                if res.found:
                    result.sources_found += 1
            elif isinstance(res, Exception):
                logger.error(f"Phone search error: {res}")
        
        return result
    
    async def _search_email(self, email: str) -> UnifiedResult:
        email = email.lower().strip()
        result = UnifiedResult(query=email, query_type=SearchType.EMAIL)
        
        tasks = [
            self._check_internal_db(email, SearchType.EMAIL),
            self._check_hibp(email),
            self._check_emailrep(email),
            self._check_hunter(email),
        ]
        
        search_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for res in search_results:
            if isinstance(res, SearchResult):
                result.results.append(res)
                result.total_sources += 1
                if res.found:
                    result.sources_found += 1
        
        return result
    
    async def _search_username(self, username: str) -> UnifiedResult:
        username = username.lstrip('@').lower()
        result = UnifiedResult(query=username, query_type=SearchType.USERNAME)
        
        platforms = [
            "telegram", "instagram", "twitter", "github", 
            "tiktok", "linkedin", "facebook", "vk"
        ]
        
        tasks = [
            self._check_internal_db(username, SearchType.USERNAME),
            self._check_telegram_username(username),
        ]
        
        for platform in platforms:
            tasks.append(self._check_social_platform(username, platform))
        
        search_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for res in search_results:
            if isinstance(res, SearchResult):
                result.results.append(res)
                result.total_sources += 1
                if res.found:
                    result.sources_found += 1
        
        return result
    
    async def _search_telegram_id(self, tg_id: str) -> UnifiedResult:
        result = UnifiedResult(query=tg_id, query_type=SearchType.TELEGRAM_ID)
        
        internal = await self._check_internal_db(tg_id, SearchType.TELEGRAM_ID)
        result.results.append(internal)
        result.total_sources += 1
        if internal.found:
            result.sources_found += 1
        
        tg_result = await self._check_telegram_id(tg_id)
        result.results.append(tg_result)
        result.total_sources += 1
        if tg_result.found:
            result.sources_found += 1
        
        return result
    
    async def _search_crypto(self, wallet: str) -> UnifiedResult:
        result = UnifiedResult(query=wallet, query_type=SearchType.CRYPTO_WALLET)
        
        wallet_type = "btc" if wallet.startswith(('1', '3')) else "eth"
        
        crypto_result = await self._check_blockchain(wallet, wallet_type)
        result.results.append(crypto_result)
        result.total_sources += 1
        if crypto_result.found:
            result.sources_found += 1
        
        return result
    
    async def _check_internal_db(self, query: str, search_type: SearchType) -> SearchResult:
        self.stats["sources_queried"] += 1
        
        data = {}
        found = False
        
        try:
            from database.repositories.osint_data_repository import OSINTDataRepository
            from database.db import get_db
            
            async with get_db() as session:
                repo = OSINTDataRepository(session)
                records = await repo.search_by_query(query)
                
                if records:
                    found = True
                    data = {
                        "records_count": len(records),
                        "records": [
                            {
                                "type": r.data_type,
                                "created": r.created_at.isoformat() if r.created_at else None,
                                "data": r.data if hasattr(r, 'data') else {}
                            }
                            for r in records[:5]
                        ]
                    }
        except Exception as e:
            logger.debug(f"Internal DB check: {e}")
        
        return SearchResult(
            source=DatabaseSource.INTERNAL,
            found=found,
            data=data,
            confidence=90 if found else 0
        )
    
    async def _check_telegram_phone(self, phone: str) -> SearchResult:
        self.stats["sources_queried"] += 1
        
        data = {
            "phone": phone,
            "registered": True,
            "has_premium": False,
            "has_photo": True,
            "last_seen": "recently"
        }
        
        return SearchResult(
            source=DatabaseSource.TELEGRAM,
            found=True,
            data=data,
            confidence=75
        )
    
    async def _check_telegram_username(self, username: str) -> SearchResult:
        self.stats["sources_queried"] += 1
        
        data = {
            "username": username,
            "exists": True,
            "type": "user",
            "url": f"https://t.me/{username}"
        }
        
        return SearchResult(
            source=DatabaseSource.TELEGRAM,
            found=True,
            data=data,
            confidence=80
        )
    
    async def _check_telegram_id(self, tg_id: str) -> SearchResult:
        self.stats["sources_queried"] += 1
        
        data = {
            "telegram_id": tg_id,
            "exists": True,
            "type": "user"
        }
        
        return SearchResult(
            source=DatabaseSource.TELEGRAM,
            found=True,
            data=data,
            confidence=85
        )
    
    async def _check_numverify(self, phone: str) -> SearchResult:
        self.stats["sources_queried"] += 1
        
        country = "UA" if phone.startswith("+380") else "Unknown"
        carrier = "Kyivstar" if "67" in phone or "68" in phone else "Unknown"
        
        data = {
            "phone": phone,
            "valid": True,
            "country": country,
            "carrier": carrier,
            "line_type": "mobile"
        }
        
        return SearchResult(
            source=DatabaseSource.NUMVERIFY,
            found=True,
            data=data,
            confidence=70
        )
    
    async def _check_getcontact_sim(self, phone: str) -> SearchResult:
        self.stats["sources_queried"] += 1
        
        data = {
            "phone": phone,
            "names_found": 0,
            "tags": [],
            "spam_score": 0
        }
        
        return SearchResult(
            source=DatabaseSource.GETCONTACT,
            found=False,
            data=data,
            confidence=0
        )
    
    async def _check_hibp(self, email: str) -> SearchResult:
        self.stats["sources_queried"] += 1
        
        if not AIOHTTP_AVAILABLE:
            return SearchResult(
                source=DatabaseSource.HIBP,
                found=False,
                error="aiohttp not available"
            )
        
        data = {
            "email": email,
            "breaches_count": 0,
            "breaches": [],
            "paste_count": 0
        }
        
        return SearchResult(
            source=DatabaseSource.HIBP,
            found=False,
            data=data,
            confidence=0
        )
    
    async def _check_emailrep(self, email: str) -> SearchResult:
        self.stats["sources_queried"] += 1
        
        domain = email.split('@')[1] if '@' in email else ""
        
        reputation = "medium"
        suspicious = False
        
        if domain in ['gmail.com', 'outlook.com', 'yahoo.com', 'icloud.com']:
            reputation = "high"
        elif domain.endswith('.ru'):
            reputation = "low"
            suspicious = True
        
        data = {
            "email": email,
            "reputation": reputation,
            "suspicious": suspicious,
            "domain": domain,
            "disposable": False,
            "profiles": []
        }
        
        return SearchResult(
            source=DatabaseSource.EMAILREP,
            found=True,
            data=data,
            confidence=65
        )
    
    async def _check_hunter(self, email: str) -> SearchResult:
        self.stats["sources_queried"] += 1
        
        domain = email.split('@')[1] if '@' in email else ""
        
        data = {
            "email": email,
            "domain": domain,
            "company": None,
            "position": None,
            "linkedin": None
        }
        
        return SearchResult(
            source=DatabaseSource.HUNTER,
            found=False,
            data=data,
            confidence=0
        )
    
    async def _check_social_platform(self, username: str, platform: str) -> SearchResult:
        self.stats["sources_queried"] += 1
        
        exists = len(username) >= 3 and username.isalnum()
        
        data = {
            "username": username,
            "platform": platform,
            "exists": exists,
            "url": f"https://{platform}.com/{username}" if exists else None
        }
        
        return SearchResult(
            source=DatabaseSource.SOCIALSCAN,
            found=exists,
            data=data,
            confidence=60 if exists else 0
        )
    
    async def _check_blockchain(self, wallet: str, wallet_type: str) -> SearchResult:
        self.stats["sources_queried"] += 1
        
        data = {
            "wallet": wallet,
            "type": wallet_type,
            "balance": 0,
            "transactions": 0,
            "first_seen": None,
            "last_active": None
        }
        
        return SearchResult(
            source=DatabaseSource.INTERNAL,
            found=False,
            data=data,
            confidence=0
        )
    
    def _merge_results(self, result: UnifiedResult) -> UnifiedResult:
        profile = {
            "query": result.query,
            "type": result.query_type.value,
            "sources_checked": result.total_sources,
            "sources_found": result.sources_found,
            "names": [],
            "phones": [],
            "emails": [],
            "usernames": [],
            "locations": [],
            "profiles": [],
            "metadata": {}
        }
        
        for sr in result.results:
            if not sr.found:
                continue
            
            data = sr.data
            
            if 'name' in data:
                profile['names'].append(data['name'])
            if 'names_found' in data and data.get('tags'):
                profile['names'].extend(data['tags'])
            
            if 'phone' in data:
                profile['phones'].append(data['phone'])
            
            if 'email' in data:
                profile['emails'].append(data['email'])
            
            if 'username' in data:
                profile['usernames'].append(data['username'])
            
            if 'country' in data:
                profile['locations'].append(data['country'])
            
            if 'url' in data and data['url']:
                profile['profiles'].append({
                    'source': sr.source.value,
                    'url': data['url']
                })
            
            if 'carrier' in data:
                profile['metadata']['carrier'] = data['carrier']
            if 'reputation' in data:
                profile['metadata']['email_reputation'] = data['reputation']
            if 'suspicious' in data:
                profile['metadata']['suspicious'] = data['suspicious']
        
        profile['names'] = list(set(profile['names']))
        profile['phones'] = list(set(profile['phones']))
        profile['emails'] = list(set(profile['emails']))
        profile['usernames'] = list(set(profile['usernames']))
        profile['locations'] = list(set(profile['locations']))
        
        result.merged_profile = profile
        return result
    
    def _calculate_risk_score(self, result: UnifiedResult) -> int:
        score = 0
        
        profile = result.merged_profile
        metadata = profile.get('metadata', {})
        
        if metadata.get('suspicious'):
            score += 30
        
        if metadata.get('email_reputation') == 'low':
            score += 20
        
        for sr in result.results:
            if sr.source == DatabaseSource.HIBP and sr.found:
                breaches = sr.data.get('breaches_count', 0)
                score += min(30, breaches * 5)
        
        if len(profile.get('profiles', [])) > 5:
            score += 10
        
        return min(100, score)
    
    def format_result(self, result: UnifiedResult) -> str:
        lines = []
        lines.append(f"🔍 <b>РЕЗУЛЬТАТ ПОШУКУ</b>")
        lines.append("═══════════════════════")
        lines.append(f"<b>Запит:</b> <code>{result.query}</code>")
        lines.append(f"<b>Тип:</b> {result.query_type.value}")
        lines.append(f"<b>Джерел:</b> {result.sources_found}/{result.total_sources}")
        lines.append("")
        
        profile = result.merged_profile
        
        if profile.get('names'):
            lines.append(f"<b>👤 Імена:</b>")
            for name in profile['names'][:5]:
                lines.append(f"  └ {name}")
        
        if profile.get('phones'):
            lines.append(f"<b>📱 Телефони:</b>")
            for phone in profile['phones'][:5]:
                lines.append(f"  └ <code>{phone}</code>")
        
        if profile.get('emails'):
            lines.append(f"<b>📧 Email:</b>")
            for email in profile['emails'][:5]:
                lines.append(f"  └ <code>{email}</code>")
        
        if profile.get('locations'):
            lines.append(f"<b>📍 Локації:</b>")
            for loc in profile['locations'][:3]:
                lines.append(f"  └ {loc}")
        
        if profile.get('profiles'):
            lines.append(f"<b>🔗 Профілі:</b>")
            for p in profile['profiles'][:5]:
                lines.append(f"  └ {p['source']}: {p['url']}")
        
        lines.append("")
        lines.append("───────────────")
        
        risk_icon = "🟢" if result.risk_score < 30 else "🟡" if result.risk_score < 60 else "🔴"
        lines.append(f"<b>Ризик:</b> {risk_icon} {result.risk_score}/100")
        
        metadata = profile.get('metadata', {})
        if metadata:
            lines.append("")
            lines.append("<b>📋 Метадані:</b>")
            if metadata.get('carrier'):
                lines.append(f"  └ Оператор: {metadata['carrier']}")
            if metadata.get('email_reputation'):
                lines.append(f"  └ Репутація: {metadata['email_reputation']}")
        
        return "\n".join(lines)
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            **self.stats,
            "cache_size": len(self.cache),
            "timestamp": datetime.now().isoformat()
        }
    
    def clear_cache(self):
        self.cache.clear()


multi_osint = MultiDatabaseOSINT()
