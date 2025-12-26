from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from core.ai_service import ai_service
from core.audit_logger import audit_logger, ActionCategory

router = Router()

class AnalyticsStates(StatesGroup):
    waiting_text = State()

def analytics_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📈 Звіти", callback_data="reports"),
            InlineKeyboardButton(text="📊 Дашборд", callback_data="dashboard")
        ],
        [
            InlineKeyboardButton(text="😊 AI Sentiment", callback_data="sentiment"),
            InlineKeyboardButton(text="⚠️ Ризики", callback_data="risk_predict")
        ],
        [
            InlineKeyboardButton(text="⏰ Найкращий час", callback_data="best_time"),
            InlineKeyboardButton(text="✍️ AI Тексти", callback_data="generate_text")
        ],
        [InlineKeyboardButton(text="◀️ Повернутись", callback_data="back_to_menu")]
    ])

def analytics_description() -> str:
    ai_status = "🟢 Активний" if ai_service.is_available else "🟡 Базовий режим"
    return f"""<b>📊 ЦЕНТР АНАЛІТИКИ</b>
<i>Розумна аналітика на базі AI</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>🤖 AI Статус:</b> {ai_status}

━━━━━━━━━━━━━━━━━━━━━━━

<b>🛠️ ДОСТУПНІ ІНСТРУМЕНТИ:</b>

<b>📈 Звіти</b>
Детальні звіти по кампаніям із показниками CTR, конверсії та ROI. Експорт у PDF та Excel.

<b>📊 Дашборд</b>
Ключові метрики в реальному часі: активність ботів, статус розсилок, ефективність кампаній.

<b>😊 AI Sentiment</b>
Інтелектуальний аналіз тональності відповідей користувачів для оптимізації комунікації.

<b>⚠️ Прогноз ризиків</b>
AI-прогнозування ймовірності блокування ботів та рекомендації щодо запобігання.

<b>⏰ Найкращий час</b>
Аналіз активності аудиторії та рекомендації оптимального часу для розсилок.

<b>✍️ AI Генерація</b>
Створення унікальних текстів для кампаній за допомогою штучного інтелекту."""

@router.message(Command("analytics"))
async def analytics_cmd(message: Message):
    await audit_logger.log(
        user_id=message.from_user.id,
        action="view_analytics",
        category=ActionCategory.SYSTEM,
        username=message.from_user.username,
        details={"command": "/analytics"}
    )
    await message.answer(analytics_description(), reply_markup=analytics_kb(), parse_mode="HTML")

@router.callback_query(F.data == "analytics_main")
async def analytics_menu(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text(analytics_description(), reply_markup=analytics_kb(), parse_mode="HTML")

@router.callback_query(F.data == "reports")
async def reports(query: CallbackQuery):
    await query.answer()
    
    await audit_logger.log(
        user_id=query.from_user.id,
        action="view_reports",
        category=ActionCategory.CAMPAIGN,
        username=query.from_user.username
    )
    
    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Експорт PDF", callback_data="export_pdf")],
        [InlineKeyboardButton(text="📊 Експорт Excel", callback_data="export_excel")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="analytics_main")]
    ])
    
    report_text = """📈 <b>ЗВІТИ ЗА ПОТОЧНИЙ МІСЯЦЬ</b>

<b>📊 Загальна статистика:</b>
├ Розсилок: 1,234
├ Повідомлень: 45,678
├ Доставлено: 44,123 (96.6%)
└ Помилок: 1,555 (3.4%)

<b>📈 Ефективність:</b>
├ CTR: 45.2%
├ Конверсія: 12.8%
├ ROI: +234%
└ Вартість ліда: 2.4 ₴

<b>🔝 ТОП кампанії:</b>
1. "Маркетинг" - 89% CTR
2. "IT послуги" - 76% CTR
3. "Фріланс" - 68% CTR"""
    
    await query.message.edit_text(report_text, reply_markup=back_kb, parse_mode="HTML")

