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
    if not message.from_user:
        return
    
    logger.info(f"Start handler called. User: {message.from_user.id}, Middleware role: {user_role}")
    
    from config.settings import ADMIN_ID
    user_id = message.from_user.id
    username = message.from_user.username or "unknown"
    first_name = message.from_user.first_name or "User"
    
    if str(user_id) == str(ADMIN_ID):
        role = UserRole.ADMIN
        db_user = user_service.get_or_create_user(user_id, username, first_name)
        if db_user and db_user.role != UserRole.ADMIN:
            user_service.set_user_role(user_id, UserRole.ADMIN)
            logger.info(f"Forced ADMIN role for owner {user_id}")
    else:
        user = user_service.get_or_create_user(user_id, username, first_name)
        role = user.role if user else UserRole.GUEST
        try:
            async with async_session() as session:
                project = await ProjectCRUD.get_by_leader_async(str(user_id))
            
            if project is not None and role == UserRole.GUEST:
                user_service.set_user_role(user_id, UserRole.LEADER)
                role = UserRole.LEADER
        except Exception as e:
            logger.error(f"Error checking project: {e}")

    await audit_logger.log_auth(
        user_id=user_id,
        action="user_start",
        username=username,
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
    
    text = f"""👤 <b>ВАШ ПРОФІЛЬ</b>
───────────────
<b>📋 Обліковий запис:</b>
├ 🆔 <code>{callback.from_user.id}</code>
├ 👤 @{callback.from_user.username or 'не вказано'}
├ 📝 {callback.from_user.first_name or 'Не вказано'}
├ 🎭 <b>{user.role.upper() if user else 'GUEST'}</b>
└ 📅 {user.created_at.strftime('%d.%m.%Y') if user and user.created_at else 'N/A'}"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])
    
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except:
        pass
    await callback.answer()

@router.callback_query(F.data == "texting_main")
async def texting_callback(callback: CallbackQuery):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    text = """✍️ <b>ТЕКСТОВКИ</b>
<i>Бібліотека шаблонів</i>
───────────────
<b>📚 Категорії:</b>
├ 💼 Бізнес
├ 🎁 Акції
├ 📢 Інфо
└ 🔥 Гарячі оффери
───────────────
<b>🤖 AI-редактор:</b>
Рерайт для обходу спаму

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
    
    text = """⚙️ <b>НАЛАШТУВАННЯ</b>
<i>Конфігурація проекту</i>
───────────────
<b>🔧 Опції:</b>
├ 📊 Інтервали
├ 🔔 Сповіщення
├ 🛡️ Безпека
└ 🤖 Боти"""
    
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
    from core.ui_components import ProgressBar
    
    text = f"""🔥 <b>ПРОГРІВ</b>
<i>Автопрогрів ботів</i>
───────────────
<b>📊 Статус:</b>
├ 🤖 В процесі: <b>0</b>
├ ✅ Прогріто: <b>0</b>
├ ⏳ В черзі: <b>0</b>
└ 🛡️ Режим: Безпечний
───────────────
<b>⚙️ Параметри:</b>
├ Інтервал: 30-120 сек
├ Дій/день: 10-50
└ Активність: Чати + Канали

<b>Прогрес:</b> {ProgressBar.render(0)}"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Запустити", callback_data="warming_start")],
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
    
    text = """💬 <b>ПІДТРИМКА</b>
<i>Технічна допомога</i>
───────────────
<b>📞 Контакти:</b>
├ 💬 @support
├ 📧 support@shadow.io
└ 🎫 Тікет-система
───────────────
<b>⏰ Години роботи:</b>
├ Пн-Пт: 09:00-21:00
└ Сб-Нд: 10:00-18:00

<b>⚡ Час відповіді:</b> ~15 хв"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎫 Тікет", callback_data="ticket_create")],
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
    from core.ui_components import ProgressBar
    
    text = f"""🔥 <b>ПРОГРІВ ЗАПУЩЕНО</b>
───────────────
<b>📊 Статус:</b>
├ 🔄 Активний
├ ⏱ Старт: зараз
└ 🤖 Ботів: 0
───────────────
<b>⚙️ Параметри:</b>
├ Інтервал: 30-120 сек
├ Дії/день: 10-50
└ Режим: Безпечний

<b>Прогрес:</b> {ProgressBar.render(25)}

<i>Фоновий режим</i>"""
    
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
        [InlineKeyboardButton(text="▶️ Запустити", callback_data="warming_start")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])
    
    try:
        await callback.message.edit_text("⏹ <b>Прогрів зупинено</b>", reply_markup=kb, parse_mode="HTML")
    except:
        pass
    await callback.answer("⏹ Зупинено", show_alert=True)
