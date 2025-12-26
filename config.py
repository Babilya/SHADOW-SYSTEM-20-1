import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Admin IDs (comma-separated list in env)
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "6838247512").split(",") if x.strip()]

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///shadow_security.db")
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL", "sqlite+aiosqlite:///shadow_security.db")

# Optional: AI and External API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

# Pricing and Tariffs
TARIFFS = {
    "free": {"name": "Free", "price": 0, "bots": 5},
    "standard": {"name": "Standard", "price": 300, "bots": 50},
    "premium": {"name": "Premium", "price": 600, "bots": 100},
    "elite": {"name": "Elite", "price": 1200, "bots": 9999}
}
