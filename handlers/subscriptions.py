from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

subscriptions_router = Router()

PACKAGES = {
    "basic": {
        "name": "БАЗОВИЙ",
        "emoji": "📦",
        "bots_limit": 100,
        "managers_limit": 1,
        "prices": {3: 1400, 14: 3500, 30: 4200},
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
        "prices": {3: 4200, 14: 10500, 30: 12500},
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
        "prices": {3: 21000, 14: 52500, 30: 62500},
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
        "prices": {3: 35000, 14: 85000, 30: 100000},
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
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])

def subscriptions_description() -> str:
    return """<b>📦 ТАРИФНІ ПЛАНИ SHADOW SYSTEM</b>

<b>🎯 Оберіть план для вашого проекту:</b>

<b>📦 БАЗОВИЙ</b> — від <b>4,200 ₴/міс</b>
├ 100 ботів | 1 менеджер
├ Базовий OSINT | Розсилки
└ <i>Для початківців</i>

<b>⭐ СТАНДАРТ</b> — від <b>12,500 ₴/міс</b>
├ 500 ботів | 5 менеджерів
├ Повний OSINT | Campaign Manager
└ <i>Для активних проектів</i>

<b>👑 ПРЕМІУМ</b> — від <b>62,500 ₴/міс</b>
├ 5000 ботів | 15 менеджерів
├ AI Sentiment | Geo-Intelligence
└ <i>Для професіоналів</i>

<b>💎 ПЕРСОНАЛЬНИЙ</b> — від <b>100,000 ₴/міс</b>
├ Безлімітні операції
├ Кастомні модулі | 24/7 підтримка
└ <i>Enterprise рішення</i>

<b>💡 Обирайте 30-денний план для найкращої ціни!</b>
<b>🎁 Знижка -20% при оплаті на 30 днів</b>"""

