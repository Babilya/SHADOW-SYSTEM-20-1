"""Database repositories for Shadow System V2.0"""
from .base import BaseRepository
from .user_repository import UserRepository
from .proxy_repository import ProxyRepository
from .bot_session_repository import BotSessionRepository
from .campaign_repository import CampaignRepository
from .osint_data_repository import OSINTDataRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "ProxyRepository",
    "BotSessionRepository",
    "CampaignRepository",
    "OSINTDataRepository",
]
