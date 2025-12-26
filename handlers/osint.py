from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

osint_router = Router()

class OSINTStates(StatesGroup):
    waiting_keyword = State()
    waiting_chat = State()

def osint_kb():
    """Комбіновано OSINT меню - 1/2/3 кнопки на рядок"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📍 Геосканування", callback_data="geo_scan"),
            InlineKeyboardButton(text="👤 Аналіз користувачів", callback_data="user_analysis")
        ],
        [
            InlineKeyboardButton(text="💬 Аналіз чатів", callback_data="chat_analysis"),
            InlineKeyboardButton(text="📥 Експорт контактів", callback_data="export_contacts")
        ],
        [
            InlineKeyboardButton(text="📊 Лог видалень", callback_data="deletion_log")
        ],
        [
            InlineKeyboardButton(text="📈 Статистика OSINT", callback_data="osint_stats")
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

<b>ПОТОЧНОГО МІСЯЦЯ:</b>
Запитів: 1,245 / 5,000 (25%)
Контактів: 45,230
Чатів: 156
Користувачів: 5,234

<b>ГРАФІК ВИКОРИСТАННЯ:</b>
▬▬░░░░░░░░ 25% від квоти

<b>ВИТРАТИ:</b>
Геосканування: 340 запитів - 8 кредитів
Аналіз користувачів: 245 запитів - 12 кредитів
Аналіз чатів: 156 запитів - 6 кредитів
Експорт: 34 експорти - 3 кредити
────────────────────────
Всього: 30 кредитів / 200 кредитів (15%)

<b>РЕКОМЕНДАЦІЯ:</b>
✓ Ви в межах ліміту
✓ Подумайте про Premium для більшої квоти""", reply_markup=kb, parse_mode="HTML")

