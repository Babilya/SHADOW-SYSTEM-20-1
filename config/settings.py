import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "6838247512"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///shadow_system.db")

TARIFFS = {
    "baseus": {"name": "Baseus", "emoji": "🔹", "bots": 5, "managers": 1, "osint": False, "prices": {2: 2800, 14: 5900, 30: 8400}},
    "standard": {"name": "Standard", "emoji": "🔶", "bots": 50, "managers": 5, "osint": True, "prices": {2: 2800, 14: 5900, 30: 8400}},
    "premium": {"name": "Premium", "emoji": "👑", "bots": 100, "managers": 999, "osint": True, "prices": {2: 5900, 14: 11800, 30: 16800}},
    "person": {"name": "Person", "emoji": "💎", "bots": 999, "managers": 999, "osint": True, "prices": {"custom": True}}
}

PAYMENT_METHODS = {
    "mono": {"emoji": "💳", "desc": "Monobank", "account": "5375 4100 1234 5678"},
    "usdt": {"emoji": "🪙", "desc": "USDT TRC-20", "account": "TYj8uVx5B9d7C6e5F4g3H2i1J0k9L8m7"}
}

MANAGER_ROLES = {
    "campaign": {"name": "Менеджер розсилок", "perms": ["create_campaign"]},
    "osint": {"name": "OSINT-аналітик", "perms": ["osint_scan"]},
    "analytics": {"name": "Аналітик", "perms": ["view_analytics"]},
    "admin": {"name": "Адміністратор проекту", "perms": ["all"]}
}
