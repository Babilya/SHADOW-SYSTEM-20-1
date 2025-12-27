from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from config.settings import ADMIN_IDS
from sqlalchemy import select
from utils.db import async_session
from database.models import UIConfig, UIButton, UIStyle
from datetime import datetime

ui_editor_router = Router()

class UIEditorStates(StatesGroup):
    editing_menu = State()
    editing_title = State()
    editing_description = State()
    editing_banner = State()
    adding_button = State()
    editing_button_text = State()
    editing_button_callback = State()
    editing_style = State()

DEFAULT_MENUS = {
    "guest": {"title": "SHADOW SYSTEM iO v2.0", "icon": "🌐"},
    "manager": {"title": "SHADOW SYSTEM iO v2.0", "icon": "🌟"},
    "leader": {"title": "SHADOW SYSTEM iO v2.0", "icon": "👑"},
    "admin": {"title": "SHADOW SYSTEM iO v2.0", "icon": "🛡️"},
    "osint": {"title": "OSINT & ПАРСИНГ", "icon": "🔍"},
    "security": {"title": "БЕЗПЕКА", "icon": "🔒"},
    "help": {"title": "ДОВІДКА", "icon": "📖"},
}

def ui_editor_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 МЕНЮ ЗА РОЛЯМИ", callback_data="ui_edit_roles")],
        [InlineKeyboardButton(text="🔘 РЕДАКТОР КНОПОК", callback_data="ui_edit_buttons")],
        [InlineKeyboardButton(text="🎨 ГЛОБАЛЬНІ СТИЛІ", callback_data="ui_edit_styles")],
        [InlineKeyboardButton(text="🖼 БАНЕРИ", callback_data="ui_edit_banners")],
        [InlineKeyboardButton(text="👁 ПРЕВ'Ю", callback_data="ui_preview")],
        [InlineKeyboardButton(text="◀️ НАЗАД", callback_data="admin_system")]
    ])

@ui_editor_router.callback_query(F.data == "ui_editor")
async def ui_editor_main(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    text = """══════════════════════════
🎨 <b>РЕДАКТОР ІНТЕРФЕЙСУ</b>
══════════════════════════
<i>Налаштування вигляду бота</i>

<b>📋 МОЖЛИВОСТІ:</b>
├ Зміна заголовків меню
├ Редагування описів
├ Додавання/видалення кнопок
├ Налаштування банерів
└ Глобальні стилі

<b>💡 ПІДКАЗКА:</b>
Зміни застосовуються одразу"""
    
    await query.message.edit_text(text, reply_markup=ui_editor_kb(), parse_mode="HTML")
    await query.answer()

@ui_editor_router.callback_query(F.data == "ui_edit_roles")
async def ui_edit_roles(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 GUEST меню", callback_data="ui_role_guest")],
        [InlineKeyboardButton(text="🌟 MANAGER меню", callback_data="ui_role_manager")],
        [InlineKeyboardButton(text="👑 LEADER меню", callback_data="ui_role_leader")],
        [InlineKeyboardButton(text="🛡️ ADMIN меню", callback_data="ui_role_admin")],
        [InlineKeyboardButton(text="◀️ НАЗАД", callback_data="ui_editor")]
    ])
    
    text = """══════════════════════════
📝 <b>МЕНЮ ЗА РОЛЯМИ</b>
══════════════════════════
<i>Оберіть меню для редагування</i>

<b>📋 ДОСТУПНІ МЕНЮ:</b>
├ 🌐 Guest — гостьовий доступ
├ 🌟 Manager — менеджер
├ 👑 Leader — лідер проекту
└ 🛡️ Admin — адміністратор"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()

@ui_editor_router.callback_query(F.data.startswith("ui_role_"))
async def ui_role_edit(query: CallbackQuery, state: FSMContext):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    role = query.data.replace("ui_role_", "")
    menu_info = DEFAULT_MENUS.get(role, {"title": role.upper(), "icon": "📋"})
    
    async with async_session() as session:
        result = await session.execute(
            select(UIConfig).where(UIConfig.menu_key == role)
        )
        config = result.scalar_one_or_none()
    
    current_title = config.title if config else menu_info["title"]
    current_desc = config.description if config else "Опис не встановлено"
    current_banner = config.banner_text if config and config.banner_text else "Немає"
    
    await state.update_data(editing_role=role)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Змінити заголовок", callback_data=f"ui_set_title_{role}")],
        [InlineKeyboardButton(text="📝 Змінити опис", callback_data=f"ui_set_desc_{role}")],
        [InlineKeyboardButton(text="🖼 Встановити банер", callback_data=f"ui_set_banner_{role}")],
        [InlineKeyboardButton(text="🔘 Редагувати кнопки", callback_data=f"ui_buttons_{role}")],
        [InlineKeyboardButton(text="👁 Прев'ю", callback_data=f"ui_preview_{role}")],
        [InlineKeyboardButton(text="◀️ НАЗАД", callback_data="ui_edit_roles")]
    ])
    
    text = f"""══════════════════════════
{menu_info['icon']} <b>РЕДАГУВАННЯ: {role.upper()}</b>
══════════════════════════

