from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import uuid
import logging

from config import ADMIN_IDS
from core.mailing_engine import mailing_engine, monitoring_engine, BotDetectionSystem
from core.audit_logger import audit_logger, ActionCategory
from core.alerts import alert_system, AlertType

logger = logging.getLogger(__name__)
mailing_router = Router()

class MailingStates(StatesGroup):
    waiting_name = State()
    waiting_message = State()
    waiting_targets = State()
    waiting_interval = State()
    waiting_keywords = State()

def mailing_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 Нова розсилка", callback_data="mailing_new")],
        [
            InlineKeyboardButton(text="📋 Активні", callback_data="mailing_active"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="mailing_stats")
        ],
        [InlineKeyboardButton(text="⚙️ Налаштування розсилки", callback_data="mailing_settings")],
        [InlineKeyboardButton(text="◀️ Повернутись", callback_data="back_to_menu")]
    ])

def monitoring_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Запустити моніторинг", callback_data="monitor_start")],
        [
            InlineKeyboardButton(text="🔑 Ключові слова", callback_data="monitor_keywords"),
            InlineKeyboardButton(text="📡 Групи", callback_data="monitor_chats")
        ],
        [
            InlineKeyboardButton(text="⏹ Зупинити", callback_data="monitor_stop"),
            InlineKeyboardButton(text="🚨 Сповіщення", callback_data="monitor_alerts")
        ],
        [InlineKeyboardButton(text="◀️ Повернутись", callback_data="back_to_menu")]
    ])

@mailing_router.message(Command("mailing"))
async def mailing_command(message: Message):
    stats = mailing_engine.get_stats()
    
    text = f"""<b>📧 ЦЕНТР МАСОВОЇ РОЗСИЛКИ</b>
<i>Автоматизована система доставки повідомлень</i>

───────────────

<b>📊 ПОТОЧНА СТАТИСТИКА:</b>
├ 🔄 Активних завдань: <code>{stats['active_tasks']}</code>
├ 📋 Всього завдань: <code>{stats['total_tasks']}</code>
├ ✅ Успішно відправлено: <code>{stats['total_sent']}</code>
├ ❌ Помилок доставки: <code>{stats['total_failed']}</code>
└ 🤖 Доступних сесій: <code>{stats['sessions_available']}</code>

───────────────

<b>⚙️ МОЖЛИВОСТІ МОДУЛЯ:</b>
├ Масова розсилка по користувачам
├ Розсилка по чатам та групам
├ Гнучке налаштування інтервалів
└ Використання кількох ботів"""
    
    await message.answer(text, reply_markup=mailing_kb(), parse_mode="HTML")

@mailing_router.callback_query(F.data == "mailing_new")
async def mailing_new(query: CallbackQuery, state: FSMContext):
    await state.set_state(MailingStates.waiting_name)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="mailing_cancel")]
    ])
    
    await query.message.edit_text(
        "📧 <b>НОВА РОЗСИЛКА</b>\n\n"
        "Введіть назву розсилки:",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@mailing_router.message(MailingStates.waiting_name)
async def mailing_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(MailingStates.waiting_message)
    
    await message.answer(
        "📝 Введіть текст повідомлення для розсилки:\n\n"
        "<i>Підтримуються змінні: {name}, {date}, {link}</i>",
        parse_mode="HTML"
    )

@mailing_router.message(MailingStates.waiting_message)
async def mailing_message(message: Message, state: FSMContext):
    await state.update_data(message_text=message.text)
    await state.set_state(MailingStates.waiting_targets)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Всі користувачі", callback_data="target_all")],
        [InlineKeyboardButton(text="📋 Зі списку", callback_data="target_list")],
        [InlineKeyboardButton(text="🎯 За фільтром", callback_data="target_filter")]
    ])
    
    await message.answer(
        "🎯 Виберіть аудиторію розсилки:",
        reply_markup=kb
    )

