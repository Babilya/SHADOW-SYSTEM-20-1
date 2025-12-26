from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

subscriptions_router = Router()

class ApplicationForm(StatesGroup):
    waiting_name = State()
    waiting_purpose = State()
    waiting_contact = State()

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
        [InlineKeyboardButton(text="💰 ОБЕРІТЬ ТЕРМІН ОРЕНДИ:", callback_data="noop")],
        [InlineKeyboardButton(text=f"⏱ 3 дні — {pkg['prices'][3]:,} ₴", callback_data=f"apply_{pkg_key}_3"),
         InlineKeyboardButton(text=f"📅 14 днів — {pkg['prices'][14]:,} ₴", callback_data=f"apply_{pkg_key}_14")],
        [InlineKeyboardButton(text=f"📆 30 днів — {pkg['prices'][30]:,} ₴ 🔥", callback_data=f"apply_{pkg_key}_30")],
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

@subscriptions_router.callback_query(F.data == "noop")
async def noop_handler(query: CallbackQuery):
    await query.answer()

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

@subscriptions_router.callback_query(F.data == "view_tariffs")
async def view_tariffs_handler(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text(subscriptions_description(), reply_markup=subscriptions_kb(), parse_mode="HTML")

@subscriptions_router.callback_query(F.data.startswith("apply_"))
async def apply_package(query: CallbackQuery, state: FSMContext):
    parts = query.data.split("_")
    if len(parts) == 3:
        pkg_key = parts[1]
        days = int(parts[2])
    else:
        await query.answer("Помилка формату")
        return
    
    if pkg_key not in PACKAGES:
        await query.answer("Тариф не знайдено")
        return
    
    pkg = PACKAGES[pkg_key]
    price = pkg['prices'].get(days, 0)
    
    await state.update_data(
        selected_package=pkg_key, 
        package_name=pkg.get('name', ''),
        package_emoji=pkg.get('emoji', ''),
        days=days,
        price=price
    )
    await state.set_state(ApplicationForm.waiting_name)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data=f"pkg_{pkg_key}")]
    ])
    
    await query.answer()
    await query.message.edit_text(
        f"""<b>📋 РЕЄСТРАЦІЯ — КРОК 1/3</b>

<b>Обраний тариф:</b> {pkg['emoji']} {pkg['name']}
<b>Термін:</b> {days} днів
<b>Вартість:</b> {price:,} ₴

<b>👤 Як до вас звертатися?</b>

Введіть ваше ім'я:""",
        reply_markup=kb, parse_mode="HTML"
    )

@subscriptions_router.message(ApplicationForm.waiting_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2 or len(name) > 50:
        await message.answer("❌ Ім'я має бути від 2 до 50 символів. Спробуйте ще раз:")
        return
    
    await state.update_data(client_name=name)
    await state.set_state(ApplicationForm.waiting_purpose)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_application")]
    ])
    
    await message.answer(
        f"""<b>📋 РЕЄСТРАЦІЯ — КРОК 2/3</b>

<b>👤 Ім'я:</b> {name}

<b>📝 Опишіть ваші задачі:</b>
<i>(наприклад: арбітраж, крипто-проекти, OSINT, маркетинг)</i>

Введіть опис:""",
        reply_markup=kb, parse_mode="HTML"
    )

@subscriptions_router.message(ApplicationForm.waiting_purpose)
async def process_purpose(message: Message, state: FSMContext):
    purpose = message.text.strip()
    if len(purpose) < 5 or len(purpose) > 500:
        await message.answer("❌ Опис має бути від 5 до 500 символів. Спробуйте ще раз:")
        return
    
    await state.update_data(purpose=purpose)
    await state.set_state(ApplicationForm.waiting_contact)
    
    contact_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Надіслати контакт", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    data = await state.get_data()
    
    await message.answer(
        f"""<b>📋 РЕЄСТРАЦІЯ — КРОК 3/3</b>

<b>👤 Ім'я:</b> {data.get('client_name', '')}
<b>📝 Мета:</b> {purpose[:100]}...

<b>📱 Надішліть ваш контакт для зв'язку:</b>

Натисніть кнопку нижче 👇""",
        reply_markup=contact_kb, parse_mode="HTML"
    )

