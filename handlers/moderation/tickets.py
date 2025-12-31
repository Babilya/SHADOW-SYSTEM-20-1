from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import logging

from config import ADMIN_IDS
from core.audit_logger import audit_logger, ActionCategory
from core.alerts import alert_system, AlertType

logger = logging.getLogger(__name__)
tickets_router = Router()
router = tickets_router

class TicketStates(StatesGroup):
    subject = State()
    message = State()
    admin_reply = State()

tickets_storage = {}
ticket_messages = {}

def generate_ticket_id():
    return f"TKT-{datetime.now().strftime('%Y%m%d')}-{len(tickets_storage) + 1:04d}"

def tickets_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Новий тікет", callback_data="ticket_new")],
        [InlineKeyboardButton(text="📋 Мої тікети", callback_data="ticket_my")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])

def admin_tickets_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Нові тікети", callback_data="admin_tickets_new")],
        [InlineKeyboardButton(text="📋 Всі тікети", callback_data="admin_tickets_all")],
        [InlineKeyboardButton(text="✅ Закриті", callback_data="admin_tickets_closed")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])

@tickets_router.message(Command("support"))
async def support_command(message: Message):
    text = """💬 <b>ПІДТРИМКА</b>

Ви можете створити тікет для зв'язку з адміністрацією.

<b>Час відповіді:</b> до 24 годин
<b>Пріоритет:</b> звичайний

Виберіть дію:"""
    
    await message.answer(text, reply_markup=tickets_kb(), parse_mode="HTML")

@tickets_router.callback_query(F.data == "ticket_new")
async def ticket_new(query: CallbackQuery, state: FSMContext):
    await state.set_state(TicketStates.subject)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="ticket_cancel")]
    ])
    
    await query.message.edit_text(
        "📝 <b>НОВИЙ ТІКЕТ</b>\n\n"
        "Введіть тему звернення:",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@tickets_router.message(TicketStates.subject)
async def ticket_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await state.set_state(TicketStates.message)
    await message.answer(
        "📝 Опишіть детально вашу проблему або питання:\n\n"
        "<i>Чим детальніше опишете, тим швидше отримаєте відповідь.</i>",
        parse_mode="HTML"
    )

@tickets_router.message(TicketStates.message)
async def ticket_message(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    
    ticket_id = generate_ticket_id()
    
    ticket = {
        "id": ticket_id,
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "first_name": message.from_user.first_name,
        "subject": data.get("subject"),
        "status": "open",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    tickets_storage[ticket_id] = ticket
    ticket_messages[ticket_id] = [{
        "from": "user",
        "user_id": message.from_user.id,
        "text": message.text,
        "time": datetime.now().isoformat()
    }]
    
    await audit_logger.log(
        user_id=message.from_user.id,
        action="ticket_created",
        category=ActionCategory.SYSTEM,
        username=message.from_user.username,
        details={"ticket_id": ticket_id, "subject": data.get("subject")}
    )
    
    for admin_id in ADMIN_IDS:
        try:
            admin_kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💬 Відповісти", callback_data=f"admin_ticket_reply_{ticket_id}")],
                [InlineKeyboardButton(text="✅ Закрити", callback_data=f"admin_ticket_close_{ticket_id}")]
            ])
            
            await bot.send_message(
                admin_id,
                f"""📥 <b>НОВИЙ ТІКЕТ</b>

<b>ID:</b> {ticket_id}
<b>Від:</b> @{message.from_user.username or 'N/A'} ({message.from_user.id})
<b>Ім'я:</b> {message.from_user.first_name}

<b>Тема:</b> {data.get('subject')}

<b>Повідомлення:</b>
{message.text[:500]}

<b>Час:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}""",
                reply_markup=admin_kb,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")
    
    await message.answer(
        f"""✅ <b>ТІКЕТ СТВОРЕНО</b>

<b>Номер тікету:</b> {ticket_id}
<b>Тема:</b> {data.get('subject')}
<b>Статус:</b> 🟢 Відкритий

Адміністратор відповість вам найближчим часом.
Ви отримаєте повідомлення коли буде відповідь.""",
        parse_mode="HTML"
    )
    await state.clear()

@tickets_router.callback_query(F.data == "ticket_my")
async def ticket_my(query: CallbackQuery):
    user_tickets = [t for t in tickets_storage.values() if t["user_id"] == query.from_user.id]
    
    if not user_tickets:
        await query.message.edit_text(
            "📋 <b>МОЇ ТІКЕТИ</b>\n\nУ вас немає тікетів.",
            reply_markup=tickets_kb(),
            parse_mode="HTML"
        )
        await query.answer()
        return
    
    kb_buttons = []
    for ticket in user_tickets[-10:]:
        status_icon = "🟢" if ticket["status"] == "open" else "🔴"
        kb_buttons.append([
            InlineKeyboardButton(
                text=f"{status_icon} {ticket['id']}: {ticket['subject'][:20]}",
                callback_data=f"view_ticket_{ticket['id']}"
            )
        ])
    kb_buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="support_menu")])
    
    await query.message.edit_text(
        f"📋 <b>МОЇ ТІКЕТИ</b>\n\nВсього: {len(user_tickets)}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_buttons),
        parse_mode="HTML"
    )
    await query.answer()