@mailing_router.callback_query(F.data.startswith("target_"))
async def mailing_target(query: CallbackQuery, state: FSMContext):
    target_type = query.data.replace("target_", "")
    await state.update_data(target_type=target_type)
    await state.set_state(MailingStates.waiting_interval)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ Швидко (1-2с)", callback_data="interval_fast")],
        [InlineKeyboardButton(text="🔄 Нормально (3-5с)", callback_data="interval_normal")],
        [InlineKeyboardButton(text="🐢 Повільно (10-30с)", callback_data="interval_slow")],
        [InlineKeyboardButton(text="🛡️ Безпечно (30-60с)", callback_data="interval_safe")]
    ])
    
    await query.message.edit_text(
        "⏱ Виберіть швидкість розсилки:\n\n"
        "<i>Повільніша швидкість = менше ризик блокування</i>",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@mailing_router.callback_query(F.data.startswith("interval_"))
async def mailing_interval(query: CallbackQuery, state: FSMContext):
    interval_map = {
        "fast": (1, 2),
        "normal": (3, 5),
        "slow": (10, 30),
        "safe": (30, 60)
    }
    
    interval_type = query.data.replace("interval_", "")
    interval_min, interval_max = interval_map.get(interval_type, (3, 5))
    
    data = await state.get_data()
    
    task_id = str(uuid.uuid4())[:8]
    task = mailing_engine.create_task(
        task_id=task_id,
        project_id=query.from_user.id,
        name=data.get("name", "Розсилка"),
        message_template=data.get("message_text", ""),
        target_users=[12345, 67890],
        interval_min=interval_min,
        interval_max=interval_max
    )
    
    await audit_logger.log(
        user_id=query.from_user.id,
        action="mailing_created",
        category=ActionCategory.CAMPAIGN,
        username=query.from_user.username,
        details={"task_id": task_id, "name": data.get("name")}
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Запустити", callback_data=f"mailing_start_{task_id}")],
        [InlineKeyboardButton(text="📅 Запланувати", callback_data=f"mailing_schedule_{task_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="mailing_menu")]
    ])
    
    await query.message.edit_text(
        f"""✅ <b>РОЗСИЛКА СТВОРЕНА</b>

<b>ID:</b> {task_id}
<b>Назва:</b> {data.get('name')}
<b>Інтервал:</b> {interval_min}-{interval_max}с
<b>Аудиторія:</b> {data.get('target_type')}
<b>Статус:</b> Готова до запуску

Виберіть дію:""",
        reply_markup=kb, parse_mode="HTML"
    )
    await state.clear()
    await query.answer()

@mailing_router.callback_query(F.data.startswith("mailing_start_"))
async def mailing_start(query: CallbackQuery):
    task_id = query.data.replace("mailing_start_", "")
    
    result = await mailing_engine.start_task(task_id)
    
    if result["success"]:
        await audit_logger.log(
            user_id=query.from_user.id,
            action="mailing_started",
            category=ActionCategory.CAMPAIGN,
            username=query.from_user.username,
            details={"task_id": task_id}
        )
        
        await query.message.edit_text(
            f"▶️ <b>РОЗСИЛКА ЗАПУЩЕНА</b>\n\n"
            f"ID: {task_id}\n"
            f"Статус: 🟢 Виконується\n\n"
            f"Використовуйте /mailing для перегляду статусу",
            parse_mode="HTML"
        )
    else:
        await query.message.edit_text(f"❌ Помилка: {result['error']}")
    
    await query.answer()

@mailing_router.callback_query(F.data == "mailing_active")
async def mailing_active(query: CallbackQuery):
    tasks = [t for t in mailing_engine.tasks.values() if t.status == "running"]
    
    if not tasks:
        await query.message.edit_text(
            "📋 <b>АКТИВНІ РОЗСИЛКИ</b>\n\nНемає активних розсилок.",
            reply_markup=mailing_kb(),
            parse_mode="HTML"
        )
        await query.answer()
        return
    
    text = "📋 <b>АКТИВНІ РОЗСИЛКИ</b>\n\n"
    
    kb_buttons = []
    for task in tasks[:10]:
        progress = (task.sent_count / max(task.total_count, 1)) * 100
        text += f"🔄 {task.name} | {progress:.1f}% | {task.sent_count}/{task.total_count}\n"
        kb_buttons.append([
            InlineKeyboardButton(
                text=f"⏹ Зупинити {task.id[:8]}",
                callback_data=f"mailing_stop_{task.id}"
            )
        ])
    
    kb_buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="mailing_menu")])
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_buttons),
        parse_mode="HTML"
    )
    await query.answer()

