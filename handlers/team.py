from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

team_router = Router()

def team_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Менеджери", callback_data="list_managers")],
        [InlineKeyboardButton(text="➕ Додати менеджера", callback_data="add_manager")],
        [InlineKeyboardButton(text="⭐ Рейтинг", callback_data="manager_rating")],
        [InlineKeyboardButton(text="📊 Активність", callback_data="team_activity")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")],
    ])

def team_description() -> str:
    return """<b>👥 ГІБРИДНЕ УПРАВЛІННЯ КОМАНДОЮ</b>

<b>👥 Менеджери</b>
Список всіх менеджерів у вашій команді з статусами, кількістю завершених проектів та активністю.

<b>➕ Додати менеджера</b>
Пригласити нового менеджера до команди. Встановлення прав доступу та розподіл ролей.

<b>⭐ Рейтинг менеджерів</b>
Система оцінювання за якістю роботи: швидкість виконання, конверсія, точність, задоволення клієнтів.

<b>📊 Активність команди</b>
Статистика діяльності: завдання виконані, середня швидкість, % точності, найактивніші менеджери."""

@team_router.message(Command("team"))
async def team_cmd(message: Message):
    await message.answer("👥 <b>Гібридне управління</b>\n\nВиберіть опцію:", reply_markup=team_kb(), parse_mode="HTML")

@team_router.callback_query(F.data == "team_main")
async def team_menu(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("👥 <b>Гібридне управління</b>\n\nВиберіть опцію:", reply_markup=team_kb(), parse_mode="HTML")

@team_router.callback_query(F.data == "list_managers")
async def list_managers(query: CallbackQuery):
    await query.answer()
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="team_main")]])
    await query.message.edit_text("👥 <b>Менеджери</b>\n\n1. Іван - 45 успішних кампаній\n2. Марія - 38 успішних кампаній\n3. Петро - 22 успішних кампанії", reply_markup=back_kb, parse_mode="HTML")

@team_router.callback_query(F.data == "add_manager")
async def add_manager(query: CallbackQuery):
    await query.answer()
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="team_main")]])
    await query.message.edit_text("➕ Введіть User ID менеджера для додавання", reply_markup=back_kb)

@team_router.callback_query(F.data == "manager_rating")
async def manager_rating(query: CallbackQuery):
    await query.answer()
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="team_main")]])
    await query.message.edit_text("⭐ <b>Рейтинг менеджерів</b>\n\n🥇 Іван: 4.8/5 (Швидкість: 95%, Конверсія: 48%)\n🥈 Марія: 4.6/5\n🥉 Петро: 4.2/5", reply_markup=back_kb, parse_mode="HTML")

@team_router.callback_query(F.data == "team_activity")
async def team_activity(query: CallbackQuery):
    await query.answer()
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="team_main")]])
    await query.message.edit_text("📊 <b>Активність команди</b>\n\nЗавдань виконано: 245\nСередня швидкість: 2.3 год\nПомилок: 3 (98.8% точність)", reply_markup=back_kb, parse_mode="HTML")

