import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from handlers.user import user_router
    from handlers.admin import admin_router
    from handlers.payments import payments_router
    from keyboards.user import main_menu
    from utils.db import db
    logger.info("✅ Всі модулі завантажені")
except Exception as e:
    logger.error(f"❌ Помилка при завантаженні модулів: {e}", exc_info=True)
    sys.exit(1)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.include_router(user_router)
dp.include_router(admin_router)
dp.include_router(payments_router)

@dp.message(CommandStart())
async def command_start(message: Message):
    try:
        user = message.from_user
        db.add_user(user.id, user.username or "Unknown", user.first_name or "")
        await message.answer(
            f"Привіт, {user.first_name}! 👋\n\n"
            "Ласкаво просимо до <b>Shadow Security Bot</b> v2.0\n\n"
            "📋 Доступні команди:\n/menu, /help, /subscription, /pay",
            reply_markup=main_menu(),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"❌ /start error: {e}")

@dp.message(Command("help"))
async def command_help(message: Message):
    await message.answer(
        "📋 <b>Довідка</b>\n\n/start, /menu, /help, /mailing, /autoreply, /stats, /pay",
        parse_mode="HTML"
    )

@dp.message(Command("menu"))
async def command_menu(message: Message):
    await message.answer("📱 Головне меню", reply_markup=main_menu())

@dp.message()
async def echo_handler(message: Message):
    await message.answer("✉️ Повідомлення отримане!\n\nНапишіть /help")

async def main():
    logger.info("🤖 BOT ЗАПУСКАЄТЬСЯ...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Webhook видалений")
        
        logger.info("✅ BOT ГОТОВИЙ!")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
