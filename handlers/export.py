from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import logging
import json
import csv
import io

from config import ADMIN_IDS
from core.audit_logger import audit_logger, ActionCategory

logger = logging.getLogger(__name__)
export_router = Router()

class ExportStates(StatesGroup):
    waiting_export_type = State()

def export_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Користувачі", callback_data="export_users")],
        [InlineKeyboardButton(text="🤖 Боти/Сесії", callback_data="export_bots")],
        [InlineKeyboardButton(text="📧 Розсилки", callback_data="export_mailings")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="export_stats")],
        [InlineKeyboardButton(text="📋 Аудит логи", callback_data="export_audit")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])

def format_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 CSV", callback_data="format_csv")],
        [InlineKeyboardButton(text="📊 JSON", callback_data="format_json")],
        [InlineKeyboardButton(text="📋 TXT", callback_data="format_txt")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="export_menu")]
    ])

@export_router.callback_query(F.data == "export_menu")
async def export_menu(query: CallbackQuery):
    await query.answer()
    
    text = """📥 <b>ЕКСПОРТ ДАНИХ</b>

<b>Доступні дані для експорту:</b>

👥 <b>Користувачі</b> - список всіх користувачів
🤖 <b>Боти/Сесії</b> - імпортовані сесії
📧 <b>Розсилки</b> - історія розсилок
📊 <b>Статистика</b> - аналітика системи
📋 <b>Аудит логи</b> - журнал дій

<b>Формати:</b> CSV, JSON, TXT"""
    
    await query.message.edit_text(text, reply_markup=export_kb(), parse_mode="HTML")

