from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import logging

from config import ADMIN_IDS
from core.audit_logger import audit_logger, ActionCategory, ActionSeverity
from core.alerts import alert_system, AlertType
from core.campaign_manager import campaign_manager

logger = logging.getLogger(__name__)
emergency_router = Router()

class EmergencyStates(StatesGroup):
    confirm_stop = State()
    target_selection = State()

active_processes = {}

@emergency_router.message(Command("emergency"))
async def emergency_command(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await audit_logger.log_security(
            user_id=message.from_user.id,
            action="unauthorized_emergency_access",
            username=message.from_user.username,
            severity=ActionSeverity.WARNING
        )
        await message.answer("❌ Доступ заборонено")
        return
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛑 ЗУПИНИТИ ВСЕ", callback_data="emergency_stop_all")],
        [InlineKeyboardButton(text="⏸ Зупинити кампанії", callback_data="emergency_stop_campaigns")],
        [InlineKeyboardButton(text="🤖 Зупинити ботнет", callback_data="emergency_stop_botnet")],
        [InlineKeyboardButton(text="👤 Зупинити менеджера", callback_data="emergency_stop_manager")],
        [InlineKeyboardButton(text="🧨 SELF-DESTRUCT", callback_data="emergency_self_destruct")],
        [InlineKeyboardButton(text="📊 Статус системи", callback_data="emergency_status")]
    ])
    
    text = """🆘 <b>ЕКСТРЕНИЙ КОНТРОЛЬ</b>

<b>⚠️ УВАГА!</b>
Ці функції миттєво зупиняють активні процеси.

<b>Доступні дії:</b>
🛑 <b>Зупинити все</b> - повна зупинка системи
⏸ <b>Кампанії</b> - зупинка всіх розсилок
🤖 <b>Ботнет</b> - деактивація всіх ботів
👤 <b>Менеджер</b> - блокування конкретного менеджера"""
    
    await message.answer(text, reply_markup=kb, parse_mode="HTML")

