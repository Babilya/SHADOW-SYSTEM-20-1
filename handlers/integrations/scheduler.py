from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
scheduler_router = Router()

class SchedulerStates(StatesGroup):
    waiting_campaign_name = State()
    waiting_schedule_time = State()
    waiting_schedule_date = State()
    waiting_repeat_interval = State()

class SchedulerCRUD:
    @staticmethod
    async def get_scheduled_campaigns(user_id: int):
        from utils.db import async_session
        from database.models import Campaign, Project
        from sqlalchemy import select
        async with async_session() as session:
            project_result = await session.execute(
                select(Project.id).where(Project.leader_id == str(user_id))
            )
            project_id = project_result.scalar()
            
            if not project_id:
                return []
            
            result = await session.execute(
                select(Campaign).where(
                    Campaign.project_id == project_id,
                    Campaign.status == "scheduled"
                ).order_by(Campaign.scheduled_at)
            )
            return result.scalars().all()
    
    @staticmethod
    async def schedule_campaign(campaign_id: int, scheduled_at: datetime, repeat_interval: str = None):
        from utils.db import async_session
        from database.models import Campaign
        from sqlalchemy import update
        async with async_session() as session:
            await session.execute(
                update(Campaign).where(Campaign.id == campaign_id).values(
                    status="scheduled",
                    scheduled_at=scheduled_at
                )
            )
            await session.commit()
    
    @staticmethod
    async def cancel_schedule(campaign_id: int):
        from utils.db import async_session
        from database.models import Campaign
        from sqlalchemy import update
        async with async_session() as session:
            await session.execute(
                update(Campaign).where(Campaign.id == campaign_id).values(
                    status="draft",
                    scheduled_at=None
                )
            )
            await session.commit()
    
    @staticmethod
    async def get_draft_campaigns(user_id: int):
        from utils.db import async_session
        from database.models import Campaign, Project
        from sqlalchemy import select
        async with async_session() as session:
            project_result = await session.execute(
                select(Project.id).where(Project.leader_id == str(user_id))
            )
            project_id = project_result.scalar()
            
            if not project_id:
                return []
            
            result = await session.execute(
                select(Campaign).where(
                    Campaign.project_id == project_id,
                    Campaign.status == "draft"
                )
            )
            return result.scalars().all()

def scheduler_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Заплановані", callback_data="scheduled_list")],
        [InlineKeyboardButton(text="➕ Нове планування", callback_data="new_schedule")],
        [InlineKeyboardButton(text="🔄 Повторювані", callback_data="recurring_campaigns")],
        [InlineKeyboardButton(text="📊 Календар", callback_data="schedule_calendar")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])

@scheduler_router.callback_query(F.data == "scheduler_menu")
async def scheduler_menu(query: CallbackQuery):
    await query.answer()
    
    scheduled = await SchedulerCRUD.get_scheduled_campaigns(query.from_user.id)
    
    text = f"""<b>📅 ПЛАНУВАЛЬНИК КАМПАНІЙ</b>

<b>📊 Статистика:</b>
├ Заплановано: {len(scheduled)}
├ Сьогодні: 0
└ Цього тижня: 0

<b>⏰ Найближчі:</b>
"""
    
    if scheduled:
        for c in scheduled[:3]:
            time_str = c.scheduled_at.strftime("%d.%m %H:%M") if c.scheduled_at else "N/A"
            text += f"├ {c.name or 'Кампанія'} — {time_str}\n"
    else:
        text += "<i>Немає запланованих кампаній</i>\n"
    
    await query.message.edit_text(text, reply_markup=scheduler_kb(), parse_mode="HTML")

