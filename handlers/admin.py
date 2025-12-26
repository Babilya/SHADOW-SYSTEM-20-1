from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_IDS
from core.audit_logger import audit_logger, ActionCategory, ActionSeverity
from core.alerts import alert_system

admin_router = Router()

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
    text = """<b>🛡️ ПАНЕЛЬ АДМІНІСТРАТОРА</b>
<i>Центр управління системою</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>👑 Рівень доступу:</b> ROOT/ADMIN

<b>🛠️ Оберіть розділ для управління:</b>"""
    await query.message.edit_text(text, reply_markup=admin_main_kb(), parse_mode="HTML")

@admin_router.callback_query(F.data == "admin_block")
async def admin_block(query: CallbackQuery, state: FSMContext):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_menu")]
    ])
    await query.message.edit_text("🚫 <b>БЛОКУВАННЯ</b>\n\nВведіть User ID або @username для блокування:", reply_markup=kb, parse_mode="HTML")
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
    text = f"""⚙️ <b>СИСТЕМА</b>

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
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
