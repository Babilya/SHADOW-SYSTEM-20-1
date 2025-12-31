from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

router = Router()

HELP_SECTIONS = {
    "botnet": """🤖 <b>BOTNET</b>
<i>Управління ботами</i>
───────────────
<b>📋 Опис:</b>
Модуль для керування Telegram ботами та акаунтами.

<b>⚡ Функції:</b>
├ Додавання ботів
├ Контроль статусу
├ Ротація проксі
├ Прогрів акаунтів
└ Моніторинг 24/7
───────────────
<b>📖 Як користуватись:</b>
├ 1. /botnet
├ 2. Додати ботів
├ 3. Завантажити CSV
├ 4. Налаштувати проксі
└ 5. Активувати прогрів""",

    "osint": """🔍 <b>OSINT & ПАРСИНГ</b>
<i>Розвідка та збір даних</i>
───────────────
<b>📋 Опис:</b>
Пошук та аналіз даних з Telegram.

<b>⚡ Функції:</b>
├ Геосканування
├ Аналіз юзерів
├ Парсинг чатів
├ Експорт CSV
└ Журнал операцій
───────────────
<b>📖 Приклади:</b>
├ 📍 Пошук по гео
├ 🎯 Парсинг груп
├ 💬 Моніторинг
└ 📊 Аналітика""",

    "analytics": """📊 <b>АНАЛІТИКА</b>
<i>Аналіз кампаній</i>
───────────────
<b>📋 Опис:</b>
Дашборд для аналізу розсилок.

<b>📈 Метрики:</b>
├ Кількість розсилок
├ CTR (кліки)
├ Конверсія / ROI
└ Блокування
───────────────
<b>🤖 AI Sentiment:</b>
├ 😊 Позитивні
├ 😐 Нейтральні
└ 😠 Негативні

<b>⚠️ Ризики:</b>
├ 🟢 Низький
├ 🟡 Середній
└ 🔴 Високий""",

    "team": """👥 <b>КОМАНДА</b>
<i>Управління менеджерами</i>
───────────────
<b>📋 Опис:</b>
Модуль координації команди.

<b>⚡ Функції:</b>
├ Додавання (INV-коди)
├ Ролі та дозволи
├ Розподіл кампаній
├ Рейтинг
└ Статистика
───────────────
<b>👤 Ролі:</b>
├ 👤 Оператор
├ 🔍 Аналітик
└ 🛡️ Адмін

<b>⭐ Рейтинг:</b>
├ Швидкість
├ Якість
├ Надійність
└ Комунікація""",

    "subscriptions": """📦 <b>РІВНІ ДОСТУПУ</b>
<i>Система ліцензій SHADOW</i>
───────────────
<b>🔑 Активація:</b>
Ліцензійні ключі від адміна.

<b>📋 Рівні:</b>

<b>📦 БАЗОВИЙ:</b>
├ До 5 ботів
├ 1 менеджер
└ Базові функції

<b>⭐ СТАНДАРТ:</b>
├ До 50 ботів
├ 5 менеджерів
└ Повний функціонал

<b>👑 ПРЕМІУМ:</b>
├ До 100 ботів
├ Безліміт менеджерів
├ AI функції
└ Пріоритет підтримка

<b>💎 ЕНТЕРПРАЙЗ:</b>
├ Індивідуальна конфіг
├ API доступ
└ VIP підтримка 24/7""",

    "activation": """🔑 <b>АКТИВАЦІЯ</b>
<i>Система ключів</i>
───────────────
<b>📋 Як активувати:</b>
├ 1. Отримайте ключ
├ 2. Введіть у меню
└ 3. Підтвердження

<b>🔐 Формат:</b>
<code>SHADOW-XXXX-XXXX-XXXX</code>

<b>⚡ Особливості:</b>
├ Миттєва активація
├ Прив'язка до TG
├ Автооновлення
└ Захист від дублів
───────────────
<b>⚠️</b> Ключ = 1 активація""",

    "settings": """⚙️ <b>НАЛАШТУВАННЯ</b>
<i>Конфігурація</i>
───────────────
<b>👤 Профіль:</b>
├ Ім'я / аватар
├ 2FA захист
├ Вихід з сесій
└ Видалення акаунту

<b>👻 Привидний режим:</b>
├ ✅ Прихований статус
├ ✅ Анонімна активність
└ ✅ Приховані логи

<b>🔔 Сповіщення:</b>
├ ✅ Push
├ ✅ SMS
├ ✅ Email
└ ✅ Custom rules

<b>🔐 Безпека:</b>
├ ✅ Зміна пароля
├ ✅ Активні пристрої
├ ✅ Контроль сесій
└ ✅ IP whitelist"""
}

def help_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🤖 BOTNET", callback_data="help_botnet"),
            InlineKeyboardButton(text="🔍 OSINT", callback_data="help_osint")
        ],
        [
            InlineKeyboardButton(text="📊 ANALYTICS", callback_data="help_analytics"),
            InlineKeyboardButton(text="👥 TEAM", callback_data="help_team")
        ],
        [
            InlineKeyboardButton(text="📦 SUBSCRIPTIONS", callback_data="help_subscriptions"),
            InlineKeyboardButton(text="⚙️ SETTINGS", callback_data="help_settings")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])

def help_description() -> str:
    return """📚 <b>ДОВІДКА SHADOW</b>
<i>Виберіть розділ:</i>
───────────────
<b>🔧 Доступні розділи:</b>
├ 🤖 Botnet
├ 🔍 OSINT
├ 📊 Analytics
├ 👥 Team
├ 📦 Subscriptions
└ ⚙️ Settings"""

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
        back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="help_main")]])
        
        if query.message.text != new_text or query.message.reply_markup != back_kb:
            try:
                await query.message.edit_text(new_text, reply_markup=back_kb, parse_mode="HTML")
            except Exception:
                pass

@router.callback_query(F.data == "help_main")
async def help_main_callback(query: CallbackQuery):
    await query.answer()
    try:
        await query.message.edit_text(help_description(), reply_markup=help_kb(), parse_mode="HTML")
    except:
        pass
