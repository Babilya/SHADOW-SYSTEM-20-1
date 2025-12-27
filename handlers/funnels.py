from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.funnel_service import funnel_service
from services.user_service import user_service
from config import ADMIN_IDS
from database.models import UserRole
import logging

logger = logging.getLogger(__name__)
funnels_router = Router()

async def check_funnel_access(user_id: int) -> bool:
    if user_id in ADMIN_IDS:
        return True
    role = user_service.get_user_role(user_id)
    return role in [UserRole.LEADER, UserRole.ADMIN]

class FunnelStates(StatesGroup):
    waiting_name = State()
    waiting_description = State()
    waiting_photo = State()
    waiting_welcome_text = State()
    waiting_tariff_info = State()
    waiting_step_content = State()
    waiting_step_photo = State()
    editing_name = State()
    editing_description = State()
    editing_photo = State()
    editing_tariff = State()
    editing_step_content = State()
    editing_step_photo = State()

def funnels_main_kb(funnels: list) -> InlineKeyboardMarkup:
    buttons = []
    for f in funnels[:10]:
        status_icon = "🟢" if f.is_active else "⚪"
        buttons.append([InlineKeyboardButton(
            text=f"{status_icon} {f.name} ({f.steps_count} кроків)",
            callback_data=f"funnel_view_{f.id}"
        )])
    buttons.append([InlineKeyboardButton(text="➕ Створити воронку", callback_data="funnel_create")])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def funnel_view_kb(funnel_id: int, is_active: bool) -> InlineKeyboardMarkup:
    toggle_text = "⏸ Призупинити" if is_active else "▶️ Активувати"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ Назва", callback_data=f"funnel_edit_name_{funnel_id}"),
            InlineKeyboardButton(text="📝 Опис", callback_data=f"funnel_edit_desc_{funnel_id}")
        ],
        [
            InlineKeyboardButton(text="🖼 Фото", callback_data=f"funnel_edit_photo_{funnel_id}"),
            InlineKeyboardButton(text="⚙️ Конфіг", callback_data=f"funnel_edit_config_{funnel_id}")
        ],
        [InlineKeyboardButton(text="📋 Кроки воронки", callback_data=f"funnel_steps_{funnel_id}")],
        [
            InlineKeyboardButton(text="📝 Шаблони", callback_data=f"funnel_templates_{funnel_id}"),
            InlineKeyboardButton(text="📅 Планування", callback_data=f"funnel_schedule_{funnel_id}")
        ],
        [
            InlineKeyboardButton(text=toggle_text, callback_data=f"funnel_toggle_{funnel_id}"),
            InlineKeyboardButton(text="📊 Статистика", callback_data=f"funnel_stats_{funnel_id}")
        ],
        [
            InlineKeyboardButton(text="🗑 Видалити", callback_data=f"funnel_delete_{funnel_id}"),
            InlineKeyboardButton(text="◀️ До воронок", callback_data="funnels_main")
        ]
    ])

