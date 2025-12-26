from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu() -> InlineKeyboardMarkup:
    """Головне меню - комбіновані кнопки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        # Рядок 1: Боти & OSINT (2 кнопки)
        [
            InlineKeyboardButton(text="🤖 Боти", callback_data="botnet_main"),
            InlineKeyboardButton(text="🔍 OSINT", callback_data="osint_main")
        ],
        # Рядок 2: Кампанії & Аналітика (2 кнопки)
        [
            InlineKeyboardButton(text="📝 Кампанії", callback_data="campaigns_main"),
            InlineKeyboardButton(text="📊 Аналітика", callback_data="analytics_main")
        ],
        # Рядок 3: Баланс & Підписки (комбіновані платежі) (2 кнопки)
        [
            InlineKeyboardButton(text="⭐ Баланс & Платежі", callback_data="balance_payments_main"),
            InlineKeyboardButton(text="📦 Підписки", callback_data="subscription_main")
        ],
        # Рядок 4: Команда & Налаштування (2 кнопки)
        [
            InlineKeyboardButton(text="👥 Команда", callback_data="team_main"),
            InlineKeyboardButton(text="⚙️ Налаштування", callback_data="settings_main")
        ],
        # Рядок 5: Прогрів & Планувальник (2 кнопки)
        [
            InlineKeyboardButton(text="🔥 Прогрів", callback_data="warming_menu"),
            InlineKeyboardButton(text="📅 Планувальник", callback_data="scheduler_menu")
        ],
        # Рядок 6: Гео & Текстовки (2 кнопки)
        [
            InlineKeyboardButton(text="🌍 Гео-скан", callback_data="geo_menu"),
            InlineKeyboardButton(text="📝 Текстовки", callback_data="texting_main")
        ],
        # Рядок 7: Довідка & Профіль (2 кнопки)
        [
            InlineKeyboardButton(text="📚 Довідка", callback_data="help_main"),
            InlineKeyboardButton(text="👤 Профіль", callback_data="profile_main")
        ],
    ])

def main_menu_description() -> str:
    """Розширений опис з проектом"""
    return """<b>🌟 SHADOW SYSTEM iO v2.0</b>
<i>Комплексна платформа для управління ботами, OSINT та маркетинг-кампаніями</i>

<b>📋 ОСНОВНІ РОЗДІЛИ:</b>

<b>🤖 BOTNET</b> - Управління Telegram ботами
├ ➕ Додавання (CSV з телефонів)
├ 📋 Список ботів (статус, активність)
├ 🔄 Ротація проксі (SOCKS5, HTTP)
└ 🔥 Прогрів ботів перед розсилкою

<b>🔍 OSINT & ПАРСИНГ</b> - Розвідка даних
├ 📍 Геосканування за локацією
├ 👤 Аналіз користувачів (профілі)
├ 💬 Аналіз чатів та трендів
└ 📊 Логи видалень з архівом

<b>📝 КАМПАНІЇ</b> - Управління проектами
├ 🤖 Управління ботами в кампаніях
├ 👥 Команда менеджерів & рейтинг
├ 📊 Статистика та метрики
└ 💬 Текстовки та шаблони повідомлень

<b>📊 АНАЛІТИКА</b> - Звіти & метрики
├ 📈 Дашборд кампаній (CTR, ROI)
├ 🤖 AI Sentiment (позитив/негатив)
├ ⚠️ Прогноз ризиків блокування
└ 💾 Експорт в PDF/Excel

<b>⭐ БАЛАНС & ПЛАТЕЖІ</b> - Система рахунків
├ 💵 Баланс (поточний: 5,240 ⭐)
├ ➕ Поповнення (Telegram Stars, Карта, Liqpay)
├ 📜 Історія платежів
└ 💎 Розраховані кошти за проекти

<b>📦 ПІДПИСКИ</b> - Тарифи
├ 🆓 Free (0 ⭐) - 5 ботів, 10 розсилок
├ ⭐ Standard (300 ⭐/мес) - 50 ботів
├ 👑 Premium (600 ⭐/мес) - 100 ботів
└ 💎 Elite (1200 ⭐/мес) - Необмежено

<b>👥 КОМАНДА</b> - Гібридне управління
├ 👥 Менеджери (додавання, рейтинг)
├ 📊 Активність (статистика)
└ ⭐ Рейтинг якості роботи

<b>⚙️ НАЛАШТУВАННЯ</b> - Конфіг профілю
├ 👻 Привидний режим
├ 🔔 Сповіщення (вкл/вимк)
├ 🌐 Мова інтерфейсу
└ 🔐 Безпека (2FA, шифрування)

<b>📝 ТЕКСТОВКИ</b> - Кампанії зі шаблонами
├ 📚 Готові шаблони (6 типів)
├ ✏️ Редактор текстовок
└ 📊 Аналіз результатів

<b>📚 ДОВІДКА</b> - Документація & Підтримка
├ 📖 Інструкції по модулям
├ ❓ FAQ з відповідями
├ 💬 Чат з технічною підтримкою
└ 🎥 Відео-туторіали

<b>👤 ПРОФІЛЬ</b> - Особисні дані
├ 📊 Статистика користувача
├ 🎁 Бонуси & промокоди
└ 🔑 Управління сесіями

<b>💡 ПОРАДИ:</b>
✓ Почніть з /start для детальної інструкції
✓ Скористайтеся документацією при запитаннях
✓ Технічна підтримка доступна 24/7"""

def balance_payments_menu() -> InlineKeyboardMarkup:
    """Комбіноване меню баланс + платежі"""
    return InlineKeyboardMarkup(inline_keyboard=[
        # Рядок 1: Баланс & Історія (2 кнопки)
        [
            InlineKeyboardButton(text="💵 Мій баланс", callback_data="balance_view"),
            InlineKeyboardButton(text="📜 Історія", callback_data="payments_history")
        ],
        # Рядок 2: Поповнення способи (2 кнопки)
        [
            InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="stars_payment"),
            InlineKeyboardButton(text="💳 Карта", callback_data="card_payment")
        ],
        # Рядок 3: Інші способи (2 кнопки)
        [
            InlineKeyboardButton(text="🔗 Liqpay", callback_data="liqpay_payment"),
            InlineKeyboardButton(text="📄 Рахунок", callback_data="create_invoice")
        ],
        # Рядок 4: Повернення (1 кнопка)
        [
            InlineKeyboardButton(text="♻️ Повернення коштів", callback_data="refund_request")
        ],
        # Рядок 5: Назад (1 кнопка)
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")
        ],
    ])

def subscription_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🆓 Free", callback_data="tier_free"),
            InlineKeyboardButton(text="⭐ Standard", callback_data="tier_standard")
        ],
        [
            InlineKeyboardButton(text="👑 Premium", callback_data="tier_premium"),
            InlineKeyboardButton(text="💎 Elite", callback_data="tier_elite")
        ],
        [
            InlineKeyboardButton(text="💬 Підтримка", callback_data="subscription_support"),
            InlineKeyboardButton(text="❓ FAQ", callback_data="subscription_faq")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
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
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])

def payment_methods() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="stars_payment"),
            InlineKeyboardButton(text="💳 Карта", callback_data="card_payment")
        ],
        [
            InlineKeyboardButton(text="🔗 Liqpay", callback_data="liqpay_payment")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="balance_payments_main")]
    ])
