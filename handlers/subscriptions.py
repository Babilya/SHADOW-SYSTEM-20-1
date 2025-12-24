from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

subscriptions_router = Router()

def subscriptions_kb():
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

def subscriptions_description() -> str:
    return """<b>📦 ПАКЕТИ ПІДПИСОК</b>

<b>💳 ВАШ ПОТОЧНИЙ: Premium (25 днів залишилось)</b>

<b>📊 ПОРІВНЯННЯ ТАРИФІВ:</b>

<b>🆓 FREE - Безкоштовно</b>
├ Боти: 5
├ Розсилок: 10/мес
├ Парсинг: 100 контактів
├ OSINT: Вимкнено
├ AI Sentiment: Ні
└ Підтримка: Email (48 годин)

<b>⭐ STANDARD - 300 ⭐/мес</b>
├ Боти: 50
├ Розсилок: 500/мес
├ Парсинг: 5,000 контактів
├ OSINT: 50 запитів
├ AI Sentiment: Базова
└ Підтримка: Chat (4 години)

<b>👑 PREMIUM - 600 ⭐/мес (ВАШ ПОТОЧНИЙ)</b>
├ Боти: 100
├ Розсилок: 5,000/мес
├ Парсинг: 50,000 контактів
├ OSINT: 500 запитів
├ AI Sentiment: Повна
├ Прогноз ризиків: ✅
└ Підтримка: Chat (1 година)

<b>💎 ELITE - 1,200 ⭐/мес</b>
├ Боти: Необмежено
├ Розсилок: Необмежено
├ Парсинг: Необмежено
├ OSINT: Необмежено
├ AI: Всі функції
├ Пріоритетна підтримка: 24/7
└ Персональний менеджер: ✅

<b>🎁 СПЕЦІАЛЬНІ ПРОПОЗИЦІЇ:</b>
✓ 3-місячна підписка = -10%
✓ 12-місячна підписка = -25%
✓ Реферальний програма = +20% бонус
✓ Корпоративні тарифи = До -40%"""

@subscriptions_router.message(Command("subscription"))
async def subscription_cmd(message: Message):
    await message.answer(subscriptions_description(), reply_markup=subscriptions_kb(), parse_mode="HTML")

@subscriptions_router.callback_query(F.data == "subscription_main")
async def subscription_menu(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text(subscriptions_description(), reply_markup=subscriptions_kb(), parse_mode="HTML")

@subscriptions_router.callback_query(F.data == "tier_free")
async def tier_free(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Підтримка", callback_data="subscription_support")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="subscription_main")]
    ])
    await query.message.edit_text("""🆓 <b>FREE ПЛАН</b>

<b>💰 ЦІНА: Безкоштовно (0 ⭐)</b>

<b>📊 МОЖЛИВОСТІ:</b>
• Боти: 5 | Розсилок: 10/мес | Парсинг: 100 контактів
• OSINT: Вимкнено | AI Sentiment: Ні
• Сховище: 1 GB | Тексті: 3 шаблони
• Підтримка: Email (48 годин відповіді)

<b>🎯 КОМУ ПІДХОДИТЬ:</b>
✓ Новачкам для тестування
✓ Маленьким проектам
✓ Навчанню платформи

<b>❌ ОБМЕЖЕННЯ:</b>
✗ Немає OSINT функцій
✗ Немає AI аналізу
✗ Обмежена техпідтримка
✗ Немає API доступу

<b>💡 РЕКОМЕНДАЦІЯ:</b>
Для більших проектів обновіть на Standard (тільки +300 ⭐/мес)""", reply_markup=kb, parse_mode="HTML")

