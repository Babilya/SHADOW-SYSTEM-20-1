from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

botnet_router = Router()

@botnet_router.message(Command("botnet"))
async def botnet_menu(message: Message):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Додати ботів", callback_data="add_bots")],
        [InlineKeyboardButton(text="📋 Мої боти", callback_data="list_bots")],
        [InlineKeyboardButton(text="🔄 Ротація проксі", callback_data="proxy_rotation")],
        [InlineKeyboardButton(text="🔥 Прогрів ботів", callback_data="warm_bots")],
    ])
    await message.answer("🤖 <b>Управління Botnet</b>\n\nВиберіть опцію:", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "add_bots")
async def add_bots(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("➕ Завантажте CSV з номерами телефонів для додавання ботів")

@botnet_router.callback_query(F.data == "list_bots")
async def list_bots(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("📋 <b>Ваші боти</b>\n\nВсього: 45\nАктивних: 38\nІнактивних: 7", parse_mode="HTML")

@botnet_router.callback_query(F.data == "proxy_rotation")
async def proxy_rotation(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("🔄 <b>Ротація проксі</b>\n\nПроксі активні: 12\nПерероблено: 5", parse_mode="HTML")

@botnet_router.callback_query(F.data == "warm_bots")
async def warm_bots(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("🔥 <b>Прогрів ботів</b>\n\nПрогрівання запущено...\nПрогріто: 28/45", parse_mode="HTML")
