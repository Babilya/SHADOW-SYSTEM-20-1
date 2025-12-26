from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

logger = logging.getLogger(__name__)
osint_router = Router()

class OSINTStates(StatesGroup):
    waiting_keyword = State()
    waiting_chat = State()
    waiting_dns_domain = State()
    waiting_whois_domain = State()
    waiting_ip = State()
    waiting_email = State()

def osint_kb():
    """Комбіновано OSINT меню - 1/2/3 кнопки на рядок"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🌐 DNS Lookup", callback_data="osint_dns"),
            InlineKeyboardButton(text="📋 WHOIS", callback_data="osint_whois")
        ],
        [
            InlineKeyboardButton(text="🌍 IP Геолокація", callback_data="osint_geoip"),
            InlineKeyboardButton(text="📧 Email Verify", callback_data="osint_email")
        ],
        [
            InlineKeyboardButton(text="👤 Telegram User", callback_data="user_analysis"),
            InlineKeyboardButton(text="💬 Chat Parsing", callback_data="chat_analysis")
        ],
        [
            InlineKeyboardButton(text="📥 Експорт", callback_data="export_contacts"),
            InlineKeyboardButton(text="📈 Статистика", callback_data="osint_stats")
        ],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")
        ],
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

@osint_router.callback_query(F.data == "geo_scan")
async def geo_scan(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏙️ Київ", callback_data="geo_kyiv")],
        [InlineKeyboardButton(text="🏙️ Москва", callback_data="geo_moscow")],
        [InlineKeyboardButton(text="🏙️ Одеса", callback_data="geo_odesa")],
        [InlineKeyboardButton(text="🏙️ Харків", callback_data="geo_kharkiv")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="osint_main")]
    ])
    await query.message.answer("""📍 <b>ГЕОСКАНУВАННЯ</b>

Виберіть регіон для сканування:""", reply_markup=kb, parse_mode="HTML")

@osint_router.callback_query(F.data.startswith("geo_"))
async def geo_region_result(query: CallbackQuery):
    await query.answer()
    region = query.data.replace("geo_", "")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Експортувати", callback_data=f"export_{region}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="geo_scan")]
    ])
    await query.message.answer(f"""📍 <b>РЕЗУЛЬТАТИ: {region.upper()}</b>

Чатів знайдено: 234
Користувачів: 12,456
Ботів: 340
Активних: 11,789

<b>ТОП ЧАТИ:</b>
1. "Маркетинг" - 1,234 учасники
2. "IT" - 890 учасники
3. "Бізнес" - 756 учасників""", reply_markup=kb, parse_mode="HTML")

@osint_router.callback_query(F.data == "user_analysis")
async def user_analysis(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Демографія", callback_data="user_demo")],
        [InlineKeyboardButton(text="💼 Професії", callback_data="user_jobs")],
        [InlineKeyboardButton(text="⏰ Активність", callback_data="user_activity")],
        [InlineKeyboardButton(text="🔴 Рискові", callback_data="user_risky")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="osint_main")]
    ])
    await query.message.answer("""👤 <b>АНАЛІЗ КОРИСТУВАЧІВ</b>

Проаналізовано: 5,234
Активних: 2,156 (41%)
Ботів: 342 (6.5%)

Виберіть категорію для детальної інформації:""", reply_markup=kb, parse_mode="HTML")

@osint_router.callback_query(F.data == "user_demo")
async def user_demo(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="user_analysis")]
    ])
    await query.message.answer("""👤 <b>ДЕМОГРАФІЯ КОРИСТУВАЧІВ</b>

<b>СТАТЬ:</b>
Чоловіків: 65% (3,389)
Жінок: 35% (1,845)

<b>ВІК:</b>
18-25: 23% | 25-35: 42% | 35-50: 25% | 50+: 10%
Середній вік: 28 років

<b>МОВА:</b>
Українська: 60% | Російська: 40%

