import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from services.user_service import user_service
from database.models import UserRole

logger = logging.getLogger(__name__)

class RoleMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = None
        telegram_id = None
        username = None
        first_name = None
        
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        
        if user:
            telegram_id = user.id
            username = user.username or ""
            first_name = user.first_name or ""
            
            db_user = user_service.get_or_create_user(telegram_id, username, first_name)
            if db_user:
                from config.settings import ADMIN_ID
                current_id_str = str(telegram_id)
                admin_id_str = str(ADMIN_ID)
                
                if current_id_str == admin_id_str:
                    if db_user.role != UserRole.ADMIN:
                        user_service.set_user_role(telegram_id, UserRole.ADMIN)
                        logger.info(f"Promoted user {telegram_id} to ADMIN")
                        db_user = user_service.get_user(telegram_id)
                
                data['user_role'] = db_user.role if db_user else UserRole.GUEST
                data['db_user'] = db_user
            else:
                data['user_role'] = UserRole.GUEST
                data['db_user'] = None
        else:
            data['user_role'] = UserRole.GUEST
            data['db_user'] = None
        
        # Check if the event is already handled by middleware and has data
        return await handler(event, data)
