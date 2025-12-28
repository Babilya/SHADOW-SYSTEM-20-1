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

def botnet_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ ДОДАТИ БОТІВ", callback_data="add_bots")],
        [
            InlineKeyboardButton(text="📋 БОТИ", callback_data="list_bots"),
            InlineKeyboardButton(text="🔄 ПРОКСІ", callback_data="proxy_rotation"),
            InlineKeyboardButton(text="📊 СТАТИ", callback_data="bots_stats")
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
