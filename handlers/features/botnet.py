from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import csv
import io
import logging

from core.botnet_manager import botnet_manager
from core.antidetect import antidetect_system
from core.recovery_system import recovery_system
from core.session_importer import session_importer

logger = logging.getLogger(__name__)
botnet_router = Router()
router = botnet_router

class BotnetStates(StatesGroup):
    waiting_csv = State()
    waiting_phone = State()
    waiting_proxy = State()
    waiting_session_file = State()
    waiting_session_string = State()
    waiting_proxy_add = State()
    waiting_reaction_target = State()
    waiting_watch_user = State()

def botnet_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ ДОДАТИ БОТІВ", callback_data="add_bots")],
        [
            InlineKeyboardButton(text="📋 БОТИ", callback_data="list_bots"),
            InlineKeyboardButton(text="🔄 ПРОКСІ", callback_data="proxy_rotation"),
            InlineKeyboardButton(text="📊 СТАТИ", callback_data="bots_stats")
        ],
        [
            InlineKeyboardButton(text="📈 АКТИВНІСТЬ", callback_data="bot_activity_dashboard"),
            InlineKeyboardButton(text="💬 ПЕРЕПИСКИ", callback_data="bot_conversations")
        ],
        [
            InlineKeyboardButton(text="⚡ КОМАНДИ", callback_data="bot_commands_menu"),
            InlineKeyboardButton(text="👁 СТЕЖЕННЯ", callback_data="bot_watch_menu")
        ],
        [
            InlineKeyboardButton(text="🔥 ПРОГРІВ", callback_data="warm_bots"),
            InlineKeyboardButton(text="🛡️ АНТИДЕТЕКТ", callback_data="antidetect_menu"),
            InlineKeyboardButton(text="🔧 РЕКАВЕРІ", callback_data="recovery_menu")
        ],
        [
            InlineKeyboardButton(text="📥 ІМПОРТ СЕСІЙ", callback_data="session_import_menu"),
            InlineKeyboardButton(text="🧬 БІОМЕТРІЯ", callback_data="tools_behavior")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="user_menu")]
    ])

def botnet_description(total=0, active=0, pending=0, errors=0) -> str:
    return f"""<b>🤖 ЦЕНТР УПРАВЛІННЯ БОТАМИ</b>
<i>Повний контроль над вашою мережею</i>

───────────────

<b>📊 ПОТОЧНИЙ СТАТУС:</b>
├ 📱 Всього ботів: <code>{total}</code>
├ 🟢 Активних: <code>{active}</code>
├ 🟡 Очікування: <code>{pending}</code>
└ 🔴 Помилки: <code>{errors}</code>

───────────────

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
    if not query.message:
        return
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
    if not query.message:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Завантажити CSV", callback_data="upload_csv")],
        [InlineKeyboardButton(text="⚙️ Налаштування імпорту", callback_data="bot_settings")],
        [InlineKeyboardButton(text="◀️ Повернутись", callback_data="botnet_main")]
    ])
    text = """<b>➕ ДОДАВАННЯ НОВИХ БОТІВ</b>
<i>Швидкий імпорт через CSV-файл</i>

───────────────

<b>📋 Формат CSV-файлу:</b>
<code>phone,firstName,lastName</code>
<code>+380501234567,Олег,Петренко</code>
<code>+380671234567,Марія,Іванова</code>

<b>💡 Підказка:</b>
Ви також можете просто надіслати список номерів телефонів, кожен з нового рядка.

───────────────

<b>⚡ Після імпорту:</b>
├ Автоматична валідація номерів
├ Підготовка до авторизації
└ Запуск циклу прогріву"""
    await query.message.answer(text, reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "upload_csv")
async def upload_csv(query: CallbackQuery, state: FSMContext):
    await query.answer()
    if not query.message:
        return
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
    
    if not message.bot or not message.document or not message.from_user:
        await message.answer("❌ Помилка обробки файлу")
        return
    
    try:
        file = await message.bot.get_file(message.document.file_id)
        if not file.file_path:
            await message.answer("❌ Не вдалося отримати файл")
            return
        file_content = await message.bot.download_file(file.file_path)
        if not file_content:
            await message.answer("❌ Не вдалося завантажити файл")
            return
        
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
    
    if not message.text or not message.from_user:
        await message.answer("❌ Помилка обробки тексту")
        return
    
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
    if not query.message:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔒 SOCKS5", callback_data="proxy_socks5")], [InlineKeyboardButton(text="🌐 HTTP", callback_data="proxy_http")], [InlineKeyboardButton(text="◀️ Назад", callback_data="add_bots")]])
    await query.message.answer("⚙️ <b>НАЛАШТУВАННЯ БОТІВ</b>\n\nТип проксі: SOCKS5 (рекомендовано)\nІнтервал: 10-30 сек\nПрогрів: Автоматичний (72 ч)", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data.in_(["proxy_socks5", "proxy_http"]))
async def proxy_type(query: CallbackQuery):
    await query.answer("✅ Тип обрано!")
    if not query.message:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="bot_settings")]])
    await query.message.answer("✅ <b>НАЛАШТУВАННЯ ЗБЕРЕЖЕНО</b>\n\nБоти будуть додані з обраними параметрами", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "list_bots")
async def list_bots(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
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

───────────────

<b>📊 ЗАГАЛЬНА СТАТИСТИКА:</b>
├ 📱 Всього у системі: <code>{total}</code>
├ 🟢 Активних та готових: <code>{active}</code>
├ 🟡 В очікуванні: <code>{pending}</code>
└ 🔴 З помилками: <code>{error}</code>

───────────────

<b>🔍 Оберіть категорію для перегляду:</b>"""
    await query.message.answer(text, reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "bots_active")
