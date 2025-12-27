import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.templates_kb import (
    templates_menu_kb, templates_list_kb, template_categories_kb,
    template_view_kb, template_create_category_kb, schedule_type_kb,
    schedule_interval_kb, schedule_target_kb, scheduled_list_kb,
    scheduled_view_kb
)
from services.template_service import template_service, scheduler_service
from utils.db import get_session

logger = logging.getLogger(__name__)

router = Router()

class TemplateStates(StatesGroup):
    waiting_name = State()
    waiting_content = State()
    waiting_media = State()
    editing_content = State()
    schedule_datetime = State()

async def safe_edit(callback: CallbackQuery, text: str, reply_markup=None):
    """Безпечне редагування повідомлення"""
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception:
        await callback.answer()

@router.callback_query(F.data == "templates_menu")
async def templates_menu(callback: CallbackQuery, state: FSMContext):
    """Головне меню шаблонів"""
    await state.clear()
    
    text = """
📝 <b>ШАБЛОНИ РОЗСИЛОК</b>
───────────────═════

Створюйте та керуйте шаблонами для розсилок.
Використовуйте готові шаблони для швидкого запуску кампаній.

<b>Можливості:</b>
├ Створення власних шаблонів
├ Категоризація та пошук
├ Змінні для персоналізації
└ Планування за розкладом
"""
    
    await safe_edit(callback, text, templates_menu_kb())

@router.callback_query(F.data == "templates_list")
async def templates_list(callback: CallbackQuery):
    """Список шаблонів користувача"""
    user_id = str(callback.from_user.id)
    
    async with get_session() as session:
        templates = await template_service.get_templates(
            session, owner_id=user_id, include_public=True
        )
    
    if not templates:
        text = "📭 У вас ще немає шаблонів.\n\nСтворіть перший шаблон!"
        await safe_edit(callback, text, templates_menu_kb())
        return
    
    text = f"""
📋 <b>МОЇ ШАБЛОНИ</b>
───────────────═════

Знайдено шаблонів: {len(templates)}

Виберіть шаблон для перегляду:
"""
    
    await safe_edit(callback, text, templates_list_kb(templates))

@router.callback_query(F.data == "templates_categories")
async def templates_categories(callback: CallbackQuery):
    """Вибір категорії"""
    text = """
📁 <b>КАТЕГОРІЇ ШАБЛОНІВ</b>
───────────────═════

Виберіть категорію:
"""
    await safe_edit(callback, text, template_categories_kb())

@router.callback_query(F.data.startswith("templates_cat:"))
async def templates_by_category(callback: CallbackQuery):
    """Шаблони за категорією"""
    category = callback.data.split(":")[1]
    user_id = str(callback.from_user.id)
    
    async with get_session() as session:
        templates = await template_service.get_templates(
            session, owner_id=user_id, category=category, include_public=True
        )
    
    if not templates:
        await callback.answer("Шаблонів у цій категорії немає", show_alert=True)
        return
    
    category_name = template_service.CATEGORIES.get(category, category)
    text = f"""
📁 <b>{category_name.upper()}</b>
───────────────═════

Знайдено: {len(templates)}
"""
    
    await safe_edit(callback, text, templates_list_kb(templates))

@router.callback_query(F.data == "templates_public")
async def templates_public(callback: CallbackQuery):
    """Публічні шаблони"""
    async with get_session() as session:
        from database.models import MailingTemplate
        from sqlalchemy import select
        
        result = await session.execute(
            select(MailingTemplate).where(MailingTemplate.is_public == True)
        )
        public_templates = result.scalars().all()
        
        templates = [
            {
                'id': t.id,
                'name': t.name,
                'category': t.category,
                'has_media': bool(t.media_file_id),
                'usage_count': t.usage_count
            }
            for t in public_templates
        ]
    
    if not templates:
        await callback.answer("Публічних шаблонів поки немає", show_alert=True)
        return
    
    text = f"""
🌐 <b>ПУБЛІЧНІ ШАБЛОНИ</b>
───────────────═════

Доступно: {len(templates)}
"""
    
    await safe_edit(callback, text, templates_list_kb(templates))

@router.callback_query(F.data == "template_create")
async def template_create(callback: CallbackQuery):
    """Створення шаблону - вибір категорії"""
    text = """
➕ <b>СТВОРЕННЯ ШАБЛОНУ</b>
───────────────═════

Виберіть категорію для нового шаблону:
"""
    await safe_edit(callback, text, template_create_category_kb())

