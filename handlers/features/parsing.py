"""
Парсинг груп та розсилка в ЛС - UI хендлери
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)
parsing_router = Router()


class ParsingStates(StatesGroup):
    waiting_group_link = State()
    waiting_list_name = State()
    waiting_dm_message = State()
    waiting_dm_name = State()
    waiting_filter_choice = State()


def parsing_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Парсинг групи", callback_data="parse_group")],
        [InlineKeyboardButton(text="📋 Збережені списки", callback_data="parse_lists")],
        [InlineKeyboardButton(text="📧 Розсилка в ЛС", callback_data="dm_menu")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="parse_stats")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="user_menu")]
    ])


def dm_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Нова розсилка", callback_data="dm_new")],
        [InlineKeyboardButton(text="📋 Активні задачі", callback_data="dm_tasks")],
        [InlineKeyboardButton(text="⚙️ Налаштування", callback_data="dm_settings")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="parsing_main")]
    ])


@parsing_router.callback_query(F.data == "parsing_main")
async def parsing_main(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    
    from core.group_parser import group_parser
    from core.dm_sender import dm_sender
    
    parser_stats = group_parser.get_stats()
    dm_stats = dm_sender.get_stats()
    
    text = "<b>🔍 ПАРСИНГ ТА РОЗСИЛКА</b>\n"
    text += "═══════════════════════\n\n"
    text += "<i>Парсинг груп → Збереження → Розсилка в ЛС</i>\n\n"
    text += "<b>📊 Статистика парсингу:</b>\n"
    text += f"├ Спарсено груп: {parser_stats['total_groups']}\n"
    text += f"├ Всього юзерів: {parser_stats['total_users']}\n"
    text += f"└ Збережених списків: {parser_stats['saved_lists']}\n\n"
    text += "<b>📧 Статистика DM:</b>\n"
    text += f"├ Відправлено: {dm_stats['total_sent']}\n"
    text += f"├ Помилок: {dm_stats['total_failed']}\n"
    text += f"└ Активних задач: {dm_stats['active_tasks']}"
    
    await query.message.edit_text(text, reply_markup=parsing_main_kb(), parse_mode="HTML")


@parsing_router.callback_query(F.data == "parse_group")
async def parse_group_start(query: CallbackQuery, state: FSMContext):
    await query.answer()
    if not query.message:
        return
    
    await state.set_state(ParsingStates.waiting_group_link)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="parsing_main")]
    ])
    
    text = "<b>🔍 ПАРСИНГ ГРУПИ</b>\n"
    text += "═══════════════════════\n\n"
    text += "<b>Введіть посилання або username групи:</b>\n\n"
    text += "<i>Приклади:</i>\n"
    text += "├ <code>@channel_username</code>\n"
    text += "├ <code>https://t.me/channel</code>\n"
    text += "└ <code>t.me/joinchat/xxx</code>\n\n"
    text += "⚠️ Бот повинен бути учасником групи"
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@parsing_router.message(ParsingStates.waiting_group_link)
async def process_group_link(message: Message, state: FSMContext):
    link = message.text.strip() if message.text else ""
    
    if not link:
        await message.answer("❌ Введіть посилання на групу")
        return
    
    await state.clear()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Всі учасники", callback_data=f"parse_filter:all:{link}")],
        [InlineKeyboardButton(text="✅ Тільки активні", callback_data=f"parse_filter:active:{link}")],
        [InlineKeyboardButton(text="📱 З username", callback_data=f"parse_filter:username:{link}")],
        [InlineKeyboardButton(text="💎 Тільки Premium", callback_data=f"parse_filter:premium:{link}")],
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="parsing_main")]
    ])
    
    await message.answer(
        f"<b>🎯 ФІЛЬТРИ ПАРСИНГУ</b>\n\n"
        f"<b>Група:</b> <code>{link}</code>\n\n"
        f"<b>Виберіть фільтр:</b>",
        reply_markup=kb, parse_mode="HTML"
    )


@parsing_router.callback_query(F.data.startswith("parse_filter:"))
async def start_parsing(query: CallbackQuery):
    await query.answer()
    if not query.message or not query.data:
        return
    
    parts = query.data.split(":", 2)
    if len(parts) < 3:
        return
    
    filter_type = parts[1]
    link = parts[2]
    
    from core.group_parser import group_parser, ParserFilter
    
    filters_map = {
        "all": [ParserFilter.NOT_BOTS],
        "active": [ParserFilter.NOT_BOTS, ParserFilter.ACTIVE_RECENTLY],
        "username": [ParserFilter.NOT_BOTS, ParserFilter.WITH_USERNAME],
        "premium": [ParserFilter.NOT_BOTS, ParserFilter.PREMIUM_ONLY]
    }
    
    filters = filters_map.get(filter_type, [ParserFilter.NOT_BOTS])
    
    await query.message.edit_text(
        "⏳ <b>ПАРСИНГ ЗАПУЩЕНО...</b>\n\n"
        f"<b>Група:</b> <code>{link}</code>\n"
        f"<b>Фільтр:</b> {filter_type}\n\n"
        "<i>Це може зайняти кілька хвилин...</i>",
        parse_mode="HTML"
    )
    
    result = await group_parser.parse_group(link, limit=500, filters=filters)
    
    text = group_parser.format_parse_result(result)
    
    job_id = result.get("job_id", "")
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💾 Зберегти список", callback_data=f"parse_save:{job_id}")],
        [InlineKeyboardButton(text="📧 Розсилка в ЛС", callback_data=f"parse_to_dm:{job_id}")],
        [InlineKeyboardButton(text="🔄 Новий парсинг", callback_data="parse_group")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="parsing_main")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@parsing_router.callback_query(F.data.startswith("parse_save:"))
async def save_parsed_list(query: CallbackQuery, state: FSMContext):
    await query.answer()
    if not query.message or not query.data:
        return
    
    job_id = query.data.replace("parse_save:", "")
    await state.update_data(save_job_id=job_id)
    await state.set_state(ParsingStates.waiting_list_name)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="parsing_main")]
    ])
    
    await query.message.edit_text(
        "<b>💾 ЗБЕРЕЖЕННЯ СПИСКУ</b>\n\n"
        "<b>Введіть назву для списку:</b>\n"
        "<i>Наприклад: 'Криптотрейдери' або 'IT-група'</i>",
        reply_markup=kb, parse_mode="HTML"
    )


@parsing_router.message(ParsingStates.waiting_list_name)
async def process_list_name(message: Message, state: FSMContext):
    data = await state.get_data()
    job_id = data.get("save_job_id", "")
    list_name = message.text.strip() if message.text else ""
    await state.clear()
    
    if not list_name:
        await message.answer("❌ Введіть назву списку")
        return
    
    from core.group_parser import group_parser
    
    job = group_parser.get_job(job_id)
    if not job:
        await message.answer("❌ Задачу парсингу не знайдено")
        return
    
    user_ids = [u.user_id for u in job.users]
    group_parser.save_user_list(list_name, user_ids)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 Розсилка цьому списку", callback_data=f"dm_to_list:{list_name}")],
        [InlineKeyboardButton(text="📋 Всі списки", callback_data="parse_lists")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="parsing_main")]
    ])
    
    await message.answer(
        f"✅ <b>СПИСОК ЗБЕРЕЖЕНО!</b>\n\n"
        f"<b>Назва:</b> {list_name}\n"
        f"<b>Користувачів:</b> {len(user_ids)}",
        reply_markup=kb, parse_mode="HTML"
    )


@parsing_router.callback_query(F.data == "parse_lists")
async def show_parse_lists(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    
    from core.group_parser import group_parser
    
    lists = group_parser.get_all_user_lists()
    
    text = "<b>📋 ЗБЕРЕЖЕНІ СПИСКИ</b>\n"
    text += "═══════════════════════\n\n"
    
    buttons = []
    
    if lists:
        for name, count in lists.items():
            text += f"├ <b>{name}</b>: {count} юзерів\n"
            buttons.append([InlineKeyboardButton(
                text=f"📧 {name} ({count})",
                callback_data=f"dm_to_list:{name}"
            )])
    else:
        text += "<i>Немає збережених списків</i>\n"
        text += "Спочатку спарсіть групу та збережіть список"
    
    buttons.append([InlineKeyboardButton(text="🔍 Новий парсинг", callback_data="parse_group")])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="parsing_main")])
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@parsing_router.callback_query(F.data == "dm_menu")
async def dm_menu(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    
    from core.dm_sender import dm_sender
    
    stats = dm_sender.get_stats()
    tasks = dm_sender.get_all_tasks()
    
    text = "<b>📧 РОЗСИЛКА В ЛС</b>\n"
    text += "═══════════════════════\n\n"
    text += "<b>📊 Статистика:</b>\n"
    text += f"├ Відправлено: {stats['total_sent']}\n"
    text += f"├ Помилок: {stats['total_failed']}\n"
    text += f"├ Активних: {stats['active_tasks']}\n"
    text += f"├ Очікують: {stats['pending_tasks']}\n"
    text += f"└ Чорний список: {stats['blacklist_size']}\n\n"
    
    if tasks:
        text += "<b>📋 Останні задачі:</b>\n"
        for task in tasks[-5:]:
            status_icon = {
                "pending": "⏳",
                "sending": "📤",
                "completed": "✅",
                "paused": "⏸️",
                "failed": "❌"
            }.get(task["status"], "❓")
            text += f"├ {status_icon} {task['name']}: {task['sent_count']}/{task['total_count']}\n"
    
    await query.message.edit_text(text, reply_markup=dm_menu_kb(), parse_mode="HTML")


@parsing_router.callback_query(F.data == "dm_new")
async def dm_new(query: CallbackQuery, state: FSMContext):
    await query.answer()
    if not query.message:
        return
    
    from core.group_parser import group_parser
    
    lists = group_parser.get_all_user_lists()
    parsed_count = len(group_parser.parsed_users_db)
    
    buttons = []
    
    if parsed_count > 0:
        buttons.append([InlineKeyboardButton(
            text=f"📥 Останні спарсені ({parsed_count})",
            callback_data="dm_from_parsed"
        )])
    
    for name, count in list(lists.items())[:5]:
        buttons.append([InlineKeyboardButton(
            text=f"📋 {name} ({count})",
            callback_data=f"dm_to_list:{name}"
        )])
    
    if not buttons:
        buttons.append([InlineKeyboardButton(text="🔍 Спочатку спарсіть групу", callback_data="parse_group")])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="dm_menu")])
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await query.message.edit_text(
        "<b>📤 НОВА РОЗСИЛКА В ЛС</b>\n"
        "═══════════════════════\n\n"
        "<b>Виберіть джерело користувачів:</b>",
        reply_markup=kb, parse_mode="HTML"
    )


@parsing_router.callback_query(F.data == "dm_from_parsed")
async def dm_from_parsed(query: CallbackQuery, state: FSMContext):
    await query.answer()
    if not query.message:
        return
    
    from core.group_parser import group_parser
    
    user_ids = group_parser.get_user_ids_for_mailing()
    await state.update_data(dm_user_ids=user_ids, dm_source="parsed")
    await state.set_state(ParsingStates.waiting_dm_name)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="dm_menu")]
    ])
    
    await query.message.edit_text(
        f"<b>📤 РОЗСИЛКА: {len(user_ids)} користувачів</b>\n\n"
        "<b>Введіть назву розсилки:</b>",
        reply_markup=kb, parse_mode="HTML"
    )


@parsing_router.callback_query(F.data.startswith("dm_to_list:"))
async def dm_to_list(query: CallbackQuery, state: FSMContext):
    await query.answer()
    if not query.message or not query.data:
        return
    
    list_name = query.data.replace("dm_to_list:", "")
    
    from core.group_parser import group_parser
    
    user_ids = group_parser.get_user_list(list_name)
    
    if not user_ids:
        await query.message.edit_text(f"❌ Список '{list_name}' порожній або не знайдено")
        return
    
    await state.update_data(dm_user_ids=user_ids, dm_source=list_name)
    await state.set_state(ParsingStates.waiting_dm_name)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="dm_menu")]
    ])
    
    await query.message.edit_text(
        f"<b>📤 РОЗСИЛКА: {len(user_ids)} користувачів</b>\n"
        f"<b>Список:</b> {list_name}\n\n"
        "<b>Введіть назву розсилки:</b>",
        reply_markup=kb, parse_mode="HTML"
    )


@parsing_router.message(ParsingStates.waiting_dm_name)
async def process_dm_name(message: Message, state: FSMContext):
    name = message.text.strip() if message.text else ""
    
    if not name:
        await message.answer("❌ Введіть назву розсилки")
        return
    
    await state.update_data(dm_name=name)
    await state.set_state(ParsingStates.waiting_dm_message)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="dm_menu")]
    ])
    
    await message.answer(
        f"<b>📝 ТЕКСТ ПОВІДОМЛЕННЯ</b>\n\n"
        f"<b>Розсилка:</b> {name}\n\n"
        f"<b>Введіть текст:</b>\n\n"
        f"<i>Доступні змінні:</i>\n"
        f"├ <code>{{name}}</code> - ім'я\n"
        f"├ <code>{{username}}</code> - username\n"
        f"├ <code>{{date}}</code> - дата\n"
        f"└ <code>{{time}}</code> - час",
        reply_markup=kb, parse_mode="HTML"
    )


@parsing_router.message(ParsingStates.waiting_dm_message)
async def process_dm_message(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_text = message.text.strip() if message.text else ""
    await state.clear()
    
    if not msg_text:
        await message.answer("❌ Введіть текст повідомлення")
        return
    
    name = data.get("dm_name", "Розсилка")
    user_ids = data.get("dm_user_ids", [])
    source = data.get("dm_source", "unknown")
    
    if not user_ids:
        await message.answer("❌ Немає користувачів для розсилки")
        return
    
    from core.dm_sender import dm_sender
    
    task_id = str(uuid.uuid4())[:8]
    task = dm_sender.create_task(
        task_id=task_id,
        name=name,
        message_template=msg_text,
        target_users=user_ids,
        interval_min=30,
        interval_max=60
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ ЗАПУСТИТИ", callback_data=f"dm_start:{task_id}")],
        [InlineKeyboardButton(text="⚙️ Налаштувати інтервал", callback_data=f"dm_interval:{task_id}")],
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="dm_menu")]
    ])
    
    await message.answer(
        f"<b>✅ РОЗСИЛКА СТВОРЕНА!</b>\n"
        f"═══════════════════════\n\n"
        f"<b>Назва:</b> {name}\n"
        f"<b>Джерело:</b> {source}\n"
        f"<b>Користувачів:</b> {task.total_count}\n\n"
        f"<b>Текст:</b>\n<i>{msg_text[:200]}...</i>\n\n"
        f"<b>Інтервал:</b> 30-60 сек",
        reply_markup=kb, parse_mode="HTML"
    )


@parsing_router.callback_query(F.data.startswith("dm_start:"))
async def dm_start(query: CallbackQuery):
    await query.answer()
    if not query.message or not query.data:
        return
    
    task_id = query.data.replace("dm_start:", "")
    
    from core.dm_sender import dm_sender
    
    result = await dm_sender.start_task(task_id)
    
    if "error" in result:
        await query.message.edit_text(f"❌ <b>Помилка:</b> {result['error']}", parse_mode="HTML")
        return
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статус", callback_data=f"dm_status:{task_id}")],
        [InlineKeyboardButton(text="⏹️ Зупинити", callback_data=f"dm_stop:{task_id}")],
        [InlineKeyboardButton(text="◀️ До меню", callback_data="dm_menu")]
    ])
    
    await query.message.edit_text(
        f"<b>▶️ РОЗСИЛКА ЗАПУЩЕНА!</b>\n\n"
        f"<b>ID:</b> <code>{task_id}</code>\n"
        f"<b>Користувачів:</b> {result.get('total_users', 0)}\n\n"
        f"<i>Розсилка працює у фоновому режимі</i>",
        reply_markup=kb, parse_mode="HTML"
    )


@parsing_router.callback_query(F.data.startswith("dm_stop:"))
async def dm_stop(query: CallbackQuery):
    await query.answer()
    if not query.message or not query.data:
        return
    
    task_id = query.data.replace("dm_stop:", "")
    
    from core.dm_sender import dm_sender
    
    result = await dm_sender.stop_task(task_id)
    
    text = dm_sender.format_task_status(task_id)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Продовжити", callback_data=f"dm_start:{task_id}")],
        [InlineKeyboardButton(text="◀️ До меню", callback_data="dm_menu")]
    ])
    
    await query.message.edit_text(
        f"⏹️ <b>РОЗСИЛКУ ЗУПИНЕНО</b>\n\n{text}",
        reply_markup=kb, parse_mode="HTML"
    )


@parsing_router.callback_query(F.data.startswith("dm_status:"))
async def dm_status(query: CallbackQuery):
    await query.answer()
    if not query.message or not query.data:
        return
    
    task_id = query.data.replace("dm_status:", "")
    
    from core.dm_sender import dm_sender
    
    text = dm_sender.format_task_status(task_id)
    task = dm_sender.get_task(task_id)
    
    buttons = []
    if task and task.status.value == "sending":
        buttons.append([InlineKeyboardButton(text="⏹️ Зупинити", callback_data=f"dm_stop:{task_id}")])
        buttons.append([InlineKeyboardButton(text="🔄 Оновити", callback_data=f"dm_status:{task_id}")])
    elif task and task.status.value in ["paused", "pending"]:
        buttons.append([InlineKeyboardButton(text="▶️ Запустити", callback_data=f"dm_start:{task_id}")])
    
    buttons.append([InlineKeyboardButton(text="◀️ До меню", callback_data="dm_menu")])
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@parsing_router.callback_query(F.data == "dm_tasks")
async def dm_tasks(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    
    from core.dm_sender import dm_sender
    
    tasks = dm_sender.get_all_tasks()
    
    text = "<b>📋 ЗАДАЧІ РОЗСИЛКИ</b>\n"
    text += "═══════════════════════\n\n"
    
    buttons = []
    
    if tasks:
        for task in tasks[-10:]:
            status_icon = {
                "pending": "⏳",
                "sending": "📤",
                "completed": "✅",
                "paused": "⏸️",
                "failed": "❌"
            }.get(task["status"], "❓")
            
            text += f"{status_icon} <b>{task['name']}</b>\n"
            text += f"   └ {task['sent_count']}/{task['total_count']} ({task['progress']}%)\n"
            
            buttons.append([InlineKeyboardButton(
                text=f"{status_icon} {task['name']}",
                callback_data=f"dm_status:{task['task_id']}"
            )])
    else:
        text += "<i>Немає задач</i>"
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="dm_menu")])
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@parsing_router.callback_query(F.data == "parse_stats")
async def parse_stats(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    
    from core.group_parser import group_parser
    from core.dm_sender import dm_sender
    
    parser_stats = group_parser.get_stats()
    dm_stats = dm_sender.get_stats()
    jobs = group_parser.get_all_jobs()
    
    text = "<b>📊 ПОВНА СТАТИСТИКА</b>\n"
    text += "═══════════════════════\n\n"
    
    text += "<b>🔍 Парсинг:</b>\n"
    text += f"├ Всього спарсено: {parser_stats['total_parsed']}\n"
    text += f"├ Груп оброблено: {parser_stats['total_groups']}\n"
    text += f"├ Унікальних юзерів: {parser_stats['total_users']}\n"
    text += f"├ Активних задач: {parser_stats['active_jobs']}\n"
    text += f"└ Збережених списків: {parser_stats['saved_lists']}\n\n"
    
    text += "<b>📧 Розсилка DM:</b>\n"
    text += f"├ Відправлено: {dm_stats['total_sent']}\n"
    text += f"├ Помилок: {dm_stats['total_failed']}\n"
    text += f"├ Активних: {dm_stats['active_tasks']}\n"
    text += f"├ В чорному списку: {dm_stats['blacklist_size']}\n"
    text += f"└ Завершених: {dm_stats['completed_tasks']}\n\n"
    
    if jobs:
        text += "<b>📋 Останні парсинги:</b>\n"
        for job in jobs[-5:]:
            status_icon = "✅" if job["status"] == "completed" else "⏳"
            text += f"├ {status_icon} {job['chat_title'][:20]}: {job['parsed_count']}\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑️ Очистити базу", callback_data="parse_clear")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="parsing_main")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@parsing_router.callback_query(F.data == "parse_clear")
async def parse_clear(query: CallbackQuery):
    from core.group_parser import group_parser
    
    group_parser.clear_parsed_users()
    
    await query.answer("✅ Базу очищено", show_alert=True)
