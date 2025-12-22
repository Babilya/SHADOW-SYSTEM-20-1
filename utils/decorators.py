from functools import wraps
from aiogram.types import Message, CallbackQuery
from config import ADMIN_IDS
import logging

logger = logging.getLogger(__name__)

def admin_only(func):
    """Декоратор для адміністративних команд"""
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id not in ADMIN_IDS:
            await message.answer("❌ У вас немає доступу до цієї команди")
            logger.warning(f"Спроба несанкціонованого доступу від {message.from_user.id}")
            return
        return await func(message, *args, **kwargs)
    return wrapper

def premium_only(func):
    """Декоратор для преміум користувачів"""
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        # Перевірка статусу підписки
        is_premium = True  # Заглушка - інтегрувати з БД
        if not is_premium:
            await message.answer(
                "❌ Ця функція доступна лише для преміум користувачів\n\n"
                "/subscription - Подробиці про підписки"
            )
            return
        return await func(message, *args, **kwargs)
    return wrapper

def rate_limit(max_calls: int = 5, period: int = 60):
    """Декоратор для обмеження кількості запитів"""
    def decorator(func):
        calls = {}
        
        @wraps(func)
        async def wrapper(message: Message, *args, **kwargs):
            user_id = message.from_user.id
            import time
            current_time = time.time()
            
            if user_id not in calls:
                calls[user_id] = []
            
            # Очищуємо старі виклики
            calls[user_id] = [t for t in calls[user_id] if current_time - t < period]
            
            if len(calls[user_id]) >= max_calls:
                await message.answer("⏱️ Занадто багато запитів. Спробуйте пізніше.")
                return
            
            calls[user_id].append(current_time)
            return await func(message, *args, **kwargs)
        return wrapper
    return decorator

def log_action(action_type: str):
    """Декоратор для логування дій"""
    def decorator(func):
        @wraps(func)
        async def wrapper(message: Message, *args, **kwargs):
            logger.info(
                f"Дія [{action_type}] від користувача {message.from_user.id}: {message.text}"
            )
            return await func(message, *args, **kwargs)
        return wrapper
    return decorator