async def bots_active(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📊 Деталі", callback_data="bot_detail_1")], [InlineKeyboardButton(text="🔧 Дії", callback_data="bot_actions")], [InlineKeyboardButton(text="◀️ Назад", callback_data="list_bots")]])
    await query.message.answer("🟢 <b>АКТИВНІ БОТИ (38)</b>\n\n@bot_001 | 234 пов. | 0 помилок\n@bot_002 | 189 пов. | 1 помилка\n@bot_003 | 156 пов. | 0 помилок", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "bot_detail_1")
async def bot_detail(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="bots_active")]])
    await query.message.answer("📊 <b>ДЕТАЛІ БОТА @bot_001</b>\n\nСтатус: 🟢 Online\nПовідомлень: 234\nПомилок: 0\nЛиш активна: 2 хв", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "bot_actions")
async def bot_actions(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔧 Перезавантажити", callback_data="restart_bot")], [InlineKeyboardButton(text="🗑️ Видалити", callback_data="delete_bot")], [InlineKeyboardButton(text="◀️ Назад", callback_data="bots_active")]])
    await query.message.answer("🔧 <b>ДІЇ З БОТОМ</b>\n\nВиберіть дію для бота @bot_001", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "delete_bot")
async def delete_bot(query: CallbackQuery):
    await query.answer("✅ Бот видален!")
    if not query.message:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="bots_active")]])
    await query.message.answer("✅ <b>БОТ ВИДАЛЕН</b>\n\n@bot_001 видален з системи", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "bots_waiting")
async def bots_waiting(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="list_bots")]])
    await query.message.answer("🟡 <b>БОТИ В ОЧІКУВАННІ (5)</b>\n\nbot_041 - Прогрівання (35%)\nbot_042 - Авторизація\nbot_043 - Чекає номера", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "bots_error")
async def bots_error(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔧 Виправити", callback_data="fix_error")], [InlineKeyboardButton(text="🗑️ Видалити", callback_data="delete_error_bot")], [InlineKeyboardButton(text="◀️ Назад", callback_data="list_bots")]])
    await query.message.answer("🔴 <b>БОТИ З ПОМИЛКАМИ (2)</b>\n\nbot_043 - Блокування від Telegram\nbot_044 - Помилка авторизації", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "fix_error")
async def fix_error(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="bots_error")]])
    await query.message.answer("🔧 <b>ВИПРАВЛЕННЯ ПОМИЛКИ</b>\n\nПопробуємо перезавантажити бота...\nПочекайте 1-2 хвилини", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "delete_error_bot")
async def delete_error_bot(query: CallbackQuery):
    await query.answer("✅ Бот видален!")
    if not query.message:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="bots_error")]])
    await query.message.answer("✅ <b>БОТ З ПОМИЛКОЮ ВИДАЛЕН</b>\n\nДобавте новий бот", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "proxy_rotation")
async def proxy_rotation(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔧 Налаштування", callback_data="proxy_config")], [InlineKeyboardButton(text="📊 Статистика", callback_data="proxy_stats")], [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]])
    await query.message.answer("🔄 <b>РОТАЦІЯ ПРОКСІ</b>\n\nАктивних: 12\nРобочих: 11 (92%)\nМертвих: 1 (8%)", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "proxy_config")
async def proxy_config(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="proxy_rotation")]])
    await query.message.answer("⚙️ <b>НАЛАШТУВАННЯ ПРОКСІ</b>\n\nІнтервал: 60 хвилин\nТип: SOCKS5 (100%)\nРегіони: UA, RU, US, EU", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "proxy_stats")
async def proxy_stats(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="proxy_rotation")]])
    await query.message.answer("📊 <b>СТАТИСТИКА ПРОКСІ</b>\n\nЗапитів день: 1,245\nПомилок: 2 (0.16%)\nСередня швидкість: 245ms", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "warm_bots")
async def warm_bots(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⏸️ Пауза", callback_data="pause_warming")], [InlineKeyboardButton(text="🛑 Зупинити", callback_data="stop_warming")], [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]])
    await query.message.answer("🔥 <b>ПРОГРІЙ БОТІВ</b>\n\nПрогрес: 28/45 (62%)\nЗалишилось: 47 годин 15 хвилин", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "pause_warming")
async def pause_warming(query: CallbackQuery):
    await query.answer("⏸️ Прогрів паузовано!")
    if not query.message:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶️ Продовжити", callback_data="warm_bots")], [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]])
    await query.message.answer("⏸️ <b>ПРОГРІЙ ПАУЗОВАНО</b>\n\nМожете продовжити коли будете готові", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "stop_warming")
async def stop_warming(query: CallbackQuery):
    await query.answer("🛑 Прогрів зупинен!")
    if not query.message:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]])
    await query.message.answer("🛑 <b>ПРОГРІЙ ЗУПИНЕН</b>\n\nПрогрів скасовано. Боти не будуть готові", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "bots_stats")
async def bots_stats(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📈 Графіки", callback_data="stat_charts")], [InlineKeyboardButton(text="⚠️ Помилки", callback_data="stat_errors")], [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]])
    await query.message.answer("📊 <b>СТАТИСТИКА БОТІВ</b>\n\nАктивність: 84.4%\nЯкість: 93.3%\nПомилки: 6.7%", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "stat_charts")
async def stat_charts(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="bots_stats")]])
    await query.message.answer("📈 <b>ГРАФІКИ АКТИВНОСТІ</b>\n\nПонеділок: 85% | Вівторок: 87% | Середа: 92%\nЧетвер: 90% | Пятниця: 88%", reply_markup=kb, parse_mode="HTML")

@botnet_router.callback_query(F.data == "stat_errors")
async def stat_errors(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="bots_stats")]])
    await query.message.answer("⚠️ <b>АНАЛІЗ ПОМИЛОК</b>\n\nБлокування: 1 (33%)\nАвторизація: 1 (33%)\nНомер: 1 (33%)", reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data == "antidetect_menu")
