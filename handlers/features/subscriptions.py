from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

class ApplicationForm(StatesGroup):
    waiting_duration = State()
    waiting_name = State()
    waiting_purpose = State()
    waiting_contact = State()

PACKAGES = {
    "basic": {
        "name": "БАЗОВИЙ",
        "emoji": "📦",
        "bots_limit": 100,
        "managers_limit": 1,
        "features": [
            "🤖 До 100 ботів",
            "👥 1 менеджер",
            "📧 500 розсилок/день",
            "🔍 Базовий OSINT (50 запитів)",
            "📊 Проста аналітика",
            "💬 Підтримка: Email (24 год)",
        ],
        "modules": ["BOTNET (базовий)", "Розсилки", "Парсинг контактів"],
        "no_access": ["Geo-Intelligence", "AI Sentiment", "Deep Chat Analysis", "Персональний менеджер"]
    },
    "standard": {
        "name": "СТАНДАРТ",
        "emoji": "⭐",
        "bots_limit": 500,
        "managers_limit": 5,
        "features": [
            "🤖 До 500 ботів",
            "👥 5 менеджерів",
            "📧 Необмежені розсилки",
            "🔍 OSINT: 200 запитів/день",
            "📊 Повна аналітика + звіти",
            "🔥 Smart Warmup (стандартний)",
            "💬 Підтримка: Chat (4 год)",
        ],
        "modules": ["BOTNET (повний)", "Campaign Manager", "OSINT базовий", "Proxy Manager", "Health Check"],
        "no_access": ["Geo-Intelligence (обмежено)", "Evidence Exporter", "Персональний менеджер"]
    },
    "premium": {
        "name": "ПРЕМІУМ",
        "emoji": "👑",
        "bots_limit": 5000,
        "managers_limit": 15,
        "features": [
            "🤖 До 5000 ботів",
            "👥 15 менеджерів",
            "📧 Необмежені розсилки",
            "🔍 OSINT: Необмежено",
            "🌍 Geo-Intelligence (50 км)",
            "🧠 AI Sentiment Analysis",
            "📊 Deep Chat Analysis",
            "🔐 Military Grade Encryption",
            "🔥 Smart Warmup (агресивний)",
            "💬 Підтримка: Chat (1 год)",
        ],
        "modules": ["Всі модулі СТАНДАРТ", "Geo-Intelligence", "AI Sentiment", "Deep Chat Analysis", "Evidence Exporter", "Law Enforcement Mode"],
        "no_access": ["Персональний менеджер", "Кастомні модулі"]
    },
    "personal": {
        "name": "ПЕРСОНАЛЬНИЙ",
        "emoji": "💎",
        "bots_limit": 999999,
        "managers_limit": 999,
        "features": [
            "🤖 БЕЗЛІМІТНІ боти",
            "👥 Необмежені менеджери",
            "📧 Необмежені операції",
            "🔍 OSINT: Повний доступ",
            "🌍 Geo-Intelligence: Безліміт",
            "🧠 AI: Всі функції",
            "🔐 AES-256-GCM шифрування",
            "⚖️ Evidence Chain of Custody",
            "🆘 Emergency Kill Switch",
            "👤 Персональний менеджер 24/7",
            "⚙️ Кастомні модулі на замовлення",
        ],
        "modules": ["ВСІ МОДУЛІ СИСТЕМИ", "ROOT Panel доступ", "Кастомна розробка", "Виділений сервер", "Пріоритетні оновлення"],
        "no_access": []
    }
}

def subscriptions_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 БАЗОВИЙ", callback_data="pkg_basic"),
         InlineKeyboardButton(text="⭐ СТАНДАРТ", callback_data="pkg_standard")],
        [InlineKeyboardButton(text="👑 ПРЕМІУМ", callback_data="pkg_premium"),
         InlineKeyboardButton(text="💎 ПЕРСОНАЛЬНИЙ", callback_data="pkg_personal")],
        [InlineKeyboardButton(text="📊 Порівняти", callback_data="pkg_compare"),
         InlineKeyboardButton(text="❓ FAQ", callback_data="subscription_faq"),
         InlineKeyboardButton(text="💬 Допомога", callback_data="subscription_support")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="user_menu")]
    ])

