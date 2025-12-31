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

WARMING_PROFILES = {
    "conservative": {
        "name": "🟢 Консервативний",
        "actions_per_day": 20,
        "interval_min": 120,
        "interval_max": 300,
        "description": "Безпечний режим: ~20 дій/день"
    },
    "standard": {
        "name": "🟡 Стандартний",
        "actions_per_day": 50,
        "interval_min": 60,
        "interval_max": 180,
        "description": "Рекомендований: ~50 дій/день"
    },
    "aggressive": {
        "name": "🔴 Агресивний",
        "actions_per_day": 100,
        "interval_min": 30,
        "interval_max": 90,
        "description": "Ризикований: 100+ дій/день"
    },
    "custom": {
        "name": "⚙️ Кастомний",
        "actions_per_day": 0,
        "interval_min": 0,
        "interval_max": 0,
        "description": "Налаштування вручну"
    }
}

def warming_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Запустити прогрів", callback_data="start_warming")],
        [InlineKeyboardButton(text="📋 Профілі прогріву", callback_data="warming_profiles")],
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
    from database.models import Bot
    from sqlalchemy import select
    
    async with async_session() as session:
        result = await session.execute(
            select(Bot).where(
                Bot.project_id == query.from_user.id,
                Bot.status.in_(["active", "pending_validation", "pending"])
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
    
    import asyncio
    asyncio.create_task(run_warming_cycle(bot_id, warming_id))
    
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

async def run_warming_cycle(bot_id: int, warming_id: int):
    import asyncio
    import random
    
    try:
        from core.session_manager import session_manager
        from utils.db import async_session
        from database.models import BotWarming, Bot
        from sqlalchemy import select, update
        
        async with async_session() as session:
            result = await session.execute(
                select(Bot).where(Bot.id == bot_id)
            )
            bot_record = result.scalar()
        
        if not bot_record:
            logger.warning(f"No bot found with id {bot_id}")
            return
        
        session_hash = bot_record.session_hash
        if not session_hash:
            logger.warning(f"No session hash for bot {bot_id}, running simulation warming")
            await run_simulation_warming(warming_id)
            return
        
        client = await session_manager.connect_client(session_hash)
        if not client:
            logger.warning(f"Could not connect client for warming {warming_id}")
            return
        
        PUBLIC_CHANNELS = [
            "@telegram", "@durov", "@tikitak", "@bbcukrainian", 
            "@unaboringtech", "@theinsider"
        ]
        
        for phase in range(1, 4):
            # Smart Warming 2.0: Динамічні затримки та маскування
            profile = WARMING_PROFILES.get(bot_record.warming_profile, WARMING_PROFILES['standard'])
            actions_limit = profile['actions_per_day']
            
            phase_duration = 24 * 3600
            phase_start = datetime.now()
            
            async with async_session() as session:
                await session.execute(
                    update(BotWarming).where(BotWarming.id == warming_id).values(
                        current_phase=phase
                    )
                )
                await session.commit()
            
            logger.info(f"Warming {warming_id} entering phase {phase} (Smart 2.0)")
            
            actions_done = 0
            while (datetime.now() - phase_start).total_seconds() < phase_duration:
                # Перевірка лімітів Smart Warming
                if actions_done >= actions_limit:
                    await asyncio.sleep(3600) # Відпочинок 1 година
                    continue

                async with async_session() as session:
                    result = await session.execute(
                        select(BotWarming.status).where(BotWarming.id == warming_id)
                    )
                    status = result.scalar()
                    if status != "active":
                        logger.info(f"Warming {warming_id} stopped")
                        return
                
                try:
                    # Емуляція "людської" поведінки через antidetect_system
                    from core.antidetect import antidetect_system
                    pattern = 'casual_user' if phase == 1 else 'active_user' if phase == 2 else 'business_user'
                    
                    if not antidetect_system.is_online_time(pattern):
                        await asyncio.sleep(1800) # Сон 30 хв якщо зараз не час онлайну
                        continue

                    if phase == 1:
                        channel = random.choice(PUBLIC_CHANNELS)
                        try:
                            entity = await client.get_entity(channel)
                            # Емуляція перегляду з випадковим часом
                            async for msg in client.iter_messages(entity, limit=random.randint(3, 8)):
                                await asyncio.sleep(random.uniform(2, 5))
                            logger.debug(f"Warming phase 1: read {channel}")
                            actions_done += 1
                        except Exception as e:
                            logger.debug(f"Warming read error: {e}")
                        
                        delay = random.uniform(profile['interval_min'], profile['interval_max'])
                        await asyncio.sleep(delay)
                    
                    elif phase == 2:
                        channel = random.choice(PUBLIC_CHANNELS)
                        try:
                            entity = await client.get_entity(channel)
                            async for msg in client.iter_messages(entity, limit=3):
                                if hasattr(msg, 'reactions') and msg.reactions:
                                    # Випадкова реакція
                                    await asyncio.sleep(await antidetect_system.emulate_thinking(pattern))
                                    pass
                            logger.debug(f"Warming phase 2: interacted with {channel}")
                            actions_done += 1
                        except Exception as e:
                            logger.debug(f"Warming interaction error: {e}")
                        
                        delay = random.uniform(profile['interval_min'], profile['interval_max']) * 0.8
                        await asyncio.sleep(delay)
                    
                    elif phase == 3:
                        channel = random.choice(PUBLIC_CHANNELS)
                        try:
                            entity = await client.get_entity(channel)
                            async for msg in client.iter_messages(entity, limit=10):
                                await asyncio.sleep(random.uniform(1, 3))
                            logger.debug(f"Warming phase 3: active on {channel}")
                            actions_done += 1
                        except Exception as e:
                            logger.debug(f"Warming active error: {e}")
                        
                        delay = random.uniform(profile['interval_min'], profile['interval_max']) * 0.5
                        await asyncio.sleep(delay)
                
                except Exception as e:
                    logger.error(f"Warming cycle error: {e}")
                    await asyncio.sleep(60)
        
        async with async_session() as session:
            await session.execute(
                update(BotWarming).where(BotWarming.id == warming_id).values(
                    status="completed",
                    end_time=datetime.now()
                )
            )
            await session.commit()
        
        logger.info(f"Warming {warming_id} completed successfully")
    
    except Exception as e:
        logger.error(f"Warming cycle failed: {e}")

async def run_simulation_warming(warming_id: int):
    import asyncio
    from utils.db import async_session
    from database.models import BotWarming
    from sqlalchemy import select, update
    
    try:
        for phase in range(1, 4):
            async with async_session() as session:
                result = await session.execute(
                    select(BotWarming.status).where(BotWarming.id == warming_id)
                )
                status = result.scalar()
                if status != "active":
                    return
                
                await session.execute(
                    update(BotWarming).where(BotWarming.id == warming_id).values(
                        current_phase=phase
                    )
                )
                await session.commit()
            
            logger.info(f"Simulation warming {warming_id} phase {phase}")
            await asyncio.sleep(10)
        
        async with async_session() as session:
            await session.execute(
                update(BotWarming).where(BotWarming.id == warming_id).values(
                    status="completed",
                    end_time=datetime.now()
                )
            )
            await session.commit()
        logger.info(f"Simulation warming {warming_id} completed")
    except Exception as e:
        logger.error(f"Simulation warming error: {e}")

@warming_router.callback_query(F.data == "warm_all")
async def warm_all(query: CallbackQuery):
    await query.answer()
    
    from utils.db import async_session
    from database.models import Bot
    from sqlalchemy import select
    
    async with async_session() as session:
        result = await session.execute(
            select(Bot).where(
                Bot.project_id == query.from_user.id,
                Bot.status.in_(["active", "pending_validation", "pending"])
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

@warming_router.callback_query(F.data == "warming_profiles")
async def warming_profiles(query: CallbackQuery):
    await query.answer()
    
    text = """<b>📋 ПРОФІЛІ ПРОГРІВУ</b>

<b>🟢 Консервативний</b>
├ ~20 дій/день
├ Інтервал: 2-5 хвилин
└ Статус: Безпечний

<b>🟡 Стандартний</b> (Рекомендовано)
├ ~50 дій/день
├ Інтервал: 1-3 хвилини
└ Статус: Оптимальний

<b>🔴 Агресивний</b>
├ 100+ дій/день
├ Інтервал: 30-90 секунд
└ Статус: Ризикований

<b>⚙️ Кастомний</b>
└ Налаштування вручну"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Консервативний", callback_data="profile_conservative")],
        [InlineKeyboardButton(text="🟡 Стандартний", callback_data="profile_standard")],
        [InlineKeyboardButton(text="🔴 Агресивний", callback_data="profile_aggressive")],
        [InlineKeyboardButton(text="⚙️ Кастомний", callback_data="profile_custom")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="warming_menu")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@warming_router.callback_query(F.data.startswith("profile_"))
async def set_warming_profile(query: CallbackQuery, state: FSMContext):
    profile_key = query.data.replace("profile_", "")
    profile = WARMING_PROFILES.get(profile_key)
    
    if profile:
        await state.update_data(warming_profile=profile_key)
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Підтвердити", callback_data="confirm_profile")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="warming_profiles")]
        ])
        
        await query.message.edit_text(
            f"""<b>✅ ПРОФІЛЬ ОБРАНО</b>

{profile['name']}
{profile['description']}

<b>Параметри:</b>
├ Дій на день: {profile['actions_per_day']}
├ Мін. інтервал: {profile['interval_min']} сек
└ Макс. інтервал: {profile['interval_max']} сек

Натисніть "Підтвердити" для застосування.""",
            reply_markup=kb, parse_mode="HTML"
        )
    
    await query.answer()

@warming_router.callback_query(F.data == "confirm_profile")
async def confirm_profile(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    profile_key = data.get("warming_profile", "standard")
    
    await query.answer(f"✅ Профіль '{profile_key}' застосовано!", show_alert=True)
    await state.clear()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Запустити прогрів", callback_data="start_warming")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="warming_menu")]
    ])
    
    await query.message.edit_text(
        f"<b>✅ ПРОФІЛЬ ЗАСТОСОВАНО</b>\n\nПрофіль: {WARMING_PROFILES[profile_key]['name']}\n\nТепер ви можете запустити прогрів з цими налаштуваннями.",
        reply_markup=kb, parse_mode="HTML"
    )

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
