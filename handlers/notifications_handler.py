import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.notifications_kb import (
    notifications_menu_kb, notification_create_type_kb, notification_target_kb,
    notification_role_kb, notification_multi_role_kb, notification_priority_kb,
    notifications_list_kb, notification_view_kb, bans_menu_kb, ban_type_kb,
    ban_duration_kb, bans_list_kb, ban_view_kb, project_stats_kb
)
from services.notification_service import notification_service, ban_service, project_stats_service
from utils.db import get_session
from core.role_constants import UserRole

logger = logging.getLogger(__name__)

router = Router()

class NotificationStates(StatesGroup):
    waiting_title = State()
    waiting_message = State()
    waiting_user_ids = State()

class BanStates(StatesGroup):
    waiting_user_id = State()
    waiting_reason = State()

async def safe_edit(callback: CallbackQuery, text: str, reply_markup=None):
    """Безпечне редагування повідомлення"""
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception:
        await callback.answer()

def is_admin(user_role: str) -> bool:
    """Перевірка чи користувач адмін"""
    return user_role in [UserRole.ADMIN, UserRole.ROOT]

@router.callback_query(F.data == "notifications_menu")
async def notifications_menu(callback: CallbackQuery, state: FSMContext):
    """Головне меню сповіщень"""
    await state.clear()
    
    is_admin_user = False
    
    text = """
🔔 <b>СПОВІЩЕННЯ</b>
═══════════════════════════════

Керуйте системними сповіщеннями.
"""
    
    await safe_edit(callback, text, notifications_menu_kb(is_admin_user))

@router.callback_query(F.data == "notifications_my")
async def notifications_my(callback: CallbackQuery):
    """Мої сповіщення"""
    user_id = str(callback.from_user.id)
    user_role = "user"
    
    async with get_session() as session:
        notifications = await notification_service.get_notifications(
            session, user_id=user_id, user_role=user_role
        )
    
    if not notifications:
        await callback.answer("Сповіщень немає", show_alert=True)
        return
    
    unread = len([n for n in notifications if not n['is_read']])
    
    text = f"""
📬 <b>МОЇ СПОВІЩЕННЯ</b>
═══════════════════════════════

Всього: {len(notifications)}
Непрочитаних: {unread}
"""
    
    await safe_edit(callback, text, notifications_list_kb(notifications))

@router.callback_query(F.data == "notifications_unread")
async def notifications_unread(callback: CallbackQuery):
    """Непрочитані сповіщення"""
    user_id = str(callback.from_user.id)
    user_role = "user"
    
    async with get_session() as session:
        notifications = await notification_service.get_notifications(
            session, user_id=user_id, user_role=user_role, unread_only=True
        )
    
    if not notifications:
        await callback.answer("Всі сповіщення прочитані", show_alert=True)
        return
    
    text = f"""
🔔 <b>НЕПРОЧИТАНІ СПОВІЩЕННЯ</b>
═══════════════════════════════

Знайдено: {len(notifications)}
"""
    
    await safe_edit(callback, text, notifications_list_kb(notifications))

@router.callback_query(F.data.startswith("notif_view:"))
async def notification_view(callback: CallbackQuery):
    """Перегляд сповіщення"""
    notif_id = int(callback.data.split(":")[1])
    user_id = str(callback.from_user.id)
    
    async with get_session() as session:
        notifications = await notification_service.get_notifications(session, user_id=user_id)
        notif = next((n for n in notifications if n['id'] == notif_id), None)
        
        if notif:
            await notification_service.mark_as_read(session, notif_id, user_id)
    
    if not notif:
        await callback.answer("Сповіщення не знайдено", show_alert=True)
        return
    
    text = f"""
{notif['type_icon']} <b>{notif['title']}</b>
═══════════════════════════════

{notif['message']}

📅 {notif['created_at']}
"""
    
    await safe_edit(callback, text, notification_view_kb(notif_id))

@router.callback_query(F.data == "notifications_read_all")
async def notifications_read_all(callback: CallbackQuery):
    """Позначити все як прочитане"""
    user_id = str(callback.from_user.id)
    
    async with get_session() as session:
        notifications = await notification_service.get_notifications(
            session, user_id=user_id, unread_only=True
        )
        
        for n in notifications:
            await notification_service.mark_as_read(session, n['id'], user_id)
    
    await callback.answer("✅ Всі сповіщення прочитані", show_alert=True)

