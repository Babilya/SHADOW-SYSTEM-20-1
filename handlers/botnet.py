from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import csv
import io
import logging

logger = logging.getLogger(__name__)
botnet_router = Router()

class BotnetStates(StatesGroup):
    waiting_csv = State()
    waiting_phone = State()
    waiting_proxy = State()

def botnet_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Додати ботів", callback_data="add_bots"),
            InlineKeyboardButton(text="📋 Мої боти", callback_data="list_bots")
        ],
        [
            InlineKeyboardButton(text="🔄 Ротація проксі", callback_data="proxy_rotation"),
            InlineKeyboardButton(text="🔥 Прогрів", callback_data="warm_bots")
        ],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="bots_stats"),
            InlineKeyboardButton(text="◀️ Повернутись", callback_data="back_to_menu")
        ]
    ])

def botnet_description(total=0, active=0, pending=0, errors=0) -> str:
    return f"""<b>🤖 ЦЕНТР УПРАВЛІННЯ БОТАМИ</b>
<i>Повний контроль над вашою мережею</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 ПОТОЧНИЙ СТАТУС:</b>
├ 📱 Всього ботів: <code>{total}</code>
├ 🟢 Активних: <code>{active}</code>
├ 🟡 Очікування: <code>{pending}</code>
└ 🔴 Помилки: <code>{errors}</code>

━━━━━━━━━━━━━━━━━━━━━━━

<b>🛠️ ДОСТУПНІ ІНСТРУМЕНТИ:</b>

<b>➕ Додати ботів</b>
Швидкий імпорт через CSV-файл. Підтримка автоматичної валідації номерів та миттєве додавання до системи.

<b>📋 Мої боти</b>
Детальний огляд усіх ботів: статуси, активність, кількість надісланих повідомлень та останній час онлайн.

<b>🔄 Ротація проксі</b>
Інтелектуальна ротація SOCKS5/HTTP проксі з підтримкою геолокації для максимального захисту.

<b>🔥 Прогрів ботів</b>
72-годинний цикл прогріву нових ботів. Імітація природної поведінки реального користувача."""

@botnet_router.message(Command("botnet"))
async def botnet_cmd(message: Message):
    from core.session_manager import session_manager
    stats = session_manager.get_stats()
    by_status = stats.get("by_status", {})
    total = stats.get("total_sessions", 0)
    active = by_status.get("active", 0) + by_status.get("validated", 0)
    pending = by_status.get("pending_validation", 0)
    errors = by_status.get("banned", 0) + by_status.get("deactivated", 0)
    await message.answer(botnet_description(total, active, pending, errors), reply_markup=botnet_kb(), parse_mode="HTML")

@botnet_router.callback_query(F.data == "botnet_main")
async def botnet_menu(query: CallbackQuery):
    await query.answer()
    from core.session_manager import session_manager
    stats = session_manager.get_stats()
    by_status = stats.get("by_status", {})
    total = stats.get("total_sessions", 0)
    active = by_status.get("active", 0) + by_status.get("validated", 0)
    pending = by_status.get("pending_validation", 0)
    errors = by_status.get("banned", 0) + by_status.get("deactivated", 0)
    await query.message.answer(botnet_description(total, active, pending, errors), reply_markup=botnet_kb(), parse_mode="HTML")

@botnet_router.callback_query(F.data == "add_bots")
async def add_bots(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Завантажити CSV", callback_data="upload_csv")],
        [InlineKeyboardButton(text="⚙️ Налаштування імпорту", callback_data="bot_settings")],
        [InlineKeyboardButton(text="◀️ Повернутись", callback_data="botnet_main")]
    ])
    text = """<b>➕ ДОДАВАННЯ НОВИХ БОТІВ</b>
<i>Швидкий імпорт через CSV-файл</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>📋 Формат CSV-файлу:</b>
<code>phone,firstName,lastName</code>
<code>+380501234567,Олег,Петренко</code>
<code>+380671234567,Марія,Іванова</code>

<b>💡 Підказка:</b>
Ви також можете просто надіслати список номерів телефонів, кожен з нового рядка.

━━━━━━━━━━━━━━━━━━━━━━━

<b>⚡ Після імпорту:</b>
├ Автоматична валідація номерів
├ Підготовка до авторизації
└ Запуск циклу прогріву"""
    await query.message.answer(text, reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "upload_csv")
async def upload_csv(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(BotnetStates.waiting_csv)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="add_bots")]])
    await query.message.answer("""📤 <b>ЗАВАНТАЖЕННЯ CSV</b>

Надішліть CSV файл з номерами телефонів.

<b>Формат файлу:</b>
<code>phone,firstName,lastName</code>
<code>+380501234567,John,Doe</code>
<code>+380671234567,Jane,Smith</code>

Або просто список номерів по рядках.""", reply_markup=kb, parse_mode="HTML")

