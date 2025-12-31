"""
Unified UI System - Consolidated menus for all roles with consistent styling
Consolidates role_menus.py, user.py, and admin.py
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.roles import UserRole

# ═════════════════════════════════════════════════════════════════════════════
# UNIVERSAL COMPONENTS
# ═════════════════════════════════════════════════════════════════════════════

DIVIDER = "───────────────"

def back_button(callback_data: str = "back_to_menu") -> InlineKeyboardButton:
    """Universal back button"""
    return InlineKeyboardButton(text="◀️ Назад", callback_data=callback_data)

# ═════════════════════════════════════════════════════════════════════════════
# GUEST ROLE
# ═════════════════════════════════════════════════════════════════════════════

def guest_menu() -> InlineKeyboardMarkup:
    """Guest access menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Тарифи", callback_data="subscription_main")],
        [
            InlineKeyboardButton(text="🔑 Ключ", callback_data="enter_key"),
            InlineKeyboardButton(text="💬 Підтримка", callback_data="support"),
            InlineKeyboardButton(text="📖 Довідка", callback_data="help_main")
        ]
    ])

def guest_description() -> str:
    """Guest status description"""
    return f"""🌐 <b>SHADOW SYSTEM iO v2.0</b>
<i>Telegram-маркетинг платформа</i>
{DIVIDER}
<b>🔒 Статус:</b> Гостьовий доступ

<b>🚀 Можливості:</b>
├ 🤖 1000+ ботів
├ 🔍 OSINT-розвідка
├ 📊 Аналітика
├ 👥 CRM команди
└ 🛡️ Анти-бан
{DIVIDER}
<b>📋 Як почати:</b>
├ Оберіть тариф
├ Заповніть заявку
├ Отримайте ключ
└ Активуйте доступ
{DIVIDER}
<b>💎 Тарифи:</b>
├ 📦 БАЗОВИЙ
├ ⭐ СТАНДАРТ
├ 👑 ПРЕМІУМ
└ 💎 ЕНТЕРПРАЙЗ"""

# ═════════════════════════════════════════════════════════════════════════════
# MANAGER ROLE
# ═════════════════════════════════════════════════════════════════════════════

def manager_menu() -> InlineKeyboardMarkup:
    """Manager main menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 КАМПАНІЇ", callback_data="campaigns_main")],
        [
            InlineKeyboardButton(text="🤖 БОТИ", callback_data="botnet_main"),
            InlineKeyboardButton(text="📊 АНАЛІТИКА", callback_data="analytics_main"),
            InlineKeyboardButton(text="📝 ШАБЛОНИ", callback_data="templates_menu")
        ],
        [
            InlineKeyboardButton(text="✍️ ТЕКСТОВКИ", callback_data="texting_main"),
            InlineKeyboardButton(text="🎧 ПІДТРИМКА", callback_data="support_menu"),
            InlineKeyboardButton(text="👤 ПРОФІЛЬ", callback_data="profile_main")
        ],
        [InlineKeyboardButton(text="📖 ДОВІДКА", callback_data="help_main")]
    ])

def manager_description() -> str:
    """Manager status description"""
    return f"""🌟 <b>SHADOW SYSTEM iO v2.0</b>
<i>Центр менеджера</i>
{DIVIDER}
<b>📋 Статус:</b> 👤 Менеджер

<b>🚀 Кампанії:</b>
├ Запуск розсилок
├ Таргетинг
└ Моніторинг
{DIVIDER}
<b>🤖 Ботнет:</b>
├ Контроль ботів
└ Логи активності

<b>📊 Аналітика:</b>
├ CTR / конверсія
└ Ефективність

<b>✍️ Текстовки:</b>
├ Шаблони
└ AI-редактор
{DIVIDER}
<b>💡</b> Підвищення → Лідер"""

# ═════════════════════════════════════════════════════════════════════════════
# LEADER ROLE
# ═════════════════════════════════════════════════════════════════════════════

def leader_menu() -> InlineKeyboardMarkup:
    """Leader main menu with full feature access"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 БОТИ", callback_data="botnet_main")],
        [
            InlineKeyboardButton(text="🔍 OSINT", callback_data="osint_main"),
            InlineKeyboardButton(text="🚀 КАМПАНІЇ", callback_data="campaigns_main"),
            InlineKeyboardButton(text="🎯 ВОРОНКИ", callback_data="funnels_main")
        ],
        [
            InlineKeyboardButton(text="📡 РЕАЛТАЙМ", callback_data="realtime_monitor"),
            InlineKeyboardButton(text="🔬 АНАЛІЗ", callback_data="deep_parse"),
            InlineKeyboardButton(text="📊 АНАЛІТИКА", callback_data="analytics_main")
        ],
        [
            InlineKeyboardButton(text="📝 ШАБЛОНИ", callback_data="templates_menu"),
            InlineKeyboardButton(text="🔔 СПОВІЩ", callback_data="notifications_menu"),
            InlineKeyboardButton(text="👥 КОМАНДА", callback_data="team_main")
        ],
        [
            InlineKeyboardButton(text="🔥 ПРОГРІВ", callback_data="warming_main"),
            InlineKeyboardButton(text="⚙️ КОНФІГ", callback_data="settings_main"),
            InlineKeyboardButton(text="🎧 ПІДТРИМКА", callback_data="support_menu")
        ],
        [InlineKeyboardButton(text="🛠 ІНСТРУМЕНТИ", callback_data="advanced_tools")],
        [InlineKeyboardButton(text="🔬 КРИМІНАЛІСТИКА", callback_data="forensics_menu")],
        [
            InlineKeyboardButton(text="📖 ДОВІДКА", callback_data="help_main"),
            InlineKeyboardButton(text="👤 ПРОФІЛЬ", callback_data="profile_main")
        ]
    ])

