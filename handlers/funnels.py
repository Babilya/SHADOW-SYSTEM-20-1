from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

funnels_router = Router()

class FunnelStates(StatesGroup):
    onboarding_step1 = State()
    onboarding_step2 = State()
    onboarding_step3 = State()

# ====== ONBOARDING FUNNEL ======
ONBOARDING_TEXT = {
    "step1": """🎯 <b>SHADOW SYSTEM iO v2.0</b>

Ласкаво просимо в найпотужнішу систему для управління Telegram ботнетом!

<b>Що ми пропонуємо:</b>
✅ Управління 100+ ботами одночасно
✅ Автоматичні розсилки з AI-аналітикою
✅ OSINT розвідка та парсинг даних
✅ Гібридна командна робота
✅ Аналітика з sentiment analysis
✅ Гнучкі тарифи від Free до Elite

<b>Вибір тарифу:</b>
🆓 Free - Безкоштовно (обмежено)
⭐ Standard - 300 грн/мес
👑 Premium - 600 грн/мес
💎 Elite - 1,200 грн/мес

Почнемо? 👇""",

    "step2": """📚 <b>Як почати роботу?</b>

<b>Крок 1: Управління ботами</b>
🤖 Додайте своїх Telegram ботів
📋 Контролюйте кожного по окремому
🔄 Автоматична ротація проксі

<b>Крок 2: Розсилки</b>
📧 Налаштуйте мішень аудиторію
💬 Напишіть повідомлення
⏰ Встановіть розклад відправлення

<b>Крок 3: Аналізуйте результати</b>
📊 Дашборд з метриками
😊 AI sentiment analysis
⚠️ Прогноз ризиків

Далі →""",

    "step3": """🚀 <b>Розширені можливості</b>

<b>OSINT & Парсинг:</b>
🔍 Геосканування по ключовим словам
👤 Аналіз користувачів
💬 Сканування чатів і каналів
📊 Лог всіх операцій

<b>Команда & Менеджмент:</b>
👥 Запросіть менеджерів
⭐ Рейтинг по якості роботи
📈 Аналітика команди
💰 Контроль виплат

<b>Платежі & Крипто:</b>
💳 Карта (Visa/Mastercard)
🔗 Liqpay (для України)
🪙 Крипто платежі (BTC, ETH, TON)

Готові стати частиною найбільшої системи? ✅"""
}

@funnels_router.message(Command("onboarding"))
async def start_onboarding(message: Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Почнемо →", callback_data="onboarding_start")]
    ])
    await message.answer(ONBOARDING_TEXT["step1"], reply_markup=kb, parse_mode="HTML")

@funnels_router.callback_query(F.data == "onboarding_start")
async def onboarding_step1(query: CallbackQuery, state: FSMContext):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Далі →", callback_data="onboarding_step2")],
        [InlineKeyboardButton(text="Пропустити", callback_data="back_to_menu")]
    ])
    await query.message.edit_text(ONBOARDING_TEXT["step2"], reply_markup=kb, parse_mode="HTML")
    await state.set_state(FunnelStates.onboarding_step1)

@funnels_router.callback_query(F.data == "onboarding_step2")
async def onboarding_step2(query: CallbackQuery, state: FSMContext):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Завершити", callback_data="onboarding_complete")],
        [InlineKeyboardButton(text="Назад", callback_data="onboarding_start")]
    ])
    await query.message.edit_text(ONBOARDING_TEXT["step3"], reply_markup=kb, parse_mode="HTML")
    await state.set_state(FunnelStates.onboarding_step2)

@funnels_router.callback_query(F.data == "onboarding_complete")
async def onboarding_complete(query: CallbackQuery, state: FSMContext):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="До меню", callback_data="back_to_menu")]
    ])
    await query.message.edit_text("✅ <b>Поздоровляємо!</b>\n\nВи готові розпочати роботу з SHADOW SYSTEM!\n\nВизначте тариф у /subscription та почніть працювати! 🚀", reply_markup=kb, parse_mode="HTML")
    await state.clear()

