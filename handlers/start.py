from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from database.crud import ProjectCRUD
from core.audit_logger import audit_logger
from core.role_constants import UserRole
from services.user_service import user_service
from keyboards.role_menus import get_description_by_role, get_menu_by_role
from utils.db import async_session

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message):
    user = user_service.get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    
    async with async_session() as session:
        project = await ProjectCRUD.get_by_leader_async(str(message.from_user.id))
    
    if project and user.role == UserRole.GUEST:
        user_service.set_user_role(message.from_user.id, UserRole.LEADER)
        user.role = UserRole.LEADER

    await audit_logger.log_auth(
        user_id=message.from_user.id,
        action="user_start",
        username=message.from_user.username,
        details={"has_project": project is not None, "role": user.role}
    )
    
    role = user.role if user else UserRole.GUEST
    
    await message.answer(
        get_description_by_role(role),
        reply_markup=get_menu_by_role(role),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "user_menu")
async def user_menu_callback(callback: CallbackQuery):
    user = user_service.get_or_create_user(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    role = user.role if user else UserRole.GUEST
    
    await callback.message.edit_text(
        get_description_by_role(role),
        reply_markup=get_menu_by_role(role),
        parse_mode="HTML"
    )
    await callback.answer()
