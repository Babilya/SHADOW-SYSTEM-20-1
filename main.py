import asyncio, logging
from aiogram import Bot, Dispatcher
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Import routers from handlers
from handlers.start import router as start_router
from handlers.auth_system import router as auth_router
from handlers.subscriptions import router as subs_router
from handlers.tickets import router as tickets_router
from handlers.admin import router as admin_router
from handlers.osint import router as osint_router
from handlers.botnet import router as botnet_router
from handlers.campaigns_handler import router as campaigns_router
from handlers.team import router as team_router
from handlers.analytics import router as analytics_router
from handlers.configurator import router as config_router
from handlers.help import router as help_router
from handlers.funnels import funnels_router
from handlers.warming import warming_router
from handlers.mailing import mailing_router
from handlers.geoscanner import geo_router
from handlers.proxy import proxy_router
from handlers.advanced_features import advanced_router
from handlers.osint_handler import osint_router as osint_handler_router
from handlers.texting import texting_router
from handlers.scheduler import scheduler_router
from handlers.templates_handler import templates_router
from handlers.support_handler import support_router
from handlers.notifications_handler import notifications_router
from handlers.missing_handlers import missing_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables!")
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    from middlewares.role_middleware import RoleMiddleware
    dp.message.middleware(RoleMiddleware())
    dp.callback_query.middleware(RoleMiddleware())

    # Register routers
    dp.include_router(start_router)
    dp.include_router(auth_router)
    dp.include_router(subs_router)
    dp.include_router(tickets_router)
    dp.include_router(admin_router)
    dp.include_router(osint_router)
    dp.include_router(botnet_router)
    dp.include_router(campaigns_router)
    dp.include_router(team_router)
    dp.include_router(analytics_router)
    dp.include_router(config_router)
    dp.include_router(help_router)
    dp.include_router(funnels_router)
    dp.include_router(warming_router)
    dp.include_router(mailing_router)
    dp.include_router(geo_router)
    dp.include_router(proxy_router)
    dp.include_router(advanced_router)
    dp.include_router(osint_handler_router)
    dp.include_router(texting_router)
    dp.include_router(scheduler_router)
    dp.include_router(templates_router)
    dp.include_router(support_router)
    dp.include_router(notifications_router)
    dp.include_router(missing_router)

    from utils.db import init_db
    await init_db()

    logger.info("🚀 Бот запущено")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот зупинений")
