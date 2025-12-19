import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings:
    API_ID = int(os.getenv("API_ID", "0"))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
    POSTGRES_DB = os.getenv("POSTGRES_DB", "shadow_system")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
    
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    SECRET_KEY = os.getenv("SECRET_KEY", "shadow-secret-key-2024")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "").encode() or b"default-encryption-key-32bytes!"[:32]
    
    MESSAGES_PER_DAY = int(os.getenv("MESSAGES_PER_DAY", 100))
    PARALLEL_TASKS = int(os.getenv("PARALLEL_TASKS", 5))
    
    SESSIONS_DIR = BASE_DIR / "sessions"
    MEDIA_DIR = BASE_DIR / "media"
    LOGS_DIR = BASE_DIR / "logs"
    
    WEB_APP_URL = os.getenv("WEB_APP_URL", "https://your-webapp.vercel.app")
    
    def __init__(self):
        self.SESSIONS_DIR.mkdir(exist_ok=True)
        self.MEDIA_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)

settings = Settings()