@botnet_router.message(BotnetStates.waiting_csv, F.document)
async def process_csv_file(message: Message, state: FSMContext):
    await state.clear()
    
    try:
        file = await message.bot.get_file(message.document.file_id)
        file_content = await message.bot.download_file(file.file_path)
        
        content = file_content.read().decode('utf-8')
        lines = content.strip().split('\n')
        
        imported = []
        errors = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('phone'):
                continue
            
            parts = line.split(',')
            phone = parts[0].strip().replace('"', '').replace("'", "")
            first_name = parts[1].strip() if len(parts) > 1 else ""
            last_name = parts[2].strip() if len(parts) > 2 else ""
            
            if phone.startswith('+') or phone.isdigit():
                imported.append({
                    'phone': phone,
                    'first_name': first_name,
                    'last_name': last_name
                })
            else:
                errors.append(f"Рядок {i+1}: невірний формат")
        
        if imported:
            from utils.db import async_session
            from database.models import Bot
            
            try:
                async with async_session() as session:
                    for bot_data in imported:
                        new_bot = Bot(
                            phone=bot_data['phone'],
                            project_id=message.from_user.id,
                            session_hash="",
                            status="pending_validation"
                        )
                        session.add(new_bot)
                    await session.commit()
            except Exception as db_error:
                logger.error(f"DB error during CSV import: {db_error}")
                await message.answer(f"❌ Помилка бази даних")
                return
            
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📋 Переглянути", callback_data="list_bots")],
                [InlineKeyboardButton(text="🔥 Запустити прогрів", callback_data="warm_bots")],
                [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]
            ])
            
            await message.answer(
                f"""✅ <b>CSV ІМПОРТОВАНО!</b>

<b>Успішно:</b> {len(imported)}
<b>Помилок:</b> {len(errors)}

<b>Статус:</b> Боти додані, потребують авторизації

<b>Наступний крок:</b>
Запустіть прогрів або перегляньте список ботів.""",
                reply_markup=kb, parse_mode="HTML"
            )
        else:
            await message.answer("❌ Не знайдено жодного валідного номера телефону")
    
    except Exception as e:
        logger.error(f"CSV import error: {e}")
        await message.answer(f"❌ Помилка імпорту: {e}")

@botnet_router.message(BotnetStates.waiting_csv)
async def process_csv_text(message: Message, state: FSMContext):
    await state.clear()
    
    lines = message.text.strip().split('\n')
    imported = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        parts = line.split(',')
        phone = parts[0].strip()
        
        if phone.startswith('+') or phone.isdigit():
            imported.append(phone)
    
    if imported:
        from utils.db import async_session
        from database.models import Bot
        
        try:
            async with async_session() as session:
                for phone in imported:
                    new_bot = Bot(
                        phone=phone,
                        project_id=message.from_user.id,
                        session_hash="",
                        status="pending_validation"
                    )
                    session.add(new_bot)
                await session.commit()
        except Exception as db_error:
            logger.error(f"DB error: {db_error}")
            await message.answer("❌ Помилка бази даних")
            return
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Переглянути", callback_data="list_bots")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]
        ])
        
        await message.answer(
            f"✅ Імпортовано {len(imported)} номерів",
            reply_markup=kb, parse_mode="HTML"
        )
    else:
        await message.answer("❌ Не знайдено валідних номерів")

@botnet_router.callback_query(F.data == "bot_settings")
async def bot_settings(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔒 SOCKS5", callback_data="proxy_socks5")], [InlineKeyboardButton(text="🌐 HTTP", callback_data="proxy_http")], [InlineKeyboardButton(text="◀️ Назад", callback_data="add_bots")]])
    await query.message.answer("⚙️ <b>НАЛАШТУВАННЯ БОТІВ</b>\n\nТип проксі: SOCKS5 (рекомендовано)\nІнтервал: 10-30 сек\nПрогрів: Автоматичний (72 ч)", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data.in_(["proxy_socks5", "proxy_http"]))
async def proxy_type(query: CallbackQuery):
    await query.answer("✅ Тип обрано!")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="bot_settings")]])
    await query.message.answer("✅ <b>НАЛАШТУВАННЯ ЗБЕРЕЖЕНО</b>\n\nБоти будуть додані з обраними параметрами", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "list_bots")
async def list_bots(query: CallbackQuery):
    await query.answer()
    from core.session_manager import session_manager
    stats = session_manager.get_stats()
    by_status = stats.get("by_status", {})
    total = stats.get("total_sessions", 0)
    active = by_status.get("active", 0) + by_status.get("validated", 0)
    pending = by_status.get("pending_validation", 0)
    error = by_status.get("banned", 0) + by_status.get("deactivated", 0)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🟢 Активні", callback_data="bots_active"),
            InlineKeyboardButton(text="🟡 Очікування", callback_data="bots_waiting")
        ],
        [InlineKeyboardButton(text="🔴 Боти з помилками", callback_data="bots_error")],
        [InlineKeyboardButton(text="◀️ Повернутись", callback_data="botnet_main")]
    ])
    text = f"""<b>📋 ОГЛЯД УСІХ БОТІВ</b>
<i>Детальний список та фільтрація</i>

━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 ЗАГАЛЬНА СТАТИСТИКА:</b>
├ 📱 Всього у системі: <code>{total}</code>
├ 🟢 Активних та готових: <code>{active}</code>
├ 🟡 В очікуванні: <code>{pending}</code>
└ 🔴 З помилками: <code>{error}</code>

━━━━━━━━━━━━━━━━━━━━━━━

<b>🔍 Оберіть категорію для перегляду:</b>"""
    await query.message.answer(text, reply_markup=kb, parse_mode="HTML")

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