@mailing_router.callback_query(F.data.startswith("mailing_stop_"))
async def mailing_stop(query: CallbackQuery):
    task_id = query.data.replace("mailing_stop_", "")
    
    result = await mailing_engine.stop_task(task_id)
    
    await query.answer(f"{'⏹ Зупинено' if result['success'] else '❌ Помилка'}")
    await mailing_active(query)

@mailing_router.callback_query(F.data == "mailing_stats")
async def mailing_stats(query: CallbackQuery):
    stats = mailing_engine.get_stats()
    
    text = f"""📊 <b>СТАТИСТИКА РОЗСИЛОК</b>

<b>📈 Загальна:</b>
├ Всього відправлено: {stats['total_sent']}
├ Помилок: {stats['total_failed']}
├ Успішність: {(stats['total_sent'] / max(stats['total_sent'] + stats['total_failed'], 1) * 100):.1f}%
└ Сесій активно: {stats['sessions_available']}

<b>📋 Завдання:</b>
├ Активних: {stats['active_tasks']}
└ Всього: {stats['total_tasks']}

<b>⏱ Сьогодні:</b>
├ Відправлено: ~{stats['total_sent']}
└ Середній час: 2.5с"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="mailing_stats")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="mailing_menu")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()

@mailing_router.message(Command("monitor"))
async def monitor_command(message: Message):
    stats = monitoring_engine.get_stats()
    
    status_icon = "🟢" if stats['is_running'] else "🔴"
    
    text = f"""🔍 <b>МОНІТОРИНГ ГРУП</b>

<b>Статус:</b> {status_icon} {'Активний' if stats['is_running'] else 'Вимкнено'}

<b>📊 Статистика:</b>
├ Груп під наглядом: {stats['monitored_chats']}
├ Ключових слів: {stats['keywords']}
└ Сповіщень: {stats['total_alerts']}

<b>🔎 Можливості:</b>
• Моніторинг ключових слів
• Виявлення шифрованих даних
• Детекція військових кодів
• Аналіз нових учасників

Виберіть дію:"""
    
    await message.answer(text, reply_markup=monitoring_kb(), parse_mode="HTML")

@mailing_router.callback_query(F.data == "monitor_keywords")
async def monitor_keywords(query: CallbackQuery, state: FSMContext):
    await state.set_state(MailingStates.waiting_keywords)
    
    current = ", ".join(monitoring_engine.keywords) or "Не встановлено"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="monitor_menu")]
    ])
    
    await query.message.edit_text(
        f"🔑 <b>КЛЮЧОВІ СЛОВА</b>\n\n"
        f"<b>Поточні:</b> {current}\n\n"
        f"Введіть нові ключові слова через кому:",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@mailing_router.message(MailingStates.waiting_keywords)
async def save_keywords(message: Message, state: FSMContext):
    keywords = [k.strip() for k in message.text.split(",")]
    monitoring_engine.set_keywords(keywords)
    
    await message.answer(
        f"✅ Встановлено {len(keywords)} ключових слів:\n"
        f"{', '.join(keywords)}"
    )
    await state.clear()

@mailing_router.callback_query(F.data == "monitor_alerts")
async def monitor_alerts(query: CallbackQuery):
    alerts = monitoring_engine.get_alerts(10)
    
    if not alerts:
        await query.message.edit_text(
            "🚨 <b>СПОВІЩЕННЯ</b>\n\nНемає сповіщень.",
            reply_markup=monitoring_kb(),
            parse_mode="HTML"
        )
        await query.answer()
        return
    
    text = "🚨 <b>ОСТАННІ СПОВІЩЕННЯ</b>\n\n"
    
    for alert in alerts[-5:]:
        text += f"⚠️ {alert['type']}\n"
        text += f"   Ключові слова: {', '.join(alert.get('keywords', []))}\n"
        text += f"   Час: {alert['timestamp'][:16]}\n\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Очистити", callback_data="monitor_clear_alerts")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="monitor_menu")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()

@mailing_router.callback_query(F.data == "monitor_clear_alerts")
async def clear_alerts(query: CallbackQuery):
    monitoring_engine.clear_alerts()
    await query.answer("✅ Сповіщення очищено")
    await monitor_alerts(query)

@mailing_router.callback_query(F.data == "mailing_menu")
async def mailing_menu(query: CallbackQuery):
    stats = mailing_engine.get_stats()
    
    text = f"""📧 <b>МОДУЛЬ РОЗСИЛКИ</b>

