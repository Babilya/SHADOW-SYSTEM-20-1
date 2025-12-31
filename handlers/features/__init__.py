"""Feature handlers - campaigns, botnet, osint, mailing, etc."""
from .botnet import botnet_router
from .funnels import funnels_router
from .analytics import router as analytics_router
from .warming import warming_router
from .mailing import mailing_router
from .osint import osint_router
from .subscriptions import router as subscriptions_router
from .team import router as team_router
from .advanced_features import advanced_router
from .advanced_tools import advanced_tools_router as tools_router
from .forensics import forensics_router
from .bots_handler import bots_router
from .campaigns_handler import router as campaigns_router
from .osint_handler import osint_router as osint_handler_router
from .proxy import proxy_router
from .referral import referral_router
from .profile import profile_router

__all__ = [
    "botnet_router",
    "funnels_router",
    "analytics_router",
    "warming_router",
    "mailing_router",
    "osint_router",
    "subscriptions_router",
    "team_router",
    "advanced_router",
    "tools_router",
    "forensics_router",
    "bots_router",
    "campaigns_router",
    "osint_handler_router",
    "proxy_router",
    "referral_router",
    "profile_router",
]
