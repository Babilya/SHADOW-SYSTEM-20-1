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
    return """<b>🌐 SHADOW SYSTEM iO v2.0</b>
<i>Професійна екосистема для Telegram-маркетингу</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>🔒 Статус:</b> Гостьовий доступ

<b>🚀 Що ви отримаєте:</b>
├ 🤖 Автоматизація до 1000+ ботів
├ 🔍 OSINT-інструменти глибокої аналітики
├ 📊 Повна статистика кампаній
├ 👥 CRM для команди менеджерів
└ 🛡️ Захист від блокувань

<b>📋 Як почати роботу:</b>
<code>1.</code> Оберіть відповідний тариф
<code>2.</code> Заповніть коротку заявку
<code>3.</code> Отримайте унікальний SHADOW-ключ
<code>4.</code> Активуйте доступ до системи

<b>💎 Тарифні плани:</b>
├ 📦 <b>БАЗОВИЙ</b> — ідеальний старт
├ ⭐ <b>СТАНДАРТ</b> — для агенцій
├ 👑 <b>ПРЕМІУМ</b> — максимум можливостей
└ 💎 <b>ЕНТЕРПРАЙЗ</b> — індивідуальні рішення"""

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
    return """<b>🌟 SHADOW SYSTEM iO v2.0</b>
<i>Центр оперативного управління менеджера</i>

═══════════════════════

<b>📋 СТАТУС:</b> 👤 Менеджер проекту
<b>🎯 ВАШІ ЗАВДАННЯ ТА ІНСТРУМЕНТИ:</b>

<b>🚀 КАМПАНІЇ:</b>
├ Створення та запуск масових розсилок
├ Налаштування таргетингу аудиторії
└ Моніторинг статусу виконання в реальному часі

<b>🤖 БОТНЕТ:</b>
├ Контроль стану підключених ботів
└ Перегляд логів активності та помилок

<b>📊 АНАЛІТИКА:</b>
├ Відстеження CTR та конверсії
└ Аналіз ефективності ваших розсилок

<b>✍️ ТЕКСТОВКИ:</b>
├ Бібліотека перевірених шаблонів
└ AI-редагування для обходу спам-фільтрів

═══════════════════════

<b>💡 ПІДКАЗКА:</b>
<i>Для отримання нових завдань або розширення прав зверніться до вашого Лідера.</i>"""

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
    return """<b>👑 SHADOW SYSTEM iO v2.0</b>
<i>Командний центр лідера проекту</i>

═══════════════════════

<b>💼 СТАТУС:</b> 🔑 Власник проекту (Leader)
<b>🎛️ ПОВНИЙ КОНТРОЛЬ ЕКОСИСТЕМИ:</b>

<b>🤖 BOTNET & PROXY:</b>
├ Масовий імпорт ботів та налаштування проксі
└ Автоматичні цикли прогріву та ротація IP

<b>🔍 OSINT & ПАРСИНГ:</b>
├ Глибока розвідка аудиторії та геосканування
└ Експорт баз даних для точкових кампаній

<b>🚀 КАМПАНІЇ & ВОРОНКИ:</b>
├ A/B тестування та автоматизація воронок
└ Глобальне планування розсилок

<b>📝 ШАБЛОНИ & КОМУНІКАЦІЯ:</b>
├ Бібліотека готових шаблонів розсилок
├ Планування за розкладом (інтервали)
├ Сповіщення по ролям та проектам
└ Центр підтримки з тікет-системою

<b>👥 УПРАВЛІННЯ КОМАНДОЮ:</b>
├ Найм менеджерів через INV-коди
└ Розподіл прав доступу та контроль KPI

═══════════════════════

<b>📈 МОНІТОРИНГ ПРОЕКТУ:</b>
├ 🤖 Ботів у мережі: <code>активно</code>
├ 👥 Менеджерів у штаті: <code>на зв'язку</code>
├ 📊 Кампаній проведено: <code>в процесі</code>
└ 🛡️ Система анти-бан: <b>ОПТИМІЗОВАНО</b>"""

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
        [InlineKeyboardButton(text="📱 ПЕРЕГЛЯД МЕНЮ ЮЗЕРА", callback_data="user_menu")],
        [InlineKeyboardButton(text="🆘 EMERGENCY ALERT", callback_data="admin_emergency")]
    ])

def admin_description() -> str:
    return """<b>🛡️ SHADOW SYSTEM iO v2.0</b>
<i>Центральний пульт адміністратора</i>

═══════════════════════

<b>💎 СТАТУС:</b> 👑 SuperAdmin / Owner
<b>🔧 ГЛОБАЛЬНЕ АДМІНІСТРУВАННЯ:</b>

<b>⚙️ СИСТЕМА & ЯДРО:</b>
├ Моніторинг навантаження та статусу серверів
└ Управління критичними оновленнями системи

<b>👥 КЕРУВАННЯ КОРИСТУВАЧАМИ:</b>
├ Ручна зміна ролей (Guest/Manager/Leader)
├ Система банів (тимчасові/постійні)
└ Глобальне блокування порушників

<b>📢 КОМУНІКАЦІЙНИЙ ЦЕНТР:</b>
├ Масові сповіщення по ролях
├ Система підтримки (тікети)
├ Шаблони для розсилок
└ Статистика по проектам

<b>🔑 ЛІЦЕНЗІЙНИЙ ЦЕНТР:</b>
├ Генерація унікальних SHADOW-ключів
└ Валідація та продовження підписок

<b>🛡️ ЦЕНТР БЕЗПЕКИ:</b>
├ Журнал аудиту (Audit Log)
└ Система екстреного реагування (Panic Button)

═══════════════════════

<b>📊 ГЛОБАЛЬНА СТАТИСТИКА:</b>
├ 🌐 Всього проектів: <code>аналіз...</code>
├ 🤖 Ботів у системі: <code>синхронізація...</code>
└ 📢 Глобальних розсилок: <code>готова</code>"""

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
