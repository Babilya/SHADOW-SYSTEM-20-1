from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

router = Router()

HELP_SECTIONS = {
    "botnet": """<b>🤖 BOTNET - Управління ботами</b>
<i>Централізований контроль мережі</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>📋 ЩО ЦЕ ТАКЕ?</b>
Модуль для управління Telegram ботами. Додавайте, видаляйте, моніторте та контролюйте всі боти з одного місця.

<b>⚡ ОСНОВНІ ФУНКЦІЇ:</b>
├ Додавання ботів з телефонів
├ Контроль статусу кожного бота
├ Ротація проксі для анонімності
├ Прогрів ботів перед використанням
└ Моніторинг статусу 24/7

━━━━━━━━━━━━━━━━━━━━━━━

<b>📖 ЯК КОРИСТУВАТИСЯ:</b>
1️⃣ Виконайте /botnet - відкрити модуль
2️⃣ Натисніть "Додати ботів"
3️⃣ Завантажте CSV файл з номерами
4️⃣ Налаштуйте проксі-сервери
5️⃣ Активуйте цикл прогріву""",

    "osint": """<b>🔍 OSINT & ПАРСИНГ</b>
<i>Інструменти розвідки даних</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>📋 ЩО ЦЕ ТАКЕ?</b>
Інструмент для пошуку, аналізу та парсингу даних з Telegram. Знаходить потрібну аудиторію на основі ключових слів, геолокації та інтересів.

<b>⚡ ОСНОВНІ ФУНКЦІЇ:</b>
├ Геосканування по назві міста
├ Аналіз користувачів (активність, інтереси)
├ Парсинг чатів та каналів
├ Експорт контактів у CSV
└ Журнал усіх сканувань

━━━━━━━━━━━━━━━━━━━━━━━

<b>📖 ПРИКЛАДИ ВИКОРИСТАННЯ:</b>
├ 📍 Пошук аудиторії за геолокацією
├ 🎯 Парсинг контактів з груп
├ 💬 Моніторинг конкурентів
└ 📊 Аналітика користувачів""",

    "analytics": """<b>📊 АНАЛІТИКА</b>
<i>Центр аналізу результатів</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>📋 ЩО ЦЕ ТАКЕ?</b>
Дашборд для аналізу кампаній. Показує метрики розсилок, успішність, ROI, sentiment-аналіз та прогнози ризиків.

<b>📈 ОСНОВНІ МЕТРИКИ:</b>
├ Кількість розсилок та статуси
├ CTR (Click-Through Rate)
├ Конверсія та ROI
└ Блокування та помилки

━━━━━━━━━━━━━━━━━━━━━━━

<b>🤖 AI SENTIMENT ANALYSIS:</b>
├ 😊 Позитивні відповіді
├ 😐 Нейтральні відповіді
├ └ 😠 Негативні відповіді

<b>⚠️ ПРОГНОЗ РИЗИКІВ:</b>
├ 🟢 Низький - безпечно
├ 🟡 Середній - затримка
└ 🔴 Високий - 24+ годин

<b>📄 ЗВІТИ:</b>
Щогодинні, щоденні, щотижневі. Експорт у PDF/Excel.""",

    "team": """<b>👥 КОМАНДА</b>
<i>Управління менеджерами</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>📋 ЩО ЦЕ ТАКЕ?</b>
Модуль для управління командою. Розподіляйте задачі між менеджерами, контролюйте якість роботи, управляйте доступом.

<b>⚡ ОСНОВНІ ФУНКЦІЇ:</b>
├ Додавання менеджерів
├ Встановлення ролей та дозволів
├ Розподіл кампаній
├ Рейтинг менеджерів
└ Статистика активності

━━━━━━━━━━━━━━━━━━━━━━━

<b>👤 РОЛІ МЕНЕДЖЕРІВ:</b>
├ 👤 Оператор - розсилає
├ 🔍 Аналітик - аналізує
└ 🛡️ Адмін - управління

<b>⭐ РЕЙТИНГ:</b>
├ Швидкість виконання
├ Якість (успішні кампанії)
├ Надійність (помилки)
└ Комунікація""",

    "subscriptions": """<b>📦 РІВНІ ДОСТУПУ</b>
<i>Система ліцензування SHADOW</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>🔑 АКТИВАЦІЯ ДОСТУПУ:</b>
Система працює на основі ліцензійних ключів. Для отримання ключа зверніться до адміністратора або подайте заявку.

<b>📋 ДОСТУПНІ РІВНІ:</b>

<b>📦 БАЗОВИЙ</b>
├ До 5 ботів
├ 1 менеджер
└ Базові функції

<b>⭐ СТАНДАРТ</b>
├ До 50 ботів
├ 5 менеджерів
└ Повний функціонал

<b>👑 ПРЕМІУМ</b>
├ До 100 ботів
├ Необмежено менеджерів
├ AI функції
└ Пріоритетна підтримка

<b>💎 ЕНТЕРПРАЙЗ</b>
├ Індивідуальна конфігурація
├ API доступ
└ VIP підтримка 24/7

━━━━━━━━━━━━━━━━━━━━━━━

<b>📨 ЯК ОТРИМАТИ КЛЮЧ:</b>
Подайте заявку через меню або зверніться напряму до адміністратора.""",

    "activation": """<b>🔑 АКТИВАЦІЯ ЛІЦЕНЗІЇ</b>
<i>Система ключів SHADOW</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>📋 ЯК АКТИВУВАТИ:</b>
1️⃣ Отримайте ключ від адміністратора
2️⃣ Введіть ключ через меню "Ввести ключ"
3️⃣ Дочекайтесь підтвердження активації

<b>🔐 ФОРМАТ КЛЮЧА:</b>
<code>SHADOW-XXXX-XXXX-XXXX</code>

<b>⚡ ОСОБЛИВОСТІ:</b>
├ Миттєва активація
├ Прив'язка до акаунту
├ Автоматичне оновлення
└ Захист від дублювання

━━━━━━━━━━━━━━━━━━━━━━━

<b>⚠️ ВАЖЛИВО:</b>
Кожен ключ можна активувати лише один раз. Зберігайте ключ у надійному місці.""",

    "settings": """<b>⚙️ НАЛАШТУВАННЯ</b>
<i>Конфігурація системи</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>👤 ПРОФІЛЬ:</b>
├ Змінити ім'я та аватар
├ Двофакторна аутентифікація
├ Вихід з інших пристроїв
└ Видалення акаунту

👻 <b>Привидний режим:</b>
✅ Приховати статус онлайну
✅ Прихована активність для команди
✅ Анонімні логи

🔔 <b>Сповіщення:</b>
✅ Push-сповіщення на телефон
✅ SMS сповіщення
✅ Email дайджесту
✅ Custom Alert rules

🌐 <b>Мова:</b>
• Українська 🇺🇦 (Default)
• Російська 🇷🇺
• Англійська 🇬🇧

🔐 <b>Безпека:</b>
✅ Зміна пароля
✅ Список пристроїв
✅ Session контроль
✅ IP whitelist

📊 <b>Інтеграції:</b>
✅ API ключ
✅ Webhook
✅ CRM інтеграції
✅ Analytics tracking"""
}