<b>📋 ПОТОЧНІ НАЛАШТУВАННЯ:</b>
├ <b>Заголовок:</b> {current_title}
├ <b>Опис:</b> {current_desc[:50]}...
└ <b>Банер:</b> {current_banner[:30]}...

<b>💡</b> Оберіть що редагувати:"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()

@ui_editor_router.callback_query(F.data.startswith("ui_set_title_"))
async def ui_set_title_start(query: CallbackQuery, state: FSMContext):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    role = query.data.replace("ui_set_title_", "")
    await state.update_data(editing_role=role)
    await state.set_state(UIEditorStates.editing_title)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data=f"ui_role_{role}")]
    ])
    
    await query.message.edit_text(
        "══════════════════════════\n"
        "✏️ <b>НОВИЙ ЗАГОЛОВОК</b>\n"
        "══════════════════════════\n"
        f"Введіть новий заголовок для <b>{role.upper()}</b>:\n"
        "<i>Макс. 100 символів</i>",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@ui_editor_router.message(UIEditorStates.editing_title)
async def ui_set_title_process(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    data = await state.get_data()
    role = data.get("editing_role")
    new_title = message.text.strip()[:100]
    
    async with async_session() as session:
        result = await session.execute(
            select(UIConfig).where(UIConfig.menu_key == role)
        )
        config = result.scalar_one_or_none()
        
        if config:
            config.title = new_title
            config.updated_by = str(message.from_user.id)
            config.updated_at = datetime.now()
        else:
            config = UIConfig(
                menu_key=role,
                title=new_title,
                description="",
                updated_by=str(message.from_user.id)
            )
            session.add(config)
        
        await session.commit()
    
    await state.clear()
    await message.answer(
        f"✅ Заголовок для <b>{role.upper()}</b> оновлено:\n"
        f"<code>{new_title}</code>",
        parse_mode="HTML"
    )

@ui_editor_router.callback_query(F.data.startswith("ui_set_desc_"))
async def ui_set_desc_start(query: CallbackQuery, state: FSMContext):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    role = query.data.replace("ui_set_desc_", "")
    await state.update_data(editing_role=role)
    await state.set_state(UIEditorStates.editing_description)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data=f"ui_role_{role}")]
    ])
    
    await query.message.edit_text(
        "══════════════════════════\n"
        "📝 <b>НОВИЙ ОПИС</b>\n"
        "══════════════════════════\n"
        f"Введіть новий опис для <b>{role.upper()}</b>:\n"
        "<i>Підтримує HTML форматування</i>",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@ui_editor_router.message(UIEditorStates.editing_description)
async def ui_set_desc_process(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    data = await state.get_data()
    role = data.get("editing_role")
    new_desc = message.text.strip()
    
    async with async_session() as session:
        result = await session.execute(
            select(UIConfig).where(UIConfig.menu_key == role)
        )
        config = result.scalar_one_or_none()
        
        if config:
            config.description = new_desc
            config.updated_by = str(message.from_user.id)
            config.updated_at = datetime.now()
        else:
            config = UIConfig(
                menu_key=role,
                title=DEFAULT_MENUS.get(role, {}).get("title", role.upper()),
                description=new_desc,
                updated_by=str(message.from_user.id)
            )
            session.add(config)
        
        await session.commit()
    
    await state.clear()
    await message.answer(
        f"✅ Опис для <b>{role.upper()}</b> оновлено!",
        parse_mode="HTML"
    )

@ui_editor_router.callback_query(F.data.startswith("ui_set_banner_"))
async def ui_set_banner_start(query: CallbackQuery, state: FSMContext):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    role = query.data.replace("ui_set_banner_", "")
    await state.update_data(editing_role=role)
    await state.set_state(UIEditorStates.editing_banner)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Видалити банер", callback_data=f"ui_del_banner_{role}")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data=f"ui_role_{role}")]
    ])
    
    await query.message.edit_text(
        "══════════════════════════\n"
        "🖼 <b>БАНЕР МЕНЮ</b>\n"
        "══════════════════════════\n"
        f"Введіть текст банера для <b>{role.upper()}</b>:\n\n"
        "<i>Приклад:</i>\n"
        "<code>🔥 АКЦІЯ! -50% на всі тарифи!</code>",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@ui_editor_router.message(UIEditorStates.editing_banner)
async def ui_set_banner_process(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    data = await state.get_data()
    role = data.get("editing_role")
    new_banner = message.text.strip()
    
    async with async_session() as session:
        result = await session.execute(
            select(UIConfig).where(UIConfig.menu_key == role)
        )
        config = result.scalar_one_or_none()
        
        if config:
            config.banner_text = new_banner
            config.updated_by = str(message.from_user.id)
            config.updated_at = datetime.now()
        else:
            config = UIConfig(
                menu_key=role,
                title=DEFAULT_MENUS.get(role, {}).get("title", role.upper()),
                description="",
                banner_text=new_banner,
                updated_by=str(message.from_user.id)
            )
            session.add(config)
        
        await session.commit()
    
    await state.clear()
    await message.answer(
        f"✅ Банер для <b>{role.upper()}</b> встановлено:\n"
        f"{new_banner}",
        parse_mode="HTML"
    )

@ui_editor_router.callback_query(F.data.startswith("ui_del_banner_"))
async def ui_del_banner(query: CallbackQuery, state: FSMContext):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    role = query.data.replace("ui_del_banner_", "")
    
    async with async_session() as session:
        result = await session.execute(
            select(UIConfig).where(UIConfig.menu_key == role)
        )
        config = result.scalar_one_or_none()
        
        if config:
            config.banner_text = None
            config.updated_by = str(query.from_user.id)
            await session.commit()
    
    await state.clear()
    await query.message.edit_text(
        f"✅ Банер для <b>{role.upper()}</b> видалено!",
        parse_mode="HTML"
    )
    await query.answer()

@ui_editor_router.callback_query(F.data == "ui_edit_styles")
async def ui_edit_styles(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="═══ Подвійні", callback_data="ui_style_double"),
            InlineKeyboardButton(text="─── Одинарні", callback_data="ui_style_single")
        ],
        [
            InlineKeyboardButton(text="▓▓▓ Блокові", callback_data="ui_style_block"),
            InlineKeyboardButton(text="••• Крапки", callback_data="ui_style_dots")
        ],
        [
            InlineKeyboardButton(text="╔╗╚╝ Рамки", callback_data="ui_style_box"),
            InlineKeyboardButton(text="*** Зірочки", callback_data="ui_style_stars")
        ],
        [InlineKeyboardButton(text="🔢 Довжина лінії", callback_data="ui_style_length")],
        [InlineKeyboardButton(text="◀️ НАЗАД", callback_data="ui_editor")]
    ])
    
    text = """══════════════════════════
🎨 <b>ГЛОБАЛЬНІ СТИЛІ</b>
══════════════════════════
<i>Налаштування роздільників</i>

<b>📋 ПОТОЧНИЙ СТИЛЬ:</b>
├ Символ: ═ (подвійний)
├ Довжина: 26 символів
└ Формат: стандартний

<b>💡</b> Оберіть новий стиль:"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()

@ui_editor_router.callback_query(F.data.startswith("ui_style_"))
async def ui_apply_style(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    style = query.data.replace("ui_style_", "")
    
    styles = {
        "double": ("═", 26),
        "single": ("─", 26),
        "block": ("▓", 26),
        "dots": ("•", 26),
        "box": ("═", 26),
        "stars": ("*", 26),
    }
    
    if style == "length":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="20", callback_data="ui_len_20"),
                InlineKeyboardButton(text="24", callback_data="ui_len_24"),
                InlineKeyboardButton(text="26", callback_data="ui_len_26"),
                InlineKeyboardButton(text="28", callback_data="ui_len_28")
            ],
            [InlineKeyboardButton(text="◀️ НАЗАД", callback_data="ui_edit_styles")]
        ])
        await query.message.edit_text(
            "══════════════════════════\n"
            "🔢 <b>ДОВЖИНА ЛІНІЇ</b>\n"
            "══════════════════════════\n"
            "Оберіть кількість символів:\n"
            "<i>Рекомендовано: 26</i>",
            reply_markup=kb, parse_mode="HTML"
        )
        await query.answer()
        return
    
    char, length = styles.get(style, ("═", 26))
    
    async with async_session() as session:
        result = await session.execute(
            select(UIStyle).where(UIStyle.style_key == "global")
        )
        ui_style = result.scalar_one_or_none()
        
        if ui_style:
            ui_style.divider_char = char
            ui_style.divider_length = length
        else:
            ui_style = UIStyle(
                style_key="global",
                divider_char=char,
                divider_length=length
            )
            session.add(ui_style)
        
        await session.commit()
    
    divider = char * length
    await query.answer(f"✅ Стиль змінено: {divider[:10]}...", show_alert=True)

@ui_editor_router.callback_query(F.data.startswith("ui_len_"))
async def ui_set_length(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    length = int(query.data.replace("ui_len_", ""))
    
    async with async_session() as session:
        result = await session.execute(
            select(UIStyle).where(UIStyle.style_key == "global")
        )
        ui_style = result.scalar_one_or_none()
        
        if ui_style:
            ui_style.divider_length = length
        else:
            ui_style = UIStyle(
                style_key="global",
                divider_char="═",
                divider_length=length
            )
            session.add(ui_style)
        
        await session.commit()
    
    await query.answer(f"✅ Довжина лінії: {length} символів", show_alert=True)

@ui_editor_router.callback_query(F.data.startswith("ui_preview_"))
async def ui_preview_role(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    role = query.data.replace("ui_preview_", "")
    menu_info = DEFAULT_MENUS.get(role, {"title": role.upper(), "icon": "📋"})
    
    async with async_session() as session:
        config_result = await session.execute(
            select(UIConfig).where(UIConfig.menu_key == role)
        )
        config = config_result.scalar_one_or_none()
        
        style_result = await session.execute(
            select(UIStyle).where(UIStyle.style_key == "global")
        )
        style = style_result.scalar_one_or_none()
    
    divider_char = style.divider_char if style else "═"
    divider_len = style.divider_length if style else 26
    divider = divider_char * divider_len
    
    title = config.title if config else menu_info["title"]
    desc = config.description if config else "<i>Опис за замовчуванням</i>"
    banner = config.banner_text if config and config.banner_text else ""
    
    preview = f"{divider}\n{menu_info['icon']} <b>{title}</b>\n{divider}\n"
    if banner:
        preview += f"\n{banner}\n"
    preview += f"\n{desc}"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ НАЗАД", callback_data=f"ui_role_{role}")]
    ])
    
    await query.message.edit_text(preview, reply_markup=kb, parse_mode="HTML")
    await query.answer()

@ui_editor_router.callback_query(F.data == "ui_preview")
async def ui_preview_all(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    async with async_session() as session:
        style_result = await session.execute(
            select(UIStyle).where(UIStyle.style_key == "global")
        )
        style = style_result.scalar_one_or_none()
    
    divider_char = style.divider_char if style else "═"
    divider_len = style.divider_length if style else 26
    divider = divider_char * divider_len
    
    preview = f"""{divider}
