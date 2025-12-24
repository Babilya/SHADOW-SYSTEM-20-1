import logging
from typing import Callable, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, Update
from database.repositories.user_repository import UserRepository
from database.db import get_session
from config import ADMIN_IDS

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    """Authentication and authorization middleware"""
    
    async def __call__(
        self,
        handler: Callable[[Update, dict], Awaitable[Any]],
        event: Update,
        data: dict
    ) -> Any:
        """Process update through middleware"""
        
        # Get user info from message or callback
        user = None
        if hasattr(event, 'message') and event.message:
            user = event.message.from_user
        elif hasattr(event, 'callback_query') and event.callback_query:
            user = event.callback_query.from_user
        
        if not user:
            return await handler(event, data)
        
        try:
            # Check if user exists in database
            async with get_session() as session:
                repo = UserRepository(session)
                db_user = await repo.get_by_telegram_id(user.id)
                
                if not db_user:
                    # Create new user
                    from database.models import User
                    new_user = User(
                        telegram_id=user.id,
                        username=user.username,
                        first_name=user.first_name,
                        last_name=user.last_name
                    )
                    db_user = await repo.create(new_user)
                    logger.info(f"✅ New user created: {user.id}")
                
                # Add user info to data
                data["user_id"] = user.id
                data["db_user"] = db_user
                data["is_admin"] = user.id in ADMIN_IDS
                
        except Exception as e:
            logger.error(f"Auth middleware error: {e}")
            data["user_id"] = user.id
            data["is_admin"] = user.id in ADMIN_IDS
        
        return await handler(event, data)


class RateLimitMiddleware(BaseMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.user_requests = {}
    
    async def __call__(
        self,
        handler: Callable[[Update, dict], Awaitable[Any]],
        event: Update,
        data: dict
    ) -> Any:
        """Process update with rate limiting"""
        
        user = None
        if hasattr(event, 'message') and event.message:
            user = event.message.from_user
        elif hasattr(event, 'callback_query') and event.callback_query:
            user = event.callback_query.from_user
        
        if not user:
            return await handler(event, data)
        
        user_id = user.id
        now = datetime.now()
        
        # Initialize user in tracking dict
        if user_id not in self.user_requests:
            self.user_requests[user_id] = []
        
        # Remove old requests
        self.user_requests[user_id] = [
            req_time for req_time in self.user_requests[user_id]
            if (now - req_time).seconds < self.time_window
        ]
        
        # Check rate limit
        if len(self.user_requests[user_id]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            if event.message:
                await event.message.answer(
                    "⚠️ Забагато запитів. Спробуйте пізніше."
                )
            return
        
        # Add current request
        self.user_requests[user_id].append(now)
        
        return await handler(event, data)


from datetime import datetime