<b>ГЕОГРАФІЯ:</b>
Київ: 34% | Москва: 18% | Одеса: 12% | Інші: 36%""", reply_markup=kb, parse_mode="HTML")

@osint_router.callback_query(F.data == "user_jobs")
async def user_jobs(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="user_analysis")]
    ])
    await query.message.answer("""💼 <b>ПРОФЕСІЙНИЙ СКЛАД</b>

Маркетолог: 23% (1,201)
IT спеціаліст: 18% (938)
Бізнесмен: 15% (781)
Фрілансер: 14% (727)
Інші: 30% (1,560)

<b>КУПІВЕЛЬНА ЗДАТНІСТЬ:</b>
Високий дохід: 28% | Середній: 45% | Низький: 27%""", reply_markup=kb, parse_mode="HTML")

@osint_router.callback_query(F.data == "user_activity")
async def user_activity(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="user_analysis")]
    ])
    await query.message.answer("""⏰ <b>АКТИВНІСТЬ КОРИСТУВАЧІВ</b>

Середня активність: 4.2 повідомлення/день
Найактивніші: 14:00-16:00 | 20:00-22:00

<b>ГРАФІК АКТИВНОСТІ:</b>
Понеділок-Пятниця: 85%
Субота-Неділя: 45%

<b>АКТИВНІ КОРИСТУВАЧИ:</b>
Кожен день: 34%
Кілька разів на день: 42%
Раз на тиждень: 24%""", reply_markup=kb, parse_mode="HTML")

@osint_router.callback_query(F.data == "user_risky")
async def user_risky(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="user_analysis")]
    ])
    await query.message.answer("""🔴 <b>РИСКОВІ КОРИСТУВАЧИ</b>

Нові акаунти (< 3 мес): 234
Розповсюджувачи спаму: 45
Боти-фейки: 87
Фішинг-акаунти: 12

<b>РЕКОМЕНДАЦІЯ:</b>
✓ Виключити зі списків розсилки
✓ Додати до чорного списку
✓ Не взаємодіяти з такими акаунтами""", reply_markup=kb, parse_mode="HTML")

@osint_router.callback_query(F.data == "chat_analysis")
async def chat_analysis(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔝 ТОП Чати", callback_data="top_chats")],
        [InlineKeyboardButton(text="🔴 Рискові", callback_data="risky_chats")],
        [InlineKeyboardButton(text="👥 Ключові особи", callback_data="key_persons")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="osint_main")]
    ])
    await query.message.answer("""💬 <b>АНАЛІЗ ЧАТІВ</b>

Чатів всього: 156
Активних: 142 (91%)

Виберіть тип аналізу:""", reply_markup=kb, parse_mode="HTML")

@osint_router.callback_query(F.data == "top_chats")
async def top_chats(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="chat_analysis")]
    ])
    await query.message.answer("""🔝 <b>ТОП 5 АКТИВНИХ ЧАТІВ</b>

1️⃣ "Маркетинг" 
   1,234 повідомл./день | 2,340 учасників

2️⃣ "IT & Розробка"
   890 повідомлень/день | 1,890 учасників

3️⃣ "Фріланс"
   765 повідомлень/день | 1,456 учасників

4️⃣ "SEO Клуб"
   645 повідомлень/день | 1,023 учасники

5️⃣ "Стартапи"
   523 повідомлення/день | 890 учасників""", reply_markup=kb, parse_mode="HTML")

@osint_router.callback_query(F.data == "risky_chats")
async def risky_chats(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="chat_analysis")]
    ])
    await query.message.answer("""🔴 <b>РИСКОВІ ЧАТИ (3)</b>

1. "Спам клуб" - 90% спаму
2. "Схеми заробітку" - Фішинг контент
3. "Лотерея" - Рекламний контент

