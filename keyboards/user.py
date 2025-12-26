from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu() -> InlineKeyboardMarkup:
    """Головне меню - комбіновані кнопки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🤖 Боти", callback_data="botnet_main"),
            InlineKeyboardButton(text="🔍 OSINT", callback_data="osint_main")
        ],
        [
            InlineKeyboardButton(text="📝 Кампанії", callback_data="campaigns_main"),
            InlineKeyboardButton(text="📊 Аналітика", callback_data="analytics_main")
        ],
        [
            InlineKeyboardButton(text="🔑 Ліцензія", callback_data="license_main"),
            InlineKeyboardButton(text="📦 Тарифи", callback_data="subscription_main")
        ],
        [
            InlineKeyboardButton(text="👥 Команда", callback_data="team_main"),
            InlineKeyboardButton(text="⚙️ Налаштування", callback_data="settings_main")
        ],
        [
            InlineKeyboardButton(text="🔥 Прогрів", callback_data="warming_menu"),
            InlineKeyboardButton(text="📅 Планувальник", callback_data="scheduler_menu")
        ],
        [
            InlineKeyboardButton(text="🌍 Гео-скан", callback_data="geo_menu"),
            InlineKeyboardButton(text="📝 Текстовки", callback_data="texting_main")
        ],
        [
            InlineKeyboardButton(text="📚 Довідка", callback_data="help_main"),
            InlineKeyboardButton(text="👤 Профіль", callback_data="profile_main")
        ]
    ])

def main_menu_description() -> str:
    """Розширений опис з проектом"""
    return """<b>🌟 SHADOW SYSTEM iO v2.0</b>
<i>Комплексна платформа для управління ботами та маркетинг-кампаніями</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>🤖 BOTNET</b>
├ Додавання ботів через CSV
├ Моніторинг статусу та активності
├ Ротація проксі (SOCKS5, HTTP)
└ Прогрів ботів перед розсилкою

<b>🔍 OSINT & ПАРСИНГ</b>
├ Геосканування за локацією
├ Аналіз профілів користувачів
├ Парсинг чатів та каналів
└ Експорт даних у CSV

<b>📝 КАМПАНІЇ</b>
├ Створення та управління розсилками
├ Таргетинг аудиторії
├ A/B тестування
└ Статистика ефективності

<b>📊 АНАЛІТИКА</b>
├ AI-дашборд кампаній
├ Sentiment-аналіз відповідей
├ Прогноз ризиків блокування
└ Експорт звітів PDF/Excel

<b>🔑 ЛІЦЕНЗІЯ</b>
├ Статус активації
├ Термін дії ключа
└ Інформація про тариф

<b>👥 КОМАНДА</b>
├ Менеджери проекту
├ Розподіл завдань
└ Рейтинг ефективності

━━━━━━━━━━━━━━━━━━━━━━━

<b>💡 Порада:</b>
<i>Технічна підтримка доступна 24/7</i>"""

def license_menu() -> InlineKeyboardMarkup:
    """Меню ліцензії"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статус ліцензії", callback_data="license_status")],
        [
            InlineKeyboardButton(text="🔑 Ввести ключ", callback_data="enter_key"),
            InlineKeyboardButton(text="📝 Заявка", callback_data="new_application")
        ],
        [InlineKeyboardButton(text="◀️ Повернутись", callback_data="back_to_menu")]
    ])

def subscription_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📦 Базовий", callback_data="tier_baseus"),
            InlineKeyboardButton(text="⭐ Стандарт", callback_data="tier_standard")
        ],
        [
            InlineKeyboardButton(text="👑 Преміум", callback_data="tier_premium"),
            InlineKeyboardButton(text="💎 Ентерпрайз", callback_data="tier_person")
        ],
        [
            InlineKeyboardButton(text="📝 Подати заявку", callback_data="new_application"),
            InlineKeyboardButton(text="❓ FAQ", callback_data="subscription_faq")
        ],
        [InlineKeyboardButton(text="◀️ Повернутись", callback_data="back_to_menu")]
    ])

def settings_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👻 Привидний", callback_data="ghost_mode"),
            InlineKeyboardButton(text="🔔 Сповіщення", callback_data="notifications")
        ],
        [
            InlineKeyboardButton(text="🌐 Мова", callback_data="language"),
            InlineKeyboardButton(text="🔐 Безпека", callback_data="security")
        ],
        [InlineKeyboardButton(text="◀️ Повернутись", callback_data="back_to_menu")]
    ])