🛡️ <b>ПРЕВ'Ю СТИЛЮ</b>
{divider}
<i>Поточні налаштування</i>

<b>📋 ПРИКЛАД МЕНЮ:</b>
├ Елемент 1
├ Елемент 2
└ Елемент 3

<b>💡 СТАТИСТИКА:</b>
├ Значення: <code>123</code>
└ Статус: <b>OK</b>"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ НАЗАД", callback_data="ui_editor")]
    ])
    
    await query.message.edit_text(preview, reply_markup=kb, parse_mode="HTML")
    await query.answer()

@ui_editor_router.callback_query(F.data == "ui_edit_buttons")
async def ui_edit_buttons(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 GUEST кнопки", callback_data="ui_buttons_guest")],
        [InlineKeyboardButton(text="🌟 MANAGER кнопки", callback_data="ui_buttons_manager")],
        [InlineKeyboardButton(text="👑 LEADER кнопки", callback_data="ui_buttons_leader")],
        [InlineKeyboardButton(text="🛡️ ADMIN кнопки", callback_data="ui_buttons_admin")],
        [InlineKeyboardButton(text="◀️ НАЗАД", callback_data="ui_editor")]
    ])
    
    text = """══════════════════════════
🔘 <b>РЕДАКТОР КНОПОК</b>
══════════════════════════
<i>Управління кнопками меню</i>

<b>📋 МОЖЛИВОСТІ:</b>
├ Додавання нових кнопок
├ Видалення існуючих
├ Зміна порядку
└ Редагування тексту

<b>💡</b> Оберіть меню:"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()

@ui_editor_router.callback_query(F.data.startswith("ui_buttons_"))
async def ui_buttons_menu(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    role = query.data.replace("ui_buttons_", "")
    
    async with async_session() as session:
        result = await session.execute(
            select(UIButton).where(UIButton.menu_key == role).order_by(UIButton.row_order, UIButton.col_order)
        )
        buttons = result.scalars().all()
    
    buttons_list = ""
    if buttons:
        for i, btn in enumerate(buttons, 1):
            status = "✅" if btn.is_active else "❌"
            buttons_list += f"├ {i}. {status} {btn.text}\n"
    else:
        buttons_list = "├ <i>Кастомних кнопок немає</i>\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Додати кнопку", callback_data=f"ui_btn_add_{role}")],
        [InlineKeyboardButton(text="🗑 Видалити кнопку", callback_data=f"ui_btn_del_{role}")],
        [InlineKeyboardButton(text="◀️ НАЗАД", callback_data="ui_edit_buttons")]
    ])
    
    text = f"""══════════════════════════
