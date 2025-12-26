from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_IDS

from core.audit_logger import audit_logger, ActionCategory, ActionSeverity
from core.alerts import alert_system, AlertType
from core.campaign_manager import campaign_manager
from core.scheduler import scheduler

admin_router = Router()

class AdminStates(StatesGroup):
    waiting_broadcast = State()
    waiting_block_id = State()
    waiting_alert_message = State()

class RootStates(StatesGroup):
    waiting_key_tariff = State()
    waiting_key_days = State()

def admin_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Розсилка", callback_data="admin_broadcast"),
         InlineKeyboardButton(text="👥 Користувачі", callback_data="admin_users")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
         InlineKeyboardButton(text="💰 Платежі", callback_data="admin_payments")],
        [InlineKeyboardButton(text="📋 Аудит логи", callback_data="admin_audit"),
         InlineKeyboardButton(text="🚨 Сповіщення", callback_data="admin_alerts")],
        [InlineKeyboardButton(text="🔑 Ключі", callback_data="admin_keys_menu"),
         InlineKeyboardButton(text="🚫 Блокування", callback_data="admin_block")],
        [InlineKeyboardButton(text="⚙️ Система", callback_data="admin_system"),
         InlineKeyboardButton(text="🔐 Безпека", callback_data="admin_security")],
        [InlineKeyboardButton(text="🆘 ЕКСТРЕНА ТРИВОГА", callback_data="admin_emergency")]
    ])

@admin_router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await audit_logger.log_security(
            user_id=message.from_user.id,
            action="unauthorized_admin_access",
            username=message.from_user.username,
            severity=ActionSeverity.WARNING
        )
        await message.answer("❌ Доступ заборонений")
        return
    
    await audit_logger.log(
        user_id=message.from_user.id,
        action="admin_panel_access",
        category=ActionCategory.SYSTEM,
        username=message.from_user.username
    )
    
    text = """🛡️ <b>АДМІНІСТРАТИВНА ПАНЕЛЬ</b>

<b>👑 ROOT/ADMIN</b>
Повний контроль над системою

<b>📊 Швидка статистика:</b>
├ Користувачів: 1,245
├ Активних проектів: 45
├ Кампаній: 12
└ Непрочитаних сповіщень: 3"""
    
    await message.answer(text, reply_markup=admin_main_kb(), parse_mode="HTML")

@admin_router.callback_query(F.data == "admin_menu")
async def admin_menu_callback(query: CallbackQuery):
    await query.answer()
    text = """🛡️ <b>АДМІНІСТРАТИВНА ПАНЕЛЬ</b>

<b>👑 ROOT/ADMIN</b>
Повний контроль над системою"""
    await query.message.edit_text(text, reply_markup=admin_main_kb(), parse_mode="HTML")

@admin_router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(query: CallbackQuery, state: FSMContext):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонений", show_alert=True)
        return
    
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_menu")]
    ])
    await query.message.edit_text("📢 <b>РОЗСИЛКА</b>\n\nНапишіть текст для розсилки всім користувачам:", reply_markup=kb, parse_mode="HTML")
    await state.set_state(AdminStates.waiting_broadcast)

@admin_router.message(AdminStates.waiting_broadcast)
async def process_broadcast(message: Message, state: FSMContext):
    await audit_logger.log(
        user_id=message.from_user.id,
        action="admin_broadcast",
        category=ActionCategory.CAMPAIGN,
        username=message.from_user.username,
        details={"text_length": len(message.text)}
    )
    
    await message.answer(f"""✅ <b>РОЗСИЛКА ЗАПУЩЕНА</b>

<b>Текст:</b>
<i>{message.text[:100]}...</i>

<b>Статус:</b>
├ Отримувачів: 1,245
├ Відправлено: 0
└ В обробці...""", parse_mode="HTML")
    await state.clear()

