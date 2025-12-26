from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

botnet_router = Router()

def botnet_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Додати ботів", callback_data="add_bots"),
         InlineKeyboardButton(text="📋 Мої боти", callback_data="list_bots")],
        [InlineKeyboardButton(text="🔄 Ротація проксі", callback_data="proxy_rotation"),
         InlineKeyboardButton(text="🔥 Прогрій ботів", callback_data="warm_bots")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="bots_stats")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])

def botnet_description() -> str:
    return """<b>🤖 УПРАВЛІННЯ BOTNET</b>

<b>📊 СТАТУС БОТІВ:</b>
├ Всього: 45
├ 🟢 Активних: 38 (84.4%)
├ 🟡 Очікування: 5 (11.1%)
└ 🔴 Помилки: 2 (4.4%)

<b>🔧 ФУНКЦІОНАЛЬНІСТЬ:</b>

<b>➕ Додати ботів</b>
Імпорт ботів через CSV файл з номерами телефонів. Підтримується автоматична авторизація та прогрів.

<b>📋 Мої боти</b>
Список всіх ботів з детальною статистикою: активність, кількість повідомлень, помилки, останній онлайн.

<b>🔄 Ротація проксі</b>
Автоматична ротація SOCKS5/HTTP проксі для захисту ботів від блокування. Підтримка геолокацій.

<b>🔥 Прогрів ботів</b>
72-годинний прогрів нових ботів перед використанням у розсилках. Імітація активності реального користувача.

<b>📊 Статистика</b>
Детальна статистика активності ботів: успішність розсилок, помилки, блокування."""

@botnet_router.message(Command("botnet"))
async def botnet_cmd(message: Message):
    await message.answer("🤖 <b>УПРАВЛІННЯ BOTNET</b>\n\nВсього: 45 | Активних: 38 | Неактивних: 7", reply_markup=botnet_kb(), parse_mode="HTML")

@botnet_router.callback_query(F.data == "botnet_main")
async def botnet_menu(query: CallbackQuery):
    await query.answer()
    await query.message.answer("🤖 <b>УПРАВЛІННЯ BOTNET</b>\n\nВсього: 45 | Активних: 38 | Неактивних: 7", reply_markup=botnet_kb(), parse_mode="HTML")

@botnet_router.callback_query(F.data == "add_bots")
async def add_bots(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📤 Завантажити CSV", callback_data="upload_csv")], [InlineKeyboardButton(text="⚙️ Налаштування", callback_data="bot_settings")], [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]])
    await query.message.answer("➕ <b>ДОДАВАННЯ БОТІВ</b>\n\nФормат CSV: phone,firstName,lastName\n79991234567,Bot,Name", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "upload_csv")
async def upload_csv(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="add_bots")]])
    await query.message.answer("📤 <b>ЗАВАНТАЖЕННЯ CSV</b>\n\nНадішліть файл з номерами телефонів", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "bot_settings")
async def bot_settings(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔒 SOCKS5", callback_data="proxy_socks5")], [InlineKeyboardButton(text="🌐 HTTP", callback_data="proxy_http")], [InlineKeyboardButton(text="◀️ Назад", callback_data="add_bots")]])
    await query.message.answer("⚙️ <b>НАЛАШТУВАННЯ БОТІВ</b>\n\nТип проксі: SOCKS5 (рекомендовано)\nІнтервал: 10-30 сек\nПрогрів: Автоматичний (72 ч)", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "proxy_socks5" | F.data == "proxy_http")
async def proxy_type(query: CallbackQuery):
    await query.answer("✅ Тип обрано!")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="bot_settings")]])
    await query.message.answer("✅ <b>НАЛАШТУВАННЯ ЗБЕРЕЖЕНО</b>\n\nБоти будуть додані з обраними параметрами", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "list_bots")
async def list_bots(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🟢 Активні", callback_data="bots_active")], [InlineKeyboardButton(text="🟡 Очікування", callback_data="bots_waiting")], [InlineKeyboardButton(text="🔴 Помилки", callback_data="bots_error")], [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]])
    await query.message.answer("📋 <b>МОЇ БОТИ</b>\n\nВсього: 45\n🟢 Активні: 38\n🟡 Очікування: 5\n🔴 Помилки: 2", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "bots_active")
async def bots_active(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📊 Деталі", callback_data="bot_detail_1")], [InlineKeyboardButton(text="🔧 Дії", callback_data="bot_actions")], [InlineKeyboardButton(text="◀️ Назад", callback_data="list_bots")]])
    await query.message.answer("🟢 <b>АКТИВНІ БОТИ (38)</b>\n\n@bot_001 | 234 пов. | 0 помилок\n@bot_002 | 189 пов. | 1 помилка\n@bot_003 | 156 пов. | 0 помилок", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "bot_detail_1")
async def bot_detail(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="bots_active")]])
    await query.message.answer("📊 <b>ДЕТАЛІ БОТА @bot_001</b>\n\nСтатус: 🟢 Online\nПовідомлень: 234\nПомилок: 0\nЛиш активна: 2 хв", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "bot_actions")
