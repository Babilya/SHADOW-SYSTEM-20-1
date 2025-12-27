from aiogram import F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from . import admin_router
from .utils import safe_edit_message

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

───────────────

<b>📊 СТАТИСТИКА:</b>
├ 📥 Нових заявок: <b>0</b>
├ ⏳ На розгляді: <b>0</b>
├ ✅ Схвалено: <b>0</b>
└ ❌ Відхилено: <b>0</b>

───────────────

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

───────────────

<b>📊 СТАТИСТИКА КЛЮЧІВ:</b>
├ 🟢 Активних: <b>0</b>
├ ⏳ Очікують активації: <b>0</b>
├ 🔴 Використаних: <b>0</b>
└ ⛔ Анульованих: <b>0</b>

<b>🎯 ФОРМАТИ КЛЮЧІВ:</b>
├ <code>SHADOW-XXXX-XXXX</code> - Стандарт
└ <code>SHADOW-INV-XXXX</code> - Інвайт

───────────────"""
    
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

───────────────

<code>{key_code}</code>

───────────────

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