def subscriptions_description() -> str:
    return """<b>📦 ТАРИФНІ ПЛАНИ SHADOW SYSTEM</b>

<b>🎯 Оберіть план для вашого проекту:</b>

<b>📦 БАЗОВИЙ</b>
├ 100 ботів | 1 менеджер
├ Базовий OSINT | Розсилки
└ <i>Для початківців</i>

<b>⭐ СТАНДАРТ</b>
├ 500 ботів | 5 менеджерів
├ Повний OSINT | Campaign Manager
└ <i>Для активних проектів</i>

<b>👑 ПРЕМІУМ</b>
├ 5000 ботів | 15 менеджерів
├ AI Sentiment | Geo-Intelligence
└ <i>Для професіоналів</i>

<b>💎 ПЕРСОНАЛЬНИЙ</b>
├ Безлімітні операції
├ Кастомні модулі | 24/7 підтримка
└ <i>Enterprise рішення</i>

<b>💡 Зверніться до адміністратора для активації ліцензії!</b>"""

def package_detail_kb(pkg_key: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Подати заявку на ключ", callback_data=f"apply_{pkg_key}_30")],
        [InlineKeyboardButton(text="📊 Порівняти", callback_data="pkg_compare"),
         InlineKeyboardButton(text="◀️ Тарифи", callback_data="subscription_main")]
    ])

def package_detail_text(pkg_key: str) -> str:
    pkg = PACKAGES[pkg_key]
    features = "\n".join(pkg["features"])
    modules = " | ".join(pkg["modules"])
    no_access_text = ""
    if pkg["no_access"]:
        no_access_text = "\n\n<b>❌ Недоступно:</b>\n" + "\n".join([f"✗ {x}" for x in pkg["no_access"]])
    
    return f"""{pkg['emoji']} <b>ТАРИФ {pkg['name']}</b>

<b>📊 ЛІМІТИ:</b>
├ Ботів: <b>{pkg['bots_limit'] if pkg['bots_limit'] < 10000 else 'Безліміт'}</b>
├ Менеджерів: <b>{pkg['managers_limit'] if pkg['managers_limit'] < 100 else 'Безліміт'}</b>

<b>✅ МОЖЛИВОСТІ:</b>
{features}

<b>📦 МОДУЛІ:</b>
{modules}{no_access_text}

<b>💡 Зверніться до адміністратора для отримання SHADOW ключа!</b>"""

def compare_packages_text() -> str:
    return """<b>📊 ПОРІВНЯННЯ ТАРИФІВ</b>

<b>┌─────────────┬────────┬─────────┬─────────┬──────────┐</b>
<b>│ Функція     │ 📦 БАЗ │ ⭐ СТД  │ 👑 ПРМ  │ 💎 ПЕРС  │</b>
<b>├─────────────┼────────┼─────────┼─────────┼──────────┤</b>
│ Боти        │  100   │   500   │  5000   │ Безлім   │
│ Менеджери   │   1    │    5    │   15    │ Безлім   │
│ Розсилки    │ 500/д  │ Безлім  │ Безлім  │ Безлім   │
│ OSINT       │  50/д  │  200/д  │ Безлім  │ Безлім   │
│ Geo-Intel   │   ❌   │   🟡    │   ✅    │   ✅     │
│ AI Sentiment│   ❌   │   🟡    │   ✅    │   ✅     │
│ Deep Chat   │   ❌   │   ❌    │   ✅    │   ✅     │
│ Encryption  │ Базове │ Базове  │ Military│ Military │
│ Evidence    │   ❌   │   ❌    │   ✅    │   ✅     │
│ Kill Switch │   ❌   │   ❌    │   ❌    │   ✅     │
│ Персон.мнж  │   ❌   │   ❌    │   ❌    │   ✅     │
<b>└─────────────┴────────┴─────────┴─────────┴──────────┘</b>

<b>🔥 РЕКОМЕНДАЦІЇ:</b>
📦 <b>БАЗОВИЙ</b> — для тестування та малих проектів
⭐ <b>СТАНДАРТ</b> — оптимальний вибір для більшості
👑 <b>ПРЕМІУМ</b> — для професійних операцій
💎 <b>ПЕРСОНАЛЬНИЙ</b> — корпоративні клієнти та LEA"""

@router.message(Command("subscription"))
async def subscription_cmd(message: Message):
    await message.answer(subscriptions_description(), reply_markup=subscriptions_kb(), parse_mode="HTML")