@router.callback_query(F.data.startswith("template_new_cat:"))
async def template_new_category(callback: CallbackQuery, state: FSMContext):
    """Вибрано категорію - введення назви"""
    category = callback.data.split(":")[1]
    
    await state.update_data(category=category)
    await state.set_state(TemplateStates.waiting_name)
    
    await callback.message.edit_text(
        "📝 Введіть назву шаблону:",
        reply_markup=None
    )

@router.message(TemplateStates.waiting_name)
async def template_name_received(message: Message, state: FSMContext):
    """Отримано назву - введення контенту"""
    await state.update_data(name=message.text)
    await state.set_state(TemplateStates.waiting_content)
    
    await message.answer("""
📄 Введіть текст шаблону.

<b>Підтримувані змінні:</b>
├ {name} - ім'я користувача
├ {username} - @username
├ {date} - поточна дата
└ {time} - поточний час

Приклад: Привіт, {name}! Дякуємо за підписку.
""", parse_mode="HTML")

@router.message(TemplateStates.waiting_content)
async def template_content_received(message: Message, state: FSMContext):
    """Отримано контент - збереження"""
    data = await state.get_data()
    user_id = str(message.from_user.id)
    
    async with get_session() as session:
        result = await template_service.create_template(
            session,
            owner_id=user_id,
            name=data['name'],
            content=message.text,
            category=data['category']
        )
    
    await state.clear()
    
    from keyboards.templates_kb import templates_menu_kb
    
    await message.answer(f"""
✅ <b>Шаблон створено!</b>

📋 Назва: {result['name']}
📁 Категорія: {template_service.CATEGORIES.get(result['category'], result['category'])}

Шаблон готовий до використання.
""", reply_markup=templates_menu_kb(), parse_mode="HTML")

@router.callback_query(F.data.startswith("template_view:"))
async def template_view(callback: CallbackQuery):
    """Перегляд шаблону"""
    template_id = int(callback.data.split(":")[1])
    user_id = str(callback.from_user.id)
    
    async with get_session() as session:
        template = await template_service.get_template(session, template_id)
    
    if not template:
        await callback.answer("Шаблон не знайдено", show_alert=True)
        return
    
    is_owner = template['owner_id'] == user_id
    category_name = template_service.CATEGORIES.get(template['category'], template['category'])
    
    text = f"""
📄 <b>{template['name']}</b>
───────────────═════

📁 Категорія: {category_name}
📊 Використань: {template['usage_count']}
{'📎 Є медіа' if template['media_file_id'] else ''}

<b>Текст:</b>
<code>{template['content'][:500]}</code>
{'...' if len(template['content']) > 500 else ''}
"""
    
    await safe_edit(callback, text, template_view_kb(template_id, is_owner))

@router.callback_query(F.data.startswith("template_delete:"))
async def template_delete(callback: CallbackQuery):
    """Видалення шаблону"""
    template_id = int(callback.data.split(":")[1])
    
    async with get_session() as session:
        await template_service.delete_template(session, template_id)
    
    await callback.answer("✅ Шаблон видалено", show_alert=True)
    
    await templates_list(callback)

@router.callback_query(F.data.startswith("template_use:"))
async def template_use(callback: CallbackQuery):
    """Використання шаблону для розсилки"""
    template_id = int(callback.data.split(":")[1])
    
    async with get_session() as session:
        template = await template_service.get_template(session, template_id)
        await template_service.increment_usage(session, template_id)
    
    await callback.answer(f"Шаблон '{template['name']}' готовий до використання")

@router.callback_query(F.data.startswith("template_schedule:"))
async def template_schedule(callback: CallbackQuery):
    """Планування розсилки за шаблоном"""
    template_id = int(callback.data.split(":")[1])
    
    text = """
⏱ <b>ПЛАНУВАННЯ РОЗСИЛКИ</b>
───────────────═════

Виберіть тип розкладу:
"""
    await safe_edit(callback, text, schedule_type_kb(template_id))

@router.callback_query(F.data.startswith("sched_interval:"))
async def schedule_interval(callback: CallbackQuery):
    """Вибір інтервалу"""
    template_id = int(callback.data.split(":")[1])
    
    text = """
⏱ <b>ВИБЕРІТЬ ІНТЕРВАЛ</b>
───────────────═════

Як часто повторювати розсилку?
"""
    await safe_edit(callback, text, schedule_interval_kb(template_id))

