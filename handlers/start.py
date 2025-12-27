import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from database.crud import ProjectCRUD
from core.audit_logger import audit_logger
from core.role_constants import UserRole
from services.user_service import user_service
from keyboards.role_menus import get_description_by_role, get_menu_by_role
from utils.db import async_session

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("start"))
async def start_handler(message: Message, user_role: str = UserRole.GUEST):
    # Log the role we received from middleware for debugging
    logger.info(f"Start handler called. User: {message.from_user.id}, Middleware role: {user_role}")
    
    # Check if user is the admin from config
    from config.settings import ADMIN_ID
    if str(message.from_user.id) == str(ADMIN_ID):
        role = UserRole.ADMIN
        # Use existing method or get_or_create
        db_user = user_service.get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
        if db_user.role != UserRole.ADMIN:
            user_service.set_user_role(message.from_user.id, UserRole.ADMIN)
            logger.info(f"Forced ADMIN role for owner {message.from_user.id}")
    else:
        user = user_service.get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
        role = user.role
        try:
            async with async_session() as session:
                project = await ProjectCRUD.get_by_leader_async(str(message.from_user.id))
            
            if project and role == UserRole.GUEST:
                user_service.set_user_role(message.from_user.id, UserRole.LEADER)
                role = UserRole.LEADER
        except Exception as e:
            logger.error(f"Error checking project: {e}")

    await audit_logger.log_auth(
        user_id=message.from_user.id,
        action="user_start",
        username=message.from_user.username,
        details={"role": role}
    )
    
    await message.answer(
        get_description_by_role(role),
        reply_markup=get_menu_by_role(role),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "user_menu")
async def user_menu_callback(callback: CallbackQuery):
    from aiogram.exceptions import TelegramBadRequest
    user = user_service.get_or_create_user(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    role = user.role if user else UserRole.GUEST
    
    new_text = get_description_by_role(role)
    new_markup = get_menu_by_role(role)
    
    try:
        await callback.message.edit_text(
            new_text,
            reply_markup=new_markup,
            parse_mode="HTML"
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await callback.answer()

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_callback(callback: CallbackQuery):
    from aiogram.exceptions import TelegramBadRequest
    user = user_service.get_or_create_user(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    role = user.role if user else UserRole.GUEST
    
    try:
        await callback.message.edit_text(
            get_description_by_role(role),
            reply_markup=get_menu_by_role(role),
            parse_mode="HTML"
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await callback.answer()

@router.callback_query(F.data == "profile_main")
async def profile_callback(callback: CallbackQuery):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    user = user_service.get_or_create_user(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    
    text = f"""══════════════════════════════════════
            👤 ВАШ ПРОФІЛЬ
══════════════════════════════════════

<b>📋 ІНФОРМАЦІЯ ОБЛІКОВОГО ЗАПИСУ:</b>
├ 🆔 ID: <code>{callback.from_user.id}</code>
├ 👤 Username: @{callback.from_user.username or 'не вказано'}
├ 📝 Ім'я: {callback.from_user.first_name or 'Не вказано'}
├ 🎭 Роль: <b>{user.role.upper() if user else 'GUEST'}</b>
└ 📅 Реєстрація: {user.created_at.strftime('%d.%m.%Y') if user and user.created_at else 'N/A'}
══════════════════════════════════════"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад до меню", callback_data="back_to_menu")]
    ])
    
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except:
        pass
    await callback.answer()

@router.callback_query(F.data == "texting_main")
async def texting_callback(callback: CallbackQuery):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    text = """<b>✍️ ТЕКСТОВКИ</b>
<i>Бібліотека шаблонів повідомлень</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>📚 КАТЕГОРІЇ:</b>
├ 💼 Бізнес-пропозиції
├ 🎁 Акції та знижки
├ 📢 Інформаційні
└ 🔥 Гарячі оффери

<b>🤖 AI-РЕДАКТОР:</b>
Автоматичний рерайт для обходу спам-фільтрів

━━━━━━━━━━━━━━━━━━━━━━━

<i>Розділ у розробці...</i>"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])
    
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except:
        pass
    await callback.answer()

@router.callback_query(F.data == "settings_main")
async def settings_callback(callback: CallbackQuery):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    text = """<b>⚙️ НАЛАШТУВАННЯ ПРОЕКТУ</b>
<i>Конфігурація вашого проекту</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>🔧 ДОСТУПНІ ОПЦІЇ:</b>
├ 📊 Інтервали розсилок
├ 🔔 Сповіщення
├ 🛡️ Безпека
└ 🤖 Налаштування ботів

━━━━━━━━━━━━━━━━━━━━━━━"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])
    
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except:
        pass
    await callback.answer()

@router.callback_query(F.data == "warming_main")
async def warming_callback(callback: CallbackQuery):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    text = """<b>🔥 ПРОГРІВ АКАУНТІВ</b>
<i>Автоматичний прогрів ботів</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 СТАТУС ПРОГРІВУ:</b>
├ 🤖 Боти в процесі: <b>0</b>
├ ✅ Прогріто: <b>0</b>
├ ⏳ В черзі: <b>0</b>
└ 🛡️ Режим: <b>Безпечний</b>

<b>⚙️ НАЛАШТУВАННЯ:</b>
├ Інтервал дій: 30-120 сек
├ Дій на день: 10-50
└ Тип активності: Чати + Канали

━━━━━━━━━━━━━━━━━━━━━━━

<i>Запустіть прогрів для підвищення живучості ботів</i>"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Запустити прогрів", callback_data="warming_start")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])
    
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except:
        pass
    await callback.answer()

@router.callback_query(F.data == "support")
async def support_callback(callback: CallbackQuery):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    text = """<b>💬 ПІДТРИМКА</b>
<i>Служба технічної підтримки</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>📞 СПОСОБИ ЗВ'ЯЗКУ:</b>
├ 💬 Telegram: @support
├ 📧 Email: support@shadow.io
└ 🎫 Тікет-система

<b>⏰ ГОДИНИ РОБОТИ:</b>
├ Пн-Пт: 09:00 - 21:00
└ Сб-Нд: 10:00 - 18:00

<b>⚡ ТЕРМІНОВІ ПИТАННЯ:</b>
Середній час відповіді: 15 хвилин

━━━━━━━━━━━━━━━━━━━━━━━"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎫 Створити тікет", callback_data="ticket_create")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])
    
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except:
        pass
    await callback.answer()

@router.callback_query(F.data == "warming_start")
async def warming_start_callback(callback: CallbackQuery):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    text = """<b>🔥 ПРОГРІВ ЗАПУЩЕНО</b>

━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 СТАТУС:</b>
├ 🔄 Прогрів активний
├ ⏱ Час початку: зараз
└ 🤖 Боти в процесі: 0

<b>⚙️ ПАРАМЕТРИ:</b>
├ Інтервал: 30-120 сек
├ Дії/день: 10-50
└ Режим: Безпечний

━━━━━━━━━━━━━━━━━━━━━━━

<i>Прогрів виконується у фоновому режимі</i>"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏹ Зупинити", callback_data="warming_stop")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="warming_main")]
    ])
    
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except:
        pass
    await callback.answer("🔥 Прогрів запущено!", show_alert=True)

@router.callback_query(F.data == "warming_stop")
async def warming_stop_callback(callback: CallbackQuery):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Запустити прогрів", callback_data="warming_start")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])
    
    try:
        await callback.message.edit_text("⏹ <b>Прогрів зупинено</b>", reply_markup=kb, parse_mode="HTML")
    except:
        pass
    await callback.answer("⏹ Прогрів зупинено", show_alert=True)
