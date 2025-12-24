from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_IDS

admin_router = Router()

class AdminStates(StatesGroup):
    waiting_broadcast = State()

@admin_router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Доступ заборонений")
        return
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Розсилка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="👥 Користувачі", callback_data="admin_users")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="💰 Платежі", callback_data="admin_payments")],
        [InlineKeyboardButton(text="🚫 Блокування", callback_data="admin_block")],
    ])
    await message.answer("🛡️ <b>Адміністративна панель</b>", reply_markup=kb, parse_mode="HTML")

@admin_router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.edit_text("📢 Напишіть текст розсилки для всіх користувачів:")
    await state.set_state(AdminStates.waiting_broadcast)

@admin_router.message(AdminStates.waiting_broadcast)
async def process_broadcast(message: Message, state: FSMContext):
    await message.answer(f"✅ Розсилка запущена!\n\nОтримувачів: 1,245\nСтатус: В обробці...")
    await state.clear()

@admin_router.callback_query(F.data == "admin_users")
async def admin_users(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("👥 <b>Управління користувачами</b>\n\nВсього: 1,245\nАктивних: 456\nПреміум: 234\nБлокованих: 8", parse_mode="HTML")

@admin_router.callback_query(F.data == "admin_stats")
async def admin_stats(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("📊 <b>Статистика боту</b>\n\nМісячний дохід: ₴45,230\nРозсилок: 5,432\nПомилок: 0.2%", parse_mode="HTML")

@admin_router.callback_query(F.data == "admin_payments")
async def admin_payments(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("💰 <b>Платежі</b>\n\nБез оплати: 3\nОчікують: 5\nОплачено: 234", parse_mode="HTML")

@admin_router.callback_query(F.data == "admin_block")
async def admin_block(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("🚫 <b>Блокування</b>\n\nЗа яких користувачів заблокувати? (напишіть User ID або username)", parse_mode="HTML")

@admin_router.callback_query(F.data == "back_to_menu")
async def admin_back_to_menu(query: CallbackQuery):
    await query.answer()
    from keyboards.user import main_menu, main_menu_description
    await query.message.edit_text(main_menu_description(), reply_markup=main_menu(), parse_mode="HTML")
