from aiogram import F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
from config import ADMIN_IDS
from . import admin_router
from .utils import safe_edit_message

async def safe_answer(query: CallbackQuery, text: str = None):
    try:
        await query.answer(text)
    except TelegramBadRequest:
        pass

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
    
    text = """══════════════════════════════════════
      🛡️ ПАНЕЛЬ АДМІНІСТРАТОРА
══════════════════════════════════════
<i>Центр управління системою SHADOW</i>

<b>👑 РІВЕНЬ ДОСТУПУ:</b> ROOT/ADMIN

<b>📊 СИСТЕМНА СТАТИСТИКА:</b>
├ 👥 Активних користувачів у системі
├ 📁 Запущених проектів на моніторингу
├ 🚀 Активних кампаній у виконанні
└ 🔔 Нових сповіщень до обробки
──────────────────────────────────────
<b>🛠️ Оберіть розділ для управління:</b>"""
    
    await message.answer(text, reply_markup=admin_main_kb(), parse_mode="HTML")

@admin_router.callback_query(F.data == "admin_menu")
async def admin_menu_callback(query: CallbackQuery):
    await safe_answer(query)
    from keyboards.role_menus import admin_description, admin_menu
    await safe_edit_message(query, admin_description(), admin_menu())

@admin_router.callback_query(F.data == "user_menu")
async def user_menu_handler(query: CallbackQuery):
    await safe_answer(query)
    from keyboards.role_menus import guest_menu, guest_description
    await safe_edit_message(query, guest_description(), guest_menu())
