from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.user import main_menu, subscription_menu, settings_menu, main_menu_description, license_menu
import json
from datetime import datetime

user_router = Router()

class UserStates(StatesGroup):
    waiting_for_mailing_text = State()
    waiting_for_target_users = State()
    waiting_for_auto_reply_trigger = State()
    waiting_for_auto_reply_text = State()

@user_router.callback_query(F.data == "texting_main")
async def texting_main_callback(query: CallbackQuery):
    await query.answer()
    from handlers.texting import texting_menu
    await texting_menu(query.message)

@user_router.callback_query(F.data == "help_main")
async def help_main_callback(query: CallbackQuery):
    await query.answer()
    from handlers.help import help_menu
    await help_menu(query.message)

@user_router.callback_query(F.data == "profile_main")
async def profile_main_callback(query: CallbackQuery):
    await query.answer()
    from services.user_service import user_service
    from config import ADMIN_IDS
    from database.models import UserRole
    from core.roles import ROLE_NAMES
    from utils.db import SessionLocal
    from database.models import Bot, Campaign
    
    user_id = query.from_user.id
    user = user_service.get_user(user_id)
    
    if user_id in ADMIN_IDS:
        role = UserRole.ADMIN
    else:
        role = user.role if user else UserRole.GUEST
    
    role_name = ROLE_NAMES.get(role, "Гість")
    username = user.username if user else query.from_user.username or "N/A"
    first_name = query.from_user.first_name or "N/A"
    
    db = SessionLocal()
    try:
        bots_count = db.query(Bot).count()
        campaigns_count = db.query(Campaign).count()
    finally:
        db.close()
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])
    
    text = f"""<b>👤 ПРОФІЛЬ КОРИСТУВАЧА</b>
<i>Особиста інформація</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>📋 ОСНОВНІ ДАНІ:</b>
├ 🆔 ID: <code>{user_id}</code>
├ 👤 Ім'я: {first_name}
├ 📱 Username: @{username}
└ 👑 Роль: {role_name}

<b>📊 СТАТИСТИКА СИСТЕМИ:</b>
├ 🤖 Ботів у системі: {bots_count}
└ 📧 Кампаній: {campaigns_count}"""
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@user_router.callback_query(F.data == "license_main")
async def license_main_callback(query: CallbackQuery):
    await query.answer()
    text = """<b>🔑 ЛІЦЕНЗІЯ SHADOW</b>
<i>Статус вашої активації</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 ПОТОЧНИЙ СТАТУС:</b>
├ 🟢 Ліцензія: Активна
├ 💎 Тариф: ПРЕМІУМ
├ 📅 Дійсна до: 26.01.2026
└ 🔑 Ключ: SHADOW-XXXX-XXXX

━━━━━━━━━━━━━━━━━━━━━━━

<b>⚙️ Доступні дії:</b>"""
    await query.message.edit_text(text, reply_markup=license_menu(), parse_mode="HTML")

@user_router.callback_query(F.data == "back_to_menu")
async def back_to_menu(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.clear()
    from keyboards.role_menus import get_menu_by_role, get_description_by_role
    from services.user_service import user_service
    from config import ADMIN_IDS
    from database.models import UserRole
    
    user_id = query.from_user.id
    if user_id in ADMIN_IDS:
        role = UserRole.ADMIN
    else:
        role = user_service.get_user_role(user_id)
    
    description = get_description_by_role(role)
    keyboard = get_menu_by_role(role)
    
    await query.message.edit_text(description, reply_markup=keyboard, parse_mode="HTML")


@user_router.callback_query(F.data == "ghost_mode")
async def ghost_mode(query: CallbackQuery):
    await query.answer("✅ Привидний режим включено")
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="settings_main")]])
    await query.message.edit_text("👻 <b>Привидний режим: ВКЛ</b>\n\nВаш профіль прихований від інших користувачів.", reply_markup=kb, parse_mode="HTML")

