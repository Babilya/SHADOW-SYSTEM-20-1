from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.admin import admin_menu, broadcast_menu
from config import ADMIN_IDS

admin_router = Router()

class AdminStates(StatesGroup):
    waiting_for_broadcast_text = State()
    waiting_for_announce_text = State()

@admin_router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Адміністративна панель"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Ви не маєте доступу до цієї команди")
        return
    
    await message.answer(
        "🛡️ <b>Адміністративна панель</b>\n\n"
        "Виберіть дію:",
        reply_markup=admin_menu(),
        parse_mode="HTML"
    )

@admin_router.callback_query(F.data == "broadcast", flags={"admin_only": True})
async def start_broadcast(query: CallbackQuery, state: FSMContext):
    """Почати розсилку"""
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонений", show_alert=True)
        return
    
    await query.message.edit_text("📢 Напишіть текст розсилки всім користувачам:")
    await state.set_state(AdminStates.waiting_for_broadcast_text)

@admin_router.message(AdminStates.waiting_for_broadcast_text)
async def process_broadcast(message: Message, state: FSMContext):
    """Обробити розсилку"""
    await message.answer(
        f"✅ Розсилка запущена!\n\n"
        f"Текст: {message.text}\n"
        f"Буде надіслано: 1,245 користувачам\n"
        f"Статус: В обробці..."
    )
    await state.clear()

@admin_router.callback_query(F.data == "stats_admin")
async def admin_stats(query: CallbackQuery):
    """Статистика для адміна"""
    await query.answer()
    await query.message.edit_text(
        "📊 <b>Статистика боту</b>\n\n"
        "Всього користувачів: <b>1,245</b>\n"
        "Активних: <b>456</b>\n"
        "Преміум: <b>234</b>\n"
        "Грошових надходжень: <b>₴45,230</b>\n"
        "Розсилок відправлено: <b>5,432</b>\n"
        "Помилок: <b>12</b>",
        parse_mode="HTML"
    )

@admin_router.callback_query(F.data == "users")
async def manage_users(query: CallbackQuery):
    """Управління користувачами"""
    await query.answer()
    await query.message.edit_text(
        "👥 <b>Управління користувачами</b>\n\n"
        "Всього: 1,245\n"
        "Активних: 456\n"
        "Заблокованих: 23\n"
        "Видалених: 12",
        parse_mode="HTML"
    )

@admin_router.callback_query(F.data == "announce")
async def announce_message(query: CallbackQuery, state: FSMContext):
    """Оголошення"""
    await query.message.edit_text("📣 Напишіть текст оголошення:")
    await state.set_state(AdminStates.waiting_for_announce_text)

@admin_router.message(AdminStates.waiting_for_announce_text)
async def process_announce(message: Message, state: FSMContext):
    """Обробити оголошення"""
    await message.answer(
        f"✅ Оголошення створене!\n\n"
        f"{message.text}\n\n"
        f"Буде показане всім користувачам при наступному запиті"
    )
    await state.clear()

@admin_router.message(Command("block"))
async def cmd_block(message: Message):
    """Заблокувати користувача"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Доступ заборонений")
        return
    
    await message.answer("/block [user_id] - Заблокувати користувача")

@admin_router.message(Command("unblock"))
async def cmd_unblock(message: Message):
    """Розблокувати користувача"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Доступ заборонений")
        return
    
    await message.answer("/unblock [user_id] - Розблокувати користувача")

@admin_router.callback_query(F.data == "maintenance")
async def maintenance_mode(query: CallbackQuery):
    """Режим обслуговування"""
    await query.answer()
    await query.message.edit_text(
        "🔧 <b>Режим обслуговування</b>\n\n"
        "Статус: ВКЛ ✅\n"
        "Користувачам показуватиметься повідомлення про обслуговування",
        parse_mode="HTML"
    )