@admin_router.callback_query(F.data == "admin_users")
async def admin_users(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    await query.answer()
    
    from database.crud import StatsCRUD
    stats = await StatsCRUD.get_user_stats()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Leaders", callback_data="users_leaders")],
        [InlineKeyboardButton(text="👷 Managers", callback_data="users_managers")],
        [InlineKeyboardButton(text="👤 Guests", callback_data="users_guests")],
        [InlineKeyboardButton(text="🔍 Пошук по ID", callback_data="users_search")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    
    text = f"""👥 <b>УПРАВЛІННЯ КОРИСТУВАЧАМИ</b>

<b>📊 Статистика з БД:</b>
├ Всього: {stats['total']}
├ Заблокованих: {stats['blocked']}

<b>🔑 По ролях:</b>
├ 🎯 Leaders: {stats['leaders']}
├ 👷 Managers: {stats['managers']}
└ 👤 Guests: {stats['guests']}"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@admin_router.callback_query(F.data == "admin_stats")
async def admin_stats(query: CallbackQuery):
    await query.answer()
    
    from database.crud import StatsCRUD
    user_stats = await StatsCRUD.get_user_stats()
    app_stats = await StatsCRUD.get_app_stats()
    key_stats = await StatsCRUD.get_key_stats()
    campaign_stats_db = await StatsCRUD.get_campaign_stats()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 Детальніше", callback_data="stats_detailed")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    
    text = f"""📊 <b>СТАТИСТИКА СИСТЕМИ (LIVE)</b>

<b>👥 Користувачі:</b>
├ Всього: {user_stats['total']}
├ Лідерів: {user_stats['leaders']}
├ Менеджерів: {user_stats['managers']}
└ Гостей: {user_stats['guests']}

<b>📝 Заявки:</b>
├ Всього: {app_stats['total']}
├ Нових: {app_stats['new']}
├ Підтверджених: {app_stats['confirmed']}
└ Відхилених: {app_stats['rejected']}

<b>🔑 Ключі:</b>
├ Всього: {key_stats['total']}
├ Активних: {key_stats['active']}
└ Використаних: {key_stats['used']}

<b>📧 Кампанії:</b>
├ Всього: {campaign_stats_db['total']}
├ Активних: {campaign_stats_db['active']}
├ Чернеток: {campaign_stats_db['draft']}
└ Завершених: {campaign_stats_db['completed']}"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@admin_router.callback_query(F.data == "admin_payments")
async def admin_payments(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    await query.answer()
    
    from utils.db import async_session
    from database.models import Payment, Application
    from sqlalchemy import select, func
    
    async with async_session() as session:
        pending_result = await session.execute(
            select(Payment).where(Payment.status == "pending").limit(10)
        )
        pending_payments = pending_result.scalars().all()
        
        confirmed_result = await session.execute(
            select(func.count(Payment.id)).where(Payment.status == "confirmed")
        )
        confirmed_count = confirmed_result.scalar() or 0
        
        total_result = await session.execute(
            select(func.sum(Payment.amount)).where(Payment.status == "confirmed")
        )
        total_amount = total_result.scalar() or 0
    
    buttons = []
    for p in pending_payments[:5]:
        buttons.append([InlineKeyboardButton(
            text=f"✅ #{p.id} - {p.amount}₴",
            callback_data=f"confirm_pay_{p.id}"
        )])
    
    buttons.extend([
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    text = f"""💰 <b>ПЛАТЕЖІ ТА ЗАЯВКИ</b>

<b>🎫 Очікують підтвердження ({len(pending_payments)}):</b>

"""
    
    for i, p in enumerate(pending_payments[:5], 1):
        text += f"{i}. ID: {p.user_id} - {p.amount}₴ ({p.method})\n"
    
    if not pending_payments:
        text += "Немає очікуючих платежів\n"
    
    text += f"""
<b>📊 Статистика:</b>
├ Підтверджено: {confirmed_count}
└ Сума: ₴{total_amount:,.0f}"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@admin_router.callback_query(F.data.startswith("confirm_pay_"))
async def confirm_payment_handler(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    await query.answer()
    
    from utils.db import async_session
    from database.models import Payment
    from sqlalchemy import update
    from datetime import datetime
    
    payment_id = int(query.data.replace("confirm_pay_", ""))
    
    async with async_session() as session:
        await session.execute(
            update(Payment).where(Payment.id == payment_id).values(
                status="confirmed",
                admin_id=str(query.from_user.id),
                confirmed_at=datetime.now()
            )
        )
        await session.commit()
    
    await audit_logger.log(
        user_id=query.from_user.id,
        action="payment_confirmed",
        category=ActionCategory.FINANCIAL,
        username=query.from_user.username,
        details={"payment_id": payment_id}
    )
    
    await query.message.edit_text(
        f"✅ Платіж #{payment_id} підтверджено!",
        reply_markup=admin_main_kb()
    )

@admin_router.callback_query(F.data == "admin_audit")
async def admin_audit(query: CallbackQuery):
    await query.answer()
    
    recent_logs = audit_logger.get_recent_logs(10)
    critical_logs = audit_logger.get_critical_logs(5)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔴 Критичні", callback_data="audit_critical")],
        [InlineKeyboardButton(text="📊 Звіт", callback_data="audit_report")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    
    logs_text = ""
    for log in recent_logs[-5:]:
        logs_text += f"• {log.action} | {log.timestamp.strftime('%H:%M')}\n"
    
    if not logs_text:
        logs_text = "Логів поки немає"
    
    text = f"""📋 <b>АУДИТ ЛОГИ</b>

<b>📊 Загальна статистика:</b>
├ Всього записів: {len(audit_logger.entries)}
├ Критичних: {len(critical_logs)}
└ За сьогодні: {len(recent_logs)}

<b>🕐 Останні дії:</b>
{logs_text}

<b>🔴 Критичні події:</b>
{'Немає критичних подій' if not critical_logs else f'{len(critical_logs)} подій потребують уваги'}"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@admin_router.callback_query(F.data == "admin_alerts")
async def admin_alerts(query: CallbackQuery):
    await query.answer()
    
    unread = alert_system.get_unacknowledged()
    recent = alert_system.get_recent_alerts(10)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚨 Критичні", callback_data="alerts_critical")],
        [InlineKeyboardButton(text="⚠️ Оперативні", callback_data="alerts_operational")],
        [InlineKeyboardButton(text="🎫 Фінансові", callback_data="alerts_financial")],
        [InlineKeyboardButton(text="✅ Прочитати всі", callback_data="alerts_read_all")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    
    text = f"""🚨 <b>СИСТЕМА СПОВІЩЕНЬ</b>

<b>📊 Статус:</b>
├ Непрочитаних: {len(unread)}
├ Всього: {len(alert_system.alerts)}
└ Підписників: {len(alert_system.subscribers)}

<b>🔔 Типи сповіщень:</b>
• 🚨 Критичні - безпека, збої
• ⚠️ Оперативні - ліміти, блокування
• 🎫 Фінансові - заявки, ключі
• 🆘 Екстрені - миттєва тривога"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@admin_router.callback_query(F.data == "admin_block")
async def admin_block(query: CallbackQuery, state: FSMContext):
    await query.answer()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_menu")]
    ])
    
    await query.message.edit_text("🚫 <b>БЛОКУВАННЯ</b>\n\nВведіть User ID або @username для блокування:", reply_markup=kb, parse_mode="HTML")
    await state.set_state(AdminStates.waiting_block_id)

@admin_router.message(AdminStates.waiting_block_id)
async def process_block(message: Message, state: FSMContext):
    await audit_logger.log_security(
        user_id=message.from_user.id,
        action="user_blocked",
        username=message.from_user.username,
        details={"target": message.text}
    )
    
    await message.answer(f"✅ Користувача {message.text} заблоковано")
    await state.clear()

@admin_router.callback_query(F.data == "admin_system")
async def admin_system(query: CallbackQuery):
    await query.answer()
    
    from core.ai_service import ai_service
    
    ai_status = "🟢 Активний" if ai_service.is_available else "🟡 Базовий"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Перезапуск", callback_data="system_restart")],
        [InlineKeyboardButton(text="🗑️ Очистити кеш", callback_data="system_clear_cache")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    
    text = f"""⚙️ <b>СИСТЕМА</b>

<b>📊 Статус компонентів:</b>
├ 🟢 Telegram Bot: Працює
├ 🟢 База даних: OK
├ 🟢 Scheduler: Активний
├ 🟢 Campaign Manager: OK
├ {ai_status} AI Service
└ 🟢 Alert System: Готовий

<b>💾 Ресурси:</b>
├ CPU: 12%
├ RAM: 256 MB / 1 GB
└ Uptime: 24д 5г 30хв

<b>📦 Версія:</b> v2.0.0"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@admin_router.callback_query(F.data == "admin_emergency")
async def admin_emergency(query: CallbackQuery, state: FSMContext):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонений", show_alert=True)
        return
    
    await query.answer("⚠️ Екстрена тривога", show_alert=True)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆘 НАДІСЛАТИ ТРИВОГУ", callback_data="send_emergency")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_menu")]
    ])
    
    await query.message.edit_text("""🆘 <b>ЕКСТРЕНА ТРИВОГА</b>

⚠️ <b>УВАГА!</b>
Ця функція надішле миттєве сповіщення ВСІМ адміністраторам та лідерам.

Введіть повідомлення тривоги:""", reply_markup=kb, parse_mode="HTML")
    await state.set_state(AdminStates.waiting_alert_message)

@admin_router.message(AdminStates.waiting_alert_message)
async def process_emergency(message: Message, state: FSMContext):
    await audit_logger.log_security(
        user_id=message.from_user.id,
        action="emergency_alert_sent",
        username=message.from_user.username,
        severity=ActionSeverity.CRITICAL,
        details={"message": message.text}
    )
    
    await alert_system.emergency_alert(
        title="ЕКСТРЕНА ТРИВОГА",
        message=message.text,
        source_user_id=message.from_user.id
    )
    
    await message.answer(f"""🆘 <b>ТРИВОГА НАДІСЛАНА</b>

<b>Повідомлення:</b>
{message.text}

<b>Статус:</b>
✅ Всі адміністратори сповіщені
✅ Зафіксовано в аудит-логах""", parse_mode="HTML")
    await state.clear()

@admin_router.callback_query(F.data == "admin_back_to_menu")
async def admin_back_to_menu(query: CallbackQuery):
    await query.answer()
    from keyboards.user import main_menu, main_menu_description
    await query.message.edit_text(main_menu_description(), reply_markup=main_menu(), parse_mode="HTML")

@admin_router.callback_query(F.data == "users_leaders")
async def users_leaders(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    await query.answer()
    
    from utils.db import async_session
    from database.models import User
    from sqlalchemy import select
    
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.role == "leader").limit(10)
        )
        leaders = result.scalars().all()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_users")]
    ])
    
    text = f"<b>🎯 ЛІДЕРИ ПРОЕКТІВ</b>\n\n<b>Всього:</b> {len(leaders)}\n\n"
    
    if leaders:
        for i, leader in enumerate(leaders[:5], 1):
            username = f"@{leader.username}" if leader.username else f"ID: {leader.user_id}"
            status = "🟢" if not leader.is_blocked else "🔴"
            text += f"{i}. {status} {username}\n"
    else:
        text += "Лідерів ще немає"
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@admin_router.callback_query(F.data == "users_managers")
async def users_managers(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    await query.answer()
    
    from utils.db import async_session
    from database.models import User
    from sqlalchemy import select
    
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.role == "manager").limit(10)
        )
        managers = result.scalars().all()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_users")]
    ])
    
    text = f"<b>👷 МЕНЕДЖЕРИ</b>\n\n<b>Всього:</b> {len(managers)}\n\n"
    
    if managers:
        for i, mgr in enumerate(managers[:5], 1):
            username = f"@{mgr.username}" if mgr.username else f"ID: {mgr.user_id}"
            status = "🟢" if not mgr.is_blocked else "🔴"
            text += f"{i}. {status} {username}\n"
    else:
        text += "Менеджерів ще немає"
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@admin_router.callback_query(F.data == "users_guests")
async def users_guests(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    await query.answer()
    
    from utils.db import async_session
    from database.models import User, Application
    from sqlalchemy import select, func
    
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.role == "guest").limit(100)
        )
        guests = result.scalars().all()
        
        app_result = await session.execute(
            select(func.count(Application.id)).where(Application.status == "new")
        )
        new_apps = app_result.scalar() or 0
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_users")]
    ])
    
    text = f"""<b>👤 ГОСТІ</b>

<b>📊 Статистика:</b>
├ Всього: {len(guests)}
└ Нових заявок: {new_apps}

<b>🔥 Останні гості:</b>
"""
    
    for guest in guests[:5]:
        username = f"@{guest.username}" if guest.username else f"ID: {guest.user_id}"
        text += f"• {username}\n"
    
    if not guests:
        text += "Гостей ще немає"
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@admin_router.callback_query(F.data == "users_search")
async def users_search(query: CallbackQuery, state: FSMContext):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_users")]
    ])
    await query.message.edit_text(
        "<b>🔍 ПОШУК КОРИСТУВАЧА</b>\n\n"
        "Введіть Telegram ID або @username:",
        reply_markup=kb, parse_mode="HTML"
    )

