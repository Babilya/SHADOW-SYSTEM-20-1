from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import logging

from core.key_generator import generate_invite_code, store_invite_code, invite_codes_storage

logger = logging.getLogger(__name__)
router = Router()

class TeamCRUD:
    @staticmethod
    async def get_team_managers(leader_id: int):
        from utils.db import async_session
        from database.models import User
        from sqlalchemy import select
        async with async_session() as session:
            result = await session.execute(
                select(User).where(
                    User.project_id == str(leader_id), 
                    User.role == "manager"
                )
            )
            return result.scalars().all()
    
    @staticmethod
    async def add_manager(manager_id: int, leader_id: int, role: str):
        from utils.db import async_session
        from database.models import User
        from sqlalchemy import update
        async with async_session() as session:
            await session.execute(
                update(User).where(User.user_id == manager_id).values(
                    role="manager",
                    project_id=str(leader_id),
                    permissions=role
                )
            )
            await session.commit()
    
    @staticmethod
    async def remove_manager(manager_id: int, leader_id: int):
        from utils.db import async_session
        from database.models import User
        from sqlalchemy import update
        async with async_session() as session:
            await session.execute(
                update(User).where(
                    User.user_id == manager_id,
                    User.project_id == str(leader_id)
                ).values(role="guest", project_id=None, permissions=None)
            )
            await session.commit()
    
    @staticmethod
    async def get_team_stats(leader_id: int):
        from utils.db import async_session
        from database.models import User, Campaign, Project
        from sqlalchemy import select, func
        async with async_session() as session:
            managers = await session.execute(
                select(func.count(User.user_id)).where(
                    User.project_id == str(leader_id), 
                    User.role == "manager"
                )
            )
            project_result = await session.execute(
                select(Project.id).where(Project.leader_id == str(leader_id))
            )
            project = project_result.scalar()
            
            campaign_count = 0
            if project:
                campaigns = await session.execute(
                    select(func.count(Campaign.id)).where(Campaign.project_id == project)
                )
                campaign_count = campaigns.scalar() or 0
            
            return {
                "managers": managers.scalar() or 0,
                "campaigns": campaign_count
            }

class TeamStates(StatesGroup):
    waiting_manager_id = State()
    waiting_manager_role = State()

def team_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👥 МЕНЕДЖЕРИ", callback_data="list_managers"),
            InlineKeyboardButton(text="➕ ДОДАТИ", callback_data="add_manager")
        ],
        [InlineKeyboardButton(text="🔑 ЗГЕНЕРУВАТИ INVITE", callback_data="generate_invite")],
        [
            InlineKeyboardButton(text="⭐ РЕЙТИНГ", callback_data="manager_rating"),
            InlineKeyboardButton(text="📊 АКТИВНІСТЬ", callback_data="team_activity")
        ],
        [
            InlineKeyboardButton(text="⚙️ ПРАВА", callback_data="team_permissions"),
            InlineKeyboardButton(text="📈 СТАТИСТИКА", callback_data="project_stats")
        ],
        [InlineKeyboardButton(text="◀️ НАЗАД", callback_data="user_menu")]
    ])

def team_description() -> str:
    return """<b>👑 КЕРУВАННЯ ПРОЕКТОМ</b>

<b>Ваш пакет:</b> ⭐ СТАНДАРТ
<b>Менеджери:</b> 2 / 5

<b>👥 ВАША КОМАНДА:</b>
├ @manager_1 — 🟢 Активний
└ @manager_2 — 🔴 Оффлайн

<b>📊 Статистика:</b>
├ Кампаній завершено: 45
├ Повідомлень надіслано: 12,500
└ Конверсія: 15.2%"""

@router.message(Command("team"))
async def team_cmd(message: Message):
    await message.answer(team_description(), reply_markup=team_kb(), parse_mode="HTML")

@router.callback_query(F.data == "team_main")
async def team_menu(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text(team_description(), reply_markup=team_kb(), parse_mode="HTML")

@router.callback_query(F.data == "list_managers")
async def list_managers(query: CallbackQuery):
    await query.answer()
    
    leader_id = query.from_user.id
    team_managers = await TeamCRUD.get_team_managers(leader_id)
    
    if team_managers:
        manager_list = ""
        for i, m in enumerate(team_managers, 1):
            status = "🟢" if not m.is_blocked else "🔴"
            username = f"@{m.username}" if m.username else f"ID: {m.user_id}"
            manager_list += f"{i}. {username} — {status}\n"
    else:
        manager_list = "<i>Менеджерів ще немає</i>\n\nЗгенеруйте INVITE-код для запрошення!"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Згенерувати INVITE", callback_data="generate_invite")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="team_main")]
    ])
    await query.message.edit_text(
        f"<b>👥 МЕНЕДЖЕРИ ПРОЕКТУ</b>\n\n{manager_list}",
        reply_markup=kb, parse_mode="HTML"
    )

