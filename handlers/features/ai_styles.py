from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

logger = logging.getLogger(__name__)
ai_styles_router = Router()
router = ai_styles_router


class AIStylesStates(StatesGroup):
    waiting_custom_name = State()
    waiting_custom_prompt = State()
    waiting_training_user = State()
    waiting_training_response = State()
    waiting_test_message = State()


def ai_styles_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎭 Вибрати стиль", callback_data="ai_select_style")],
        [InlineKeyboardButton(text="➕ Створити свій", callback_data="ai_create_custom")],
        [InlineKeyboardButton(text="📚 Навчити на прикладах", callback_data="ai_train_examples")],
        [InlineKeyboardButton(text="🧪 Тестувати відповіді", callback_data="ai_test_response")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="ai_styles_stats")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="user_menu")]
    ])


@ai_styles_router.callback_query(F.data == "ai_styles_menu")
async def ai_styles_menu(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    
    from core.ai_communication_styles import ai_communication_styles
    
    stats = ai_communication_styles.get_stats()
    
    text = "<b>🎭 AI СТИЛІ КОМУНІКАЦІЇ</b>\n"
    text += "═══════════════════════\n\n"
    text += "<i>Налаштуйте як боти будуть спілкуватися</i>\n\n"
    text += f"<b>📊 Статистика:</b>\n"
    text += f"├ Стилів: {stats['total_personas']}\n"
    text += f"├ Кастомних: {stats['custom_personas']}\n"
    text += f"├ Призначено ботам: {stats['active_assignments']}\n"
    text += f"└ Прикладів навчання: {stats['training_examples']}\n\n"
    text += "<b>Доступні стилі:</b>\n"
    text += "├ 😊 Дружній помічник\n"
    text += "├ 👔 Професійний менеджер\n"
    text += "├ 😎 Свій в дошку\n"
    text += "├ 💼 Експерт продажів\n"
    text += "├ 🖥 Технічний гуру\n"
    text += "├ 🪙 Крипто трейдер\n"
    text += "├ 🎧 Агент підтримки\n"
    text += "└ 🔮 Загадкова особа"
    
    await query.message.edit_text(text, reply_markup=ai_styles_kb(), parse_mode="HTML")


@ai_styles_router.callback_query(F.data == "ai_select_style")
async def ai_select_style(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    
    from core.ai_communication_styles import ai_communication_styles
    
    personas = ai_communication_styles.get_all_personas()
    
    text = "<b>🎭 ВИБІР СТИЛЮ</b>\n"
    text += "═══════════════════════\n\n"
    text += "<i>Виберіть стиль для ботів:</i>"
    
    buttons = []
    for persona in personas:
        emoji = {
            "friendly_helper": "😊",
            "professional_manager": "👔",
            "casual_friend": "😎",
            "sales_expert": "💼",
            "tech_guru": "🖥",
            "crypto_trader": "🪙",
            "support_agent": "🎧",
            "mysterious_stranger": "🔮"
        }.get(persona.persona_id, "🎭")
        
        custom_badge = " ⭐" if persona.is_custom else ""
        buttons.append([InlineKeyboardButton(
            text=f"{emoji} {persona.name}{custom_badge}",
            callback_data=f"ai_style_view:{persona.persona_id}"
        )])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="ai_styles_menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@ai_styles_router.callback_query(F.data.startswith("ai_style_view:"))
async def ai_style_view(query: CallbackQuery):
    await query.answer()
    if not query.message or not query.data:
        return
    
    persona_id = query.data.replace("ai_style_view:", "")
    
    from core.ai_communication_styles import ai_communication_styles
    
    persona = ai_communication_styles.get_persona(persona_id)
    if not persona:
        await query.message.edit_text("❌ Стиль не знайдено")
        return
    
    text = ai_communication_styles.format_persona_info(persona)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Застосувати до всіх ботів", callback_data=f"ai_style_apply:{persona_id}")],
        [InlineKeyboardButton(text="🧪 Тестувати", callback_data=f"ai_style_test:{persona_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="ai_select_style")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@ai_styles_router.callback_query(F.data.startswith("ai_style_apply:"))
async def ai_style_apply(query: CallbackQuery):
    if not query.data:
        return
    
    persona_id = query.data.replace("ai_style_apply:", "")
    
    from core.ai_communication_styles import ai_communication_styles
    from core.session_manager import session_manager
    
    sessions = session_manager.get_active_sessions()
    applied = 0
    
    for session in sessions:
        bot_id = session.get("phone", session.get("session_id", "unknown"))
        if ai_communication_styles.set_active_persona(bot_id, persona_id):
            applied += 1
    
    persona = ai_communication_styles.get_persona(persona_id)
    name = persona.name if persona else persona_id
    
    await query.answer(f"✅ Стиль '{name}' застосовано до {applied} ботів", show_alert=True)


@ai_styles_router.callback_query(F.data.startswith("ai_style_test:"))
async def ai_style_test(query: CallbackQuery, state: FSMContext):
    await query.answer()
    if not query.message or not query.data:
        return
    
    persona_id = query.data.replace("ai_style_test:", "")
    await state.update_data(test_persona_id=persona_id)
    await state.set_state(AIStylesStates.waiting_test_message)
    
    from core.ai_communication_styles import ai_communication_styles
    persona = ai_communication_styles.get_persona(persona_id)
    name = persona.name if persona else persona_id
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data=f"ai_style_view:{persona_id}")]
    ])
    
    await query.message.edit_text(
        f"🧪 <b>ТЕСТ СТИЛЮ: {name}</b>\n"
        f"═══════════════════════\n\n"
        f"<b>Напишіть тестове повідомлення:</b>\n"
        f"<i>Наприклад: 'Привіт, як справи?'</i>",
        reply_markup=kb, parse_mode="HTML"
    )


