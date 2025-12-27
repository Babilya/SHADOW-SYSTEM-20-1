from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict

def support_menu_kb(is_admin: bool = False) -> InlineKeyboardMarkup:
    """Головне меню підтримки"""
    buttons = [
        [InlineKeyboardButton(text="📩 Створити тікет", callback_data="ticket_create")],
        [InlineKeyboardButton(text="📋 Мої тікети", callback_data="tickets_my")]
    ]
    
    if is_admin:
        buttons.extend([
            [InlineKeyboardButton(text="📥 Всі тікети", callback_data="tickets_all")],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="tickets_stats")]
        ])
    
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def ticket_category_kb() -> InlineKeyboardMarkup:
    """Вибір категорії тікета"""
    categories = [
        ("🔧 Технічна підтримка", "technical"),
        ("💳 Питання оплати", "billing"),
        ("👤 Акаунт та доступ", "account"),
        ("💡 Запит функції", "feature"),
        ("🐛 Повідомити про баг", "bug"),
        ("❓ Загальне питання", "general")
    ]
    
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"ticket_cat:{cat}")]
        for name, cat in categories
    ]
    buttons.append([InlineKeyboardButton(text="❌ Скасувати", callback_data="support_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def ticket_priority_kb(category: str) -> InlineKeyboardMarkup:
    """Вибір пріоритету"""
    priorities = [
        ("🟢 Низький", "low"),
        ("🟡 Звичайний", "normal"),
        ("🟠 Високий", "high"),
        ("🔴 Терміновий", "urgent")
    ]
    
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"ticket_pri:{category}:{pri}")]
        for name, pri in priorities
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="ticket_create")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def tickets_list_kb(tickets: List[Dict], is_admin: bool = False) -> InlineKeyboardMarkup:
    """Список тікетів"""
    buttons = []
    
    for t in tickets[:10]:
        icon = t.get('status_icon', '📂')
        buttons.append([
            InlineKeyboardButton(
                text=f"{icon} {t['ticket_code']}: {t['subject'][:20]}...",
                callback_data=f"ticket_view:{t['id']}"
            )
        ])
    
    if is_admin:
        buttons.append([
            InlineKeyboardButton(text="📂 Відкриті", callback_data="tickets_filter:open"),
            InlineKeyboardButton(text="🔄 В роботі", callback_data="tickets_filter:in_progress")
        ])
    
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="support_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def ticket_view_kb(ticket_id: int, status: str, is_admin: bool = False) -> InlineKeyboardMarkup:
    """Перегляд тікета"""
    buttons = []
    
    if status not in ['resolved', 'closed']:
        buttons.append([
            InlineKeyboardButton(text="💬 Відповісти", callback_data=f"ticket_reply:{ticket_id}")
        ])
    
    if is_admin:
        if status == 'open':
            buttons.append([
                InlineKeyboardButton(text="📌 Взяти в роботу", callback_data=f"ticket_assign:{ticket_id}")
            ])
        
        buttons.append([
            InlineKeyboardButton(text="🔄 Змінити статус", callback_data=f"ticket_status:{ticket_id}")
        ])
    
    if status == 'resolved':
        buttons.append([
            InlineKeyboardButton(text="⭐ Оцінити", callback_data=f"ticket_rate:{ticket_id}")
        ])
    
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="tickets_my")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def ticket_status_kb(ticket_id: int) -> InlineKeyboardMarkup:
    """Зміна статусу тікета"""
    statuses = [
        ("📂 Відкритий", "open"),
        ("🔄 В роботі", "in_progress"),
        ("⏳ Очікує відповіді", "waiting"),
        ("✅ Вирішено", "resolved"),
        ("📁 Закритий", "closed")
    ]
    
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"ticket_set_status:{ticket_id}:{status}")]
        for name, status in statuses
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"ticket_view:{ticket_id}")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def ticket_rating_kb(ticket_id: int) -> InlineKeyboardMarkup:
    """Оцінка тікета"""
    buttons = [[
        InlineKeyboardButton(text="⭐", callback_data=f"ticket_rating:{ticket_id}:1"),
        InlineKeyboardButton(text="⭐⭐", callback_data=f"ticket_rating:{ticket_id}:2"),
        InlineKeyboardButton(text="⭐⭐⭐", callback_data=f"ticket_rating:{ticket_id}:3"),
        InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data=f"ticket_rating:{ticket_id}:4"),
        InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data=f"ticket_rating:{ticket_id}:5")
    ]]
    buttons.append([InlineKeyboardButton(text="🔙 Пропустити", callback_data=f"ticket_view:{ticket_id}")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