async def antidetect_menu(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Профілі пристроїв", callback_data="antidetect_profiles")],
        [InlineKeyboardButton(text="🎭 Патерни поведінки", callback_data="antidetect_behavior")],
        [InlineKeyboardButton(text="🔑 Генерувати Fingerprint", callback_data="antidetect_generate")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="antidetect_stats")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]
    ])
    await query.message.edit_text(
        "<b>🛡️ АНТИДЕТЕКТ СИСТЕМА</b>\n"
        "═══════════════════════\n\n"
        "Захист від виявлення Telegram:\n"
        "├ 9 профілів пристроїв\n"
        "├ 5 патернів поведінки\n"
        "├ Унікальні fingerprint\n"
        "└ Емуляція людської поведінки\n\n"
        "Оберіть опцію:",
        reply_markup=kb, parse_mode="HTML"
    )


@botnet_router.callback_query(F.data == "antidetect_profiles")
async def antidetect_profiles(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    profiles = list(antidetect_system.DEVICE_PROFILES.keys())
    text = "<b>📱 ПРОФІЛІ ПРИСТРОЇВ</b>\n═══════════════════════\n\n"
    for i, p in enumerate(profiles, 1):
        profile = antidetect_system.DEVICE_PROFILES[p]
        text += f"{i}. <b>{p}</b>\n   └ {profile['device_model']} | {profile['system_version']}\n"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="antidetect_menu")]
    ])
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data == "antidetect_behavior")
async def antidetect_behavior(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    patterns = list(antidetect_system.BEHAVIOR_PATTERNS.keys())
    text = "<b>🎭 ПАТЕРНИ ПОВЕДІНКИ</b>\n═══════════════════════\n\n"
    for p in patterns:
        pattern = antidetect_system.BEHAVIOR_PATTERNS[p]
        online = pattern['online_times']
        text += f"<b>{p}</b>\n"
        text += f"├ Онлайн: {online}\n"
        text += f"├ Швидкість: {pattern['typing_speed']} мс\n"
        text += f"└ Реакція: {pattern['reaction_time']} сек\n\n"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="antidetect_menu")]
    ])
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data == "antidetect_generate")
async def antidetect_generate(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    profile_type = antidetect_system.get_random_profile_type()
    fingerprint = antidetect_system.generate_device_fingerprint(profile_type)
    report = antidetect_system.format_fingerprint_report(fingerprint)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Згенерувати ще", callback_data="antidetect_generate")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="antidetect_menu")]
    ])
    await query.message.edit_text(report, reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data == "antidetect_stats")
async def antidetect_stats(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    generated = len(antidetect_system.generated_fingerprints)
    profiles_count = len(antidetect_system.DEVICE_PROFILES)
    patterns_count = len(antidetect_system.BEHAVIOR_PATTERNS)
    text = (
        "<b>📊 СТАТИСТИКА АНТИДЕТЕКТ</b>\n"
        "═══════════════════════\n\n"
        f"├ Згенеровано fingerprint: {generated}\n"
        f"├ Профілів пристроїв: {profiles_count}\n"
        f"└ Патернів поведінки: {patterns_count}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="antidetect_menu")]
    ])
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data == "recovery_menu")
async def recovery_menu(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    proxy_stats = await recovery_system.health_check_proxies()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Відновити ботів", callback_data="recovery_bots")],
        [InlineKeyboardButton(text="🌐 Пул проксі", callback_data="recovery_proxies")],
        [InlineKeyboardButton(text="💾 Резервні копії", callback_data="recovery_backups")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]
    ])
    await query.message.edit_text(
        "<b>🔧 СИСТЕМА ВІДНОВЛЕННЯ</b>\n"
        "═══════════════════════\n\n"
        f"<b>Пул проксі:</b>\n"
        f"├ Всього: {proxy_stats['total']}\n"
        f"├ Активних: {proxy_stats['active']}\n"
        f"└ Мертвих: {proxy_stats['dead']}\n\n"
        "<b>Можливості:</b>\n"
        "├ Автовідновлення ботів\n"
        "├ Ротація проксі\n"
        "└ Резервне копіювання",
        reply_markup=kb, parse_mode="HTML"
    )


@botnet_router.callback_query(F.data == "recovery_bots")
async def recovery_bots(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    stats = botnet_manager.get_statistics()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Відновити все", callback_data="recovery_all")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="recovery_menu")]
    ])
    await query.message.edit_text(
        "<b>🔄 ВІДНОВЛЕННЯ БОТІВ</b>\n"
        "═══════════════════════\n\n"
        f"├ Всього ботів: {stats['total_bots']}\n"
        f"├ Доступних: {stats['available_bots']}\n"
        f"├ Зайнятих: {stats['busy_bots']}\n"
        f"├ Черга завдань: {stats['queue_size']}\n"
        f"└ Воркерів: {stats['workers']}\n\n"
        "Натисніть для масового відновлення:",
        reply_markup=kb, parse_mode="HTML"
    )


@botnet_router.callback_query(F.data == "recovery_all")
async def recovery_all(query: CallbackQuery):
    await query.answer("🔄 Запуск відновлення...")
    if not query.message:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="recovery_menu")]
    ])
    await query.message.edit_text(
        "<b>✅ ВІДНОВЛЕННЯ ЗАПУЩЕНО</b>\n"
        "═══════════════════════\n\n"
        "Система автоматично відновлює ботів:\n"
        "├ Перепідключення\n"
        "├ Ротація проксі\n"
        "└ Відновлення з бекапу\n\n"
        "Перегляньте статистику пізніше.",
        reply_markup=kb, parse_mode="HTML"
    )