def funnel_steps_kb(funnel_id: int, steps: list) -> InlineKeyboardMarkup:
    buttons = []
    for step in steps:
        photo_icon = "🖼" if step.photo_file_id else "📝"
        buttons.append([InlineKeyboardButton(
            text=f"{step.step_order}. {photo_icon} {step.title or step.content[:30]}...",
            callback_data=f"step_view_{step.id}"
        )])
    buttons.append([InlineKeyboardButton(text="➕ Додати крок", callback_data=f"step_add_{funnel_id}")])
    buttons.append([InlineKeyboardButton(text="◀️ До воронки", callback_data=f"funnel_view_{funnel_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@funnels_router.callback_query(F.data == "funnels_main")
async def funnels_main(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.clear()
    
    if not await check_funnel_access(query.from_user.id):
        await query.message.edit_text("❌ У вас немає доступу до управління воронками")
        return
    
    user_id = str(query.from_user.id)
    funnels = funnel_service.get_funnels_by_owner(user_id)
    
    total_views = sum(f.views_count or 0 for f in funnels)
    total_conv = sum(f.conversions or 0 for f in funnels)
    active_count = sum(1 for f in funnels if f.is_active)
    
    text = f"""<b>🎯 МЕНЕДЖЕР ВОРОНОК</b>
<i>Створюйте та керуйте воронками продажів</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 СТАТИСТИКА:</b>
├ 📁 Всього воронок: <b>{len(funnels)}</b>
├ 🟢 Активних: <b>{active_count}</b>
├ 👁 Переглядів: <b>{total_views}</b>
└ ✅ Конверсій: <b>{total_conv}</b>

━━━━━━━━━━━━━━━━━━━━━━━

<b>🎯 ВАШІ ВОРОНКИ:</b>"""
    
    if not funnels:
        text += "\n<i>Воронок ще немає. Створіть першу!</i>"
    
    await query.message.edit_text(text, reply_markup=funnels_main_kb(funnels), parse_mode="HTML")

@funnels_router.callback_query(F.data == "funnel_create")
async def funnel_create_start(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(FunnelStates.waiting_name)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="funnels_main")]
    ])
    await query.message.edit_text(
        "<b>➕ СТВОРЕННЯ ВОРОНКИ</b>\n\n"
        "Введіть назву нової воронки:\n"
        "<i>Наприклад: Онбордінг новачків, Продаж преміум...</i>",
        reply_markup=kb, parse_mode="HTML"
    )

@funnels_router.message(FunnelStates.waiting_name)
async def funnel_create_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2 or len(name) > 100:
        await message.answer("❌ Назва має бути від 2 до 100 символів")
        return
    
    user_id = str(message.from_user.id)
    funnel = funnel_service.create_funnel(user_id, name)
    
    if funnel:
        await state.clear()
        text = f"""✅ <b>Воронку створено!</b>

<b>📁 {funnel.name}</b>
├ ID: <code>{funnel.id}</code>
├ Статус: Чернетка
└ Кроків: 0

Тепер налаштуйте воронку:"""
        await message.answer(text, reply_markup=funnel_view_kb(funnel.id, funnel.is_active), parse_mode="HTML")
    else:
        await message.answer("❌ Помилка створення воронки")

@funnels_router.callback_query(F.data.startswith("funnel_view_"))
async def funnel_view(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.clear()
    funnel_id = int(query.data.split("_")[-1])
    funnel = funnel_service.get_funnel(funnel_id)
    
    if not funnel:
        await query.message.edit_text("❌ Воронку не знайдено")
        return
    
    status = "🟢 Активна" if funnel.is_active else "⚪ Неактивна"
    conv_rate = 0
    if funnel.views_count and funnel.views_count > 0:
        conv_rate = round((funnel.conversions or 0) / funnel.views_count * 100, 1)
    
    text = f"""<b>🎯 {funnel.name}</b>
<i>{funnel.description or 'Без опису'}</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>📋 ІНФОРМАЦІЯ:</b>
├ 🆔 ID: <code>{funnel.id}</code>
├ 📊 Статус: {status}
├ 📝 Кроків: <b>{funnel.steps_count}</b>
├ 🖼 Фото: {'Так' if funnel.photo_file_id else 'Ні'}
└ ⚙️ Конфіг: {'Налаштовано' if funnel.tariff_info else 'Не вказано'}

<b>📈 СТАТИСТИКА:</b>
├ 👁 Переглядів: <b>{funnel.views_count or 0}</b>
├ ✅ Конверсій: <b>{funnel.conversions or 0}</b>
└ 📊 CR: <b>{conv_rate}%</b>

━━━━━━━━━━━━━━━━━━━━━━━

<b>⚙️ НАЛАШТУВАННЯ:</b>"""
    
    await query.message.edit_text(text, reply_markup=funnel_view_kb(funnel_id, funnel.is_active), parse_mode="HTML")

@funnels_router.callback_query(F.data.startswith("funnel_edit_name_"))
async def funnel_edit_name_start(query: CallbackQuery, state: FSMContext):
    await query.answer()
    funnel_id = int(query.data.split("_")[-1])
    await state.update_data(editing_funnel_id=funnel_id)
    await state.set_state(FunnelStates.editing_name)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data=f"funnel_view_{funnel_id}")]
    ])
    await query.message.edit_text(
        "<b>✏️ РЕДАГУВАННЯ НАЗВИ</b>\n\nВведіть нову назву воронки:",
        reply_markup=kb, parse_mode="HTML"
    )

