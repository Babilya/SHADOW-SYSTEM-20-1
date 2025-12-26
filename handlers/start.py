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
async def start_handler(message: Message):
    from services.user_service import user_service
    from database.crud import ProjectCRUD
    from utils.db import async_session
    from core.role_constants import UserRole
    
    user = user_service.get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    
    async with async_session() as session:
        project = await ProjectCRUD.get_by_leader_async(str(message.from_user.id))
    
    # Auto-upgrade role to LEADER if they have a project
    if project and user.role == UserRole.GUEST:
        user_service.set_user_role(message.from_user.id, UserRole.LEADER)
        user.role = UserRole.LEADER

    await audit_logger.log_auth(
        user_id=message.from_user.id,
        action="user_start",
        username=message.from_user.username,
        details={"has_project": project is not None, "role": user.role}
    )
    
    from keyboards.role_menus import get_description_by_role, get_menu_by_role
    role = user.role if user else UserRole.GUEST
    
    await message.answer(
        get_description_by_role(role),
        reply_markup=get_menu_by_role(role),
        parse_mode="HTML"
    )