@router.callback_query(F.data == "notification_create")
async def notification_create(callback: CallbackQuery):
    """Створення сповіщення"""
    text = """
📢 <b>НОВЕ СПОВІЩЕННЯ</b>
═══════════════════════════════

Виберіть тип сповіщення:
"""
    await safe_edit(callback, text, notification_create_type_kb())

@router.callback_query(F.data.startswith("notif_type:"))
async def notification_type(callback: CallbackQuery):
    """Вибір типу - вибір аудиторії"""
    notif_type = callback.data.split(":")[1]
    
    type_info = notification_service.TYPES.get(notif_type, {})
    
    text = f"""
{type_info.get('icon', 'ℹ️')} <b>{type_info.get('name', notif_type).upper()}</b>
═══════════════════════════════

Кому надіслати сповіщення?
"""
    await safe_edit(callback, text, notification_target_kb(notif_type))

@router.callback_query(F.data.startswith("notif_target:"))
async def notification_target(callback: CallbackQuery, state: FSMContext):
    """Вибір цільової аудиторії"""
    parts = callback.data.split(":")
    notif_type = parts[1]
    target = parts[2]
    
    await state.update_data(notif_type=notif_type, target_type=target)
    
    if target == 'role':
        text = """
👔 <b>ВИБІР РОЛІ</b>
═══════════════════════════════

Виберіть роль для надсилання:
"""
        await safe_edit(callback, text, notification_role_kb(notif_type))
    
    elif target == 'multi_role':
        text = """
👥 <b>ВИБІР РОЛЕЙ</b>
═══════════════════════════════

Виберіть одну або декілька ролей:
"""
        await safe_edit(callback, text, notification_multi_role_kb(notif_type))
    
    elif target == 'personal':
        await state.set_state(NotificationStates.waiting_user_ids)
        await callback.message.edit_text(
            "👤 Введіть Telegram ID користувачів через кому:",
            reply_markup=None
        )
    
    else:
        text = """
⚡ <b>ПРІОРИТЕТ</b>
═══════════════════════════════

Виберіть пріоритет сповіщення:
"""
        await safe_edit(callback, text, notification_priority_kb(notif_type, target))

@router.callback_query(F.data.startswith("notif_role:"))
async def notification_role(callback: CallbackQuery, state: FSMContext):
    """Вибрано роль"""
    parts = callback.data.split(":")
    notif_type = parts[1]
    role = parts[2]
    
    await state.update_data(target_roles=[role])
    
    text = """
⚡ <b>ПРІОРИТЕТ</b>
═══════════════════════════════

Виберіть пріоритет сповіщення:
"""
    await safe_edit(callback, text, notification_priority_kb(notif_type, 'role'))

@router.callback_query(F.data.startswith("notif_multi_toggle:"))
async def notification_multi_toggle(callback: CallbackQuery, state: FSMContext):
    """Переключення ролі"""
    parts = callback.data.split(":")
    notif_type = parts[1]
    role = parts[2]
    
    data = await state.get_data()
    selected = data.get('target_roles', [])
    
    if role in selected:
        selected.remove(role)
    else:
        selected.append(role)
    
    await state.update_data(target_roles=selected)
    
    text = f"""
👥 <b>ВИБІР РОЛЕЙ</b>
═══════════════════════════════

Обрано: {len(selected)}
"""
    await safe_edit(callback, text, notification_multi_role_kb(notif_type, selected))

@router.callback_query(F.data.startswith("notif_multi_done:"))
async def notification_multi_done(callback: CallbackQuery, state: FSMContext):
    """Завершено вибір ролей"""
    notif_type = callback.data.split(":")[1]
    data = await state.get_data()
    
    if not data.get('target_roles'):
        await callback.answer("Виберіть хоча б одну роль", show_alert=True)
        return
    
    text = """
⚡ <b>ПРІОРИТЕТ</b>
═══════════════════════════════

Виберіть пріоритет сповіщення:
"""
    await safe_edit(callback, text, notification_priority_kb(notif_type, 'multi_role'))

@router.callback_query(F.data.startswith("notif_pri:"))
async def notification_priority(callback: CallbackQuery, state: FSMContext):
    """Вибрано пріоритет - введення заголовку"""
    parts = callback.data.split(":")
    priority = parts[3] if len(parts) > 3 else parts[2]
    
    await state.update_data(priority=priority)
    await state.set_state(NotificationStates.waiting_title)
    
    await callback.message.edit_text(
        "📝 Введіть заголовок сповіщення:",
        reply_markup=None
    )

