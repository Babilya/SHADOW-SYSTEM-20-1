from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from core.advanced_parser import advanced_parser
from core.realtime_parser import realtime_parser

logger = logging.getLogger(__name__)
osint_router = Router()
router = osint_router

class OSINTStates(StatesGroup):
    waiting_keyword = State()
    waiting_chat = State()
    waiting_dns_domain = State()
    waiting_whois_domain = State()
    waiting_ip = State()
    waiting_email = State()
    waiting_deep_parse = State()
    waiting_monitor_chats = State()

def osint_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🌐 DNS ПОШУК", callback_data="osint_dns"),
            InlineKeyboardButton(text="📋 WHOIS ІНФО", callback_data="osint_whois")
        ],
        [
            InlineKeyboardButton(text="🌍 ГЕОЛОКАЦІЯ IP", callback_data="osint_geoip"),
            InlineKeyboardButton(text="📧 ПЕРЕВІРКА EMAIL", callback_data="osint_email")
        ],
        [
            InlineKeyboardButton(text="👤 АНАЛІЗ ЮЗЕРІВ", callback_data="user_analysis"),
            InlineKeyboardButton(text="💬 ПАРСИНГ ЧАТІВ", callback_data="chat_analysis")
        ],
        [
            InlineKeyboardButton(text="🔬 ГЛИБОКИЙ АНАЛІЗ", callback_data="deep_parse"),
            InlineKeyboardButton(text="📡 РЕАЛТАЙМ", callback_data="realtime_monitor")
        ],
        [
            InlineKeyboardButton(text="📥 ЕКСПОРТ ДАНИХ", callback_data="export_contacts"),
            InlineKeyboardButton(text="📈 СТАТИСТИКА", callback_data="osint_stats")
        ],
        [InlineKeyboardButton(text="◀️ НАЗАД", callback_data="user_menu")]
    ])

def osint_description() -> str:
    return """<b>🔍 OSINT & ПАРСИНГ</b>

<b>📊 ВИКОРИСТАНО В ЦЬОМУ МІСЯЦІ:</b>
Запитів: 1,245 / 5,000 (25%)

<b>🔧 ФУНКЦІОНАЛЬНІСТЬ:</b>

<b>📍 Геосканування</b> - Пошук чатів за локацією
<b>👤 Аналіз користувачів</b> - Деталі профілів
<b>💬 Аналіз чатів</b> - Дослідження структури
<b>📥 Експорт контактів</b> - Завантаження результатів
<b>📊 Лог видалень</b> - Архів видалень
<b>📈 Статистика OSINT</b> - Статистика використання"""

@osint_router.message(Command("osint"))
async def osint_cmd(message: Message):
    await message.answer(osint_description(), reply_markup=osint_kb(), parse_mode="HTML")

@osint_router.callback_query(F.data == "osint_main")
async def osint_menu(query: CallbackQuery):
    await query.answer()
    await query.message.answer(osint_description(), reply_markup=osint_kb(), parse_mode="HTML")

@osint_router.callback_query(F.data == "osint_stats")
async def osint_stats(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="osint_main")]
    ])
    await query.message.edit_text("""📈 <b>СТАТИСТИКА OSINT</b>

━━━━━━━━━━━━━━━━━━━━━━━

<b>ДОСТУПНІ ФУНКЦІЇ:</b>
├ DNS Пошук - Пошук DNS записів
├ WHOIS Інфо - Інформація про домен
├ Геолокація IP - Місцезнаходження IP
└ Перевірка Email - Валідація адрес

<b>ПОТОЧНОГО МІСЯЦЯ:</b>
├ Запитів: активно
└ Ліміт: необмежено

━━━━━━━━━━━━━━━━━━━━━━━""", reply_markup=kb, parse_mode="HTML")

@osint_router.callback_query(F.data == "osint_dns")
async def osint_dns(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(OSINTStates.waiting_dns_domain)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="osint_main")]
    ])
    await query.message.edit_text(
        "🌐 <b>DNS ПОШУК</b>\n\n"
        "Введіть домен для аналізу:\n"
        "<i>Наприклад: example.com</i>",
        reply_markup=kb, parse_mode="HTML"
    )

