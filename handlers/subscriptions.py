from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

subscriptions_router = Router()

def subscriptions_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆓 Free", callback_data="tier_free")],
        [InlineKeyboardButton(text="⭐ Standard", callback_data="tier_standard")],
        [InlineKeyboardButton(text="👑 Premium", callback_data="tier_premium")],
        [InlineKeyboardButton(text="💎 VIP Elite", callback_data="tier_elite")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")],
    ])

@subscriptions_router.message(Command("subscription"))
async def subscription_cmd(message: Message):
    await message.answer("📦 <b>Пакети підписок</b>\n\nВаш поточний: Premium (30 днів залишилось)", reply_markup=subscriptions_kb(), parse_mode="HTML")

@subscriptions_router.callback_query(F.data == "subscription_main")
async def subscription_menu(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("📦 <b>Пакети підписок</b>\n\nВаш поточний: Premium (30 днів залишилось)", reply_markup=subscriptions_kb(), parse_mode="HTML")

@subscriptions_router.callback_query(F.data == "tier_free")
async def tier_free(query: CallbackQuery):
    await query.answer()
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="subscription_main")]])
    await query.message.edit_text("🆓 <b>Free - Безкоштовно</b>\n\nБотів: 5\nРозсилок: 10\nПарсинг: 100\nOSINT: 0", reply_markup=back_kb, parse_mode="HTML")

@subscriptions_router.callback_query(F.data == "tier_standard")
async def tier_standard(query: CallbackQuery):
    await query.answer()
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="subscription_main")]])
    await query.message.edit_text("⭐ <b>Standard - 300 грн/мес</b>\n\nБотів: 50\nРозсилок: 500\nПарсинг: 5000\nOSINT: 50\n\n➡️ Купити", reply_markup=back_kb, parse_mode="HTML")

@subscriptions_router.callback_query(F.data == "tier_premium")
async def tier_premium(query: CallbackQuery):
    await query.answer()
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="subscription_main")]])
    await query.message.edit_text("👑 <b>Premium - 600 грн/мес</b>\n\nБотів: 100\nРозсилок: 5000\nПарсинг: 50000\nOSINT: 500\nAI Sentiment: ✅\n\n➡️ Перейти", reply_markup=back_kb, parse_mode="HTML")

@subscriptions_router.callback_query(F.data == "tier_elite")
async def tier_elite(query: CallbackQuery):
    await query.answer()
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="subscription_main")]])
    await query.message.edit_text("💎 <b>VIP Elite - 1,200 грн/мес</b>\n\nБотів: 500 (необмежено)\nРозсилок: Необмежено\nПарсинг: Необмежено\nOSINT: Необмежено\nAI: Повний доступ\nПріоритетна підтримка\n\n🎁 Бонус: +30% ліміти", reply_markup=back_kb, parse_mode="HTML")