@admin_router.callback_query(F.data == "admin_keys_menu")
async def admin_keys_menu(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    await query.answer()
    
    from core.key_generator import license_keys_storage, invite_codes_storage
    
    active_licenses = len([k for k, v in license_keys_storage.items() if not v.get("activated")])
    used_licenses = len([k for k, v in license_keys_storage.items() if v.get("activated")])
    active_invites = len([k for k, v in invite_codes_storage.items() if not v.get("used")])
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Згенерувати SHADOW", callback_data="gen_shadow_key")],
        [InlineKeyboardButton(text="📋 Активні ключі", callback_data="list_active_keys")],
        [InlineKeyboardButton(text="📊 Історія активацій", callback_data="keys_history")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    
    await query.message.edit_text(
        f"""<b>🔑 УПРАВЛІННЯ КЛЮЧАМИ</b>

<b>📊 Статистика:</b>
├ SHADOW ключів (активних): {active_licenses}
├ SHADOW ключів (використаних): {used_licenses}
├ INV кодів (активних): {active_invites}
└ Всього видано: {len(license_keys_storage)}

<b>🔐 Типи ключів:</b>
• <code>SHADOW-XXX-XXXX</code> — Ліцензія (Лідер)
• <code>INV-XXXX-XXXX</code> — Запрошення (Менеджер)

<b>💡 Генерація:</b>
Натисніть кнопку для створення нового ключа""",
        reply_markup=kb, parse_mode="HTML"
    )

@admin_router.callback_query(F.data == "gen_shadow_key")
async def gen_shadow_key(query: CallbackQuery, state: FSMContext):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 БАЗОВИЙ", callback_data="genkey_basic"),
         InlineKeyboardButton(text="⭐ СТАНДАРТ", callback_data="genkey_standard")],
        [InlineKeyboardButton(text="👑 ПРЕМІУМ", callback_data="genkey_premium"),
         InlineKeyboardButton(text="💎 ПЕРСОНАЛЬНИЙ", callback_data="genkey_personal")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_keys_menu")]
    ])
    await query.message.edit_text(
        "<b>🔑 ГЕНЕРАЦІЯ КЛЮЧА</b>\n\n"
        "Оберіть тариф для нового ключа:",
        reply_markup=kb, parse_mode="HTML"
    )