@tickets_router.callback_query(F.data.startswith("view_ticket_"))
async def view_ticket(query: CallbackQuery):
    ticket_id = query.data.replace("view_ticket_", "")
    ticket = tickets_storage.get(ticket_id)
    
    if not ticket:
        await query.answer("Тікет не знайдено")
        return
    
    messages = ticket_messages.get(ticket_id, [])
    
    text = f"""📋 <b>ТІКЕТ {ticket_id}</b>

<b>Тема:</b> {ticket['subject']}
<b>Статус:</b> {'🟢 Відкритий' if ticket['status'] == 'open' else '🔴 Закритий'}
<b>Створено:</b> {ticket['created_at'][:16]}

<b>Повідомлення:</b>
"""
    
    for msg in messages[-5:]:
        sender = "👤 Ви" if msg["from"] == "user" else "🛡️ Адмін"
        text += f"\n{sender}: {msg['text'][:100]}..."
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Відповісти", callback_data=f"reply_ticket_{ticket_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="ticket_my")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()

@tickets_router.callback_query(F.data.startswith("admin_ticket_reply_"))
async def admin_ticket_reply_start(query: CallbackQuery, state: FSMContext):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    ticket_id = query.data.replace("admin_ticket_reply_", "")
    await state.update_data(ticket_id=ticket_id)
    await state.set_state(TicketStates.admin_reply)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_tickets_menu")]
    ])
    
    await query.message.edit_text(
        f"💬 <b>ВІДПОВІДЬ НА ТІКЕТ {ticket_id}</b>\n\n"
        f"Напишіть відповідь:",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@tickets_router.message(TicketStates.admin_reply)
async def admin_ticket_reply_send(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    ticket_id = data.get("ticket_id")
    ticket = tickets_storage.get(ticket_id)
    
    if not ticket:
        await message.answer("❌ Тікет не знайдено")
        await state.clear()
        return
    
    if ticket_id not in ticket_messages:
        ticket_messages[ticket_id] = []
    
    ticket_messages[ticket_id].append({
        "from": "admin",
        "user_id": message.from_user.id,
        "text": message.text,
        "time": datetime.now().isoformat()
    })
    
    ticket["updated_at"] = datetime.now().isoformat()
    
    try:
        await bot.send_message(
            ticket["user_id"],
            f"""📩 <b>ВІДПОВІДЬ НА ТІКЕТ</b>

<b>Тікет:</b> {ticket_id}
<b>Тема:</b> {ticket['subject']}

<b>Відповідь адміністратора:</b>
{message.text}

<i>Для продовження діалогу використайте /support</i>""",
            parse_mode="HTML"
        )
        
        await message.answer(f"✅ Відповідь надіслано користувачу {ticket['user_id']}")
    except Exception as e:
        await message.answer(f"❌ Помилка: {e}")
    
    await state.clear()

@tickets_router.callback_query(F.data.startswith("admin_ticket_close_"))
async def admin_ticket_close(query: CallbackQuery, bot: Bot):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    ticket_id = query.data.replace("admin_ticket_close_", "")
    ticket = tickets_storage.get(ticket_id)
    
    if not ticket:
        await query.answer("Тікет не знайдено")
        return
    
    ticket["status"] = "closed"
    ticket["closed_by"] = query.from_user.id
    ticket["closed_at"] = datetime.now().isoformat()
    
    try:
        await bot.send_message(
            ticket["user_id"],
            f"""✅ <b>ТІКЕТ ЗАКРИТО</b>

<b>Тікет:</b> {ticket_id}
<b>Тема:</b> {ticket['subject']}

Ваш тікет було закрито адміністратором.
Для нових питань створіть новий тікет: /support""",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to notify user: {e}")
    
    await query.message.edit_text(f"✅ Тікет {ticket_id} закрито")
    await query.answer("Тікет закрито!")

@tickets_router.message(Command("tickets"))
async def admin_tickets_command(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Доступ заборонено")
        return
    
    open_tickets = [t for t in tickets_storage.values() if t["status"] == "open"]
    
    text = f"""📥 <b>АДМІН-КИШЕНЯ</b>

<b>📊 Статистика:</b>
├ Відкритих: {len(open_tickets)}
├ Всього: {len(tickets_storage)}
└ Сьогодні: {sum(1 for t in tickets_storage.values() if t['created_at'][:10] == datetime.now().strftime('%Y-%m-%d'))}

Виберіть дію:"""
    
    await message.answer(text, reply_markup=admin_tickets_kb(), parse_mode="HTML")

@tickets_router.callback_query(F.data == "admin_tickets_new")
async def admin_tickets_new(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    open_tickets = [t for t in tickets_storage.values() if t["status"] == "open"]
    
    if not open_tickets:
        await query.message.edit_text(
            "📥 <b>НОВІ ТІКЕТИ</b>\n\nНемає відкритих тікетів.",
            reply_markup=admin_tickets_kb(),
            parse_mode="HTML"
        )
        await query.answer()
        return
    
    kb_buttons = []
    for ticket in open_tickets[-10:]:
        kb_buttons.append([
            InlineKeyboardButton(
                text=f"🟢 {ticket['id']}: @{ticket.get('username', 'N/A')}",
                callback_data=f"admin_view_ticket_{ticket['id']}"
            )
        ])
    kb_buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="admin_tickets_menu")])
    
    await query.message.edit_text(
        f"📥 <b>ВІДКРИТІ ТІКЕТИ ({len(open_tickets)})</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_buttons),
        parse_mode="HTML"
    )
    await query.answer()

@tickets_router.callback_query(F.data == "ticket_cancel")
async def ticket_cancel(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.edit_text("❌ Створення тікету скасовано", reply_markup=tickets_kb())
    await query.answer()

@tickets_router.callback_query(F.data == "support_menu")
async def support_menu(query: CallbackQuery):
    await query.message.edit_text(
        "💬 <b>ПІДТРИМКА</b>\n\nВиберіть дію:",
        reply_markup=tickets_kb(),
        parse_mode="HTML"
    )
    await query.answer()

@tickets_router.callback_query(F.data == "admin_tickets_menu")
async def admin_tickets_menu(query: CallbackQuery):
    open_tickets = [t for t in tickets_storage.values() if t["status"] == "open"]
    
    text = f"""📥 <b>АДМІН-КИШЕНЯ</b>

<b>📊 Статистика:</b>
├ Відкритих: {len(open_tickets)}
├ Всього: {len(tickets_storage)}

Виберіть дію:"""
    
    await query.message.edit_text(text, reply_markup=admin_tickets_kb(), parse_mode="HTML")
    await query.answer()