def leader_description() -> str:
    """Leader status description"""
    return f"""👑 <b>SHADOW SYSTEM iO v2.0</b>
<i>Командний центр лідера</i>
{DIVIDER}
<b>💼 Статус:</b> 🔑 Leader

<b>🤖 Botnet:</b>
├ Імпорт сесій
├ Проксі-ротація
└ Прогрів
{DIVIDER}
<b>🔍 OSINT:</b>
├ Розвідка
├ Аналіз юзерів
└ Експорт баз

<b>🚀 Кампанії:</b>
├ A/B тести
├ Планування
└ Автоворонки

<b>👥 Команда:</b>
├ INV-коди
└ Контроль KPI
{DIVIDER}
<b>📈 Моніторинг:</b>
├ 🤖 Боти: <code>OK</code>
├ 👥 Команда: <code>ON</code>
└ 🛡️ Захист: <code>OK</code>"""

# ═════════════════════════════════════════════════════════════════════════════
# ADMIN ROLE
# ═════════════════════════════════════════════════════════════════════════════

def admin_menu() -> InlineKeyboardMarkup:
    """Admin full system control menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ СИСТЕМА", callback_data="admin_system")],
        [
            InlineKeyboardButton(text="🚫 БАНИ", callback_data="bans_menu"),
            InlineKeyboardButton(text="🔄 РОЛІ", callback_data="admin_roles"),
            InlineKeyboardButton(text="🎧 ТІКЕТИ", callback_data="support_menu")
        ],
        [
            InlineKeyboardButton(text="📝 ШАБЛОНИ", callback_data="templates_menu"),
            InlineKeyboardButton(text="🔑 ЛІЦЕНЗІЇ", callback_data="admin_keys"),
            InlineKeyboardButton(text="📋 ЗАЯВКИ", callback_data="admin_apps")
        ],
        [
            InlineKeyboardButton(text="📢 СПОВІЩЕННЯ", callback_data="notifications_menu"),
            InlineKeyboardButton(text="📊 СТАТИСТИКА", callback_data="project_stats")
        ],
        [
            InlineKeyboardButton(text="🔍 OSINT", callback_data="osint_main"),
            InlineKeyboardButton(text="🤖 БОТНЕТ", callback_data="botnet_main")
        ],
        [
            InlineKeyboardButton(text="🎨 РЕДАКТОР UI", callback_data="ui_editor"),
            InlineKeyboardButton(text="📱 МЕНЮ ЮЗЕРА", callback_data="user_menu")
        ],
        [InlineKeyboardButton(text="🔬 КРИМІНАЛІСТИКА", callback_data="forensics_menu")],
        [InlineKeyboardButton(text="🆘 EMERGENCY", callback_data="admin_emergency")]
    ])

def admin_description() -> str:
    """Admin status description"""
    return f"""🛡️ <b>SHADOW SYSTEM iO v2.0</b>
<i>Панель адміністратора</i>
{DIVIDER}
<b>💎 Статус:</b> 👑 Admin

<b>⚙️ Система:</b>
├ Моніторинг
├ Оновлення
└ Бекапи
{DIVIDER}
<b>👥 Користувачі:</b>
├ Зміна ролей
├ Бани
└ Блокування

<b>📢 Комунікації:</b>
├ Сповіщення
├ Тікети
├ Шаблони
└ Статистика

<b>🔑 Ліцензії:</b>
├ Генерація
└ Валідація
{DIVIDER}
<b>📊 Статистика:</b>
├ 🌐 Проекти: <code>OK</code>
├ 🤖 Боти: <code>OK</code>
└ 📢 Розсилки: <code>OK</code>"""

# ═════════════════════════════════════════════════════════════════════════════
# ADDITIONAL MENUS (Previously from keyboards/user.py and keyboards/admin.py)
# ═════════════════════════════════════════════════════════════════════════════

def main_menu() -> InlineKeyboardMarkup:
    """Universal main menu with all features"""
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

def license_menu() -> InlineKeyboardMarkup:
    """License status and activation menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статус ліцензії", callback_data="license_status")],
        [
            InlineKeyboardButton(text="🔑 Ввести ключ", callback_data="enter_key"),
            InlineKeyboardButton(text="📝 Заявка", callback_data="new_application")
        ],
        [back_button("back_to_menu")]
    ])