@router.callback_query(F.data.startswith("sched_int_set:"))
async def schedule_interval_set(callback: CallbackQuery, state: FSMContext):
    """Встановлено інтервал"""
    parts = callback.data.split(":")
    template_id = int(parts[1])
    interval = int(parts[2])
    
    await state.update_data(template_id=template_id, interval=interval, schedule_type='interval')
    
    text = """
🎯 <b>ВИБЕРІТЬ АУДИТОРІЮ</b>
───────────────═════

Кому надсилати?
"""
    await safe_edit(callback, text, schedule_target_kb(template_id))

@router.callback_query(F.data.startswith("sched_target:"))
async def schedule_target(callback: CallbackQuery, state: FSMContext):
    """Вибір аудиторії"""
    parts = callback.data.split(":")
    template_id = int(parts[1])
    target = parts[2]
    
    data = await state.get_data()
    user_id = str(callback.from_user.id)
    
    target_roles = [target] if target != 'all' else []
    
    async with get_session() as session:
        result = await scheduler_service.create_scheduled_mailing(
            session,
            template_id=template_id,
            owner_id=user_id,
            name=f"Розсилка #{template_id}",
            schedule_type=data.get('schedule_type', 'interval'),
            interval_minutes=data.get('interval', 60),
            target_roles=target_roles
        )
    
    await state.clear()
    
    await callback.answer("✅ Розсилку заплановано!", show_alert=True)
    await templates_menu(callback, state)

@router.callback_query(F.data == "scheduled_list")
async def scheduled_list(callback: CallbackQuery):
    """Список запланованих розсилок"""
    user_id = str(callback.from_user.id)
    
    async with get_session() as session:
        mailings = await scheduler_service.get_scheduled_mailings(session, owner_id=user_id)
    
    if not mailings:
        await callback.answer("Запланованих розсилок немає", show_alert=True)
        return
    
    text = f"""
📅 <b>ЗАПЛАНОВАНІ РОЗСИЛКИ</b>
───────────────═════

Активних: {len([m for m in mailings if m['status'] == 'active'])}
"""
    
    await safe_edit(callback, text, scheduled_list_kb(mailings))

@router.callback_query(F.data.startswith("sched_view:"))
async def scheduled_view(callback: CallbackQuery):
    """Перегляд запланованої розсилки"""
    mailing_id = int(callback.data.split(":")[1])
    
    async with get_session() as session:
        mailings = await scheduler_service.get_scheduled_mailings(session)
        mailing = next((m for m in mailings if m['id'] == mailing_id), None)
    
    if not mailing:
        await callback.answer("Розсилку не знайдено", show_alert=True)
        return
    
    text = f"""
📨 <b>{mailing['name']}</b>
───────────────═════

📅 Тип: {mailing['schedule_type_name']}
⏱ Інтервал: {mailing.get('interval_minutes', '-')} хв
📊 Запусків: {mailing['runs_count']}
📆 Наступний: {mailing['next_run_at']}
🔄 Статус: {mailing['status']}
"""
    
    await safe_edit(callback, text, scheduled_view_kb(mailing_id, mailing['status']))

@router.callback_query(F.data.startswith("sched_pause:"))
async def scheduled_pause(callback: CallbackQuery):
    """Пауза розсилки"""
    mailing_id = int(callback.data.split(":")[1])
    
    async with get_session() as session:
        new_status = await scheduler_service.toggle_status(session, mailing_id)
    
    await callback.answer(f"Статус змінено на: {new_status}", show_alert=True)
    await scheduled_list(callback)

@router.callback_query(F.data.startswith("sched_resume:"))
async def scheduled_resume(callback: CallbackQuery):
    """Відновлення розсилки"""
    mailing_id = int(callback.data.split(":")[1])
    
    async with get_session() as session:
        new_status = await scheduler_service.toggle_status(session, mailing_id)
    
    await callback.answer(f"Статус змінено на: {new_status}", show_alert=True)
    await scheduled_list(callback)

@router.callback_query(F.data.startswith("sched_delete:"))
async def scheduled_delete(callback: CallbackQuery):
    """Видалення запланованої розсилки"""
    mailing_id = int(callback.data.split(":")[1])
    
    async with get_session() as session:
        await scheduler_service.delete_scheduled(session, mailing_id)
    
    await callback.answer("✅ Розсилку видалено", show_alert=True)
    await scheduled_list(callback)

templates_router = router
