import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "6838247512"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///shadow_system.db")

from database.models import Base, User, Application, Key, Project
from database.crud import UserCRUD, KeyCRUD, ProjectCRUD, ApplicationCRUD
from core.key_generator import generate_key

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL, echo=False)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

class AppFSM(StatesGroup):
    tariff = State()
    duration = State()
    name = State()
    purpose = State()
    contact = State()
    person_req = State()
    confirm = State()

def get_db():
    return SessionLocal()

def guest_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📦 Тарифи та Можливості")],
        [KeyboardButton(text="🔐 Авторизація")],
        [KeyboardButton(text="📚 Допомога та Інфо")]
    ], resize_keyboard=True)

def tariffs_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔹 Baseus", callback_data="tariff_baseus")],
        [InlineKeyboardButton(text="🔶 Standard", callback_data="tariff_standard")],
        [InlineKeyboardButton(text="👑 Premium", callback_data="tariff_premium")],
        [InlineKeyboardButton(text="💎 Person", callback_data="tariff_person")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_guest")]
    ])

def duration_kb(tariff):
    btns = []
    if tariff != "person":
        btns.append([
            KeyboardButton(text="2 дні"),
            KeyboardButton(text="14 днів"),
            KeyboardButton(text="30 днів")
        ])
    btns.append([KeyboardButton(text="🔙 Скасувати")])
    return ReplyKeyboardMarkup(keyboard=btns, resize_keyboard=True)

def apply_kb(tariff):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оформити заявку", callback_data=f"apply_{tariff}")],
        [InlineKeyboardButton(text="🔙 До списку", callback_data="tariffs")]
    ])

def user_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🤖 Botnet"), KeyboardButton(text="🚀 Розсилки")],
        [KeyboardButton(text="🔍 OSINT"), KeyboardButton(text="📊 Аналітика")],
        [KeyboardButton(text="👥 Команда"), KeyboardButton(text="⚙️ Налаштування")],
        [KeyboardButton(text="📚 Допомога")]
    ], resize_keyboard=True)

TARIFF_DESC = {
    "baseus": """🔹 ТАРИФ: BASEUS
Ідеальний для новачків та тестування

✅ ФУНКЦІОНАЛ:
• 5 активних ботів одночасно
• 1 акаунт менеджера (CRM)
• Базова статистика
• Підтримка 10:00-22:00 (1 рівень)

💰 ВАРТІСТЬ:
⏱ 2 дні (Тест) — 2 800 ₴
📅 14 днів — 5 900 ₴
📆 30 днів — 8 400 ₴ (ВИГІДНО!)

🎯 Для кого: Стартапи, фріленсери""",

    "standard": """🔶 ТАРИФ: STANDARD
Ідеальний для маркетингових агенцій

✅ ФУНКЦІОНАЛ:
• 50 активних ботів одночасно
• 5 акаунтів менеджерів (CRM)
• Модуль OSINT (Парсинг + Гео-сканер)
• Експорт звітів у PDF/CSV
• Підтримка 10:00-22:00 (2 рівень)
• Розумний прогрів ботів

💰 ВАРТІСТЬ:
⏱ 2 дні (Тест) — 2 800 ₴
📅 14 днів — 5 900 ₴
📆 30 днів — 8 400 ₴ (ВИГІДНО!)

🎯 Для кого: Маркетингові агенції, арбітраж""",

    "premium": """👑 ТАРИФ: PREMIUM
Для професіоналів та швидкого масштабування

✅ ФУНКЦІОНАЛ:
• 100 активних ботів одночасно
• Безліміт менеджерів (CRM)
• Весь модуль OSINT (Парсинг, Гео-сканер, Поіск по базам)
• Експорт звітів у PDF/CSV/JSON
• Пріоритетна підтримка 24/7 (3 рівень)
• Розумний прогрів + ротація проксі
• API для інтеграцій
• Webhook для автоматизації

💰 ВАРТІСТЬ:
⏱ 2 дні (Тест) — 5 900 ₴
📅 14 днів — 11 800 ₴
📆 30 днів — 16 800 ₴ (ВИГІДНО!)

🎯 Для кого: PRO менеджери, крупные агенции""",

    "person": """💎 ТАРИФ: PERSON
Enterprise рішення з індивідуальним підходом

✅ ФУНКЦІОНАЛ:
• Більш 1000+ ботів одночасно
• Безліміт менеджерів (CRM)
• Весь функціонал системи
• Персональна підтримка 24/7 (VIP)
• Білий ярлик / Ребрендинг
• Власна API з документацією
• Спеціальні інтеграції
• Консультація архітектора
• SLA гарантії 99.9%

💰 ВАРТІСТЬ:
Узгоджується індивідуально в залежності від об'ємів

🎯 Для кого: Корпорації, крупні холдинги, resellers"""
}