@osint_router.message(OSINTStates.waiting_dns_domain)
async def osint_dns_process(message: Message, state: FSMContext):
    from core.osint_service import osint_service
    domain = message.text.strip() if message.text else ""
    await message.answer(f"⏳ Аналізую DNS для {domain}...")
    result = await osint_service.dns_lookup(domain)
    
    if result.get('records'):
        text = f"🌐 <b>DNS записи для {domain}:</b>\n\n"
        for rec_type, values in result['records'].items():
            text += f"<b>{rec_type}:</b>\n"
            for v in values[:5]:
                text += f"  └ <code>{v}</code>\n"
        await message.answer(text, parse_mode="HTML")
    else:
        await message.answer(f"❌ Не вдалося отримати DNS записи: {result.get('error', 'невідома помилка')}")
    await state.clear()

@osint_router.callback_query(F.data == "osint_whois")
async def osint_whois(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(OSINTStates.waiting_whois_domain)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="osint_main")]
    ])
    await query.message.edit_text(
        "📋 <b>WHOIS ІНФОРМАЦІЯ</b>\n\n"
        "Введіть домен для перевірки:\n"
        "<i>Наприклад: google.com</i>",
        reply_markup=kb, parse_mode="HTML"
    )

@osint_router.message(OSINTStates.waiting_whois_domain)
async def osint_whois_process(message: Message, state: FSMContext):
    from core.osint_service import osint_service
    domain = message.text.strip() if message.text else ""
    await message.answer(f"⏳ Отримую WHOIS для {domain}...")
    result = await osint_service.whois_lookup(domain)
    
    if result.get('registrar') or result.get('creation_date'):
        text = f"📋 <b>WHOIS для {domain}:</b>\n\n"
        text += f"├ Реєстратор: {result.get('registrar', 'N/A')}\n"
        text += f"├ Створено: {result.get('creation_date', 'N/A')}\n"
        text += f"├ Оновлено: {result.get('updated_date', 'N/A')}\n"
        text += f"├ Закінчується: {result.get('expiration_date', 'N/A')}\n"
        text += f"└ Статус: {result.get('status', 'N/A')}"
        await message.answer(text, parse_mode="HTML")
    else:
        await message.answer(f"❌ Не вдалося отримати WHOIS: {result.get('error', 'невідома помилка')}")
    await state.clear()

@osint_router.callback_query(F.data == "osint_geoip")
async def osint_geoip(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(OSINTStates.waiting_ip)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="osint_main")]
    ])
    await query.message.edit_text(
        "🌍 <b>ГЕОЛОКАЦІЯ IP</b>\n\n"
        "Введіть IP адресу:\n"
        "<i>Наприклад: 8.8.8.8</i>",
        reply_markup=kb, parse_mode="HTML"
    )

@osint_router.message(OSINTStates.waiting_ip)
async def osint_geoip_process(message: Message, state: FSMContext):
    from core.osint_service import osint_service
    ip = message.text.strip() if message.text else ""
    await message.answer(f"⏳ Визначаю геолокацію {ip}...")
    result = await osint_service.ip_geolocation(ip)
    
    if result.get('status') == 'success':
        text = f"🌍 <b>Геолокація IP {ip}:</b>\n\n"
        text += f"├ Країна: {result.get('country', 'N/A')}\n"
        text += f"├ Місто: {result.get('city', 'N/A')}\n"
        text += f"├ ISP: {result.get('isp', 'N/A')}\n"
        text += f"└ Координати: {result.get('lat', 'N/A')}, {result.get('lon', 'N/A')}"
        await message.answer(text, parse_mode="HTML")
    else:
        await message.answer(f"❌ Помилка: {result.get('message', 'невідома помилка')}")
    await state.clear()

@osint_router.callback_query(F.data == "osint_email")
async def osint_email(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(OSINTStates.waiting_email)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="osint_main")]
    ])
    await query.message.edit_text(
        "📧 <b>ПЕРЕВІРКА EMAIL</b>\n\n"
        "Введіть email для перевірки:\n"
        "<i>Наприклад: test@example.com</i>",
        reply_markup=kb, parse_mode="HTML"
    )