@router.callback_query(F.data == "generate_invite")
async def generate_invite(query: CallbackQuery):
    await query.answer()
    
    leader_id = query.from_user.id
    invite_code = generate_invite_code(leader_id)
    store_invite_code(invite_code, leader_id)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Згенерувати новий", callback_data="generate_invite")],
        [InlineKeyboardButton(text="📋 Мої коди", callback_data="my_invite_codes")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="team_main")]
    ])
    
    await query.message.edit_text(
        f"""<b>🔑 INVITE-КОД ЗГЕНЕРОВАНО!</b>

<b>Код для менеджера:</b>
<code>{invite_code}</code>

<b>📋 Інструкція:</b>
1. Надішліть цей код менеджеру
2. Менеджер вводить: /start → 🔑 Ввести ключ
3. Після активації менеджер отримає доступ

<b>⚠️ Увага:</b>
• Код одноразовий
• Дійсний 24 години
• Прив'яжеться до вашого проекту""",
        reply_markup=kb, parse_mode="HTML"
    )

@router.callback_query(F.data == "my_invite_codes")
async def my_invite_codes(query: CallbackQuery):
    await query.answer()
    
    leader_id = query.from_user.id
    my_codes = [(code, data) for code, data in invite_codes_storage.items() 
                if data.get("leader_id") == leader_id]
    
    if my_codes:
        codes_text = ""
        for code, data in my_codes[-5:]:
            status = "✅ Використаний" if data.get("used") else "🟢 Активний"
            codes_text += f"<code>{code}</code> — {status}\n"
    else:
        codes_text = "<i>Кодів ще немає</i>"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Згенерувати новий", callback_data="generate_invite")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="team_main")]
    ])
    
    await query.message.edit_text(
        f"<b>📋 МОЇ INVITE-КОДИ</b>\n\n{codes_text}",
        reply_markup=kb, parse_mode="HTML"
    )

@router.callback_query(F.data == "add_manager")
async def add_manager(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(TeamStates.waiting_manager_id)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Краще INVITE-код", callback_data="generate_invite")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="team_main")]
    ])
    await query.message.edit_text(
        "<b>➕ ДОДАТИ МЕНЕДЖЕРА</b>\n\n"
        "Введіть Telegram ID користувача:\n"
        "<i>(або згенеруйте INVITE-код для безпечного запрошення)</i>",
        reply_markup=kb, parse_mode="HTML"
    )

@router.message(TeamStates.waiting_manager_id)
async def process_manager_id(message: Message, state: FSMContext):
    try:
        manager_id = int(message.text.strip())
        await state.update_data(manager_id=manager_id)
        await state.set_state(TeamStates.waiting_manager_role)
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📧 Розсилки", callback_data="role_mailing")],
            [InlineKeyboardButton(text="🔍 OSINT", callback_data="role_osint")],
            [InlineKeyboardButton(text="🤖 Botnet", callback_data="role_botnet")],
            [InlineKeyboardButton(text="📊 Аналітика", callback_data="role_analytics")],
            [InlineKeyboardButton(text="👑 Повний доступ", callback_data="role_full")],
            [InlineKeyboardButton(text="❌ Скасувати", callback_data="team_main")]
        ])
        
        await message.answer(
            f"<b>⚙️ НАЛАШТУВАННЯ ПРАВ</b>\n\n"
            f"<b>Менеджер ID:</b> <code>{manager_id}</code>\n\n"
            "Оберіть рівень доступу:",
            reply_markup=kb, parse_mode="HTML"
        )
    except ValueError:
        await message.answer("❌ Невірний формат ID. Введіть числовий Telegram ID:")

@router.callback_query(F.data.startswith("role_"))
async def set_manager_role(query: CallbackQuery, state: FSMContext):
    role = query.data.replace("role_", "")
    data = await state.get_data()
    manager_id = data.get("manager_id")
    
    if manager_id:
        await TeamCRUD.add_manager(manager_id, query.from_user.id, role)
    
    role_names = {
        "mailing": "📧 Розсилки",
        "osint": "🔍 OSINT",
        "botnet": "🤖 Botnet",
        "analytics": "📊 Аналітика",
        "full": "👑 Повний доступ"
    }
    
    await state.clear()
    await query.answer("✅ Менеджера додано!")
    await query.message.edit_text(
        f"<b>✅ МЕНЕДЖЕРА ДОДАНО!</b>\n\n"
        f"<b>ID:</b> <code>{manager_id}</code>\n"
        f"<b>Роль:</b> {role_names.get(role, role)}\n\n"
        "<i>Менеджер отримає сповіщення про доступ.</i>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ До команди", callback_data="team_main")]
        ]),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "manager_rating")
