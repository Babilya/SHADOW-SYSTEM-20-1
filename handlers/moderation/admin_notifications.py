from aiogram import Router

router = Router()

async def send_admin_notification(bot, admin_id, text):
    try:
        await bot.send_message(admin_id, text)
    except:
        pass
