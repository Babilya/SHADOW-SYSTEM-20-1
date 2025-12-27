from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict

def templates_menu_kb() -> InlineKeyboardMarkup:
    """Головне меню шаблонів"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Мої шаблони", callback_data="templates_list")],
        [InlineKeyboardButton(text="➕ Створити шаблон", callback_data="template_create")],
        [InlineKeyboardButton(text="📁 За категоріями", callback_data="templates_categories")],
        [InlineKeyboardButton(text="🌐 Публічні шаблони", callback_data="templates_public")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="mailing_main")]
    ])

def templates_list_kb(templates: List[Dict]) -> InlineKeyboardMarkup:
    """Список шаблонів"""
    buttons = []
    
    for t in templates[:10]:
        icon = "📎" if t.get('has_media') else "📄"
        buttons.append([
            InlineKeyboardButton(
                text=f"{icon} {t['name']}",
                callback_data=f"template_view:{t['id']}"
            )
        ])
    
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="templates_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def template_categories_kb() -> InlineKeyboardMarkup:
    """Категорії шаблонів"""
    categories = [
        ("👋 Привітальні", "welcome"),
        ("🎁 Промо", "promo"),
        ("📰 Новини", "news"),
        ("⏰ Нагадування", "reminder"),
        ("🔔 Сповіщення", "alert"),
        ("📋 Загальні", "general")
    ]
    
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"templates_cat:{cat}")]
        for name, cat in categories
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="templates_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def template_view_kb(template_id: int, is_owner: bool = True) -> InlineKeyboardMarkup:
    """Перегляд шаблону"""
    buttons = []
    
    if is_owner:
        buttons.append([
            InlineKeyboardButton(text="✏️ Редагувати", callback_data=f"template_edit:{template_id}"),
            InlineKeyboardButton(text="🗑 Видалити", callback_data=f"template_delete:{template_id}")
        ])
    
    buttons.append([
        InlineKeyboardButton(text="🚀 Використати", callback_data=f"template_use:{template_id}")
    ])
    buttons.append([
        InlineKeyboardButton(text="⏱ Запланувати", callback_data=f"template_schedule:{template_id}")
    ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="templates_list")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def template_create_category_kb() -> InlineKeyboardMarkup:
    """Вибір категорії при створенні"""
    categories = [
        ("👋 Привітальні", "welcome"),
        ("🎁 Промо", "promo"),
        ("📰 Новини", "news"),
        ("⏰ Нагадування", "reminder"),
        ("🔔 Сповіщення", "alert"),
        ("📋 Загальні", "general")
    ]
    
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"template_new_cat:{cat}")]
        for name, cat in categories
    ]
    buttons.append([InlineKeyboardButton(text="❌ Скасувати", callback_data="templates_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def schedule_type_kb(template_id: int) -> InlineKeyboardMarkup:
    """Вибір типу розкладу"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔂 Одноразово", callback_data=f"sched_once:{template_id}")],
        [InlineKeyboardButton(text="⏱ За інтервалом", callback_data=f"sched_interval:{template_id}")],
        [InlineKeyboardButton(text="📅 Щодня", callback_data=f"sched_daily:{template_id}")],
        [InlineKeyboardButton(text="📆 Щотижня", callback_data=f"sched_weekly:{template_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"template_view:{template_id}")]
    ])

def schedule_interval_kb(template_id: int) -> InlineKeyboardMarkup:
    """Вибір інтервалу"""
    intervals = [
        ("15 хв", 15), ("30 хв", 30), ("1 год", 60),
        ("2 год", 120), ("4 год", 240), ("6 год", 360),
        ("12 год", 720), ("24 год", 1440)
    ]
    
    buttons = []
    row = []
    for name, minutes in intervals:
        row.append(InlineKeyboardButton(
            text=name,
            callback_data=f"sched_int_set:{template_id}:{minutes}"
        ))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"template_schedule:{template_id}")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def schedule_target_kb(template_id: int) -> InlineKeyboardMarkup:
    """Вибір цільової аудиторії"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Всі користувачі", callback_data=f"sched_target:{template_id}:all")],
        [InlineKeyboardButton(text="👔 Менеджери", callback_data=f"sched_target:{template_id}:manager")],
        [InlineKeyboardButton(text="👑 Лідери", callback_data=f"sched_target:{template_id}:leader")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"template_schedule:{template_id}")]
    ])

def scheduled_list_kb(mailings: List[Dict]) -> InlineKeyboardMarkup:
    """Список запланованих розсилок"""
    buttons = []
    
    status_icons = {'active': '▶️', 'paused': '⏸', 'completed': '✅'}
    
    for m in mailings[:10]:
        icon = status_icons.get(m['status'], '📨')
        buttons.append([
            InlineKeyboardButton(
                text=f"{icon} {m['name']}",
                callback_data=f"sched_view:{m['id']}"
            )
        ])
    
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="mailing_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def scheduled_view_kb(mailing_id: int, status: str) -> InlineKeyboardMarkup:
    """Перегляд запланованої розсилки"""
    buttons = []
    
    if status == 'active':
        buttons.append([InlineKeyboardButton(text="⏸ Пауза", callback_data=f"sched_pause:{mailing_id}")])
    elif status == 'paused':
        buttons.append([InlineKeyboardButton(text="▶️ Відновити", callback_data=f"sched_resume:{mailing_id}")])
    
    buttons.append([
        InlineKeyboardButton(text="🗑 Видалити", callback_data=f"sched_delete:{mailing_id}")
    ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="scheduled_list")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