@subscriptions_router.callback_query(F.data == "tier_standard")
async def tier_standard(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Купити (300 ⭐/мес)", callback_data="buy_standard")],
        [InlineKeyboardButton(text="💬 Підтримка", callback_data="subscription_support")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="subscription_main")]
    ])
    await query.message.edit_text("""⭐ <b>STANDARD ПЛАН</b>

<b>💰 ЦІНА: 300 ⭐/мес</b>

<b>📊 МОЖЛИВОСТІ:</b>
• Боти: 50 | Розсилок: 500/мес | Парсинг: 5,000 контактів
• OSINT: 50 запитів | AI Sentiment: Базова версія
• Сховище: 10 GB | Текстовок: 6 шаблонів + редактор
• Підтримка: Chat (4 години відповіді)

<b>✅ ПЕРЕВАГИ:</b>
✓ 10x більше можливостей ніж Free
✓ OSINT функції включені
✓ Базовий AI аналіз
✓ Швидша техпідтримка
✓ API доступ

<b>📈 СТАТИСТИКА КОРИСТУВАЧІВ:</b>
Середній ROI: 300% | Середній месячний заробок: ₴4,500

<b>🎯 КОМУ ПІДХОДИТЬ:</b>
✓ Середнім проектам
✓ Тим, хто зростає
✓ Любителям автоматизації

<b>💡 ПАКЕТНІ ЦІНИ:</b>
3 місяці: 810 ⭐ (-10%) | 12 місяців: 2,700 ⭐ (-25%)""", reply_markup=kb, parse_mode="HTML")

@subscriptions_router.callback_query(F.data == "tier_premium")
async def tier_premium(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Поновити (600 ⭐/мес)", callback_data="renew_premium")],
        [InlineKeyboardButton(text="💬 Підтримка", callback_data="subscription_support")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="subscription_main")]
    ])
    await query.message.edit_text("""👑 <b>PREMIUM ПЛАН (ВАШ ПОТОЧНИЙ)</b>

<b>💰 ЦІНА: 600 ⭐/мес</b>
<b>⏰ ЗАЛИШИЛОСЬ: 25 днів</b>

<b>📊 МОЖЛИВОСТІ:</b>
• Боти: 100 | Розсилок: 5,000/мес | Парсинг: 50,000 контактів
• OSINT: 500 запитів | AI Sentiment: Повна версія
• Прогноз ризиків: ✅ | Сховище: 100 GB
• Текстовок: Необмежено + A/B тестування
• Підтримка: Chat (1 година відповіді)

<b>✅ ПЕРЕВАГИ:</b>
✓ 10x більше ніж Standard
✓ Повний AI аналіз
✓ Прогноз ризиків блокування
✓ A/B тестування текстовок
✓ Пріоритетна технічна підтримка
✓ Командна робота (2 менеджери)

<b>📈 СТАТИСТИКА КОРИСТУВАЧІВ:</b>
Середній ROI: 450% | Середній месячний заробок: ₴8,900

<b>💡 ВІТАЄМО! Ви вже прибутковий користувач! 🎉</b>""", reply_markup=kb, parse_mode="HTML")

@subscriptions_router.callback_query(F.data == "tier_elite")
async def tier_elite(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Апгрейдити на Elite (1,200 ⭐/мес)", callback_data="buy_elite")],
        [InlineKeyboardButton(text="💬 Підтримка", callback_data="subscription_support")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="subscription_main")]
    ])
    await query.message.edit_text("""💎 <b>VIP ELITE ПЛАН</b>

<b>💰 ЦІНА: 1,200 ⭐/мес</b>

<b>📊 МОЖЛИВОСТІ:</b>
• Боти: Необмежено | Розсилок: Необмежено | Парсинг: Необмежено
• OSINT: Необмежено | AI: Всі функції + Custom моделі
• Сховище: Необмежено | Текстовок: Необмежено
• API доступ: Повний + WebSocket
• Інтеграції: 50+ сервісів включено
• Підтримка: 24/7 Chat + Телефон

<b>🌟 СПЕЦІАЛЬНІ ПЕРЕВАГИ ELITE:</b>
✓ Персональний менеджер проектів
✓ Приватний Slack канал для комунікації
✓ Месячні стратегічні консультації
✓ Пріоритет в новихфункціях
✓ Custom розробки на замовлення
✓ Гарантія 99.99% uptime (SLA)
✓白-label рішення
✓ Корпоративні навчання (до 10 осіб)

<b>📈 СТАТИСТИКА КЛІЄНТІВ ELITE:</b>
Середній ROI: 600% | Середній месячний заробок: ₴18,900
Клієнти: 45+ компаній в Україні і СНД

<b>🎁 СПЕЦІАЛЬНА ПРОПОЗИЦІЯ:</b>
Перші 3 місяці: -30% = 840 ⭐/мес
Потім: 1,200 ⭐/мес (стандартна ціна)

<b>🏆 РЕКОМЕНДОВАНО ДЛЯ:</b>
✓ Крупних компаній
✓ Агенцій з командою 5+
✓ Серйозних підприємців""", reply_markup=kb, parse_mode="HTML")

