from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.roles import UserRole

def guest_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Тарифи та плани", callback_data="subscription_main")],
        [
            InlineKeyboardButton(text="🔑 Активувати ключ", callback_data="enter_key"),
            InlineKeyboardButton(text="💬 Підтримка", callback_data="support")
        ],
        [InlineKeyboardButton(text="📖 Довідковий центр", callback_data="help_main")]
    ])

def guest_description() -> str:
    return """══════════════════════════
🌐 <b>SHADOW SYSTEM iO v2.0</b>
══════════════════════════
<i>Telegram-маркетинг платформа</i>

<b>🔒 СТАТУС:</b> Гостьовий доступ

<b>🚀 ЩО ВИ ОТРИМАЄТЕ:</b>
├ 🤖 Управління 1000+ ботами
├ 🔍 OSINT-аналітика та розвідка
├ 📊 Статистика кампаній
├ 👥 CRM для команди
└ 🛡️ Захист від блокувань

<b>📋 ЯК ПОЧАТИ:</b>
├ 1. Оберіть тариф
├ 2. Заповніть заявку
├ 3. Отримайте SHADOW-ключ
└ 4. Активуйте доступ

<b>💎 ТАРИФИ:</b>
├ 📦 <b>БАЗОВИЙ</b> — старт
├ ⭐ <b>СТАНДАРТ</b> — агенції
├ 👑 <b>ПРЕМІУМ</b> — максимум
└ 💎 <b>ЕНТЕРПРАЙЗ</b> — корпоративи"""

def manager_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 КАМПАНІЇ", callback_data="campaigns_main")],
        [
            InlineKeyboardButton(text="🤖 БОТИ", callback_data="botnet_main"),
            InlineKeyboardButton(text="📊 АНАЛІТИКА", callback_data="analytics_main")
        ],
        [
            InlineKeyboardButton(text="📝 ШАБЛОНИ", callback_data="templates_menu"),
            InlineKeyboardButton(text="✍️ ТЕКСТОВКИ", callback_data="texting_main")
        ],
        [
            InlineKeyboardButton(text="🎧 ПІДТРИМКА", callback_data="support_menu"),
            InlineKeyboardButton(text="👤 ПРОФІЛЬ", callback_data="profile_main")
        ],
        [InlineKeyboardButton(text="📖 ДОВІДКА", callback_data="help_main")]
    ])

def manager_description() -> str:
    return """══════════════════════════
🌟 <b>SHADOW SYSTEM iO v2.0</b>
══════════════════════════
<i>Центр управління менеджера</i>

<b>📋 СТАТУС:</b> 👤 Менеджер

<b>🚀 КАМПАНІЇ:</b>
├ Запуск розсилок
├ Таргетинг аудиторії
└ Моніторинг статусу

<b>🤖 БОТНЕТ:</b>
├ Контроль ботів
└ Логи активності

<b>📊 АНАЛІТИКА:</b>
├ CTR та конверсія
└ Ефективність кампаній

<b>✍️ ТЕКСТОВКИ:</b>
├ Бібліотека шаблонів
└ AI-редагування
──────────────────────────
<b>💡</b> Розширення прав — до Лідера"""

def leader_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 УПРАВЛІННЯ БОТАМИ", callback_data="botnet_main")],
        [
            InlineKeyboardButton(text="🔍 OSINT", callback_data="osint_main"),
            InlineKeyboardButton(text="🚀 КАМПАНІЇ", callback_data="campaigns_main")
        ],
        [
            InlineKeyboardButton(text="🎯 ВОРОНКИ", callback_data="funnels_main"),
            InlineKeyboardButton(text="📊 АНАЛІТИКА", callback_data="analytics_main")
        ],
        [
            InlineKeyboardButton(text="📡 РЕАЛТАЙМ", callback_data="realtime_monitor"),
            InlineKeyboardButton(text="🔬 ГЛИБОКИЙ АНАЛІЗ", callback_data="deep_parse")
        ],
        [
            InlineKeyboardButton(text="📝 ШАБЛОНИ", callback_data="templates_menu"),
            InlineKeyboardButton(text="🔔 СПОВІЩЕННЯ", callback_data="notifications_menu")
        ],
        [
            InlineKeyboardButton(text="👥 КОМАНДА", callback_data="team_main"),
            InlineKeyboardButton(text="🎧 ПІДТРИМКА", callback_data="support_menu")
        ],
        [
            InlineKeyboardButton(text="🔥 ПРОГРІВ", callback_data="warming_main"),
            InlineKeyboardButton(text="⚙️ КОНФІГУРАЦІЯ", callback_data="settings_main")
        ],
        [InlineKeyboardButton(text="🛠 РОЗШИРЕНІ ІНСТРУМЕНТИ", callback_data="advanced_tools")],
        [
            InlineKeyboardButton(text="📖 ДОВІДКА", callback_data="help_main"),
            InlineKeyboardButton(text="👤 ПРОФІЛЬ", callback_data="profile_main")
        ]
    ])

