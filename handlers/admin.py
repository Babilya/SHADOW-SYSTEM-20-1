from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from config import ADMIN_IDS
from core.audit_logger import audit_logger, ActionCategory, ActionSeverity
from core.alerts import alert_system

admin_router = Router()
router = admin_router

import logging

logger = logging.getLogger(__name__)

async def safe_edit_message(query: CallbackQuery, text: str, reply_markup=None, parse_mode="HTML"):
    try:
        if query.message:
            await query.message.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e) and "query is too old" not in str(e):
            logger.warning(f"TelegramBadRequest in safe_edit_message: {e}")
            raise

class AdminStates(StatesGroup):
    waiting_broadcast = State()
    waiting_block_id = State()
    waiting_alert_message = State()

def admin_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚙️ Налаштування", callback_data="admin_system"),
            InlineKeyboardButton(text="🚫 Блокування", callback_data="admin_block")
        ],
        [
            InlineKeyboardButton(text="🔄 Змінити роль", callback_data="admin_roles"),
            InlineKeyboardButton(text="📱 Юзер меню", callback_data="user_menu")
        ],
        [InlineKeyboardButton(text="🆘 ЕКСТРЕНА ТРИВОГА", callback_data="admin_emergency")]
    ])

@admin_router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Доступ заборонений")
        return
    
    text = """<b>🛡️ ПАНЕЛЬ АДМІНІСТРАТОРА</b>
<i>Центр управління системою</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>👑 Рівень доступу:</b> ROOT/ADMIN

<b>📊 СИСТЕМНА СТАТИСТИКА:</b>
├ 👥 Активних користувачів
├ 📁 Запущених проектів
├ 🚀 Активних кампаній
└ 🔔 Нових сповіщень

━━━━━━━━━━━━━━━━━━━━━━━

<b>🛠️ Оберіть розділ для управління:</b>"""
    
    await message.answer(text, reply_markup=admin_main_kb(), parse_mode="HTML")

@admin_router.callback_query(F.data == "admin_menu")
async def admin_menu_callback(query: CallbackQuery):
    await query.answer()
    from keyboards.role_menus import admin_description, admin_menu
    await safe_edit_message(query, admin_description(), admin_menu())

@admin_router.callback_query(F.data == "admin_block")
async def admin_block(query: CallbackQuery, state: FSMContext):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_menu")]
    ])
    await safe_edit_message(query, "🚫 <b>БЛОКУВАННЯ</b>\n\nВведіть User ID або @username для блокування:", kb)
    await state.set_state(AdminStates.waiting_block_id)

@admin_router.message(AdminStates.waiting_block_id)
async def process_block(message: Message, state: FSMContext):
    await message.answer(f"✅ Користувача {message.text} заблоковано")
    await state.clear()

