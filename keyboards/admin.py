from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_menu() -> InlineKeyboardMarkup:
    """Адміністративне меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Розсилка", callback_data="broadcast")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="stats_admin")],
        [InlineKeyboardButton(text="👥 Користувачі", callback_data="users")],
        [InlineKeyboardButton(text="📣 Оголошення", callback_data="announce")],
        [InlineKeyboardButton(text="🔧 Обслуговування", callback_data="maintenance")],
    ])

def broadcast_menu() -> InlineKeyboardMarkup:
    """Меню розсилки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Розсилка всім", callback_data="broadcast_all")],
        [InlineKeyboardButton(text="👑 Лише преміум", callback_data="broadcast_premium")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")],
    ])

def confirm_keyboard() -> InlineKeyboardMarkup:
    """Підтвердження для адміна"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Підтвердити", callback_data="admin_confirm"),
            InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_cancel"),
        ]
    ])