async def bot_actions(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔧 Перезавантажити", callback_data="restart_bot")], [InlineKeyboardButton(text="🗑️ Видалити", callback_data="delete_bot")], [InlineKeyboardButton(text="◀️ Назад", callback_data="bots_active")]])
    await query.message.answer("🔧 <b>ДІЇ З БОТОМ</b>\n\nВиберіть дію для бота @bot_001", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "delete_bot")
async def delete_bot(query: CallbackQuery):
    await query.answer("✅ Бот видален!")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="bots_active")]])
    await query.message.answer("✅ <b>БОТ ВИДАЛЕН</b>\n\n@bot_001 видален з системи", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "bots_waiting")
async def bots_waiting(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="list_bots")]])
    await query.message.answer("🟡 <b>БОТИ В ОЧІКУВАННІ (5)</b>\n\nbot_041 - Прогрівання (35%)\nbot_042 - Авторизація\nbot_043 - Чекає номера", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "bots_error")
async def bots_error(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔧 Виправити", callback_data="fix_error")], [InlineKeyboardButton(text="🗑️ Видалити", callback_data="delete_error_bot")], [InlineKeyboardButton(text="◀️ Назад", callback_data="list_bots")]])
    await query.message.answer("🔴 <b>БОТИ З ПОМИЛКАМИ (2)</b>\n\nbot_043 - Блокування від Telegram\nbot_044 - Помилка авторизації", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "fix_error")
async def fix_error(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="bots_error")]])
    await query.message.answer("🔧 <b>ВИПРАВЛЕННЯ ПОМИЛКИ</b>\n\nПопробуємо перезавантажити бота...\nПочекайте 1-2 хвилини", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "delete_error_bot")
async def delete_error_bot(query: CallbackQuery):
    await query.answer("✅ Бот видален!")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="bots_error")]])
    await query.message.answer("✅ <b>БОТ З ПОМИЛКОЮ ВИДАЛЕН</b>\n\nДобавте новий бот", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "proxy_rotation")
async def proxy_rotation(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔧 Налаштування", callback_data="proxy_config")], [InlineKeyboardButton(text="📊 Статистика", callback_data="proxy_stats")], [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]])
    await query.message.answer("🔄 <b>РОТАЦІЯ ПРОКСІ</b>\n\nАктивних: 12\nРобочих: 11 (92%)\nМертвих: 1 (8%)", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "proxy_config")
async def proxy_config(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="proxy_rotation")]])
    await query.message.answer("⚙️ <b>НАЛАШТУВАННЯ ПРОКСІ</b>\n\nІнтервал: 60 хвилин\nТип: SOCKS5 (100%)\nРегіони: UA, RU, US, EU", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "proxy_stats")
async def proxy_stats(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="proxy_rotation")]])
    await query.message.answer("📊 <b>СТАТИСТИКА ПРОКСІ</b>\n\nЗапитів день: 1,245\nПомилок: 2 (0.16%)\nСередня швидкість: 245ms", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "warm_bots")
async def warm_bots(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⏸️ Пауза", callback_data="pause_warming")], [InlineKeyboardButton(text="🛑 Зупинити", callback_data="stop_warming")], [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]])
    await query.message.answer("🔥 <b>ПРОГРІЙ БОТІВ</b>\n\nПрогрес: 28/45 (62%)\nЗалишилось: 47 годин 15 хвилин", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "pause_warming")
async def pause_warming(query: CallbackQuery):
    await query.answer("⏸️ Прогрів паузовано!")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶️ Продовжити", callback_data="warm_bots")], [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]])
    await query.message.answer("⏸️ <b>ПРОГРІЙ ПАУЗОВАНО</b>\n\nМожете продовжити коли будете готові", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "stop_warming")
async def stop_warming(query: CallbackQuery):
    await query.answer("🛑 Прогрів зупинен!")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]])
    await query.message.answer("🛑 <b>ПРОГРІЙ ЗУПИНЕН</b>\n\nПрогрів скасовано. Боти не будуть готові", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "bots_stats")
async def bots_stats(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📈 Графіки", callback_data="stat_charts")], [InlineKeyboardButton(text="⚠️ Помилки", callback_data="stat_errors")], [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]])
    await query.message.answer("📊 <b>СТАТИСТИКА БОТІВ</b>\n\nАктивність: 84.4%\nЯкість: 93.3%\nПомилки: 6.7%", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "stat_charts")
async def stat_charts(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="bots_stats")]])
    await query.message.answer("📈 <b>ГРАФІКИ АКТИВНОСТІ</b>\n\nПонеділок: 85% | Вівторок: 87% | Середа: 92%\nЧетвер: 90% | Пятниця: 88%", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "stat_errors")
async def stat_errors(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="bots_stats")]])
    await query.message.answer("⚠️ <b>АНАЛІЗ ПОМИЛОК</b>\n\nБлокування: 1 (33%)\nАвторизація: 1 (33%)\nНомер: 1 (33%)", reply_markup=kb, parse_mode="HTML")