@ai_styles_router.message(AIStylesStates.waiting_test_message)
async def process_test_message(message: Message, state: FSMContext):
    data = await state.get_data()
    persona_id = data.get("test_persona_id", "friendly_helper")
    user_message = message.text.strip() if message.text else ""
    await state.clear()
    
    if not user_message:
        await message.answer("❌ Порожнє повідомлення")
        return
    
    from core.ai_communication_styles import ai_communication_styles
    
    ai_communication_styles.set_active_persona("test_bot", persona_id)
    
    await message.answer("⏳ Генерую відповідь...")
    
    response = await ai_communication_styles.generate_response("test_bot", user_message)
    
    persona = ai_communication_styles.get_persona(persona_id)
    name = persona.name if persona else persona_id
    
    text = f"🧪 <b>РЕЗУЛЬТАТ ТЕСТУ</b>\n"
    text += f"═══════════════════════\n\n"
    text += f"<b>Стиль:</b> {name}\n\n"
    text += f"<b>Ваше повідомлення:</b>\n"
    text += f"<i>{user_message}</i>\n\n"
    text += f"<b>Відповідь бота:</b>\n"
    text += f"{response}"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Ще тест", callback_data=f"ai_style_test:{persona_id}")],
        [InlineKeyboardButton(text="◀️ До стилю", callback_data=f"ai_style_view:{persona_id}")]
    ])
    
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@ai_styles_router.callback_query(F.data == "ai_create_custom")
async def ai_create_custom(query: CallbackQuery, state: FSMContext):
    await query.answer()
    if not query.message:
        return
    
    await state.set_state(AIStylesStates.waiting_custom_name)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="ai_styles_menu")]
    ])
    
    await query.message.edit_text(
        "<b>➕ СТВОРЕННЯ КАСТОМНОГО СТИЛЮ</b>\n"
        "═══════════════════════\n\n"
        "<b>Крок 1/2: Назва стилю</b>\n\n"
        "<i>Введіть назву для нового стилю:</i>\n"
        "Наприклад: 'Веселий продавець'",
        reply_markup=kb, parse_mode="HTML"
    )