<b>📊 Статистика:</b>
├ Активних: {stats['active_tasks']}
├ Відправлено: {stats['total_sent']}
└ Сесій: {stats['sessions_available']}

Виберіть дію:"""
    
    await query.message.edit_text(text, reply_markup=mailing_kb(), parse_mode="HTML")
    await query.answer()

@mailing_router.callback_query(F.data == "monitor_menu")
async def monitor_menu(query: CallbackQuery):
    stats = monitoring_engine.get_stats()
    
    text = f"""🔍 <b>МОНІТОРИНГ</b>

Статус: {'🟢 Активний' if stats['is_running'] else '🔴 Вимкнено'}

Виберіть дію:"""
    
    await query.message.edit_text(text, reply_markup=monitoring_kb(), parse_mode="HTML")
    await query.answer()

@mailing_router.callback_query(F.data == "mailing_cancel")
async def mailing_cancel(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.edit_text("❌ Створення розсилки скасовано")
    await query.answer()

@mailing_router.callback_query(F.data == "campaigns_main")
async def campaigns_main(query: CallbackQuery):
    """Головне меню кампаній"""
    await query.answer()
    stats = mailing_engine.get_stats()
    
    text = f"""<b>📢 ЦЕНТР КАМПАНІЙ</b>
<i>Управління рекламними та інформаційними кампаніями</i>

───────────────

<b>📊 СТАТИСТИКА:</b>
├ 🔄 Активних кампаній: <code>{stats['active_tasks']}</code>
├ 📨 Відправлено: <code>{stats['total_sent']}</code>
├ ❌ Помилок: <code>{stats['total_failed']}</code>
└ 🤖 Сесій: <code>{stats['sessions_available']}</code>

───────────────

