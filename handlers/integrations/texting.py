from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

texting_router = Router()

def texting_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Створити текстовку", callback_data="create_text")],
        [InlineKeyboardButton(text="📚 Шаблони", callback_data="templates_list")],
        [InlineKeyboardButton(text="📊 Мої текстовки", callback_data="my_texts")],
        [InlineKeyboardButton(text="⚙️ Налаштування", callback_data="text_settings")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")],
    ])

class TextingStates(StatesGroup):
    waiting_campaign_name = State()
    waiting_message_text = State()
    waiting_targets = State()

TEXT_TEMPLATES = {
    "promo": {
        "icon": "🎁",
        "title": "Промо-пропозиція",
        "template": """Привіт! 👋

Ми пропонуємо спеціальну пропозицію для вас:

{promo_text}

💰 Спеціальна ціна: {price}
⏰ Дійсна до: {date}

Скористайся зараз 👇"""
    },
    
    "welcome": {
        "icon": "👋",
        "title": "Привітання",
        "template": """Привіт, {name}! 👋

Чудово, що ти приєднався до нашої спільноти!

{welcome_text}

🎁 Бонус для новачків: +10% до першого замовлення
📍 Твоє місце: {location}
💳 Тарифи: {plan}

Готовий почати? ✨"""
    },
    
    "feedback": {
        "icon": "⭐",
        "title": "Запит відгуку",
        "template": """Як пройшла твоя користування нашим сервісом? ⭐

Твій відгук дуже важливий для нас!

Оцініть наш сервіс:
⭐⭐⭐⭐⭐ - Відмінно
⭐⭐⭐⭐ - Добре
⭐⭐⭐ - Задовільно

Поділись своїм коментарем у відповідь 👇"""
    },
    
    "reminder": {
        "icon": "🔔",
        "title": "Нагадування",
        "template": """Привіт! ⏰

Хочемо нагадати про:
{reminder_text}

⏰ Залишилось: {time_left}
🎯 Важливо: Не забудьте!

Перейти тут 👉 {link}"""
    },
    
    "announcement": {
        "icon": "📢",
        "title": "Оголошення",
        "template": """📢 <b>ВАЖЛИВЕ ОГОЛОШЕННЯ</b>

{announcement_text}

📅 Дата: {date}
⏰ Час: {time}
🌍 Для всіх: Так

Дізнайтеся більше 👇"""
    },
    
    "upsell": {
        "icon": "📈",
        "title": "Upgrade пропозиція",
        "template": """Привіт! 🚀

Помітили, що ти активно користуєшся нашим сервісом!

Ось що тобі подобатиметься:
✨ {feature1}
✨ {feature2}
✨ {feature3}

💎 Перейти на Premium - Спеціальна ціна для тебе
🎁 +30% бонус при переказі до кінця тижня

Дізнатись більше 👇"""
    }
}

def texting_description() -> str:
    return """<b>📝 ТЕКСТОВІ ВОРОНКИ</b>

Управління текстовими кампаніями та шаблонами для масових розсилок."""

@texting_router.message(Command("texting"))
async def texting_cmd(message: Message):
    await message.answer(texting_description(), reply_markup=texting_kb(), parse_mode="HTML")

async def texting_menu(message: Message):
    """Функція для виклику з інших модулів"""
    await message.edit_text(texting_description(), reply_markup=texting_kb(), parse_mode="HTML")

@texting_router.callback_query(F.data == "create_text")
async def create_text(query: CallbackQuery, state: FSMContext):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назва кампанії", callback_data="input_name")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="texting_menu_back")]
    ])
    await query.message.edit_text(
        "📝 Як назвати вашу текстовку?\n\nПриклад: 'Промо липня', 'Привіт новачків'",
        reply_markup=kb
    )

@texting_router.callback_query(F.data == "templates_list")
async def templates_list(query: CallbackQuery):
    await query.answer()
    
    template_buttons = [
        [InlineKeyboardButton(text=f"{data['icon']} {data['title']}", callback_data=f"template_{key}")]
        for key, data in TEXT_TEMPLATES.items()
    ]
    template_buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="texting_menu_back")])
    
    kb = InlineKeyboardMarkup(inline_keyboard=template_buttons)
    await query.message.edit_text(
        "<b>📚 ШАБЛОНИ</b>\n\n"
        "Готові шаблони для розсилок. Виберіть потрібний:",
        reply_markup=kb, parse_mode="HTML"
    )