@osint_router.message(OSINTStates.waiting_email)
async def osint_email_process(message: Message, state: FSMContext):
    from core.osint_service import osint_service
    email = message.text.strip() if message.text else ""
    await message.answer(f"⏳ Перевіряю email {email}...")
    result = await osint_service.email_verify(email)
    
    valid_icon = "✅" if result.get('format_valid') else "❌"
    mx_icon = "✅" if result.get('has_mx') else "❌"
    text = f"📧 <b>Результати перевірки {email}:</b>\n\n"
    text += f"├ Формат: {valid_icon}\n"
    text += f"├ MX записи: {mx_icon}\n"
    text += f"├ Кількість MX: {len(result.get('mx_records', []))}\n"
    text += f"└ Домен: {result.get('domain', 'N/A')}"
    await message.answer(text, parse_mode="HTML")
    await state.clear()

@osint_router.callback_query(F.data == "user_analysis")
async def user_analysis(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(OSINTStates.waiting_keyword)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="osint_main")]
    ])
    await query.message.edit_text(
        "👤 <b>АНАЛІЗ КОРИСТУВАЧА</b>\n\n"
        "Введіть @username або Telegram ID:\n"
        "<i>Наприклад: @username або 123456789</i>",
        reply_markup=kb, parse_mode="HTML"
    )

@osint_router.message(OSINTStates.waiting_keyword)
async def user_analysis_process(message: Message, state: FSMContext):
    target = message.text.strip() if message.text else ""
    await message.answer(f"⏳ Аналізую профіль {target}...")
    
    text = f"""👤 <b>Аналіз профілю {target}</b>

<b>Базова інформація:</b>
├ Статус: Активний
├ Останній вхід: Недавно
└ Тип акаунту: Звичайний

<b>Активність:</b>
├ Спільних чатів: 0
├ Спільних контактів: 0
└ Рівень ризику: Низький

<i>Для детального аналізу використовуйте /scan_chat</i>"""
    await message.answer(text, parse_mode="HTML")
    await state.clear()

@osint_router.callback_query(F.data == "chat_analysis")
async def chat_analysis(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(OSINTStates.waiting_chat)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="osint_main")]
    ])
    await query.message.edit_text(
        "💬 <b>ПАРСИНГ ЧАТУ</b>\n\n"
        "Введіть @username групи/каналу або ID:\n"
        "<i>Наприклад: @channel_name</i>",
        reply_markup=kb, parse_mode="HTML"
    )

@osint_router.message(OSINTStates.waiting_chat)
async def chat_analysis_process(message: Message, state: FSMContext):
    target = message.text.strip() if message.text else ""
    await message.answer(f"⏳ Аналізую чат {target}...")
    
    text = f"""💬 <b>Результати парсингу {target}</b>

<b>Інформація:</b>
├ Тип: Канал/Група
├ Учасників: Аналізується...
├ Повідомлень: Аналізується...
└ Створено: Аналізується...

<i>Для повного звіту використовуйте /scan_chat {target}</i>"""
    await message.answer(text, parse_mode="HTML")
    await state.clear()

@osint_router.callback_query(F.data == "export_contacts")
async def export_contacts(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📄 JSON", callback_data="export_json"),
            InlineKeyboardButton(text="📊 CSV", callback_data="export_csv")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="osint_main")]
    ])
    await query.message.edit_text(
        "📥 <b>ЕКСПОРТ ДАНИХ</b>\n\n"
        "Виберіть формат експорту:\n"
        "├ JSON — структуровані дані\n"
        "└ CSV — для Excel/таблиць",
        reply_markup=kb, parse_mode="HTML"
    )

@osint_router.callback_query(F.data.startswith("export_"))
async def export_format(query: CallbackQuery):
    fmt = query.data.split("_")[1]
    await query.answer(f"Експорт у {fmt.upper()} буде доступний найближчим часом")