@router.message(Command("start"))
async def start(msg: Message):
    db = get_db()
    try:
        user = UserCRUD.get_or_create(db, str(msg.from_user.id), msg.from_user.username, msg.from_user.first_name)
        project = ProjectCRUD.get_by_leader(db, str(msg.from_user.id))
        
        if project and project.is_active:
            ws = f"""🖥 РОБОЧИЙ СТІЛ | Проект #{project.id}

👤 Власник: {user.first_name} ({msg.from_user.id})
💎 Тариф: {project.tariff.upper()} (до 25.12.2025)
👥 Доступно менеджерів: {project.managers_used}/{project.managers_limit}
🤖 Доступно ботів: {project.bots_used}/{project.bots_limit}

Статус системи: 🟢 АКТИВНА"""
            await msg.answer(ws, reply_markup=user_kb())
        else:
            welcome = """👋 Вітаємо в SHADOW SYSTEM v2.0
Професійна платформа для автоматизації Telegram-маркетингу

💡 Чому обирають нас?
• Масштаб: 1000+ ботів в один клік
• Безпека: Унікальні відбитки та проксі
• OSINT: Глибокий аналіз аудиторії
• CRM: Кабінет для ваших менеджерів

🔒 Статус: ГІСТЬ
Для доступу оберіть тариф або авторизуйтесь"""
            await msg.answer(welcome, reply_markup=guest_kb())
    finally:
        db.close()

@router.message(F.text.contains("Тарифи"))
async def show_tariffs(msg: Message):
    await msg.answer("""💎 ОБЕРІТЬ РІВЕНЬ ДОСТУПУ

🔹 Baseus — Тест/Новачок (5 ботів, 1 менеджер)
🔶 Standard — Агенція/Арбітраж (50 ботів, 5 менеджерів)
👑 Premium — PRO/Швидкість (100 ботів, безліміт менеджерів)
💎 Person — Enterprise (Індивідуальна збірка)""", reply_markup=tariffs_kb())

@router.callback_query(F.data.startswith("tariff_"))
async def show_tariff_details(query: CallbackQuery):
    tariff = query.data.split("_")[1]
    if tariff in TARIFF_DESC:
        await query.message.edit_text(TARIFF_DESC[tariff], reply_markup=apply_kb(tariff))
    await query.answer()

@router.callback_query(F.data.startswith("apply_"))
async def start_application(query: CallbackQuery, state: FSMContext):
    tariff = query.data.split("_")[1]
    await state.update_data(tariff=tariff)
    
    if tariff == "person":
        await state.set_state(AppFSM.name)
        await query.message.edit_text("👤 Як до вас звертатися?")
    else:
        await state.set_state(AppFSM.duration)
        await query.message.edit_text("На який термін бажаєте придбати доступ?", 
                                     reply_markup=duration_kb(tariff))
    await query.answer()

@router.message(AppFSM.duration)
async def process_duration(msg: Message, state: FSMContext):
    try:
        days = int(msg.text.split()[0])
        await state.update_data(duration=days)
        await state.set_state(AppFSM.name)
        await msg.answer("👤 Як до вас звертатися?")
    except:
        await msg.answer("❌ Виберіть з запропонованих варіантів")

@router.message(AppFSM.name)
async def process_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await state.set_state(AppFSM.purpose)
    await msg.answer("""🎯 Для яких задач плануєте використовувати систему?
(наприклад: арбітраж трафіку, товарка, послуги, крипто-промо)""")

@router.message(AppFSM.purpose)
async def process_purpose(msg: Message, state: FSMContext):
    await state.update_data(purpose=msg.text)
    await state.set_state(AppFSM.contact)
    await msg.answer("📞 Залиште контакт для зв'язку (Telegram, Phone, Email)")

