from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.roles import UserRole

def guest_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Тарифи", callback_data="subscription_main")],
        [
            InlineKeyboardButton(text="🔑 Ключ", callback_data="enter_key"),
            InlineKeyboardButton(text="💬 Підтримка", callback_data="support"),
            InlineKeyboardButton(text="📖 Довідка", callback_data="help_main")
        ]
    ])

def guest_description() -> str:
    return """🌐 <b>SHADOW SYSTEM iO v2.0</b>
<i>Telegram-маркетинг платформа</i>
───────────────
<b>🔒 Статус:</b> Гостьовий доступ

<b>🚀 Можливості:</b>
├ 🤖 1000+ ботів
├ 🔍 OSINT-розвідка
├ 📊 Аналітика
├ 👥 CRM команди
└ 🛡️ Анти-бан
───────────────
<b>📋 Як почати:</b>
├ Оберіть тариф
├ Заповніть заявку
├ Отримайте ключ
└ Активуйте доступ
───────────────
<b>💎 Тарифи:</b>
├ 📦 БАЗОВИЙ
├ ⭐ СТАНДАРТ
├ 👑 ПРЕМІУМ
└ 💎 ЕНТЕРПРАЙЗ"""

def manager_menu() -> InlineKeyboardMarkup:
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
    return """🌟 <b>SHADOW SYSTEM iO v2.0</b>
<i>Центр менеджера</i>
───────────────
<b>📋 Статус:</b> 👤 Менеджер

<b>🚀 Кампанії:</b>
├ Запуск розсилок
├ Таргетинг
└ Моніторинг
───────────────
<b>🤖 Ботнет:</b>
├ Контроль ботів
└ Логи активності

<b>📊 Аналітика:</b>
├ CTR / конверсія
└ Ефективність

<b>✍️ Текстовки:</b>
├ Шаблони
└ AI-редактор
───────────────
<b>💡</b> Підвищення → Лідер"""

def leader_menu() -> InlineKeyboardMarkup:
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
        [
            InlineKeyboardButton(text="📖 ДОВІДКА", callback_data="help_main"),
            InlineKeyboardButton(text="👤 ПРОФІЛЬ", callback_data="profile_main")
        ]
    ])

def leader_description() -> str:
    return """👑 <b>SHADOW SYSTEM iO v2.0</b>
<i>Командний центр лідера</i>
───────────────
<b>💼 Статус:</b> 🔑 Leader

<b>🤖 Botnet:</b>
├ Імпорт сесій
├ Проксі-ротація
└ Прогрів
───────────────
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
───────────────
<b>📈 Моніторинг:</b>
├ 🤖 Боти: <code>OK</code>
├ 👥 Команда: <code>ON</code>
└ 🛡️ Захист: <code>OK</code>"""

def admin_menu() -> InlineKeyboardMarkup:
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
        [InlineKeyboardButton(text="🆘 EMERGENCY", callback_data="admin_emergency")]
    ])

def admin_description() -> str:
    return """🛡️ <b>SHADOW SYSTEM iO v2.0</b>
<i>Панель адміністратора</i>
───────────────
<b>💎 Статус:</b> 👑 Admin

<b>⚙️ Система:</b>
├ Моніторинг
├ Оновлення
└ Бекапи
───────────────
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
───────────────
<b>📊 Статистика:</b>
├ 🌐 Проекти: <code>OK</code>
├ 🤖 Боти: <code>OK</code>
└ 📢 Розсилки: <code>OK</code>"""

def get_menu_by_role(role: str) -> InlineKeyboardMarkup:
    if role == UserRole.ADMIN:
        return admin_menu()
    elif role == UserRole.LEADER:
        return leader_menu()
    elif role == UserRole.MANAGER:
        return manager_menu()
    else:
        return guest_menu()

def get_description_by_role(role: str) -> str:
    if role == UserRole.ADMIN:
        return admin_description()
    elif role == UserRole.LEADER:
        return leader_description()
    elif role == UserRole.MANAGER:
        return manager_description()
    else:
        return guest_description()
