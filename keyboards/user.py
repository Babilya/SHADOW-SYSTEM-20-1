"""
User keyboards - wrapper for backward compatibility
All menus are consolidated in role_menus.py
"""
from keyboards.role_menus import (
    main_menu,
    main_menu_description,
    guest_menu,
    guest_description,
    manager_menu,
    manager_description,
    leader_menu,
    leader_description,
    admin_menu,
    admin_description,
    back_button,
    DIVIDER
)

__all__ = [
    "main_menu",
    "main_menu_description",
    "guest_menu",
    "guest_description",
    "manager_menu",
    "manager_description",
    "leader_menu",
    "leader_description",
    "admin_menu",
    "admin_description",
    "back_button",
    "DIVIDER"
]
