from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.roles import UserRole

def guest_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Тарифи", callback_data="subscription_main")],
        [InlineKeyboardButton(text="🔑 Ввести ключ", callback_data="enter_key"),
         InlineKeyboardButton(text="💬 Підтримка", callback_data="support")],
        [InlineKeyboardButton(text="📚 Довідка", callback_data="help_main")]
    ])

def guest_description() -> str:
    return """<b>👋 SHADOW SYSTEM iO v2.0</b>

<b>Ви ще не авторизовані в системі.</b>

<b>Як отримати повний доступ:</b>
1️⃣ Оберіть тариф → 📦 Тарифи
2️⃣ Подайте заявку в обраному тарифі
3️⃣ Отримайте ключ від адміністратора
4️⃣ Введіть ключ → 🔑 Ввести ключ

<b>📦 Доступні тарифи:</b>
├ 📦 БАЗОВИЙ — від 4,200 ₴
├ ⭐ СТАНДАРТ — від 12,500 ₴
├ 👑 ПРЕМІУМ — від 62,500 ₴
└ 💎 ПЕРСОНАЛЬНИЙ — від 100,000 ₴"""

def manager_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Кампанії", callback_data="campaigns_main"),
            InlineKeyboardButton(text="🤖 Боти", callback_data="botnet_main")
        ],
        [
            InlineKeyboardButton(text="📊 Аналітика", callback_data="analytics_main"),
            InlineKeyboardButton(text="📝 Текстовки", callback_data="texting_main")
        ],
        [InlineKeyboardButton(text="📚 Довідка", callback_data="help_main")],
        [InlineKeyboardButton(text="👤 Профіль", callback_data="profile_main")]
    ])

def manager_description() -> str:
    return """<b>🌟 SHADOW SYSTEM iO v2.0</b>
<i>Роль: Менеджер</i>

<b>📋 ДОСТУПНІ ФУНКЦІЇ:</b>

<b>📝 Кампанії</b> - Створення та управління розсилками
<b>🤖 Боти</b> - Перегляд статусу ботів
<b>📊 Аналітика</b> - Перегляд статистики
<b>📝 Текстовки</b> - Редагування шаблонів

<b>💡 Підказка:</b>
Зверніться до Лідера проекту для розширення можливостей."""

def leader_menu() -> InlineKeyboardMarkup:
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
            InlineKeyboardButton(text="⭐ Баланс", callback_data="balance_payments_main"),
            InlineKeyboardButton(text="📦 Підписки", callback_data="subscription_main")
        ],
        [
            InlineKeyboardButton(text="👥 Команда", callback_data="team_main"),
            InlineKeyboardButton(text="⚙️ Налаштування", callback_data="settings_main")
        ],
        [
            InlineKeyboardButton(text="📝 Текстовки", callback_data="texting_main"),
            InlineKeyboardButton(text="📚 Довідка", callback_data="help_main")
        ],
        [InlineKeyboardButton(text="👤 Профіль", callback_data="profile_main")]
    ])

def leader_description() -> str:
    return """<b>🌟 SHADOW SYSTEM iO v2.0</b>
<i>Роль: Лідер проекту</i>

<b>📋 ПОВНИЙ ДОСТУП:</b>

<b>🤖 Botnet</b> - Управління ботами, імпорт, прогрів
<b>🔍 OSINT</b> - Геосканування, парсинг, аналіз
<b>📝 Кампанії</b> - Створення та розсилки
<b>📊 Аналітика</b> - Звіти, AI Sentiment, ризики
<b>⭐ Баланс</b> - Поповнення, історія платежів
<b>📦 Підписки</b> - Управління тарифом
<b>👥 Команда</b> - Менеджери, ролі, рейтинг
<b>⚙️ Налаштування</b> - Конфігурація проекту

<b>📈 Статистика проекту:</b>
├ Ботів: 45/100
├ Менеджерів: 3/15
└ Підписка: Premium (25 днів)"""

def admin_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👥 Користувачі", callback_data="admin_users"),
            InlineKeyboardButton(text="📝 Заявки", callback_data="admin_applications")
        ],
        [
            InlineKeyboardButton(text="🔑 Ключі", callback_data="admin_keys"),
            InlineKeyboardButton(text="💰 Платежі", callback_data="admin_payments")
        ],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
            InlineKeyboardButton(text="📢 Розсилка", callback_data="admin_broadcast")
        ],
        [
            InlineKeyboardButton(text="⚙️ Налаштування", callback_data="admin_settings"),
            InlineKeyboardButton(text="🚫 Блокування", callback_data="admin_block")
        ],
        [InlineKeyboardButton(text="🔄 Змінити роль", callback_data="admin_change_role")],
        [InlineKeyboardButton(text="📱 Користувацьке меню", callback_data="user_menu")]
    ])

def admin_description() -> str:
    return """<b>🛡️ АДМІНІСТРАТИВНА ПАНЕЛЬ</b>
<i>Роль: Адміністратор</i>

<b>👑 ПОВНЕ УПРАВЛІННЯ СИСТЕМОЮ:</b>

<b>👥 Користувачі</b> - Перегляд, редагування, ролі
<b>📝 Заявки</b> - Обробка заявок на підписку
<b>🔑 Ключі</b> - Генерація та управління ключами
<b>💰 Платежі</b> - Контроль транзакцій
<b>📊 Статистика</b> - Загальна аналітика системи
<b>📢 Розсилка</b> - Масове повідомлення
<b>⚙️ Налаштування</b> - Конфігурація системи
<b>🚫 Блокування</b> - Управління доступом

<b>📈 Загальна статистика:</b>
├ Користувачів: 1,245
├ Активних: 456
├ Преміум: 234
└ Дохід/міс: ₴45,230"""

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
