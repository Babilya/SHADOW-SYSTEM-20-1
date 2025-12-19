import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from config.database import Database
from database.models import init_db
from core.bot_manager import bot_manager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("system.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("🚀 Starting SHADOW SYSTEM iO...")
    logger.info(f"📝 API_ID: {'✓' if settings.API_ID else '✗'}")
    logger.info(f"📝 BOT_TOKEN: {'✓' if settings.BOT_TOKEN else '✗'}")
    
    try:
        await Database.get_pool()
        try:
            await Database.get_redis()
            logger.info("✅ Redis connected")
        except:
            logger.warning("⚠️ Redis not available (optional)")
        
        await init_db()
        logger.info("✅ Database connected and initialized")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        logger.info("⚠️ Starting in offline mode...")
    
    logger.info("🔥 System is ready!")
    logger.info("📋 Waiting for commands...")
    
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down...")
        await Database.close()

if __name__ == "__main__":
    asyncio.run(main())
