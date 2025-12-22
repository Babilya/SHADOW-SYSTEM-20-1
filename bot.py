import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def command_start(message: Message):
    await message.answer(
        f"Привіт, {message.from_user.first_name}! 👋\n\n"
        "Ласкаво просимо до бота Shadow Security.",
        parse_mode="HTML"
    )

@dp.message(Command("help"))
async def command_help(message: Message):
    await message.answer(
        "📋 <b>Доступні команди:</b>\n\n"
        "/start - Почати роботу\n"
        "/help - Показати цю довідку\n"
        "/info - Інформація про бота",
        parse_mode="HTML"
    )

@dp.message(Command("info"))
async def command_info(message: Message):
    await message.answer(
        "ℹ️ <b>Shadow Security Bot</b>\n\n"
        "Версія: 2.0\n"
        "Мова: Українська\n"
        "Статус: Активний ✅",
        parse_mode="HTML"
    )

@dp.message()
async def echo(message: Message):
    await message.answer("✉️ Повідомлення отримане!")

async def main():
    logger.info("🤖 Бот запускається...")
    # Видаляємо webhook якщо він активний
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("✅ Webhook видалений")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