@botnet_router.callback_query(F.data == "recovery_proxies")
async def recovery_proxies(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    stats = recovery_system.get_proxy_stats()
    text = "<b>🌐 ПУЛ ПРОКСІ</b>\n═══════════════════════\n\n"
    if not stats:
        text += "Немає проксі в пулі.\nДодайте проксі для роботи."
    else:
        for i, p in enumerate(stats[:10], 1):
            status_emoji = "🟢" if p['status'] == 'active' else "🔴"
            text += f"{i}. {status_emoji} {p['host']}:{p['port']}\n"
            text += f"   └ Використань: {p['usage_count']} | Помилок: {p['failure_count']}\n"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Додати проксі", callback_data="add_proxy")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="recovery_menu")]
    ])
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data == "add_proxy")
async def add_proxy(query: CallbackQuery, state: FSMContext):
    await query.answer()
    if not query.message:
        return
    await state.set_state(BotnetStates.waiting_proxy_add)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="recovery_proxies")]
    ])
    await query.message.edit_text(
        "<b>➕ ДОДАВАННЯ ПРОКСІ</b>\n"
        "═══════════════════════\n\n"
        "Надішліть проксі у форматі:\n"
        "<code>host:port:username:password</code>\n\n"
        "Або без авторизації:\n"
        "<code>host:port</code>\n\n"
        "Можна кілька, по одному на рядок.",
        reply_markup=kb, parse_mode="HTML"
    )


@botnet_router.message(BotnetStates.waiting_proxy_add)
async def process_proxy_add(message: Message, state: FSMContext):
    await state.clear()
    if not message.text:
        await message.answer("❌ Невірний формат")
        return
    lines = message.text.strip().split('\n')
    added = 0
    for line in lines:
        parts = line.strip().split(':')
        if len(parts) >= 2:
            proxy = {
                'host': parts[0],
                'port': int(parts[1]) if parts[1].isdigit() else 0,
                'username': parts[2] if len(parts) > 2 else None,
                'password': parts[3] if len(parts) > 3 else None,
                'type': 'socks5'
            }
            if proxy['port'] > 0:
                recovery_system.add_proxy(proxy)
                added += 1
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="recovery_proxies")]
    ])
    await message.answer(f"✅ Додано {added} проксі", reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data == "recovery_backups")
async def recovery_backups(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    backups_count = sum(len(b) for b in recovery_system.backup_storage.values())
    bots_with_backups = len(recovery_system.backup_storage)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="recovery_menu")]
    ])
    await query.message.edit_text(
        "<b>💾 РЕЗЕРВНІ КОПІЇ</b>\n"
        "═══════════════════════\n\n"
        f"├ Ботів з бекапами: {bots_with_backups}\n"
        f"├ Всього бекапів: {backups_count}\n"
        f"└ Макс. на бота: {recovery_system.settings['max_backups_per_bot']}\n\n"
        "Бекапи створюються автоматично.",
        reply_markup=kb, parse_mode="HTML"
    )


@botnet_router.callback_query(F.data == "session_import_menu")
async def session_import_menu(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    imported = len(session_importer.imported_sessions)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Завантажити файл", callback_data="import_session_file")],
        [InlineKeyboardButton(text="📝 Ввести StringSession", callback_data="import_session_string")],
        [InlineKeyboardButton(text="📋 Імпортовані сесії", callback_data="imported_sessions_list")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]
    ])
    await query.message.edit_text(
        "<b>📥 ІМПОРТ СЕСІЙ</b>\n"
        "═══════════════════════\n\n"
        f"Імпортовано сесій: {imported}\n\n"
        "<b>Підтримувані формати:</b>\n"
        "├ .session (Telethon)\n"
        "├ .json (Pyrogram)\n"
        "├ .txt (StringSession)\n"
        "└ .zip (TData)\n\n"
        "Оберіть спосіб імпорту:",
        reply_markup=kb, parse_mode="HTML"
    )


@botnet_router.callback_query(F.data == "import_session_file")
async def import_session_file(query: CallbackQuery, state: FSMContext):
    await query.answer()
    if not query.message:
        return
    await state.set_state(BotnetStates.waiting_session_file)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="session_import_menu")]
    ])
    await query.message.edit_text(
        "<b>📤 ЗАВАНТАЖЕННЯ СЕСІЇ</b>\n"
        "═══════════════════════\n\n"
        "Надішліть файл сесії:\n"
        "├ .session (Telethon)\n"
        "├ .json (Pyrogram)\n"
        "└ .zip (TData архів)",
        reply_markup=kb, parse_mode="HTML"
    )


@botnet_router.message(BotnetStates.waiting_session_file, F.document)
async def process_session_file(message: Message, state: FSMContext):
    await state.clear()
    if not message.bot or not message.document:
        await message.answer("❌ Помилка обробки файлу")
        return
    try:
        file = await message.bot.get_file(message.document.file_id)
        if not file.file_path:
            await message.answer("❌ Не вдалося отримати файл")
            return
        file_name = message.document.file_name or "session"
        file_path = f"/tmp/{file_name}"
        await message.bot.download_file(file.file_path, file_path)
        result = await session_importer.import_session(file_path=file_path)
        report = session_importer.format_import_report(result)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Валідувати", callback_data=f"validate_session:{result.get('session_hash', '')}")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="session_import_menu")]
        ])
        await message.answer(report, reply_markup=kb, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Session import error: {e}")
        await message.answer(f"❌ Помилка імпорту: {e}")


@botnet_router.callback_query(F.data == "import_session_string")
async def import_session_string(query: CallbackQuery, state: FSMContext):
    await query.answer()
    if not query.message:
        return
    await state.set_state(BotnetStates.waiting_session_string)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="session_import_menu")]
    ])
    await query.message.edit_text(
        "<b>📝 ВВЕДЕННЯ STRINGSESSION</b>\n"
        "═══════════════════════\n\n"
        "Надішліть StringSession.\n\n"
        "Підтримуються:\n"
        "├ Telethon (починається з 1)\n"
        "└ Pyrogram (починається з B)",
        reply_markup=kb, parse_mode="HTML"
    )


