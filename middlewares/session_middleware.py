"""
Session Middleware - перевірка паролю сесії
SHADOW SYSTEM iO v2.0
"""
import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update
from aiogram.fsm.context import FSMContext

from services.profile_service import profile_service

logger = logging.getLogger(__name__)

EXCLUDED_CALLBACKS = {
    "enter_password",
    "my_profile",
    "profile_main",
    "back_to_start",
    "cancel",
}

EXCLUDED_COMMANDS = {"/start", "/help", "/cancel"}


class SessionPasswordMiddleware(BaseMiddleware):
    """Middleware для перевірки паролю сесії"""
    
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        user_id = None
        
        if isinstance(event, Message):
            if event.from_user:
                user_id = str(event.from_user.id)
                if event.text and event.text.split()[0] in EXCLUDED_COMMANDS:
                    return await handler(event, data)
                    
        elif isinstance(event, CallbackQuery):
            if event.from_user:
                user_id = str(event.from_user.id)
                if event.data in EXCLUDED_CALLBACKS:
                    return await handler(event, data)
        
        if user_id:
            needs_auth = await profile_service.needs_password_check(user_id)
            if needs_auth:
                data["needs_password"] = True
                state: FSMContext = data.get("state")
                if state:
                    current_state = await state.get_state()
                    if current_state and "password" in current_state.lower():
                        return await handler(event, data)
                
                if isinstance(event, CallbackQuery):
                    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                    kb = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔐 Ввести пароль", callback_data="enter_password")]
                    ])
                    await event.answer("🔐 Потрібна автентифікація", show_alert=True)
                    try:
                        await event.message.edit_text(
                            "🔐 <b>Сесія закінчилась</b>\n\n"
                            "Для продовження роботи введіть пароль.",
                            reply_markup=kb,
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass
                    return
                
                elif isinstance(event, Message):
                    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                    kb = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔐 Ввести пароль", callback_data="enter_password")]
                    ])
                    await event.answer(
                        "🔐 <b>Сесія закінчилась</b>\n\n"
                        "Для продовження роботи введіть пароль.",
                        reply_markup=kb,
                        parse_mode="HTML"
                    )
                    return
            
            await profile_service.update_activity(user_id)
        
        return await handler(event, data)
