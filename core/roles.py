from typing import List, Dict, Any
from functools import wraps
from aiogram.types import Message, CallbackQuery
from core.role_constants import UserRole, ROLE_HIERARCHY, ROLE_NAMES, ROLE_DESCRIPTIONS

__all__ = ['UserRole', 'ROLE_HIERARCHY', 'ROLE_NAMES', 'ROLE_DESCRIPTIONS', 'ROLE_PERMISSIONS', 
           'TARIFFS', 'has_permission', 'get_role_level', 'can_manage_role', 'get_tariff', 'check_role_access']

ROLE_PERMISSIONS = {
    UserRole.GUEST: [
        "view_tariffs",
        "submit_application",
        "view_help"
    ],
    UserRole.MANAGER: [
        "view_tariffs",
        "view_help",
        "view_campaigns",
        "create_campaign",
        "run_campaign",
        "view_bots",
        "manage_assigned_bots",
        "send_messages",
        "view_analytics",
        "basic_osint",
        "view_own_stats"
    ],
    UserRole.LEADER: [
        "view_tariffs",
        "view_help",
        "view_campaigns",
        "create_campaign",
        "run_campaign",
        "pause_campaign",
        "stop_campaign",
        "view_bots",
        "add_bots",
        "manage_bots",
        "send_messages",
        "view_analytics",
        "view_team",
        "add_manager",
        "remove_manager",
        "generate_license_key",
        "view_osint",
        "use_osint",
        "advanced_osint",
        "manage_project",
        "view_payments",
        "submit_ticket",
        "view_manager_activity",
        "pause_manager_campaign"
    ],
    UserRole.ADMIN: [
        "all",
        "view_all_projects",
        "manage_all_users",
        "approve_tickets",
        "reject_tickets",
        "generate_master_key",
        "view_audit_logs",
        "emergency_alert",
        "system_settings",
        "database_access",
        "stop_any_campaign"
    ]
}

TARIFFS = {
    "basic": {
        "name": "БАЗОВИЙ",
        "name_en": "BASIC",
        "max_bots": 100,
        "max_managers": 1,
        "features": ["Базовий OSINT", "До 100 ботів", "1 менеджер"],
        "price_uah": 4200,
        "price_display": "4 200 ₴/міс"
    },
    "standard": {
        "name": "СТАНДАРТ",
        "name_en": "STANDARD",
        "max_bots": 500,
        "max_managers": 5,
        "features": ["Масові операції", "Аналітика", "До 500 ботів", "5 менеджерів"],
        "price_uah": 12500,
        "price_display": "12 500 ₴/міс"
    },
    "premium": {
        "name": "ПРЕМІУМ",
        "name_en": "PREMIUM",
        "max_bots": 5000,
        "max_managers": 20,
        "features": ["Глибокий OSINT", "Анти-детект", "До 5000 ботів", "20 менеджерів"],
        "price_uah": 62500,
        "price_display": "62 500 ₴/міс"
    },
    "personal": {
        "name": "ПЕРСОНАЛЬНИЙ",
        "name_en": "PERSONAL",
        "max_bots": -1,
        "max_managers": -1,
        "features": ["Безлімітні операції", "Кастомні модулі", "Пріоритетна підтримка"],
        "price_uah": 100000,
        "price_display": "Від 100 000 ₴/міс"
    }
}

def has_permission(role: str, permission: str) -> bool:
    if role == UserRole.ADMIN:
        return True
    role_perms = ROLE_PERMISSIONS.get(role, [])
    return permission in role_perms or "all" in role_perms

def get_role_level(role: str) -> int:
    return ROLE_HIERARCHY.get(role, 0)

def can_manage_role(manager_role: str, target_role: str) -> bool:
    return get_role_level(manager_role) > get_role_level(target_role)

def get_tariff(tariff_id: str) -> Dict[str, Any]:
    return TARIFFS.get(tariff_id, TARIFFS["basic"])

def check_role_access(required_roles: List[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            event = args[0] if args else None
            if isinstance(event, (Message, CallbackQuery)):
                user_role = kwargs.get('user_role', UserRole.GUEST)
                if user_role in required_roles or user_role == UserRole.ADMIN:
                    return await func(*args, **kwargs)
                else:
                    if isinstance(event, Message):
                        await event.answer("❌ У вас немає доступу до цієї функції")
                    else:
                        await event.answer("❌ Немає доступу", show_alert=True)
                    return None
            return await func(*args, **kwargs)
        return wrapper
    return decorator