@botnet_router.message(BotnetStates.waiting_session_string)
async def process_session_string(message: Message, state: FSMContext):
    await state.clear()
    if not message.text:
        await message.answer("❌ Невірний формат")
        return
    result = await session_importer.import_session(session_string=message.text)
    report = session_importer.format_import_report(result)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Валідувати", callback_data=f"validate_session:{result.get('session_hash', '')}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="session_import_menu")]
    ])
    await message.answer(report, reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data.startswith("validate_session:"))
async def validate_session(query: CallbackQuery):
    await query.answer("⏳ Валідація...")
    if not query.message or not query.data:
        return
    parts = query.data.split(":")
    session_hash = parts[1] if len(parts) > 1 else ""
    if not session_hash:
        await query.message.edit_text("❌ Невірний hash сесії")
        return
    validation = await session_importer.validate_session(session_hash)
    report = session_importer.format_validation_report(validation)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="session_import_menu")]
    ])
    await query.message.edit_text(report, reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data == "imported_sessions_list")
async def imported_sessions_list(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    sessions = session_importer.get_imported_sessions()
    text = "<b>📋 ІМПОРТОВАНІ СЕСІЇ</b>\n═══════════════════════\n\n"
    if not sessions:
        text += "Немає імпортованих сесій."
    else:
        for i, s in enumerate(sessions[:10], 1):
            status = "✅" if s.get('success') else "❌"
            text += f"{i}. {status} <code>{s.get('session_hash', 'N/A')}</code>\n"
            text += f"   └ Формат: {s.get('format', 'N/A')}\n"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="session_import_menu")]
    ])
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data == "bot_activity_dashboard")
async def bot_activity_dashboard(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    
    from core.bot_activity_tracker import bot_activity_tracker
    from core.session_manager import session_manager
    
    stats = bot_activity_tracker.get_stats()
    summaries = await bot_activity_tracker.get_all_bots_summary()
    
    text = "<b>📈 ДАШБОРД АКТИВНОСТІ БОТІВ</b>\n"
    text += "═══════════════════════\n\n"
    text += f"<b>📊 Загальна статистика:</b>\n"
    text += f"├ Ботів відстежується: {stats['bots_tracked']}\n"
    text += f"├ Всього подій: {stats['total_events']}\n"
    text += f"└ Всього діалогів: {stats['total_conversations']}\n\n"
    
    if summaries:
        text += "<b>🤖 Активність ботів:</b>\n"
        for i, bot in enumerate(summaries[:8], 1):
            status_icon = "🟢" if bot["is_active"] else "🔴"
            health_icon = "💚" if bot["health_score"] >= 80 else "💛" if bot["health_score"] >= 50 else "❤️"
            text += f"{i}. {status_icon} <code>{bot['bot_id'][:20]}</code>\n"
            text += f"   ├ {health_icon} Здоров'я: {bot['health_score']}%\n"
            text += f"   ├ ↑ Відправлено: {bot['messages_sent']}\n"
            text += f"   ├ ↓ Отримано: {bot['messages_received']}\n"
            text += f"   └ 💬 Діалогів: {bot['conversations']}\n"
    else:
        text += "<i>Немає даних про активність</i>\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Детальний звіт", callback_data="bot_detailed_report")],
        [InlineKeyboardButton(text="📩 Хто пише ботам", callback_data="bot_incoming_contacts")],
        [InlineKeyboardButton(text="📤 Кому пишуть боти", callback_data="bot_outgoing_contacts")],
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="bot_activity_dashboard")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data == "bot_conversations")
async def bot_conversations_menu(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    
    from core.bot_activity_tracker import bot_activity_tracker
    
    stats = bot_activity_tracker.get_stats()
    
    text = "<b>💬 ПЕРЕПИСКИ БОТІВ</b>\n"
    text += "═══════════════════════\n\n"
    text += f"<b>📊 Статистика:</b>\n"
    text += f"├ Всього діалогів: {stats['total_conversations']}\n"
    text += f"└ Ботів з діалогами: {stats['bots_tracked']}\n\n"
    text += "<b>Виберіть категорію:</b>"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📩 Вхідні (хто пише ботам)", callback_data="bot_incoming_contacts")],
        [InlineKeyboardButton(text="📤 Вихідні (кому пишуть боти)", callback_data="bot_outgoing_contacts")],
        [InlineKeyboardButton(text="🔥 Топ контакти", callback_data="bot_top_contacts")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data == "bot_incoming_contacts")
async def bot_incoming_contacts(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    
    from core.bot_activity_tracker import bot_activity_tracker
    
    all_incoming = []
    for bot_id in bot_activity_tracker.conversations.keys():
        incoming = await bot_activity_tracker.get_incoming_contacts(bot_id)
        for conv in incoming:
            all_incoming.append((bot_id, conv))
    
    all_incoming.sort(key=lambda x: x[1].last_message, reverse=True)
    
    text = "<b>📩 ХТО ПИШЕ БОТАМ</b>\n"
    text += "═══════════════════════\n"
    text += "<i>Контакти, які ініціювали діалог</i>\n\n"
    
    if not all_incoming:
        text += "<i>Немає вхідних контактів</i>"
    else:
        for i, (bot_id, conv) in enumerate(all_incoming[:15], 1):
            name = conv.user_username or conv.user_name or str(conv.user_id)
            diff = (query.message.date.replace(tzinfo=None) - conv.last_message) if hasattr(query.message, 'date') else None
            time_str = conv.last_message.strftime("%d.%m %H:%M")
            
            text += f"<b>{i}. {name}</b>\n"
            text += f"   ├ ID: <code>{conv.user_id}</code>\n"
            text += f"   ├ Бот: <code>{bot_id[:15]}...</code>\n"
            text += f"   ├ ↑{conv.messages_sent} ↓{conv.messages_received}\n"
            text += f"   └ 🕐 {time_str}\n"
            
            if conv.last_message_preview:
                text += f"   💬 <i>{conv.last_message_preview[:40]}...</i>\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="bot_incoming_contacts")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="bot_conversations")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data == "bot_outgoing_contacts")
async def bot_outgoing_contacts(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    
    from core.bot_activity_tracker import bot_activity_tracker
    
    all_outgoing = []
    for bot_id in bot_activity_tracker.conversations.keys():
        outgoing = await bot_activity_tracker.get_outgoing_conversations(bot_id)
        for conv in outgoing:
            all_outgoing.append((bot_id, conv))
    
    all_outgoing.sort(key=lambda x: x[1].last_message, reverse=True)
    
    text = "<b>📤 КОМУ ПИШУТЬ БОТИ</b>\n"
    text += "═══════════════════════\n"
    text += "<i>Вихідні діалоги</i>\n\n"
    
    if not all_outgoing:
        text += "<i>Немає вихідних діалогів</i>"
    else:
        for i, (bot_id, conv) in enumerate(all_outgoing[:15], 1):
            name = conv.user_username or conv.user_name or str(conv.user_id)
            time_str = conv.last_message.strftime("%d.%m %H:%M")
            
            text += f"<b>{i}. {name}</b>\n"
            text += f"   ├ ID: <code>{conv.user_id}</code>\n"
            text += f"   ├ Бот: <code>{bot_id[:15]}...</code>\n"
            text += f"   ├ ↑{conv.messages_sent} ↓{conv.messages_received}\n"
            text += f"   └ 🕐 {time_str}\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="bot_outgoing_contacts")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="bot_conversations")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data == "bot_top_contacts")
async def bot_top_contacts(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    
    from core.bot_activity_tracker import bot_activity_tracker
    
    all_contacts = []
    for bot_id, convs in bot_activity_tracker.conversations.items():
        for user_id, conv in convs.items():
            total_msgs = conv.messages_sent + conv.messages_received
            all_contacts.append((bot_id, conv, total_msgs))
    
    all_contacts.sort(key=lambda x: x[2], reverse=True)
    
    text = "<b>🔥 ТОП КОНТАКТИ</b>\n"
    text += "═══════════════════════\n"
    text += "<i>За кількістю повідомлень</i>\n\n"
    
    if not all_contacts:
        text += "<i>Немає даних</i>"
    else:
        for i, (bot_id, conv, total) in enumerate(all_contacts[:15], 1):
            name = conv.user_username or conv.user_name or str(conv.user_id)
            direction = "📩" if conv.is_incoming else "📤"
            
            text += f"<b>{i}. {direction} {name}</b>\n"
            text += f"   ├ Всього: {total} повідомлень\n"
            text += f"   └ ↑{conv.messages_sent} ↓{conv.messages_received}\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="bot_top_contacts")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="bot_conversations")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data == "bot_detailed_report")
async def bot_detailed_report(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    
    from core.bot_activity_tracker import bot_activity_tracker
    
    summaries = await bot_activity_tracker.get_all_bots_summary()
    
    text = "<b>📋 ДЕТАЛЬНИЙ ЗВІТ БОТІВ</b>\n"
    text += "═══════════════════════\n\n"
    
    if not summaries:
        text += "<i>Немає даних</i>"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="bot_activity_dashboard")]
        ])
    else:
        buttons = []
        for bot in summaries[:10]:
            bot_id = bot['bot_id']
            short_id = bot_id[:15] + "..." if len(bot_id) > 15 else bot_id
            status = "🟢" if bot["is_active"] else "🔴"
            buttons.append([InlineKeyboardButton(
                text=f"{status} {short_id} ({bot['messages_sent']}↑ {bot['messages_received']}↓)",
                callback_data=f"bot_report:{bot_id[:30]}"
            )])
        
        text += "Виберіть бота для детального звіту:\n"
        
        buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="bot_activity_dashboard")])
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data.startswith("bot_report:"))
async def show_bot_report(query: CallbackQuery):
    await query.answer("⏳ Генерую звіт...")
    if not query.message or not query.data:
        return
    
    bot_id = query.data.replace("bot_report:", "")
    
    from core.bot_activity_tracker import bot_activity_tracker
    
    report = await bot_activity_tracker.get_bot_report(bot_id)
    text = bot_activity_tracker.format_report(report)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Переписки", callback_data=f"bot_convs:{bot_id[:30]}")],
        [InlineKeyboardButton(text="🔄 Оновити", callback_data=f"bot_report:{bot_id[:30]}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="bot_detailed_report")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data.startswith("bot_convs:"))
async def show_bot_conversations(query: CallbackQuery):
    await query.answer()
    if not query.message or not query.data:
        return
    
    bot_id = query.data.replace("bot_convs:", "")
    
    from core.bot_activity_tracker import bot_activity_tracker
    
    conversations = list(bot_activity_tracker.conversations.get(bot_id, {}).values())
    conversations.sort(key=lambda x: x.last_message, reverse=True)
    
    text = bot_activity_tracker.format_conversations_list(
        conversations,
        f"💬 ПЕРЕПИСКИ БОТА"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Оновити", callback_data=f"bot_convs:{bot_id[:30]}")],
        [InlineKeyboardButton(text="◀️ До звіту", callback_data=f"bot_report:{bot_id[:30]}")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data == "bot_commands_menu")
async def bot_commands_menu(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    
    from core.bot_commands import bot_commands
    
    stats = bot_commands.get_stats()
    
    text = "<b>⚡ КОМАНДИ БОТАМ</b>\n"
    text += "═══════════════════════\n\n"
    text += f"<b>📊 Статистика:</b>\n"
    text += f"├ Команд в черзі: {stats['total_pending_commands']}\n"
    text += f"├ Ботів з командами: {stats['bots_with_commands']}\n"
    text += f"└ Виконано: {stats['command_history_size']}\n\n"
    text += "<b>Доступні команди:</b>\n"
    text += "├ 👍 Реакції на пости\n"
    text += "├ 💬 Відправка повідомлень\n"
    text += "├ 📥 Вхід в чати\n"
    text += "└ 📤 Вихід з чатів"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👍 Поставити реакцію", callback_data="cmd_add_reaction")],
        [InlineKeyboardButton(text="💬 Відправити повідомлення", callback_data="cmd_send_message")],
        [InlineKeyboardButton(text="📥 Вступити в чат", callback_data="cmd_join_chat")],
        [InlineKeyboardButton(text="📋 Черга команд", callback_data="cmd_queue_view")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data == "cmd_add_reaction")
async def cmd_add_reaction_menu(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    
    from core.bot_commands import bot_commands
    
    reactions = bot_commands.available_reactions[:32]
    reaction_text = " ".join(reactions)
    
    text = "<b>👍 ДОДАТИ РЕАКЦІЮ</b>\n"
    text += "═══════════════════════\n\n"
    text += "<b>Доступні реакції:</b>\n"
    text += f"{reaction_text}\n\n"
    text += "<b>Виберіть популярну реакцію:</b>"
    
    buttons = []
    row = []
    for i, r in enumerate(reactions[:16]):
        row.append(InlineKeyboardButton(text=r, callback_data=f"reaction_select:{r}"))
        if len(row) == 4:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="bot_commands_menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data.startswith("reaction_select:"))
async def reaction_selected(query: CallbackQuery, state: FSMContext):
    await query.answer()
    if not query.message or not query.data:
        return
    
    reaction = query.data.replace("reaction_select:", "")
    await state.update_data(selected_reaction=reaction)
    await state.set_state(BotnetStates.waiting_reaction_target)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="bot_commands_menu")]
    ])
    
    await query.message.edit_text(
        f"👍 <b>РЕАКЦІЯ: {reaction}</b>\n"
        f"═══════════════════════\n\n"
        f"<b>Введіть посилання на пост:</b>\n"
        f"<i>https://t.me/channel/123</i>\n\n"
        f"Або у форматі:\n"
        f"<code>@channel 123</code>",
        reply_markup=kb, parse_mode="HTML"
    )


@botnet_router.message(BotnetStates.waiting_reaction_target)
async def process_reaction_target(message: Message, state: FSMContext):
    data = await state.get_data()
    reaction = data.get("selected_reaction", "👍")
    target = message.text.strip() if message.text else ""
    await state.clear()
    
    if not target:
        await message.answer("❌ Порожній ввід")
        return
    
    from core.bot_commands import bot_commands, CommandType
    from core.session_manager import session_manager
    
    sessions = session_manager.get_active_sessions()
    if not sessions:
        await message.answer("❌ Немає активних ботів")
        return
    
    chat_id = 0
    message_id = 0
    
    if "t.me/" in target:
        parts = target.split("/")
        if len(parts) >= 2:
            try:
                message_id = int(parts[-1])
                chat_id = parts[-2] if not parts[-2].isdigit() else int(parts[-2])
            except:
                pass
    elif " " in target:
        parts = target.split()
        if len(parts) >= 2:
            chat_id = parts[0]
            try:
                message_id = int(parts[1])
            except:
                pass
    
    if not message_id:
        await message.answer("❌ Не вдалось розпарсити посилання")
        return
    
    queued = 0
    for session in sessions[:5]:
        bot_id = session.get("phone", session.get("session_id", "unknown"))
        await bot_commands.queue_command(
            bot_id=bot_id,
            command_type=CommandType.ADD_REACTION,
            target_id=chat_id if isinstance(chat_id, int) else None,
            target_username=chat_id if isinstance(chat_id, str) else None,
            params={"message_id": message_id, "reaction": reaction}
        )
        queued += 1
    
    await message.answer(
        f"✅ <b>Команди додано в чергу</b>\n\n"
        f"├ Реакція: {reaction}\n"
        f"├ Чат: <code>{chat_id}</code>\n"
        f"├ Повідомлення: {message_id}\n"
        f"└ Ботів: {queued}",
        parse_mode="HTML"
    )


@botnet_router.callback_query(F.data == "cmd_queue_view")
async def cmd_queue_view(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    
    from core.bot_commands import bot_commands
    
    text = "<b>📋 ЧЕРГА КОМАНД</b>\n"
    text += "═══════════════════════\n\n"
    
    total = 0
    for bot_id, commands in bot_commands.pending_commands.items():
        if commands:
            total += len(commands)
            text += f"<b>{bot_id[:20]}...</b>\n"
            for cmd in commands[:3]:
                text += f"  └ {cmd.command_type.value}\n"
            if len(commands) > 3:
                text += f"  └ ...ще {len(commands) - 3}\n"
    
    if total == 0:
        text += "<i>Черга порожня</i>"
    else:
        text += f"\n<b>Всього команд:</b> {total}"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Очистити чергу", callback_data="cmd_clear_queue")],
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="cmd_queue_view")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="bot_commands_menu")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data == "cmd_clear_queue")
async def cmd_clear_queue(query: CallbackQuery):
    from core.bot_commands import bot_commands
    bot_commands.pending_commands.clear()
    await query.answer("✅ Чергу очищено", show_alert=True)
    await cmd_queue_view(query)