@subscriptions_router.message(ApplicationForm.waiting_contact, F.contact)
async def process_contact(message: Message, state: FSMContext):
    contact = message.contact
    data = await state.get_data()
    
    pkg_key = data.get('selected_package', '')
    pkg = PACKAGES.get(pkg_key, {})
    days = data.get('days', 0)
    price = data.get('price', 0)
    client_name = data.get('client_name', '')
    purpose = data.get('purpose', '')
    phone = contact.phone_number if contact else 'Не вказано'
    
    remove_kb = ReplyKeyboardRemove()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Все вірно, Надіслати", callback_data="confirm_application")],
        [InlineKeyboardButton(text="❌ Скасувати та вийти", callback_data="cancel_application")]
    ])
    
    await state.update_data(phone=phone)
    
    await message.answer(
        f"""<b>📋 ПЕРЕВІРКА ВАШОЇ ЗАЯВКИ</b>

<b>💎 Пакет:</b> {pkg.get('emoji', '')} {pkg.get('name', '')}
<b>📅 Термін:</b> {days} днів
<b>💵 До сплати:</b> {price:,} ₴

<b>👤 Ім'я:</b> {client_name}
<b>📝 Мета:</b> {purpose}
<b>📞 Контакт:</b> {phone}

<b>⚠️ Важливо:</b>
Після надсилання адміністратор зв'яжеться з вами протягом 15 хвилин для надання реквізитів та ліцензійного ключа.""",
        reply_markup=kb, parse_mode="HTML"
    )
    
    await message.answer("Перевірте дані та підтвердіть заявку 👆", reply_markup=remove_kb)

@subscriptions_router.callback_query(F.data == "confirm_application")
async def confirm_application(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    pkg_key = data.get('selected_package', '')
    pkg = PACKAGES.get(pkg_key, {})
    days = data.get('days', 0)
    price = data.get('price', 0)
    client_name = data.get('client_name', '')
    purpose = data.get('purpose', '')
    phone = data.get('phone', 'Не вказано')
    
    from config import ADMIN_IDS
    
    user = query.from_user
    
    admin_text = f"""<b>🔔 НОВИЙ ЛІД #{user.id % 1000}</b>

<b>👤 Клієнт:</b> {client_name} (@{user.username or 'немає'})
<b>🆔 TG-ID:</b> <code>{user.id}</code>
<b>📞 Телефон:</b> {phone}

<b>💎 Пакет:</b> {pkg.get('emoji', '')} {pkg.get('name', '')}
<b>💵 Сума:</b> {price:,} ₴ ({days} днів)
<b>📝 Ціль:</b> {purpose}"""

    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Реквізити", callback_data=f"send_requisites_{user.id}_{pkg_key}_{days}"),
         InlineKeyboardButton(text="💬 Написати", url=f"tg://user?id={user.id}")],
        [InlineKeyboardButton(text="✅ Оплату отримано", callback_data=f"payment_received_{user.id}_{pkg_key}_{days}"),
         InlineKeyboardButton(text="❌ Відхилити", callback_data=f"reject_app_{user.id}")]
    ])
    
    try:
        bot = query.bot
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
    
    await query.answer("✅ Заявку успішно створено!")
    await query.message.edit_text(
        f"""<b>✅ ЗАЯВКУ УСПІШНО СТВОРЕНО!</b>

Ваш запит <b>#INV-{user.id % 10000}</b> передано до адміністративного відділу.

<b>📦 Пакет:</b> {pkg.get('emoji', '')} {pkg.get('name', '')}
<b>📅 Термін:</b> {days} днів
<b>💰 Сума:</b> {price:,} ₴

Ми перевіримо дані та зв'яжемося з вами в особисті повідомлення для надання реквізитів.

<b>Дякуємо, що обрали Shadow System!</b> 🖤""",
        reply_markup=kb, parse_mode="HTML"
    )
    await state.clear()