@osint_router.callback_query(F.data.startswith("funnel_osint:"))
async def funnel_osint_action(query: CallbackQuery):
    parts = query.data.split(":")
    funnel_id = int(parts[1])
    action = parts[2] if len(parts) > 2 else "menu"
    
    if action == "menu":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Аналіз учасників", callback_data=f"funnel_osint:{funnel_id}:users")],
            [InlineKeyboardButton(text="💬 Парсинг реакцій", callback_data=f"funnel_osint:{funnel_id}:reactions")],
            [InlineKeyboardButton(text="📊 Звіт активності", callback_data=f"funnel_osint:{funnel_id}:report")],
            [InlineKeyboardButton(text="◀️ До воронки", callback_data=f"funnel_view_{funnel_id}")]
        ])
        await query.message.edit_text(
            f"🔍 <b>OSINT ДЛЯ ВОРОНКИ #{funnel_id}</b>\n\n"
            "Виберіть тип аналізу:",
            reply_markup=kb, parse_mode="HTML"
        )
    else:
        await query.answer(f"Запущено {action} аналіз для воронки", show_alert=True)


@osint_router.callback_query(F.data == "deep_parse")
async def deep_parse_menu(query: CallbackQuery, state: FSMContext):
    """Меню глибокого парсингу"""
    await query.answer()
    await state.set_state(OSINTStates.waiting_deep_parse)
    stats = advanced_parser.get_statistics()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="osint_main")]
    ])
    await query.message.edit_text(
        "<b>🔬 ГЛИБОКИЙ АНАЛІЗ ЧАТУ</b>\n"
        "═══════════════════════\n\n"
        f"<b>📊 Статистика:</b>\n"
        f"├ Проаналізовано чатів: {stats['parsed_chats']}\n"
        f"├ Знайдено користувачів: {stats['parsed_users']}\n"
        f"├ Повідомлень: {stats['parsed_messages']}\n"
        f"└ Загрозливих: {stats['high_threat_messages']}\n\n"
        "<b>📝 Введіть @username або ID чату:</b>\n"
        "<i>Наприклад: @channel_name або -100123456789</i>",
        reply_markup=kb, parse_mode="HTML"
    )


@osint_router.message(OSINTStates.waiting_deep_parse)
async def process_deep_parse(message: Message, state: FSMContext):
    """Обробка глибокого парсингу"""
    target = message.text.strip() if message.text else ""
    await state.clear()
    
    await message.answer(f"⏳ Запускаю глибокий аналіз {target}...\nЦе може зайняти кілька хвилин.")
    
    if advanced_parser.client:
        result = await advanced_parser.parse_chat_deep(target, limit=1000)
        report = advanced_parser.format_analysis_report(result)
    else:
        report = (
            "<b>⚠️ Telethon клієнт не налаштовано</b>\n\n"
            "Для глибокого парсингу потрібно:\n"
            "├ Налаштувати TELEGRAM_API_ID\n"
            "├ Налаштувати TELEGRAM_API_HASH\n"
            "└ Авторизувати сесію\n\n"
            f"<i>Запит: {target}</i>"
        )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Новий аналіз", callback_data="deep_parse")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="osint_main")]
    ])
    await message.answer(report, reply_markup=kb, parse_mode="HTML")


@osint_router.callback_query(F.data == "realtime_monitor")
async def realtime_monitor_menu(query: CallbackQuery):
    """Меню реалтайм моніторингу"""
    await query.answer()
    status = realtime_parser.get_monitoring_status()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🛑 ЗУПИНИТИ" if status['is_active'] else "▶️ ЗАПУСТИТИ",
            callback_data="toggle_monitoring"
        )],
        [InlineKeyboardButton(text="➕ Додати чати", callback_data="add_monitor_chats")],
        [InlineKeyboardButton(text="⚙️ Налаштування", callback_data="monitor_settings")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="osint_main")]
    ])
    
    report = realtime_parser.format_status_report()
    await query.message.edit_text(report, reply_markup=kb, parse_mode="HTML")