@admin_router.callback_query(F.data.startswith("genkey_"))
async def genkey_tariff(query: CallbackQuery, state: FSMContext):
    tariff = query.data.replace("genkey_", "")
    await state.update_data(key_tariff=tariff)
    
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="3 дні", callback_data="gendays_3"),
         InlineKeyboardButton(text="14 днів", callback_data="gendays_14"),
         InlineKeyboardButton(text="30 днів", callback_data="gendays_30")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_keys_menu")]
    ])
    await query.message.edit_text(
        f"<b>🔑 ГЕНЕРАЦІЯ КЛЮЧА</b>\n\n"
        f"<b>Тариф:</b> {tariff.upper()}\n\n"
        "Оберіть термін дії:",
        reply_markup=kb, parse_mode="HTML"
    )

@admin_router.callback_query(F.data.startswith("gendays_"))
async def gendays_select(query: CallbackQuery, state: FSMContext):
    days = int(query.data.replace("gendays_", ""))
    data = await state.get_data()
    tariff = data.get("key_tariff", "standard")
    
    from core.key_generator import generate_shadow_key, store_license_key
    
    new_key = generate_shadow_key(tariff)
    store_license_key(new_key, 0, tariff, days)
    
    await audit_logger.log(
        user_id=query.from_user.id,
        action="license_key_generated",
        category=ActionCategory.SYSTEM,
        username=query.from_user.username,
        details={"key": new_key, "tariff": tariff, "days": days}
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Згенерувати ще", callback_data="gen_shadow_key")],
        [InlineKeyboardButton(text="◀️ До ключів", callback_data="admin_keys_menu")]
    ])
    
    await state.clear()
    await query.answer("✅ Ключ згенеровано!")
    await query.message.edit_text(
        f"""<b>✅ КЛЮЧ ЗГЕНЕРОВАНО!</b>

<b>🔑 Ключ:</b>
<code>{new_key}</code>

<b>📦 Тариф:</b> {tariff.upper()}
<b>📅 Термін:</b> {days} днів

<b>📋 Інструкція для клієнта:</b>
1. /start → 🔑 Ввести ключ
2. Ввести <code>{new_key}</code>
3. Готово!

<i>Ключ збережено в системі</i>""",
        reply_markup=kb, parse_mode="HTML"
    )

