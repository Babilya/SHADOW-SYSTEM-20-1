from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import logging

from config import ADMIN_IDS
from core.audit_logger import audit_logger, ActionCategory, ActionSeverity
from core.alerts import alert_system, AlertType
from middlewares.security_middleware import (
    blocked_users, kicked_users, 
    is_user_blocked, is_user_kicked,
    block_user, kick_user, unblock_user, clear_kick,
    persist_block, persist_kick, persist_unblock
)

logger = logging.getLogger(__name__)
security_router = Router()

class SecurityStates(StatesGroup):
    ban_reason = State()
    kick_reason = State()
    target_user = State()

def security_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚫 Заблокувати", callback_data="sec_ban"),
         InlineKeyboardButton(text="👢 Кікнути", callback_data="sec_kick")],
        [InlineKeyboardButton(text="✅ Розблокувати", callback_data="sec_unban")],
        [InlineKeyboardButton(text="📋 Список блокувань", callback_data="sec_list")],
        [InlineKeyboardButton(text="📊 Security Monitor", callback_data="sec_monitor")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])

@security_router.message(Command("security"))
async def security_command(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await audit_logger.log_security(
            user_id=message.from_user.id,
            action="unauthorized_security_access",
            username=message.from_user.username,
            severity=ActionSeverity.WARNING
        )
        await message.answer("❌ Доступ заборонено")
        return
    
    text = f"""🛡️ <b>SECURITY CENTER</b>

<b>📊 Статистика:</b>
├ Заблокованих: {sum(1 for u in blocked_users.values() if u.get('is_blocked'))}
├ Кікнутих: {sum(1 for u in kicked_users.values() if u.get('requires_new_key'))}
└ Загроз сьогодні: 0

<b>⚠️ Останні інциденти:</b>
Немає критичних інцидентів

Виберіть дію:"""
    
    await message.answer(text, reply_markup=security_kb(), parse_mode="HTML")

@security_router.callback_query(F.data == "sec_ban")
async def sec_ban(query: CallbackQuery, state: FSMContext):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    await state.set_state(SecurityStates.target_user)
    await state.update_data(action="ban")
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="security_menu")]
    ])
    
    await query.message.edit_text(
        "🚫 <b>БЛОКУВАННЯ КОРИСТУВАЧА</b>\n\n"
        "Введіть User ID або @username для блокування:",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@security_router.callback_query(F.data == "sec_kick")
async def sec_kick(query: CallbackQuery, state: FSMContext):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    await state.set_state(SecurityStates.target_user)
    await state.update_data(action="kick")
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="security_menu")]
    ])
    
    await query.message.edit_text(
        "👢 <b>КІК КОРИСТУВАЧА</b>\n\n"
        "Введіть User ID або @username.\n"
        "Користувачу буде скинуто FSM і вимагатиметься новий ключ:",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@security_router.message(SecurityStates.target_user)
async def process_target_user(message: Message, state: FSMContext):
    target = message.text.strip()
    await state.update_data(target=target)
    
    data = await state.get_data()
    action = data.get("action")
    
    if action == "ban":
        await state.set_state(SecurityStates.ban_reason)
        await message.answer(
            "📝 Введіть причину блокування та юридичну підставу:\n\n"
            "<i>Формат: Причина | Юридична підстава</i>\n"
            "<i>Приклад: Спам | Стаття 190 ККУ</i>",
            parse_mode="HTML"
        )
    else:
        await state.set_state(SecurityStates.kick_reason)
        await message.answer("📝 Введіть причину кіку:")

@security_router.message(SecurityStates.ban_reason)
async def process_ban(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    target = data.get("target")
    
    parts = message.text.split("|")
    reason = parts[0].strip()
    legal_basis = parts[1].strip() if len(parts) > 1 else "Не вказано"
    
    try:
        user_id = int(target.replace("@", ""))
    except ValueError:
        user_id = hash(target) % 1000000000
    
    block_user(user_id, message.from_user.id, reason, legal_basis)
    await persist_block(user_id, message.from_user.id, reason, legal_basis)
    
    await audit_logger.log_security(
        user_id=message.from_user.id,
        action="user_banned",
        username=message.from_user.username,
        severity=ActionSeverity.CRITICAL,
        details={
            "target": target,
            "target_id": user_id,
            "reason": reason,
            "legal_basis": legal_basis,
            "admin_id": message.from_user.id
        }
    )
    
    await alert_system.send_alert(
        alert_type=AlertType.CRITICAL,
        title="🚫 Користувача заблоковано",
        message=f"Target: {target}\nПричина: {reason}\nПідстава: {legal_basis}\nАдмін: @{message.from_user.username}"
    )
    
    await message.answer(
        f"""✅ <b>КОРИСТУВАЧА ЗАБЛОКОВАНО</b>

<b>Ціль:</b> {target}
<b>Причина:</b> {reason}
<b>Юридична підстава:</b> {legal_basis}
<b>Адмін:</b> @{message.from_user.username}
<b>Час:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}

<i>Записано в AuditLog</i>""",
        parse_mode="HTML"
    )
    await state.clear()

@security_router.message(SecurityStates.kick_reason)
async def process_kick(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    target = data.get("target")
    reason = message.text
    
    try:
        user_id = int(target.replace("@", ""))
    except ValueError:
        user_id = hash(target) % 1000000000
    
    kick_user(user_id, message.from_user.id, reason)
    await persist_kick(user_id, message.from_user.id, reason)
    
    await audit_logger.log_security(
        user_id=message.from_user.id,
        action="user_kicked",
        username=message.from_user.username,
        severity=ActionSeverity.WARNING,
        details={
            "target": target,
            "target_id": user_id,
            "reason": reason,
            "requires_new_key": True,
            "admin_id": message.from_user.id
        }
    )
    
    await message.answer(
        f"""👢 <b>КОРИСТУВАЧА КІКНУТО</b>

<b>Ціль:</b> {target}
<b>Причина:</b> {reason}
<b>Статус:</b> FSM скинуто, вимагається новий ключ

<i>Записано в AuditLog</i>""",
        parse_mode="HTML"
    )
    await state.clear()

@security_router.callback_query(F.data == "sec_unban")
async def sec_unban(query: CallbackQuery, state: FSMContext):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    blocked = [(uid, data) for uid, data in blocked_users.items() if data.get("is_blocked")]
    
    if not blocked:
        await query.answer("Немає заблокованих користувачів")
        return
    
    kb_buttons = []
    for uid, data in blocked[:10]:
        kb_buttons.append([
            InlineKeyboardButton(
                text=f"🔓 {uid} ({data.get('reason', 'N/A')[:20]})",
                callback_data=f"unban_{uid}"
            )
        ])
    kb_buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="security_menu")])
    
    await query.message.edit_text(
        "✅ <b>РОЗБЛОКУВАННЯ</b>\n\nВиберіть користувача:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_buttons),
        parse_mode="HTML"
    )
    await query.answer()