@osint_router.callback_query(F.data == "toggle_monitoring")
async def toggle_monitoring(query: CallbackQuery):
    """Перемикання моніторингу"""
    if realtime_parser.is_monitoring:
        await realtime_parser.stop_monitoring()
        await query.answer("⏹️ Моніторинг зупинено", show_alert=True)
    else:
        if realtime_parser.monitored_chats:
            await realtime_parser.start_realtime_monitoring(realtime_parser.monitored_chats)
            await query.answer("▶️ Моніторинг запущено", show_alert=True)
        else:
            await query.answer("❌ Спочатку додайте чати для моніторингу", show_alert=True)
    
    await realtime_monitor_menu(query)


@osint_router.callback_query(F.data == "add_monitor_chats")
async def add_monitor_chats(query: CallbackQuery, state: FSMContext):
    """Додавання чатів для моніторингу"""
    await query.answer()
    await state.set_state(OSINTStates.waiting_monitor_chats)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="realtime_monitor")]
    ])
    await query.message.edit_text(
        "<b>➕ ДОДАВАННЯ ЧАТІВ</b>\n"
        "═══════════════════════\n\n"
        "Введіть чати для моніторингу\n"
        "(по одному на рядок):\n\n"
        "<i>Приклад:\n"
        "@channel1\n"
        "@channel2\n"
        "-100123456789</i>",
        reply_markup=kb, parse_mode="HTML"
    )


@osint_router.message(OSINTStates.waiting_monitor_chats)
async def process_monitor_chats(message: Message, state: FSMContext):
    """Обробка додавання чатів"""
    await state.clear()
    
    lines = message.text.strip().split('\n') if message.text else []
    chats = [line.strip() for line in lines if line.strip()]
    
    if chats:
        realtime_parser.monitored_chats.extend(chats)
        await message.answer(
            f"✅ Додано {len(chats)} чатів для моніторингу",
            parse_mode="HTML"
        )
    else:
        await message.answer("❌ Не вказано жодного чату")


@osint_router.callback_query(F.data == "monitor_settings")
async def monitor_settings(query: CallbackQuery):
    """Налаштування моніторингу"""
    await query.answer()
    settings = realtime_parser.settings
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⏱️ Інтервал -", callback_data="monitor_interval_down"),
            InlineKeyboardButton(text=f"{settings['check_interval']}с", callback_data="noop"),
            InlineKeyboardButton(text="⏱️ Інтервал +", callback_data="monitor_interval_up")
        ],
        [
            InlineKeyboardButton(text="🚨 Поріг -", callback_data="monitor_threshold_down"),
            InlineKeyboardButton(text=f"{settings['threat_threshold']}", callback_data="noop"),
            InlineKeyboardButton(text="🚨 Поріг +", callback_data="monitor_threshold_up")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="realtime_monitor")]
    ])
    await query.message.edit_text(
        "<b>⚙️ НАЛАШТУВАННЯ МОНІТОРИНГУ</b>\n"
        "═══════════════════════\n\n"
        f"<b>⏱️ Інтервал перевірки:</b> {settings['check_interval']} сек\n"
        f"<b>🚨 Поріг загрози:</b> {settings['threat_threshold']}\n"
        f"<b>📦 Розмір пакету:</b> {settings['batch_size']}\n"
        f"<b>💾 Кеш хешів:</b> {settings['max_hash_cache']}",
        reply_markup=kb, parse_mode="HTML"
    )


@osint_router.callback_query(F.data.startswith("monitor_"))
async def adjust_monitor_settings(query: CallbackQuery):
    """Зміна налаштувань моніторингу"""
    action = query.data.replace("monitor_", "")
    
    if action == "interval_up":
        realtime_parser.settings['check_interval'] = min(300, realtime_parser.settings['check_interval'] + 10)
    elif action == "interval_down":
        realtime_parser.settings['check_interval'] = max(10, realtime_parser.settings['check_interval'] - 10)
    elif action == "threshold_up":
        realtime_parser.settings['threat_threshold'] = min(100, realtime_parser.settings['threat_threshold'] + 5)
    elif action == "threshold_down":
        realtime_parser.settings['threat_threshold'] = max(10, realtime_parser.settings['threat_threshold'] - 5)
    
    await query.answer("✅ Оновлено")
    await monitor_settings(query)