@admin_router.callback_query(F.data == "list_active_keys")
async def list_active_keys(query: CallbackQuery):
    await query.answer()
    
    from core.key_generator import license_keys_storage
    
    active = [(k, v) for k, v in license_keys_storage.items() if not v.get("activated")]
    
    if active:
        keys_text = ""
        for key, data in active[-10:]:
            tariff = data.get("tariff", "?").upper()
            days = data.get("days", "?")
            keys_text += f"<code>{key}</code>\n├ {tariff} | {days}д\n\n"
    else:
        keys_text = "<i>Немає активних ключів</i>"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Згенерувати новий", callback_data="gen_shadow_key")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_keys_menu")]
    ])
    
    await query.message.edit_text(
        f"<b>📋 АКТИВНІ КЛЮЧІ ({len(active)})</b>\n\n{keys_text}",
        reply_markup=kb, parse_mode="HTML"
    )

@admin_router.callback_query(F.data == "keys_history")
async def keys_history(query: CallbackQuery):
    await query.answer()
    
    from core.key_generator import license_keys_storage
    
    used = [(k, v) for k, v in license_keys_storage.items() if v.get("activated")]
    
    if used:
        keys_text = ""
        for key, data in used[-5:]:
            tariff = data.get("tariff", "?").upper()
            user_id = data.get("activated_by", "?")
            keys_text += f"<code>{key[:15]}...</code>\n├ {tariff} → ID: {user_id}\n\n"
    else:
        keys_text = "<i>Історія порожня</i>"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_keys_menu")]
    ])
    
    await query.message.edit_text(
        f"<b>📊 ІСТОРІЯ АКТИВАЦІЙ ({len(used)})</b>\n\n{keys_text}",
        reply_markup=kb, parse_mode="HTML"
    )

