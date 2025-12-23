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

@botnet_router.message(Command("botnet"))
async def botnet_cmd(message: Message):
    await message.answer("🤖 <b>Управління Botnet</b>\n\nВиберіть опцію:", reply_markup=botnet_kb(), parse_mode="HTML")

@botnet_router.callback_query(F.data == "botnet_main")
async def botnet_menu(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("🤖 <b>Управління Botnet</b>\n\nВиберіть опцію:", reply_markup=botnet_kb(), parse_mode="HTML")

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
    await query.message.edit_text("🔥 <b>Прогрів ботів</b>\n\nПрогрівання запущено...\nПрогріто: 28/45", reply_markup=back_kb, parse_mode="HTML")