@ai_styles_router.message(AIStylesStates.waiting_custom_name)
async def process_custom_name(message: Message, state: FSMContext):
    name = message.text.strip() if message.text else ""
    
    if not name:
        await message.answer("❌ Введіть назву")
        return
    
    await state.update_data(custom_name=name)
    await state.set_state(AIStylesStates.waiting_custom_prompt)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="ai_styles_menu")]
    ])
    
    await message.answer(
        f"<b>➕ СТВОРЕННЯ: {name}</b>\n"
        f"═══════════════════════\n\n"
        f"<b>Крок 2/2: Опис поведінки</b>\n\n"
        f"<i>Опишіть як бот має спілкуватись:</i>\n\n"
        f"Наприклад:\n"
        f"'Ти веселий продавець. Використовуй багато емодзі. "
        f"Жартуй, але не забувай пропонувати товари. "
        f"Відповідай коротко та енергійно.'",
        reply_markup=kb, parse_mode="HTML"
    )


@ai_styles_router.message(AIStylesStates.waiting_custom_prompt)
async def process_custom_prompt(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("custom_name", "Кастомний стиль")
    prompt = message.text.strip() if message.text else ""
    await state.clear()
    
    if not prompt:
        await message.answer("❌ Введіть опис поведінки")
        return
    
    from core.ai_communication_styles import ai_communication_styles, CommunicationStyle, ConversationTopic
    
    persona = ai_communication_styles.create_custom_persona(
        name=name,
        style=CommunicationStyle.CASUAL,
        topic=ConversationTopic.CUSTOM,
        description=f"Кастомний стиль: {name}",
        custom_prompt=prompt
    )
    
    text = f"✅ <b>СТИЛЬ СТВОРЕНО!</b>\n"
    text += f"═══════════════════════\n\n"
    text += f"<b>Назва:</b> {persona.name}\n"
    text += f"<b>ID:</b> <code>{persona.persona_id}</code>\n\n"
    text += f"<b>Промпт:</b>\n<i>{prompt[:200]}...</i>"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧪 Тестувати", callback_data=f"ai_style_test:{persona.persona_id}")],
        [InlineKeyboardButton(text="📚 Додати приклади", callback_data=f"ai_train_persona:{persona.persona_id}")],
        [InlineKeyboardButton(text="◀️ До меню", callback_data="ai_styles_menu")]
    ])
    
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@ai_styles_router.callback_query(F.data == "ai_train_examples")
async def ai_train_examples(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    
    from core.ai_communication_styles import ai_communication_styles
    
    personas = ai_communication_styles.get_all_personas()
    
    text = "<b>📚 НАВЧАННЯ НА ПРИКЛАДАХ</b>\n"
    text += "═══════════════════════\n\n"
    text += "<i>Виберіть стиль для навчання:</i>\n\n"
    text += "Ви зможете додати приклади діалогів,\n"
    text += "щоб бот краще відповідав у вашому стилі."
    
    buttons = []
    for persona in personas[:10]:
        examples = len(ai_communication_styles.get_training_examples(persona.persona_id))
        badge = f" ({examples})" if examples > 0 else ""
        buttons.append([InlineKeyboardButton(
            text=f"📚 {persona.name}{badge}",
            callback_data=f"ai_train_persona:{persona.persona_id}"
        )])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="ai_styles_menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@ai_styles_router.callback_query(F.data.startswith("ai_train_persona:"))
async def ai_train_persona(query: CallbackQuery, state: FSMContext):
    await query.answer()
    if not query.message or not query.data:
        return
    
    persona_id = query.data.replace("ai_train_persona:", "")
    await state.update_data(train_persona_id=persona_id)
    await state.set_state(AIStylesStates.waiting_training_user)
    
    from core.ai_communication_styles import ai_communication_styles
    
    persona = ai_communication_styles.get_persona(persona_id)
    name = persona.name if persona else persona_id
    examples = ai_communication_styles.get_training_examples(persona_id)
    
    text = f"📚 <b>НАВЧАННЯ: {name}</b>\n"
    text += f"═══════════════════════\n\n"
    text += f"<b>Прикладів:</b> {len(examples)}\n\n"
    text += "<b>Введіть приклад повідомлення користувача:</b>\n"
    text += "<i>Наприклад: 'Скільки коштує доставка?'</i>"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="ai_train_examples")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@ai_styles_router.message(AIStylesStates.waiting_training_user)
