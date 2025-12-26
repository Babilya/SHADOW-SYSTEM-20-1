import asyncio
import time
from typing import Dict, Optional
from collections import defaultdict
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TokenBucket:
    def __init__(self, rate: float, capacity: float):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def acquire(self, tokens: float = 1.0) -> bool:
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    async def wait_and_acquire(self, tokens: float = 1.0, timeout: float = 30.0) -> bool:
        start = time.monotonic()
        while time.monotonic() - start < timeout:
            if await self.acquire(tokens):
                return True
            await asyncio.sleep(0.1)
        return False

class RateLimiter:
    def __init__(self):
        self.global_bucket = TokenBucket(rate=30, capacity=30)
        self.user_buckets: Dict[int, TokenBucket] = {}
        self.bot_buckets: Dict[str, TokenBucket] = {}
        self.spam_tracker: Dict[int, list] = defaultdict(list)
        self.blocked_users: set = set()
        self._cleanup_task: Optional[asyncio.Task] = None
    
    def _get_user_bucket(self, user_id: int) -> TokenBucket:
        if user_id not in self.user_buckets:
            self.user_buckets[user_id] = TokenBucket(rate=1, capacity=5)
        return self.user_buckets[user_id]
    
    def _get_bot_bucket(self, bot_id: str) -> TokenBucket:
        if bot_id not in self.bot_buckets:
            self.bot_buckets[bot_id] = TokenBucket(rate=25, capacity=25)
        return self.bot_buckets[bot_id]
    
    async def start(self):
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("RateLimiter started")
    
    async def stop(self):
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
    
    async def _cleanup_loop(self):
        while True:
            await asyncio.sleep(60)
            now = time.time()
            for user_id in list(self.spam_tracker.keys()):
                self.spam_tracker[user_id] = [t for t in self.spam_tracker[user_id] if now - t < 60]
                if not self.spam_tracker[user_id]:
                    del self.spam_tracker[user_id]
    
    async def check_rate_limit(self, user_id: int, bot_id: str = "default") -> tuple:
        if user_id in self.blocked_users:
            return False, "blocked"
        
        now = time.time()
        self.spam_tracker[user_id].append(now)
        recent = [t for t in self.spam_tracker[user_id] if now - t < 10]
        
        if len(recent) > 20:
            self.blocked_users.add(user_id)
            logger.warning(f"User {user_id} blocked for spam")
            return False, "spam_blocked"
        
        if not await self._get_user_bucket(user_id).acquire():
            return False, "user_limit"
        
        if not await self._get_bot_bucket(bot_id).acquire():
            return False, "bot_limit"
        
        if not await self.global_bucket.acquire():
            return False, "global_limit"
        
        return True, "ok"
    
    async def wait_for_slot(self, user_id: int, bot_id: str = "default", timeout: float = 30.0) -> bool:
        if user_id in self.blocked_users:
            return False
        
        tasks = [
            self._get_user_bucket(user_id).wait_and_acquire(timeout=timeout),
            self._get_bot_bucket(bot_id).wait_and_acquire(timeout=timeout),
            self.global_bucket.wait_and_acquire(timeout=timeout)
        ]
        results = await asyncio.gather(*tasks)
        return all(results)
    
    def unblock_user(self, user_id: int):
        self.blocked_users.discard(user_id)
        self.spam_tracker[user_id] = []
        logger.info(f"User {user_id} unblocked")
    
    def is_allowed(self, user_id: int) -> bool:
        now = datetime.now()
        if user_id not in self.spam_tracker:
            self.spam_tracker[user_id] = []
        
        self.spam_tracker[user_id] = [t for t in self.spam_tracker[user_id] 
                                     if isinstance(t, datetime) and now - t < timedelta(seconds=60)]
        
        if len(self.spam_tracker[user_id]) < 30:
            self.spam_tracker[user_id].append(now)
            return True
        return False
    
    def get_stats(self) -> dict:
        return {
            "blocked_users": len(self.blocked_users),
            "tracked_users": len(self.spam_tracker),
            "global_tokens": self.global_bucket.tokens
        }

rate_limiter = RateLimiter()
limiter = rate_limiter