@user_router.callback_query(F.data == "notifications")
async def notifications(query: CallbackQuery):
    await query.answer("✅ Сповіщення вимкнено")
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="settings_main")]])
    await query.message.edit_text("🔔 <b>Сповіщення: ВИМК</b>\n\nВи не будете отримувати сповіщення про нові розсилки.", reply_markup=kb, parse_mode="HTML")

@user_router.callback_query(F.data == "language")
async def language(query: CallbackQuery):
    await query.answer()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_uk"), InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="settings_main")]
    ])
    await query.message.edit_text("🌐 <b>Мова</b>\n\nВиберіть мову інтерфейсу:", reply_markup=kb, parse_mode="HTML")

@user_router.callback_query(F.data == "security")
async def security(query: CallbackQuery):
    await query.answer()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="settings_main")]])
    await query.message.edit_text("🔐 <b>Безпека</b>\n\n2FA: ✅ ВКЛ\nШифрування: ✅ ВКЛ\nСеанси: 1 активний\nПослідній вхід: 1 хв тому", reply_markup=kb, parse_mode="HTML")

@user_router.callback_query(F.data == "tier_free")
async def tier_free(query: CallbackQuery):
    await query.answer()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="subscription_main")]])
    await query.message.edit_text("🆓 <b>Free - Безкоштовно</b>\n\nБоти: 5\nРозсилок: 10\nПарсинг: 100\nOSINT: 0\n\nІдеально для новачків!", reply_markup=kb, parse_mode="HTML")

@user_router.callback_query(F.data == "tier_standard")
async def tier_standard(query: CallbackQuery):
    await query.answer()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Купити", callback_data="buy_standard"), InlineKeyboardButton(text="◀️ Назад", callback_data="subscription_main")]])
    await query.message.edit_text("⭐ <b>Standard - 300 грн/мес</b>\n\nБоти: 50\nРозсилок: 500\nПарсинг: 5,000\nOSINT: 50", reply_markup=kb, parse_mode="HTML")

@user_router.callback_query(F.data == "tier_premium")
async def tier_premium(query: CallbackQuery):
    await query.answer()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Купити", callback_data="buy_premium"), InlineKeyboardButton(text="◀️ Назад", callback_data="subscription_main")]])
    await query.message.edit_text("👑 <b>Premium - 600 грн/мес</b>\n\nБоти: 100\nРозсилок: 5,000\nПарсинг: 50,000\nOSINT: 500\nAI Sentiment: ✅", reply_markup=kb, parse_mode="HTML")

@user_router.callback_query(F.data == "tier_elite")
async def tier_elite(query: CallbackQuery):
    await query.answer()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Купити", callback_data="buy_elite"), InlineKeyboardButton(text="◀️ Назад", callback_data="subscription_main")]])
    await query.message.edit_text("💎 <b>VIP Elite - 1,200 грн/мес</b>\n\nВсе необмежено!\nПріоритетна підтримка 24/7\n🎁 Бонус: +30% ліміти", reply_markup=kb, parse_mode="HTML")

@user_router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer(main_menu_description(), reply_markup=main_menu(), parse_mode="HTML")

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
    await query.message.edit_text(main_menu_description(), reply_markup=main_menu(), parse_mode="HTML")

# Обробники для нових функцій
@user_router.callback_query(F.data == "payments_main")
async def payments_main(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Активувати SHADOW ключ", callback_data="activate_key")],
        [InlineKeyboardButton(text="📋 Мій ключ", callback_data="my_license")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="user_menu")]
    ])
    await query.message.edit_text("""🔐 <b>ЛІЦЕНЗУВАННЯ</b>

═══════════════════════

<b>💎 SHADOW SYSTEM</b> використовує систему 
ліцензійних ключів для авторизації.

<b>🔑 Як отримати ключ:</b>
├ Зв'яжіться з адміністратором
├ Отримайте унікальний SHADOW ключ
└ Активуйте через команду /activate

<b>📋 Типи ліцензій:</b>
├ <code>MANAGER</code> - Операційний доступ
├ <code>LEADER</code> - Керування командою
└ <code>ADMIN</code> - Повний контроль""", reply_markup=kb, parse_mode="HTML")