async def process_training_user(message: Message, state: FSMContext):
    user_msg = message.text.strip() if message.text else ""
    
    if not user_msg:
        await message.answer("❌ Введіть повідомлення")
        return
    
    await state.update_data(train_user_msg=user_msg)
    await state.set_state(AIStylesStates.waiting_training_response)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="ai_train_examples")]
    ])
    
    await message.answer(
        f"📚 <b>НАВЧАННЯ</b>\n"
        f"═══════════════════════\n\n"
        f"<b>Повідомлення користувача:</b>\n"
        f"<i>{user_msg}</i>\n\n"
        f"<b>Тепер введіть ідеальну відповідь бота:</b>",
        reply_markup=kb, parse_mode="HTML"
    )


@ai_styles_router.message(AIStylesStates.waiting_training_response)
async def process_training_response(message: Message, state: FSMContext):
    data = await state.get_data()
    persona_id = data.get("train_persona_id")
    user_msg = data.get("train_user_msg", "")
    response = message.text.strip() if message.text else ""
    await state.clear()
    
    if not response:
        await message.answer("❌ Введіть відповідь")
        return
    
    from core.ai_communication_styles import ai_communication_styles
    
    ai_communication_styles.add_training_example(persona_id, user_msg, response)
    
    persona = ai_communication_styles.get_persona(persona_id)
    name = persona.name if persona else persona_id
    total = len(ai_communication_styles.get_training_examples(persona_id))
    
    text = f"✅ <b>ПРИКЛАД ДОДАНО!</b>\n"
    text += f"═══════════════════════\n\n"
    text += f"<b>Стиль:</b> {name}\n"
    text += f"<b>Всього прикладів:</b> {total}\n\n"
    text += f"<b>Користувач:</b>\n<i>{user_msg}</i>\n\n"
    text += f"<b>Відповідь:</b>\n<i>{response}</i>"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Ще приклад", callback_data=f"ai_train_persona:{persona_id}")],
        [InlineKeyboardButton(text="🧪 Тестувати", callback_data=f"ai_style_test:{persona_id}")],
        [InlineKeyboardButton(text="◀️ До меню", callback_data="ai_styles_menu")]
    ])
    
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@ai_styles_router.callback_query(F.data == "ai_test_response")
async def ai_test_response(query: CallbackQuery, state: FSMContext):
    await query.answer()
    if not query.message:
        return
    
    await state.update_data(test_persona_id="friendly_helper")
    await state.set_state(AIStylesStates.waiting_test_message)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Скасувати", callback_data="ai_styles_menu")]
    ])
    
    await query.message.edit_text(
        "<b>🧪 ТЕСТУВАННЯ ВІДПОВІДЕЙ</b>\n"
        "═══════════════════════\n\n"
        "<i>Використовується активний стиль бота</i>\n\n"
        "<b>Напишіть тестове повідомлення:</b>",
        reply_markup=kb, parse_mode="HTML"
    )


@ai_styles_router.callback_query(F.data == "ai_styles_stats")
async def ai_styles_stats(query: CallbackQuery):
    await query.answer()
    if not query.message:
        return
    
    from core.ai_communication_styles import ai_communication_styles
    
    stats = ai_communication_styles.get_stats()
    
    text = "<b>📊 СТАТИСТИКА AI СТИЛІВ</b>\n"
    text += "═══════════════════════\n\n"
    text += f"<b>Загальна інформація:</b>\n"
    text += f"├ Всього стилів: {stats['total_personas']}\n"
    text += f"├ Кастомних: {stats['custom_personas']}\n"
    text += f"├ Активних: {stats['active_assignments']}\n"
    text += f"└ Прикладів: {stats['training_examples']}\n\n"
    
    text += "<b>Призначені стилі:</b>\n"
    for bot_id, persona_id in ai_communication_styles.active_personas.items():
        persona = ai_communication_styles.get_persona(persona_id)
        name = persona.name if persona else persona_id
        text += f"├ {bot_id[:15]}... → {name}\n"
    
    if not ai_communication_styles.active_personas:
        text += "<i>Немає призначень</i>"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="ai_styles_menu")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")