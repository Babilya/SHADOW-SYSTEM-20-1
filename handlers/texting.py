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

# Text templates library
TEXT_TEMPLATES = {
    "promo": {
        "title": "🎁 Промо-пропозиція",
        "template": """Привіт! 👋

Ми пропонуємо спеціальну пропозицію для вас:

{promo_text}

💰 Спеціальна ціна: {price}
⏰ Дійсна до: {date}

Скорити у відповідь 👇"""
    },
    
    "welcome": {
        "title": "👋 Привітання",
        "template": """Привіт, {name}! 👋

Чудово, що ти приєднався до нашої спільноти!

{welcome_text}

🎁 Бонус для новачків: +10% до першого замовлення
📍 Твоє місце: {location}
💳 Тарифи: {plan}

Готовий почати? ✨"""
    },
    
    "feedback": {
        "title": "⭐ Запит відгуку",
        "template": """Як пройшла твоя користування нашим сервісом? ⭐

Твій відгук дуже важливий для нас!

Оцініть наш сервіс:
⭐⭐⭐⭐⭐ - Відмінно
⭐⭐⭐⭐ - Добре
⭐⭐⭐ - Задовільно

Поділись своїм коментарем у відповідь 👇"""
    },
    
    "reminder": {
        "title": "🔔 Нагадування",
        "template": """Привіт! ⏰

Хочемо нагадати про:
{reminder_text}

⏰ Залишилось: {time_left}
🎯 Важливо: Не забудьте!

Перейти тут 👉 {link}"""
    },
    
    "announcement": {
        "title": "📢 Оголошення",
        "template": """📢 <b>ВАЖЛИВЕ ОГОЛОШЕННЯ</b>

{announcement_text}

📅 Дата: {date}
⏰ Час: {time}
🌍 Для всіх: Так

Дізнайтеся більше 👇"""
    },
    
    "upsell": {
        "title": "📈 Upgrade пропозиція",
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

@texting_router.message(Command("texting"))
async def texting_menu(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Створити текстовку", callback_data="create_text")],
        [InlineKeyboardButton(text="📚 Шаблони", callback_data="templates_list")],
        [InlineKeyboardButton(text="📊 Мої текстовки", callback_data="my_texts")],
        [InlineKeyboardButton(text="⚙️ Налаштування", callback_data="text_settings")],
    ])
    await message.answer("📝 <b>ТЕКСТОВІ ВОРОНКИ</b>\n\nУпраління текстовими кампаніями та шаблонами", reply_markup=kb, parse_mode="HTML")

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
        [InlineKeyboardButton(text=f"🎁 {name['title']}", callback_data=f"template_{key}")]
        for key, name in TEXT_TEMPLATES.items()
    ]
    template_buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="texting_menu_back")])
    
    kb = InlineKeyboardMarkup(inline_keyboard=template_buttons)
    await query.message.edit_text("<b>📚 ШАБЛОНИ ТЕКСТОВОК</b>\n\nВиберіть готовий шаблон:", reply_markup=kb, parse_mode="HTML")

@texting_router.callback_query(F.data.startswith("template_"))
async def show_template(query: CallbackQuery):
    template_key = query.data.replace("template_", "")
    await query.answer()
    
    if template_key in TEXT_TEMPLATES:
        template = TEXT_TEMPLATES[template_key]
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Використати", callback_data=f"use_template_{template_key}")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="templates_list")]
        ])
        
        preview = f"<b>{template['title']}</b>\n\n{template['template']}"
        await query.message.edit_text(preview, reply_markup=kb, parse_mode="HTML")

@texting_router.callback_query(F.data == "my_texts")
async def my_texts(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 Промо-пропозиція", callback_data="text_detail_1")],
        [InlineKeyboardButton(text="📄 Привітання", callback_data="text_detail_2")],
        [InlineKeyboardButton(text="📄 Запит відгуку", callback_data="text_detail_3")],
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
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="text_stats")],
        [InlineKeyboardButton(text="✏️ Редагувати", callback_data="text_edit")],
        [InlineKeyboardButton(text="📤 Відправити знову", callback_data="text_resend")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="my_texts")]
    ])
    
    text = """<b>📄 ДЕТАЛІ ТЕКСТОВКИ</b>

<b>Назва:</b> Промо-пропозиція
<b>Створена:</b> 15 грудня, 2024
<b>Статус:</b> Завершено ✅

<b>Текст:</b>
"Привіт! Спеціальна пропозиція тільки для тебе..."

<b>Результати:</b>
📤 Відправлено: 245
✅ Доставлено: 234
👀 Прочитано: 189
💬 Відповідей: 45
📊 CTR: 12%"""
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@texting_router.callback_query(F.data == "text_settings")
async def text_settings(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏰ Час відправлення", callback_data="text_time")],
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
