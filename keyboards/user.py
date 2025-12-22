from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 Botnet", callback_data="botnet_main")],
        [InlineKeyboardButton(text="🔍 OSINT", callback_data="osint_main")],
        [InlineKeyboardButton(text="📊 Аналітика", callback_data="analytics_main")],
        [InlineKeyboardButton(text="👥 Команда", callback_data="team_main")],
        [InlineKeyboardButton(text="📦 Підписки", callback_data="subscription_main")],
        [InlineKeyboardButton(text="💳 Платежі", callback_data="payments_main")],
        [InlineKeyboardButton(text="⚙️ Налаштування", callback_data="settings_main")],
    ])

def subscription_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Standard", callback_data="tier_standard")],
        [InlineKeyboardButton(text="👑 Premium", callback_data="tier_premium")],
        [InlineKeyboardButton(text="💎 Elite", callback_data="tier_elite")],
    ])

def settings_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👻 Привидний режим", callback_data="ghost_mode")],
        [InlineKeyboardButton(text="🔔 Сповіщення", callback_data="notifications")],
        [InlineKeyboardButton(text="🌐 Мова", callback_data="language")],
        [InlineKeyboardButton(text="🔐 Безпека", callback_data="security")],
    ])

def payment_methods() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Карта", callback_data="card_payment")],
        [InlineKeyboardButton(text="🔗 Liqpay", callback_data="liqpay_payment")],
        [InlineKeyboardButton(text="🪙 Крипто", callback_data="crypto_payment")],
    ])
