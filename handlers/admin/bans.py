from aiogram import F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from . import admin_router, AdminStates
from .utils import safe_edit_message

@admin_router.callback_query(F.data == "admin_block")
async def admin_block(query: CallbackQuery, state: FSMContext):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_menu")]
    ])
    await safe_edit_message(query, "🚫 <b>БЛОКУВАННЯ</b>\n\nВведіть User ID або @username для блокування:", kb)
    await state.set_state(AdminStates.waiting_block_id)

@admin_router.callback_query(F.data == "bans_menu")
async def bans_menu(query: CallbackQuery):
    await query.answer()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚫 Забанити користувача", callback_data="ban_user")],
        [InlineKeyboardButton(text="📋 Активні бани", callback_data="active_bans")],
        [InlineKeyboardButton(text="📜 Історія банів", callback_data="ban_history")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_menu")]
    ])
    
    text = """<b>🚫 УПРАВЛІННЯ БАНАМИ</b>

───────────────

Система блокування користувачів.

<b>📊 СТАТИСТИКА:</b>
├ 🔴 Активних банів: <b>0</b>
├ ⏳ Тимчасових: <b>0</b>
├ ♾️ Постійних: <b>0</b>
└ 📅 За цей місяць: <b>0</b>

───────────────"""
    
    await safe_edit_message(query, text, kb)

@admin_router.callback_query(F.data == "ban_user")
async def ban_user_handler(query: CallbackQuery, state: FSMContext):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="bans_menu")]
    ])
    await safe_edit_message(query, "🚫 <b>ЗАБАНИТИ КОРИСТУВАЧА</b>\n\nВведіть Telegram ID або @username:", kb)
    await state.set_state(AdminStates.waiting_ban_user)

@admin_router.callback_query(F.data == "active_bans")
async def active_bans_handler(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="bans_menu")]
    ])
    await safe_edit_message(query, "<b>📋 АКТИВНІ БАНИ</b>\n\n<i>Немає активних банів</i>", kb)

@admin_router.callback_query(F.data == "ban_history")
async def ban_history_handler(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="bans_menu")]
    ])
    await safe_edit_message(query, "<b>📜 ІСТОРІЯ БАНІВ</b>\n\n<i>Історія порожня</i>", kb)
