import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.role_menus import (
    support_menu_kb, ticket_category_kb, ticket_priority_kb,
    tickets_list_kb, ticket_view_kb, ticket_status_kb, ticket_rating_kb
)
from services.support_service import support_service
from utils.db import get_session
from core.role_constants import UserRole

logger = logging.getLogger(__name__)

router = Router()

class TicketStates(StatesGroup):
    waiting_subject = State()
    waiting_message = State()
    waiting_reply = State()

async def safe_edit(callback: CallbackQuery, text: str, reply_markup=None):
    """Безпечне редагування повідомлення"""
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception:
        await callback.answer()

def is_admin(user_role: str) -> bool:
    """Перевірка чи користувач адмін"""
    return user_role in [UserRole.ADMIN, UserRole.ROOT]

@router.callback_query(F.data == "support_menu")
async def support_menu(callback: CallbackQuery, state: FSMContext):
    """Головне меню підтримки"""
    await state.clear()
    
    user_role = callback.message.chat.type
    is_admin_user = False
    
    text = """
🎧 <b>ЦЕНТР ПІДТРИМКИ</b>
───────────────═════

Потрібна допомога? Створіть тікет, 
і наша команда відповість якнайшвидше.

<b>Час відповіді:</b>
├ 🔴 Терміновий: до 1 години
├ 🟠 Високий: до 4 годин
├ 🟡 Звичайний: до 24 годин
└ 🟢 Низький: до 48 годин
"""
    
    await safe_edit(callback, text, support_menu_kb(is_admin_user))

@router.callback_query(F.data == "ticket_create")
async def ticket_create(callback: CallbackQuery):
    """Створення тікета - вибір категорії"""
    text = """
📩 <b>НОВИЙ ТІКЕТ</b>
───────────────═════

Виберіть категорію вашого запиту:
"""
    await safe_edit(callback, text, ticket_category_kb())

@router.callback_query(F.data.startswith("ticket_cat:"))
async def ticket_category(callback: CallbackQuery):
    """Вибрано категорію - вибір пріоритету"""
    category = callback.data.split(":")[1]
    
    category_name = support_service.CATEGORIES.get(category, category)
    
    text = f"""
📩 <b>НОВИЙ ТІКЕТ</b>
───────────────═════

📁 Категорія: {category_name}

Виберіть пріоритет:
"""
    await safe_edit(callback, text, ticket_priority_kb(category))

@router.callback_query(F.data.startswith("ticket_pri:"))
async def ticket_priority(callback: CallbackQuery, state: FSMContext):
    """Вибрано пріоритет - введення теми"""
    parts = callback.data.split(":")
    category = parts[1]
    priority = parts[2]
    
    await state.update_data(category=category, priority=priority)
    await state.set_state(TicketStates.waiting_subject)
    
    await callback.message.edit_text(
        "📝 Введіть тему тікета (коротко опишіть проблему):",
        reply_markup=None
    )

@router.message(TicketStates.waiting_subject)
async def ticket_subject_received(message: Message, state: FSMContext):
    """Отримано тему - введення повідомлення"""
    await state.update_data(subject=message.text)
    await state.set_state(TicketStates.waiting_message)
    
    await message.answer("""
📄 Тепер детально опишіть вашу проблему або запит.

Включіть:
├ Що саме сталося
├ Коли це почалося
├ Кроки для відтворення (якщо можливо)
└ Скріншоти (якщо є)
""", parse_mode="HTML")

@router.message(TicketStates.waiting_message)
async def ticket_message_received(message: Message, state: FSMContext):
    """Отримано повідомлення - створення тікета"""
    data = await state.get_data()
    user_id = str(message.from_user.id)
    user_role = "user"
    
    async with get_session() as session:
        result = await support_service.create_ticket(
            session,
            user_id=user_id,
            user_role=user_role,
            subject=data['subject'],
            message=message.text,
            category=data['category'],
            priority=data['priority']
        )
    
    await state.clear()
    
    await message.answer(f"""
✅ <b>ТІКЕТ СТВОРЕНО</b>
───────────────═════

🎫 Код: <code>{result['ticket_code']}</code>
📋 Тема: {result['subject']}
📁 Категорія: {result['category']}
⚡ Пріоритет: {result['priority']}

Очікуйте відповіді від нашої команди підтримки.
""", reply_markup=support_menu_kb(), parse_mode="HTML")

@router.callback_query(F.data == "tickets_my")
async def tickets_my(callback: CallbackQuery):
    """Мої тікети"""
    user_id = str(callback.from_user.id)
    
    async with get_session() as session:
        tickets = await support_service.get_tickets(session, user_id=user_id)
    
    if not tickets:
        text = "📭 У вас ще немає тікетів.\n\nСтворіть новий тікет, якщо потрібна допомога."
        await safe_edit(callback, text, support_menu_kb())
        return
    
    text = f"""
📋 <b>МОЇ ТІКЕТИ</b>
───────────────═════

Всього: {len(tickets)}
"""
    
    await safe_edit(callback, text, tickets_list_kb(tickets))

@router.callback_query(F.data == "tickets_all")
async def tickets_all(callback: CallbackQuery):
    """Всі тікети (для адмінів)"""
    async with get_session() as session:
        tickets = await support_service.get_tickets(session)
    
    text = f"""
📥 <b>ВСІ ТІКЕТИ</b>
───────────────═════

Всього: {len(tickets)}
Відкритих: {len([t for t in tickets if t['status'] == 'Відкритий'])}
"""
    
    await safe_edit(callback, text, tickets_list_kb(tickets, is_admin=True))