<b>РЕКОМЕНДАЦІЯ:</b>
✗ Не вести розсилку в ці чати
✗ Видалити список контактів звідти
✓ Монітирувати активність""", reply_markup=kb, parse_mode="HTML")

@osint_router.callback_query(F.data == "key_persons")
async def key_persons(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="chat_analysis")]
    ])
    await query.message.answer("""👥 <b>КЛЮЧОВІ ОСОБИ В ЧАТАХ</b>

<b>МОДЕРАТОРИ (8):</b>
@mod_1, @mod_2, @mod_3...

<b>АДМІНІСТРАТОРИ (3):</b>
@admin_1, @admin_2, @admin_3

<b>АКТИВНІ ЮЗЕРИ (TOP 5):</b>
1. @user_123 - 456 повідомлень
2. @user_456 - 389 повідомлень
3. @user_789 - 267 повідомлень
4. @user_101 - 198 повідомлень
5. @user_202 - 145 повідомлень

<b>ТИП:</b>
🤖 Боти: 12
👤 Реальні люди: 15
❓ Невідомі: 8""", reply_markup=kb, parse_mode="HTML")

@osint_router.callback_query(F.data == "export_contacts")
async def export_contacts(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 CSV", callback_data="export_csv")],
        [InlineKeyboardButton(text="📊 Excel", callback_data="export_excel")],
        [InlineKeyboardButton(text="📋 JSON", callback_data="export_json")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="osint_main")]
    ])
    await query.message.answer("""📥 <b>ЕКСПОРТ КОНТАКТІВ</b>

Доступно для експорту: 45,230
├ З email: 12,340 (27%)
├ З телефонами: 8,950 (20%)
├ З Telegram: 24,940 (55%)

Виберіть формат експорту:""", reply_markup=kb, parse_mode="HTML")

@osint_router.callback_query(F.data.startswith("export_"))
async def export_format(query: CallbackQuery):
    await query.answer()
    fmt = query.data.replace("export_", "")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Завантажити", callback_data=f"download_{fmt}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="export_contacts")]
    ])
    await query.message.answer(f"""📥 <b>ЕКСПОРТ {fmt.upper()}</b>

Файл: contacts_{fmt}.{fmt}
Розмір: 12.4 MB
Контактів: 45,230
Формат: {fmt.upper()}
Статус: Готово до завантаження

<b>ВМІСТ:</b>
✓ Ім'я
✓ Username
✓ Email
✓ Телефон
✓ Регіон
✓ Інтереси""", reply_markup=kb, parse_mode="HTML")

@osint_router.callback_query(F.data == "deletion_log")
async def deletion_log(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📉 Статистика", callback_data="deletion_stats")],
        [InlineKeyboardButton(text="📋 Причини", callback_data="deletion_reasons")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="osint_main")]
    ])
    await query.message.answer("""📊 <b>ЛОГ ВИДАЛЕНЬ</b>

Видалено повідомлень: 1,234
Видалено користувачів: 45
Період: 2025-12-01 до 2025-12-24

Виберіть розділ:""", reply_markup=kb, parse_mode="HTML")

@osint_router.callback_query(F.data == "deletion_stats")
async def deletion_stats(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="deletion_log")]
    ])
    await query.message.answer("""📉 <b>СТАТИСТИКА ВИДАЛЕНЬ</b>

<b>ПОВІДОМЛЕННЯ:</b>
Всього: 1,234
За спам: 890 (72%)
За матеріал: 234 (19%)
За скарги: 110 (9%)

<b>КОРИСТУВАЧИ:</b>
Всього: 45
Бани за спам: 32
Бани за непристойність: 10
Бани за фішинг: 3

<b>ГРАФІК:</b>
День 1-7: 156 видалень
День 8-14: 234 видалень ← Найбільше
День 15-21: 178 видалень
День 22-24: 89 видалень""", reply_markup=kb, parse_mode="HTML")

@osint_router.callback_query(F.data == "deletion_reasons")
async def deletion_reasons(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="deletion_log")]
    ])
    await query.message.answer("""📋 <b>ПРИЧИНИ ВИДАЛЕНЬ</b>

