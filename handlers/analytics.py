from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

analytics_router = Router()

def analytics_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 Звіти", callback_data="reports")],
        [InlineKeyboardButton(text="😊 AI Sentiment", callback_data="sentiment")],
        [InlineKeyboardButton(text="⚠️ Прогноз ризиків", callback_data="risk_predict")],
        [InlineKeyboardButton(text="📊 Дашборд", callback_data="dashboard")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")],
    ])

def analytics_description() -> str:
    return """<b>📊 АНАЛІТИКА & МЕТРИКИ</b>

<b>📈 Звіти</b>
Детальні звіти по всім кампаніям: CTR, конверсія, ROI, витрати, дохідність. Експорт в PDF/Excel, порівняння періодів.

<b>😊 AI Sentiment</b>
Аналіз тональності повідомлень за допомогою штучного інтелекту. Визначення позитивних, негативних та нейтральних повідомлень.

<b>⚠️ Прогноз ризиків</b>
AI прогнозування ризику блокування розсилки. Рекомендації щодо затримок та интервалів для максимальної успішності.

<b>📊 Дашборд</b>
Головний екран з ключовими метриками: активні проекти, боти в роботі, помилки, дохід, статус розсилок в реальному часі."""

@analytics_router.message(Command("analytics"))
async def analytics_cmd(message: Message):
    await message.answer("📊 <b>Аналітика</b>\n\nВиберіть опцію:", reply_markup=analytics_kb(), parse_mode="HTML")

@analytics_router.callback_query(F.data == "analytics_main")
async def analytics_menu(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("📊 <b>Аналітика</b>\n\nВиберіть опцію:", reply_markup=analytics_kb(), parse_mode="HTML")

@analytics_router.callback_query(F.data == "reports")
async def reports(query: CallbackQuery):
    await query.answer()
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="analytics_main")]])
    await query.message.edit_text("📈 <b>Звіти</b>\n\nЗагальні метрики за період:\n• Розсилок: 1,234\n• CTR: 45%\n• Конверсія: 12%", reply_markup=back_kb, parse_mode="HTML")

@analytics_router.callback_query(F.data == "sentiment")
async def sentiment(query: CallbackQuery):
    await query.answer()
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="analytics_main")]])
    await query.message.edit_text("😊 <b>AI Sentiment Analysis</b>\n\nПозитивні: 67%\nНейтральні: 23%\nНегативні: 10%", reply_markup=back_kb, parse_mode="HTML")

@analytics_router.callback_query(F.data == "risk_predict")
async def risk_predict(query: CallbackQuery):
    await query.answer()
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="analytics_main")]])
    await query.message.edit_text("⚠️ <b>Прогноз ризиків</b>\n\nРискова кампанія: Чат #123 (80% ризик блоку)\nРекомендація: Затримка 24 години", reply_markup=back_kb, parse_mode="HTML")

@analytics_router.callback_query(F.data == "dashboard")
async def dashboard(query: CallbackQuery):
    await query.answer()
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="analytics_main")]])
    await query.message.edit_text("📊 <b>Дашборд</b>\n\nАктивних проектів: 5\nБотів в роботі: 38\nРозсилок в черзі: 12\nТекучі помилки: 0", reply_markup=back_kb, parse_mode="HTML")

@analytics_router.callback_query(F.data == "back_to_menu")
async def analytics_back_to_menu(query: CallbackQuery):
    await query.answer()
    from keyboards.user import main_menu, main_menu_description
    await query.message.edit_text(main_menu_description(), reply_markup=main_menu(), parse_mode="HTML")