@router.callback_query(F.data == "subscription_main")
async def subscription_menu(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text(subscriptions_description(), reply_markup=subscriptions_kb(), parse_mode="HTML")

@router.callback_query(F.data == "pkg_compare")
async def pkg_compare(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 БАЗОВИЙ", callback_data="pkg_basic"),
         InlineKeyboardButton(text="⭐ СТАНДАРТ", callback_data="pkg_standard")],
        [InlineKeyboardButton(text="👑 ПРЕМІУМ", callback_data="pkg_premium"),
         InlineKeyboardButton(text="💎 ПЕРСОНАЛЬНИЙ", callback_data="pkg_personal")],
        [InlineKeyboardButton(text="◀️ До тарифів", callback_data="subscription_main")]
    ])
    await query.message.edit_text(compare_packages_text(), reply_markup=kb, parse_mode="HTML")

@router.callback_query(F.data.startswith("pkg_"))
async def package_detail(query: CallbackQuery):
    pkg_key = query.data.replace("pkg_", "")
    if pkg_key not in PACKAGES:
        await query.answer("Тариф не знайдено")
        return
    
    await query.answer()
    await query.message.edit_text(
        package_detail_text(pkg_key), 
        reply_markup=package_detail_kb(pkg_key), 
        parse_mode="HTML"
    )

@router.callback_query(F.data == "subscription_faq")
async def subscription_faq(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="subscription_main")]
    ])
    await query.message.edit_text(
        """<b>❓ ЧАСТІ ПИТАННЯ</b>

<b>Q: Як активувати ключ?</b>
A: Введіть /activate SHADOW-XXXX-XXXX

<b>Q: Чи можна змінити тариф?</b>
A: Так, зверніться до адміністратора

<b>Q: Що буде після закінчення підписки?</b>
A: Доступ буде обмежено до Guest

<b>Q: Як отримати ключ?</b>
A: Надішліть заявку в розділі тарифів""",
        reply_markup=kb, parse_mode="HTML"
    )

@router.callback_query(F.data == "subscription_support")
async def subscription_support(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Написати", url="https://t.me/shadow_support")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="subscription_main")]
    ])
    await query.message.edit_text(
        """<b>💬 ПІДТРИМКА</b>

<b>📧 Email:</b> support@shadowsystem.io
<b>💬 Telegram:</b> @shadow_support

<b>⏰ Час відповіді:</b>
├ 📦 БАЗОВИЙ: до 24 годин
├ ⭐ СТАНДАРТ: до 4 годин
├ 👑 ПРЕМІУМ: до 1 години
└ 💎 ПЕРСОНАЛЬНИЙ: миттєво (24/7)""",
        reply_markup=kb, parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("apply_"))
async def apply_package(query: CallbackQuery, state: FSMContext):
    parts = query.data.split("_")
    pkg_key = parts[1]
    
    if pkg_key not in PACKAGES:
        await query.answer("Тариф не знайдено")
        return
    
    pkg = PACKAGES[pkg_key]
    await state.update_data(
        selected_package=pkg_key, 
        package_name=pkg.get('name', ''),
        package_emoji=pkg.get('emoji', '')
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏳ 14 днів", callback_data="dur_14"),
         InlineKeyboardButton(text="⏳ 30 днів", callback_data="dur_30")],
        [InlineKeyboardButton(text="⏳ 90 днів", callback_data="dur_90"),
         InlineKeyboardButton(text="⏳ 365 днів", callback_data="dur_365")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="user_menu")]
    ])
    
    await state.set_state(ApplicationForm.waiting_duration)
    await query.answer()
    await query.message.edit_text(
        f"<b>📋 ОФОРМЛЕННЯ ЗАЯВКИ — КРОК 1/4</b>\n\n"
        f"═══════════════════════\n\n"
        f"<b>📦 Обраний тариф:</b> {pkg['emoji']} {pkg['name']}\n\n"
        f"<b>⏳ Оберіть термін дії ліцензії:</b>",
        reply_markup=kb, parse_mode="HTML"
    )

@router.callback_query(ApplicationForm.waiting_duration, F.data.startswith("dur_"))
async def process_duration(query: CallbackQuery, state: FSMContext):
    duration = query.data.replace("dur_", "")
    await state.update_data(duration=duration)
    await state.set_state(ApplicationForm.waiting_name)
    
    data = await state.get_data()
    pkg_name = data.get('package_name')
    pkg_emoji = data.get('package_emoji')
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_application")]
    ])
    
    await query.answer()
    await query.message.edit_text(
        f"<b>📋 ОФОРМЛЕННЯ ЗАЯВКИ — КРОК 2/4</b>\n\n"
        f"═══════════════════════\n\n"
        f"<b>📦 Тариф:</b> {pkg_emoji} {pkg_name}\n"
        f"<b>⏳ Термін:</b> {duration} днів\n\n"
        f"<b>👤 Як до вас звертатися?</b>\n\n"
        f"<i>Введіть ваше ім'я або нікнейм:</i>",
        reply_markup=kb, parse_mode="HTML"
    )