def subscription_menu() -> InlineKeyboardMarkup:
    """Subscription tier selection menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📦 Базовий", callback_data="tier_basic"),
            InlineKeyboardButton(text="⭐ Стандарт", callback_data="tier_standard")
        ],
        [
            InlineKeyboardButton(text="👑 Преміум", callback_data="tier_premium"),
            InlineKeyboardButton(text="💎 Ентерпрайз", callback_data="tier_enterprise")
        ],
        [
            InlineKeyboardButton(text="📝 Подати заявку", callback_data="new_application"),
            InlineKeyboardButton(text="❓ FAQ", callback_data="subscription_faq")
        ],
        [back_button("back_to_menu")]
    ])

def settings_menu() -> InlineKeyboardMarkup:
    """User settings menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👻 Привидний", callback_data="ghost_mode"),
            InlineKeyboardButton(text="🔔 Сповіщення", callback_data="notifications")
        ],
        [
            InlineKeyboardButton(text="🌐 Мова", callback_data="language"),
            InlineKeyboardButton(text="🔐 Безпека", callback_data="security")
        ],
        [back_button("back_to_menu")]
    ])

def main_menu_description() -> str:
    """Extended main menu description with project info"""
    return f"""<b>🌟 SHADOW SYSTEM iO v2.0</b>
<i>Комплексна платформа для управління ботами та маркетинг-кампаніями</i>

{DIVIDER}

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

{DIVIDER}

<b>💡 Порада:</b>
<i>Технічна підтримка доступна 24/7</i>"""

# ═════════════════════════════════════════════════════════════════════════════
# BROADCAST & CONFIRMATION MENUS (Previously from keyboards/admin.py)
# ═════════════════════════════════════════════════════════════════════════════

def broadcast_menu() -> InlineKeyboardMarkup:
    """Admin broadcast distribution menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Розсилка всім", callback_data="broadcast_all")],
        [
            InlineKeyboardButton(text="👑 Преміум", callback_data="broadcast_premium"),
            InlineKeyboardButton(text="👥 Лідери", callback_data="broadcast_leaders")
        ],
        [back_button("admin_menu")]
    ])

def confirm_keyboard() -> InlineKeyboardMarkup:
    """Confirmation dialog for admin actions"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Підтвердити", callback_data="admin_confirm"),
            InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_cancel")
        ]
    ])

def users_management_kb() -> InlineKeyboardMarkup:
    """User management menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔍 Пошук", callback_data="admin_user_search"),
            InlineKeyboardButton(text="📋 Список", callback_data="admin_user_list")
        ],
        [
            InlineKeyboardButton(text="🚫 Заблоковані", callback_data="admin_blocked_users"),
            InlineKeyboardButton(text="👑 Преміум", callback_data="admin_premium_users")
        ],
        [back_button("admin_menu")]
    ])

def keys_management_kb() -> InlineKeyboardMarkup:
    """License key management menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Створити ключ", callback_data="admin_key_create")],
        [
            InlineKeyboardButton(text="📋 Активні", callback_data="admin_keys_active"),
            InlineKeyboardButton(text="✅ Використані", callback_data="admin_keys_used")
        ],
        [back_button("admin_menu")]
    ])

def admin_app_kb(app_id):
    """Admin application handling menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Шаблон", callback_data=f"template_{app_id}")],
        [InlineKeyboardButton(text="❌ Відхилити", callback_data=f"reject_{app_id}")]
    ])

# ═════════════════════════════════════════════════════════════════════════════
# ADVANCED TOOLS (Previously from keyboards/advanced_kb.py)
# ═════════════════════════════════════════════════════════════════════════════

def get_ai_analysis_menu() -> InlineKeyboardMarkup:
    """AI analysis menu"""
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
    """Spam analyzer menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Текст", callback_data="spam_check_text"),
            InlineKeyboardButton(text="📊 Кампанія", callback_data="spam_check_campaign"),
            InlineKeyboardButton(text="📋 Поради", callback_data="spam_recommendations")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="mailing_main")]
    ])

