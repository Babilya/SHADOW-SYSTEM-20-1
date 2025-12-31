from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_app_kb(app_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Шаблон", callback_data=f"template_{app_id}")],
        [InlineKeyboardButton(text="❌ Відхилити", callback_data=f"reject_{app_id}")]
    ])
