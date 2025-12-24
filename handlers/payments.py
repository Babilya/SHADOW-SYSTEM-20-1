from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

payments_router = Router()

def balance_payments_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💵 Баланс", callback_data="balance_view"),
         InlineKeyboardButton(text="📜 Історія", callback_data="payments_history")],
        [InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="stars_payment"),
         InlineKeyboardButton(text="💳 Карта", callback_data="card_payment")],
        [InlineKeyboardButton(text="🔗 Liqpay", callback_data="liqpay_payment"),
         InlineKeyboardButton(text="📄 Рахунок", callback_data="create_invoice")],
        [InlineKeyboardButton(text="♻️ Повернення", callback_data="refund_request")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])

@payments_router.message(Command("pay"))
async def cmd_pay(message: Message):
    await message.answer("⭐ <b>БАЛАНС & ПЛАТЕЖІ</b>\n\nВаш баланс: <b>5,240 ⭐</b>\n\nВиберіть опцію:", reply_markup=balance_payments_kb(), parse_mode="HTML")

@payments_router.callback_query(F.data == "balance_payments_main")
async def balance_payments_main(query: CallbackQuery):
    await query.answer()
    await query.message.answer("⭐ <b>БАЛАНС & ПЛАТЕЖІ</b>\n\nВаш баланс: <b>5,240 ⭐</b>\n\nВиберіть опцію:", reply_markup=balance_payments_kb(), parse_mode="HTML")

@payments_router.callback_query(F.data == "balance_view")
async def balance_view(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="➕ Поповнити", callback_data="add_funds")], [InlineKeyboardButton(text="◀️ Назад", callback_data="balance_payments_main")]])
    await query.message.answer("💵 <b>МІЙ БАЛАНС</b>\n\n💰 Баланс: <b>5,240 ⭐</b>\n🔒 Заморожено: 0 ⭐\n🎁 Бонус: 240 ⭐\n📊 До видачі: 5,000 ⭐", reply_markup=kb, parse_mode="HTML")

@payments_router.callback_query(F.data == "add_funds")
async def add_funds(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="stars_payment")], [InlineKeyboardButton(text="◀️ Назад", callback_data="balance_view")]])
    await query.message.answer("➕ <b>ДОДАТИ КОШТИ</b>\n\nВиберіть спосіб поповнення баланс:", reply_markup=kb, parse_mode="HTML")

@payments_router.callback_query(F.data == "payments_history")
async def payments_history(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📥 Поповнення", callback_data="history_topup")], [InlineKeyboardButton(text="📤 Видачі", callback_data="history_withdraw")], [InlineKeyboardButton(text="◀️ Назад", callback_data="balance_payments_main")]])
    await query.message.answer("📜 <b>ІСТОРІЯ ПЛАТЕЖІВ</b>\n\n1. 2025-12-24 | +300 ⭐ | Telegram Stars | ✅\n2. 2025-12-20 | +500 ⭐ | Карта | ✅\n3. 2025-12-18 | +1,000 ⭐ | Liqpay | ✅", reply_markup=kb, parse_mode="HTML")

@payments_router.callback_query(F.data == "history_topup")
async def history_topup(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="payments_history")]])
    await query.message.answer("📥 <b>ІСТОРІЯ ПОПОВНЕНЬ</b>\n\n1. 2025-12-24 | +300 ⭐ | Telegram Stars | ✅\n2. 2025-12-20 | +500 ⭐ | Карта | ✅\n3. 2025-12-18 | +1,000 ⭐ | Liqpay | ✅\n\nВсього поповлено: 4,800 ⭐", reply_markup=kb, parse_mode="HTML")

@payments_router.callback_query(F.data == "history_withdraw")
async def history_withdraw(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="payments_history")]])
    await query.message.answer("📤 <b>ІСТОРІЯ ВИДАЧ</b>\n\n1. 2025-12-15 | -1,500 ⭐ | Карта | ✅\n2. 2025-12-10 | -500 ⭐ | Комісія | ✅\n\nВсього видано: 2,100 ⭐", reply_markup=kb, parse_mode="HTML")

@payments_router.callback_query(F.data == "stars_payment")
async def stars_payment(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⭐ 100 Stars", callback_data="buy_100_stars")], [InlineKeyboardButton(text="⭐ 500 Stars", callback_data="buy_500_stars")], [InlineKeyboardButton(text="⭐ 1000 Stars", callback_data="buy_1000_stars")], [InlineKeyboardButton(text="💳 Інша сума", callback_data="custom_stars")], [InlineKeyboardButton(text="◀️ Назад", callback_data="balance_payments_main")]])
    await query.message.answer("⭐ <b>ОПЛАТА TELEGRAM STARS</b>\n\n✓ Комісія: 0%\n✓ Миттєво\n✓ Без верифікації", reply_markup=kb, parse_mode="HTML")

@payments_router.callback_query(F.data.startswith("buy_") & F.data.endswith("_stars"))
async def buy_stars(query: CallbackQuery):
    await query.answer()
    amount = query.data.replace("buy_", "").replace("_stars", "")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Купити", callback_data=f"confirm_stars_{amount}")], [InlineKeyboardButton(text="◀️ Назад", callback_data="stars_payment")]])
    await query.message.answer(f"⭐ <b>КУПІВЛЯ {amount} STARS</b>\n\nКількість: {amount} ⭐\nКомісія: 0%\nСтатус: Готово до оплати", reply_markup=kb, parse_mode="HTML")

@payments_router.callback_query(F.data.startswith("confirm_stars_"))
async def confirm_stars(query: CallbackQuery):
    await query.answer("✅ Оплата оброблена!")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="balance_payments_main")]])
    await query.message.answer("✅ <b>ПЛАТІЖ УСПІШНИЙ</b>\n\nКошти додано до баланс\nНовий баланс: 5,340 ⭐", reply_markup=kb, parse_mode="HTML")

