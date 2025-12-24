import asyncio, logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "6838247512"))
DB = create_engine(os.getenv("DATABASE_URL", "sqlite:///shadow_system.db"))

from database.models import Base, User, Application, Key, Project, Ticket, Manager
from core.key_generator import generate_access_key, generate_ticket_id, generate_manager_key
from core.notification_system import NotificationSystem

Base.metadata.create_all(DB)
S = sessionmaker(bind=DB)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

class AppFSM(StatesGroup):
    tariff = State()
    duration = State()
    name = State()
    purpose = State()
    contact = State()
    confirm = State()

class AdminFSM(StatesGroup):
    app_id = State()
    template = State()
    custom_msg = State()

class TicketFSM(StatesGroup):
    subject = State()
    description = State()

class ManagerFSM(StatesGroup):
    project_id = State()
    role = State()

# === KEYBOARDS ===
def guest_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📦 Тарифи")], [KeyboardButton(text="🔐 Авторизація")], [KeyboardButton(text="🎫 Тікети")]], resize_keyboard=True)

def tariffs_inline():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔹 Baseus", callback_data="tariff_baseus")], [InlineKeyboardButton(text="🔶 Standard", callback_data="tariff_standard")], [InlineKeyboardButton(text="👑 Premium", callback_data="tariff_premium")], [InlineKeyboardButton(text="💎 Person", callback_data="tariff_person")]])

def user_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🤖 Botnet"), KeyboardButton(text="🚀 Розсилки")], [KeyboardButton(text="👥 Команда"), KeyboardButton(text="📊 Аналітика")], [KeyboardButton(text="⚙️ Налаштування"), KeyboardButton(text="🎫 Тікети")]], resize_keyboard=True)

def admin_kb(app_id):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📝 Шаблон", callback_data=f"adm_tmpl_{app_id}")], [InlineKeyboardButton(text="✏️ Своє", callback_data=f"adm_custom_{app_id}")], [InlineKeyboardButton(text="❌ Відхилити", callback_data=f"adm_reject_{app_id}")]])

# === TARIFF DETAILS ===
TARIFFS_TEXT = {
    "baseus": "🔹 BASEUS\n✅ 5 ботів\n✅ 1 менеджер\n💰 30д: 8400₴",
    "standard": "🔶 STANDARD\n✅ 50 ботів\n✅ 5 менеджерів\n✅ OSINT\n💰 30д: 8400₴",
    "premium": "👑 PREMIUM\n✅ 100 ботів\n✅ ∞ менеджерів\n💰 30д: 16800₴",
    "person": "💎 PERSON\n✅ ∞ ботів\n✅ ∞ менеджерів\n✅ Всь\n💰 Узгоджується"
}

# === HANDLERS ===
@router.message(Command("start"))
async def start(msg: Message):
    db = S()
    try:
        user = db.query(User).filter(User.telegram_id == str(msg.from_user.id)).first()
        if not user:
            user = User(telegram_id=str(msg.from_user.id), username=msg.from_user.username, first_name=msg.from_user.first_name)
            db.add(user)
            db.commit()
        
        project = db.query(Project).filter(Project.leader_id == str(msg.from_user.id)).first()
        if project and project.is_active:
            await msg.answer(f"🖥 РОБОЧИЙ СТІЛ\n💎 {project.tariff}\n🤖 {project.bots_used}/{project.bots_limit}\n👥 {project.managers_used}/{project.managers_limit}", reply_markup=user_kb())
        else:
            await msg.answer("👋 Вітаємо в SHADOW SYSTEM v2.0\n\n💡 Обирайте опцію:", reply_markup=guest_kb())
    finally:
        db.close()

@router.message(F.text.contains("Тарифи"))
async def tariffs(msg: Message):
    await msg.answer("💎 ОБЕРІТЬ ТАРИФ:", reply_markup=tariffs_inline())

@router.callback_query(F.data.startswith("tariff_"))
async def tariff_detail(q: CallbackQuery, state: FSMContext):
    tariff = q.data.split("_")[1]
    await state.update_data(tariff=tariff)
    if tariff == "person":
        await state.set_state(AppFSM.name)
    else:
        await state.set_state(AppFSM.duration)
    await q.message.edit_text(TARIFFS_TEXT[tariff] + "\n\n[2 дні | 14 днів | 30 днів]")
    await q.answer()

@router.message(AppFSM.duration)
async def duration(msg: Message, state: FSMContext):
    await state.update_data(duration=int(msg.text.split()[0]))
    await state.set_state(AppFSM.name)
    await msg.answer("👤 Як вас звати?")

