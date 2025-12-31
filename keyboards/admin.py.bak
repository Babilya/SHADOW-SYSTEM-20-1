from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_menu() -> InlineKeyboardMarkup:
    """Адміністративне меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👥 Користувачі", callback_data="admin_users"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton(text="🤖 Боти", callback_data="admin_bots"),
            InlineKeyboardButton(text="🔑 Ліцензії", callback_data="admin_keys_menu")
        ],
        [
            InlineKeyboardButton(text="📝 Кампанії", callback_data="admin_campaigns"),
            InlineKeyboardButton(text="⚙️ Налаштування", callback_data="admin_settings")
        ],
        [
            InlineKeyboardButton(text="📈 Аналітика", callback_data="admin_analytics"),
            InlineKeyboardButton(text="🔐 Безпека", callback_data="admin_security")
        ],
        [InlineKeyboardButton(text="◀️ Повернутись", callback_data="back_to_menu")]
    ])

def broadcast_menu() -> InlineKeyboardMarkup:
    """Меню розсилки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Розсилка всім", callback_data="broadcast_all")],
        [
            InlineKeyboardButton(text="👑 Преміум", callback_data="broadcast_premium"),
            InlineKeyboardButton(text="👥 Лідери", callback_data="broadcast_leaders")
        ],
        [InlineKeyboardButton(text="◀️ Повернутись", callback_data="admin_menu")]
    ])

def confirm_keyboard() -> InlineKeyboardMarkup:
    """Підтвердження для адміна"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Підтвердити", callback_data="admin_confirm"),
            InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_cancel")
        ]
    ])

def users_management_kb() -> InlineKeyboardMarkup:
    """Меню управління користувачами"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔍 Пошук", callback_data="admin_user_search"),
            InlineKeyboardButton(text="📋 Список", callback_data="admin_user_list")
        ],
        [
            InlineKeyboardButton(text="🚫 Заблоковані", callback_data="admin_blocked_users"),
            InlineKeyboardButton(text="👑 Преміум", callback_data="admin_premium_users")
        ],
        [InlineKeyboardButton(text="◀️ Повернутись", callback_data="admin_menu")]
    ])

def keys_management_kb() -> InlineKeyboardMarkup:
    """Меню управління ключами"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Створити ключ", callback_data="admin_key_create")],
        [
            InlineKeyboardButton(text="📋 Активні", callback_data="admin_keys_active"),
            InlineKeyboardButton(text="✅ Використані", callback_data="admin_keys_used")
        ],
        [InlineKeyboardButton(text="◀️ Повернутись", callback_data="admin_menu")]
    ])
