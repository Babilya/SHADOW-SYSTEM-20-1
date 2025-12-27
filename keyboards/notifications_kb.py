from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict

def notifications_menu_kb(is_admin: bool = False) -> InlineKeyboardMarkup:
    """Головне меню сповіщень"""
    buttons = [
        [InlineKeyboardButton(text="📬 Мої сповіщення", callback_data="notifications_my")],
        [InlineKeyboardButton(text="🔔 Непрочитані", callback_data="notifications_unread")]
    ]
    
    if is_admin:
        buttons.extend([
            [InlineKeyboardButton(text="📢 Створити сповіщення", callback_data="notification_create")],
            [InlineKeyboardButton(text="📋 Історія відправок", callback_data="notifications_history")]
        ])
    
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def notification_create_type_kb() -> InlineKeyboardMarkup:
    """Вибір типу сповіщення"""
    types = [
        ("ℹ️ Інформація", "info"),
        ("⚠️ Попередження", "warning"),
        ("📢 Оголошення", "announcement"),
        ("🔄 Оновлення", "update"),
        ("🔧 Техроботи", "maintenance")
    ]
    
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"notif_type:{ntype}")]
        for name, ntype in types
    ]
    buttons.append([InlineKeyboardButton(text="❌ Скасувати", callback_data="notifications_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def notification_target_kb(notif_type: str) -> InlineKeyboardMarkup:
    """Вибір цільової аудиторії"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Всі користувачі", callback_data=f"notif_target:{notif_type}:all")],
        [InlineKeyboardButton(text="👔 За роллю", callback_data=f"notif_target:{notif_type}:role")],
        [InlineKeyboardButton(text="👥👔 Декілька ролей", callback_data=f"notif_target:{notif_type}:multi_role")],
        [InlineKeyboardButton(text="👤 Персональні", callback_data=f"notif_target:{notif_type}:personal")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="notification_create")]
    ])

def notification_role_kb(notif_type: str) -> InlineKeyboardMarkup:
    """Вибір ролі"""
    roles = [
        ("👤 Гості", "guest"),
        ("👔 Менеджери", "manager"),
        ("👑 Лідери", "leader"),
        ("🔑 Адміни", "admin")
    ]
    
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"notif_role:{notif_type}:{role}")]
        for name, role in roles
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"notif_target:{notif_type}:role")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def notification_multi_role_kb(notif_type: str, selected: List[str] = None) -> InlineKeyboardMarkup:
    """Вибір декількох ролей"""
    selected = selected or []
    
    roles = [
        ("👤 Гості", "guest"),
        ("👔 Менеджери", "manager"),
        ("👑 Лідери", "leader"),
        ("🔑 Адміни", "admin")
    ]
    
    buttons = []
    for name, role in roles:
        check = "✅ " if role in selected else ""
        buttons.append([
            InlineKeyboardButton(
                text=f"{check}{name}",
                callback_data=f"notif_multi_toggle:{notif_type}:{role}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text="✓ Готово", callback_data=f"notif_multi_done:{notif_type}")
    ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"notif_target:{notif_type}:multi_role")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def notification_priority_kb(notif_type: str, target: str) -> InlineKeyboardMarkup:
    """Вибір пріоритету"""
    priorities = [
        ("🟢 Низький", "low"),
        ("🟡 Звичайний", "normal"),
        ("🟠 Високий", "high"),
        ("🔴 Терміновий", "urgent")
    ]
    
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"notif_pri:{notif_type}:{target}:{pri}")]
        for name, pri in priorities
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"notif_target:{notif_type}:{target}")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def notifications_list_kb(notifications: List[Dict]) -> InlineKeyboardMarkup:
    """Список сповіщень"""
    buttons = []
    
    for n in notifications[:10]:
        icon = n.get('type_icon', 'ℹ️')
        read_mark = "" if n.get('is_read') else "🔵 "
        buttons.append([
            InlineKeyboardButton(
                text=f"{read_mark}{icon} {n['title'][:30]}...",
                callback_data=f"notif_view:{n['id']}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text="✓ Прочитати всі", callback_data="notifications_read_all")
    ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="notifications_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def notification_view_kb(notif_id: int, is_admin: bool = False) -> InlineKeyboardMarkup:
    """Перегляд сповіщення"""
    buttons = []
    
    if is_admin:
        buttons.append([
            InlineKeyboardButton(text="🗑 Видалити", callback_data=f"notif_delete:{notif_id}")
        ])
    
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="notifications_my")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def bans_menu_kb() -> InlineKeyboardMarkup:
    """Меню банів"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚫 Забанити користувача", callback_data="ban_user")],
        [InlineKeyboardButton(text="📋 Активні бани", callback_data="bans_active")],
        [InlineKeyboardButton(text="📜 Історія банів", callback_data="bans_history")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")]
    ])

def ban_type_kb() -> InlineKeyboardMarkup:
    """Вибір типу бану"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏱ Тимчасовий", callback_data="ban_type:temporary")],
        [InlineKeyboardButton(text="🔒 Постійний", callback_data="ban_type:permanent")],
        [InlineKeyboardButton(text="⚠️ Попередження", callback_data="ban_type:warning")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="bans_menu")]
    ])

def ban_duration_kb(ban_type: str) -> InlineKeyboardMarkup:
    """Вибір тривалості бану"""
    durations = [
        ("1 година", 1), ("6 годин", 6), ("12 годин", 12),
        ("1 день", 24), ("3 дні", 72), ("7 днів", 168),
        ("30 днів", 720)
    ]
    
    buttons = []
    row = []
    for name, hours in durations:
        row.append(InlineKeyboardButton(
            text=name,
            callback_data=f"ban_dur:{ban_type}:{hours}"
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="ban_user")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def bans_list_kb(bans: List[Dict]) -> InlineKeyboardMarkup:
    """Список банів"""
    buttons = []
    
    for b in bans[:10]:
        buttons.append([
            InlineKeyboardButton(
                text=f"🚫 {b['user_id']} - {b['ban_type']}",
                callback_data=f"ban_view:{b['id']}"
            )
        ])
    
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="bans_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def ban_view_kb(ban_id: int, user_id: str) -> InlineKeyboardMarkup:
    """Перегляд бану"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Розбанити", callback_data=f"unban:{user_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="bans_active")]
    ])

def project_stats_kb(project_id: int) -> InlineKeyboardMarkup:
    """Статистика проекту"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📅 7 днів", callback_data=f"stats_period:{project_id}:7"),
            InlineKeyboardButton(text="📅 30 днів", callback_data=f"stats_period:{project_id}:30")
        ],
        [InlineKeyboardButton(text="📊 Детальний звіт", callback_data=f"stats_detail:{project_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="projects_list")]
    ])
