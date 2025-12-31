"""
Cache Service - In-memory caching with TTL support
SHADOW SYSTEM iO v2.0
"""
import time
import asyncio
import logging
from typing import Any, Optional, Dict, Callable
from functools import wraps
from datetime import datetime, timedelta
from collections import OrderedDict
import hashlib
import json

logger = logging.getLogger(__name__)


class CacheEntry:
    """Single cache entry with TTL"""
    
    def __init__(self, value: Any, ttl: int = 300):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.hits = 0
    
    @property
    def is_expired(self) -> bool:
        return time.time() - self.created_at > self.ttl
    
    @property
    def remaining_ttl(self) -> int:
        remaining = self.ttl - (time.time() - self.created_at)
        return max(0, int(remaining))


class CacheService:
    """
    High-performance in-memory cache with:
    - TTL support
    - LRU eviction
    - Cache statistics
    - Async support
    """
    
    def __init__(self, max_size: int = 10000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "sets": 0
        }
        self._lock = asyncio.Lock()
        self._started = False
    
    async def start(self):
        """Start cache cleanup task"""
        if not self._started:
            self._started = True
            asyncio.create_task(self._cleanup_loop())
            logger.info("CacheService started")
    
    async def _cleanup_loop(self):
        """Background cleanup of expired entries"""
        while self._started:
            await asyncio.sleep(60)
            await self.cleanup_expired()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._stats["misses"] += 1
                return None
            
            if entry.is_expired:
                del self._cache[key]
                self._stats["misses"] += 1
                return None
            
            self._cache.move_to_end(key)
            entry.hits += 1
            self._stats["hits"] += 1
            return entry.value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        async with self._lock:
            if len(self._cache) >= self.max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._stats["evictions"] += 1
            
            self._cache[key] = CacheEntry(value, ttl or self.default_ttl)
            self._cache.move_to_end(key)
            self._stats["sets"] += 1
            return True
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists and not expired"""
        value = await self.get(key)
        return value is not None
    
    async def get_or_set(
        self, 
        key: str, 
        factory: Callable, 
        ttl: Optional[int] = None
    ) -> Any:
        """Get from cache or compute and store"""
        value = await self.get(key)
        if value is not None:
            return value
        
        if asyncio.iscoroutinefunction(factory):
            value = await factory()
        else:
            value = factory()
        
        await self.set(key, value, ttl)
        return value
    
    async def cleanup_expired(self) -> int:
        """Remove all expired entries"""
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired
            ]
            for key in expired_keys:
                del self._cache[key]
            return len(expired_keys)
    
    async def clear(self) -> int:
        """Clear all cache entries"""
        async with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "hit_rate": round(hit_rate, 2),
            "evictions": self._stats["evictions"],
            "sets": self._stats["sets"]
        }
    
    def format_stats_message(self) -> str:
        """Format stats for display"""
        stats = self.get_stats()
        return f"""📦 <b>КЕШ</b>

├ Розмір: {stats["size"]} / {stats["max_size"]}
├ Hits: {stats["hits"]} | Misses: {stats["misses"]}
├ Hit Rate: {stats["hit_rate"]}%
├ Evictions: {stats["evictions"]}
└ Total Sets: {stats["sets"]}"""


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(ttl: int = 300, prefix: str = ""):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"
            return await cache_service.get_or_set(
                key, 
                lambda: func(*args, **kwargs),
                ttl
            )
        return wrapper
    return decorator


cache_service = CacheService()
