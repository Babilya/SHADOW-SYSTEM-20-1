import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "7787256575").split(",") if x.strip()]
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///shadow_security.db")
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL", "sqlite+aiosqlite:///shadow_security.db")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

TARIFFS = {
    "free": {"name": "Free", "price": 0, "bots": 5},
    "standard": {"name": "Standard", "price": 300, "bots": 50},
    "premium": {"name": "Premium", "price": 600, "bots": 100},
    "elite": {"name": "Elite", "price": 1200, "bots": 9999}
}

PAYMENT_METHODS = {
    "mono": {"emoji": "💳", "desc": "Monobank", "account": "5375 4100 1234 5678"},
    "usdt": {"emoji": "🪙", "desc": "USDT TRC-20", "account": "TYj8uVx5B9d7C6e5F4g3H2i1J0k9L8m7"}
}
