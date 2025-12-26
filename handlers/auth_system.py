from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from database.crud import KeyCRUD, ProjectCRUD
import logging

logger = logging.getLogger(__name__)

auth_router = Router()

@auth_router.message(F.text.startswith("SHADOW-"))
async def auth_key(message: Message, state: FSMContext):
    code = message.text.strip().upper()
    logger.info(f"Validating key: {code} for user {message.from_user.id}")
    
    try:
        key = await KeyCRUD.validate_key(code)
        
        if key:
            project = await ProjectCRUD.create_async(
                leader_id=str(message.from_user.id),
                leader_username=message.from_user.username or "",
                key_id=key.id,
                name="Проект",
                tariff=key.tariff,
                bots_limit=50,
                managers_limit=5
            )
            
            await KeyCRUD.use_key(code, str(message.from_user.id))
            
            await message.answer(
                f"✅ <b>АВТОРИЗАЦІЯ УСПІШНА!</b>\n\n"
                f"🎯 Тариф: <b>{key.tariff}</b>\n"
                f"📁 Проект створено\n\n"
                f"Натисніть /menu для доступу до функцій",
                parse_mode="HTML"
            )
            logger.info(f"Key {code} activated for user {message.from_user.id}")
        else:
            await message.answer(
                "❌ <b>Ключ невалідний або вже використаний</b>\n\n"
                "Перевірте правильність коду або зверніться до підтримки.",
                parse_mode="HTML"
            )
            logger.warning(f"Invalid key attempt: {code} by user {message.from_user.id}")
    except Exception as e:
        logger.error(f"Auth error: {e}")
        await message.answer("❌ Помилка авторизації. Спробуйте пізніше.")

@auth_router.message(F.text.startswith("INV-"))
async def invite_code(message: Message, state: FSMContext):
    code = message.text.strip().upper()
    logger.info(f"Processing invite code: {code} for user {message.from_user.id}")
    
    await message.answer(
        "🔄 <b>Обробка коду запрошення...</b>\n\n"
        "Функція запрошень буде доступна найближчим часом.",
        parse_mode="HTML"
    )