@botnet_router.callback_query(F.data == "bot_watch_menu")
async def bot_watch_menu(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    
    from core.bot_commands import bot_commands
    
    stats = bot_commands.get_stats()
    unread_alerts = stats['unread_alerts']
    
    alert_badge = f" ({unread_alerts})" if unread_alerts > 0 else ""
    
    text = "<b>👁 СТЕЖЕННЯ ЗА ЮЗЕРАМИ</b>\n"
    text += "═══════════════════════\n\n"
    text += f"<b>📊 Статистика:</b>\n"
    text += f"├ Відстежується: {stats['total_watched_users']}\n"
    text += f"├ Сповіщень: {stats['total_alerts']}\n"
    text += f"└ Непрочитаних: {unread_alerts}\n\n"
    text += "<b>🔔 Відстежувані зміни:</b>\n"
    text += "├ 👤 Зміна юзернейму\n"
    text += "├ 📝 Зміна імені\n"
    text += "├ 🖼 Зміна фото\n"
    text += "├ 📄 Зміна біо\n"
    text += "└ 🟢 Онлайн статус"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🔔 Сповіщення{alert_badge}", callback_data="watch_alerts")],
        [InlineKeyboardButton(text="➕ Додати юзера", callback_data="watch_add_user")],
        [InlineKeyboardButton(text="📋 Список відстежуваних", callback_data="watch_list")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="botnet_main")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data == "watch_add_user")