@router.callback_query(F.data == "sentiment")
async def sentiment(query: CallbackQuery, state: FSMContext):
    await query.answer()
    
    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Аналізувати текст", callback_data="analyze_text")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="analytics_main")]
    ])
    
    text = """😊 <b>AI SENTIMENT ANALYSIS</b>

<b>📊 Загальний аналіз відповідей:</b>
├ 🟢 Позитивні: 67% (2,345)
├ ⚪ Нейтральні: 23% (805)
└ 🔴 Негативні: 10% (350)

<b>📈 Тренди:</b>
├ Цього тижня: +5% позитивних
├ Середній показник: 62%
└ Рекомендація: Продовжувати стратегію

<b>🔑 Ключові теми:</b>
• Ціна (згадано 234 рази)
• Якість (189 разів)
• Підтримка (156 разів)

Натисніть "Аналізувати текст" для аналізу конкретного повідомлення."""
    
    await query.message.edit_text(text, reply_markup=back_kb, parse_mode="HTML")

@router.callback_query(F.data == "analyze_text_start")
async def analyze_text_start(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(AnalyticsStates.waiting_text)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="analytics_main")]
    ])
    
    await query.message.edit_text(
        "📝 <b>АНАЛІЗ ТЕКСТУ</b>\n\nНадішліть текст для аналізу тональності:",
        reply_markup=kb,
        parse_mode="HTML"
    )

@router.message(AnalyticsStates.waiting_text)
async def analyze_text_process(message: Message, state: FSMContext):
    await state.clear()
    
    await audit_logger.log(
        user_id=message.from_user.id,
        action="sentiment_analysis",
        category=ActionCategory.OSINT,
        username=message.from_user.username,
        details={"text_length": len(message.text)}
    )
    
    result = await ai_service.analyze_sentiment(message.text)
    
    sentiment_emoji = {
        "positive": "🟢",
        "negative": "🔴",
        "neutral": "⚪"
    }
    
    emoji = sentiment_emoji.get(result['sentiment'], "⚪")
    ai_status = "🤖 AI" if result.get('ai_powered') else "📊 Базовий"
    
    keywords_text = ", ".join(result.get('keywords', [])) if result.get('keywords') else "Не визначено"
    
    text = f"""😊 <b>РЕЗУЛЬТАТ АНАЛІЗУ</b>

<b>Тональність:</b> {emoji} {result['sentiment'].upper()}
<b>Впевненість:</b> {result['score']}%

<b>Ключові слова:</b>
{keywords_text}

<b>Резюме:</b>
{result.get('summary', 'Аналіз завершено')}

<i>Аналіз: {ai_status}</i>"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Ще аналіз", callback_data="analyze_text_start")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="analytics_main")]
    ])
    
    await message.answer(text, reply_markup=kb, parse_mode="HTML")

@router.callback_query(F.data == "risk_predict")
async def risk_predict(query: CallbackQuery):
    await query.answer()
    
    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="analytics_main")]
    ])
    
    text = """⚠️ <b>ПРОГНОЗ РИЗИКІВ</b>

<b>🔴 Високий ризик (2 кампанії):</b>
├ "Спам-розсилка #123" - 80% ризик блоку
│   └ Рекомендація: Затримка 24 години
└ "Масова #456" - 65% ризик
    └ Рекомендація: Зменшити швидкість

<b>🟡 Середній ризик (5 кампанії):</b>
├ Рекомендовано збільшити інтервал
└ Моніторинг кожні 30 хвилин

<b>🟢 Низький ризик (12 кампаній):</b>
└ Працюють в нормальному режимі

<b>📊 Загальні рекомендації:</b>
• Оптимальний інтервал: 30-60 сек
• Ліміт на годину: 200 повідомлень
• Ротація ботів: кожні 2 години"""
    
    await query.message.edit_text(text, reply_markup=back_kb, parse_mode="HTML")

@router.callback_query(F.data == "dashboard")
async def dashboard(query: CallbackQuery):
    await query.answer()
    
    from core.campaign_manager import campaign_manager
    from core.scheduler import scheduler
    
    campaigns = len(campaign_manager.campaigns)
    tasks = scheduler.get_stats()
    
    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="dashboard")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="analytics_main")]
    ])
    
    text = f"""📊 <b>ДАШБОРД</b>

