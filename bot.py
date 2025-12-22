import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def command_start(message: Message):
    await message.answer(
        f"Привіт, {message.from_user.first_name}! 👋\n\nЦе бот Shadow Security.",
        parse_mode="HTML"
    )

@dp.message()
async def echo(message: Message):
    await message.answer("Я отримав твоє повідомлення!")

async def main():
    logger.info("Бот запускається...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