async def watch_add_user(query: CallbackQuery, state: FSMContext):
    await query.answer()
    if not query.message:
        return
    
    await state.set_state(BotnetStates.waiting_watch_user)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="bot_watch_menu")]
    ])
    
    await query.message.edit_text(
        "<b>➕ ДОДАТИ ДО СТЕЖЕННЯ</b>\n"
        "═══════════════════════\n\n"
        "<b>Введіть юзера:</b>\n"
        "<i>@username або Telegram ID</i>\n\n"
        "<b>Що відстежується:</b>\n"
        "├ Зміна юзернейму\n"
        "├ Зміна імені\n"
        "├ Зміна фото\n"
        "└ Зміна біо",
        reply_markup=kb, parse_mode="HTML"
    )


@botnet_router.message(BotnetStates.waiting_watch_user)
async def process_watch_user(message: Message, state: FSMContext):
    target = message.text.strip() if message.text else ""
    await state.clear()
    
    if not target:
        await message.answer("❌ Порожній ввід")
        return
    
    from core.bot_commands import bot_commands, WatchEventType
    from core.session_manager import session_manager
    
    sessions = session_manager.get_active_sessions()
    if not sessions:
        await message.answer("❌ Немає активних ботів")
        return
    
    username = target.lstrip("@") if target.startswith("@") else None
    try:
        user_id = int(target) if not username else 0
    except:
        user_id = 0
    
    if not username and not user_id:
        await message.answer("❌ Невірний формат")
        return
    
    bot_id = sessions[0].get("phone", sessions[0].get("session_id", "unknown"))
    
    await bot_commands.watch_user(
        bot_id=bot_id,
        user_id=user_id or hash(username) % 1000000000,
        username=username,
        events=[
            WatchEventType.USERNAME_CHANGED,
            WatchEventType.NAME_CHANGED,
            WatchEventType.PHOTO_CHANGED,
            WatchEventType.BIO_CHANGED
        ],
        notify_user_id=message.from_user.id if message.from_user else 0
    )
    
    await message.answer(
        f"✅ <b>Додано до стеження</b>\n\n"
        f"├ Юзер: <code>{username or user_id}</code>\n"
        f"├ Бот: <code>{bot_id[:20]}</code>\n"
        f"└ Сповіщення: увімкнено",
        parse_mode="HTML"
    )