# ====== SALES FUNNEL ======
SALES_FUNNEL = {
    "pain": """😤 <b>Проблеми з ботнетом?</b>

❌ Складно управляти багатьма ботами
❌ Ручна розсилка забирає багато часу
❌ Немає статистики та аналітики
❌ Високі витрати на підтримку
❌ Жоден інструмент не робить все одночасно

У нас є рішення! 👇""",

    "solution": """✅ <b>SHADOW SYSTEM - Ваше рішення</b>

🎯 Управління до 1000+ ботів в одній платформі
⚡ Автоматичні розсилки за 30 секунд
📊 Реал-тайм аналітика всіх кампаній
🛡️ Безпечність на рівні enterprise
🚀 24/7 підтримка та оновлення

<b>Результати клієнтів:</b>
✨ 10x швидше розсилки
✨ 3x більше конверсії
✨ 80% менше часу на операції
✨ 100% моніторинг всіх ботів""",

    "offer": """💎 <b>Спеціальна пропозиція</b>

<b>Виберіть свій пакет:</b>

🆓 <b>Free</b> - Тільки спробувати
⭐ <b>Standard</b> - 300 грн/мес - Для новачків
👑 <b>Premium</b> - 600 грн/мес - Для професіоналів
💎 <b>Elite</b> - 1,200 грн/мес - Необмежено

<b>В кожному пакеті:</b>
✅ Технічна підтримка
✅ Регулярні оновлення
✅ Всі нові функції
✅ Гарантія працездатності

<i>Перший місяць - 50% скидка! 🎁</i>""",

    "urgency": """⏰ <b>Обмежена пропозиція!</b>

Це спеціальна цена тільки для перших 100 користувачів.

<b>Після їхнього запуску ціни будуть:</b>
⭐ Standard - 500 грн/мес
👑 Premium - 900 грн/мес
💎 Elite - 1,800 грн/мес

<b>Поспішайте! Бронюйте місце зараз!</b>

✨ Покупці отримають:
• Безстроковий доступ за сегодняшню ціну
• Персональний менеджер
• Пріоритетну підтримку"""
}

@funnels_router.message(Command("sales"))
async def sales_funnel_start(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, у мене є проблема!", callback_data="sales_pain")]
    ])
    await message.answer(SALES_FUNNEL["pain"], reply_markup=kb, parse_mode="HTML")

@funnels_router.callback_query(F.data == "sales_pain")
async def sales_pain_point(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Потрібно рішення!", callback_data="sales_solution")]
    ])
    await query.message.edit_text(SALES_FUNNEL["solution"], reply_markup=kb, parse_mode="HTML")

@funnels_router.callback_query(F.data == "sales_solution")
async def sales_offer(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Розглянути пакети", callback_data="subscription_main")],
        [InlineKeyboardButton(text="Закупити зараз!", callback_data="sales_offer")]
    ])
    await query.message.edit_text(SALES_FUNNEL["offer"], reply_markup=kb, parse_mode="HTML")

@funnels_router.callback_query(F.data == "sales_offer")
async def sales_urgency(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Я готовий!", callback_data="subscription_main")],
        [InlineKeyboardButton(text="Мені потрібно подумати", callback_data="back_to_menu")]
    ])
    await query.message.edit_text(SALES_FUNNEL["urgency"], reply_markup=kb, parse_mode="HTML")

# ====== LEAD MAGNET FUNNEL ======
LEAD_MAGNET_TEXT = {
    "start": """🎁 <b>БЕЗКОШТОВНИЙ ГАЙД</b>

Бажаєте дізнатися, як збільшити конверсію ваших розсилок у 3 рази?

Ми підготували для вас ексклюзивний PDF-гайд:
<b>"ТОП-10 секретів успішного Telegram-маркетингу 2024"</b>

Отримайте його прямо зараз безкоштовно! 👇""",
    "success": """✅ <b>Ваш гайд готовий!</b>

Завантажуйте за посиланням нижче:
🔗 <a href='https://example.com/guide.pdf'>Завантажити Гайд (PDF)</a>

Також ми даруємо вам <b>+10% до першого поповнення</b> балансу! 🎁"""
}

@funnels_router.message(Command("gift"))
async def lead_magnet_start(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отримати гайд! 📥", callback_data="get_lead_magnet")]
    ])
    await message.answer(LEAD_MAGNET_TEXT["start"], reply_markup=kb, parse_mode="HTML")

@funnels_router.callback_query(F.data == "get_lead_magnet")
async def lead_magnet_success(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text(LEAD_MAGNET_TEXT["success"], parse_mode="HTML")

# ====== LEAD MAGNET FUNNEL ======
LEAD_MAGNET_TEXT = {
    "start": """🎁 <b>БЕЗКОШТОВНИЙ ГАЙД</b>

Бажаєте дізнатися, як збільшити конверсію ваших розсилок у 3 рази?

Ми підготували для вас ексклюзивний PDF-гайд:
<b>"ТОП-10 секретів успішного Telegram-маркетингу 2024"</b>

Отримайте його прямо зараз безкоштовно! 👇""",
    "success": """✅ <b>Ваш гайд готовий!</b>

Завантажуйте за посиланням нижче:
🔗 <a href='https://example.com/guide.pdf'>Завантажити Гайд (PDF)</a>

Також ми даруємо вам <b>+10% до першого поповнення</b> балансу! 🎁"""
}

@funnels_router.message(Command("gift"))
async def lead_magnet_start(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отримати гайд! 📥", callback_data="get_lead_magnet")]
    ])
    await message.answer(LEAD_MAGNET_TEXT["start"], reply_markup=kb, parse_mode="HTML")

@funnels_router.callback_query(F.data == "get_lead_magnet")
async def lead_magnet_success(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text(LEAD_MAGNET_TEXT["success"], parse_mode="HTML")