def get_drip_campaign_menu() -> InlineKeyboardMarkup:
    """Drip campaign menu"""
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
    """Drip campaign actions"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Запустити", callback_data=f"drip_start:{campaign_id}")],
        [InlineKeyboardButton(text="⏸ Пауза", callback_data=f"drip_pause:{campaign_id}")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data=f"drip_stats:{campaign_id}")],
        [InlineKeyboardButton(text="✏️ Редагувати", callback_data=f"drip_edit:{campaign_id}")],
        [InlineKeyboardButton(text="🗑 Видалити", callback_data=f"drip_delete:{campaign_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="drip_list")]
    ])

def get_behavior_menu() -> InlineKeyboardMarkup:
    """Behavior analysis menu"""
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
    """Keyword analysis menu"""
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
    """Reports generation menu"""
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
    """Advanced tools main menu"""
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

# ═════════════════════════════════════════════════════════════════════════════
# NOTIFICATIONS & BANS (Previously from keyboards/notifications_kb.py)
# ═════════════════════════════════════════════════════════════════════════════

def notifications_menu_kb(is_admin: bool = False) -> InlineKeyboardMarkup:
    """Notifications main menu"""
    buttons = [
        [
            InlineKeyboardButton(text="📬 Мої", callback_data="notifications_my"),
            InlineKeyboardButton(text="🔔 Нові", callback_data="notifications_unread")
        ]
    ]
    if is_admin:
        buttons.append([
            InlineKeyboardButton(text="📢 Створити", callback_data="notification_create"),
            InlineKeyboardButton(text="📋 Історія", callback_data="notifications_history")
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def notification_create_type_kb() -> InlineKeyboardMarkup:
    """Notification type selection"""
    types = [
        ("ℹ️ Інформація", "info"),
        ("⚠️ Попередження", "warning"),
        ("📢 Оголошення", "announcement"),
        ("🔄 Оновлення", "update"),
        ("🔧 Техроботи", "maintenance")
    ]
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"notif_type:{ntype}")]
        for name, ntype in types
    ]
    buttons.append([InlineKeyboardButton(text="❌ Скасувати", callback_data="notifications_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def notification_target_kb(notif_type: str) -> InlineKeyboardMarkup:
    """Notification target selection"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Всі користувачі", callback_data=f"notif_target:{notif_type}:all")],
        [InlineKeyboardButton(text="👔 За роллю", callback_data=f"notif_target:{notif_type}:role")],
        [InlineKeyboardButton(text="👥👔 Декілька ролей", callback_data=f"notif_target:{notif_type}:multi_role")],
        [InlineKeyboardButton(text="👤 Персональні", callback_data=f"notif_target:{notif_type}:personal")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="notification_create")]
    ])

