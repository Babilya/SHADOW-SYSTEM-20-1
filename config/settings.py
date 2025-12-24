from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///shadow_system.db")

SUPER_ADMIN_IDS = [ADMIN_ID]

TARIFFS = {
    "baseus": {
        "name": "Baseus",
        "emoji": "🔹",
        "description": "Тест/Новачок",
        "bots_limit": 5,
        "managers_limit": 1,
        "osint": False,
        "prices": {2: 2800, 14: 5900, 30: 8400}
    },
    "standard": {
        "name": "Standard",
        "emoji": "🔶",
        "description": "Агенція/Арбітраж",
        "bots_limit": 50,
        "managers_limit": 5,
        "osint": True,
        "prices": {2: 2800, 14: 5900, 30: 8400}
    },
    "premium": {
        "name": "Premium",
        "emoji": "👑",
        "description": "PRO/Швидкість",
        "bots_limit": 100,
        "managers_limit": 999,
        "osint": True,
        "prices": {2: 5900, 14: 11800, 30: 16800}
    },
    "person": {
        "name": "Person",
        "emoji": "💎",
        "description": "Enterprise",
        "bots_limit": 999,
        "managers_limit": 999,
        "osint": True,
        "prices": {"custom": "узгоджується"}
    }
}

PAYMENT_METHODS = {
    "monobank": "5375 4100 1234 5678",
    "usdt_trc20": "TYj8uVx5B9d7C6e5F4g3H2i1J0k9L8m7"
}

MANAGER_ROLES = {
    "campaign_manager": "Менеджер розсилок",
    "osint_analyst": "OSINT-аналітик",
    "analytics": "Аналітик",
    "admin": "Адміністратор проекту"
}

SESSION_TIMEOUT = 3600
RATE_LIMIT = 30
RATE_LIMIT_WINDOW = 60

SUPPORT_HOURS = "10:00-22:00"
TIMEZONE = "Europe/Kyiv"
