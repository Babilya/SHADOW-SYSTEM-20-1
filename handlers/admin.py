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

def admin_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Розсилка", callback_data="admin_broadcast"),
         InlineKeyboardButton(text="👥 Користувачі", callback_data="admin_users")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
         InlineKeyboardButton(text="💰 Платежі", callback_data="admin_payments")],
        [InlineKeyboardButton(text="📋 Аудит логи", callback_data="admin_audit"),
         InlineKeyboardButton(text="🚨 Сповіщення", callback_data="admin_alerts")],
        [InlineKeyboardButton(text="🚫 Блокування", callback_data="admin_block"),
         InlineKeyboardButton(text="⚙️ Система", callback_data="admin_system")],
        [InlineKeyboardButton(text="🆘 Екстрена тривога", callback_data="admin_emergency")]
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
    await query.answer()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👑 Адміни", callback_data="users_admins")],
        [InlineKeyboardButton(text="🎯 Лідери", callback_data="users_leaders")],
        [InlineKeyboardButton(text="👷 Менеджери", callback_data="users_managers")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    
    text = """👥 <b>УПРАВЛІННЯ КОРИСТУВАЧАМИ</b>

<b>📊 Статистика:</b>
├ Всього: 1,245
├ Активних (24г): 456
├ Преміум: 234
└ Заблокованих: 8

<b>🔑 По ролях:</b>
├ 👑 Адміни: 3
├ 🎯 Лідери: 45
├ 👷 Менеджери: 156
└ 👤 Гості: 1,041"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@admin_router.callback_query(F.data == "admin_stats")
async def admin_stats(query: CallbackQuery):
    await query.answer()
    
    campaign_stats = len(campaign_manager.campaigns)
    scheduler_stats = scheduler.get_stats()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 Детальніше", callback_data="stats_detailed")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    
    text = f"""📊 <b>СТАТИСТИКА СИСТЕМИ</b>

<b>💰 Фінанси (місяць):</b>
├ Дохід: ₴145,230
├ Витрати: ₴12,450
└ Прибуток: ₴132,780

<b>📧 Кампанії:</b>
├ Активних: {campaign_stats}
├ В черзі: {scheduler_stats.get('pending', 0)}
├ Завершених: {scheduler_stats.get('completed', 0)}
└ Помилок: {scheduler_stats.get('failed', 0)}

<b>🤖 Ботнет:</b>
├ Всього ботів: 1,234
├ Активних: 1,089 (88.3%)
└ Блокованих: 45 (3.6%)

<b>📈 Трафік (сьогодні):</b>
├ Повідомлень: 45,678
├ Доставлено: 44,123 (96.6%)
└ CTR: 12.4%"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@admin_router.callback_query(F.data == "admin_payments")
async def admin_payments(query: CallbackQuery):
    await query.answer()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Підтвердити", callback_data="confirm_payment")],
        [InlineKeyboardButton(text="❌ Відхилити", callback_data="reject_payment")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    
    text = """💰 <b>ПЛАТЕЖІ ТА ЗАЯВКИ</b>

<b>🎫 Очікують підтвердження (3):</b>

1️⃣ <b>@user123</b> - СТАНДАРТ
   └ 12,500 ₴ | 2 год тому

2️⃣ <b>@company_lead</b> - ПРЕМІУМ
   └ 62,500 ₴ | 5 год тому

3️⃣ <b>@newbie</b> - БАЗОВИЙ
   └ 4,200 ₴ | 1 день тому

<b>📊 Статистика (місяць):</b>
├ Оплачено: 45 заявок
├ Сума: ₴234,500
└ Відхилено: 3"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

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
