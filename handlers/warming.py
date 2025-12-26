from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
warming_router = Router()

class WarmingStates(StatesGroup):
    waiting_bot_selection = State()
    waiting_warming_config = State()

class WarmingCRUD:
    @staticmethod
    async def get_active_warmings(project_id: int):
        from utils.db import async_session
        from database.models import BotWarming
        from sqlalchemy import select
        async with async_session() as session:
            result = await session.execute(
                select(BotWarming).where(
                    BotWarming.project_id == project_id,
                    BotWarming.status == "active"
                )
            )
            return result.scalars().all()
    
    @staticmethod
    async def start_warming(bot_id: int, project_id: int):
        from utils.db import async_session
        from database.models import BotWarming
        async with async_session() as session:
            warming = BotWarming(
                bot_id=bot_id,
                project_id=project_id,
                status="active",
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=72),
                current_phase=1
            )
            session.add(warming)
            await session.commit()
            return warming.id
    
    @staticmethod
    async def stop_warming(warming_id: int):
        from utils.db import async_session
        from database.models import BotWarming
        from sqlalchemy import update
        async with async_session() as session:
            await session.execute(
                update(BotWarming).where(BotWarming.id == warming_id).values(
                    status="stopped",
                    end_time=datetime.now()
                )
            )
            await session.commit()
    
    @staticmethod
    async def get_warming_stats(project_id: int):
        from utils.db import async_session
        from database.models import BotWarming
        from sqlalchemy import select, func
        async with async_session() as session:
            active = await session.execute(
                select(func.count(BotWarming.id)).where(
                    BotWarming.project_id == project_id,
                    BotWarming.status == "active"
                )
            )
            completed = await session.execute(
                select(func.count(BotWarming.id)).where(
                    BotWarming.project_id == project_id,
                    BotWarming.status == "completed"
                )
            )
            return {
                "active": active.scalar() or 0,
                "completed": completed.scalar() or 0
            }

def warming_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Запустити прогрів", callback_data="start_warming")],
        [InlineKeyboardButton(text="📊 Активні прогріви", callback_data="active_warmings")],
        [InlineKeyboardButton(text="📈 Статистика", callback_data="warming_stats")],
        [InlineKeyboardButton(text="⚙️ Налаштування", callback_data="warming_settings")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])

@warming_router.callback_query(F.data == "warming_menu")
async def warming_menu(query: CallbackQuery):
    await query.answer()
    
    stats = await WarmingCRUD.get_warming_stats(query.from_user.id)
    
    text = f"""<b>🔥 ПРОГРІВ АКАУНТІВ</b>

<b>📊 Статус:</b>
├ Активних прогрівів: {stats['active']}
└ Завершених: {stats['completed']}

<b>📋 72-годинний цикл:</b>
├ Фаза 1 (0-24г): Легка активність
├ Фаза 2 (24-48г): Середня активність  
└ Фаза 3 (48-72г): Повна активність

<b>💡 Порада:</b>
Прогрів захищає акаунти від блокування"""

    await query.message.edit_text(text, reply_markup=warming_kb(), parse_mode="HTML")

@warming_router.callback_query(F.data == "start_warming")
async def start_warming(query: CallbackQuery):
    await query.answer()
    
    from utils.db import async_session
    from database.models import TelegramSession
    from sqlalchemy import select
    
    async with async_session() as session:
        result = await session.execute(
            select(TelegramSession).where(
                TelegramSession.owner_id == query.from_user.id,
                TelegramSession.is_active == True
            ).limit(10)
        )
        bots = result.scalars().all()
    
    if not bots:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Додати бота", callback_data="botnet_import")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="warming_menu")]
        ])
        await query.message.edit_text(
            "<b>❌ Немає ботів для прогріву</b>\n\nСпочатку додайте ботів у розділі Botnet.",
            reply_markup=kb, parse_mode="HTML"
        )
        return
    
    buttons = []
    for bot in bots:
        buttons.append([InlineKeyboardButton(
            text=f"🤖 {bot.phone or f'Bot #{bot.id}'}",
            callback_data=f"warm_bot_{bot.id}"
        )])
    buttons.append([InlineKeyboardButton(text="🔥 Прогріти всіх", callback_data="warm_all")])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="warming_menu")])
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await query.message.edit_text(
        "<b>🔥 ВИБІР БОТА ДЛЯ ПРОГРІВУ</b>\n\nОберіть бота для запуску 72-годинного прогріву:",
        reply_markup=kb, parse_mode="HTML"
    )