def notification_role_kb(notif_type: str) -> InlineKeyboardMarkup:
    """Notification role selection"""
    roles = [
        ("👤 Гості", "guest"),
        ("👔 Менеджери", "manager"),
        ("👑 Лідери", "leader"),
        ("🔑 Адміни", "admin")
    ]
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"notif_role:{notif_type}:{role}")]
        for name, role in roles
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"notif_target:{notif_type}:role")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def notification_multi_role_kb(notif_type: str, selected: list = None) -> InlineKeyboardMarkup:
    """Notification multi-role selection"""
    if selected is None:
        selected = []
    roles = [
        ("👤 Гості", "guest"),
        ("👔 Менеджери", "manager"),
        ("👑 Лідери", "leader"),
        ("🔑 Адміни", "admin")
    ]
    buttons = []
    for name, role in roles:
        check = "✅ " if role in selected else ""
        buttons.append([
            InlineKeyboardButton(
                text=f"{check}{name}",
                callback_data=f"notif_multi_toggle:{notif_type}:{role}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="✓ Готово", callback_data=f"notif_multi_done:{notif_type}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"notif_target:{notif_type}:multi_role")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def notification_priority_kb(notif_type: str, target: str) -> InlineKeyboardMarkup:
    """Notification priority selection"""
    priorities = [
        ("🟢 Низький", "low"),
        ("🟡 Звичайний", "normal"),
        ("🟠 Високий", "high"),
        ("🔴 Терміновий", "urgent")
    ]
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"notif_pri:{notif_type}:{target}:{pri}")]
        for name, pri in priorities
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"notif_target:{notif_type}:{target}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def notifications_list_kb(notifications: list) -> InlineKeyboardMarkup:
    """Notifications list"""
    buttons = []
    for n in notifications[:10]:
        icon = n.get('type_icon', 'ℹ️')
        read_mark = "" if n.get('is_read') else "🔵 "
        buttons.append([
            InlineKeyboardButton(
                text=f"{read_mark}{icon} {n['title'][:30]}...",
                callback_data=f"notif_view:{n['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="✓ Прочитати всі", callback_data="notifications_read_all")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="notifications_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def notification_view_kb(notif_id: int, is_admin: bool = False) -> InlineKeyboardMarkup:
    """Notification view"""
    buttons = []
    if is_admin:
        buttons.append([InlineKeyboardButton(text="🗑 Видалити", callback_data=f"notif_delete:{notif_id}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="notifications_my")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def bans_menu_kb() -> InlineKeyboardMarkup:
    """Bans main menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚫 Забанити", callback_data="ban_user")],
        [
            InlineKeyboardButton(text="📋 Активні", callback_data="bans_active"),
            InlineKeyboardButton(text="📜 Історія", callback_data="bans_history")
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")]
    ])

def ban_type_kb() -> InlineKeyboardMarkup:
    """Ban type selection"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏱ Тимчасовий", callback_data="ban_type:temporary")],
        [InlineKeyboardButton(text="🔒 Постійний", callback_data="ban_type:permanent")],
        [InlineKeyboardButton(text="⚠️ Попередження", callback_data="ban_type:warning")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="bans_menu")]
    ])

def ban_duration_kb(ban_type: str) -> InlineKeyboardMarkup:
    """Ban duration selection"""
    durations = [
        ("1 година", 1), ("6 годин", 6), ("12 годин", 12),
        ("1 день", 24), ("3 дні", 72), ("7 днів", 168),
        ("30 днів", 720)
    ]
    buttons = []
    row = []
    for name, hours in durations:
        row.append(InlineKeyboardButton(text=name, callback_data=f"ban_dur:{ban_type}:{hours}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="ban_user")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def bans_list_kb(bans: list) -> InlineKeyboardMarkup:
    """Bans list"""
    buttons = []
    for b in bans[:10]:
        buttons.append([
            InlineKeyboardButton(
                text=f"🚫 {b['user_id']} - {b['ban_type']}",
                callback_data=f"ban_view:{b['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="bans_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def ban_view_kb(ban_id: int, user_id: str) -> InlineKeyboardMarkup:
    """Ban view"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Розбанити", callback_data=f"unban:{user_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="bans_active")]
    ])

def project_stats_kb(project_id: int) -> InlineKeyboardMarkup:
    """Project statistics"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📅 7 днів", callback_data=f"stats_period:{project_id}:7"),
            InlineKeyboardButton(text="📅 30 днів", callback_data=f"stats_period:{project_id}:30")
        ],
        [InlineKeyboardButton(text="📊 Детальний звіт", callback_data=f"stats_detail:{project_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="projects_list")]
    ])

# ═════════════════════════════════════════════════════════════════════════════
# FORENSICS (Previously from keyboards/forensics_kb.py)
# ═════════════════════════════════════════════════════════════════════════════

def forensics_main_kb() -> InlineKeyboardMarkup:
    """Forensics main menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔬 Forensic Snapshot", callback_data="forensic_main")],
        [InlineKeyboardButton(text="🧠 AI Sentiment", callback_data="sentiment_main")],
        [InlineKeyboardButton(text="👻 Anti-Ghost Recovery", callback_data="ghost_main")],
        [InlineKeyboardButton(text="🔍 X-Ray Metadata", callback_data="xray_main")],
        [InlineKeyboardButton(text="💾 Memory Indexer", callback_data="indexer_main")],
        [InlineKeyboardButton(text="📡 Enhanced Monitoring", callback_data="monitoring_main")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="user_menu")]
    ])

def forensic_snapshot_kb() -> InlineKeyboardMarkup:
    """Forensic snapshot menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Захопити медіа", callback_data="forensic_capture")],
        [
            InlineKeyboardButton(text="📋 Всі знімки", callback_data="forensic_list"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="forensic_stats")
        ],
        [InlineKeyboardButton(text="🔄 Відновити видалене", callback_data="forensic_recover")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="forensics_menu")]
    ])

def ai_sentiment_kb() -> InlineKeyboardMarkup:
    """AI sentiment menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Аналізувати текст", callback_data="sentiment_analyze")],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="sentiment_stats"),
            InlineKeyboardButton(text="📈 Звіт", callback_data="sentiment_report")
        ],
        [InlineKeyboardButton(text="⚙️ Налаштування AI", callback_data="sentiment_settings")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="forensics_menu")]
    ])

def ghost_recovery_kb() -> InlineKeyboardMarkup:
    """Ghost recovery menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Видалені повідомлення", callback_data="ghost_deleted")],
        [
            InlineKeyboardButton(text="✏️ Історія редагувань", callback_data="ghost_edits"),
            InlineKeyboardButton(text="🔍 Пошук", callback_data="ghost_search")
        ],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="ghost_stats")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="forensics_menu")]
    ])

def xray_metadata_kb() -> InlineKeyboardMarkup:
    """X-Ray metadata menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔬 Аналізувати файл", callback_data="xray_analyze")],
        [
            InlineKeyboardButton(text="📋 Результати", callback_data="xray_results"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="xray_stats")
        ],
        [InlineKeyboardButton(text="⚠️ Аномалії", callback_data="xray_anomalies")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="forensics_menu")]
    ])

def memory_indexer_kb() -> InlineKeyboardMarkup:
    """Memory indexer menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Пошук", callback_data="indexer_search")],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="indexer_stats"),
            InlineKeyboardButton(text="🧹 Очистити", callback_data="indexer_cleanup")
        ],
        [InlineKeyboardButton(text="📁 По типах", callback_data="indexer_by_type")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="forensics_menu")]
    ])

