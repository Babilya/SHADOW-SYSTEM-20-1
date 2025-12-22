from .user import user_router
from .admin import admin_router
from .payments import payments_router

__all__ = ["user_router", "admin_router", "payments_router"]
