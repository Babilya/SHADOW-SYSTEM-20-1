from aiogram import F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from . import admin_router, AdminStates
from .utils import safe_edit_message

@admin_router.callback_query(F.data == "admin_emergency")
async def admin_emergency(query: CallbackQuery):
    await query.answer("⚠️ Режим екстреної тривоги", show_alert=True)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔴 АКТИВУВАТИ ТРИВОГУ", callback_data="emergency_activate")],
        [InlineKeyboardButton(text="📢 Масове сповіщення", callback_data="emergency_broadcast")],
        [InlineKeyboardButton(text="🔒 Заблокувати всіх", callback_data="emergency_lockdown")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    
    text = """<b>🆘 ЕКСТРЕНИЙ ЦЕНТР</b>
<i>Критичні операції системи</i>
───────────────
<b>⚠️ УВАГА!</b>
Ці дії мають критичний вплив.
Використовуйте в екстрених випадках!

<b>🔴 ДІЇ:</b>
├ Активація тривоги
├ Масове сповіщення
└ Блокування доступу
───────────────
<b>📊 СТАТУС:</b> 🟢 Нормальний"""
    
    await safe_edit_message(query, text, kb)

@admin_router.callback_query(F.data == "emergency_activate")
async def emergency_activate(query: CallbackQuery):
    await query.answer("⚠️ Режим тривоги активовано!", show_alert=True)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Деактивувати", callback_data="admin_emergency")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    await safe_edit_message(query, "🔴 <b>РЕЖИМ ТРИВОГИ АКТИВОВАНО!</b>\n\nВсі критичні операції призупинено.", kb)

@admin_router.callback_query(F.data == "emergency_broadcast")
async def emergency_broadcast(query: CallbackQuery, state: FSMContext):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_emergency")]
    ])
    await safe_edit_message(query, "<b>📢 МАСОВЕ СПОВІЩЕННЯ</b>\n\nВведіть текст повідомлення:", kb)
    await state.set_state(AdminStates.waiting_alert_message)

@admin_router.callback_query(F.data == "emergency_lockdown")
async def emergency_lockdown(query: CallbackQuery):
    await query.answer("⚠️ Це заблокує всіх користувачів!", show_alert=True)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚠️ ПІДТВЕРДИТИ БЛОКУВАННЯ", callback_data="emergency_lockdown_confirm")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_emergency")]
    ])
    await safe_edit_message(query, "<b>🔒 ПОВНЕ БЛОКУВАННЯ</b>\n\n⚠️ Ви впевнені? Це заблокує всіх користувачів!", kb)

@admin_router.callback_query(F.data == "emergency_lockdown_confirm")
async def emergency_lockdown_confirm(query: CallbackQuery):
    await query.answer("🔒 Блокування активовано", show_alert=True)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔓 Зняти блокування", callback_data="admin_emergency")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    await safe_edit_message(query, "🔒 <b>СИСТЕМА ЗАБЛОКОВАНА</b>\n\nВсі користувачі не мають доступу до функцій.", kb)

@admin_router.message(AdminStates.waiting_alert_message)
async def process_alert_message(message: Message, state: FSMContext):
    from keyboards.role_menus import admin_menu
    await message.answer(f"✅ Повідомлення відправлено всім користувачам:\n\n{message.text}", reply_markup=admin_menu())
    await state.clear()