@funnels_router.message(FunnelStates.editing_name)
async def funnel_edit_name_save(message: Message, state: FSMContext):
    data = await state.get_data()
    funnel_id = data.get("editing_funnel_id")
    name = message.text.strip()
    
    if funnel_service.update_funnel(funnel_id, name=name):
        await state.clear()
        funnel = funnel_service.get_funnel(funnel_id)
        await message.answer(f"✅ Назву змінено на: <b>{name}</b>", 
                           reply_markup=funnel_view_kb(funnel_id, funnel.is_active if funnel else True),
                           parse_mode="HTML")
    else:
        await message.answer("❌ Помилка збереження")

@funnels_router.callback_query(F.data.startswith("funnel_edit_desc_"))
async def funnel_edit_desc_start(query: CallbackQuery, state: FSMContext):
    await query.answer()
    funnel_id = int(query.data.split("_")[-1])
    await state.update_data(editing_funnel_id=funnel_id)
    await state.set_state(FunnelStates.editing_description)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data=f"funnel_view_{funnel_id}")]
    ])
    await query.message.edit_text(
        "<b>📝 РЕДАГУВАННЯ ОПИСУ</b>\n\nВведіть опис воронки:",
        reply_markup=kb, parse_mode="HTML"
    )

@funnels_router.message(FunnelStates.editing_description)
async def funnel_edit_desc_save(message: Message, state: FSMContext):
    data = await state.get_data()
    funnel_id = data.get("editing_funnel_id")
    
    if funnel_service.update_funnel(funnel_id, description=message.text):
        await state.clear()
        funnel = funnel_service.get_funnel(funnel_id)
        await message.answer("✅ Опис збережено!", 
                           reply_markup=funnel_view_kb(funnel_id, funnel.is_active if funnel else True),
                           parse_mode="HTML")
    else:
        await message.answer("❌ Помилка збереження")

@funnels_router.callback_query(F.data.startswith("funnel_edit_photo_"))
async def funnel_edit_photo_start(query: CallbackQuery, state: FSMContext):
    await query.answer()
    funnel_id = int(query.data.split("_")[-1])
    await state.update_data(editing_funnel_id=funnel_id)
    await state.set_state(FunnelStates.editing_photo)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Видалити фото", callback_data=f"funnel_remove_photo_{funnel_id}")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data=f"funnel_view_{funnel_id}")]
    ])
    await query.message.edit_text(
        "<b>🖼 РЕДАГУВАННЯ ФОТО</b>\n\nНадішліть нове фото для воронки:",
        reply_markup=kb, parse_mode="HTML"
    )

@funnels_router.message(FunnelStates.editing_photo, F.photo)
async def funnel_edit_photo_save(message: Message, state: FSMContext):
    data = await state.get_data()
    funnel_id = data.get("editing_funnel_id")
    photo_id = message.photo[-1].file_id
    
    if funnel_service.update_funnel(funnel_id, photo_file_id=photo_id):
        await state.clear()
        funnel = funnel_service.get_funnel(funnel_id)
        await message.answer("✅ Фото збережено!", 
                           reply_markup=funnel_view_kb(funnel_id, funnel.is_active if funnel else True),
                           parse_mode="HTML")
    else:
        await message.answer("❌ Помилка збереження")

@funnels_router.callback_query(F.data.startswith("funnel_remove_photo_"))
async def funnel_remove_photo(query: CallbackQuery, state: FSMContext):
    await query.answer()
    funnel_id = int(query.data.split("_")[-1])
    funnel_service.update_funnel(funnel_id, photo_file_id=None)
    await state.clear()
    funnel = funnel_service.get_funnel(funnel_id)
    await query.message.edit_text("✅ Фото видалено!", 
                                 reply_markup=funnel_view_kb(funnel_id, funnel.is_active if funnel else True),
                                 parse_mode="HTML")