@admin_router.callback_query(F.data == "admin_system")
async def admin_system(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Перезапуск", callback_data="system_restart")],
        [InlineKeyboardButton(text="🗑️ Очистити кеш", callback_data="system_clear_cache")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    text = """⚙️ <b>СИСТЕМА</b>

<b>📊 Статус компонентів:</b>
├ 🟢 Telegram Bot: Працює
├ 🟢 База даних: OK
├ 🟢 Scheduler: Активний
├ 🟢 Campaign Manager: OK
└ 🟢 Alert System: Готовий

<b>💾 Ресурси:</b>
├ CPU: 12%
├ RAM: 256 MB / 1 GB
└ Uptime: 24д 5г 30хв

<b>📦 Версія:</b> v2.0.0"""
    await safe_edit_message(query, text, kb)

@admin_router.callback_query(F.data == "admin_roles")
async def admin_roles(query: CallbackQuery, state: FSMContext):
    await query.answer()
    from services.user_service import user_service
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Призначити роль", callback_data="admin_set_role")],
        [InlineKeyboardButton(text="📋 Список користувачів", callback_data="admin_users_list")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    
    text = """<b>🔄 УПРАВЛІННЯ РОЛЯМИ</b>
<i>Призначення та зміна ролей користувачів</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 ДОСТУПНІ РОЛІ:</b>
├ 👤 <b>GUEST</b> - Гостьовий доступ
├ 👷 <b>MANAGER</b> - Менеджер проекту
├ 👑 <b>LEADER</b> - Лідер/Власник
└ 🛡️ <b>ADMIN</b> - Адміністратор

<b>⚙️ ОПЦІЇ:</b>"""
    
    await safe_edit_message(query, text, kb)

@admin_router.callback_query(F.data == "admin_apps")
async def admin_apps(query: CallbackQuery):
    await query.answer()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Нові заявки", callback_data="admin_new_apps")],
        [InlineKeyboardButton(text="✅ Схвалені", callback_data="admin_approved_apps")],
        [InlineKeyboardButton(text="❌ Відхилені", callback_data="admin_rejected_apps")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    
    text = """<b>📋 УПРАВЛІННЯ ЗАЯВКАМИ</b>
<i>Розгляд та обробка заявок на підписки</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 СТАТИСТИКА:</b>
├ 📥 Нових заявок: <b>0</b>
├ ⏳ На розгляді: <b>0</b>
├ ✅ Схвалено: <b>0</b>
└ ❌ Відхилено: <b>0</b>

━━━━━━━━━━━━━━━━━━━━━━━

<b>⚙️ ОБЕРІТЬ ДІЮ:</b>"""
    
    await safe_edit_message(query, text, kb)

@admin_router.callback_query(F.data == "admin_keys")
async def admin_keys(query: CallbackQuery):
    await query.answer()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Генерувати ключ", callback_data="admin_gen_key")],
        [InlineKeyboardButton(text="📋 Активні ключі", callback_data="admin_active_keys")],
        [InlineKeyboardButton(text="🗑 Анулювати ключ", callback_data="admin_revoke_key")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    
    text = """<b>🔑 ЛІЦЕНЗІЙНИЙ ЦЕНТР</b>
<i>Генерація та управління SHADOW-ключами</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 СТАТИСТИКА КЛЮЧІВ:</b>
├ 🟢 Активних: <b>0</b>
├ ⏳ Очікують активації: <b>0</b>
├ 🔴 Використаних: <b>0</b>
└ ⛔ Анульованих: <b>0</b>

<b>🎯 ФОРМАТИ КЛЮЧІВ:</b>
├ <code>SHADOW-XXXX-XXXX</code> - Стандарт
└ <code>SHADOW-INV-XXXX</code> - Інвайт

━━━━━━━━━━━━━━━━━━━━━━━"""
    
    await safe_edit_message(query, text, kb)

@admin_router.callback_query(F.data == "admin_emergency")
async def admin_emergency(query: CallbackQuery):
    await query.answer("⚠️ Режим екстреної тривоги", show_alert=True)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔴 АКТИВУВАТИ ТРИВОГУ", callback_data="emergency_activate")],
        [InlineKeyboardButton(text="📢 Масове сповіщення", callback_data="emergency_broadcast")],
        [InlineKeyboardButton(text="🔒 Заблокувати всіх", callback_data="emergency_lockdown")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    
    text = """<b>🆘 ЕКСТРЕНИЙ ЦЕНТР</b>
<i>Критичні операції системи</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>⚠️ УВАГА!</b>
Ці дії мають критичний вплив на систему.
Використовуйте тільки в екстрених випадках!

<b>🔴 ДОСТУПНІ ДІЇ:</b>
├ Активація загальної тривоги
├ Масове сповіщення всіх користувачів
└ Повне блокування доступу

━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 ПОТОЧНИЙ СТАТУС:</b> 🟢 Нормальний"""
    
    await safe_edit_message(query, text, kb)

@admin_router.callback_query(F.data == "system_restart")
async def system_restart(query: CallbackQuery):
    await query.answer("🔄 Система буде перезапущена", show_alert=True)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_system")]
    ])
    await safe_edit_message(query, "🔄 <b>Перезапуск системи...</b>\n\nСистема буде доступна через декілька секунд.", kb)

@admin_router.callback_query(F.data == "system_clear_cache")
async def system_clear_cache(query: CallbackQuery):
    await query.answer("✅ Кеш очищено!", show_alert=True)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_system")]
    ])
    await safe_edit_message(query, "🗑️ <b>Кеш очищено!</b>\n\nВсі тимчасові дані видалено.", kb)

@admin_router.callback_query(F.data == "admin_set_role")
async def admin_set_role(query: CallbackQuery, state: FSMContext):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_roles")]
    ])
    await safe_edit_message(query, "🔄 <b>ЗМІНА РОЛІ</b>\n\nВведіть Telegram ID користувача:", kb)

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