@user_router.callback_query(F.data == "settings_main")
async def settings_main(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("⚙️ <b>Налаштування</b>", reply_markup=settings_menu(), parse_mode="HTML")

@user_router.callback_query(F.data == "texting")
async def texting_callback(query: CallbackQuery):
    await query.answer()
    from handlers.texting import texting_menu
    await texting_menu(query.message)

@user_router.callback_query(F.data == "help")
async def help_callback(query: CallbackQuery):
    await query.answer()
    from handlers.help import help_menu
    await help_menu(query.message)

@user_router.callback_query(F.data == "profile")
async def profile_callback(query: CallbackQuery):
    await query.answer()
    from core.roles import ROLE_NAMES
    user = query.from_user
    role = user_service.get_user_role(user.id)
    role_name = ROLE_NAMES.get(role, "Гість")
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="user_menu")]
    ])
    
    await query.message.edit_text(f"""👤 <b>ПРОФІЛЬ</b>

═══════════════════════

<b>📋 Інформація:</b>
├ 🆔 ID: <code>{user.id}</code>
├ 👤 Ім'я: {user.first_name}
├ 🏷 Username: @{user.username or 'не вказано'}
└ 👔 Роль: <b>{role_name}</b>

<b>🔑 Ліцензія:</b>
└ Статус: {'✅ Активна' if role != 'guest' else '⏳ Очікує активації'}""", reply_markup=kb, parse_mode="HTML")

@user_router.callback_query(F.data == "my_bots")
async def my_bots_callback(query: CallbackQuery):
    await query.answer()
    from handlers.botnet import botnet_description, botnet_kb
    await query.message.edit_text(botnet_description(), reply_markup=botnet_kb(), parse_mode="HTML")

@user_router.callback_query(F.data == "osint_data")
async def osint_data_callback(query: CallbackQuery):
    await query.answer()
    from handlers.osint import osint_description, osint_kb
    await query.message.edit_text(osint_description(), reply_markup=osint_kb(), parse_mode="HTML")

@user_router.callback_query(F.data == "campaigns")
async def campaigns_callback(query: CallbackQuery):
    await query.answer()
    from handlers.texting import texting_kb
    await query.message.edit_text("📝 <b>Кампанії</b>\n\nВсього кампаній: 45\nАктивних: 12\nПриклад результатів:\n• Промо: CTR 45%, конверсія 12%\n• Привітання: Engagement 78%", reply_markup=texting_kb(), parse_mode="HTML")

@user_router.callback_query(F.data == "campaigns_main")
async def campaigns_main_callback(query: CallbackQuery):
    await query.answer()
    from handlers.texting import texting_kb, texting_description
    await query.message.edit_text(texting_description(), reply_markup=texting_kb(), parse_mode="HTML")

@user_router.callback_query(F.data == "analytics_main")
async def analytics_main_callback(query: CallbackQuery):
    await query.answer()
    from handlers.analytics import analytics_description, analytics_kb
    await query.message.edit_text(analytics_description(), reply_markup=analytics_kb(), parse_mode="HTML")

@user_router.callback_query(F.data == "subscription_main")
async def subscription_main_callback(query: CallbackQuery):
    await query.answer()
    from handlers.subscriptions import subscriptions_description, subscriptions_kb
    await query.message.edit_text(subscriptions_description(), reply_markup=subscriptions_kb(), parse_mode="HTML")

@user_router.callback_query(F.data == "onboarding_start")
async def onboarding_start_callback(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("🎯 <b>Онбординг - Навчання новачків</b>\n\n📍 Рівень 1: Основи\n📍 Рівень 2: Практика\n📍 Рівень 3: Продвинуті функції\n\nПрогрес: 0%\n\nРозпочати навчання →", parse_mode="HTML")

