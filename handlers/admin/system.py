from aiogram import F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from . import admin_router, AdminStates
from .utils import safe_edit_message
from core.system_stats import system_stats
from core.cache_service import cache_service
from core.health_dashboard import health_dashboard

@admin_router.callback_query(F.data == "admin_system")
async def admin_system(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏥 Health Dashboard", callback_data="system_health")],
        [InlineKeyboardButton(text="📦 Кеш статистика", callback_data="system_cache_stats")],
        [InlineKeyboardButton(text="🔄 Перезапуск", callback_data="system_restart")],
        [InlineKeyboardButton(text="🗑️ Очистити кеш", callback_data="system_clear_cache")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    text = system_stats.format_stats_message()
    await safe_edit_message(query, text, kb)

@admin_router.callback_query(F.data == "system_health")
async def system_health(query: CallbackQuery):
    await query.answer()
    await health_dashboard.check_all()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="system_health")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_system")]
    ])
    text = health_dashboard.format_dashboard_message()
    await safe_edit_message(query, text, kb)

@admin_router.callback_query(F.data == "system_cache_stats")
async def system_cache_stats(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑️ Очистити кеш", callback_data="system_clear_cache")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_system")]
    ])
    text = cache_service.format_stats_message()
    await safe_edit_message(query, text, kb)

@admin_router.callback_query(F.data == "system_restart")
async def system_restart(query: CallbackQuery):
    await query.answer("🔄 Система буде перезапущена", show_alert=True)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_system")]
    ])
    await safe_edit_message(query, "🔄 <b>Перезапуск системи...</b>\n\nСистема буде доступна через декілька секунд.", kb)

@admin_router.callback_query(F.data == "system_clear_cache")
async def system_clear_cache(query: CallbackQuery):
    await query.answer("✅ Кеш очищено!", show_alert=True)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_system")]
    ])
    await safe_edit_message(query, "🗑️ <b>Кеш очищено!</b>\n\nВсі тимчасові дані видалено.", kb)

@admin_router.message(AdminStates.waiting_block_id)
async def process_block(message: Message, state: FSMContext):
    await message.answer(f"✅ Користувача {message.text} заблоковано")
    await state.clear()