@security_router.callback_query(F.data.startswith("unban_"))
async def process_unban(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    user_id = int(query.data.split("_")[1])
    unblock_user(user_id)
    await persist_unblock(user_id)
    
    await audit_logger.log_security(
        user_id=query.from_user.id,
        action="user_unbanned",
        username=query.from_user.username,
        details={"target_id": user_id}
    )
    
    await query.message.edit_text(f"✅ Користувача {user_id} розблоковано")
    await query.answer("Розблоковано!")

@security_router.callback_query(F.data == "sec_list")
async def sec_list(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    blocked = [(uid, data) for uid, data in blocked_users.items() if data.get("is_blocked")]
    kicked = [(uid, data) for uid, data in kicked_users.items() if data.get("requires_new_key")]
    
    text = "📋 <b>СПИСОК БЛОКУВАНЬ</b>\n\n"
    
    text += "<b>🚫 Заблоковані:</b>\n"
    if blocked:
        for uid, data in blocked[:5]:
            text += f"├ {uid}: {data.get('reason', 'N/A')[:30]}\n"
    else:
        text += "├ Немає\n"
    
    text += "\n<b>👢 Кікнуті (очікують ключ):</b>\n"
    if kicked:
        for uid, data in kicked[:5]:
            text += f"├ {uid}: {data.get('reason', 'N/A')[:30]}\n"
    else:
        text += "├ Немає\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="security_menu")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()

@security_router.callback_query(F.data == "sec_monitor")
async def sec_monitor(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    recent_security = audit_logger.get_by_category(ActionCategory.SECURITY, 10)
    
    text = "📊 <b>SECURITY MONITOR</b>\n\n"
    text += "<b>🔐 Останні події безпеки:</b>\n"
    
    if recent_security:
        for log in recent_security[-5:]:
            severity_icon = "🔴" if log.severity == ActionSeverity.CRITICAL else "🟡" if log.severity == ActionSeverity.WARNING else "🟢"
            text += f"{severity_icon} {log.action} | {log.timestamp.strftime('%H:%M')}\n"
    else:
        text += "Немає подій\n"
    
    text += f"\n<b>📈 Статистика:</b>\n"
    text += f"├ Всього подій: {len(audit_logger.entries)}\n"
    text += f"├ Критичних: {len(audit_logger.get_critical_logs())}\n"
    text += f"└ Безпека: {len(recent_security)}\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="sec_monitor")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="security_menu")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()

@security_router.callback_query(F.data == "security_menu")
async def security_menu(query: CallbackQuery):
    text = f"""🛡️ <b>SECURITY CENTER</b>

<b>📊 Статистика:</b>
├ Заблокованих: {sum(1 for u in blocked_users.values() if u.get('is_blocked'))}
├ Кікнутих: {sum(1 for u in kicked_users.values() if u.get('requires_new_key'))}
└ Загроз сьогодні: 0

Виберіть дію:"""
    
    await query.message.edit_text(text, reply_markup=security_kb(), parse_mode="HTML")
    await query.answer()
