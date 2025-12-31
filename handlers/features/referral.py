from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
import logging

from config import ADMIN_IDS
from core.audit_logger import audit_logger, ActionCategory
from core.referral_system import referral_system, ReferralTier

logger = logging.getLogger(__name__)
referral_router = Router()


def get_referral_link(user_id: int, bot_username: str = "SH_SYSTEMbot") -> str:
    user = referral_system.users.get(user_id)
    if not user:
        user = referral_system.register_user(user_id)
    return f"https://t.me/{bot_username}?start=ref_{user.referral_code}"


def process_referral(new_user_id: int, referral_code: str) -> bool:
    if referral_code in referral_system.codes:
        referral_system.register_user(new_user_id, referral_code)
        return True
    return False


def get_parent_leader_id(user_id: int) -> int | None:
    user = referral_system.users.get(user_id)
    return user.referrer_id if user else None


def referral_kb(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Моє посилання", callback_data="ref_my_link")],
        [InlineKeyboardButton(text="👥 Мої реферали", callback_data="ref_my_referrals")],
        [InlineKeyboardButton(text="💰 Бонуси", callback_data="ref_bonuses")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="ref_stats")],
        [InlineKeyboardButton(text="🏆 Рейтинг", callback_data="ref_leaderboard")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="user_menu")]
    ])


@referral_router.message(Command("referral"))
async def referral_command(message: Message):
    user_id = message.from_user.id
    
    if user_id not in referral_system.users:
        referral_system.register_user(user_id)
    
    stats = referral_system.get_user_stats(user_id)
    tier_name = referral_system._get_tier_name(ReferralTier(stats['tier']))
    
    text = f"""🔗 <b>РЕФЕРАЛЬНА ПРОГРАМА</b>

<b>Ваш рівень:</b> {tier_name}

<b>📊 Ваша статистика:</b>
├ Запрошено: {stats['total_referrals']}
├ Активних: {stats['active_referrals']}
├ Бонусних днів: +{stats['bonus_days_earned']}
└ Зароблено: {stats['total_earnings']:.2f} ₴

<b>💰 Бонуси вашого рівня:</b>
├ Рівень 1: {stats['bonuses'].get(1, 0)}%
├ Рівень 2: {stats['bonuses'].get(2, 0)}%
└ Рівень 3: {stats['bonuses'].get(3, 0)}%

Виберіть дію:"""
    
    await message.answer(text, reply_markup=referral_kb(message.from_user.id), parse_mode="HTML")


@referral_router.callback_query(F.data == "ref_my_link")
async def ref_my_link(query: CallbackQuery):
    user_id = query.from_user.id
    link = get_referral_link(user_id)
    stats = referral_system.get_user_stats(user_id)
    
    text = f"""🔗 <b>ВАШЕ РЕФЕРАЛЬНЕ ПОСИЛАННЯ</b>

<code>{link}</code>

<i>Натисніть на посилання щоб скопіювати</i>

<b>Як це працює:</b>
1. Поділіться посиланням з друзями
2. Вони реєструються за вашим посиланням
3. Ви отримуєте бонуси від їх оплат

<b>🎁 Ваші бонуси ({referral_system._get_tier_name(ReferralTier(stats['tier']))}):</b>
├ {stats['bonuses'].get(1, 0)}% від оплат рефералів 1-го рівня
├ {stats['bonuses'].get(2, 0)}% від оплат рефералів 2-го рівня
└ {stats['bonuses'].get(3, 0)}% від оплат рефералів 3-го рівня

<b>📅 +{stats['bonus_days_per_referral']} днів</b> підписки за кожного реферала!"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Поділитися", switch_inline_query=f"Приєднуйся до SHADOW SYSTEM: {link}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="referral_menu")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()


@referral_router.callback_query(F.data == "ref_my_referrals")
async def ref_my_referrals(query: CallbackQuery):
    user_id = query.from_user.id
    
    referrals = [
        u for u in referral_system.users.values()
        if u.referrer_id == user_id
    ]
    
    text = f"👥 <b>МОЇ РЕФЕРАЛИ ({len(referrals)})</b>\n\n"
    
    if referrals:
        for i, ref in enumerate(referrals[-10:], 1):
            tier = referral_system._get_tier_name(ref.tier)
            joined = ref.joined_at.strftime('%d.%m.%Y')
            text += f"{i}. {tier} ID: {ref.user_id} | {joined}\n"
        
        if len(referrals) > 10:
            text += f"\n<i>... та ще {len(referrals) - 10}</i>"
    else:
        text += "Поки немає рефералів.\n\n<i>Поділіться вашим посиланням!</i>"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌳 Дерево рефералів", callback_data="ref_tree")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="referral_menu")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()


@referral_router.callback_query(F.data == "ref_tree")
async def ref_tree(query: CallbackQuery):
    user_id = query.from_user.id
    tree = referral_system.get_referral_tree(user_id, depth=3)
    
    def format_tree(node: dict, level: int = 0) -> str:
        if not node or "error" in node:
            return ""
        
        prefix = "  " * level + ("└ " if level > 0 else "")
        tier_name = referral_system._get_tier_name(ReferralTier(node.get("tier", "bronze")))
        result = f"{prefix}{tier_name} ID: {node['user_id']}\n"
        
        for child in node.get("referrals", [])[:5]:
            result += format_tree(child, level + 1)
        
        return result
    
    tree_text = format_tree(tree) or "Немає рефералів"
    
    text = f"""🌳 <b>ДЕРЕВО РЕФЕРАЛІВ</b>

<code>{tree_text}</code>