@subscriptions_router.callback_query(F.data == "cancel_application")
async def cancel_application(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.answer("Заявку скасовано")
    await query.message.edit_text(subscriptions_description(), reply_markup=subscriptions_kb(), parse_mode="HTML")

# ========== ADMIN HANDLERS ==========

@subscriptions_router.callback_query(F.data.startswith("send_requisites_"))
async def admin_send_requisites(query: CallbackQuery):
    from config import ADMIN_IDS
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    parts = query.data.split("_")
    user_id = int(parts[2])
    pkg_key = parts[3]
    days = int(parts[4])
    pkg = PACKAGES.get(pkg_key, {})
    price = pkg.get('prices', {}).get(days, 0)
    
    requisites_text = f"""🔑 <b>ЗАЯВКА НА ЛІЦЕНЗІЮ</b>

<b>💎 Пакет:</b> {pkg.get('emoji', '')} {pkg.get('name', '')}
<b>📅 Термін:</b> {days} днів

<b>✅ Ваша заявка прийнята!</b>

Адміністратор розглядає вашу заявку.
Після схвалення ви отримаєте SHADOW ключ для активації.

<b>⏱ Середній час обробки:</b> 15-30 хвилин

<i>Дякуємо за довіру!</i>"""

    try:
        await query.bot.send_message(user_id, requisites_text, parse_mode="HTML")
        await query.message.edit_text(
            query.message.text + f"\n\n✅ <b>Реквізити надіслано користувачу!</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Оплату отримано", callback_data=f"payment_received_{user_id}_{pkg_key}_{days}"),
                 InlineKeyboardButton(text="❌ Відхилити", callback_data=f"reject_app_{user_id}")]
            ])
        )
        await query.answer("✅ Реквізити надіслано!")
    except Exception as e:
        await query.answer(f"❌ Помилка: {str(e)}", show_alert=True)

@subscriptions_router.callback_query(F.data.startswith("payment_received_"))
async def admin_payment_received(query: CallbackQuery):
    from config import ADMIN_IDS
    from core.encryption import encryption_manager
    from core.key_generator import generate_shadow_key, store_license_key
    
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    parts = query.data.split("_")
    user_id = int(parts[2])
    pkg_key = parts[3]
    days = int(parts[4])
    pkg = PACKAGES.get(pkg_key, {})
    
    license_key = generate_shadow_key(pkg_key)
    store_license_key(license_key, user_id, pkg_key, days)
    
    key_text = f"""✅ <b>ОПЛАТА ПІДТВЕРДЖЕНА!</b>

<b>💎 Пакет:</b> {pkg.get('emoji', '')} {pkg.get('name', '')}
<b>📅 Термін:</b> {days} днів

<b>🔑 Ваш ліцензійний ключ:</b>
<code>{license_key}</code>

<b>Для активації введіть ключ:</b>
Натисніть /start → 🔑 Ввести ключ

<b>⚠️ ВАЖЛИВО:</b>
Збережіть ключ у безпечному місці!

<b>Дякуємо за покупку!</b> 🖤"""

    try:
        await query.bot.send_message(user_id, key_text, parse_mode="HTML")
        await query.message.edit_text(
            query.message.text + f"\n\n✅ <b>ОПЛАТА ПІДТВЕРДЖЕНА</b>\n🔑 Ключ: <code>{license_key}</code>\n👤 Підтвердив: @{query.from_user.username}",
            parse_mode="HTML"
        )
        await query.answer("✅ Ключ згенеровано та надіслано!")
    except Exception as e:
        await query.answer(f"❌ Помилка: {str(e)}", show_alert=True)

@subscriptions_router.callback_query(F.data.startswith("reject_app_"))
async def admin_reject_application(query: CallbackQuery):
    from config import ADMIN_IDS
    
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    user_id = int(query.data.split("_")[2])
    
    reject_text = """❌ <b>ЗАЯВКА ВІДХИЛЕНА</b>

На жаль, вашу заявку було відхилено.

<b>Можливі причини:</b>
• Неповні або некоректні дані
• Підозріла активність
• Інші причини

Для уточнення зверніться до підтримки: @shadow_support"""

    try:
        await query.bot.send_message(user_id, reject_text, parse_mode="HTML")
        await query.message.edit_text(
            query.message.text + f"\n\n❌ <b>ЗАЯВКА ВІДХИЛЕНА</b>\n👤 Відхилив: @{query.from_user.username}",
            parse_mode="HTML"
        )
        await query.answer("❌ Заявку відхилено!")
    except Exception as e:
        await query.answer(f"❌ Помилка: {str(e)}", show_alert=True)