@funnels_router.callback_query(F.data.startswith("funnel_edit_config_"))
async def funnel_edit_config_start(query: CallbackQuery, state: FSMContext):
    await query.answer()
    funnel_id = int(query.data.split("_")[-1])
    await state.update_data(editing_funnel_id=funnel_id)
    await state.set_state(FunnelStates.editing_tariff)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data=f"funnel_view_{funnel_id}")]
    ])
    await query.message.edit_text(
        "<b>⚙️ НАЛАШТУВАННЯ КОНФІГУРАЦІЇ</b>\n\n"
        "Введіть додаткову інформацію для цієї воронки:",
        reply_markup=kb, parse_mode="HTML"
    )

@funnels_router.message(FunnelStates.editing_tariff)
async def funnel_edit_config_save(message: Message, state: FSMContext):
    data = await state.get_data()
    funnel_id = data.get("editing_funnel_id")
    
    if funnel_service.update_funnel(funnel_id, tariff_info=message.text):
        await state.clear()
        funnel = funnel_service.get_funnel(funnel_id)
        await message.answer("✅ Конфігурацію збережено!", 
                           reply_markup=funnel_view_kb(funnel_id, funnel.is_active if funnel else True),
                           parse_mode="HTML")
    else:
        await message.answer("❌ Помилка збереження")

@funnels_router.callback_query(F.data.startswith("funnel_toggle_"))
async def funnel_toggle(query: CallbackQuery):
    await query.answer()
    funnel_id = int(query.data.split("_")[-1])
    funnel = funnel_service.get_funnel(funnel_id)
    if funnel:
        new_status = not funnel.is_active
        funnel_service.update_funnel(funnel_id, is_active=new_status)
        status_text = "🟢 Активовано" if new_status else "⚪ Призупинено"
        await query.message.edit_text(
            f"✅ Статус воронки змінено: {status_text}",
            reply_markup=funnel_view_kb(funnel_id, new_status),
            parse_mode="HTML"
        )

@funnels_router.callback_query(F.data.startswith("funnel_stats_"))
async def funnel_stats(query: CallbackQuery):
    await query.answer()
    funnel_id = int(query.data.split("_")[-1])
    funnel = funnel_service.get_funnel(funnel_id)
    
    if not funnel:
        return
    
    conv_rate = 0
    if funnel.views_count and funnel.views_count > 0:
        conv_rate = round((funnel.conversions or 0) / funnel.views_count * 100, 1)
    
    text = f"""<b>📊 СТАТИСТИКА ВОРОНКИ</b>
<i>{funnel.name}</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>📈 МЕТРИКИ:</b>
├ 👁 Переглядів: <b>{funnel.views_count or 0}</b>
├ ✅ Конверсій: <b>{funnel.conversions or 0}</b>
├ 📊 Конверсія: <b>{conv_rate}%</b>
└ 📝 Кроків пройдено: <b>{funnel.steps_count}</b>

<b>📅 ДАТИ:</b>
├ 🗓 Створено: {funnel.created_at.strftime('%d.%m.%Y') if funnel.created_at else 'N/A'}
└ ✏️ Оновлено: {funnel.updated_at.strftime('%d.%m.%Y') if funnel.updated_at else 'N/A'}"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ До воронки", callback_data=f"funnel_view_{funnel_id}")]
    ])
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@funnels_router.callback_query(F.data.startswith("funnel_delete_"))
async def funnel_delete_confirm(query: CallbackQuery):
    await query.answer()
    funnel_id = int(query.data.split("_")[-1])
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Так, видалити", callback_data=f"funnel_delete_confirm_{funnel_id}"),
            InlineKeyboardButton(text="❌ Ні", callback_data=f"funnel_view_{funnel_id}")
        ]
    ])
    await query.message.edit_text(
        "⚠️ <b>ВИДАЛЕННЯ ВОРОНКИ</b>\n\n"
        "Ви впевнені? Це видалить воронку та всі її кроки!",
        reply_markup=kb, parse_mode="HTML"
    )

@funnels_router.callback_query(F.data.startswith("funnel_delete_confirm_"))
async def funnel_delete_execute(query: CallbackQuery):
    await query.answer("Видалено!")
    funnel_id = int(query.data.split("_")[-1])
    funnel_service.delete_funnel(funnel_id)
    
    user_id = str(query.from_user.id)
    funnels = funnel_service.get_funnels_by_owner(user_id)
    await query.message.edit_text(
        "✅ Воронку успішно видалено!",
        reply_markup=funnels_main_kb(funnels),
        parse_mode="HTML"
    )

@funnels_router.callback_query(F.data.startswith("funnel_steps_"))
async def funnel_steps_list(query: CallbackQuery):
    await query.answer()
    funnel_id = int(query.data.split("_")[-1])
    funnel = funnel_service.get_funnel(funnel_id)
    steps = funnel_service.get_steps(funnel_id)
    
    text = f"""<b>📋 КРОКИ ВОРОНКИ</b>
