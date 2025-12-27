from aiogram import F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from . import admin_router, AdminStates
from .utils import safe_edit_message

@admin_router.callback_query(F.data == "admin_roles")
async def admin_roles(query: CallbackQuery, state: FSMContext):
    await query.answer()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Призначити роль", callback_data="admin_set_role")],
        [InlineKeyboardButton(text="📋 Список користувачів", callback_data="admin_users_list")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    
    text = """<b>🔄 УПРАВЛІННЯ РОЛЯМИ</b>
<i>Призначення та зміна ролей користувачів</i>

───────────────

<b>📊 ДОСТУПНІ РОЛІ:</b>
├ 👤 <b>GUEST</b> - Гостьовий доступ
├ 👷 <b>MANAGER</b> - Менеджер проекту
├ 👑 <b>LEADER</b> - Лідер/Власник
└ 🛡️ <b>ADMIN</b> - Адміністратор

<b>⚙️ ОПЦІЇ:</b>"""
    
    await safe_edit_message(query, text, kb)

@admin_router.callback_query(F.data == "admin_set_role")
async def admin_set_role(query: CallbackQuery, state: FSMContext):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_roles")]
    ])
    await safe_edit_message(query, "🔄 <b>ЗМІНА РОЛІ</b>\n\nВведіть Telegram ID користувача:", kb)
    await state.set_state(AdminStates.waiting_role_user_id)

@admin_router.callback_query(F.data == "admin_users_list")
async def admin_users_list(query: CallbackQuery):
    await query.answer()
    from services.user_service import user_service
    users = user_service.get_all_users()
    
    text = "<b>📋 СПИСОК КОРИСТУВАЧІВ</b>\n\n"
    for u in users[:20]:
        role_emoji = {"admin": "🛡️", "leader": "👑", "manager": "👷", "guest": "👤"}.get(u.role, "👤")
        text += f"{role_emoji} <code>{u.telegram_id}</code> - @{u.username or 'N/A'} ({u.role})\n"
    
    if len(users) > 20:
        text += f"\n<i>...та ще {len(users) - 20} користувачів</i>"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_roles")]
    ])
    await safe_edit_message(query, text, kb)

@admin_router.message(AdminStates.waiting_role_user_id)
async def process_role_user_id(message: Message, state: FSMContext):
    user_id = message.text.strip()
    await state.update_data(target_user_id=user_id)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👤 Guest", callback_data="set_role_guest"),
            InlineKeyboardButton(text="👷 Manager", callback_data="set_role_manager")
        ],
        [
            InlineKeyboardButton(text="👑 Leader", callback_data="set_role_leader"),
            InlineKeyboardButton(text="🛡️ Admin", callback_data="set_role_admin")
        ],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_roles")]
    ])
    await message.answer(f"Оберіть нову роль для користувача <code>{user_id}</code>:", reply_markup=kb, parse_mode="HTML")
    await state.set_state(AdminStates.waiting_role_selection)

@admin_router.callback_query(F.data.startswith("set_role_"), AdminStates.waiting_role_selection)
async def set_user_role(query: CallbackQuery, state: FSMContext):
    await query.answer()
    role = query.data.replace("set_role_", "")
    data = await state.get_data()
    user_id = data.get("target_user_id", "")
    
    from services.user_service import user_service
    user_service.set_user_role(int(user_id), role)
    
    await state.clear()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_roles")]
    ])
    await safe_edit_message(query, f"✅ Роль користувача <code>{user_id}</code> змінено на <b>{role.upper()}</b>", kb)