@router.message(AppFSM.contact)
async def process_contact(msg: Message, state: FSMContext):
    data = await state.get_data()
    contact = msg.text
    tariff = data["tariff"]
    duration = data.get("duration", 30)
    
    prices = {"baseus": {2: 2800, 14: 5900, 30: 8400},
              "standard": {2: 2800, 14: 5900, 30: 8400},
              "premium": {2: 5900, 14: 11800, 30: 16800},
              "person": {0: 0}}
    amount = prices.get(tariff, {}).get(duration, 0)
    
    db = get_db()
    try:
        app = ApplicationCRUD.create(db,
            user_id=str(msg.from_user.id),
            telegram_id=f"@{msg.from_user.username}",
            tariff=tariff,
            duration=duration,
            name=data["name"],
            purpose=data["purpose"],
            contact=contact,
            amount=amount
        )
        
        await msg.answer(f"""📋 ПЕРЕВІРКА ВАШОЇ ЗАЯВКИ

💎 Тариф: {tariff.upper()} ({duration} днів)
💰 Сума: {amount} ₴
👤 Ім'я: {data['name']}
🎯 Мета: {data['purpose']}
📞 Контакт: {contact}

⚠️ Натискаючи "Надіслати", ви погоджуєтесь з умовами.
Заборонено: спам, шахрайство, наркотики.""")
        
        await bot.send_message(ADMIN_ID, 
f"""🔔 НОВА ЗАЯВКА #{app.id}

👤 Клієнт: {data['name']} ({msg.from_user.id})
📊 Username: @{msg.from_user.username}
💎 Тариф: {tariff.upper()} ({duration} днів)
💰 Сума: {amount} ₴
🎯 Мета: {data['purpose']}
📞 Контакт: {contact}
⏰ Час: {datetime.now().strftime('%H:%M')}
📈 Статус: НОВА""")
        
        await msg.answer("✅ Заявку успішно надіслано!\n\nАдміністратор отримав ваш запит. Очікуйте на відповідь.")
    finally:
        db.close()
    
    await state.clear()

@router.message(F.text.contains("Авторизація"))
async def auth_menu(msg: Message):
    await msg.answer("🔐 ЦЕНТР АВТОРИЗАЦІЇ\n\nВведіть ваш ліцензійний ключ (формат: SHADOW-XXXX-XXXX)")

@router.message(F.text.startswith("SHADOW-"))
async def check_key(msg: Message):
    db = get_db()
    try:
        key_code = msg.text.upper()
        key = KeyCRUD.get_by_code(db, key_code)
        
        if not key:
            await msg.answer("❌ Ключ не знайден. Перевірте правильність введення.")
        elif key.is_used:
            await msg.answer("❌ Ключ вже використаний іншим користувачем")
        elif key.expires_at and key.expires_at < datetime.now():
            await msg.answer("❌ Ключ закінчився")
        else:
            project = ProjectCRUD.create(db,
                leader_id=str(msg.from_user.id),
                leader_username=msg.from_user.username,
                key_id=key.id,
                name=f"Проект {msg.from_user.first_name}",
                tariff=key.tariff,
                bots_limit=50 if key.tariff == "standard" else (100 if key.tariff == "premium" else 5),
                managers_limit=5 if key.tariff == "standard" else (999 if key.tariff in ["premium", "person"] else 1)
            )
            
            await msg.answer(f"""✅ АВТОРИЗАЦІЯ УСПІШНА!

👋 Ласкаво просимо, {msg.from_user.first_name}!
💎 Ваш тариф: {key.tariff.upper()}
👥 Ваш проект: Проект #{project.id}
🔧 Статус: 🟢 АКТИВНИЙ

Зараз відкривається ваш робочий стіл...""", reply_markup=user_kb())
    finally:
        db.close()

@router.message(F.text.contains("Допомога"))
async def help_handler(msg: Message):
    await msg.answer("""📚 ЦЕНТР ДОПОМОГИ

❓ ПОШИРЕНІ ПИТАННЯ:

1️⃣ Як купити доступ?
   Оберіть тариф → Заповніть форму → Отримайте ключ

2️⃣ Як активувати ключ?
   Перейдіть в "Авторизація" → Введіть ключ

3️⃣ Скільки це коштує?
   Дивіться в розділі "Тарифи"

4️⃣ Є ліміти на боти?
   Так, залежить від вибраного тарифу

📞 КОНТАКТИ:
Технічна підтримка: t.me/shadow_support
Продажі: t.me/shadow_sales""")

@router.message()
async def default_handler(msg: Message):
    await msg.answer("👋 Оберіть опцію:", reply_markup=guest_kb())

dp.include_router(router)

async def main():
    logger.info("🚀 Бот запущено успішно!")
    logger.info(f"💎 ID власника: {ADMIN_ID}")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