@payments_router.callback_query(F.data == "custom_stars")
async def custom_stars(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="stars_payment")]])
    await query.message.answer("⭐ <b>КАСТОМНА СУМА</b>\n\nНапишіть кількість stars яку хочете купити (мінімум 10 ⭐)", reply_markup=kb, parse_mode="HTML")

@payments_router.callback_query(F.data == "card_payment")
async def card_payment(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💳 Оплатити", callback_data="process_card")], [InlineKeyboardButton(text="◀️ Назад", callback_data="balance_payments_main")]])
    await query.message.answer("💳 <b>ОПЛАТА КАРТКОЮ</b>\n\nМінімум: 100 ⭐ (~2 USD)\nМаксимум: 100,000 ⭐ (~2,000 USD)\nКомісія: 1.5%", reply_markup=kb, parse_mode="HTML")

@payments_router.callback_query(F.data == "process_card")
async def process_card(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="card_payment")]])
    await query.message.answer("💳 <b>ВВЕДЕННЯ ДЕТАЛЕЙ КАРТИ</b>\n\nНапишіть суму в ⭐ (наприклад: 500)", reply_markup=kb, parse_mode="HTML")

@payments_router.callback_query(F.data == "liqpay_payment")
async def liqpay_payment(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔗 Перейти", url="https://liqpay.com")], [InlineKeyboardButton(text="◀️ Назад", callback_data="balance_payments_main")]])
    await query.message.answer("🔗 <b>ОПЛАТА LIQPAY</b>\n\nКомісія: 2.5%\nЧас: 15-30 хвилин\nДоступно всім методам Liqpay", reply_markup=kb, parse_mode="HTML")

@payments_router.callback_query(F.data == "create_invoice")
async def create_invoice(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💰 1000 ⭐", callback_data="inv_1000")], [InlineKeyboardButton(text="💰 5000 ⭐", callback_data="inv_5000")], [InlineKeyboardButton(text="💰 Кастом", callback_data="inv_custom")], [InlineKeyboardButton(text="◀️ Назад", callback_data="balance_payments_main")]])
    await query.message.answer("📄 <b>СТВОРЕННЯ РАХУНКУ</b>\n\nРахунок це счёт за послуги. Строк: 48 годин", reply_markup=kb, parse_mode="HTML")

@payments_router.callback_query(F.data.startswith("inv_"))
async def invoice_created(query: CallbackQuery):
    await query.answer()
    amount = query.data.replace("inv_", "")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📋 Копія", callback_data=f"copy_inv_{amount}")], [InlineKeyboardButton(text="📤 Поділитися", callback_data=f"share_inv_{amount}")], [InlineKeyboardButton(text="◀️ Назад", callback_data="create_invoice")]])
    await query.message.answer(f"📄 <b>РАХУНОК {amount} ⭐</b>\n\nID: INV-#12345\nСтатус: Очікування\nАктивний: 48 годин", reply_markup=kb, parse_mode="HTML")

@payments_router.callback_query(F.data.startswith("copy_inv_") | F.data.startswith("share_inv_"))
async def invoice_action(query: CallbackQuery):
    await query.answer("✅ Готово!")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="create_invoice")]])
    await query.message.answer("✅ <b>ДІЯ ВИКОНАНА</b>\n\nРахунок скопійовано у буфер обміну", reply_markup=kb, parse_mode="HTML")

@payments_router.callback_query(F.data == "refund_request")
async def refund_request(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📝 Запросити", callback_data="submit_refund")], [InlineKeyboardButton(text="📜 Історія", callback_data="refund_history")], [InlineKeyboardButton(text="◀️ Назад", callback_data="balance_payments_main")]])
    await query.message.answer("♻️ <b>ПОВЕРНЕННЯ КОШТІВ</b>\n\nПеріод: 14 днів\nМаксимум: 5 за місяц\nКомісія: 1%", reply_markup=kb, parse_mode="HTML")

@payments_router.callback_query(F.data == "submit_refund")
async def submit_refund(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="refund_request")]])
    await query.message.answer("📝 <b>ЗАПИТ ПОВЕРНЕННЯ</b>\n\nМаксимум можна повернути: 300 ⭐\n\nНапишіть суму та причину", reply_markup=kb, parse_mode="HTML")

@payments_router.callback_query(F.data == "refund_history")
async def refund_history(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="refund_request")]])
    await query.message.answer("📜 <b>ІСТОРІЯ ПОВЕРНЕНЬ</b>\n\n1. 2025-12-20 | -500 ⭐ | Поверено | ✅\n2. 2025-12-01 | -100 ⭐ | На розгляді | ⏳", reply_markup=kb, parse_mode="HTML")

@payments_router.callback_query(F.data == "back_to_menu")
async def back_to_menu(query: CallbackQuery):
    await query.answer()
    from keyboards.user import main_menu, main_menu_description
    await query.message.answer(main_menu_description(), reply_markup=main_menu(), parse_mode="HTML")