def monitoring_main_kb() -> InlineKeyboardMarkup:
    """Monitoring main menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Додати ціль", callback_data="monitor_add")],
        [
            InlineKeyboardButton(text="📋 Мої цілі", callback_data="monitor_targets"),
            InlineKeyboardButton(text="⚠️ Сповіщення", callback_data="monitor_alerts")
        ],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="monitor_stats"),
            InlineKeyboardButton(text="📈 Події", callback_data="monitor_events")
        ],
        [InlineKeyboardButton(text="🔔 Тригери", callback_data="monitor_triggers")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="forensics_menu")]
    ])

def monitoring_target_kb(target_id: int, is_active: bool) -> InlineKeyboardMarkup:
    """Monitoring target menu"""
    toggle_text = "⏸ Зупинити" if is_active else "▶️ Запустити"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=toggle_text, callback_data=f"monitor_toggle:{target_id}"),
            InlineKeyboardButton(text="📊 Статистика", callback_data=f"monitor_target_stats:{target_id}")
        ],
        [
            InlineKeyboardButton(text="🔔 Тригери", callback_data=f"monitor_target_triggers:{target_id}"),
            InlineKeyboardButton(text="📋 Події", callback_data=f"monitor_target_events:{target_id}")
        ],
        [InlineKeyboardButton(text="🗑 Видалити", callback_data=f"monitor_delete:{target_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="monitor_targets")]
    ])

def monitoring_alerts_kb(alerts_count: int = 0) -> InlineKeyboardMarkup:
    """Monitoring alerts menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"⚠️ Непрочитані ({alerts_count})", callback_data="monitor_alerts_unread")],
        [InlineKeyboardButton(text="✅ Прочитані", callback_data="monitor_alerts_read")],
        [InlineKeyboardButton(text="🗑 Очистити все", callback_data="monitor_alerts_clear")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="monitoring_main")]
    ])

def alert_action_kb(alert_id: str) -> InlineKeyboardMarkup:
    """Alert action menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Прочитано", callback_data=f"alert_ack:{alert_id}"),
            InlineKeyboardButton(text="🔍 Деталі", callback_data=f"alert_details:{alert_id}")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="monitor_alerts")]
    ])

def trigger_types_kb(target_id: int) -> InlineKeyboardMarkup:
    """Trigger types menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔤 Ключове слово", callback_data=f"trigger_keyword:{target_id}")],
        [InlineKeyboardButton(text="📝 Регулярний вираз", callback_data=f"trigger_regex:{target_id}")],
        [InlineKeyboardButton(text="📋 Мої тригери", callback_data=f"trigger_list:{target_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"monitor_view:{target_id}")]
    ])

def back_to_forensics_kb() -> InlineKeyboardMarkup:
    """Back to forensics button"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="forensics_menu")]
    ])

def confirm_action_kb(action: str, item_id: str) -> InlineKeyboardMarkup:
    """Action confirmation menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Так", callback_data=f"confirm_{action}:{item_id}"),
            InlineKeyboardButton(text="❌ Ні", callback_data=f"cancel_{action}:{item_id}")
        ]
    ])

# ═════════════════════════════════════════════════════════════════════════════
# TEMPLATES & SCHEDULING (Previously from keyboards/templates_kb.py)
# ═════════════════════════════════════════════════════════════════════════════

def templates_menu_kb() -> InlineKeyboardMarkup:
    """Templates main menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Мої", callback_data="templates_list"),
            InlineKeyboardButton(text="➕ Створити", callback_data="template_create")
        ],
        [
            InlineKeyboardButton(text="📁 Категорії", callback_data="templates_categories"),
            InlineKeyboardButton(text="🌐 Публічні", callback_data="templates_public")
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="mailing_main")]
    ])

def templates_list_kb(templates: list) -> InlineKeyboardMarkup:
    """Templates list"""
    buttons = []
    for t in templates[:10]:
        icon = "📎" if t.get('has_media') else "📄"
        buttons.append([
            InlineKeyboardButton(
                text=f"{icon} {t['name']}",
                callback_data=f"template_view:{t['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="templates_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def template_categories_kb() -> InlineKeyboardMarkup:
    """Template categories"""
    categories = [
        ("👋 Привітальні", "welcome"),
        ("🎁 Промо", "promo"),
        ("📰 Новини", "news"),
        ("⏰ Нагадування", "reminder"),
        ("🔔 Сповіщення", "alert"),
        ("📋 Загальні", "general")
    ]
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"templates_cat:{cat}")]
        for name, cat in categories
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="templates_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def template_view_kb(template_id: int, is_owner: bool = True) -> InlineKeyboardMarkup:
    """Template view"""
    buttons = []
    if is_owner:
        buttons.append([
            InlineKeyboardButton(text="✏️ Редагувати", callback_data=f"template_edit:{template_id}"),
            InlineKeyboardButton(text="🗑 Видалити", callback_data=f"template_delete:{template_id}")
        ])
    buttons.append([InlineKeyboardButton(text="🚀 Використати", callback_data=f"template_use:{template_id}")])
    buttons.append([InlineKeyboardButton(text="⏱ Запланувати", callback_data=f"template_schedule:{template_id}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="templates_list")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def template_create_category_kb() -> InlineKeyboardMarkup:
    """Template category selection for creation"""
    categories = [
        ("👋 Привітальні", "welcome"),
        ("🎁 Промо", "promo"),
        ("📰 Новини", "news"),
        ("⏰ Нагадування", "reminder"),
        ("🔔 Сповіщення", "alert"),
        ("📋 Загальні", "general")
    ]
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"template_new_cat:{cat}")]
        for name, cat in categories
    ]
    buttons.append([InlineKeyboardButton(text="❌ Скасувати", callback_data="templates_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def schedule_type_kb(template_id: int) -> InlineKeyboardMarkup:
    """Schedule type selection"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔂 Одноразово", callback_data=f"sched_once:{template_id}")],
        [InlineKeyboardButton(text="⏱ За інтервалом", callback_data=f"sched_interval:{template_id}")],
        [InlineKeyboardButton(text="📅 Щодня", callback_data=f"sched_daily:{template_id}")],
        [InlineKeyboardButton(text="📆 Щотижня", callback_data=f"sched_weekly:{template_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"template_view:{template_id}")]
    ])

