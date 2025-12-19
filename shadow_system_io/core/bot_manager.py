import logging

logger = logging.getLogger(__name__)

class BotManager:
    def __init__(self):
        self.bots = {}
        logger.info("🤖 BotManager initialized")
    
    async def add_bot(self, bot_id: str, session_string: str):
        self.bots[bot_id] = {"session": session_string, "status": "active"}
        logger.info(f"✅ Bot {bot_id} added")
    
    async def get_bot(self, bot_id: str):
        return self.bots.get(bot_id)

bot_manager = BotManager()
