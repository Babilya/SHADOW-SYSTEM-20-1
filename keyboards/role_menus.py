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
        [
            InlineKeyboardButton(text="🚀 Кампанії", callback_data="campaigns_main"),
            InlineKeyboardButton(text="🤖 Боти", callback_data="botnet_main")
        ],
        [
            InlineKeyboardButton(text="📊 Аналітика", callback_data="analytics_main"),
            InlineKeyboardButton(text="✍️ Текстовки", callback_data="texting_main")
        ],
        [
            InlineKeyboardButton(text="📖 Довідка", callback_data="help_main"),
            InlineKeyboardButton(text="👤 Мій профіль", callback_data="profile_main")
        ]
    ])

def manager_description() -> str:
    return """<b>🌟 SHADOW SYSTEM iO v2.0</b>
<i>Панель менеджера</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>🎯 ВАШІ ІНСТРУМЕНТИ:</b>

<b>🚀 Кампанії</b>
Створюйте розсилки, налаштовуйте таргетинг та відстежуйте результати в реальному часі.

<b>🤖 Боти</b>
Моніторинг статусу ботів, перегляд активності та помилок.

<b>📊 Аналітика</b>
Детальна статистика ефективності ваших кампаній.

<b>✍️ Текстовки</b>
Бібліотека шаблонів та AI-генерація текстів.

━━━━━━━━━━━━━━━━━━━━━━━

<b>💡 Порада:</b>
<i>Для розширення можливостей зверніться до Лідера проекту або адміністратора.</i>"""

def leader_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🤖 Боти", callback_data="botnet_main"),
            InlineKeyboardButton(text="🔍 OSINT", callback_data="osint_main")
        ],
        [
            InlineKeyboardButton(text="🚀 Кампанії", callback_data="campaigns_main"),
            InlineKeyboardButton(text="📊 Аналітика", callback_data="analytics_main")
        ],
        [
            InlineKeyboardButton(text="📦 Підписки", callback_data="subscription_main")
        ],
        [
            InlineKeyboardButton(text="👥 Команда", callback_data="team_main"),
            InlineKeyboardButton(text="⚙️ Налаштування", callback_data="settings_main")
        ],
        [
            InlineKeyboardButton(text="🔥 Прогрів", callback_data="warming_main"),
            InlineKeyboardButton(text="📅 Планувальник", callback_data="scheduler_main")
        ],
        [
            InlineKeyboardButton(text="🌍 Гео-скан", callback_data="geo_scan"),
            InlineKeyboardButton(text="✍️ Текстовки", callback_data="texting_main")
        ],
        [
            InlineKeyboardButton(text="📖 Довідка", callback_data="help_main"),
            InlineKeyboardButton(text="👤 Профіль", callback_data="profile_main")
        ]
    ])

def leader_description() -> str:
    return """<b>👑 SHADOW SYSTEM iO v2.0</b>
<i>Командний центр лідера</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>🎛️ ПОВНЕ УПРАВЛІННЯ ПРОЕКТОМ:</b>

<b>🤖 Botnet</b>
Імпорт ботів, налаштування проксі, моніторинг активності та автоматичний прогрів.

<b>🔍 OSINT</b>
Геосканування, парсинг аудиторії, глибокий аналіз та експорт даних.

<b>🚀 Кампанії</b>
Масові розсилки з A/B тестуванням та детальною аналітикою.

<b>📊 Аналітика</b>
AI-аналіз, прогнозування ризиків та візуалізація результатів.

<b>👥 Команда</b>
Управління менеджерами, розподіл завдань та рейтинг ефективності.

<b>⚙️ Налаштування</b>
Конфігурація проекту, автовідповідачі та інтеграції.

━━━━━━━━━━━━━━━━━━━━━━━

<b>📈 СТАТУС ПРОЕКТУ:</b>
├ 🤖 Ботів підключено
├ 👥 Менеджерів активних
├ 📊 Кампаній запущено
└ 🛡️ Система захисту активна"""

def admin_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👥 Користувачі", callback_data="admin_users"),
            InlineKeyboardButton(text="📝 Заявки", callback_data="admin_applications")
        ],
        [
            InlineKeyboardButton(text="🔑 Ліцензії", callback_data="admin_keys"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton(text="📢 Розсилка", callback_data="admin_broadcast"),
            InlineKeyboardButton(text="🚫 Блокування", callback_data="admin_block")
        ],
        [
            InlineKeyboardButton(text="⚙️ Система", callback_data="admin_settings"),
            InlineKeyboardButton(text="🔐 Безпека", callback_data="admin_security")
        ],
        [InlineKeyboardButton(text="📋 Аудит логи", callback_data="admin_audit")],
        [InlineKeyboardButton(text="📱 Режим користувача", callback_data="user_menu")]
    ])

def admin_description() -> str:
    return """<b>🛡️ АДМІНІСТРАТИВНА ПАНЕЛЬ</b>
<i>Центр управління системою</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>🔧 ІНСТРУМЕНТИ АДМІНІСТРАТОРА:</b>

<b>👥 Користувачі</b>
Управління акаунтами, ролями та правами доступу.

<b>📝 Заявки</b>
Обробка запитів на активацію, перегляд історії заявок.

<b>🔑 Ліцензії</b>
Генерація SHADOW-ключів, управління терміном дії.

<b>📊 Статистика</b>
Аналітика використання системи та активності користувачів.

<b>📢 Розсилка</b>
Масові повідомлення для всіх або обраних користувачів.

<b>🔐 Безпека</b>
Моніторинг підозрілої активності та захист системи.

━━━━━━━━━━━━━━━━━━━━━━━

<b>📈 ЗАГАЛЬНА СТАТИСТИКА:</b>
├ 👥 Активних користувачів
├ 🔑 Виданих ліцензій
├ 📊 Проектів у системі
└ 🛡️ Статус безпеки: АКТИВНИЙ"""

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
