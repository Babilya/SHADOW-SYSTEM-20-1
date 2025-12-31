import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from database.repositories.user_repository import UserRepository
from database.db import get_session

logger = logging.getLogger(__name__)
users_router = Router()


@users_router.message(Command("profile"))
async def cmd_profile(message: Message):
    """Show user profile"""
    try:
        async with get_session() as session:
            repo = UserRepository(session)
            user = await repo.get_by_telegram_id(message.from_user.id)
            
            if not user:
                await message.answer("❌ Профіль не знайдено")
                return
            
            text = (
                f"👤 <b>Ваш профіль</b>\n\n"
                f"ID: <code>{user.telegram_id}</code>\n"
                f"Ім'я: {user.first_name}\n"
                f"Username: @{user.username or 'не задано'}\n"
                f"Роль: {user.role.value}\n"
                f"План: {user.plan.value if user.plan else 'Безплатний'}\n"
                f"Статистика: {user.statistics or {}}\n"
                f"Дата входу: {user.last_login}"
            )
            await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error in profile handler: {e}")
        await message.answer(f"❌ Помилка: {e}")


@users_router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Show user statistics"""
    try:
        async with get_session() as session:
            repo = UserRepository(session)
            user = await repo.get_by_telegram_id(message.from_user.id)
            
            if not user:
                await message.answer("❌ Статистика не знайдена")
                return
            
            stats = user.statistics or {}
            text = (
                f"📊 <b>Статистика</b>\n\n"
                f"Ботів: {stats.get('bots_count', 0)}\n"
                f"Кампаній: {stats.get('campaigns_count', 0)}\n"
                f"Повідомлень: {stats.get('messages_sent', 0)}\n"
                f"Успішність: {stats.get('success_rate', 0)}%\n"
                f"Заробів: {stats.get('total_earnings', 0)}"
            )
            await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error in stats handler: {e}")
        await message.answer(f"❌ Помилка: {e}")