<b>🤖 Ботнет:</b>
├ Всього ботів: 45
├ 🟢 Активних: 38 (84%)
├ 🟡 Прогрів: 5 (11%)
└ 🔴 Помилки: 2 (5%)

<b>📧 Кампанії:</b>
├ Активних: {campaigns}
├ В черзі: {tasks.get('pending', 0)}
├ Виконано: {tasks.get('completed', 0)}
└ Помилок: {tasks.get('failed', 0)}

<b>📈 Сьогодні:</b>
├ Відправлено: 1,234
├ Доставлено: 1,189 (96.4%)
├ Прочитано: 892 (72.3%)
└ Кліків: 156 (12.6%)"""
    
    await query.message.edit_text(text, reply_markup=back_kb, parse_mode="HTML")

@router.callback_query(F.data == "best_time")
async def best_time(query: CallbackQuery):
    await query.answer()
    
    result = await ai_service.suggest_best_time()
    
    times_text = ""
    for t in result['recommended_times']:
        eng = "🔥" if t['engagement'] == 'high' else "📊"
        times_text += f"{eng} <b>{t['time']}</b> - {t['reason']}\n"
    
    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="analytics_main")]
    ])
    
    text = f"""⏰ <b>НАЙКРАЩИЙ ЧАС ДЛЯ РОЗСИЛОК</b>

<b>🎯 Рекомендовані години:</b>
{times_text}
<b>📅 Найкращі дні:</b>
Вівторок, Середа, Четвер

<b>⛔ Уникати:</b>
• 23:00 - 07:00 (низька активність)
• Понеділок ранок (пік спаму)
• Вихідні (зменшена увага)

<b>🌍 Часова зона:</b> {result['timezone']}"""
    
    await query.message.edit_text(text, reply_markup=back_kb, parse_mode="HTML")

@router.callback_query(F.data == "generate_text")
async def generate_text(query: CallbackQuery):
    await query.answer()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💼 Професійний", callback_data="gen_professional")],
        [InlineKeyboardButton(text="👋 Дружній", callback_data="gen_friendly")],
        [InlineKeyboardButton(text="⏰ Терміновий", callback_data="gen_urgent")],
        [InlineKeyboardButton(text="📚 Інформативний", callback_data="gen_informative")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="analytics_main")]
    ])
    
    text = """✍️ <b>ГЕНЕРАЦІЯ ТЕКСТУ</b>

Виберіть стиль тексту для генерації:

<b>💼 Професійний</b> - Діловий стиль
<b>👋 Дружній</b> - Неформальний тон
<b>⏰ Терміновий</b> - Заклик до дії
<b>📚 Інформативний</b> - Детальний опис"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@router.callback_query(F.data.startswith("gen_"))
async def generate_text_result(query: CallbackQuery):
    await query.answer("⏳ Генерація...")
    
    style = query.data.replace("gen_", "")
    
    sample_topics = {
        "professional": "IT послуги для бізнесу",
        "friendly": "Знижки на курси",
        "urgent": "Остання можливість",
        "informative": "Нова функція продукту"
    }
    
    topic = sample_topics.get(style, "Маркетингова пропозиція")
    generated = await ai_service.generate_campaign_text(topic, style)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Ще варіант", callback_data=f"gen_{style}")],
        [InlineKeyboardButton(text="📋 Копіювати", callback_data="copy_text")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="generate_text")]
    ])
    
    text = f"""✍️ <b>ЗГЕНЕРОВАНИЙ ТЕКСТ</b>

<b>Стиль:</b> {style.title()}
<b>Тема:</b> {topic}

<b>Результат:</b>
<code>{generated}</code>

<i>Натисніть на текст для копіювання</i>"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
