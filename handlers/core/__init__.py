"""Core handlers - authentication, start, help, user, security"""
from .start import router as start_router
from .user import user_router
from .help import router as help_router
from .security import security_router
from .auth_system import router as auth_router

__all__ = [
    "start_router",
    "user_router",
    "help_router",
    "security_router",
    "auth_router",
]