@router.callback_query(F.data.startswith("tickets_filter:"))
async def tickets_filter(callback: CallbackQuery):
    """Фільтр тікетів"""
    status = callback.data.split(":")[1]
    
    async with get_session() as session:
        tickets = await support_service.get_tickets(session, status=status)
    
    status_name = support_service.STATUSES.get(status, {}).get('name', status)
    
    text = f"""
📋 <b>ТІКЕТИ: {status_name.upper()}</b>
───────────────═════

Знайдено: {len(tickets)}
"""
    
    await safe_edit(callback, text, tickets_list_kb(tickets, is_admin=True))

@router.callback_query(F.data.startswith("ticket_view:"))
async def ticket_view(callback: CallbackQuery):
    """Перегляд тікета"""
    ticket_id = int(callback.data.split(":")[1])
    user_id = str(callback.from_user.id)
    
    async with get_session() as session:
        ticket = await support_service.get_ticket(session, ticket_id)
    
    if not ticket:
        await callback.answer("Тікет не знайдено", show_alert=True)
        return
    
    is_admin_user = False
    
    messages_text = ""
    for msg in ticket['messages'][-5:]:
        role_icon = "👤" if msg['sender_role'] == "user" else "👨‍💼"
        messages_text += f"\n{role_icon} <i>{msg['created_at']}</i>\n{msg['message'][:200]}...\n"
    
    text = f"""
🎫 <b>ТІКЕТ {ticket['ticket_code']}</b>
───────────────═════

📋 Тема: {ticket['subject']}
📁 Категорія: {ticket['category_name']}
⚡ Пріоритет: {ticket['priority_name']}
🔄 Статус: {ticket['status_name']}
📅 Створено: {ticket['created_at']}

<b>ПОВІДОМЛЕННЯ:</b>
{messages_text}
"""
    
    await safe_edit(callback, text, ticket_view_kb(ticket_id, ticket['status'], is_admin_user))

@router.callback_query(F.data.startswith("ticket_reply:"))
async def ticket_reply(callback: CallbackQuery, state: FSMContext):
    """Відповідь на тікет"""
    ticket_id = int(callback.data.split(":")[1])
    
    await state.update_data(ticket_id=ticket_id)
    await state.set_state(TicketStates.waiting_reply)
    
    await callback.message.edit_text(
        "💬 Введіть вашу відповідь:",
        reply_markup=None
    )

@router.message(TicketStates.waiting_reply)
async def ticket_reply_received(message: Message, state: FSMContext):
    """Отримано відповідь"""
    data = await state.get_data()
    ticket_id = data['ticket_id']
    user_id = str(message.from_user.id)
    user_role = "user"
    
    async with get_session() as session:
        await support_service.add_message(
            session,
            ticket_id=ticket_id,
            sender_id=user_id,
            sender_role=user_role,
            message=message.text
        )
    
    await state.clear()
    
    await message.answer("✅ Відповідь додано до тікета", reply_markup=support_menu_kb())

@router.callback_query(F.data.startswith("ticket_assign:"))
async def ticket_assign(callback: CallbackQuery):
    """Взяти тікет в роботу"""
    ticket_id = int(callback.data.split(":")[1])
    admin_id = str(callback.from_user.id)
    
    async with get_session() as session:
        await support_service.assign_ticket(session, ticket_id, admin_id)
    
    await callback.answer("✅ Тікет призначено вам", show_alert=True)

@router.callback_query(F.data.startswith("ticket_status:"))
async def ticket_status(callback: CallbackQuery):
    """Зміна статусу тікета"""
    ticket_id = int(callback.data.split(":")[1])
    
    text = """
🔄 <b>ЗМІНИТИ СТАТУС</b>
───────────────═════

Виберіть новий статус:
"""
    await safe_edit(callback, text, ticket_status_kb(ticket_id))

@router.callback_query(F.data.startswith("ticket_set_status:"))
async def ticket_set_status(callback: CallbackQuery):
    """Встановлення статусу"""
    parts = callback.data.split(":")
    ticket_id = int(parts[1])
    status = parts[2]
    
    async with get_session() as session:
        await support_service.update_status(session, ticket_id, status)
    
    status_name = support_service.STATUSES.get(status, {}).get('name', status)
    await callback.answer(f"✅ Статус змінено на: {status_name}", show_alert=True)

@router.callback_query(F.data.startswith("ticket_rate:"))
async def ticket_rate(callback: CallbackQuery):
    """Оцінка тікета"""
    ticket_id = int(callback.data.split(":")[1])
    
    text = """
⭐ <b>ОЦІНІТЬ ПІДТРИМКУ</b>
───────────────═════

Як ви оцінюєте якість наданої підтримки?
"""
    await safe_edit(callback, text, ticket_rating_kb(ticket_id))

@router.callback_query(F.data.startswith("ticket_rating:"))
async def ticket_rating(callback: CallbackQuery):
    """Встановлення оцінки"""
    parts = callback.data.split(":")
    ticket_id = int(parts[1])
    rating = int(parts[2])
    
    async with get_session() as session:
        await support_service.rate_ticket(session, ticket_id, rating)
    
    await callback.answer(f"✅ Дякуємо за оцінку: {'⭐' * rating}", show_alert=True)
    await support_menu(callback, FSMContext)

@router.callback_query(F.data == "tickets_stats")
async def tickets_stats(callback: CallbackQuery):
    """Статистика тікетів"""
    async with get_session() as session:
        stats = await support_service.get_stats(session)
    
    text = f"""
📊 <b>СТАТИСТИКА ТІКЕТІВ</b>
───────────────═════

📂 Відкриті: {stats['open']}
🔄 В роботі: {stats['in_progress']}
⏳ Очікують: {stats['waiting']}
✅ Вирішені: {stats['resolved']}
📁 Закриті: {stats['closed']}

📈 Всього: {stats['total']}
"""
    
    await safe_edit(callback, text, support_menu_kb(is_admin=True))

support_router = router
