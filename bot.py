import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import F

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from config import BOT_TOKEN, ADMIN_IDS
    from handlers.user import user_router
    from handlers.admin import admin_router
    from handlers.botnet import botnet_router
    from handlers.osint import osint_router
    from handlers.analytics import analytics_router
    from handlers.team import team_router
    from handlers.subscriptions import subscriptions_router
    from handlers.funnels import funnels_router
    from handlers.help import help_router
    from handlers.texting import texting_router
    from handlers.applications import applications_router
    from handlers.emergency import emergency_router
    from handlers.configurator import configurator_router
    from handlers.security import security_router
    from handlers.tickets import tickets_router
    from handlers.referral import referral_router
    from handlers.mailing import mailing_router
    from handlers.missing_handlers import missing_router
    from handlers.auth_system import auth_router
    from handlers.proxy import proxy_router
    from handlers.export import export_router
    from handlers.warming import warming_router
    from handlers.scheduler import scheduler_router
    from handlers.geoscanner import geo_router
    from handlers.advanced_features import advanced_router
    from middlewares.security_middleware import SecurityMiddleware
    from utils.db import init_db
    from middlewares.role_middleware import RoleMiddleware
    from keyboards.role_menus import get_menu_by_role, get_description_by_role
    from services.user_service import user_service
    from database.models import UserRole
    logger.info("✅ Все модулі завантажені успішно")
except Exception as e:
    logger.error(f"❌ Помилка при завантаженні модулів: {e}", exc_info=True)

bot = Bot(token=BOT_TOKEN or "PLACEHOLDER")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.message.middleware(SecurityMiddleware())
dp.callback_query.middleware(SecurityMiddleware())
dp.message.middleware(RoleMiddleware())
dp.callback_query.middleware(RoleMiddleware())

routers = [
    user_router, admin_router, botnet_router,
    osint_router, analytics_router, team_router, subscriptions_router,
    funnels_router, help_router, texting_router, applications_router,
    emergency_router, configurator_router, security_router, 
    tickets_router, referral_router, mailing_router, missing_router,
    proxy_router, export_router, warming_router, scheduler_router, geo_router,
    auth_router, advanced_router
]

for r in routers:
    try:
        dp.include_router(r)
    except Exception as e:
        logger.error(f"❌ Error including router: {e}")

@dp.message(CommandStart())
async def command_start(message: Message, user_role: str = UserRole.GUEST, **kwargs):
    try:
        user = message.from_user
        
        if user.id in ADMIN_IDS and user_role != UserRole.ADMIN:
            user_service.set_user_role(user.id, UserRole.ADMIN)
            user_role = UserRole.ADMIN
        
        menu = get_menu_by_role(user_role)
        description = get_description_by_role(user_role)
        
        await message.answer(
            f"Привіт, {user.first_name}! 👋\n\n" + description,
            reply_markup=menu,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"❌ /start error: {e}", exc_info=True)

@dp.message(Command("menu"))
async def command_menu(message: Message, user_role: str = UserRole.GUEST, **kwargs):
    menu = get_menu_by_role(user_role)
    description = get_description_by_role(user_role)
    await message.answer(description, reply_markup=menu, parse_mode="HTML")

@dp.message(Command("role"))
async def command_role(message: Message, user_role: str = UserRole.GUEST, **kwargs):
    from core.roles import ROLE_NAMES
    role_name = ROLE_NAMES.get(user_role, "Невідома")
    await message.answer(f"👤 Ваша роль: <b>{role_name}</b>", parse_mode="HTML")

@dp.callback_query(F.data == "user_menu")
async def user_menu_callback(query: CallbackQuery, user_role: str = UserRole.GUEST, **kwargs):
    await query.answer()
    from keyboards.user import main_menu, main_menu_description
    await query.message.edit_text(main_menu_description(), reply_markup=main_menu(), parse_mode="HTML")

@dp.callback_query(F.data == "view_tariffs")
async def view_tariffs_callback(query: CallbackQuery, **kwargs):
    await query.answer()
    from handlers.subscriptions import subscriptions_description, subscriptions_kb
    await query.message.edit_text(subscriptions_description(), reply_markup=subscriptions_kb(), parse_mode="HTML")

