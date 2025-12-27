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
    return """══════════════════════════════════════
       🌐 SHADOW SYSTEM iO v2.0
══════════════════════════════════════
<i>Професійна екосистема для Telegram-маркетингу</i>

<b>🔒 СТАТУС:</b> Гостьовий доступ

<b>🚀 ЩО ВИ ОТРИМАЄТЕ:</b>
├ 🤖 Автоматизація управління 1000+ ботами одночасно
├ 🔍 OSINT-інструменти глибокої аналітики та розвідки
├ 📊 Детальна статистика кампаній у реальному часі
├ 👥 CRM-система для координації команди менеджерів
└ 🛡️ Інтегрований захист від блокувань та детекції

<b>📋 ЯК ПОЧАТИ РОБОТУ:</b>
├ 1. Оберіть відповідний тариф із запропонованих планів
├ 2. Заповніть коротку заявку на отримання доступу
├ 3. Отримайте унікальний SHADOW-ключ активації
└ 4. Активуйте повний доступ до системи

<b>💎 ТАРИФНІ ПЛАНИ:</b>
├ 📦 <b>БАЗОВИЙ</b> — ідеальний старт для початківців
├ ⭐ <b>СТАНДАРТ</b> — розширений пакет для агенцій
├ 👑 <b>ПРЕМІУМ</b> — максимум функцій та можливостей
└ 💎 <b>ЕНТЕРПРАЙЗ</b> — індивідуальні корпоративні рішення
══════════════════════════════════════"""

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
    return """══════════════════════════════════════
       🌟 SHADOW SYSTEM iO v2.0
══════════════════════════════════════
<i>Центр оперативного управління менеджера</i>

<b>📋 СТАТУС:</b> 👤 Менеджер проекту

<b>🎯 ВАШІ ЗАВДАННЯ ТА ІНСТРУМЕНТИ:</b>

<b>🚀 КАМПАНІЇ:</b>
├ Створення та запуск масових розсилок за шаблонами
├ Налаштування таргетингу цільової аудиторії проекту
└ Моніторинг статусу виконання кампаній у реальному часі

<b>🤖 БОТНЕТ:</b>
├ Контроль стану всіх підключених ботів у мережі
└ Перегляд детальних логів активності та помилок

<b>📊 АНАЛІТИКА:</b>
├ Відстеження показників CTR та конверсії розсилок
└ Аналіз загальної ефективності ваших кампаній

<b>✍️ ТЕКСТОВКИ:</b>
├ Доступ до бібліотеки перевірених шаблонів
└ AI-редагування повідомлень для обходу спам-фільтрів
──────────────────────────────────────
<b>💡 ПІДКАЗКА:</b> Для розширення прав зверніться до Лідера
══════════════════════════════════════"""

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
    return """══════════════════════════════════════
       👑 SHADOW SYSTEM iO v2.0
══════════════════════════════════════
<i>Командний центр лідера проекту</i>

<b>💼 СТАТУС:</b> 🔑 Власник проекту (Leader)

<b>🎛️ ПОВНИЙ КОНТРОЛЬ ЕКОСИСТЕМИ:</b>

<b>🤖 BOTNET & PROXY:</b>
├ Масовий імпорт ботів з різних форматів сесій
├ Налаштування проксі та автоматична ротація IP
└ Інтелектуальні цикли прогріву облікових записів

<b>🔍 OSINT & ПАРСИНГ:</b>
├ Глибока розвідка аудиторії та геосканування міст
├ Аналіз користувачів та виявлення ключових осіб
└ Експорт баз даних для точкових кампаній

<b>🚀 КАМПАНІЇ & ВОРОНКИ:</b>
├ A/B тестування та автоматизація воронок продажів
├ Глобальне планування розсилок за розкладом
└ Тригерні переходи між етапами воронки

<b>📝 ШАБЛОНИ & КОМУНІКАЦІЯ:</b>
├ Бібліотека готових шаблонів для всіх типів розсилок
├ Планування повідомлень за розкладом та інтервалами
└ Центр підтримки з повноцінною тікет-системою

<b>👥 УПРАВЛІННЯ КОМАНДОЮ:</b>
├ Найм та розподіл менеджерів через INV-коди
└ Контроль KPI та налаштування прав доступу
──────────────────────────────────────
<b>📈 МОНІТОРИНГ ПРОЕКТУ:</b>
├ 🤖 Ботів у мережі: <code>активно</code>
├ 👥 Менеджерів у штаті: <code>на зв'язку</code>
├ 📊 Кампаній проведено: <code>в процесі</code>
└ 🛡️ Система анти-бан: <b>ОПТИМІЗОВАНО</b>
══════════════════════════════════════"""

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
        [InlineKeyboardButton(text="📱 ПЕРЕГЛЯД МЕНЮ ЮЗЕРА", callback_data="user_menu")],
        [InlineKeyboardButton(text="🆘 EMERGENCY ALERT", callback_data="admin_emergency")]
    ])

def admin_description() -> str:
    return """══════════════════════════════════════
       🛡️ SHADOW SYSTEM iO v2.0
══════════════════════════════════════
<i>Центральний пульт адміністратора системи</i>

<b>💎 СТАТУС:</b> 👑 SuperAdmin / Owner

<b>🔧 ГЛОБАЛЬНЕ АДМІНІСТРУВАННЯ:</b>

<b>⚙️ СИСТЕМА & ЯДРО:</b>
├ Моніторинг навантаження та статусу всіх серверів
├ Управління критичними оновленнями та патчами системи
└ Контроль цілісності та резервного копіювання

<b>👥 КЕРУВАННЯ КОРИСТУВАЧАМИ:</b>
├ Ручна зміна ролей користувачів (Guest/Manager/Leader)
├ Система банів із таймаутами (тимчасові/постійні)
└ Глобальне блокування порушників правил системи

<b>📢 КОМУНІКАЦІЙНИЙ ЦЕНТР:</b>
├ Масові сповіщення користувачам за ролями
├ Система підтримки із тікетами та пріоритетами
├ Управління шаблонами для розсилок
└ Детальна статистика по всіх проектах

<b>🔑 ЛІЦЕНЗІЙНИЙ ЦЕНТР:</b>
├ Генерація унікальних SHADOW-ключів активації
└ Валідація ключів та продовження підписок
──────────────────────────────────────
<b>📊 ГЛОБАЛЬНА СТАТИСТИКА:</b>
├ 🌐 Всього проектів: <code>аналіз...</code>
├ 🤖 Ботів у системі: <code>синхронізація...</code>
└ 📢 Глобальних розсилок: <code>готово</code>
══════════════════════════════════════"""

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
