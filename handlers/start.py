from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy.orm import Session
from database.crud import UserCRUD, ProjectCRUD
from config.templates import MESSAGES
from keyboards.guest_kb import guest_main_kb, tariffs_kb
from keyboards.user_kb import user_main_kb
from core.audit_logger import audit_logger, ActionCategory
from core.alerts import alert_system, AlertType

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message, db: Session):
    user = UserCRUD.get_or_create(db, str(message.from_user.id), message.from_user.username, message.from_user.first_name)
    project = ProjectCRUD.get_by_leader(db, str(message.from_user.id))
    
    await audit_logger.log_auth(
        user_id=message.from_user.id,
        action="user_start",
        username=message.from_user.username,
        details={"has_project": project is not None}
    )
    
    if project:
        await message.answer("🖥 РОБОЧИЙ СТІЛ", reply_markup=user_main_kb())
    else:
        await message.answer(MESSAGES["guest_welcome"], reply_markup=guest_main_kb())