@scheduler_router.callback_query(F.data == "scheduled_list")
async def scheduled_list(query: CallbackQuery):
    await query.answer()
    
    scheduled = await SchedulerCRUD.get_scheduled_campaigns(query.from_user.id)
    
    text = "<b>📅 ЗАПЛАНОВАНІ КАМПАНІЇ</b>\n\n"
    
    if scheduled:
        for i, c in enumerate(scheduled[:10], 1):
            time_str = c.scheduled_at.strftime("%d.%m %H:%M") if c.scheduled_at else "N/A"
            text += f"{i}. <b>{c.name or 'Кампанія'}</b>\n"
            text += f"   └ 📅 {time_str}\n"
    else:
        text += "<i>Немає запланованих кампаній</i>"
    
    buttons = []
    for c in scheduled[:5]:
        buttons.append([InlineKeyboardButton(
            text=f"❌ Скасувати #{c.id}",
            callback_data=f"cancel_schedule_{c.id}"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="scheduler_menu")])
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@scheduler_router.callback_query(F.data == "new_schedule")
async def new_schedule(query: CallbackQuery):
    await query.answer()
    
    drafts = await SchedulerCRUD.get_draft_campaigns(query.from_user.id)
    
    if not drafts:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Створити кампанію", callback_data="mailing_create")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="scheduler_menu")]
        ])
        await query.message.edit_text(
            "<b>❌ Немає чернеток</b>\n\nСпочатку створіть кампанію у розділі Розсилки.",
            reply_markup=kb, parse_mode="HTML"
        )
        return
    
    buttons = []
    for d in drafts[:5]:
        buttons.append([InlineKeyboardButton(
            text=f"📧 {d.name or f'Кампанія #{d.id}'}",
            callback_data=f"schedule_campaign_{d.id}"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="scheduler_menu")])
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await query.message.edit_text(
        "<b>📅 ВИБІР КАМПАНІЇ</b>\n\nОберіть кампанію для планування:",
        reply_markup=kb, parse_mode="HTML"
    )

@scheduler_router.callback_query(F.data.startswith("schedule_campaign_"))
async def schedule_campaign(query: CallbackQuery, state: FSMContext):
    await query.answer()
    
    campaign_id = int(query.data.replace("schedule_campaign_", ""))
    await state.update_data(campaign_id=campaign_id)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏰ Через 1 годину", callback_data="schedule_1h")],
        [InlineKeyboardButton(text="⏰ Через 3 години", callback_data="schedule_3h")],
        [InlineKeyboardButton(text="⏰ Через 6 годин", callback_data="schedule_6h")],
        [InlineKeyboardButton(text="📅 Завтра 10:00", callback_data="schedule_tomorrow")],
        [InlineKeyboardButton(text="✏️ Вказати час", callback_data="schedule_custom")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="new_schedule")]
    ])
    
    await query.message.edit_text(
        f"<b>⏰ ВИБІР ЧАСУ</b>\n\nКоли запустити кампанію #{campaign_id}?",
        reply_markup=kb, parse_mode="HTML"
    )

@scheduler_router.callback_query(F.data.startswith("schedule_"))
async def process_schedule_time(query: CallbackQuery, state: FSMContext):
    time_option = query.data.replace("schedule_", "")
    
    if time_option in ["1h", "3h", "6h", "tomorrow"]:
        await query.answer()
        
        data = await state.get_data()
        campaign_id = data.get("campaign_id")
        
        if not campaign_id:
            await query.message.edit_text("❌ Помилка: кампанію не вибрано")
            return
        
        now = datetime.now()
        if time_option == "1h":
            scheduled_at = now + timedelta(hours=1)
        elif time_option == "3h":
            scheduled_at = now + timedelta(hours=3)
        elif time_option == "6h":
            scheduled_at = now + timedelta(hours=6)
        elif time_option == "tomorrow":
            tomorrow = now + timedelta(days=1)
            scheduled_at = tomorrow.replace(hour=10, minute=0, second=0)
        
        await SchedulerCRUD.schedule_campaign(campaign_id, scheduled_at)
        await state.clear()
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📅 Заплановані", callback_data="scheduled_list")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="scheduler_menu")]
        ])
        
        await query.message.edit_text(
            f"""<b>✅ КАМПАНІЮ ЗАПЛАНОВАНО!</b>

<b>ID:</b> {campaign_id}
<b>Запуск:</b> {scheduled_at.strftime("%d.%m.%Y %H:%M")}

<i>Кампанія запуститься автоматично</i>""",
            reply_markup=kb, parse_mode="HTML"
        )
    elif time_option == "custom":
        await query.answer()
        await state.set_state(SchedulerStates.waiting_schedule_time)
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Скасувати", callback_data="scheduler_menu")]
        ])
        
        await query.message.edit_text(
            "<b>✏️ ВКАЖІТЬ ЧАС</b>\n\nВведіть дату та час у форматі:\n<code>DD.MM.YYYY HH:MM</code>\n\nНаприклад: <code>25.12.2024 14:30</code>",
            reply_markup=kb, parse_mode="HTML"
        )

