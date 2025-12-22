from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
import logging
from typing import Callable, Any, Awaitable

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseMiddleware):
    """Middleware для логування всіх повідомлень"""
    
    async def __call__(
        self,
        handler: Callable[[Message], Awaitable[Any]],
        event: Message,
        data: dict
    ) -> Any:
        user = event.from_user
        logger.info(
            f"Повідомлення від {user.id} (@{user.username}): {event.text}"
        )
        return await handler(event, data)

class UserActionMiddleware(BaseMiddleware):
    """Middleware для відслідковування дій користувачів"""
    
    async def __call__(
        self,
        handler: Callable[[Message], Awaitable[Any]],
        event: Message,
        data: dict
    ) -> Any:
        user = event.from_user
        logger.info(f"Дія користувача {user.id}: {event.text}")
        return await handler(event, data)
