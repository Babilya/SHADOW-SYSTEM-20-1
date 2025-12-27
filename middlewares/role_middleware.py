from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from services.user_service import user_service
from database.models import UserRole

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
            username = user.username
            first_name = user.first_name
            
            db_user = user_service.get_or_create_user(telegram_id, username, first_name)
            if db_user:
                from config.settings import ADMIN_ID
                # Convert both to string for reliable comparison
                if str(telegram_id) == str(ADMIN_ID) and db_user.role != UserRole.ADMIN:
                    db_user.role = UserRole.ADMIN
                    user_service.update_user(db_user)
                
                data['user_role'] = db_user.role
                data['db_user'] = db_user
            else:
                data['user_role'] = UserRole.GUEST
                data['db_user'] = None
        else:
            data['user_role'] = UserRole.GUEST
            data['db_user'] = None
        
        return await handler(event, data)