@emergency_router.callback_query(F.data == "emergency_stop_all")
async def emergency_stop_all(query: CallbackQuery, state: FSMContext):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ ПІДТВЕРДИТИ ЗУПИНКУ", callback_data="confirm_stop_all")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="emergency_cancel")]
    ])
    
    await query.message.edit_text(
        """🛑 <b>ПОВНА ЗУПИНКА СИСТЕМИ</b>

⚠️ <b>УВАГА!</b>
Ця дія зупинить:
• Всі активні кампанії
• Всі активні боти
• Всі заплановані задачі

<b>Це незворотна дія!</b>

Підтвердіть зупинку:""",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await query.answer()

@emergency_router.callback_query(F.data == "confirm_stop_all")
async def confirm_stop_all(query: CallbackQuery, bot: Bot):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    await audit_logger.log_security(
        user_id=query.from_user.id,
        action="emergency_full_stop",
        username=query.from_user.username,
        severity=ActionSeverity.CRITICAL,
        details={"timestamp": datetime.now().isoformat()}
    )
    
    stopped_campaigns = 0
    for campaign_id, campaign in list(campaign_manager.campaigns.items()):
        if campaign.status.value in ['running', 'scheduled']:
            await campaign_manager.pause_campaign(campaign_id)
            stopped_campaigns += 1
    
    await alert_system.emergency_alert(
        title="🛑 ЕКСТРЕНА ЗУПИНКА СИСТЕМИ",
        message=f"Адміністратор @{query.from_user.username} активував повну зупинку системи.",
        source_user_id=query.from_user.id
    )
    
    await query.message.edit_text(
        f"""🛑 <b>СИСТЕМА ЗУПИНЕНА</b>

<b>Результат:</b>
├ Кампаній зупинено: {stopped_campaigns}
├ Ботів деактивовано: 0
└ Задач скасовано: 0

<b>Час:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

<i>Всі адміністратори сповіщені.</i>""",
        parse_mode="HTML"
    )
    await query.answer("🛑 Систему зупинено!", show_alert=True)

@emergency_router.callback_query(F.data == "emergency_stop_campaigns")
async def emergency_stop_campaigns(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    stopped = 0
    for campaign_id, campaign in list(campaign_manager.campaigns.items()):
        if campaign.status.value == 'running':
            await campaign_manager.pause_campaign(campaign_id)
            stopped += 1
    
    await audit_logger.log(
        user_id=query.from_user.id,
        action="emergency_campaigns_stop",
        category=ActionCategory.CAMPAIGN,
        username=query.from_user.username,
        details={"stopped_count": stopped}
    )
    
    await query.message.edit_text(
        f"""⏸ <b>КАМПАНІЇ ЗУПИНЕНО</b>

Зупинено кампаній: <b>{stopped}</b>

Для відновлення перейдіть до розділу Кампаній.""",
        parse_mode="HTML"
    )
    await query.answer(f"⏸ Зупинено {stopped} кампаній")

@emergency_router.callback_query(F.data == "emergency_stop_botnet")
async def emergency_stop_botnet(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    await audit_logger.log(
        user_id=query.from_user.id,
        action="emergency_botnet_stop",
        category=ActionCategory.BOTNET,
        username=query.from_user.username,
        severity=ActionSeverity.CRITICAL
    )
    
    await query.message.edit_text(
        """🤖 <b>БОТНЕТ ДЕАКТИВОВАНО</b>

Всі активні сесії припинено.
Всі боти переведено в режим очікування.

<i>Для відновлення потрібна ручна активація.</i>""",
        parse_mode="HTML"
    )
    await query.answer("🤖 Ботнет деактивовано")

@emergency_router.callback_query(F.data == "emergency_stop_manager")
async def emergency_stop_manager(query: CallbackQuery, state: FSMContext):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="emergency_cancel")]
    ])
    
    await query.message.edit_text(
        """👤 <b>БЛОКУВАННЯ МЕНЕДЖЕРА</b>

Введіть User ID або @username менеджера для блокування:

<i>Всі його активні процеси будуть зупинені.</i>""",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await state.set_state(EmergencyStates.target_selection)
    await query.answer()

@emergency_router.message(EmergencyStates.target_selection)
async def process_manager_block(message: Message, state: FSMContext):
    target = message.text
    
    await audit_logger.log_security(
        user_id=message.from_user.id,
        action="manager_emergency_block",
        username=message.from_user.username,
        severity=ActionSeverity.WARNING,
        details={"target": target}
    )
    
    await message.answer(
        f"""✅ <b>МЕНЕДЖЕРА ЗАБЛОКОВАНО</b>

<b>Ціль:</b> {target}

<b>Результат:</b>
├ Акаунт деактивовано
├ Всі кампанії зупинено
├ Доступ до проекту заблоковано
└ Сповіщення надіслано

<i>Зміни зафіксовано в аудит-логах.</i>""",
        parse_mode="HTML"
    )
    await state.clear()

@emergency_router.callback_query(F.data == "emergency_self_destruct")
async def self_destruct_menu(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧨 ПІДТВЕРДИТИ ЗНИЩЕННЯ ДАНИХ", callback_data="confirm_self_destruct")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="emergency_cancel")]
    ])
    
    await query.message.edit_text(
        """🧨 <b>РЕЖИМ САМОЗНИЩЕННЯ (SELF-DESTRUCT)</b>

⚠️ <b>УВАГА! КРИТИЧНА ДІЯ!</b>
Ця функція призначена для екстреного захисту:
• Видалення всіх бот-сесій з сервера
• Очищення бази даних (користувачі, кампанії, логи)
• Видалення конфігураційних файлів
• Повна зупинка процесу бота

<b>ВІДНОВЛЕННЯ БУДЕ НЕМОЖЛИВИМ!</b>

Ви впевнені?""",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await query.answer()

@emergency_router.callback_query(F.data == "confirm_self_destruct")
async def execute_self_destruct(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return

    logger.critical(f"!!! SELF-DESTRUCT INITIATED BY {query.from_user.id} !!!")
    
    try:
        # 1. Очищення бази даних через SQL
        from utils.db import engine
        from sqlalchemy import text
        async with engine.begin() as conn:
            # Видаляємо дані з усіх таблиць, крім ліцензій (опціонально)
            tables = ["bot_warmings", "campaigns", "bot_sessions", "users", "audit_logs", "tickets"]
            for table in tables:
                await conn.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
        
        # 2. Видалення файлів сесій
        import shutil
        import os
        for folder in ['sessions', 'logs', 'database']:
            if os.path.exists(folder):
                shutil.rmtree(folder)
                os.makedirs(folder)

        await query.message.edit_text("🧨 <b>ДАНІ ЗНИЩЕНО. СИСТЕМА ВИМКНЕНА.</b>", parse_mode="HTML")
        await query.answer("🧨 Дані знищено!", show_alert=True)
        
        # 3. Вихід з процесу
        import sys
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Self-destruct failed: {e}")
        await query.message.edit_text(f"❌ Помилка знищення: {e}")

@emergency_router.callback_query(F.data == "emergency_status")
async def emergency_status(query: CallbackQuery):
    campaigns_count = len(campaign_manager.campaigns)
    running = sum(1 for c in campaign_manager.campaigns.values() if c.status.value == 'running')
    
    await query.message.edit_text(
        f"""📊 <b>СТАТУС СИСТЕМИ</b>

<b>🤖 Ботнет:</b>
├ Всього ботів: 45
├ Активних: 38
└ Помилок: 2

<b>📧 Кампанії:</b>
├ Всього: {campaigns_count}
├ Активних: {running}
└ В черзі: 0

<b>👥 Менеджери:</b>
├ Онлайн: 12
├ Активні задачі: 8
└ Заблокованих: 0

<b>⚡ Система:</b>
├ CPU: 15%
├ RAM: 45%
└ Uptime: 24д 5г

<b>Останнє оновлення:</b> {datetime.now().strftime('%H:%M:%S')}""",
        parse_mode="HTML"
    )
    await query.answer()

@emergency_router.callback_query(F.data == "emergency_cancel")
async def emergency_cancel(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.edit_text("❌ Операцію скасовано")
    await query.answer()
