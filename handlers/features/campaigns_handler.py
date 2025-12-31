import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from database.repositories.campaign_repository import CampaignRepository
from database.db import get_session

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("campaigns"))
async def cmd_campaigns(message: Message):
    """List user campaigns"""
    try:
        async with get_session() as session:
            repo = CampaignRepository(session)
            campaigns = await repo.get_user_campaigns(message.from_user.id)
            
            if not campaigns:
                await message.answer("❌ Кампанії не знайдені")
                return
            
            text = "📊 <b>Ваші кампанії:</b>\n\n"
            for camp in campaigns:
                text += (
                    f"<b>{camp.name}</b>\n"
                    f"Статус: {camp.status.value}\n"
                    f"Видано: {camp.sent_count}/{camp.total_targets}\n"
                    f"Успішних: {camp.success_count}\n"
                    f"─────────────\n"
                )
            
            await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error listing campaigns: {e}")
        await message.answer(f"❌ Помилка: {e}")

@router.message(Command("new_campaign"))
async def cmd_new_campaign(message: Message):
    """Create new campaign"""
    await message.answer(
        "📝 <b>Нова кампанія</b>\n\n"
        "Надішліть назву кампанії:",
        parse_mode="HTML"
    )

@router.message(Command("running"))
async def cmd_running_campaigns(message: Message):
    """Show running campaigns"""
    try:
        async with get_session() as session:
            repo = CampaignRepository(session)
            running = await repo.get_running_campaigns()
            
            text = f"🔴 <b>Активних кампаній: {len(running)}</b>\n\n"
            for camp in running:
                progress = (camp.sent_count / camp.total_targets * 100) if camp.total_targets > 0 else 0
                text += (
                    f"📌 {camp.name}\n"
                    f"Прогрес: {progress:.1f}% ({camp.sent_count}/{camp.total_targets})\n\n"
                )
            
            await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error getting running campaigns: {e}")
        await message.answer(f"❌ Помилка: {e}")
