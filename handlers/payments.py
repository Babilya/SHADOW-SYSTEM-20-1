from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from keyboards.user import payment_methods
import json

payments_router = Router()

PAYMENT_METHODS = {
    "liqpay": {"name": "Liqpay", "commission": 2.5},
    "card": {"name": "Банківська карта", "commission": 1.5},
    "crypto": {"name": "Крипто", "commission": 0}
}

@payments_router.message(Command("pay"))
async def cmd_pay(message: Message):
    """Поповнення рахунку"""
    await message.answer(
        "💳 <b>Поповнення рахунку</b>\n\n"
        "Виберіть спосіб оплати:",
        reply_markup=payment_methods(),
        parse_mode="HTML"
    )

@payments_router.callback_query(F.data == "liqpay_payment")
async def liqpay_payment(query: CallbackQuery):
    """Оплата через Liqpay"""
    await query.answer()
    await query.message.edit_text(
        "🔗 <b>Оплата через Liqpay</b>\n\n"
        "<a href='https://liqpay.com'>Перейти до оплати</a>\n\n"
        "Комісія: 2.5%",
        parse_mode="HTML"
    )

@payments_router.callback_query(F.data == "card_payment")
async def card_payment(query: CallbackQuery):
    """Оплата карткою"""
    await query.answer()
    await query.message.edit_text(
        "💳 <b>Оплата карткою</b>\n\n"
        "Введіть суму (UAH):\n\n"
        "Мінімум: 100\n"
        "Максимум: 100,000\n\n"
        "Комісія: 1.5%",
        parse_mode="HTML"
    )

@payments_router.callback_query(F.data == "crypto_payment")
async def crypto_payment(query: CallbackQuery):
    """Оплата крипто"""
    await query.answer()
    await query.message.edit_text(
        "🪙 <b>Оплата крипто</b>\n\n"
        "<b>Bitcoin:</b> 1A1z7agoat5LjSrGFJcn3EYjoz2zWfkwL\n\n"
        "<b>Ethereum:</b> 0x71C7656EC7ab88b098defB751B7401B5f6d8976F\n\n"
        "Комісія: 0%",
        parse_mode="HTML"
    )

@payments_router.message(Command("history"))
async def payment_history(message: Message):
    """Історія платежів"""
    await message.answer(
        "📜 <b>Історія платежів</b>\n\n"
        "1. 2025-12-20 | +₴1,000 | Liqpay | ✅\n"
        "2. 2025-12-18 | +₴500 | Карта | ✅\n"
        "3. 2025-12-15 | +₴2,000 | Liqpay | ✅\n"
        "4. 2025-12-10 | +₴1,500 | Крипто | ✅\n\n"
        "Всього поповлено: <b>₴5,000</b>",
        parse_mode="HTML"
    )

@payments_router.message(Command("invoice"))
async def create_invoice(message: Message):
    """Створити рахунок"""
    await message.answer(
        "📄 <b>創Рахунок</b>\n\n"
        "Сума: <b>₴1,000</b>\n"
        "ID: <b>INV-12345</b>\n"
        "Статус: Очікування оплати\n\n"
        "Рахунок буде активний 48 годин"
    )

@payments_router.message(Command("refund"))
async def refund_request(message: Message):
    """Запит повернення коштів"""
    await message.answer(
        "♻️ <b>Запит повернення</b>\n\n"
        "Максимальний період для повернення: 14 днів\n"
        "Ваш останній платіж: 2025-12-20 (в межах періоду)\n\n"
        "Поточний баланс: ₴5,240\n\n"
        "Напишіть причину повернення:"
    )

@payments_router.message(Command("subscription"))
async def subscription_options(message: Message):
    """Варіанти підписок"""
    await message.answer(
        "📦 <b>Пакети підписок</b>\n\n"
        "<b>🆓 Free</b> - ₴0/мес\n"
        "  • Розсилок: 10\n"
        "  • Парсинг: 100\n"
        "  • OSINT: 0\n\n"
        "<b>⭐ Premium</b> - ₴299/мес\n"
        "  • Розсилок: 1,000\n"
        "  • Парсинг: 10,000\n"
        "  • OSINT: 500\n\n"
        "<b>👑 Elite</b> - ₴999/мес\n"
        "  • Розсилок: 10,000\n"
        "  • Парсинг: 100,000\n"
        "  • OSINT: 5,000\n"
        "  • Приватна підтримка",
        parse_mode="HTML"
    )
