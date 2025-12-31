from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def guest_main_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📦 Тарифи")],
        [KeyboardButton(text="🔐 Авторизація")]
    ], resize_keyboard=True)

def tariffs_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔹 Baseus", callback_data="tariff_baseus")],
        [InlineKeyboardButton(text="🔶 Standard", callback_data="tariff_standard")]
    ])