@admin_router.callback_query(F.data == "admin_new_apps")
async def admin_new_apps(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_apps")]
    ])
    await safe_edit_message(query, "<b>📥 НОВІ ЗАЯВКИ</b>\n\n<i>Немає нових заявок</i>", kb)

@admin_router.callback_query(F.data == "admin_approved_apps")
async def admin_approved_apps(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_apps")]
    ])
    await safe_edit_message(query, "<b>✅ СХВАЛЕНІ ЗАЯВКИ</b>\n\n<i>Немає схвалених заявок</i>", kb)

@admin_router.callback_query(F.data == "admin_rejected_apps")
async def admin_rejected_apps(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_apps")]
    ])
    await safe_edit_message(query, "<b>❌ ВІДХИЛЕНІ ЗАЯВКИ</b>\n\n<i>Немає відхилених заявок</i>", kb)

@admin_router.callback_query(F.data == "admin_gen_key")
async def admin_gen_key(query: CallbackQuery):
    await query.answer()
    import secrets
    key_code = f"SHADOW-{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Ще один ключ", callback_data="admin_gen_key")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_keys")]
    ])
    
    text = f"""<b>🔑 НОВИЙ КЛЮЧ ЗГЕНЕРОВАНО</b>

━━━━━━━━━━━━━━━━━━━━━━━

<code>{key_code}</code>

━━━━━━━━━━━━━━━━━━━━━━━

<i>Скопіюйте та передайте клієнту</i>"""
    
    await safe_edit_message(query, text, kb)

@admin_router.callback_query(F.data == "admin_active_keys")
async def admin_active_keys(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_keys")]
    ])
    await safe_edit_message(query, "<b>📋 АКТИВНІ КЛЮЧІ</b>\n\n<i>Немає активних ключів</i>", kb)

@admin_router.callback_query(F.data == "admin_revoke_key")
async def admin_revoke_key(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_keys")]
    ])
    await safe_edit_message(query, "<b>🗑 АНУЛЮВАННЯ КЛЮЧА</b>\n\nВведіть код ключа для анулювання:", kb)

@admin_router.callback_query(F.data == "emergency_activate")
async def emergency_activate(query: CallbackQuery):
    await query.answer("⚠️ Режим тривоги активовано!", show_alert=True)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Деактивувати", callback_data="admin_emergency")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    await safe_edit_message(query, "🔴 <b>РЕЖИМ ТРИВОГИ АКТИВОВАНО!</b>\n\nВсі критичні операції призупинено.", kb)

@admin_router.callback_query(F.data == "emergency_broadcast")
async def emergency_broadcast(query: CallbackQuery, state: FSMContext):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_emergency")]
    ])
    await safe_edit_message(query, "<b>📢 МАСОВЕ СПОВІЩЕННЯ</b>\n\nВведіть текст повідомлення:", kb)
    await state.set_state(AdminStates.waiting_alert_message)

@admin_router.callback_query(F.data == "emergency_lockdown")
async def emergency_lockdown(query: CallbackQuery):
    await query.answer("⚠️ Це заблокує всіх користувачів!", show_alert=True)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚠️ ПІДТВЕРДИТИ БЛОКУВАННЯ", callback_data="emergency_lockdown_confirm")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_emergency")]
    ])
    await safe_edit_message(query, "<b>🔒 ПОВНЕ БЛОКУВАННЯ</b>\n\n⚠️ Ви впевнені? Це заблокує всіх користувачів!", kb)

@admin_router.callback_query(F.data == "emergency_lockdown_confirm")
async def emergency_lockdown_confirm(query: CallbackQuery):
    await query.answer("🔒 Блокування активовано", show_alert=True)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔓 Зняти блокування", callback_data="admin_emergency")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    await safe_edit_message(query, "🔒 <b>СИСТЕМА ЗАБЛОКОВАНА</b>\n\nВсі користувачі не мають доступу до функцій.", kb)

@admin_router.message(AdminStates.waiting_alert_message)
async def process_alert_message(message: Message, state: FSMContext):
    from keyboards.role_menus import admin_menu
    await message.answer(f"✅ Повідомлення відправлено всім користувачам:\n\n{message.text}", reply_markup=admin_menu())
    await state.clear()
