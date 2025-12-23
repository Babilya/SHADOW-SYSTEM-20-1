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

@user_router.callback_query(F.data == "back_to_menu")
async def back_to_menu(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("📱 <b>Головне меню</b>\n\nВиберіть опцію:", reply_markup=main_menu(), parse_mode="HTML")

@user_router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer("📱 <b>Головне меню</b>\n\nВиберіть опцію:", reply_markup=main_menu(), parse_mode="HTML")

@user_router.message(Command("subscription"))
async def cmd_subscription(message: Message):
    await message.answer("🎯 <b>Підписка</b>\n\nТип: Premium\nДнів: 30", reply_markup=subscription_menu(), parse_mode="HTML")

@user_router.message(Command("mailing"))
async def cmd_mailing(message: Message, state: FSMContext):
    await message.answer("📧 Напишіть текст розсилки:", parse_mode="HTML")
    await state.set_state(UserStates.waiting_for_mailing_text)

@user_router.message(UserStates.waiting_for_mailing_text)
async def process_mailing_text(message: Message, state: FSMContext):
    await state.update_data(mailing_text=message.text)
    await message.answer("📋 Вкажіть ID користувачів:")
    await state.set_state(UserStates.waiting_for_target_users)

@user_router.message(UserStates.waiting_for_target_users)
async def process_target_users(message: Message, state: FSMContext):
    await message.answer("✅ Розсилка створена!")
    await state.clear()

@user_router.message(Command("autoreply"))
async def cmd_autoreply(message: Message, state: FSMContext):
    await message.answer("🤖 Напишіть тригер:")
    await state.set_state(UserStates.waiting_for_auto_reply_trigger)

@user_router.message(UserStates.waiting_for_auto_reply_trigger)
async def process_autoreply_trigger(message: Message, state: FSMContext):
    await state.update_data(trigger=message.text)
    await message.answer("Напишіть відповідь:")
    await state.set_state(UserStates.waiting_for_auto_reply_text)

@user_router.message(UserStates.waiting_for_auto_reply_text)
async def process_autoreply_text(message: Message, state: FSMContext):
    await message.answer("✅ Автовідповідь налаштована!")
    await state.clear()

@user_router.message(Command("stats"))
async def cmd_stats(message: Message):
    await message.answer("📊 <b>Статистика</b>\n\nРозсилок: 245\nПаршено: 12,450\nOSINT: 89", parse_mode="HTML")

@user_router.message(Command("settings"))
async def cmd_settings(message: Message):
    await message.answer("⚙️ <b>Налаштування</b>", reply_markup=settings_menu(), parse_mode="HTML")

@user_router.message(Command("balance"))
async def cmd_balance(message: Message):
    await message.answer("💰 <b>Баланс: ₴5,240</b>", parse_mode="HTML")

# Обробники кнопок з головного меню
@user_router.callback_query(F.data == "mailing")
async def button_mailing(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.edit_text("📧 Напишіть текст розсилки:")
    await state.set_state(UserStates.waiting_for_mailing_text)

@user_router.callback_query(F.data == "stats")
async def button_stats(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("📊 <b>Ваша статистика</b>\n\nРозсилок: 245\nПаршено: 12,450\nOSINT: 89\nБаланс: ₴5,240", parse_mode="HTML")

@user_router.callback_query(F.data == "autoreply")
async def button_autoreply(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.edit_text("🤖 Напишіть текст для тригера:")
    await state.set_state(UserStates.waiting_for_auto_reply_trigger)

@user_router.callback_query(F.data == "balance")
async def button_balance(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("💰 <b>Баланс: ₴5,240</b>\n\nСпособи поповнення: 💳 Карта, 🔗 Liqpay, 🪙 Крипто", parse_mode="HTML")

@user_router.callback_query(F.data == "settings")
async def button_settings(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("⚙️ <b>Налаштування</b>", reply_markup=settings_menu(), parse_mode="HTML")

# Обробники підменю
@user_router.callback_query(F.data == "ghost_mode")
async def toggle_ghost_mode(query: CallbackQuery):
    await query.answer("✅ Привидний режим: ВКЛ")
    await query.message.edit_text("👻 <b>Привидний режим: ВКЛ</b>", parse_mode="HTML")

@user_router.callback_query(F.data == "notifications")
async def toggle_notifications(query: CallbackQuery):
    await query.answer("✅ Сповіщення: ВИМК")
    await query.message.edit_text("🔔 <b>Сповіщення: ВИМК</b>", parse_mode="HTML")

@user_router.callback_query(F.data == "language")
async def change_language(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("🌐 Мова: <b>Українська</b>", parse_mode="HTML")

@user_router.callback_query(F.data == "security")
async def security_settings(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("🔐 <b>Безпека</b>\n\n2FA: ВКЛ\nШифрування: ВКЛ", parse_mode="HTML")

@user_router.callback_query(F.data == "upgrade_premium")
async def upgrade_premium(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("⭐ <b>Premium - 300 грн/місяць</b>\n\nРозсилок: 1000\nПарсинг: 10000", parse_mode="HTML")

@user_router.callback_query(F.data == "upgrade_elite")
async def upgrade_elite(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("👑 <b>Elite - 600 грн/місяць</b>\n\nРозсилок: 10000\nПарсинг: 100000", parse_mode="HTML")

@user_router.callback_query(F.data == "limits")
async def show_limits(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("📋 <b>Ваші ліміти</b>\n\nРозсилок: 500/1000\nПарсинг: 5000/10000\nOSINT: 100/500", parse_mode="HTML")

@user_router.callback_query(F.data == "back")
async def go_back(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("📱 <b>Головне меню</b>\n\nВиберіть опцію:", reply_markup=main_menu(), parse_mode="HTML")