<i>{funnel.name if funnel else 'N/A'}</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>📝 Всього кроків:</b> {len(steps)}

Виберіть крок для редагування:"""
    
    await query.message.edit_text(text, reply_markup=funnel_steps_kb(funnel_id, steps), parse_mode="HTML")

@funnels_router.callback_query(F.data.startswith("step_add_"))
async def step_add_start(query: CallbackQuery, state: FSMContext):
    await query.answer()
    funnel_id = int(query.data.split("_")[-1])
    await state.update_data(adding_step_funnel_id=funnel_id)
    await state.set_state(FunnelStates.waiting_step_content)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data=f"funnel_steps_{funnel_id}")]
    ])
    await query.message.edit_text(
        "<b>➕ ДОДАВАННЯ КРОКУ</b>\n\n"
        "Введіть текст для цього кроку воронки:\n"
        "<i>Можете використовувати HTML теги: &lt;b&gt;, &lt;i&gt;, &lt;code&gt;</i>",
        reply_markup=kb, parse_mode="HTML"
    )

@funnels_router.message(FunnelStates.waiting_step_content)
async def step_add_content(message: Message, state: FSMContext):
    data = await state.get_data()
    funnel_id = data.get("adding_step_funnel_id")
    content = message.text
    
    await state.update_data(step_content=content)
    await state.set_state(FunnelStates.waiting_step_photo)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭ Пропустити фото", callback_data="step_skip_photo")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data=f"funnel_steps_{funnel_id}")]
    ])
    await message.answer(
        "📸 Тепер надішліть фото для цього кроку (необов'язково):",
        reply_markup=kb
    )

@funnels_router.message(FunnelStates.waiting_step_photo, F.photo)
async def step_add_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    funnel_id = data.get("adding_step_funnel_id")
    content = data.get("step_content")
    photo_id = message.photo[-1].file_id
    
    step = funnel_service.add_step(funnel_id, content, photo_file_id=photo_id)
    await state.clear()
    
    if step:
        steps = funnel_service.get_steps(funnel_id)
        await message.answer(f"✅ Крок #{step.step_order} додано з фото!", 
                           reply_markup=funnel_steps_kb(funnel_id, steps))
    else:
        await message.answer("❌ Помилка додавання кроку")

@funnels_router.callback_query(F.data == "step_skip_photo")
async def step_skip_photo(query: CallbackQuery, state: FSMContext):
    await query.answer()
    data = await state.get_data()
    funnel_id = data.get("adding_step_funnel_id")
    content = data.get("step_content")
    
    step = funnel_service.add_step(funnel_id, content)
    await state.clear()
    
    if step:
        steps = funnel_service.get_steps(funnel_id)
        await query.message.edit_text(f"✅ Крок #{step.step_order} додано!", 
                                     reply_markup=funnel_steps_kb(funnel_id, steps))
    else:
        await query.message.edit_text("❌ Помилка додавання кроку")

@funnels_router.callback_query(F.data.startswith("step_view_"))
async def step_view(query: CallbackQuery):
    await query.answer()
    step_id = int(query.data.split("_")[-1])
    
    from utils.db import SessionLocal
    from database.models import FunnelStep
    db = SessionLocal()
    try:
        step = db.query(FunnelStep).filter(FunnelStep.id == step_id).first()
        if not step:
            await query.message.edit_text("❌ Крок не знайдено")
            return
        
        funnel_id = step.funnel_id
        text = f"""<b>📝 КРОК #{step.step_order}</b>

