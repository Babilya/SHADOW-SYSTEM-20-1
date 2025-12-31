"""Moderation handlers - notifications, support, tickets, users"""
from .notifications_handler import router as notifications_router
from .support_handler import router as support_router
from .tickets import tickets_router
from .admin_notifications import router as admin_notifications_router
from .users_handler import users_router

__all__ = [
    "notifications_router",
    "support_router",
    "tickets_router",
    "admin_notifications_router",
    "users_router",
]