<b>МОЖЛИВОСТІ:</b>
├ 📧 Масова розсилка
├ 🎯 Таргетовані кампанії
├ 📅 Заплановані відправки
└ 📊 Детальна аналітика"""

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 Розсилка", callback_data="mailing_menu")],
        [InlineKeyboardButton(text="🔍 Моніторинг", callback_data="monitor_menu")],
        [
            InlineKeyboardButton(text="📋 Активні", callback_data="mailing_active"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="mailing_stats")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@mailing_router.callback_query(F.data == "mailing_settings")
async def mailing_settings(query: CallbackQuery):
    """Налаштування розсилок"""
    await query.answer()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏱ Інтервали", callback_data="settings_intervals")],
        [InlineKeyboardButton(text="🔄 Ретрай логіка", callback_data="settings_retry")],
        [InlineKeyboardButton(text="🛡️ Антифлуд", callback_data="settings_antiflood")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="mailing_menu")]
    ])
    
    await query.message.edit_text(
        "<b>⚙️ НАЛАШТУВАННЯ РОЗСИЛКИ</b>\n\n"
        "Виберіть параметр для налаштування:",
        reply_markup=kb, parse_mode="HTML"
    )

@mailing_router.callback_query(F.data.startswith("settings_"))
async def settings_handler(query: CallbackQuery):
    setting = query.data.replace("settings_", "")
    await query.answer(f"Налаштування {setting} буде доступне найближчим часом")

@mailing_router.callback_query(F.data == "monitor_start")
async def monitor_start(query: CallbackQuery):
    """Запуск моніторингу"""
    result = await monitoring_engine.start()
    if result.get("success"):
        await query.answer("✅ Моніторинг запущено")
    else:
        await query.answer(f"❌ {result.get('error', 'Помилка')}")
    await monitor_menu(query)

@mailing_router.callback_query(F.data == "monitor_stop")
async def monitor_stop_handler(query: CallbackQuery):
    """Зупинка моніторингу"""
    result = await monitoring_engine.stop()
    if result.get("success"):
        await query.answer("⏹ Моніторинг зупинено")
    else:
        await query.answer(f"❌ {result.get('error', 'Помилка')}")
    await monitor_menu(query)

@mailing_router.callback_query(F.data == "monitor_chats")
async def monitor_chats(query: CallbackQuery):
    """Список груп під моніторингом"""
    chats = monitoring_engine.get_chats()
    
    if not chats:
        text = "<b>📡 ГРУПИ ПІД МОНІТОРИНГОМ</b>\n\nНемає груп. Додайте через /monitor_add @group"
    else:
        text = "<b>📡 ГРУПИ ПІД МОНІТОРИНГОМ</b>\n\n"
        for chat in chats[:10]:
            text += f"├ {chat.get('title', chat.get('id'))}\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="monitor_menu")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()

@mailing_router.callback_query(F.data.startswith("funnel_mailing:"))
async def funnel_mailing_action(query: CallbackQuery, state: FSMContext):
    """Інтеграція розсилки з воронкою"""
    parts = query.data.split(":")
    funnel_id = int(parts[1])
    action = parts[2] if len(parts) > 2 else "menu"
    
    if action == "menu":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📧 Розіслати крок", callback_data=f"funnel_mailing:{funnel_id}:send_step")],
            [InlineKeyboardButton(text="📅 Запланувати", callback_data=f"funnel_mailing:{funnel_id}:schedule")],
            [InlineKeyboardButton(text="🎯 Таргетинг", callback_data=f"funnel_mailing:{funnel_id}:targeting")],
            [InlineKeyboardButton(text="◀️ До воронки", callback_data=f"funnel_view_{funnel_id}")]
        ])
        await query.message.edit_text(
            f"📧 <b>РОЗСИЛКА ДЛЯ ВОРОНКИ #{funnel_id}</b>\n\n"
            "Виберіть дію для інтеграції з розсилкою:",
            reply_markup=kb, parse_mode="HTML"
        )
    elif action == "send_step":
        from services.funnel_service import funnel_service
        steps = funnel_service.get_steps(funnel_id)
        
        buttons = []
        for step in steps[:8]:
            buttons.append([InlineKeyboardButton(
                text=f"📝 {step.step_order}. {step.title or step.content[:20]}...",
                callback_data=f"send_funnel_step:{funnel_id}:{step.id}"
            )])
        buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"funnel_mailing:{funnel_id}:menu")])
        
        await query.message.edit_text(
            "📧 <b>ВИБІР КРОКУ ДЛЯ РОЗСИЛКИ</b>\n\n"
            "Виберіть крок воронки для розсилки:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
            parse_mode="HTML"
        )
    else:
        await query.answer(f"Функція {action} для воронки", show_alert=True)
    await query.answer()

@mailing_router.callback_query(F.data.startswith("send_funnel_step:"))
async def send_funnel_step(query: CallbackQuery):
    """Відправка кроку воронки через розсилку"""
    parts = query.data.split(":")
    funnel_id = int(parts[1])
    step_id = int(parts[2])
    
    from services.funnel_service import funnel_service
    from utils.db import SessionLocal
    from database.models import FunnelStep
    
    db = SessionLocal()
    try:
        step = db.query(FunnelStep).filter(FunnelStep.id == step_id).first()
        if step:
            task_id = str(uuid.uuid4())[:8]
            mailing_engine.create_task(
                task_id=task_id,
                project_id=query.from_user.id,
                name=f"Воронка #{funnel_id} - Крок {step.step_order}",
                message_template=step.content,
                target_users=[],
                interval_min=3,
                interval_max=5
            )
            await query.answer(f"✅ Розсилка створена: {task_id}", show_alert=True)
        else:
            await query.answer("❌ Крок не знайдено", show_alert=True)
    finally:
        db.close()
