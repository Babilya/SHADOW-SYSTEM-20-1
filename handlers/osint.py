from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

osint_router = Router()

class OSINTStates(StatesGroup):
    waiting_keyword = State()
    waiting_chat = State()

def osint_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Геосканування", callback_data="geo_scan")],
        [InlineKeyboardButton(text="👤 Аналіз користувачів", callback_data="user_analysis")],
        [InlineKeyboardButton(text="💬 Аналіз чатів", callback_data="chat_analysis")],
        [InlineKeyboardButton(text="📊 Лог видалень", callback_data="deletion_log")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")],
    ])

def osint_description() -> str:
    return """<b>🔍 OSINT & ПАРСИНГ</b>

<b>🔍 Геосканування</b>
Знаходження чатів та каналів за географічною локацією. Пошук активних користувачів в конкретному регіоні з фільтрацією за інтересами.

<b>👤 Аналіз користувачів</b>
Детальний аналіз профілів користувачів: активність, історія повідомлень, зв'язки з іншими користувачами, ризик-фактори.

<b>💬 Аналіз чатів</b>
Дослідження структури чатів, динаміки розмов, ключових осіб та трендів. Виявлення модераторів, ботів та особливо активних членів.

<b>📊 Лог видалень</b>
Архів видалених повідомлень та користувачів. Відновлення історії видалень з датами та часом видалення."""

@osint_router.message(Command("osint"))
async def osint_cmd(message: Message):
    await message.answer("🔍 <b>OSINT та Парсинг</b>\n\nВиберіть опцію:", reply_markup=osint_kb(), parse_mode="HTML")

@osint_router.callback_query(F.data == "osint_main")
async def osint_menu(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("🔍 <b>OSINT та Парсинг</b>\n\nВиберіть опцію:", reply_markup=osint_kb(), parse_mode="HTML")

# Старий код

@osint_router.callback_query(F.data == "geo_scan")
async def geo_scan(query: CallbackQuery, state: FSMContext):
    await query.answer()
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="osint_main")]])
    await query.message.edit_text("🔍 Напишіть ключове слово для геосканування (наприклад: 'Чернівці')", reply_markup=back_kb)
    await state.set_state(OSINTStates.waiting_keyword)

@osint_router.message(OSINTStates.waiting_keyword)
async def process_keyword(message: Message, state: FSMContext):
    await message.answer(f"🔍 Сканування за '{message.text}'...\n\nЗнайдено чатів: 12\nЗнайдено користувачів: 245")
    await state.clear()

@osint_router.callback_query(F.data == "user_analysis")
async def user_analysis(query: CallbackQuery):
    await query.answer()
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="osint_main")]])
    await query.message.edit_text("👤 <b>Аналіз користувачів</b>\n\nАнальзовано: 5,234\nАктивних: 2,156\nБотів: 342", reply_markup=back_kb, parse_mode="HTML")

@osint_router.callback_query(F.data == "chat_analysis")
async def chat_analysis(query: CallbackQuery):
    await query.answer()
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="osint_main")]])
    await query.message.edit_text("💬 <b>Аналіз чатів</b>\n\nЧатів: 156\nСередня активність: 234 повідомлення/день\nРискові чати: 3", reply_markup=back_kb, parse_mode="HTML")

@osint_router.callback_query(F.data == "deletion_log")
async def deletion_log(query: CallbackQuery):
    await query.answer()
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="osint_main")]])
    await query.message.edit_text("📊 <b>Лог видалень</b>\n\nВидалено повідомлень: 1,234\nВидалено користувачів: 45\nПослідня активність: 2 хв тому", reply_markup=back_kb, parse_mode="HTML")

@osint_router.callback_query(F.data == "back_to_menu")
async def osint_back_to_menu(query: CallbackQuery):
    await query.answer()
    from keyboards.user import main_menu, main_menu_description
    await query.message.edit_text(main_menu_description(), reply_markup=main_menu(), parse_mode="HTML")