@texting_router.callback_query(F.data.startswith("template_"))
async def show_template(query: CallbackQuery):
    template_key = query.data.replace("template_", "")
    if template_key.startswith("use_"):
        return
    
    await query.answer()
    
    if template_key in TEXT_TEMPLATES:
        template = TEXT_TEMPLATES[template_key]
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Використати", callback_data=f"use_template_{template_key}")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="templates_list")]
        ])
        
        preview = f"{template['icon']} <b>{template['title']}</b>\n\n{template['template']}"
        await query.message.edit_text(preview, reply_markup=kb, parse_mode="HTML")

@texting_router.callback_query(F.data == "my_texts")
async def my_texts(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 Промо-пропозиція", callback_data="text_detail_promo")],
        [InlineKeyboardButton(text="📄 Привітання", callback_data="text_detail_welcome")],
        [InlineKeyboardButton(text="📄 Запит відгуку", callback_data="text_detail_feedback")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="texting_menu_back")]
    ])
    
    text = """<b>📊 МОІ ТЕКСТОВКИ</b>

<b>Створені:</b>
✅ Промо-пропозиція (245 отримавців, 12% CTR)
✅ Привітання новачків (1,203 отримавців, 34% CTR)
✅ Запит відгуку (523 відповіді)

<b>На чернетці:</b>
📝 Оголошення про нові функції
📝 Upgrade пропозиція"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@texting_router.callback_query(F.data.startswith("text_detail_"))
async def text_detail(query: CallbackQuery):
    await query.answer()
    text_key = query.data.replace("text_detail_", "")
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data=f"text_stats_{text_key}")],
        [InlineKeyboardButton(text="✏️ Редагувати", callback_data=f"text_edit_{text_key}")],
        [InlineKeyboardButton(text="📤 Відправити знову", callback_data=f"text_resend_{text_key}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="my_texts")]
    ])
    
    texts_data = {
        "promo": {
            "name": "Промо-пропозиція",
            "date": "15 грудня, 2024",
            "text": "Привіт! Спеціальна пропозиція тільки для тебе...",
            "sent": 245, "delivered": 234, "read": 189, "replies": 45, "ctr": "12%"
        },
        "welcome": {
            "name": "Привітання новачків",
            "date": "12 грудня, 2024",
            "text": "Привіт! Чудово, що ти приєднався до нашої спільноти...",
            "sent": 1203, "delivered": 1180, "read": 980, "replies": 125, "ctr": "34%"
        },
        "feedback": {
            "name": "Запит відгуку",
            "date": "20 грудня, 2024",
            "text": "Як пройшла твоя користування нашим сервісом?...",
            "sent": 800, "delivered": 785, "read": 650, "replies": 523, "ctr": "65%"
        }
    }
    
    data = texts_data.get(text_key, texts_data["promo"])
    
    text = f"""<b>📄 ДЕТАЛІ ТЕКСТОВКИ</b>

<b>Назва:</b> {data['name']}
<b>Створена:</b> {data['date']}
<b>Статус:</b> Завершено ✅

<b>Текст:</b>
"{data['text']}"

<b>Результати:</b>
📤 Відправлено: {data['sent']}
✅ Доставлено: {data['delivered']}
👀 Прочитано: {data['read']}
💬 Відповідей: {data['replies']}
📊 CTR: {data['ctr']}"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@texting_router.callback_query(F.data == "text_settings")
async def text_settings(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🕰 Час відправлення", callback_data="text_time")],
        [InlineKeyboardButton(text="🎯 Сегментація", callback_data="text_segmentation")],
        [InlineKeyboardButton(text="📊 A/B тестування", callback_data="text_ab")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="texting_menu_back")]
    ])
    
    text = """<b>⚙️ НАЛАШТУВАННЯ ТЕКСТОВОК</b>

<b>Час відправлення:</b>
🕐 Автоматичний (оптимальний час)
🕐 Ручний (виберіть час)
🕐 За розкладом (CronJob)

<b>Сегментація:</b>
👥 За статусом підписки
👥 За географією
👥 За активністю
👥 За інтересам

<b>A/B тестування:</b>
📊 Варіант A vs B
📊 Автоматичний вибір кращого
📊 Статистичний аналіз"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@texting_router.callback_query(F.data == "texting_menu_back")
async def texting_back(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Створити текстовку", callback_data="create_text")],
        [InlineKeyboardButton(text="📚 Шаблони", callback_data="templates_list")],
        [InlineKeyboardButton(text="📊 Мої текстовки", callback_data="my_texts")],
        [InlineKeyboardButton(text="⚙️ Налаштування", callback_data="text_settings")],
    ])
    await query.message.edit_text("📝 <b>ТЕКСТОВІ ВОРОНКИ</b>\n\nУпраління текстовими кампаніями та шаблонами", reply_markup=kb, parse_mode="HTML")
