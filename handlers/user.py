from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.user import main_menu, subscription_menu, settings_menu
import json
from datetime import datetime

user_router = Router()

class UserStates(StatesGroup):
    waiting_for_mailing_text = State()
    waiting_for_target_users = State()
    waiting_for_auto_reply_trigger = State()
    waiting_for_auto_reply_text = State()

@user_router.message(Command("menu"))
async def cmd_menu(message: Message):
    """Показати головне меню"""
    await message.answer(
        "📱 <b>Головне меню Shadow Security</b>\n\n"
        "Виберіть потрібну опцію:",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

@user_router.message(Command("subscription"))
async def cmd_subscription(message: Message):
    """Показати інформацію про підписку"""
    await message.answer(
        "🎯 <b>Ваша підписка</b>\n\n"
        "Тип: <b>Premium</b>\n"
        "Залишилось днів: <b>30</b>\n"
        "Ліміти:\n"
        "  • Розсилок: 500/1000\n"
        "  • Парсинг: 5000/10000\n"
        "  • OSINT: 100/500",
        reply_markup=subscription_menu(),
        parse_mode="HTML"
    )

@user_router.message(Command("mailing"))
async def cmd_mailing(message: Message, state: FSMContext):
    """Почати створення розсилки"""
    await message.answer("📧 <b>Створення розсилки</b>\n\nНапишіть текст розсилки:", parse_mode="HTML")
    await state.set_state(UserStates.waiting_for_mailing_text)

@user_router.message(UserStates.waiting_for_mailing_text)
async def process_mailing_text(message: Message, state: FSMContext):
    """Обробити текст розсилки"""
    await state.update_data(mailing_text=message.text)
    await message.answer("📋 Тепер вкажіть цільову аудиторію (ID користувачів через кому):")
    await state.set_state(UserStates.waiting_for_target_users)

@user_router.message(UserStates.waiting_for_target_users)
async def process_target_users(message: Message, state: FSMContext):
    """Обробити цільову аудиторію"""
    data = await state.get_data()
    await message.answer(
        f"✅ Розсилка створена!\n\n"
        f"Текст: {data['mailing_text']}\n"
        f"Цільова аудиторія: {message.text}\n\n"
        f"Розсилка буде відправлена протягом 5 хвилин"
    )
    await state.clear()

@user_router.message(Command("autoreply"))
async def cmd_autoreply(message: Message, state: FSMContext):
    """Налаштувати автовідповідь"""
    await message.answer(
        "🤖 <b>Налаштування автовідповіді</b>\n\n"
        "Напишіть текст, на який потрібно відповідати:",
        parse_mode="HTML"
    )
    await state.set_state(UserStates.waiting_for_auto_reply_trigger)

@user_router.message(UserStates.waiting_for_auto_reply_trigger)
async def process_autoreply_trigger(message: Message, state: FSMContext):
    """Обробити тригер"""
    await state.update_data(trigger=message.text)
    await message.answer("Напишіть текст автовідповіді:")
    await state.set_state(UserStates.waiting_for_auto_reply_text)

@user_router.message(UserStates.waiting_for_auto_reply_text)
async def process_autoreply_text(message: Message, state: FSMContext):
    """Обробити текст автовідповіді"""
    data = await state.get_data()
    await message.answer(
        f"✅ Автовідповідь налаштована!\n\n"
        f"Тригер: {data['trigger']}\n"
        f"Відповідь: {message.text}"
    )
    await state.clear()

@user_router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Показати статистику"""
    await message.answer(
        "📊 <b>Ваша статистика</b>\n\n"
        "Розсилок відправлено: <b>245</b>\n"
        "Користувачів спарсено: <b>12,450</b>\n"
        "OSINT запитів: <b>89</b>\n"
        "Баланс: <b>₴5,240</b>\n\n"
        "Статистика оновлюється кожну годину",
        parse_mode="HTML"
    )

@user_router.message(Command("settings"))
async def cmd_settings(message: Message):
    """Показати налаштування"""
    await message.answer(
        "⚙️ <b>Налаштування</b>\n\n"
        "Виберіть що змінити:",
        reply_markup=settings_menu(),
        parse_mode="HTML"
    )

@user_router.callback_query(F.data == "ghost_mode")
async def toggle_ghost_mode(query: CallbackQuery):
    """Включити/вимкнути привидний режим"""
    await query.answer("✅ Привидний режим увімкнений", show_alert=False)
    await query.message.edit_text("👻 Привидний режим: <b>ВКЛ</b>", parse_mode="HTML")

@user_router.callback_query(F.data == "notifications")
async def toggle_notifications(query: CallbackQuery):
    """Включити/вимкнути сповіщення"""
    await query.answer("✅ Сповіщення вимкнені", show_alert=False)
    await query.message.edit_text("🔔 Сповіщення: <b>ВИМК</b>", parse_mode="HTML")

@user_router.message(Command("balance"))
async def cmd_balance(message: Message):
    """Показати баланс"""
    await message.answer(
        "💰 <b>Ваш баланс</b>\n\n"
        "Поточний баланс: <b>₴5,240</b>\n"
        "Витрачено цього місяця: <b>₴1,760</b>\n\n"
        "Способи поповнення:\n"
        "💳 Карта\n"
        "📱 Liqpay\n"
        "🪙 Крипто",
        parse_mode="HTML"
    )
