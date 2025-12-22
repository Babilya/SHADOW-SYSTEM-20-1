import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BotCommand
from config import BOT_TOKEN
from handlers.user import user_router
from handlers.admin import admin_router
from handlers.payments import payments_router
from keyboards.user import main_menu
from utils.db import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Реєстрація роутерів
dp.include_router(user_router)
dp.include_router(admin_router)
dp.include_router(payments_router)

@dp.message(CommandStart())
async def command_start(message: Message):
    """Команда /start"""
    user = message.from_user
    
    # Додаємо користувача в БД
    db.add_user(user.id, user.username or "Unknown", user.first_name or "")
    
    await message.answer(
        f"Привіт, {user.first_name}! 👋\n\n"
        "Ласкаво просимо до <b>Shadow Security Bot</b> v2.0\n\n"
        "📋 Доступні команди:\n"
        "/menu - Головне меню\n"
        "/help - Довідка\n"
        "/subscription - Мої підписки\n"
        "/pay - Поповнити рахунок\n\n"
        "Виберіть потрібну опцію:",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

@dp.message(Command("help"))
async def command_help(message: Message):
    """Команда /help"""
    await message.answer(
        "📋 <b>Довідка</b>\n\n"
        "<b>Основні команди:</b>\n"
        "/start - Почати\n"
        "/menu - Меню\n"
        "/help - Ця довідка\n\n"
        "<b>Користувацькі функції:</b>\n"
        "/mailing - Розсилка\n"
        "/autoreply - Автовідповідь\n"
        "/stats - Статистика\n"
        "/settings - Налаштування\n\n"
        "<b>Платежі:</b>\n"
        "/pay - Поповнити рахунок\n"
        "/balance - Баланс\n"
        "/history - Історія платежів\n\n"
        "<b>Адміністративні команди:</b>\n"
        "/admin - Панель адміна (тільки для адміністраторів)",
        parse_mode="HTML"
    )

@dp.message(Command("menu"))
async def command_menu(message: Message):
    """Команда /menu"""
    await message.answer(
        "📱 <b>Головне меню</b>",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

@dp.message()
async def echo(message: Message):
    """Обробник всіх повідомлень"""
    await message.answer(
        "✉️ Повідомлення отримане!\n\n"
        "Напишіть /help для отримання списку команд"
    )

async def main():
    logger.info("🤖 Shadow Security Bot v2.0 запускається...")
    
    # Видаляємо webhook якщо він активний
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("✅ Webhook видалений")
    
    # Встановлюємо команди
    await bot.set_my_commands([
        BotCommand(command="start", description="Почати"),
        BotCommand(command="menu", description="Меню"),
        BotCommand(command="help", description="Довідка"),
        BotCommand(command="subscription", description="Підписки"),
        BotCommand(command="pay", description="Поповнити"),
        BotCommand(command="admin", description="Адмін панель"),
    ])
    
    logger.info("✅ Команди встановлені")
    logger.info("🚀 Бот готовий!")
    
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