<i>Показано до 3 рівнів глибини</i>"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="ref_my_referrals")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()


@referral_router.callback_query(F.data == "ref_bonuses")
async def ref_bonuses(query: CallbackQuery):
    user_id = query.from_user.id
    stats = referral_system.get_user_stats(user_id)
    
    achievements = ""
    milestones = [1, 5, 10, 25, 50, 100]
    for m in milestones:
        bonus = referral_system.ACHIEVEMENT_BONUSES.get(m, {})
        icon = "✅" if stats['total_referrals'] >= m else "⬜"
        achievements += f"{icon} {m} реферал{'ів' if m > 1 else ''} - +{bonus.get('days', 0)} днів\n"
    
    text = f"""💰 <b>БОНУСИ</b>

<b>💵 Баланс:</b>
├ Всього зароблено: {stats['total_earnings']:.2f} ₴
├ Доступно до виводу: {stats['pending_earnings']:.2f} ₴
└ Виведено: {stats['withdrawn_earnings']:.2f} ₴

<b>📋 Структура бонусів ({referral_system._get_tier_name(ReferralTier(stats['tier']))}):</b>
├ Рівень 1: {stats['bonuses'].get(1, 0)}% від оплат
├ Рівень 2: {stats['bonuses'].get(2, 0)}% від оплат
└ Рівень 3: {stats['bonuses'].get(3, 0)}% від оплат

<b>📅 Бонус днів:</b> +{stats['bonus_days_per_referral']} за реферала

<b>🏆 Досягнення:</b>
{achievements}
<b>Бонусних днів зароблено:</b> +{stats['bonus_days_earned']}"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💸 Вивести бонуси", callback_data="ref_withdraw")],
        [InlineKeyboardButton(text="🎯 Рівні та бонуси", callback_data="ref_tiers")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="referral_menu")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()


@referral_router.callback_query(F.data == "ref_tiers")
async def ref_tiers(query: CallbackQuery):
    user_id = query.from_user.id
    stats = referral_system.get_user_stats(user_id)
    current_tier = stats['tier']
    
    tiers_info = ""
    for tier in ReferralTier:
        threshold = referral_system.TIER_THRESHOLDS[tier]
        bonuses = referral_system.TIER_BONUSES[tier]
        bonus_days = referral_system.TIER_BONUS_DAYS[tier]
        tier_name = referral_system._get_tier_name(tier)
        
        is_current = tier.value == current_tier
        marker = "👉 " if is_current else "   "
        
        tiers_info += f"""{marker}<b>{tier_name}</b>
   ├ Поріг: {threshold}+ рефералів
   ├ L1: {bonuses[1]}% | L2: {bonuses[2]}% | L3: {bonuses[3]}%
   └ +{bonus_days} днів/реферал

"""
    
    text = f"""🎯 <b>РІВНІ РЕФЕРАЛЬНОЇ ПРОГРАМИ</b>

<b>Ваш прогрес:</b> {stats['tier_progress']}% до наступного рівня

{tiers_info}"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="ref_bonuses")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()


@referral_router.callback_query(F.data == "ref_stats")
async def ref_stats(query: CallbackQuery):
    user_id = query.from_user.id
    text = referral_system.format_stats_message(user_id)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="ref_stats")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="referral_menu")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()


@referral_router.callback_query(F.data == "ref_leaderboard")
async def ref_leaderboard(query: CallbackQuery):
    leaderboard = referral_system.get_leaderboard(10)
    user_id = query.from_user.id
    
    text = "🏆 <b>ТОП-10 РЕФЕРАЛІВ</b>\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    
    for entry in leaderboard:
        rank = entry['rank']
        medal = medals[rank - 1] if rank <= 3 else f"{rank}."
        is_you = " (Ви)" if entry['user_id'] == user_id else ""
        
        text += f"{medal} {entry['tier']} - {entry['referrals']} реф. | {entry['earnings']:.0f}₴{is_you}\n"
    
    if not leaderboard:
        text += "Поки немає даних"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="ref_leaderboard")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="referral_menu")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()


@referral_router.callback_query(F.data == "ref_withdraw")
async def ref_withdraw(query: CallbackQuery):
    user_id = query.from_user.id
    result = referral_system.request_withdrawal(user_id)
    
    if "error" in result:
        await query.answer(result["error"], show_alert=True)
        return
    
    text = f"""💸 <b>ЗАЯВКА НА ВИВІД</b>

<b>Сума:</b> {result['amount']:.2f} ₴
<b>Залишок:</b> {result['remaining']:.2f} ₴

✅ Заявка створена! Очікуйте виплату протягом 24 годин.

<i>Для виводу зв'яжіться з адміністратором.</i>"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="ref_bonuses")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer("Заявка на вивід створена!")


@referral_router.callback_query(F.data == "referral_menu")
async def referral_menu(query: CallbackQuery):
    user_id = query.from_user.id
    
    if user_id not in referral_system.users:
        referral_system.register_user(user_id)
    
    stats = referral_system.get_user_stats(user_id)
    tier_name = referral_system._get_tier_name(ReferralTier(stats['tier']))
    
    text = f"""🔗 <b>РЕФЕРАЛЬНА ПРОГРАМА</b>

<b>Ваш рівень:</b> {tier_name}

<b>📊 Ваша статистика:</b>
├ Запрошено: {stats['total_referrals']}
├ Активних: {stats['active_referrals']}
└ Зароблено: {stats['total_earnings']:.2f} ₴

Виберіть дію:"""
    
    await query.message.edit_text(text, reply_markup=referral_kb(user_id), parse_mode="HTML")
    await query.answer()