@router.message(NotificationStates.waiting_title)
async def notification_title_received(message: Message, state: FSMContext):
    """Отримано заголовок - введення тексту"""
    await state.update_data(title=message.text)
    await state.set_state(NotificationStates.waiting_message)
    
    await message.answer("📄 Введіть текст сповіщення:")

@router.message(NotificationStates.waiting_message)
async def notification_message_received(message: Message, state: FSMContext):
    """Отримано текст - створення сповіщення"""
    data = await state.get_data()
    sender_id = str(message.from_user.id)
    
    async with get_session() as session:
        result = await notification_service.create_notification(
            session,
            sender_id=sender_id,
            title=data['title'],
            message=message.text,
            notification_type=data.get('notif_type', 'info'),
            target_type=data.get('target_type', 'all'),
            target_roles=data.get('target_roles', []),
            target_user_ids=data.get('target_user_ids', []),
            priority=data.get('priority', 'normal')
        )
        
        send_result = await notification_service.send_notification(session, result['id'])
    
    await state.clear()
    
    await message.answer(f"""
✅ <b>СПОВІЩЕННЯ НАДІСЛАНО</b>
═══════════════════════════════

📋 Заголовок: {result['title']}
📤 Надіслано: {send_result.get('sent', 0)}
❌ Помилок: {send_result.get('failed', 0)}
""", reply_markup=notifications_menu_kb(is_admin=True), parse_mode="HTML")

@router.callback_query(F.data == "bans_menu")
async def bans_menu(callback: CallbackQuery, state: FSMContext):
    """Меню банів"""
    await state.clear()
    
    text = """
🚫 <b>УПРАВЛІННЯ БАНАМИ</b>
═══════════════════════════════

Система блокування користувачів.
"""
    
    await safe_edit(callback, text, bans_menu_kb())

@router.callback_query(F.data == "ban_user")
async def ban_user(callback: CallbackQuery):
    """Бан користувача - вибір типу"""
    text = """
🚫 <b>ЗАБЛОКУВАТИ КОРИСТУВАЧА</b>
═══════════════════════════════

Виберіть тип блокування:
"""
    await safe_edit(callback, text, ban_type_kb())

@router.callback_query(F.data.startswith("ban_type:"))
async def ban_type(callback: CallbackQuery, state: FSMContext):
    """Вибрано тип бану"""
    ban_type = callback.data.split(":")[1]
    
    await state.update_data(ban_type=ban_type)
    
    if ban_type == 'temporary':
        text = """
⏱ <b>ТРИВАЛІСТЬ БАНУ</b>
═══════════════════════════════

На скільки заблокувати?
"""
        await safe_edit(callback, text, ban_duration_kb(ban_type))
    else:
        await state.set_state(BanStates.waiting_user_id)
        await callback.message.edit_text(
            "👤 Введіть Telegram ID користувача:",
            reply_markup=None
        )

@router.callback_query(F.data.startswith("ban_dur:"))
async def ban_duration(callback: CallbackQuery, state: FSMContext):
    """Вибрано тривалість"""
    parts = callback.data.split(":")
    hours = int(parts[2])
    
    await state.update_data(duration_hours=hours)
    await state.set_state(BanStates.waiting_user_id)
    
    await callback.message.edit_text(
        "👤 Введіть Telegram ID користувача:",
        reply_markup=None
    )

@router.message(BanStates.waiting_user_id)
async def ban_user_id_received(message: Message, state: FSMContext):
    """Отримано ID - введення причини"""
    await state.update_data(user_id=message.text)
    await state.set_state(BanStates.waiting_reason)
    
    await message.answer("📝 Введіть причину блокування:")

@router.message(BanStates.waiting_reason)
async def ban_reason_received(message: Message, state: FSMContext):
    """Отримано причину - створення бану"""
    data = await state.get_data()
    banned_by = str(message.from_user.id)
    
    async with get_session() as session:
        result = await ban_service.ban_user(
            session,
            user_id=data['user_id'],
            banned_by=banned_by,
            reason=message.text,
            ban_type=data.get('ban_type', 'temporary'),
            duration_hours=data.get('duration_hours')
        )
    
    await state.clear()
    
    await message.answer(f"""
🚫 <b>КОРИСТУВАЧА ЗАБЛОКОВАНО</b>
═══════════════════════════════

👤 ID: {result['user_id']}
📋 Тип: {result['ban_type']}
⏱ До: {result['expires_at']}
""", reply_markup=bans_menu_kb(), parse_mode="HTML")