━━━━━━━━━━━━━━━━━━━━━━━

<b>📄 Контент:</b>
{step.content[:500]}{'...' if len(step.content) > 500 else ''}

<b>🖼 Фото:</b> {'Є' if step.photo_file_id else 'Немає'}
<b>🔘 Кнопка:</b> {step.button_text}"""
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ Редагувати", callback_data=f"step_edit_{step_id}"),
                InlineKeyboardButton(text="🗑 Видалити", callback_data=f"step_delete_{step_id}")
            ],
            [InlineKeyboardButton(text="◀️ До кроків", callback_data=f"funnel_steps_{funnel_id}")]
        ])
        await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    finally:
        db.close()

@funnels_router.callback_query(F.data.startswith("step_delete_"))
async def step_delete(query: CallbackQuery):
    await query.answer("Видалено!")
    step_id = int(query.data.split("_")[-1])
    
    from utils.db import SessionLocal
    from database.models import FunnelStep
    db = SessionLocal()
    try:
        step = db.query(FunnelStep).filter(FunnelStep.id == step_id).first()
        funnel_id = step.funnel_id if step else None
    finally:
        db.close()
    
    funnel_service.delete_step(step_id)
    
    if funnel_id:
        steps = funnel_service.get_steps(funnel_id)
        await query.message.edit_text("✅ Крок видалено!", reply_markup=funnel_steps_kb(funnel_id, steps))

@funnels_router.callback_query(F.data.startswith("step_edit_"))
async def step_edit_start(query: CallbackQuery, state: FSMContext):
    await query.answer()
    step_id = int(query.data.split("_")[-1])
    
    from utils.db import SessionLocal
    from database.models import FunnelStep
    db = SessionLocal()
    try:
        step = db.query(FunnelStep).filter(FunnelStep.id == step_id).first()
        if not step:
            await query.message.edit_text("❌ Крок не знайдено")
            return
        funnel_id = step.funnel_id
    finally:
        db.close()
    
    await state.update_data(editing_step_id=step_id, editing_step_funnel_id=funnel_id)
    await state.set_state(FunnelStates.editing_step_content)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data=f"step_view_{step_id}")]
    ])
    await query.message.edit_text(
        "<b>✏️ РЕДАГУВАННЯ КРОКУ</b>\n\n"
        "Введіть новий текст для цього кроку:",
        reply_markup=kb, parse_mode="HTML"
    )

@funnels_router.message(FunnelStates.editing_step_content)
async def step_edit_content_save(message: Message, state: FSMContext):
    data = await state.get_data()
    step_id = data.get("editing_step_id")
    funnel_id = data.get("editing_step_funnel_id")
    
    if funnel_service.update_step(step_id, content=message.text):
        await state.clear()
        steps = funnel_service.get_steps(funnel_id)
        await message.answer("✅ Текст кроку оновлено!", reply_markup=funnel_steps_kb(funnel_id, steps))
    else:
        await message.answer("❌ Помилка збереження")

@funnels_router.callback_query(F.data.startswith("funnel_templates_"))
async def funnel_templates(query: CallbackQuery):
    await query.answer()
    funnel_id = int(query.data.split("_")[-1])
    funnel = funnel_service.get_funnel(funnel_id)
    
    text = f"""<b>📝 ШАБЛОНИ ДЛЯ ВОРОНКИ</b>
<i>{funnel.name if funnel else 'Воронка'}</i>

═══════════════════════════════

Шаблони дозволяють швидко створювати 
повідомлення для кроків воронки.