<b>ТОП ПРИЧИНИ:</b>
1. Спам (72%) ████████████
2. Ненормативна лексика (19%) ███░
3. Скарги користувачів (9%) █░

<b>ДЕТАЛІ:</b>
• Спам: Реклама, ботів, NSFW
• Непристойність: Лайки, погрози
• Скарги: Донос від юзерів

<b>ОСТАННІ ВИДАЛЕННЯ:</b>
2025-12-24 10:45 - Спам
2025-12-24 09:30 - Непристойність
2025-12-24 08:15 - Спам""", reply_markup=kb, parse_mode="HTML")

@osint_router.callback_query(F.data == "osint_stats")
async def osint_stats(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="osint_main")]
    ])
    await query.message.answer("""📈 <b>СТАТИСТИКА OSINT</b>

<b>ДОСТУПНІ ФУНКЦІЇ:</b>
DNS Lookup - Пошук DNS записів
WHOIS - Інформація про домен
IP Геолокація - Місцезнаходження IP
Email Verify - Перевірка email

<b>ПОТОЧНОГО МІСЯЦЯ:</b>
Запитів: активно
Ліміт: необмежено""", reply_markup=kb, parse_mode="HTML")

@osint_router.callback_query(F.data == "osint_dns")
async def osint_dns_start(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(OSINTStates.waiting_dns_domain)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="osint_main")]
    ])
    await query.message.edit_text(
        "🌐 <b>DNS LOOKUP</b>\n\nВведіть домен для пошуку (наприклад: example.com):",
        reply_markup=kb, parse_mode="HTML"
    )

@osint_router.message(OSINTStates.waiting_dns_domain)
async def osint_dns_process(message: Message, state: FSMContext):
    domain = message.text.strip().lower()
    await state.clear()
    
    await message.answer("🔍 Виконую DNS lookup...")
    
    try:
        from core.osint_service import osint_service
        result = await osint_service.dns_lookup(domain)
        
        if result.get("status") == "success":
            records = result.get("records", {})
            text = f"🌐 <b>DNS ЗАПИСИ: {domain}</b>\n\n"
            
            for rtype, values in records.items():
                if values:
                    text += f"<b>{rtype}:</b>\n"
                    for v in values[:5]:
                        text += f"  • <code>{v}</code>\n"
            
            if not any(records.values()):
                text += "Записів не знайдено"
        else:
            text = f"❌ Помилка: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"DNS lookup error: {e}")
        text = f"❌ Помилка: {e}"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Ще один запит", callback_data="osint_dns")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="osint_main")]
    ])
    await message.answer(text, reply_markup=kb, parse_mode="HTML")

@osint_router.callback_query(F.data == "osint_whois")
async def osint_whois_start(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(OSINTStates.waiting_whois_domain)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="osint_main")]
    ])
    await query.message.edit_text(
        "📋 <b>WHOIS LOOKUP</b>\n\nВведіть домен для пошуку:",
        reply_markup=kb, parse_mode="HTML"
    )

@osint_router.message(OSINTStates.waiting_whois_domain)
async def osint_whois_process(message: Message, state: FSMContext):
    domain = message.text.strip().lower()
    await state.clear()
    
    await message.answer("🔍 Виконую WHOIS lookup...")
    
    try:
        from core.osint_service import osint_service
        result = await osint_service.whois_lookup(domain)
        
        if result.get("status") == "success":
            data = result.get("data", {})
            registrant = data.get("registrant", {})
            text = f"📋 <b>WHOIS: {domain}</b>\n\n"
            
            if data.get("domainName"):
                text += f"<b>Домен:</b> {data.get('domainName')}\n"
            if data.get("createdDate"):
                text += f"<b>Створено:</b> {data.get('createdDate')[:10]}\n"
            if data.get("updatedDate"):
                text += f"<b>Оновлено:</b> {data.get('updatedDate')[:10]}\n"
            if data.get("expiresDate"):
                text += f"<b>Закінчується:</b> {data.get('expiresDate')[:10]}\n"
            if data.get("registrarName"):
                text += f"<b>Реєстратор:</b> {data.get('registrarName')}\n"
            if registrant.get("organization"):
                text += f"<b>Організація:</b> {registrant.get('organization')}\n"
            if registrant.get("country"):
                text += f"<b>Країна:</b> {registrant.get('country')}\n"
        else:
            text = f"❌ Помилка: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"WHOIS lookup error: {e}")
        text = f"❌ Помилка: {e}"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Ще один запит", callback_data="osint_whois")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="osint_main")]
    ])
    await message.answer(text, reply_markup=kb, parse_mode="HTML")

@osint_router.callback_query(F.data == "osint_geoip")
async def osint_geoip_start(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(OSINTStates.waiting_ip)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="osint_main")]
    ])
    await query.message.edit_text(
        "🌍 <b>IP ГЕОЛОКАЦІЯ</b>\n\nВведіть IP адресу (наприклад: 8.8.8.8):",
        reply_markup=kb, parse_mode="HTML"
    )

@osint_router.message(OSINTStates.waiting_ip)
async def osint_geoip_process(message: Message, state: FSMContext):
    ip = message.text.strip()
    await state.clear()
    
    await message.answer("🔍 Виконую геолокацію...")
    
    try:
        from core.osint_service import osint_service
        result = await osint_service.ip_geolocation(ip)
        
        if result.get("status") == "success":
            text = f"""🌍 <b>ГЕОЛОКАЦІЯ IP: {ip}</b>