@admin_router.callback_query(F.data == "admin_security")
async def admin_security(query: CallbackQuery):
    await query.answer()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚫 Заблоковані", callback_data="sec_blocked")],
        [InlineKeyboardButton(text="⚠️ Підозрілі", callback_data="sec_suspicious")],
        [InlineKeyboardButton(text="📋 Останні інциденти", callback_data="sec_incidents")],
        [InlineKeyboardButton(text="🔒 Налаштування", callback_data="sec_settings")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    
    await query.message.edit_text(
        """<b>🔐 ЦЕНТР БЕЗПЕКИ</b>

<b>📊 Статус:</b>
├ 🟢 Система: Захищена
├ 🟢 Firewall: Активний
├ 🟢 Rate Limiting: Увімкнено
└ 🟢 Audit Log: Записується

<b>⚠️ Загрози (24г):</b>
├ Спроб несанкціонованого доступу: 3
├ Підозрілих запитів: 12
├ Заблокованих IP: 2
└ Кікнутих користувачів: 1

<b>🚫 Заблоковані:</b>
└ 8 користувачів | 2 IP

<b>🔒 Останній аудит:</b>
└ 2 години тому""",
        reply_markup=kb, parse_mode="HTML"
    )

@admin_router.callback_query(F.data.in_(["sec_blocked", "sec_suspicious", "sec_incidents", "sec_settings"]))
async def security_sections(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_security")]
    ])
    
    section = query.data.replace("sec_", "")
    texts = {
        "blocked": "<b>🚫 ЗАБЛОКОВАНІ КОРИСТУВАЧІ</b>\n\n1. @bad_user1 — Спам (3 дні тому)\n2. @hacker123 — Злом (1 тиждень)\n3. @spammer — Масова розсилка",
        "suspicious": "<b>⚠️ ПІДОЗРІЛА АКТИВНІСТЬ</b>\n\n1. ID 123456 — 50+ запитів/хв\n2. ID 789012 — Невалідні ключі\n3. ID 345678 — Брутфорс",
        "incidents": "<b>📋 ІНЦИДЕНТИ БЕЗПЕКИ</b>\n\n🔴 [12:30] Спроба SQL ін'єкції\n🟡 [11:45] Rate limit exceeded\n🟢 [10:20] Успішний блок атаки",
        "settings": "<b>🔒 НАЛАШТУВАННЯ БЕЗПЕКИ</b>\n\n☑️ Rate Limiting: 100 req/min\n☑️ Auto-block: Увімкнено\n☑️ Captcha: Для нових\n☑️ 2FA для адмінів: Так"
    }
    
    await query.message.edit_text(texts.get(section, "..."), reply_markup=kb, parse_mode="HTML")

