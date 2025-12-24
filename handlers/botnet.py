from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

botnet_router = Router()

def botnet_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Додати ботів", callback_data="add_bots")],
        [InlineKeyboardButton(text="📋 Мої боти", callback_data="list_bots")],
        [InlineKeyboardButton(text="🔄 Ротація проксі", callback_data="proxy_rotation")],
        [InlineKeyboardButton(text="🔥 Прогрій ботів", callback_data="warm_bots")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")],
    ])

def botnet_description() -> str:
    return """<b>🤖 УПРАВЛІННЯ BOTNET</b>

<b>➕ Додати ботів</b>
Завантажте CSV файл з номерами телефонів для автоматичного створення та налаштування ботів. Підтримує масове додавання до 1000+ ботів за раз.

<b>📋 Мої боти</b>
Переглядайте весь список ваших активних ботів. Статус кожного, последня активність, вчисленням помилок та логи роботи.

<b>🔄 Ротація проксі</b>
Автоматична ротація IP адрес для уникнення блокування. Підтримує SOCKS5, HTTP, Rotating proxies. Налаштування інтервалів та whitelist.

<b>🔥 Прогрій ботів</b>
Прогрівання ботів перед розсилкою для підвищення успішності. Включає повільне прогрівання та побудову репутації."""

@botnet_router.message(Command("botnet"))
async def botnet_cmd(message: Message):
    await message.answer(botnet_description(), reply_markup=botnet_kb(), parse_mode="HTML")

@botnet_router.callback_query(F.data == "botnet_main")
async def botnet_menu(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text(botnet_description(), reply_markup=botnet_kb(), parse_mode="HTML")

@botnet_router.callback_query(F.data == "add_bots")
async def add_bots(query: CallbackQuery):
    await query.answer()
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]])
    await query.message.edit_text("➕ Завантажте CSV з номерами телефонів для додавання ботів", reply_markup=back_kb)

@botnet_router.callback_query(F.data == "list_bots")
async def list_bots(query: CallbackQuery):
    await query.answer()
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]])
    await query.message.edit_text("📋 <b>Ваші боти</b>\n\nВсього: 45\nАктивних: 38\nІнактивних: 7", reply_markup=back_kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "proxy_rotation")
async def proxy_rotation(query: CallbackQuery):
    await query.answer()
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]])
    await query.message.edit_text("🔄 <b>Ротація проксі</b>\n\nПроксі активні: 12\nПерероблено: 5", reply_markup=back_kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "warm_bots")
async def warm_bots(query: CallbackQuery):
    await query.answer()
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]])
    await query.message.edit_text("🔥 <b>Прогрій ботів</b>\n\nПрогрівання запущено...\nПрогріто: 28/45", reply_markup=back_kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "back_to_menu")
async def botnet_back_to_menu(query: CallbackQuery):
    await query.answer()
    from keyboards.user import main_menu, main_menu_description
    await query.message.edit_text(main_menu_description(), reply_markup=main_menu(), parse_mode="HTML")