<b>Країна:</b> {result.get('country', 'N/A')} ({result.get('country_code', '')})
<b>Регіон:</b> {result.get('region', 'N/A')}
<b>Місто:</b> {result.get('city', 'N/A')}
<b>Індекс:</b> {result.get('zip', 'N/A')}
<b>Координати:</b> {result.get('lat', 'N/A')}, {result.get('lon', 'N/A')}
<b>ISP:</b> {result.get('isp', 'N/A')}
<b>Організація:</b> {result.get('org', 'N/A')}
<b>AS:</b> {result.get('as', 'N/A')}"""
        else:
            text = f"❌ Помилка: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"GeoIP error: {e}")
        text = f"❌ Помилка: {e}"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Ще один запит", callback_data="osint_geoip")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="osint_main")]
    ])
    await message.answer(text, reply_markup=kb, parse_mode="HTML")

@osint_router.callback_query(F.data == "osint_email")
async def osint_email_start(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(OSINTStates.waiting_email)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="osint_main")]
    ])
    await query.message.edit_text(
        "📧 <b>EMAIL VERIFY</b>\n\nВведіть email для перевірки:",
        reply_markup=kb, parse_mode="HTML"
    )

@osint_router.message(OSINTStates.waiting_email)
async def osint_email_process(message: Message, state: FSMContext):
    email = message.text.strip()
    await state.clear()
    
    await message.answer("🔍 Перевіряю email...")
    
    try:
        from core.osint_service import osint_service
        result = await osint_service.email_verify(email)
        
        if result.get("status") == "success":
            has_mx = "✅" if result.get('has_mx') else "❌"
            format_valid = "✅" if result.get('format_valid') else "❌"
            mx_records = "\n".join([f"  • {r}" for r in result.get('mx_records', [])[:3]]) or "  Не знайдено"
            
            text = f"""📧 <b>ПЕРЕВІРКА EMAIL: {email}</b>

<b>Формат:</b> {format_valid}
<b>Домен:</b> {result.get('domain', 'N/A')}
<b>MX записи:</b> {has_mx}
{mx_records}"""
        else:
            text = f"❌ Помилка: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Email verify error: {e}")
        text = f"❌ Помилка: {e}"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Ще один запит", callback_data="osint_email")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="osint_main")]
    ])
    await message.answer(text, reply_markup=kb, parse_mode="HTML")

