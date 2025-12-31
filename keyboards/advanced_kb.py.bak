"""
Advanced Keyboards - Клавіатури для розширених модулів
AI аналіз, спам-аналізатор, каскадні кампанії, профілювання
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_ai_analysis_menu() -> InlineKeyboardMarkup:
    """Меню AI аналізу"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔍 Текст", callback_data="ai_analyze_text"),
            InlineKeyboardButton(text="📍 Координати", callback_data="ai_find_coords"),
            InlineKeyboardButton(text="⚠️ Загрози", callback_data="ai_detect_threats")
        ],
        [
            InlineKeyboardButton(text="📱 Телефони", callback_data="ai_find_phones"),
            InlineKeyboardButton(text="💰 Крипто", callback_data="ai_find_crypto")
        ],
        [InlineKeyboardButton(text="🤖 Повний AI аналіз", callback_data="ai_full_analysis")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="osint_main")]
    ])


def get_spam_analyzer_menu() -> InlineKeyboardMarkup:
    """Меню аналізатора спаму"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Текст", callback_data="spam_check_text"),
            InlineKeyboardButton(text="📊 Кампанія", callback_data="spam_check_campaign"),
            InlineKeyboardButton(text="📋 Поради", callback_data="spam_recommendations")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="mailing_main")]
    ])


def get_drip_campaign_menu() -> InlineKeyboardMarkup:
    """Меню каскадних кампаній"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Створити кампанію", callback_data="drip_create")],
        [
            InlineKeyboardButton(text="📋 Мої", callback_data="drip_list"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="drip_stats"),
            InlineKeyboardButton(text="⚙️ Шаблони", callback_data="drip_templates")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="mailing_main")]
    ])


def get_drip_campaign_actions(campaign_id: str) -> InlineKeyboardMarkup:
    """Дії з кампанією"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Запустити", callback_data=f"drip_start:{campaign_id}")],
        [InlineKeyboardButton(text="⏸ Пауза", callback_data=f"drip_pause:{campaign_id}")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data=f"drip_stats:{campaign_id}")],
        [InlineKeyboardButton(text="✏️ Редагувати", callback_data=f"drip_edit:{campaign_id}")],
        [InlineKeyboardButton(text="🗑 Видалити", callback_data=f"drip_delete:{campaign_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="drip_list")]
    ])


def get_behavior_menu() -> InlineKeyboardMarkup:
    """Меню аналізу поведінки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👤 Юзер", callback_data="behavior_analyze_user"),
            InlineKeyboardButton(text="📊 Патерни", callback_data="behavior_patterns")
        ],
        [
            InlineKeyboardButton(text="⚠️ Аномалії", callback_data="behavior_anomalies"),
            InlineKeyboardButton(text="🔮 Прогноз", callback_data="behavior_predict")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="osint_main")]
    ])


def get_keyword_menu() -> InlineKeyboardMarkup:
    """Меню аналізу ключових слів"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Текст", callback_data="keywords_analyze_text"),
            InlineKeyboardButton(text="📊 ТОП", callback_data="keywords_top")
        ],
        [
            InlineKeyboardButton(text="😊 Сентимент", callback_data="keywords_sentiment"),
            InlineKeyboardButton(text="📈 Тренди", callback_data="keywords_trends")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="osint_main")]
    ])


def get_reports_menu() -> InlineKeyboardMarkup:
    """Меню генерації звітів"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📄 OSINT", callback_data="report_osint"),
            InlineKeyboardButton(text="📊 Кампанія", callback_data="report_campaign")
        ],
        [
            InlineKeyboardButton(text="👤 Юзер", callback_data="report_user"),
            InlineKeyboardButton(text="📈 Аналітика", callback_data="report_analytics")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])


def get_advanced_tools_menu() -> InlineKeyboardMarkup:
    """Меню розширених інструментів"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🤖 AI Аналіз", callback_data="tools_ai"),
            InlineKeyboardButton(text="📊 Спам-чек", callback_data="tools_spam")
        ],
        [
            InlineKeyboardButton(text="📧 Drip кампанії", callback_data="tools_drip"),
            InlineKeyboardButton(text="👤 Профілювання", callback_data="tools_behavior")
        ],
        [
            InlineKeyboardButton(text="🔑 Ключові слова", callback_data="tools_keywords"),
            InlineKeyboardButton(text="📄 Звіти", callback_data="tools_reports")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])