@export_router.callback_query(F.data == "export_users")
async def export_users(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.update_data(export_type="users")
    
    await query.message.edit_text(
        "👥 <b>ЕКСПОРТ КОРИСТУВАЧІВ</b>\n\nВиберіть формат:",
        reply_markup=format_kb(),
        parse_mode="HTML"
    )

@export_router.callback_query(F.data == "export_bots")
async def export_bots(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.update_data(export_type="bots")
    
    await query.message.edit_text(
        "🤖 <b>ЕКСПОРТ СЕСІЙ</b>\n\nВиберіть формат:",
        reply_markup=format_kb(),
        parse_mode="HTML"
    )

@export_router.callback_query(F.data == "export_mailings")
async def export_mailings(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.update_data(export_type="mailings")
    
    await query.message.edit_text(
        "📧 <b>ЕКСПОРТ РОЗСИЛОК</b>\n\nВиберіть формат:",
        reply_markup=format_kb(),
        parse_mode="HTML"
    )

@export_router.callback_query(F.data == "export_stats")
async def export_stats(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.update_data(export_type="stats")
    
    await query.message.edit_text(
        "📊 <b>ЕКСПОРТ СТАТИСТИКИ</b>\n\nВиберіть формат:",
        reply_markup=format_kb(),
        parse_mode="HTML"
    )

@export_router.callback_query(F.data == "export_audit")
async def export_audit(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.update_data(export_type="audit")
    
    await query.message.edit_text(
        "📋 <b>ЕКСПОРТ АУДИТ ЛОГІВ</b>\n\nВиберіть формат:",
        reply_markup=format_kb(),
        parse_mode="HTML"
    )

@export_router.callback_query(F.data.startswith("format_"))
async def process_format(query: CallbackQuery, state: FSMContext, bot: Bot):
    await query.answer()
    
    format_type = query.data.replace("format_", "")
    data = await state.get_data()
    export_type = data.get("export_type", "users")
    await state.clear()
    
    await query.message.edit_text("🔄 Генерую файл експорту...")
    
    try:
        export_data = await get_export_data(export_type, query.from_user.id)
        
        if format_type == "csv":
            file_content, filename = generate_csv(export_data, export_type)
            content_type = "text/csv"
        elif format_type == "json":
            file_content, filename = generate_json(export_data, export_type)
            content_type = "application/json"
        else:
            file_content, filename = generate_txt(export_data, export_type)
            content_type = "text/plain"
        
        document = BufferedInputFile(
            file=file_content.encode('utf-8'),
            filename=filename
        )
        
        await bot.send_document(
            chat_id=query.from_user.id,
            document=document,
            caption=f"✅ Експорт {export_type} завершено\nЗаписів: {len(export_data)}"
        )
        
        await audit_logger.log(
            user_id=query.from_user.id,
            action="data_exported",
            category=ActionCategory.DATA,
            username=query.from_user.username,
            details={"type": export_type, "format": format_type, "records": len(export_data)}
        )
        
        await query.message.edit_text(
            f"✅ <b>ЕКСПОРТ ЗАВЕРШЕНО</b>\n\nТип: {export_type}\nФормат: {format_type.upper()}\nЗаписів: {len(export_data)}",
            reply_markup=export_kb(),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        await query.message.edit_text(
            f"❌ Помилка експорту: {e}",
            reply_markup=export_kb()
        )

async def get_export_data(export_type: str, user_id: int) -> list:
    from database.crud import UserCRUD, StatsCRUD
    
    if export_type == "users":
        from utils.db import async_session
        from database.models import User
        from sqlalchemy import select
        
        async with async_session() as session:
            result = await session.execute(select(User).limit(1000))
            users = result.scalars().all()
            return [
                {
                    "user_id": u.user_id,
                    "username": u.username,
                    "role": u.role,
                    "is_blocked": u.is_blocked,
                    "created_at": str(u.created_at) if u.created_at else None
                }
                for u in users
            ]
    
    elif export_type == "bots":
        from utils.db import async_session
        from database.models import Bot
        from sqlalchemy import select
        
        async with async_session() as session:
            result = await session.execute(select(Bot).limit(1000))
            bots = result.scalars().all()
            return [
                {
                    "id": b.id,
                    "project_id": b.project_id,
                    "phone": b.phone,
                    "status": b.status,
                    "created_at": str(b.created_at) if b.created_at else None
                }
                for b in bots
            ]
    
    elif export_type == "mailings":
        from utils.db import async_session
        from database.models import MailingTask
        from sqlalchemy import select
        
        async with async_session() as session:
            result = await session.execute(select(MailingTask).limit(1000))
            tasks = result.scalars().all()
            return [
                {
                    "id": t.id,
                    "name": t.name,
                    "status": t.status,
                    "sent_count": t.sent_count,
                    "failed_count": t.failed_count,
                    "created_at": str(t.created_at) if t.created_at else None
                }
                for t in tasks
            ]
    
    elif export_type == "audit":
        from utils.db import async_session
        from database.models import AuditLog
        from sqlalchemy import select
        
        async with async_session() as session:
            result = await session.execute(
                select(AuditLog).order_by(AuditLog.created_at.desc()).limit(1000)
            )
            logs = result.scalars().all()
            return [
                {
                    "id": l.id,
                    "user_id": l.user_id,
                    "action": l.action,
                    "category": l.category,
                    "severity": l.severity,
                    "created_at": str(l.created_at) if l.created_at else None
                }
                for l in logs
            ]
    
    elif export_type == "stats":
        stats = await StatsCRUD.get_user_stats()
        return [stats]
    
    return []

def generate_csv(data: list, export_type: str) -> tuple:
    if not data:
        return "", f"empty_{export_type}.csv"
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    
    filename = f"{export_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return output.getvalue(), filename

def generate_json(data: list, export_type: str) -> tuple:
    content = json.dumps(data, ensure_ascii=False, indent=2, default=str)
    filename = f"{export_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return content, filename

def generate_txt(data: list, export_type: str) -> tuple:
    lines = []
    for item in data:
        line = " | ".join(f"{k}: {v}" for k, v in item.items())
        lines.append(line)
    
    content = "\n".join(lines)
    filename = f"{export_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    return content, filename