def schedule_interval_kb(template_id: int) -> InlineKeyboardMarkup:
    """Schedule interval selection"""
    intervals = [
        ("15 хв", 15), ("30 хв", 30), ("1 год", 60),
        ("2 год", 120), ("4 год", 240), ("6 год", 360),
        ("12 год", 720), ("24 год", 1440)
    ]
    buttons = []
    row = []
    for name, minutes in intervals:
        row.append(InlineKeyboardButton(text=name, callback_data=f"sched_int_set:{template_id}:{minutes}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"template_schedule:{template_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def schedule_target_kb(template_id: int) -> InlineKeyboardMarkup:
    """Schedule target audience selection"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Всі користувачі", callback_data=f"sched_target:{template_id}:all")],
        [InlineKeyboardButton(text="👔 Менеджери", callback_data=f"sched_target:{template_id}:manager")],
        [InlineKeyboardButton(text="👑 Лідери", callback_data=f"sched_target:{template_id}:leader")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"template_schedule:{template_id}")]
    ])

def scheduled_list_kb(mailings: list) -> InlineKeyboardMarkup:
    """Scheduled mailings list"""
    buttons = []
    status_icons = {'active': '▶️', 'paused': '⏸', 'completed': '✅'}
    for m in mailings[:10]:
        icon = status_icons.get(m['status'], '📨')
        buttons.append([
            InlineKeyboardButton(
                text=f"{icon} {m['name']}",
                callback_data=f"sched_view:{m['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="mailing_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def scheduled_view_kb(mailing_id: int, status: str) -> InlineKeyboardMarkup:
    """Scheduled mailing view"""
    buttons = []
    if status == 'active':
        buttons.append([InlineKeyboardButton(text="⏸ Пауза", callback_data=f"sched_pause:{mailing_id}")])
    elif status == 'paused':
        buttons.append([InlineKeyboardButton(text="▶️ Відновити", callback_data=f"sched_resume:{mailing_id}")])
    buttons.append([InlineKeyboardButton(text="🗑 Видалити", callback_data=f"sched_delete:{mailing_id}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="scheduled_list")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ═════════════════════════════════════════════════════════════════════════════
# SUPPORT (Previously from keyboards/support_kb.py)
# ═════════════════════════════════════════════════════════════════════════════

def support_menu_kb(is_admin: bool = False) -> InlineKeyboardMarkup:
    """Support main menu"""
    buttons = [
        [
            InlineKeyboardButton(text="📩 Створити", callback_data="ticket_create"),
            InlineKeyboardButton(text="📋 Мої", callback_data="tickets_my")
        ]
    ]
    if is_admin:
        buttons.append([
            InlineKeyboardButton(text="📥 Всі", callback_data="tickets_all"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="tickets_stats")
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def ticket_category_kb() -> InlineKeyboardMarkup:
    """Ticket category selection"""
    categories = [
        ("🔧 Технічна підтримка", "technical"),
        ("💳 Питання оплати", "billing"),
        ("👤 Акаунт та доступ", "account"),
        ("💡 Запит функції", "feature"),
        ("🐛 Повідомити про баг", "bug"),
        ("❓ Загальне питання", "general")
    ]
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"ticket_cat:{cat}")]
        for name, cat in categories
    ]
    buttons.append([InlineKeyboardButton(text="❌ Скасувати", callback_data="support_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def ticket_priority_kb(category: str) -> InlineKeyboardMarkup:
    """Ticket priority selection"""
    priorities = [
        ("🟢 Низький", "low"),
        ("🟡 Звичайний", "normal"),
        ("🟠 Високий", "high"),
        ("🔴 Терміновий", "urgent")
    ]
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"ticket_pri:{category}:{pri}")]
        for name, pri in priorities
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="ticket_create")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def tickets_list_kb(tickets: list, is_admin: bool = False) -> InlineKeyboardMarkup:
    """Tickets list"""
    buttons = []
    for t in tickets[:10]:
        icon = t.get('status_icon', '📂')
        buttons.append([
            InlineKeyboardButton(
                text=f"{icon} {t['ticket_code']}: {t['subject'][:20]}...",
                callback_data=f"ticket_view:{t['id']}"
            )
        ])
    if is_admin:
        buttons.append([
            InlineKeyboardButton(text="📂 Відкриті", callback_data="tickets_filter:open"),
            InlineKeyboardButton(text="🔄 В роботі", callback_data="tickets_filter:in_progress")
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="support_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def ticket_view_kb(ticket_id: int, status: str, is_admin: bool = False) -> InlineKeyboardMarkup:
    """Ticket view"""
    buttons = []
    if status not in ['resolved', 'closed']:
        buttons.append([InlineKeyboardButton(text="💬 Відповісти", callback_data=f"ticket_reply:{ticket_id}")])
    if is_admin:
        if status == 'open':
            buttons.append([InlineKeyboardButton(text="📌 Взяти в роботу", callback_data=f"ticket_assign:{ticket_id}")])
        buttons.append([InlineKeyboardButton(text="🔄 Змінити статус", callback_data=f"ticket_status:{ticket_id}")])
    if status == 'resolved':
        buttons.append([InlineKeyboardButton(text="⭐ Оцінити", callback_data=f"ticket_rate:{ticket_id}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="tickets_my")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def ticket_status_kb(ticket_id: int) -> InlineKeyboardMarkup:
    """Ticket status change menu"""
    statuses = [
        ("📂 Відкритий", "open"),
        ("🔄 В роботі", "in_progress"),
        ("⏳ Очікує відповіді", "waiting"),
        ("✅ Вирішено", "resolved"),
        ("📁 Закритий", "closed")
    ]
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"ticket_set_status:{ticket_id}:{status}")]
        for name, status in statuses
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"ticket_view:{ticket_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def ticket_rating_kb(ticket_id: int) -> InlineKeyboardMarkup:
    """Ticket rating menu"""
    buttons = [[
        InlineKeyboardButton(text="⭐", callback_data=f"ticket_rating:{ticket_id}:1"),
        InlineKeyboardButton(text="⭐⭐", callback_data=f"ticket_rating:{ticket_id}:2"),
        InlineKeyboardButton(text="⭐⭐⭐", callback_data=f"ticket_rating:{ticket_id}:3"),
        InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data=f"ticket_rating:{ticket_id}:4"),
        InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data=f"ticket_rating:{ticket_id}:5")
    ]]
    buttons.append([InlineKeyboardButton(text="🔙 Пропустити", callback_data=f"ticket_view:{ticket_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ═════════════════════════════════════════════════════════════════════════════
# MISC KEYBOARDS (Previously from keyboards/application_kb.py, guest_kb.py, user_kb.py)
# ═════════════════════════════════════════════════════════════════════════════

def duration_kb():
    """Application duration selection"""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="2 дні"), KeyboardButton(text="14 днів")],
        [KeyboardButton(text="30 днів")]
    ], resize_keyboard=True)

def guest_main_kb():
    """Guest main menu (reply keyboard)"""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📦 Тарифи")],
        [KeyboardButton(text="🔐 Авторизація")]
    ], resize_keyboard=True)

def tariffs_kb():
    """Tariffs selection"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔹 Basic", callback_data="tariff_basic")],
        [InlineKeyboardButton(text="🔶 Standard", callback_data="tariff_standard")]
    ])

def user_main_kb():
    """User main menu (reply keyboard)"""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🤖 Botnet"), KeyboardButton(text="🚀 Розсилки")],
        [KeyboardButton(text="👥 Команда"), KeyboardButton(text="📊 Аналітика")]
    ], resize_keyboard=True)

# ═════════════════════════════════════════════════════════════════════════════
# ROLE-BASED DISPATCHERS (Main entry points)
# ═════════════════════════════════════════════════════════════════════════════

def get_menu_by_role(role: str) -> InlineKeyboardMarkup:
    """Get appropriate menu based on user role"""
    if role == UserRole.ADMIN:
        return admin_menu()
    elif role == UserRole.LEADER:
        return leader_menu()
    elif role == UserRole.MANAGER:
        return manager_menu()
    else:
        return guest_menu()

def get_description_by_role(role: str) -> str:
    """Get appropriate description based on user role"""
    if role == UserRole.ADMIN:
        return admin_description()
    elif role == UserRole.LEADER:
        return leader_description()
    elif role == UserRole.MANAGER:
        return manager_description()
    else:
        return guest_description()