@subscriptions_router.callback_query(F.data == "subscription_support")
async def subscription_support(query: CallbackQuery):
    await query.answer()
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="subscription_main")]])
    await query.message.edit_text("""💬 <b>ТЕХНІІЧНА ПІДТРИМКА</b>

<b>🕐 ЧАСИ РОБОТИ:</b>
Понеділок-Пятниця: 09:00 - 18:00 (UTC+2)
Субота-Неділя: 10:00 - 16:00 (УТ+2)

<b>📞 СПОСОБИ ЗВ'ЯЗКУ:</b>
├ Chat на платформі (1-4 години)
├ Email: support@shadowsystem.io (24-48 годин)
├ Telegram: @shadow_support_bot (миттєво)
└ Phone (Elite): +380 44 XXX XXXX

<b>❓ ЧАСТІ ЗАПИТАННЯ:</b>
• Як додати ботів?
• Як запустити розсилку?
• Як підійняти CTR текстовки?
• Як налаштувати ротацію проксі?
• Як інтегрувати з CRM?
• Як отримати API доступ?

<b>📚 ДОКУМЕНТАЦІЯ:</b>
├ Вікі: https://wiki.shadowsystem.io
├ Відео-туторіали: YouTube канал
├ Вебінари: Щотижня по четвергам
└ Блог: https://blog.shadowsystem.io""", reply_markup=back_kb, parse_mode="HTML")

@subscriptions_router.callback_query(F.data == "subscription_faq")
async def subscription_faq(query: CallbackQuery):
    await query.answer()
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="subscription_main")]])
    await query.message.edit_text("""❓ <b>ЧАСТІ ЗАПИТАННЯ (FAQ)</b>

<b>💳 ОПЛАТА:</b>

❓ Який найешевший спосіб оплати?
✅ Telegram Stars без комісії (0%)

❓ Чи можна отримати повернення?
✅ Так, в межах 14 днів від платежу (мінус комісія)

❓ Чи буде розраховуватися лишок?
✅ Так, автоматично на наступний місяць

<b>🤖 БОТИ:</b>

❓ Скільки ботів можу додати?
✅ Free: 5 | Standard: 50 | Premium: 100 | Elite: Необмежено

❓ Як бути впевненим, що боти не будуть заблоковані?
✅ Використовуйте прогрів (72 години) + ротація проксі

<b>📊 РОЗСИЛКА:</b>

❓ Який оптимальний інтервал між ботами?
✅ 5-10 секунд для безпеки

❓ Коли найкраще відправляти?
✅ 14:00-16:00 або 19:00-21:00

<b>💰 ЗАРОБОК:</b>

❓ Який середній ROI?
✅ Free: 0% | Standard: 300% | Premium: 450% | Elite: 600%

❓ Коли перший заробок?
✅ Зазвичай після першої успішної кампанії (3-7 днів)

<b>⚙️ ТЕХНІЧНЕ:</b>

❓ Чи є API?
✅ Так, включено в Premium+ (REST + WebSocket)

❓ Чи можна інтегрувати з моєю CRM?
✅ Так, підтримуємо 50+ інтеграцій""", reply_markup=back_kb, parse_mode="HTML")

@subscriptions_router.callback_query(F.data == "back_to_menu")
async def subscriptions_back_to_menu(query: CallbackQuery):
    await query.answer()
    from keyboards.user import main_menu, main_menu_description
    await query.message.edit_text(main_menu_description(), reply_markup=main_menu(), parse_mode="HTML")
