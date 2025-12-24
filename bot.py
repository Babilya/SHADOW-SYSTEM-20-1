import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from config import BOT_TOKEN
    from handlers.user import user_router
    from handlers.admin import admin_router
    from handlers.payments import payments_router
    from handlers.botnet import botnet_router
    from handlers.osint import osint_router
    from handlers.analytics import analytics_router
    from handlers.team import team_router
    from handlers.subscriptions import subscriptions_router
    from handlers.funnels import funnels_router
    from handlers.help import help_router
    from handlers.texting import texting_router
    from keyboards.user import main_menu
    from utils.db import db
    from middlewares.auth import AuthMiddleware, RateLimitMiddleware
    logger.info("✅ Все модулі завантажені успішно")
except Exception as e:
    logger.error(f"❌ Помилка при завантаженні модулів: {e}", exc_info=True)
    sys.exit(1)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Додання middleware
dp.message.middleware(AuthMiddleware())
dp.callback_query.middleware(AuthMiddleware())
dp.message.middleware(RateLimitMiddleware(max_requests=20, time_window=60))

# Реєстрація всіх роутерів
dp.include_router(user_router)
dp.include_router(admin_router)
dp.include_router(payments_router)
dp.include_router(botnet_router)
dp.include_router(osint_router)
dp.include_router(analytics_router)
dp.include_router(team_router)
dp.include_router(subscriptions_router)
dp.include_router(funnels_router)
dp.include_router(help_router)
dp.include_router(texting_router)

@dp.message(CommandStart())
async def command_start(message: Message):
    try:
        from keyboards.user import main_menu_description
        user = message.from_user
        db.add_user(user.id, user.username or "Unknown", user.first_name or "")
        await message.answer(
            f"Привіт, {user.first_name}! 👋\n\n" + main_menu_description(),
            reply_markup=main_menu(),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"❌ /start error: {e}")

@dp.message(Command("start_help"))
async def command_start_help(message: Message):
    await message.answer(
        "📋 <b>SHADOW SYSTEM iO - Довідка</b>\n\n"
        "🤖 /botnet - Управління ботнетом\n"
        "🔍 /osint - OSINT та парсинг\n"
        "📊 /analytics - Аналітика та звіти\n"
        "👥 /team - Управління командою\n"
        "📦 /subscription - Підписки\n"
        "💳 /pay - Поповнення рахунку\n"
        "⚙️ /settings - Налаштування\n"
        "📝 /texting - Текстові воронки\n"
        "📚 /help - Дізнайтеся більше\n"
        "🎯 /onboarding - Навчання новачків\n"
        "📢 /sales - Sales воронка\n"
        "/admin - Адміністративна панель",
        parse_mode="HTML"
    )

@dp.message(Command("menu"))
async def command_menu(message: Message):
    await message.answer("📱 Головне меню", reply_markup=main_menu())

@dp.message()
async def echo_handler(message: Message):
    await message.answer("✉️ Повідомлення отримане!\n\nНапишіть /help для списку команд")

async def main():
    logger.info("🤖 SHADOW SYSTEM iO v2.0 запускається...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Все готово!")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