@scheduler_router.message(SchedulerStates.waiting_schedule_time)
async def process_custom_time(message: Message, state: FSMContext):
    try:
        scheduled_at = datetime.strptime(message.text.strip(), "%d.%m.%Y %H:%M")
        
        if scheduled_at <= datetime.now():
            await message.answer("❌ Час має бути у майбутньому!")
            return
        
        data = await state.get_data()
        campaign_id = data.get("campaign_id")
        
        if campaign_id:
            await SchedulerCRUD.schedule_campaign(campaign_id, scheduled_at)
        
        await state.clear()
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📅 Заплановані", callback_data="scheduled_list")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="scheduler_menu")]
        ])
        
        await message.answer(
            f"<b>✅ КАМПАНІЮ ЗАПЛАНОВАНО!</b>\n\n<b>Запуск:</b> {scheduled_at.strftime('%d.%m.%Y %H:%M')}",
            reply_markup=kb, parse_mode="HTML"
        )
    except ValueError:
        await message.answer("❌ Невірний формат. Використовуйте: DD.MM.YYYY HH:MM")

@scheduler_router.callback_query(F.data.startswith("cancel_schedule_"))
async def cancel_schedule(query: CallbackQuery):
    await query.answer()
    
    campaign_id = int(query.data.replace("cancel_schedule_", ""))
    await SchedulerCRUD.cancel_schedule(campaign_id)
    
    await query.message.edit_text(
        f"<b>❌ Планування скасовано</b>\n\nКампанія #{campaign_id} повернута у чернетки.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="scheduler_menu")]
        ]),
        parse_mode="HTML"
    )

@scheduler_router.callback_query(F.data == "recurring_campaigns")
async def recurring_campaigns(query: CallbackQuery):
    await query.answer()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Створити повторювану", callback_data="create_recurring")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="scheduler_menu")]
    ])
    
    await query.message.edit_text(
        """<b>🔄 ПОВТОРЮВАНІ КАМПАНІЇ</b>

<b>Типи повторень:</b>
├ Щодня
├ Щотижня
├ Щомісяця
└ Власний інтервал

<i>Немає активних повторюваних кампаній</i>""",
        reply_markup=kb, parse_mode="HTML"
    )

@scheduler_router.callback_query(F.data == "schedule_calendar")
async def schedule_calendar(query: CallbackQuery):
    await query.answer()
    
    now = datetime.now()
    month_name = now.strftime("%B %Y")
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Попередній", callback_data="cal_prev"),
         InlineKeyboardButton(text="▶️ Наступний", callback_data="cal_next")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="scheduler_menu")]
    ])
    
    await query.message.edit_text(
        f"""<b>📅 КАЛЕНДАР КАМПАНІЙ</b>

<b>{month_name}</b>

<pre>
Пн Вт Ср Чт Пт Сб Нд
                  1
2  3  4  5  6  7  8
9  10 11 12 13 14 15
16 17 18 19 20 21 22
23 24 25 26 27 28 29
30 31
</pre>

<b>📍 Заплановані дати:</b>
<i>Немає запланованих кампаній</i>""",
        reply_markup=kb, parse_mode="HTML"
    )
