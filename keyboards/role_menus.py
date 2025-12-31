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