def help_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 BOTNET", callback_data="help_botnet")],
        [InlineKeyboardButton(text="🔍 OSINT", callback_data="help_osint")],
        [InlineKeyboardButton(text="📊 ANALYTICS", callback_data="help_analytics")],
        [InlineKeyboardButton(text="👥 TEAM", callback_data="help_team")],
        [InlineKeyboardButton(text="📦 SUBSCRIPTIONS", callback_data="help_subscriptions")],
        [InlineKeyboardButton(text="💳 PAYMENTS", callback_data="help_payments")],
        [InlineKeyboardButton(text="⚙️ SETTINGS", callback_data="help_settings")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])

def help_description() -> str:
    return "📚 <b>ДОВІДКА SHADOW SYSTEM</b>\n\nВиберіть розділ для детальної інформації:"

@router.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(help_description(), reply_markup=help_kb(), parse_mode="HTML")

async def help_menu(message: Message):
    """Функція для виклику з інших модулів"""
    await message.edit_text(help_description(), reply_markup=help_kb(), parse_mode="HTML")

@router.callback_query(F.data.startswith("help_"))
async def show_help(query: CallbackQuery):
    section = query.data.replace("help_", "")
    await query.answer()
    
    if section in HELP_SECTIONS:
        new_text = HELP_SECTIONS[section]
        back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]])
        
        if query.message.text != new_text or query.message.reply_markup != back_kb:
            try:
                await query.message.edit_text(new_text, reply_markup=back_kb, parse_mode="HTML")
            except Exception:
                pass