<b>Категорії шаблонів:</b>
├ 👋 Привітальні — для першого контакту
├ 📢 Промо — акції та пропозиції  
├ 📰 Новини — інформаційні повідомлення
├ ⏰ Нагадування — follow-up
├ 🚨 Алерти — термінові сповіщення
└ 📄 Загальні — універсальні шаблони

<b>Змінні для персоналізації:</b>
├ <code>{name}</code> — ім'я користувача
├ <code>{username}</code> — @username
├ <code>{date}</code> — поточна дата
└ <code>{time}</code> — поточний час"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Мої шаблони", callback_data="templates_list")],
        [InlineKeyboardButton(text="➕ Створити шаблон", callback_data="template_create")],
        [InlineKeyboardButton(text="🌐 Публічні шаблони", callback_data="templates_public")],
        [InlineKeyboardButton(text="◀️ До воронки", callback_data=f"funnel_view_{funnel_id}")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@funnels_router.callback_query(F.data.startswith("funnel_schedule_"))
async def funnel_schedule(query: CallbackQuery):
    await query.answer()
    funnel_id = int(query.data.split("_")[-1])
    funnel = funnel_service.get_funnel(funnel_id)
    
    text = f"""<b>📅 ПЛАНУВАННЯ ВОРОНКИ</b>
<i>{funnel.name if funnel else 'Воронка'}</i>

═══════════════════════════════

Налаштуйте автоматичний запуск кроків 
воронки за розкладом.

<b>Типи розкладу:</b>
├ 🔂 Одноразовий — запуск в заданий час
├ ⏱ Інтервальний — кожні N хвилин/годин
├ 📆 Щоденний — в певний час кожен день
├ 📅 Щотижневий — в певні дні тижня
└ 🗓 Щомісячний — в певний день місяця

<b>Поточний статус:</b>
├ 📊 Активних розкладів: 0
└ ⏰ Наступний запуск: не заплановано"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Мої розклади", callback_data="scheduled_list")],
        [InlineKeyboardButton(text="➕ Додати розклад", callback_data=f"funnel_add_schedule_{funnel_id}")],
        [InlineKeyboardButton(text="◀️ До воронки", callback_data=f"funnel_view_{funnel_id}")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@funnels_router.callback_query(F.data.startswith("funnel_add_schedule_"))
async def funnel_add_schedule(query: CallbackQuery):
    await query.answer()
    funnel_id = int(query.data.split("_")[-1])
    
    text = """<b>⏱ ВИБІР ІНТЕРВАЛУ</b>
═══════════════════════════════

Як часто запускати кроки воронки?"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⏱ Щогодини", callback_data=f"funnel_sched_set_{funnel_id}_60"),
            InlineKeyboardButton(text="⏱ Кожні 4 год", callback_data=f"funnel_sched_set_{funnel_id}_240")
        ],
        [
            InlineKeyboardButton(text="📆 Щодня", callback_data=f"funnel_sched_set_{funnel_id}_1440"),
            InlineKeyboardButton(text="📅 Щотижня", callback_data=f"funnel_sched_set_{funnel_id}_10080")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"funnel_schedule_{funnel_id}")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@funnels_router.callback_query(F.data.startswith("funnel_sched_set_"))
async def funnel_schedule_set(query: CallbackQuery):
    parts = query.data.split("_")
    funnel_id = int(parts[3])
    interval = int(parts[4])
    
    interval_names = {60: "щогодини", 240: "кожні 4 години", 1440: "щодня", 10080: "щотижня"}
    
    await query.answer(f"✅ Розклад встановлено: {interval_names.get(interval, f'{interval} хв')}", show_alert=True)
    
    funnel = funnel_service.get_funnel(funnel_id)
    await query.message.edit_text(
        f"✅ Розклад для воронки <b>{funnel.name if funnel else ''}</b> налаштовано!\n\n"
        f"⏱ Інтервал: {interval_names.get(interval, f'{interval} хв')}",
        reply_markup=funnel_view_kb(funnel_id, funnel.is_active if funnel else True),
        parse_mode="HTML"
    )