def leader_description() -> str:
    return """══════════════════════════
👑 <b>SHADOW SYSTEM iO v2.0</b>
══════════════════════════
<i>Командний центр лідера</i>

<b>💼 СТАТУС:</b> 🔑 Leader

<b>🤖 BOTNET & PROXY:</b>
├ Імпорт ботів/сесій
├ Проксі та ротація IP
└ Цикли прогріву

<b>🔍 OSINT & ПАРСИНГ:</b>
├ Розвідка аудиторії
├ Аналіз користувачів
└ Експорт баз даних

<b>🚀 КАМПАНІЇ & ВОРОНКИ:</b>
├ A/B тестування
├ Планування розсилок
└ Автоматизація воронок

<b>📝 ШАБЛОНИ:</b>
├ Бібліотека шаблонів
├ Планування розкладу
└ Тікет-система

<b>👥 КОМАНДА:</b>
├ INV-коди менеджерів
└ Контроль KPI
──────────────────────────
<b>📈 МОНІТОРИНГ:</b>
├ 🤖 Боти: <code>активно</code>
├ 👥 Команда: <code>онлайн</code>
└ 🛡️ Анти-бан: <b>ОК</b>"""

def admin_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ УПРАВЛІННЯ СИСТЕМОЮ", callback_data="admin_system")],
        [
            InlineKeyboardButton(text="🚫 БАНИ", callback_data="bans_menu"),
            InlineKeyboardButton(text="🔄 РОЛІ", callback_data="admin_roles")
        ],
        [
            InlineKeyboardButton(text="📢 СПОВІЩЕННЯ", callback_data="notifications_menu"),
            InlineKeyboardButton(text="🎧 ТІКЕТИ", callback_data="support_menu")
        ],
        [
            InlineKeyboardButton(text="📝 ШАБЛОНИ", callback_data="templates_menu"),
            InlineKeyboardButton(text="🔑 ЛІЦЕНЗІЇ", callback_data="admin_keys")
        ],
        [
            InlineKeyboardButton(text="📋 ЗАЯВКИ", callback_data="admin_apps"),
            InlineKeyboardButton(text="📊 СТАТИСТИКА", callback_data="project_stats")
        ],
        [
            InlineKeyboardButton(text="🔍 OSINT", callback_data="osint_main"),
            InlineKeyboardButton(text="🤖 БОТНЕТ", callback_data="botnet_main")
        ],
        [InlineKeyboardButton(text="🎨 РЕДАКТОР UI", callback_data="ui_editor")],
        [InlineKeyboardButton(text="📱 ПЕРЕГЛЯД МЕНЮ ЮЗЕРА", callback_data="user_menu")],
        [InlineKeyboardButton(text="🆘 EMERGENCY ALERT", callback_data="admin_emergency")]
    ])

def admin_description() -> str:
    return """══════════════════════════
🛡️ <b>SHADOW SYSTEM iO v2.0</b>
══════════════════════════
<i>Центральний пульт адміністратора</i>

<b>💎 СТАТУС:</b> 👑 SuperAdmin / Owner
<b>🔧 ГЛОБАЛЬНЕ АДМІНІСТРУВАННЯ:</b>

<b>⚙️ СИСТЕМА & ЯДРО:</b>
├ Моніторинг серверів
├ Оновлення та патчі
└ Резервне копіювання

<b>👥 КЕРУВАННЯ КОРИСТУВАЧАМИ:</b>
├ Зміна ролей (Guest/Manager/Leader)
├ Бани (тимчасові/постійні)
└ Блокування порушників

<b>📢 КОМУНІКАЦІЙНИЙ ЦЕНТР:</b>
├ Сповіщення за ролями
├ Тікети підтримки
├ Шаблони розсилок
└ Статистика проектів

<b>🔑 ЛІЦЕНЗІЙНИЙ ЦЕНТР:</b>
├ Генерація SHADOW-ключів
└ Валідація підписок
──────────────────────────
<b>📊 ГЛОБАЛЬНА СТАТИСТИКА:</b>
├ 🌐 Проектів: <code>аналіз...</code>
├ 🤖 Ботів: <code>синхронізація...</code>
└ 📢 Розсилок: <code>готово</code>"""

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
