from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

logger = logging.getLogger(__name__)
osint_router = Router()
router = osint_router

class OSINTStates(StatesGroup):
    waiting_keyword = State()
    waiting_chat = State()
    waiting_dns_domain = State()
    waiting_whois_domain = State()
    waiting_ip = State()
    waiting_email = State()

def osint_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🌐 DNS Lookup", callback_data="osint_dns"),
            InlineKeyboardButton(text="📋 WHOIS", callback_data="osint_whois")
        ],
        [
            InlineKeyboardButton(text="🌍 IP Геолокація", callback_data="osint_geoip"),
            InlineKeyboardButton(text="📧 Email Verify", callback_data="osint_email")
        ],
        [
            InlineKeyboardButton(text="👤 Telegram User", callback_data="user_analysis"),
            InlineKeyboardButton(text="💬 Chat Parsing", callback_data="chat_analysis")
        ],
        [
            InlineKeyboardButton(text="📥 Експорт", callback_data="export_contacts"),
            InlineKeyboardButton(text="📈 Статистика", callback_data="osint_stats")
        ],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")
        ],
    ])

def osint_description() -> str:
    return """<b>🔍 OSINT & ПАРСИНГ</b>

<b>📊 ВИКОРИСТАНО В ЦЬОМУ МІСЯЦІ:</b>
Запитів: 1,245 / 5,000 (25%)

<b>🔧 ФУНКЦІОНАЛЬНІСТЬ:</b>

<b>📍 Геосканування</b> - Пошук чатів за локацією
<b>👤 Аналіз користувачів</b> - Деталі профілів
<b>💬 Аналіз чатів</b> - Дослідження структури
<b>📥 Експорт контактів</b> - Завантаження результатів
<b>📊 Лог видалень</b> - Архів видалень
<b>📈 Статистика OSINT</b> - Статистика використання"""

@osint_router.message(Command("osint"))
async def osint_cmd(message: Message):
    await message.answer(osint_description(), reply_markup=osint_kb(), parse_mode="HTML")

@osint_router.callback_query(F.data == "osint_main")
async def osint_menu(query: CallbackQuery):
    await query.answer()
    await query.message.answer(osint_description(), reply_markup=osint_kb(), parse_mode="HTML")

@osint_router.callback_query(F.data == "osint_stats")
async def osint_stats(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="osint_main")]
    ])
    await query.message.answer("""📈 <b>СТАТИСТИКА OSINT</b>

<b>ДОСТУПНІ ФУНКЦІЇ:</b>
DNS Lookup - Пошук DNS записів
WHOIS - Інформація про домен
IP Геолокація - Місцезнаходження IP
Email Verify - Перевірка email

<b>ПОТОЧНОГО МІСЯЦЯ:</b>
Запитів: активно
Ліміт: необмежено""", reply_markup=kb, parse_mode="HTML")