@router.message(ApplicationForm.waiting_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(client_name=name)
    await state.set_state(ApplicationForm.waiting_purpose)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_application")]
    ])
    
    await message.answer(
        f"<b>📋 ОФОРМЛЕННЯ ЗАЯВКИ — КРОК 3/4</b>\n\n"
        f"═══════════════════════\n\n"
        f"<b>👤 Клієнт:</b> {name}\n\n"
        f"<b>📝 Опишіть ваші цілі та задачі:</b>\n"
        f"<i>(Наприклад: розсилка по базі, парсинг, OSINT моніторинг)</i>", 
        reply_markup=kb, parse_mode="HTML"
    )

@router.message(ApplicationForm.waiting_purpose)
async def process_purpose(message: Message, state: FSMContext):
    purpose = message.text.strip()
    await state.update_data(purpose=purpose)
    await state.set_state(ApplicationForm.waiting_contact)
    
    contact_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Надіслати мій контакт", request_contact=True)]], 
        resize_keyboard=True, 
        one_time_keyboard=True
    )
    
    await message.answer(
        f"<b>📋 ОФОРМЛЕННЯ ЗАЯВКИ — КРОК 4/4</b>\n\n"
        f"═══════════════════════\n\n"
        f"<b>📱 Останній крок:</b>\n\n"
        f"Нам потрібен ваш контакт для оперативного зв'язку в разі виникнення питань щодо активації.", 
        reply_markup=contact_kb, parse_mode="HTML"
    )

@router.message(ApplicationForm.waiting_contact, F.contact)
async def process_contact(message: Message, state: FSMContext):
    contact = message.contact
    data = await state.get_data()
    pkg_name = data.get('package_name')
    pkg_emoji = data.get('package_emoji')
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Надіслати заявку", callback_data="confirm_application")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_application")]
    ])
    
    await state.update_data(phone=contact.phone_number)
    
    price = data.get('price', 'Уточнюється')
    duration = data.get('duration', 30)
    
    await message.answer(
        f"<b>📋 ПЕРЕВІРКА ВАШОЇ ЗАЯВКИ</b>\n\n"
        f"<b>💎 Тариф:</b> {pkg_emoji} {pkg_name.upper()}\n"
        f"<b>📅 Термін:</b> {duration} днів\n"
        f"<b>💵 До сплати:</b> {price}\n\n"
        f"<b>👤 Ім'я:</b> {data.get('client_name')}\n"
        f"<b>📝 Мета:</b> {data.get('purpose')}\n"
        f"<b>📞 Контакт:</b> {contact.phone_number}\n\n"
        f"⚠️ <b>УВАГА:</b> Натискаючи «Надіслати», ви підтверджуєте, що ознайомилися з правилами сервісу та погоджуєтесь з умовами оферти. Спам, шахрайство та заборонені тематики суворо модеруються.",
        reply_markup=kb, parse_mode="HTML"
    )

@router.callback_query(F.data == "user_menu")
async def user_menu_handler(callback: CallbackQuery):
    await callback.answer()
    from keyboards.role_menus import get_description_by_role, get_menu_by_role
    from services.user_service import user_service
    user = user_service.get_or_create_user(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    await callback.message.edit_text(
        get_description_by_role(user.role),
        reply_markup=get_menu_by_role(user.role),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "confirm_application")
async def confirm_application(query: CallbackQuery, state: FSMContext):
    await query.answer("✅ Заявку надіслано!")
    await query.message.edit_text(
        "<b>✅ Заявку успішно створено!</b>\n\n"
        "Адміністратор вже отримав ваш запит. Ми перевіримо дані та зв'яжемося з вами в особисті повідомлення протягом 15 хвилин для надання реквізитів.\n\n"
        "<i>Дякуємо, що обрали Shadow System.</i>",
        parse_mode="HTML"
    )
    await state.clear()

@router.callback_query(F.data == "cancel_application")
async def cancel_application(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.answer("Заявку скасовано")
    
    from keyboards.role_menus import get_menu_by_role, get_description_by_role
    from services.user_service import user_service
    from database.models import UserRole
    
    db_user = user_service.get_user_by_telegram_id(query.from_user.id)
    role = db_user.role if db_user else UserRole.GUEST
    
    await query.message.edit_text(
        get_description_by_role(role),
        reply_markup=get_menu_by_role(role),
        parse_mode="HTML"
    )
