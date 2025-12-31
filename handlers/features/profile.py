"""
Profile Handlers - управління профілем користувача
SHADOW SYSTEM iO v2.0
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.profile_service import profile_service
from core.role_constants import UserRole

logger = logging.getLogger(__name__)
profile_router = Router()


class ProfileStates(StatesGroup):
    waiting_name = State()
    waiting_email = State()
    waiting_project_name = State()
    waiting_project_goals = State()
    waiting_password = State()
    waiting_password_confirm = State()
    waiting_current_password = State()
    waiting_session_timeout = State()


def profile_menu_kb(has_password: bool = False) -> InlineKeyboardMarkup:
    """Клавіатура меню профілю"""
    buttons = [
        [InlineKeyboardButton(text="✏️ Редагувати ім'я", callback_data="profile_edit_name")],
        [InlineKeyboardButton(text="📧 Редагувати email", callback_data="profile_edit_email")],
        [InlineKeyboardButton(text="🏢 Редагувати проект", callback_data="profile_edit_project")],
        [InlineKeyboardButton(text="🎯 Редагувати цілі", callback_data="profile_edit_goals")],
    ]
    
    if has_password:
        buttons.append([
            InlineKeyboardButton(text="🔐 Змінити пароль", callback_data="profile_change_password"),
            InlineKeyboardButton(text="🔓 Вимкнути пароль", callback_data="profile_disable_password")
        ])
        buttons.append([InlineKeyboardButton(text="⏱️ Таймаут сесії", callback_data="profile_session_timeout")])
    else:
        buttons.append([InlineKeyboardButton(text="🔐 Встановити пароль", callback_data="profile_set_password")])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_start")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def back_to_profile_kb() -> InlineKeyboardMarkup:
    """Кнопка назад до профілю"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад до профілю", callback_data="my_profile")]
    ])


@profile_router.callback_query(F.data.in_({"my_profile", "profile_main"}))
async def show_profile(query: CallbackQuery, state: FSMContext):
    """Показати профіль"""
    await query.answer()
    await state.clear()
    
    telegram_id = str(query.from_user.id)
    profile = await profile_service.get_or_create_profile(
        telegram_id,
        display_name=query.from_user.full_name
    )
    
    text = profile_service.format_profile(profile)
    kb = profile_menu_kb(profile.password_enabled)
    
    try:
        await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await query.message.answer(text, reply_markup=kb, parse_mode="HTML")


@profile_router.callback_query(F.data == "profile_edit_name")
async def edit_name_start(query: CallbackQuery, state: FSMContext):
    """Редагування імені"""
    await query.answer()
    await state.set_state(ProfileStates.waiting_name)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="my_profile")]
    ])
    await query.message.edit_text(
        "✏️ <b>Редагування імені</b>\n\n"
        "Введіть нове ім'я (як вас називати):",
        reply_markup=kb,
        parse_mode="HTML"
    )


@profile_router.message(ProfileStates.waiting_name)
async def edit_name_save(message: Message, state: FSMContext):
    """Зберегти ім'я"""
    await profile_service.update_profile(
        str(message.from_user.id),
        display_name=message.text[:100]
    )
    await state.clear()
    await message.answer(
        f"✅ Ім'я оновлено: <b>{message.text[:100]}</b>",
        reply_markup=back_to_profile_kb(),
        parse_mode="HTML"
    )


@profile_router.callback_query(F.data == "profile_edit_email")
async def edit_email_start(query: CallbackQuery, state: FSMContext):
    """Редагування email"""
    await query.answer()
    await state.set_state(ProfileStates.waiting_email)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="my_profile")]
    ])
    await query.message.edit_text(
        "📧 <b>Редагування email</b>\n\n"
        "Введіть email адресу:",
        reply_markup=kb,
        parse_mode="HTML"
    )


@profile_router.message(ProfileStates.waiting_email)
async def edit_email_save(message: Message, state: FSMContext):
    """Зберегти email"""
    email = message.text.strip()
    if "@" not in email or "." not in email:
        await message.answer("❌ Введіть коректний email", reply_markup=back_to_profile_kb())
        return
    
    await profile_service.update_profile(str(message.from_user.id), email=email[:255])
    await state.clear()
    await message.answer(
        f"✅ Email оновлено: <b>{email[:255]}</b>",
        reply_markup=back_to_profile_kb(),
        parse_mode="HTML"
    )