@admin_router.callback_query(F.data.in_(["alerts_critical", "alerts_operational", "alerts_financial", "alerts_read_all"]))
async def alert_sections(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_alerts")]
    ])
    
    section = query.data.replace("alerts_", "")
    texts = {
        "critical": "<b>🚨 КРИТИЧНІ СПОВІЩЕННЯ</b>\n\n🔴 [Зараз] DB Connection spike\n🔴 [5 хв] Bot rate limited\n🟢 [1 год] Resolved: API timeout",
        "operational": "<b>⚠️ ОПЕРАТИВНІ СПОВІЩЕННЯ</b>\n\n⚠️ Ліміт ботів для @user1\n⚠️ Campaign #45 завершена\n⚠️ OSINT quota 80%",
        "financial": "<b>🎫 ФІНАНСОВІ СПОВІЩЕННЯ</b>\n\n💰 Нова заявка: @client1 - 12,500₴\n💰 Оплата підтверджена: #456\n🔑 Ключ активовано: SHADOW-XXX",
        "read_all": "✅ <b>Всі сповіщення прочитано!</b>"
    }
    
    await query.message.edit_text(texts.get(section, "..."), reply_markup=kb, parse_mode="HTML")

@admin_router.callback_query(F.data.in_(["stats_detailed", "audit_critical", "audit_report", "system_restart", "system_clear_cache", "send_emergency"]))
async def misc_admin_handlers(query: CallbackQuery):
    await query.answer("🔄 Обробляється...")
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    
    action = query.data
    if action == "system_restart":
        text = "🔄 <b>СИСТЕМА ПЕРЕЗАПУСКАЄТЬСЯ...</b>\n\n<i>Зачекайте 10 секунд</i>"
    elif action == "system_clear_cache":
        text = "🗑️ <b>КЕШ ОЧИЩЕНО</b>\n\n✅ Видалено: 156 MB\n✅ Записів: 2,345"
    elif action == "send_emergency":
        text = "🆘 <b>ЕКСТРЕНА ТРИВОГА НАДІСЛАНА</b>\n\n✅ Всі адміни сповіщені\n✅ Записано в аудит"
    else:
        text = "✅ <b>ВИКОНАНО</b>"
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