@router.message(AppFSM.name)
async def name_app(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await state.set_state(AppFSM.purpose)
    await msg.answer("🎯 Для чого система?")

@router.message(AppFSM.purpose)
async def purpose_app(msg: Message, state: FSMContext):
    await state.update_data(purpose=msg.text)
    await state.set_state(AppFSM.contact)
    await msg.answer("📞 Контакт:")

@router.message(AppFSM.contact)
async def contact_app(msg: Message, state: FSMContext):
    data = await state.get_data()
    db = S()
    try:
        tariff = data["tariff"]
        days = data.get("duration", 30)
        prices = {"baseus": {2: 2800, 14: 5900, 30: 8400}, "standard": {2: 2800, 14: 5900, 30: 8400}, "premium": {2: 5900, 14: 11800, 30: 16800}, "person": {0: 0}}
        amount = prices.get(tariff, {}).get(days, 0)
        
        app = Application(user_id=str(msg.from_user.id), telegram_id=f"@{msg.from_user.username}", tariff=tariff, duration=days, name=data["name"], purpose=data["purpose"], contact=msg.text, amount=amount)
        db.add(app)
        db.commit()
        
        await msg.answer("✅ Заявка надіслана! Адміністратор зв'яжеться за 15 хвилин.")
        
        # NOTIFY ADMIN
        admin_msg = f"🔔 НОВА ЗАЯВКА #{app.id}\n👤 {data['name']}\n💎 {tariff}\n💰 {amount}₴\n📞 {msg.text}"
        await bot.send_message(ADMIN_ID, admin_msg, reply_markup=admin_kb(app.id))
    finally:
        db.close()
    await state.clear()

@router.message(F.text.contains("Авторизація"))
async def auth_menu(msg: Message):
    await msg.answer("🔐 Введіть ключ (SHADOW-XXXX-XXXX):")

@router.message(F.text.startswith("SHADOW-"))
async def auth_key(msg: Message):
    db = S()
    try:
        key = db.query(Key).filter(Key.code == msg.text.upper()).first()
        if not key or key.is_used or (key.expires_at and key.expires_at < datetime.now()):
            await msg.answer("❌ Ключ невалідний")
        else:
            project = Project(leader_id=str(msg.from_user.id), leader_username=msg.from_user.username, key_id=key.id, name=f"Проект {msg.from_user.first_name}", tariff=key.tariff, bots_limit=50, managers_limit=5)
            key.is_used = True
            key.user_id = str(msg.from_user.id)
            db.add(project)
            db.commit()
            await msg.answer("✅ АВТОРИЗАЦІЯ! Ласкаво просимо! 🎉", reply_markup=user_kb())
    finally:
        db.close()

@router.message(F.text.contains("Тікети"))
async def create_ticket(msg: Message, state: FSMContext):
    await state.set_state(TicketFSM.subject)
    await msg.answer("🎫 Тема тікету:")

@router.message(TicketFSM.subject)
async def ticket_subject(msg: Message, state: FSMContext):
    await state.update_data(subject=msg.text)
    await state.set_state(TicketFSM.description)
    await msg.answer("📝 Опишіть проблему:")

@router.message(TicketFSM.description)
async def ticket_desc(msg: Message, state: FSMContext):
    data = await state.get_data()
    db = S()
    try:
        ticket_id = generate_ticket_id()
        ticket = Ticket(ticket_id=ticket_id, user_id=str(msg.from_user.id), subject=data["subject"], description=msg.text, status="open")
        db.add(ticket)
        db.commit()
        
        await msg.answer(f"✅ Тікет #{ticket_id} створено!\nНаша команда розглянеться протягом 2 годин.")
        await bot.send_message(ADMIN_ID, f"🎫 НОВИЙ ТІКЕТ #{ticket_id}\n👤 @{msg.from_user.username}\n📌 {data['subject']}")
    finally:
        db.close()
    await state.clear()

@router.callback_query(F.data.startswith("adm_tmpl_"))
async def admin_template(q: CallbackQuery, state: FSMContext):
    app_id = q.data.split("_")[2]
    templates = {"mono": "💳 Монобанк: 5375...", "usdt": "🪙 USDT: TYj8u...", "clarify": "❓ Уточніть", "call": "📞 Зателефонуємо"}
    
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"1. {v}", callback_data=f"send_{k}_{app_id}")] for k, v in templates.items()])
    await q.message.edit_text("🔄 Оберіть шаблон:", reply_markup=kb)
    await q.answer()

@router.callback_query(F.data.startswith("send_"))
async def send_template(q: CallbackQuery):
    parts = q.data.split("_")
    template = parts[1]
    app_id = parts[2]
    
    templates_text = {
        "mono": "💳 Реквізити Monobank: 5375 4100 1234 5678",
        "usdt": "🪙 USDT TRC20: TYj8uVx5B9d7C6e5F4g3H2i1J0k9L8m7",
        "clarify": "❓ Уточніть детальніше вашу мету",
        "call": "📞 Наш менеджер спеціально зателефонує"
    }
    
    db = S()
    try:
        app = db.query(Application).filter(Application.id == int(app_id)).first()
        if app:
            await bot.send_message(int(app.user_id), templates_text[template])
            await q.answer("✅ Надіслано клієнту")
    finally:
        db.close()

@router.callback_query(F.data.startswith("adm_reject_"))
async def reject_app(q: CallbackQuery):
    app_id = q.data.split("_")[2]
    db = S()
    try:
        app = db.query(Application).filter(Application.id == int(app_id)).first()
        if app:
            app.status = "rejected"
            db.commit()
            await bot.send_message(int(app.user_id), "❌ На жаль, вашу заявку відхилено")
            await q.answer("✅ Відхилено")
    finally:
        db.close()

@router.message()
async def default(msg: Message):
    await msg.answer("👋 Оберіть опцію:", reply_markup=guest_kb())

dp.include_router(router)

async def main():
    logger.info(f"🚀 Бот запущено (Admin: {ADMIN_ID})")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
