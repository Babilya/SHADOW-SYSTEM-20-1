from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def main_menu() -> InlineKeyboardMarkup:
    """Головне меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 Розсилка", callback_data="mailing")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton(text="🤖 Автовідповідь", callback_data="autoreply")],
        [InlineKeyboardButton(text="💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton(text="⚙️ Налаштування", callback_data="settings")],
    ])

def subscription_menu() -> InlineKeyboardMarkup:
    """Меню підписок"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Upgrade to Premium", callback_data="upgrade_premium")],
        [InlineKeyboardButton(text="👑 Upgrade to Elite", callback_data="upgrade_elite")],
        [InlineKeyboardButton(text="📋 Мої ліміти", callback_data="limits")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")],
    ])

def settings_menu() -> InlineKeyboardMarkup:
    """Меню налаштувань"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👻 Привидний режим", callback_data="ghost_mode")],
        [InlineKeyboardButton(text="🔔 Сповіщення", callback_data="notifications")],
        [InlineKeyboardButton(text="🌐 Мова", callback_data="language")],
        [InlineKeyboardButton(text="🔐 Безпека", callback_data="security")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")],
    ])

def payment_methods() -> InlineKeyboardMarkup:
    """Способи оплати"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Карта", callback_data="card_payment")],
        [InlineKeyboardButton(text="🔗 Liqpay", callback_data="liqpay_payment")],
        [InlineKeyboardButton(text="🪙 Крипто", callback_data="crypto_payment")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")],
    ])

def confirm_keyboard() -> InlineKeyboardMarkup:
    """Підтвердження"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Так", callback_data="confirm_yes"),
            InlineKeyboardButton(text="❌ Ні", callback_data="confirm_no"),
        ]
    ])

def cancel_keyboard() -> ReplyKeyboardMarkup:
    """Скасування"""
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="❌ Скасувати")]
    ], resize_keyboard=True)