def package_detail_kb(pkg_key: str):
    pkg = PACKAGES[pkg_key]
    buttons = [
        [InlineKeyboardButton(text=f"3 дні — {pkg['prices'][3]:,} ₴", callback_data=f"buy_{pkg_key}_3"),
         InlineKeyboardButton(text=f"14 днів — {pkg['prices'][14]:,} ₴", callback_data=f"buy_{pkg_key}_14")],
        [InlineKeyboardButton(text=f"🔥 30 днів — {pkg['prices'][30]:,} ₴ ВИГІДНО", callback_data=f"buy_{pkg_key}_30")],
        [InlineKeyboardButton(text="📝 Подати заявку", callback_data=f"apply_{pkg_key}")],
        [InlineKeyboardButton(text="📊 Порівняти", callback_data="pkg_compare"),
         InlineKeyboardButton(text="◀️ Тарифи", callback_data="subscription_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def package_detail_text(pkg_key: str) -> str:
    pkg = PACKAGES[pkg_key]
    
    features = "\n".join(pkg["features"])
    modules = " | ".join(pkg["modules"])
    
    no_access_text = ""
    if pkg["no_access"]:
        no_access_text = "\n\n<b>❌ Недоступно:</b>\n" + "\n".join([f"✗ {x}" for x in pkg["no_access"]])
    
    price_3 = pkg['prices'][3]
    price_14 = pkg['prices'][14]
    price_30 = pkg['prices'][30]
    
    daily_3 = price_3 / 3
    daily_14 = price_14 / 14
    daily_30 = price_30 / 30
    
    return f"""{pkg['emoji']} <b>ТАРИФ {pkg['name']}</b>

<b>💰 ЦІНИ:</b>
├ 3 дні: <b>{price_3:,} ₴</b> ({daily_3:.0f} ₴/день)
├ 14 днів: <b>{price_14:,} ₴</b> ({daily_14:.0f} ₴/день)
└ 30 днів: <b>{price_30:,} ₴</b> ({daily_30:.0f} ₴/день) 🔥

<b>📊 ЛІМІТИ:</b>
├ Ботів: <b>{pkg['bots_limit'] if pkg['bots_limit'] < 10000 else 'Безліміт'}</b>
└ Менеджерів: <b>{pkg['managers_limit'] if pkg['managers_limit'] < 100 else 'Безліміт'}</b>

<b>✅ МОЖЛИВОСТІ:</b>
{features}

<b>📦 МОДУЛІ:</b>
{modules}{no_access_text}

<b>💡 Обирайте 30-денний план — це найвигідніше!</b>"""

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
<b>├─────────────┼────────┼─────────┼─────────┼──────────┤</b>
│ <b>Ціна 30дн</b>  │ 4,200₴ │ 12,500₴ │ 62,500₴ │ 100,000₴ │
<b>└─────────────┴────────┴─────────┴─────────┴──────────┘</b>

<b>🔥 РЕКОМЕНДАЦІЇ:</b>
📦 <b>БАЗОВИЙ</b> — для тестування та малих проектів
⭐ <b>СТАНДАРТ</b> — оптимальний вибір для більшості
👑 <b>ПРЕМІУМ</b> — для професійних операцій
💎 <b>ПЕРСОНАЛЬНИЙ</b> — корпоративні клієнти та LEA

<b>🎁 При оплаті на 30 днів економія до 20%!</b>"""

@subscriptions_router.message(Command("subscription"))
async def subscription_cmd(message: Message):
    await message.answer(subscriptions_description(), reply_markup=subscriptions_kb(), parse_mode="HTML")

@subscriptions_router.callback_query(F.data == "subscription_main")
async def subscription_menu(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text(subscriptions_description(), reply_markup=subscriptions_kb(), parse_mode="HTML")

@subscriptions_router.callback_query(F.data == "pkg_compare")
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

@subscriptions_router.callback_query(F.data.startswith("pkg_"))
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

@subscriptions_router.callback_query(F.data.startswith("buy_"))
async def buy_package(query: CallbackQuery):
    parts = query.data.split("_")
    pkg_key = parts[1]
    days = int(parts[2])
    
    if pkg_key not in PACKAGES:
        await query.answer("Тариф не знайдено")
        return
    
    pkg = PACKAGES[pkg_key]
    price = pkg['prices'][days]
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Картка", callback_data=f"pay_card_{pkg_key}_{days}"),
         InlineKeyboardButton(text="⭐ Stars", callback_data=f"pay_stars_{pkg_key}_{days}"),
         InlineKeyboardButton(text="🏦 LiqPay", callback_data=f"pay_liqpay_{pkg_key}_{days}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"pkg_{pkg_key}")]
    ])
    
    await query.answer()
    await query.message.edit_text(
        f"""<b>🛒 ОФОРМЛЕННЯ ЗАМОВЛЕННЯ</b>

<b>📦 Тариф:</b> {pkg['emoji']} {pkg['name']}
<b>📅 Термін:</b> {days} днів
<b>💰 Сума:</b> <b>{price:,} ₴</b>

<b>🔐 Що ви отримаєте:</b>
├ Ліцензійний ключ SHADOW-XXXX-XXXX
├ Миттєва активація
├ Доступ до всіх функцій тарифу
└ Підтримка протягом підписки

<b>💳 Оберіть спосіб оплати:</b>""",
        reply_markup=kb, parse_mode="HTML"
    )

@subscriptions_router.callback_query(F.data.startswith("pay_card_"))
async def pay_card(query: CallbackQuery):
    parts = query.data.split("_")
    pkg_key = parts[2]
    days = int(parts[3])
    pkg = PACKAGES.get(pkg_key, {})
    price = pkg.get('prices', {}).get(days, 0)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Надіслати скріншот", callback_data=f"screenshot_{pkg_key}_{days}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"buy_{pkg_key}_{days}")]
    ])
    
    await query.answer()
    await query.message.edit_text(
        f"""<b>💳 ОПЛАТА КАРТКОЮ</b>

<b>📦 Тариф:</b> {pkg.get('emoji', '')} {pkg.get('name', '')}
<b>📅 Термін:</b> {days} днів
<b>💰 Сума:</b> <b>{price:,} ₴</b>

<b>📋 Реквізити для оплати:</b>
<code>4441 1144 5555 7777</code>
<b>Отримувач:</b> ФОП Іванов І.І.

<b>⚠️ ВАЖЛИВО:</b>
1. Вкажіть у коментарі ваш Telegram ID: <code>{query.from_user.id}</code>
2. Після оплати надішліть скріншот квитанції
3. Ключ буде надіслано після підтвердження адміном

<i>⏳ Час обробки: до 30 хвилин</i>""",
        reply_markup=kb, parse_mode="HTML"
    )

@subscriptions_router.callback_query(F.data.startswith("pay_stars_"))
async def pay_stars(query: CallbackQuery):
    parts = query.data.split("_")
    pkg_key = parts[2]
    days = int(parts[3])
    pkg = PACKAGES.get(pkg_key, {})
    price = pkg.get('prices', {}).get(days, 0)
    stars = int(price / 2.5)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"⭐ Оплатити {stars} Stars", callback_data=f"confirm_stars_{pkg_key}_{days}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"buy_{pkg_key}_{days}")]
    ])
    
    await query.answer()
    await query.message.edit_text(
        f"""<b>⭐ ОПЛАТА TELEGRAM STARS</b>

<b>📦 Тариф:</b> {pkg.get('emoji', '')} {pkg.get('name', '')}
<b>📅 Термін:</b> {days} днів
<b>💰 Сума:</b> <b>{stars:,} ⭐</b> (~{price:,} ₴)

<b>ℹ️ Як це працює:</b>
1. Натисніть кнопку оплати
2. Підтвердіть транзакцію в Telegram
3. Ключ буде згенеровано автоматично

<i>✅ Миттєва активація!</i>""",
        reply_markup=kb, parse_mode="HTML"
    )

@subscriptions_router.callback_query(F.data.startswith("pay_liqpay_"))
async def pay_liqpay(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="subscription_main")]
    ])
    await query.answer()
    await query.message.edit_text(
        "🏦 <b>LIQPAY</b>\n\nЦей метод оплати тимчасово недоступний.\nБудь ласка, оберіть інший спосіб.",
        reply_markup=kb, parse_mode="HTML"
    )

@subscriptions_router.callback_query(F.data == "subscription_faq")
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
A: Так, різниця буде перерахована

<b>Q: Що буде після закінчення підписки?</b>
A: Доступ буде обмежено до Guest

<b>Q: Чи є пробний період?</b>
A: Так, тариф БАЗОВИЙ на 3 дні

<b>Q: Як отримати рахунок?</b>
A: Зверніться до підтримки

<b>Q: Чи є знижки для команд?</b>
A: Так, від 5 ліцензій -15%

<b>Q: Як працює реферальна програма?</b>
A: 10% від першого платежу реферала""",
        reply_markup=kb, parse_mode="HTML"
    )

@subscriptions_router.callback_query(F.data == "subscription_support")
async def subscription_support(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Написати", url="https://t.me/shadow_support"),
         InlineKeyboardButton(text="🎫 Тікет", callback_data="create_ticket")],
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
└ 💎 ПЕРСОНАЛЬНИЙ: миттєво (24/7)

<b>🔧 Типові питання:</b>
• Активація ключа
• Оплата та рахунки
• Технічні проблеми
• Повернення коштів""",
        reply_markup=kb, parse_mode="HTML"
    )

@subscriptions_router.callback_query(F.data.startswith("screenshot_"))
async def screenshot_upload(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="subscription_main")]
    ])
    await query.answer()
    await query.message.edit_text(
        "📸 <b>НАДСИЛАННЯ СКРІНШОТУ</b>\n\n"
        "Надішліть скріншот квитанції про оплату як фото у цей чат.\n\n"
        "Адміністратор перевірить платіж та надішле ліцензійний ключ.",
        reply_markup=kb, parse_mode="HTML"
    )

@subscriptions_router.callback_query(F.data == "view_tariffs")
async def view_tariffs_handler(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text(subscriptions_description(), reply_markup=subscriptions_kb(), parse_mode="HTML")

@subscriptions_router.callback_query(F.data.startswith("apply_"))
async def apply_package(query: CallbackQuery):
    pkg_key = query.data.replace("apply_", "")
    if pkg_key not in PACKAGES:
        await query.answer("Тариф не знайдено")
        return
    
    pkg = PACKAGES[pkg_key]
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Заповнити форму", callback_data=f"application_start_{pkg_key}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"pkg_{pkg_key}")]
    ])
    
    await query.answer()
    await query.message.edit_text(
        f"""<b>📝 ЗАЯВКА НА ТАРИФ {pkg['emoji']} {pkg['name']}</b>

<b>💰 Ціни:</b>
├ 3 дні: {pkg['prices'][3]:,} ₴
├ 14 днів: {pkg['prices'][14]:,} ₴
└ 30 днів: {pkg['prices'][30]:,} ₴

<b>ℹ️ Як це працює:</b>
1️⃣ Заповніть коротку форму
2️⃣ Адмін перевірить вашу заявку
3️⃣ Отримаєте реквізити для оплати
4️⃣ Після оплати отримаєте ключ SHADOW-XXXX-XXXX

<b>⏱️ Час обробки:</b> до 30 хвилин

Натисніть "Заповнити форму" щоб продовжити 👇""",
        reply_markup=kb, parse_mode="HTML"
    )

@subscriptions_router.callback_query(F.data.startswith("application_start_"))
async def application_start(query: CallbackQuery, state: FSMContext):
    pkg_key = query.data.replace("application_start_", "")
    pkg = PACKAGES.get(pkg_key, {})
    
    await state.update_data(selected_package=pkg_key, package_name=pkg.get('name', ''))
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="3 дні", callback_data=f"app_days_3_{pkg_key}"),
         InlineKeyboardButton(text="14 днів", callback_data=f"app_days_14_{pkg_key}"),
         InlineKeyboardButton(text="30 днів", callback_data=f"app_days_30_{pkg_key}")],
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data=f"pkg_{pkg_key}")]
    ])
    
    await query.answer()
    await query.message.edit_text(
        f"""<b>📝 КРОК 1/3: Термін підписки</b>

<b>Обраний тариф:</b> {pkg.get('emoji', '')} {pkg.get('name', '')}

Оберіть бажаний термін підписки:""",
        reply_markup=kb, parse_mode="HTML"
    )

@subscriptions_router.callback_query(F.data.startswith("app_days_"))
async def app_days_select(query: CallbackQuery, state: FSMContext):
    parts = query.data.split("_")
    days = int(parts[2])
    pkg_key = parts[3]
    pkg = PACKAGES.get(pkg_key, {})
    price = pkg.get('prices', {}).get(days, 0)
    
    await state.update_data(days=days, price=price)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Підтвердити заявку", callback_data=f"app_confirm_{pkg_key}_{days}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"application_start_{pkg_key}")]
    ])
    
    await query.answer()
    await query.message.edit_text(
        f"""<b>📝 КРОК 2/3: Підтвердження</b>

<b>📦 Тариф:</b> {pkg.get('emoji', '')} {pkg.get('name', '')}
<b>📅 Термін:</b> {days} днів
<b>💰 Вартість:</b> {price:,} ₴

<b>ℹ️ Що далі:</b>
• Ваша заявка буде надіслана адміністратору
• Ви отримаєте реквізити для оплати
• Після підтвердження оплати отримаєте ключ

Натисніть "Підтвердити заявку" для надсилання 👇""",
        reply_markup=kb, parse_mode="HTML"
    )

@subscriptions_router.callback_query(F.data.startswith("app_confirm_"))
async def app_confirm(query: CallbackQuery, state: FSMContext):
    parts = query.data.split("_")
    pkg_key = parts[2]
    days = int(parts[3])
    pkg = PACKAGES.get(pkg_key, {})
    price = pkg.get('prices', {}).get(days, 0)
    
    from config import ADMIN_IDS
    from aiogram import Bot
    
    user = query.from_user
    
    admin_text = f"""<b>📝 НОВА ЗАЯВКА!</b>

<b>👤 Користувач:</b>
├ ID: <code>{user.id}</code>
├ Ім'я: {user.first_name} {user.last_name or ''}
└ Username: @{user.username or 'немає'}

<b>📦 Тариф:</b> {pkg.get('emoji', '')} {pkg.get('name', '')}
<b>📅 Термін:</b> {days} днів
<b>💰 Сума:</b> {price:,} ₴"""

    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Надіслати реквізити", callback_data=f"send_requisites_{user.id}_{pkg_key}_{days}"),
         InlineKeyboardButton(text="❌ Відхилити", callback_data=f"reject_app_{user.id}")]
    ])
    
    try:
        bot = Bot.get_current()
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(admin_id, admin_text, reply_markup=admin_kb, parse_mode="HTML")
            except:
                pass
    except:
        pass
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ До тарифів", callback_data="subscription_main")]
    ])
    
    await query.answer("✅ Заявка надіслана!")
    await query.message.edit_text(
        f"""<b>✅ ЗАЯВКА НАДІСЛАНА!</b>

<b>📦 Тариф:</b> {pkg.get('emoji', '')} {pkg.get('name', '')}
<b>📅 Термін:</b> {days} днів
<b>💰 Сума:</b> {price:,} ₴

<b>⏳ Що далі:</b>
Адміністратор перевірить вашу заявку та надішле реквізити для оплати.

<b>⏱️ Час очікування:</b> до 30 хвилин

Ми повідомимо вас, коли все буде готово! 🔔""",
        reply_markup=kb, parse_mode="HTML"
    )
    await state.clear()
