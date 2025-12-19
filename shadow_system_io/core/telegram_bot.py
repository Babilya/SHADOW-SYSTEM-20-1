import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config.settings import settings
from database.crud import (
    create_user, get_user, get_project_bots, create_audit_log
)
from core.auth import rbac

logger = logging.getLogger(__name__)

class TelegramBotManager:
    """Central Telegram Bot Manager"""
    
    def __init__(self):
        self.app = None
        self.bot_token = settings.BOT_TOKEN
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "User"
        
        # Create or update user
        await create_user(user_id, username, role="manager")
        await create_audit_log(user_id, "login", "user", str(user_id))
        
        # Get user role
        user = await get_user(user_id)
        role = user.get("role") if user else "manager"
        
        welcome_text = f"""
🎯 **SHADOW SYSTEM iO 2.0**
Привіт, {username}! 👋

Ваша роль: **{role.upper()}**

Виберіть дію:
"""
        
        keyboard = self._get_main_menu_keyboard(role)
        await update.message.reply_text(welcome_text, reply_markup=keyboard, parse_mode="Markdown")
        
        logger.info(f"✅ User {user_id} ({username}) logged in as {role}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📚 **Доступні команди:**

/start - Головне меню
/help - Ця довідка
/projects - Мої проекти
/bots - Мої боти
/campaigns - Мої кампанії
/stats - Статистика
/settings - Налаштування

**Для адміна:**
/create_project - Створити проект
/add_manager - Додати менеджера

**Для суперадміна:**
/users - Управління користувачами
/system_settings - Системні налаштування
"""
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def projects_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's projects"""
        user_id = update.effective_user.id
        
        projects = await rbac.get_user_projects(user_id)
        
        if not projects:
            await update.message.reply_text("❌ У вас немає проектів.")
            return
        
        text = "📋 **Ваші проекти:**\n\n"
        for p in projects:
            text += f"• {p.get('name')} (ID: {p.get('project_id')})\n"
        
        await update.message.reply_text(text, parse_mode="Markdown")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button clicks"""
        query = update.callback_query
        user_id = query.from_user.id
        
        await query.answer()
        
        if query.data == "main_menu":
            user = await get_user(user_id)
            role = user.get("role") if user else "manager"
            keyboard = self._get_main_menu_keyboard(role)
            await query.edit_message_text("🎯 **Головне меню**", 
                                         reply_markup=keyboard, parse_mode="Markdown")
        
        elif query.data == "view_projects":
            await self.projects_command(update, context)
        
        elif query.data == "view_bots":
            await self._show_bots(update, context)
        
        elif query.data == "view_campaigns":
            await self._show_campaigns(update, context)
        
        elif query.data == "view_stats":
            await self._show_stats(update, context)
    
    async def _show_bots(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's bots"""
        user_id = update.effective_user.id
        user = await get_user(user_id)
        project_id = user.get("project_id") if user else None
        
        if not project_id:
            await update.message.reply_text("❌ Проект не призначений.")
            return
        
        bots = await get_project_bots(project_id)
        
        if not bots:
            await update.message.reply_text("❌ У проекту немає ботів.")
            return
        
        text = "🤖 **Боти проекту:**\n\n"
        for bot in bots:
            text += f"• {bot.get('bot_id')} - {bot.get('status')}\n"
        
        await update.message.reply_text(text, parse_mode="Markdown")
    
    async def _show_campaigns(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show campaigns"""
        await update.message.reply_text("📊 Функція кампаній в розробці...")
    
    async def _show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show statistics"""
        await update.message.reply_text("📈 Статистика в розробці...")
    
    def _get_main_menu_keyboard(self, role: str) -> InlineKeyboardMarkup:
        """Get main menu keyboard based on role"""
        buttons = [
            [InlineKeyboardButton("📋 Проекти", callback_data="view_projects")],
            [InlineKeyboardButton("🤖 Боти", callback_data="view_bots")],
            [InlineKeyboardButton("📊 Кампанії", callback_data="view_campaigns")],
            [InlineKeyboardButton("📈 Статистика", callback_data="view_stats")],
        ]
        
        if role in ["admin", "superadmin"]:
            buttons.append([InlineKeyboardButton("⚙️ Налаштування", callback_data="settings")])
        
        if role == "superadmin":
            buttons.append([InlineKeyboardButton("👥 Користувачі", callback_data="users")])
        
        return InlineKeyboardMarkup(buttons)
    
    async def setup(self):
        """Setup bot handlers"""
        self.app = Application.builder().token(self.bot_token).build()
        
        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("projects", self.projects_command))
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        
        logger.info("✅ Telegram bot handlers configured")
    
    async def run(self):
        """Run bot"""
        if not self.app:
            await self.setup()
        
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        logger.info("🚀 Telegram bot polling started")
    
    async def stop(self):
        """Stop bot"""
        if self.app:
            await self.app.stop()
            logger.info("🛑 Telegram bot stopped")

telegram_bot = TelegramBotManager()
