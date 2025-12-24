from datetime import datetime
from enum import Enum

class NotificationType(Enum):
    NEW_APPLICATION = "new_app"
    PAYMENT_CONFIRMED = "payment"
    KEY_GENERATED = "key_gen"
    MANAGER_ADDED = "mgr_add"
    BOT_BLOCKED = "bot_block"
    CAMPAIGN_COMPLETE = "campaign"
    SYSTEM_ERROR = "error"

class NotificationSystem:
    @staticmethod
    async def notify(bot, user_id: int, message: str, buttons=None):
        try:
            if buttons:
                await bot.send_message(user_id, message, reply_markup=buttons)
            else:
                await bot.send_message(user_id, message)
        except Exception as e:
            print(f"Notification error: {e}")
    
    @staticmethod
    def format_app_notification(app_id: int, client_name: str, tariff: str, amount: int, user_id: int) -> str:
        return f"""🔔 НОВА ЗАЯВКА #{app_id}

👤 Клієнт: {client_name} ({user_id})
💎 Тариф: {tariff.upper()}
💰 Сума: {amount} ₴
⏰ Час: {datetime.now().strftime('%H:%M')}
📈 Статус: НОВА"""
    
    @staticmethod
    def format_key_notification(key: str, tariff: str, days: int) -> str:
        return f"""🎉 ВАШ КЛЮЧ ДОСТУПУ!

🔑 Код: {key}
💎 Тариф: {tariff.upper()} ({days} днів)

Для активації:
1. /start
2. 🔐 Авторизація
3. Введіть ключ"""

    @staticmethod
    def format_ticket_notification(ticket_id: str, user_name: str) -> str:
        return f"""🎫 ТІКЕТ СТВОРЕНО

🆔 ID: {ticket_id}
👤 Від: {user_name}
📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}

Наша команда розглянеться протягом 2 годин."""