🔘 <b>КНОПКИ: {role.upper()}</b>
══════════════════════════

<b>📋 ПОТОЧНІ КНОПКИ:</b>
{buttons_list}└ <i>Системні кнопки не показані</i>

<b>💡</b> Оберіть дію:"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()

@ui_editor_router.callback_query(F.data.startswith("ui_btn_add_"))
async def ui_btn_add_start(query: CallbackQuery, state: FSMContext):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    role = query.data.replace("ui_btn_add_", "")
    await state.update_data(editing_role=role)
    await state.set_state(UIEditorStates.adding_button)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data=f"ui_buttons_{role}")]
    ])
    
    await query.message.edit_text(
        "══════════════════════════\n"
        "➕ <b>НОВА КНОПКА</b>\n"
        "══════════════════════════\n"
        "Введіть дані у форматі:\n"
        "<code>Текст кнопки | callback_data</code>\n\n"
        "<i>Приклад:</i>\n"
        "<code>🚀 Нова функція | new_feature</code>",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@ui_editor_router.message(UIEditorStates.adding_button)
async def ui_btn_add_process(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    data = await state.get_data()
    role = data.get("editing_role")
    
    parts = message.text.split("|")
    if len(parts) != 2:
        await message.answer("❌ Невірний формат. Використовуйте: Текст | callback")
        return
    
    btn_text = parts[0].strip()
    callback = parts[1].strip()
    
    async with async_session() as session:
        result = await session.execute(
            select(UIButton).where(UIButton.menu_key == role)
        )
        existing = result.scalars().all()
        row_order = len(existing)
        
        new_btn = UIButton(
            menu_key=role,
            text=btn_text,
            callback_data=callback,
            row_order=row_order,
            is_active=True
        )
        session.add(new_btn)
        await session.commit()
    
    await state.clear()
    await message.answer(
        f"✅ Кнопку додано до <b>{role.upper()}</b>:\n"
        f"<code>{btn_text}</code> → <code>{callback}</code>",
        parse_mode="HTML"
    )

@ui_editor_router.callback_query(F.data == "ui_edit_banners")
async def ui_edit_banners(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 GUEST банер", callback_data="ui_set_banner_guest")],
        [InlineKeyboardButton(text="🌟 MANAGER банер", callback_data="ui_set_banner_manager")],
        [InlineKeyboardButton(text="👑 LEADER банер", callback_data="ui_set_banner_leader")],
        [InlineKeyboardButton(text="🛡️ ADMIN банер", callback_data="ui_set_banner_admin")],
        [InlineKeyboardButton(text="◀️ НАЗАД", callback_data="ui_editor")]
    ])
    
    text = """══════════════════════════
🖼 <b>УПРАВЛІННЯ БАНЕРАМИ</b>
══════════════════════════
<i>Банери відображаються вгорі меню</i>

<b>📋 ПРИКЛАДИ БАНЕРІВ:</b>
├ 🔥 АКЦІЯ! -50% на тарифи!
├ ⚠️ Технічні роботи 10:00-12:00
└ 🎉 Новий функціонал доступний!

<b>💡</b> Оберіть меню:"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await query.answer()

async def get_dynamic_description(role: str) -> str:
    """Отримати динамічний опис меню з БД"""
    async with async_session() as session:
        config_result = await session.execute(
            select(UIConfig).where(UIConfig.menu_key == role)
        )
        config = config_result.scalar_one_or_none()
        
        style_result = await session.execute(
            select(UIStyle).where(UIStyle.style_key == "global")
        )
        style = style_result.scalar_one_or_none()
    
    if not config:
        return None
    
    divider_char = style.divider_char if style else "═"
    divider_len = style.divider_length if style else 26
    divider = divider_char * divider_len
    
    menu_info = DEFAULT_MENUS.get(role, {"icon": "📋"})
    
    text = f"{divider}\n{menu_info['icon']} <b>{config.title}</b>\n{divider}\n"
    if config.banner_text:
        text += f"\n{config.banner_text}\n"
    if config.description:
        text += f"\n{config.description}"
    
    return text
