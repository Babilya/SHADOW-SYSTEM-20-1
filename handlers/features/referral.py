from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
import hashlib
import logging

from config import ADMIN_IDS
from core.audit_logger import audit_logger, ActionCategory

logger = logging.getLogger(__name__)
referral_router = Router()

referrals_storage = {}
referral_links = {}
user_parent_map = {}

def generate_referral_code(user_id: int) -> str:
    data = f"{user_id}_{datetime.now().timestamp()}"
    return hashlib.md5(data.encode()).hexdigest()[:8].upper()

def get_referral_link(user_id: int, bot_username: str = "SH_SYSTEMbot") -> str:
    if user_id not in referral_links:
        code = generate_referral_code(user_id)
        referral_links[user_id] = code
        referrals_storage[code] = {
            "owner_id": user_id,
            "created_at": datetime.now().isoformat(),
            "referrals": [],
            "total_earnings": 0
        }
    
    code = referral_links[user_id]
    return f"https://t.me/{bot_username}?start=ref_{code}"

def get_parent_leader_id(user_id: int) -> int | None:
    return user_parent_map.get(user_id)

def process_referral(new_user_id: int, referral_code: str) -> bool:
    if referral_code not in referrals_storage:
        return False
    
    ref_data = referrals_storage[referral_code]
    parent_id = ref_data["owner_id"]
    
    if new_user_id == parent_id:
        return False
    
    existing_ids = [r["user_id"] for r in ref_data["referrals"]]
    if new_user_id in existing_ids:
        return False
    
    ref_data["referrals"].append({
        "user_id": new_user_id,
        "joined_at": datetime.now().isoformat(),
        "status": "pending"
    })
    
    user_parent_map[new_user_id] = parent_id
    
    return True

def get_referral_stats(user_id: int) -> dict:
    code = referral_links.get(user_id)
    if not code or code not in referrals_storage:
        return {"total": 0, "active": 0, "earnings": 0}
    
    ref_data = referrals_storage[code]
    return {
        "total": len(ref_data["referrals"]),
        "active": sum(1 for r in ref_data["referrals"] if r.get("status") == "active"),
        "earnings": ref_data["total_earnings"]
    }

def referral_kb(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Моє посилання", callback_data="ref_my_link")],
        [InlineKeyboardButton(text="👥 Мої реферали", callback_data="ref_my_referrals")],
        [InlineKeyboardButton(text="💰 Бонуси", callback_data="ref_bonuses")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="ref_stats")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="user_menu")]
    ])

@referral_router.message(Command("referral"))
async def referral_command(message: Message):
    stats = get_referral_stats(message.from_user.id)
    
    text = f"""🔗 <b>РЕФЕРАЛЬНА ПРОГРАМА</b>

<b>📊 Ваша статистика:</b>
├ Запрошено: {stats['total']}
├ Активних: {stats['active']}
└ Зароблено: {stats['earnings']} ₴

<b>💰 Бонуси:</b>
• +10% від першої оплати реферала
• +5% від наступних оплат
• Бонусні дні підписки

Виберіть дію:"""
    
    await message.answer(text, reply_markup=referral_kb(message.from_user.id), parse_mode="HTML")