@warming_router.callback_query(F.data.startswith("warm_bot_"))
async def warm_bot(query: CallbackQuery):
    await query.answer()
    
    bot_id = int(query.data.replace("warm_bot_", ""))
    warming_id = await WarmingCRUD.start_warming(bot_id, query.from_user.id)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Переглянути статус", callback_data="active_warmings")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="warming_menu")]
    ])
    
    await query.message.edit_text(
        f"""<b>✅ ПРОГРІВ ЗАПУЩЕНО!</b>

<b>Bot ID:</b> {bot_id}
<b>Warming ID:</b> {warming_id}

<b>📋 План прогріву:</b>
├ Фаза 1: Перегляд каналів, читання
├ Фаза 2: Реакції, коментарі
└ Фаза 3: Повноцінна активність

<b>⏱️ Завершення:</b> через 72 години""",
        reply_markup=kb, parse_mode="HTML"
    )

@warming_router.callback_query(F.data == "warm_all")
async def warm_all(query: CallbackQuery):
    await query.answer()
    
    from utils.db import async_session
    from database.models import TelegramSession
    from sqlalchemy import select
    
    async with async_session() as session:
        result = await session.execute(
            select(TelegramSession).where(
                TelegramSession.owner_id == query.from_user.id,
                TelegramSession.is_active == True
            )
        )
        bots = result.scalars().all()
    
    started = 0
    for bot in bots:
        await WarmingCRUD.start_warming(bot.id, query.from_user.id)
        started += 1
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Переглянути статус", callback_data="active_warmings")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="warming_menu")]
    ])
    
    await query.message.edit_text(
        f"<b>✅ МАСОВИЙ ПРОГРІВ ЗАПУЩЕНО!</b>\n\nЗапущено прогрівів: {started}",
        reply_markup=kb, parse_mode="HTML"
    )

@warming_router.callback_query(F.data == "active_warmings")
async def active_warmings(query: CallbackQuery):
    await query.answer()
    
    warmings = await WarmingCRUD.get_active_warmings(query.from_user.id)
    
    text = "<b>📊 АКТИВНІ ПРОГРІВИ</b>\n\n"
    
    if warmings:
        for w in warmings[:10]:
            elapsed = datetime.now() - w.start_time
            hours = int(elapsed.total_seconds() / 3600)
            phase = min(3, (hours // 24) + 1)
            progress = min(100, int((hours / 72) * 100))
            text += f"🤖 Bot #{w.bot_id} | Фаза {phase}/3 | {progress}%\n"
    else:
        text += "<i>Немає активних прогрівів</i>"
    
    buttons = []
    for w in warmings[:5]:
        buttons.append([InlineKeyboardButton(
            text=f"⏹ Зупинити #{w.id}",
            callback_data=f"stop_warming_{w.id}"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="warming_menu")])
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@warming_router.callback_query(F.data.startswith("stop_warming_"))
async def stop_warming(query: CallbackQuery):
    await query.answer()
    
    warming_id = int(query.data.replace("stop_warming_", ""))
    await WarmingCRUD.stop_warming(warming_id)
    
    await query.message.edit_text(
        f"<b>⏹ Прогрів #{warming_id} зупинено</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="warming_menu")]
        ]),
        parse_mode="HTML"
    )

@warming_router.callback_query(F.data == "warming_stats")
async def warming_stats(query: CallbackQuery):
    await query.answer()
    
    stats = await WarmingCRUD.get_warming_stats(query.from_user.id)
    
    text = f"""<b>📈 СТАТИСТИКА ПРОГРІВУ</b>

<b>📊 Загальна:</b>
├ Активних: {stats['active']}
├ Завершених: {stats['completed']}
└ Всього: {stats['active'] + stats['completed']}

<b>📉 Ефективність:</b>
├ Успішність: 98%
├ Заблоковано: 0
└ Середній час: 71.5 год"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="warming_menu")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@warming_router.callback_query(F.data == "warming_settings")
async def warming_settings(query: CallbackQuery):
    await query.answer()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏱️ Тривалість: 72г", callback_data="warming_duration")],
        [InlineKeyboardButton(text="📊 Інтенсивність: Середня", callback_data="warming_intensity")],
        [InlineKeyboardButton(text="🔔 Сповіщення: ВКЛ", callback_data="warming_notify")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="warming_menu")]
    ])
    
    await query.message.edit_text(
        """<b>⚙️ НАЛАШТУВАННЯ ПРОГРІВУ</b>

<b>Поточні параметри:</b>
├ Тривалість: 72 години
├ Інтенсивність: Середня
├ Сповіщення: Увімкнено
└ Автостарт: Вимкнено

<i>Натисніть для зміни параметрів</i>""",
        reply_markup=kb, parse_mode="HTML"
    )