@dp.callback_query(F.data == "submit_application")
async def submit_application_callback(query: CallbackQuery, **kwargs):
    await query.answer()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆓 Free", callback_data="apply_free")],
        [InlineKeyboardButton(text="⭐ Standard", callback_data="apply_standard")],
        [InlineKeyboardButton(text="👑 Premium", callback_data="apply_premium")],
        [InlineKeyboardButton(text="💎 Elite", callback_data="apply_elite")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_start")]
    ])
    await query.message.edit_text(
        "📝 <b>ПОДАТИ ЗАЯВКУ</b>\n\nОберіть тариф для подачі заявки:",
        reply_markup=kb,
        parse_mode="HTML"
    )


@dp.callback_query(F.data == "support")
async def support_callback(query: CallbackQuery, **kwargs):
    await query.answer()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Написати", url="https://t.me/shadow_support")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_start")]
    ])
    await query.message.edit_text(
        "💬 <b>ПІДТРИМКА</b>\n\n"
        "Маєте питання? Зверніться до нашої підтримки!\n\n"
        "📧 Email: support@shadowsystem.io\n"
        "💬 Telegram: @shadow_support",
        reply_markup=kb,
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "back_to_start")
async def back_to_start_callback(query: CallbackQuery, user_role: str = UserRole.GUEST, **kwargs):
    await query.answer()
    menu = get_menu_by_role(user_role)
    description = get_description_by_role(user_role)
    await query.message.edit_text(description, reply_markup=menu, parse_mode="HTML")

@dp.callback_query(F.data == "admin_applications")
async def admin_applications_callback(query: CallbackQuery, user_role: str = UserRole.GUEST, **kwargs):
    if user_role != UserRole.ADMIN:
        await query.answer("❌ Тільки для адміністраторів", show_alert=True)
        return
    await query.answer()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Нові заявки (3)", callback_data="new_applications")],
        [InlineKeyboardButton(text="✅ Схвалені", callback_data="approved_applications")],
        [InlineKeyboardButton(text="❌ Відхилені", callback_data="rejected_applications")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_start")]
    ])
    await query.message.edit_text(
        "📝 <b>ЗАЯВКИ</b>\n\n"
        "Нових заявок: 3\nОчікують: 2\nСхвалено: 45\nВідхилено: 5",
        reply_markup=kb,
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "admin_keys")
async def admin_keys_callback(query: CallbackQuery, user_role: str = UserRole.GUEST, **kwargs):
    if user_role != UserRole.ADMIN:
        await query.answer("❌ Тільки для адміністраторів", show_alert=True)
        return
    await query.answer()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Генерувати ключ", callback_data="generate_key")],
        [InlineKeyboardButton(text="📋 Активні ключі", callback_data="active_keys")],
        [InlineKeyboardButton(text="🗑️ Використані", callback_data="used_keys")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_start")]
    ])
    await query.message.edit_text(
        "🔑 <b>УПРАВЛІННЯ КЛЮЧАМИ</b>\n\n"
        "Активних: 12\nВикористаних: 45\nВсього: 57",
        reply_markup=kb,
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "admin_change_role")
async def admin_change_role_callback(query: CallbackQuery, user_role: str = UserRole.GUEST, **kwargs):
    if user_role != UserRole.ADMIN:
        await query.answer("❌ Тільки для адміністраторів", show_alert=True)
        return
    await query.answer()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_start")]
    ])
    await query.message.edit_text(
        "🔄 <b>ЗМІНА РОЛІ</b>\n\n"
        "Щоб змінити роль користувача, надішліть команду:\n"
        "<code>/setrole USER_ID ROLE</code>\n\n"
        "Доступні ролі:\n"
        "• guest - Гість\n"
        "• manager - Менеджер\n"
        "• leader - Лідер\n"
        "• admin - Адміністратор\n\n"
        "Приклад:\n"
        "<code>/setrole 123456789 leader</code>",
        reply_markup=kb,
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "admin_settings")
async def admin_settings_callback(query: CallbackQuery, user_role: str = UserRole.GUEST, **kwargs):
    if user_role != UserRole.ADMIN:
        await query.answer("❌ Тільки для адміністраторів", show_alert=True)
        return
    await query.answer()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_start")]
    ])
    await query.message.edit_text(
        "⚙️ <b>НАЛАШТУВАННЯ СИСТЕМИ</b>\n\n"
        "• Режим: Production\n"
        "• База даних: PostgreSQL\n"
        "• Кешування: Redis\n"
        "• Логування: Увімкнено",
        reply_markup=kb,
        parse_mode="HTML"
    )