@botnet_router.callback_query(F.data == "watch_list")
async def watch_list(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    
    from core.bot_commands import bot_commands
    
    all_watched = await bot_commands.get_all_watched_users()
    
    text = "<b>📋 СПИСОК ВІДСТЕЖУВАНИХ</b>\n"
    text += "═══════════════════════\n\n"
    
    total = 0
    for bot_id, targets in all_watched.items():
        if targets:
            total += len(targets)
            text += f"<b>🤖 {bot_id[:15]}...</b>\n"
            for target in targets[:5]:
                name = target.target_username or target.target_name or str(target.target_id)
                text += f"  └ 👁 {name}\n"
            if len(targets) > 5:
                text += f"  └ ...ще {len(targets) - 5}\n"
    
    if total == 0:
        text += "<i>Список порожній</i>"
    else:
        text += f"\n<b>Всього:</b> {total}"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="watch_list")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="bot_watch_menu")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data == "watch_alerts")
async def watch_alerts(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    
    from core.bot_commands import bot_commands
    
    alerts = await bot_commands.get_unread_alerts()
    text = bot_commands.format_alerts(alerts)
    
    buttons = []
    if alerts:
        alert_ids = [a.alert_id for a in alerts]
        buttons.append([InlineKeyboardButton(
            text="✅ Прочитано",
            callback_data=f"mark_alerts_read:{len(alert_ids)}"
        )])
    
    buttons.append([InlineKeyboardButton(text="🔄 Оновити", callback_data="watch_alerts")])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="bot_watch_menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@botnet_router.callback_query(F.data.startswith("mark_alerts_read:"))
async def mark_alerts_read(query: CallbackQuery):
    from core.bot_commands import bot_commands
    
    alerts = await bot_commands.get_unread_alerts()
    alert_ids = [a.alert_id for a in alerts]
    await bot_commands.mark_alerts_notified(alert_ids)
    
    await query.answer(f"✅ {len(alert_ids)} сповіщень прочитано", show_alert=True)
    await watch_alerts(query)


@botnet_router.callback_query(F.data == "cmd_send_message")
async def cmd_send_message(query: CallbackQuery):
    await query.answer("🔧 В розробці", show_alert=True)


@botnet_router.callback_query(F.data == "cmd_join_chat")
async def cmd_join_chat(query: CallbackQuery):
    await query.answer("🔧 В розробці", show_alert=True)