@profile_router.callback_query(F.data == "profile_edit_project")
async def edit_project_start(query: CallbackQuery, state: FSMContext):
    """Редагування назви проекту"""
    await query.answer()
    await state.set_state(ProfileStates.waiting_project_name)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="my_profile")]
    ])
    await query.message.edit_text(
        "🏢 <b>Редагування проекту</b>\n\n"
        "Введіть назву вашого проекту/компанії:",
        reply_markup=kb,
        parse_mode="HTML"
    )


@profile_router.message(ProfileStates.waiting_project_name)
async def edit_project_save(message: Message, state: FSMContext):
    """Зберегти назву проекту"""
    await profile_service.update_profile(
        str(message.from_user.id),
        project_name=message.text[:200]
    )
    await state.clear()
    await message.answer(
        f"✅ Проект оновлено: <b>{message.text[:200]}</b>",
        reply_markup=back_to_profile_kb(),
        parse_mode="HTML"
    )


@profile_router.callback_query(F.data == "profile_edit_goals")
async def edit_goals_start(query: CallbackQuery, state: FSMContext):
    """Редагування цілей"""
    await query.answer()
    await state.set_state(ProfileStates.waiting_project_goals)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="my_profile")]
    ])
    await query.message.edit_text(
        "🎯 <b>Редагування цілей</b>\n\n"
        "Опишіть основні цілі використання системи:",
        reply_markup=kb,
        parse_mode="HTML"
    )


@profile_router.message(ProfileStates.waiting_project_goals)
async def edit_goals_save(message: Message, state: FSMContext):
    """Зберегти цілі"""
    await profile_service.update_profile(
        str(message.from_user.id),
        project_goals=message.text[:500]
    )
    await state.clear()
    await message.answer(
        "✅ Цілі оновлено!",
        reply_markup=back_to_profile_kb(),
        parse_mode="HTML"
    )


@profile_router.callback_query(F.data == "profile_set_password")
async def set_password_start(query: CallbackQuery, state: FSMContext):
    """Встановити пароль"""
    await query.answer()
    await state.set_state(ProfileStates.waiting_password)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="my_profile")]
    ])
    await query.message.edit_text(
        "🔐 <b>Встановлення паролю</b>\n\n"
        "Пароль буде запитуватись після тривалої неактивності.\n\n"
        "Введіть новий пароль (мін. 4 символи):",
        reply_markup=kb,
        parse_mode="HTML"
    )


@profile_router.message(ProfileStates.waiting_password)
async def set_password_confirm(message: Message, state: FSMContext):
    """Підтвердження паролю"""
    if len(message.text) < 4:
        await message.answer("❌ Пароль занадто короткий (мін. 4 символи)")
        return
    
    await state.update_data(new_password=message.text)
    await state.set_state(ProfileStates.waiting_password_confirm)
    
    try:
        await message.delete()
    except Exception:
        pass
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="my_profile")]
    ])
    await message.answer(
        "🔐 Підтвердіть пароль (введіть ще раз):",
        reply_markup=kb,
        parse_mode="HTML"
    )


@profile_router.message(ProfileStates.waiting_password_confirm)
async def set_password_save(message: Message, state: FSMContext):
    """Зберегти пароль"""
    data = await state.get_data()
    new_password = data.get("new_password")
    
    if message.text != new_password:
        await message.answer("❌ Паролі не співпадають! Спробуйте знову.")
        await state.set_state(ProfileStates.waiting_password)
        return
    
    await profile_service.set_password(str(message.from_user.id), new_password)
    await profile_service.create_session(str(message.from_user.id))
    await state.clear()
    
    try:
        await message.delete()
    except Exception:
        pass
    
    await message.answer(
        "✅ <b>Пароль встановлено!</b>\n\n"
        "Тепер після 6 годин неактивності система попросить ввести пароль.",
        reply_markup=back_to_profile_kb(),
        parse_mode="HTML"
    )