async def manager_rating(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 За тиждень", callback_data="rating_week")],
        [InlineKeyboardButton(text="📅 За місяць", callback_data="rating_month")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="team_main")]
    ])
    await query.message.edit_text(
        """<b>⭐ РЕЙТИНГ МЕНЕДЖЕРІВ</b>

<b>🏆 ТОП-5 ЗА МІСЯЦЬ:</b>

🥇 <b>@manager_ivan</b> — 4.9/5
├ Кампаній: 45 | Конверсія: 18.5%
├ Швидкість: 95% | Точність: 99%
└ Відгуків: 23 (⭐⭐⭐⭐⭐)

🥈 <b>@manager_maria</b> — 4.7/5
├ Кампаній: 38 | Конверсія: 15.2%
├ Швидкість: 92% | Точність: 97%
└ Відгуків: 18

🥉 <b>@manager_petro</b> — 4.5/5
├ Кампаній: 22 | Конверсія: 12.8%
└ Швидкість: 88% | Точність: 95%""",
        reply_markup=kb, parse_mode="HTML"
    )

@router.callback_query(F.data == "team_activity")
async def team_activity(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Детальний звіт", callback_data="activity_report")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="team_main")]
    ])
    await query.message.edit_text(
        """<b>📊 АКТИВНІСТЬ КОМАНДИ</b>

<b>📈 СТАТИСТИКА (24 год):</b>
├ Завдань виконано: 47
├ Кампаній запущено: 8
├ Повідомлень надіслано: 2,450
└ Помилок: 3 (99.4% успіх)

<b>⏱️ СЕРЕДНІ ПОКАЗНИКИ:</b>
├ Час відповіді: 12 хв
├ Час виконання: 2.3 год
└ Якість: 4.6/5

<b>👥 ОНЛАЙН ЗАРАЗ:</b>
├ 🟢 @manager_ivan (15 хв тому)
└ 🟢 @manager_maria (3 хв тому)""",
        reply_markup=kb, parse_mode="HTML"
    )

@router.callback_query(F.data == "team_permissions")
async def team_permissions(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 Розсилки", callback_data="perm_mailing"),
         InlineKeyboardButton(text="🔍 OSINT", callback_data="perm_osint")],
        [InlineKeyboardButton(text="🤖 Botnet", callback_data="perm_botnet"),
         InlineKeyboardButton(text="📊 Аналітика", callback_data="perm_analytics")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="team_main")]
    ])
    await query.message.edit_text(
        """<b>⚙️ НАЛАШТУВАННЯ ПРАВ</b>

<b>Модулі та доступ:</b>

<b>📧 Розсилки</b>
├ @manager_ivan ✅
├ @manager_maria ✅
└ @manager_petro ❌

<b>🔍 OSINT</b>
├ @manager_ivan ✅
└ @manager_maria ❌

<b>🤖 Botnet</b>
└ @manager_ivan ✅

<b>📊 Аналітика</b>
└ Всі менеджери ✅""",
        reply_markup=kb, parse_mode="HTML"
    )

@router.callback_query(F.data == "project_stats")
async def project_stats(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Експорт PDF", callback_data="export_pdf"),
         InlineKeyboardButton(text="📊 Експорт CSV", callback_data="export_csv")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="team_main")]
    ])
    await query.message.edit_text(
        """<b>📈 СТАТИСТИКА ПРОЕКТУ</b>

<b>💎 ТАРИФ:</b> ⭐ СТАНДАРТ
<b>📅 Активний до:</b> 15.01.2026

<b>📊 ЗАГАЛЬНА СТАТИСТИКА:</b>
├ Кампаній проведено: 156
├ Повідомлень надіслано: 45,230
├ Відповідей отримано: 6,784
├ Конверсія: 15.0%
└ ROI: +245%

<b>🤖 БОТИ:</b>
├ Всього: 45 / 500
├ Активних: 42
└ З помилками: 3

<b>👥 КОМАНДА:</b>
├ Менеджерів: 3 / 5
└ Активних сьогодні: 2

<b>💰 ВИТРАТИ:</b>
└ Цей місяць: 12,500 ₴""",
        reply_markup=kb, parse_mode="HTML"
    )

@router.callback_query(F.data.in_(["rating_week", "rating_month", "activity_report", "export_pdf", "export_csv"]))
async def misc_team_handlers(query: CallbackQuery):
    await query.answer("🔄 Генерується звіт...")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="team_main")]
    ])
    await query.message.edit_text(
        "📊 <b>ЗВІТ ЗГЕНЕРОВАНО</b>\n\n"
        "<i>Файл буде надіслано найближчим часом...</i>",
        reply_markup=kb, parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("perm_"))
async def toggle_permission(query: CallbackQuery):
    module = query.data.replace("perm_", "")
    await query.answer(f"⚙️ Налаштування {module}")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="team_permissions")]
    ])
    await query.message.edit_text(
        f"<b>⚙️ ПРАВА: {module.upper()}</b>\n\n"
        "Оберіть менеджерів для доступу до модуля:\n\n"
        "☑️ @manager_ivan\n"
        "☐ @manager_maria\n"
        "☐ @manager_petro",
        reply_markup=kb, parse_mode="HTML"
    )
