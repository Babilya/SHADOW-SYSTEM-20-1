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
    from keyboards.user import main_menu
    from utils.db import db
    logger.info("✅ Все модулі завантажені успішно")
except Exception as e:
    logger.error(f"❌ Помилка при завантаженні модулів: {e}", exc_info=True)
    sys.exit(1)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Реєстрація всіх роутерів
dp.include_router(user_router)
dp.include_router(admin_router)
dp.include_router(payments_router)
dp.include_router(botnet_router)
dp.include_router(osint_router)
dp.include_router(analytics_router)
dp.include_router(team_router)
dp.include_router(subscriptions_router)

@dp.message(CommandStart())
async def command_start(message: Message):
    try:
        user = message.from_user
        db.add_user(user.id, user.username or "Unknown", user.first_name or "")
        await message.answer(
            f"Привіт, {user.first_name}! 👋\n\n"
            "<b>SHADOW SYSTEM iO v2.0</b> - Повна система управління Telegram Botnet\n\n"
            "📋 Основні команди:\n"
            "/menu - Меню користувача\n"
            "/botnet - Управління ботами\n"
            "/osint - OSINT & Парсинг\n"
            "/analytics - Аналітика\n"
            "/team - Управління командою\n"
            "/subscription - Підписки\n"
            "/pay - Платежі\n"
            "/admin - Панель адміна\n\n"
            "Виберіть функцію:",
            reply_markup=main_menu(),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"❌ /start error: {e}")

@dp.message(Command("help"))
async def command_help(message: Message):
    await message.answer(
        "📋 <b>SHADOW SYSTEM iO - Довідка</b>\n\n"
        "🤖 /botnet - Управління ботнетом\n"
        "🔍 /osint - OSINT та парсинг\n"
        "📊 /analytics - Аналітика та звіти\n"
        "👥 /team - Управління командою\n"
        "📦 /subscription - Підписки\n"
        "💳 /pay - Поповнення рахунку\n"
        "⚙️ /settings - Налаштування\n"
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