@router.callback_query(F.data == "bans_active")
async def bans_active(callback: CallbackQuery):
    """Активні бани"""
    async with get_session() as session:
        bans = await ban_service.get_all_bans(session, active_only=True)
    
    if not bans:
        await callback.answer("Активних банів немає", show_alert=True)
        return
    
    text = f"""
🚫 <b>АКТИВНІ БАНИ</b>
═══════════════════════════════

Всього: {len(bans)}
"""
    
    await safe_edit(callback, text, bans_list_kb(bans))

@router.callback_query(F.data.startswith("ban_view:"))
async def ban_view(callback: CallbackQuery):
    """Перегляд бану"""
    ban_id = int(callback.data.split(":")[1])
    
    async with get_session() as session:
        bans = await ban_service.get_all_bans(session)
        ban = next((b for b in bans if b['id'] == ban_id), None)
    
    if not ban:
        await callback.answer("Бан не знайдено", show_alert=True)
        return
    
    text = f"""
🚫 <b>ДЕТАЛІ БАНУ</b>
═══════════════════════════════

👤 Користувач: {ban['user_id']}
📋 Тип: {ban['ban_type']}
📝 Причина: {ban['reason']}
📅 Створено: {ban['created_at']}
⏱ До: {ban['expires_at']}
"""
    
    await safe_edit(callback, text, ban_view_kb(ban_id, ban['user_id']))

@router.callback_query(F.data.startswith("unban:"))
async def unban(callback: CallbackQuery):
    """Розбан користувача"""
    user_id = callback.data.split(":")[1]
    
    async with get_session() as session:
        await ban_service.unban_user(session, user_id)
    
    await callback.answer("✅ Користувача розблоковано", show_alert=True)
    await bans_active(callback)

@router.callback_query(F.data == "project_stats")
async def project_stats_main(callback: CallbackQuery):
    """Головне меню статистики проектів"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    text = """
📊 <b>СТАТИСТИКА ПРОЕКТІВ</b>
═══════════════════════════════

Аналітика по всіх проектах системи.

<b>Доступні метрики:</b>
├ 📨 Надіслано повідомлень
├ ✅ Доставлено / ❌ Помилок
├ 👥 Нових користувачів
├ 🤖 Активних ботів
├ 🚀 Запущених кампаній
└ 🔍 OSINT звітів

Виберіть період для перегляду:
"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📅 Сьогодні", callback_data="stats_period:1:1"),
            InlineKeyboardButton(text="📅 7 днів", callback_data="stats_period:1:7")
        ],
        [
            InlineKeyboardButton(text="📅 30 днів", callback_data="stats_period:1:30"),
            InlineKeyboardButton(text="📅 90 днів", callback_data="stats_period:1:90")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])
    
    await safe_edit(callback, text, kb)

@router.callback_query(F.data.startswith("stats_period:"))
async def stats_period(callback: CallbackQuery):
    """Статистика за період"""
    parts = callback.data.split(":")
    project_id = int(parts[1])
    days = int(parts[2])
    
    async with get_session() as session:
        stats = await project_stats_service.get_project_stats(session, project_id, days)
    
    if not stats:
        await callback.answer("Проект не знайдено", show_alert=True)
        return
    
    text = f"""
📊 <b>СТАТИСТИКА: {stats['project_name']}</b>
═══════════════════════════════

📅 Період: {days} днів

<b>ПОВІДОМЛЕННЯ:</b>
├ Надіслано: {stats['totals']['messages_sent']}
├ Доставлено: {stats['totals']['messages_delivered']}
├ Помилок: {stats['totals']['messages_failed']}
└ Доставляємість: {stats['delivery_rate']}%

<b>РЕСУРСИ:</b>
├ Менеджерів: {stats['managers_count']}
├ Кампаній: {stats['campaigns_count']}
└ Ботів: {stats['bots_used']}/{stats['bots_limit']}

<b>АКТИВНІСТЬ:</b>
├ Нових користувачів: {stats['totals']['new_users']}
└ OSINT звітів: {stats['totals']['osint_reports']}
"""
    
    await safe_edit(callback, text, project_stats_kb(project_id))

notifications_router = router
