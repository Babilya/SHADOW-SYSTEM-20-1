import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from database.repositories.bot_session_repository import BotSessionRepository
from database.models import BotStatus
from database.db import get_session

logger = logging.getLogger(__name__)
bots_router = Router()


@bots_router.message(Command("my_bots"))
async def cmd_my_bots(message: Message):
    """List user's bots"""
    try:
        async with get_session() as session:
            repo = BotSessionRepository(session)
            bots = await repo.get_active_bots_for_user(message.from_user.id)
            
            if not bots:
                await message.answer("❌ Ботів не знайдено")
                return
            
            text = f"🤖 <b>Ваші боти ({len(bots)}):</b>\n\n"
            for bot in bots:
                text += (
                    f"📱 {bot.phone}\n"
                    f"Статус: {bot.status.value}\n"
                    f"Повідомлень: {bot.messages_sent}\n"
                    f"Успішність: {bot.success_rate}%\n"
                    f"─────────────\n"
                )
            
            await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error listing bots: {e}")
        await message.answer(f"❌ Помилка: {e}")


@bots_router.message(Command("add_bot"))
async def cmd_add_bot(message: Message):
    """Add new bot"""
    text = (
        "🤖 <b>Додавання нового бота</b>\n\n"
        "Надішліть сеансовий рядок (session string):\n\n"
        "Як отримати session string?"
    )
    await message.answer(text, parse_mode="HTML")


@bots_router.message(Command("bot_stats"))
async def cmd_bot_stats(message: Message):
    """Show bot statistics"""
    try:
        async with get_session() as session:
            repo = BotSessionRepository(session)
            active_count = await repo.count_by_status_for_user(message.from_user.id, BotStatus.ACTIVE)
            warmup_count = await repo.count_by_status_for_user(message.from_user.id, BotStatus.WARMUP)
            blocked_count = await repo.count_by_status_for_user(message.from_user.id, BotStatus.BLOCKED)
            
            text = (
                f"🤖 <b>Статистика ботів</b>\n\n"
                f"✅ Активних: {active_count}\n"
                f"🔥 На прогріванні: {warmup_count}\n"
                f"🚫 Заблоковано: {blocked_count}\n"
                f"Всього: {active_count + warmup_count + blocked_count}"
            )
            await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error getting bot stats: {e}")
        await message.answer(f"❌ Помилка: {e}")