@referral_router.callback_query(F.data == "ref_my_link")
async def ref_my_link(query: CallbackQuery):
    link = get_referral_link(query.from_user.id)
    
    text = f"""🔗 <b>ВАШЕ РЕФЕРАЛЬНЕ ПОСИЛАННЯ</b>

<code>{link}</code>

<i>Натисніть на посилання щоб скопіювати</i>

<b>Як це працює:</b>
1. Поділіться посиланням з друзями
2. Вони реєструються за вашим посиланням
3. Ви отримуєте бонуси від їх оплат

<b>Ваші бонуси:</b>
• 10% від першої оплати
• 5% від наступних оплат
• Бонусні дні підписки"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Поділитися", switch_inline_query=f"Приєднуйся до SHADOW SYSTEM: {link}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="referral_menu")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()

@referral_router.callback_query(F.data == "ref_my_referrals")
async def ref_my_referrals(query: CallbackQuery):
    code = referral_links.get(query.from_user.id)
    
    if not code or code not in referrals_storage:
        await query.message.edit_text(
            "👥 <b>МОЇ РЕФЕРАЛИ</b>\n\nУ вас поки немає рефералів.\n\nПоділіться вашим посиланням!",
            reply_markup=referral_kb(query.from_user.id),
            parse_mode="HTML"
        )
        await query.answer()
        return
    
    ref_data = referrals_storage[code]
    referrals = ref_data["referrals"]
    
    text = f"👥 <b>МОЇ РЕФЕРАЛИ ({len(referrals)})</b>\n\n"
    
    if referrals:
        for i, ref in enumerate(referrals[-10:], 1):
            status_icon = "🟢" if ref.get("status") == "active" else "🟡"
            text += f"{i}. {status_icon} ID: {ref['user_id']} | {ref['joined_at'][:10]}\n"
    else:
        text += "Поки немає рефералів"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="referral_menu")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()

@referral_router.callback_query(F.data == "ref_bonuses")
async def ref_bonuses(query: CallbackQuery):
    stats = get_referral_stats(query.from_user.id)
    
    text = f"""💰 <b>БОНУСИ</b>

<b>💵 Зароблено всього:</b> {stats['earnings']} ₴

<b>📋 Структура бонусів:</b>
├ 10% від першої оплати реферала
├ 5% від наступних оплат
├ +3 дні підписки за кожного
└ +7 днів за 5 рефералів

<b>🎁 Досягнення:</b>
{'✅' if stats['total'] >= 1 else '⬜'} 1 реферал - +3 дні
{'✅' if stats['total'] >= 5 else '⬜'} 5 рефералів - +7 днів
{'✅' if stats['total'] >= 10 else '⬜'} 10 рефералів - +15 днів
{'✅' if stats['total'] >= 25 else '⬜'} 25 рефералів - +30 днів"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💸 Вивести бонуси", callback_data="ref_withdraw")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="referral_menu")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()

@referral_router.callback_query(F.data == "ref_stats")
async def ref_stats(query: CallbackQuery):
    stats = get_referral_stats(query.from_user.id)
    code = referral_links.get(query.from_user.id, "N/A")
    
    text = f"""📊 <b>СТАТИСТИКА</b>

<b>🔗 Ваш код:</b> <code>{code}</code>

<b>📈 Показники:</b>
├ Всього переходів: ~{stats['total'] * 3}
├ Реєстрацій: {stats['total']}
├ Активних: {stats['active']}
├ Конверсія: {(stats['active'] / max(stats['total'], 1) * 100):.1f}%
└ Зароблено: {stats['earnings']} ₴

<b>📅 За періодами:</b>
├ Сьогодні: 0
├ Цього тижня: 0
└ Цього місяця: {stats['total']}"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="ref_stats")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="referral_menu")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()

@referral_router.callback_query(F.data == "ref_withdraw")
async def ref_withdraw(query: CallbackQuery):
    stats = get_referral_stats(query.from_user.id)
    
    if stats['earnings'] < 100:
        await query.answer("Мінімальна сума виводу: 100 ₴", show_alert=True)
        return
    
    await query.answer("Заявка на вивід створена!")

@referral_router.callback_query(F.data == "referral_menu")
async def referral_menu(query: CallbackQuery):
    stats = get_referral_stats(query.from_user.id)
    
    text = f"""🔗 <b>РЕФЕРАЛЬНА ПРОГРАМА</b>

<b>📊 Ваша статистика:</b>
├ Запрошено: {stats['total']}
├ Активних: {stats['active']}
└ Зароблено: {stats['earnings']} ₴

Виберіть дію:"""
    
    await query.message.edit_text(text, reply_markup=referral_kb(query.from_user.id), parse_mode="HTML")
    await query.answer()