@profile_router.callback_query(F.data == "profile_change_password")
async def change_password_start(query: CallbackQuery, state: FSMContext):
    """Змінити пароль"""
    await query.answer()
    await state.set_state(ProfileStates.waiting_current_password)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="my_profile")]
    ])
    await query.message.edit_text(
        "🔐 <b>Зміна паролю</b>\n\n"
        "Введіть поточний пароль:",
        reply_markup=kb,
        parse_mode="HTML"
    )


@profile_router.message(ProfileStates.waiting_current_password)
async def change_password_verify(message: Message, state: FSMContext):
    """Перевірити поточний пароль"""
    data = await state.get_data()
    auth_flow = data.get("auth_flow", False)
    
    if not await profile_service.check_password(str(message.from_user.id), message.text):
        await message.answer("❌ Невірний пароль!")
        return
    
    try:
        await message.delete()
    except Exception:
        pass
    
    if auth_flow:
        await profile_service.authenticate(str(message.from_user.id), message.text)
        await state.clear()
        from keyboards.role_menus import get_menu_by_role, get_description_by_role
        from services.user_service import user_service
        user_role = user_service.get_user_role(message.from_user.id)
        menu = get_menu_by_role(user_role)
        description = get_description_by_role(user_role)
        await message.answer(
            f"✅ <b>Автентифікація успішна!</b>\n\n{description}",
            reply_markup=menu,
            parse_mode="HTML"
        )
        return
    
    await state.set_state(ProfileStates.waiting_password)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="my_profile")]
    ])
    await message.answer(
        "✅ Пароль вірний!\n\nТепер введіть новий пароль:",
        reply_markup=kb,
        parse_mode="HTML"
    )


@profile_router.callback_query(F.data == "profile_disable_password")
async def disable_password(query: CallbackQuery):
    """Вимкнути пароль"""
    await query.answer()
    await profile_service.disable_password(str(query.from_user.id))
    
    await query.message.edit_text(
        "🔓 <b>Пароль вимкнено!</b>\n\n"
        "Система більше не буде запитувати пароль.",
        reply_markup=back_to_profile_kb(),
        parse_mode="HTML"
    )


@profile_router.callback_query(F.data == "enter_password")
async def enter_password_start(query: CallbackQuery, state: FSMContext):
    """Введення паролю для автентифікації"""
    await query.answer()
    await state.set_state(ProfileStates.waiting_current_password)
    await state.update_data(auth_flow=True)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="back_to_start")]
    ])
    await query.message.edit_text(
        "🔐 <b>Автентифікація</b>\n\n"
        "Введіть ваш пароль для продовження:",
        reply_markup=kb,
        parse_mode="HTML"
    )


@profile_router.callback_query(F.data == "profile_session_timeout")
async def session_timeout_start(query: CallbackQuery, state: FSMContext):
    """Налаштування таймауту сесії"""
    await query.answer()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1 година", callback_data="timeout_1"),
            InlineKeyboardButton(text="3 години", callback_data="timeout_3"),
        ],
        [
            InlineKeyboardButton(text="6 годин", callback_data="timeout_6"),
            InlineKeyboardButton(text="12 годин", callback_data="timeout_12"),
        ],
        [InlineKeyboardButton(text="24 години", callback_data="timeout_24")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="my_profile")]
    ])
    await query.message.edit_text(
        "⏱️ <b>Таймаут сесії</b>\n\n"
        "Через скільки годин неактивності запитувати пароль?",
        reply_markup=kb,
        parse_mode="HTML"
    )


@profile_router.callback_query(F.data.startswith("timeout_"))
async def set_timeout(query: CallbackQuery):
    """Встановити таймаут"""
    await query.answer()
    hours = int(query.data.split("_")[1])
    
    await profile_service.update_profile(
        str(query.from_user.id),
        session_timeout_hours=hours
    )
    
    await query.message.edit_text(
        f"✅ <b>Таймаут встановлено: {hours} годин</b>\n\n"
        f"Пароль запитуватиметься після {hours} годин неактивності.",
        reply_markup=back_to_profile_kb(),
        parse_mode="HTML"
    )