@dp.message(Command("setrole"))
async def command_setrole(message: Message, user_role: str = UserRole.GUEST, **kwargs):
    if user_role != UserRole.ADMIN:
        await message.answer("❌ Тільки для адміністраторів")
        return
    
    args = message.text.split()[1:]
    if len(args) != 2:
        await message.answer(
            "❌ Неправильний формат.\n\n"
            "Використання: /setrole USER_ID ROLE\n"
            "Приклад: /setrole 123456789 leader"
        )
        return
    
    try:
        target_user_id = int(args[0])
        new_role = args[1].lower()
        
        valid_roles = [UserRole.GUEST, UserRole.MANAGER, UserRole.LEADER, UserRole.ADMIN]
        if new_role not in valid_roles:
            await message.answer(f"❌ Невідома роль: {new_role}\nДоступні: guest, manager, leader, admin")
            return
        
        if user_service.set_user_role(target_user_id, new_role):
            from core.roles import ROLE_NAMES
            role_name = ROLE_NAMES.get(new_role, new_role)
            await message.answer(f"✅ Роль користувача {target_user_id} змінено на: {role_name}")
        else:
            await message.answer(f"❌ Користувача {target_user_id} не знайдено")
    except ValueError:
        await message.answer("❌ USER_ID повинен бути числом")

@dp.message(Command("start_help"))
async def command_start_help(message: Message, user_role: str = UserRole.GUEST, **kwargs):
    from core.roles import ROLE_NAMES
    role_name = ROLE_NAMES.get(user_role, "Гість")
    
    help_text = f"📋 <b>SHADOW SYSTEM iO - Довідка</b>\n\n👤 Ваша роль: <b>{role_name}</b>\n\n"
    
    if user_role == UserRole.GUEST:
        help_text += (
            "📦 /menu - Головне меню\n"
            "📝 Подати заявку на доступ\n"
            "🔑 Ввести ключ активації\n"
            "📚 /help - Довідка"
        )
    elif user_role == UserRole.MANAGER:
        help_text += (
            "📝 /menu - Головне меню\n"
            "📊 /analytics - Аналітика\n"
            "📝 /texting - Текстовки\n"
            "📚 /help - Довідка"
        )
    elif user_role == UserRole.LEADER:
        help_text += (
            "🤖 /botnet - Управління ботами\n"
            "🔍 /osint - OSINT інструменти\n"
            "📊 /analytics - Аналітика\n"
            "👥 /team - Команда\n"
            "📦 /subscription - Підписки\n"
            "💳 /pay - Платежі\n"
            "📝 /texting - Текстовки\n"
            "📚 /help - Довідка"
        )
    else:
        help_text += (
            "🛡️ /admin - Адмін-панель\n"
            "🔄 /setrole USER_ID ROLE - Змінити роль\n"
            "📢 /broadcast - Розсилка\n"
            "📊 /stats - Статистика\n"
            "Всі функції лідера доступні"
        )
    
    await message.answer(help_text, parse_mode="HTML")

async def start_services():
    try:
        from core.rate_limiter import rate_limiter
        await rate_limiter.start()
        logger.info("✅ RateLimiter started")
    except Exception as e:
        logger.warning(f"RateLimiter failed: {e}")
    
    try:
        from core.message_queue import message_queue
        await message_queue.start()
        logger.info("✅ MessageQueue started")
    except Exception as e:
        logger.warning(f"MessageQueue failed: {e}")
    
    try:
        from core.mailing_scheduler import mailing_scheduler
        await mailing_scheduler.start()
        logger.info("✅ MailingScheduler started")
    except Exception as e:
        logger.warning(f"MailingScheduler failed: {e}")
    
    try:
        from core.antifraud import antifraud_service
        await antifraud_service.start()
        logger.info("✅ AntiFraud started")
    except Exception as e:
        logger.warning(f"AntiFraud failed: {e}")
    
    try:
        from core.key_notifications import key_notification_service
        key_notification_service.set_bot(bot)
        await key_notification_service.start()
        logger.info("✅ KeyNotifications started")
    except Exception as e:
        logger.warning(f"KeyNotifications failed: {e}")
    
    try:
        from core.segmentation import segmentation_service
        await segmentation_service.start()
        logger.info("✅ Segmentation started")
    except Exception as e:
        logger.warning(f"Segmentation failed: {e}")

async def main():
    logger.info("🤖 SHADOW SYSTEM iO v2.0 запускається...")
    try:
        await init_db()
        from middlewares.security_middleware import sync_from_db
        await sync_from_db()
        logger.info("✅ Security cache synced from DB")
        
        await start_services()
        logger.info("✅ All services started")
        
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Все готово!")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
