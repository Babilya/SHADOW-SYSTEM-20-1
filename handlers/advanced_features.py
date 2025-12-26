from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
advanced_router = Router()

class ScheduleMailingStates(StatesGroup):
    waiting_name = State()
    waiting_text = State()
    waiting_datetime = State()
    waiting_ab_variants = State()

class AutoResponseStates(StatesGroup):
    waiting_keyword = State()
    waiting_response = State()
    waiting_match_type = State()

def get_advanced_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Планувальник розсилок", callback_data="adv_scheduler")],
        [InlineKeyboardButton(text="🤖 Авто-відповіді", callback_data="adv_autoresponder")],
        [InlineKeyboardButton(text="📊 A/B тестування", callback_data="adv_ab_testing")],
        [InlineKeyboardButton(text="🏷️ Сегментація", callback_data="adv_segmentation")],
        [InlineKeyboardButton(text="📤 CRM експорт", callback_data="adv_crm_export")],
        [InlineKeyboardButton(text="📄 PDF звіти", callback_data="adv_pdf_export")],
        [InlineKeyboardButton(text="🔐 Безпека", callback_data="adv_security")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_start")]
    ])

@advanced_router.callback_query(F.data == "advanced_features")
async def advanced_features_menu(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text(
        "🚀 <b>РОЗШИРЕНІ ФУНКЦІЇ</b>\n\n"
        "Оберіть розділ:",
        reply_markup=get_advanced_menu(),
        parse_mode="HTML"
    )

@advanced_router.callback_query(F.data == "adv_scheduler")
async def scheduler_menu(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Нова розсилка", callback_data="schedule_new")],
        [InlineKeyboardButton(text="📋 Заплановані", callback_data="schedule_list")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="advanced_features")]
    ])
    await query.message.edit_text(
        "📅 <b>ПЛАНУВАЛЬНИК РОЗСИЛОК</b>\n\n"
        "Створюйте відкладені розсилки на конкретний час.\n\n"
        "Функції:\n"
        "• Відкладена публікація\n"
        "• A/B тестування повідомлень\n"
        "• Прогрес у реальному часі",
        reply_markup=kb,
        parse_mode="HTML"
    )

@advanced_router.callback_query(F.data == "schedule_new")
async def schedule_new(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(ScheduleMailingStates.waiting_name)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="adv_scheduler")]
    ])
    await query.message.edit_text(
        "📝 <b>Нова запланована розсилка</b>\n\n"
        "Введіть назву розсилки:",
        reply_markup=kb,
        parse_mode="HTML"
    )

@advanced_router.message(ScheduleMailingStates.waiting_name)
async def schedule_name_received(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(ScheduleMailingStates.waiting_text)
    await message.answer(
        "✏️ Тепер введіть текст повідомлення для розсилки:",
        parse_mode="HTML"
    )

@advanced_router.message(ScheduleMailingStates.waiting_text)
async def schedule_text_received(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(ScheduleMailingStates.waiting_datetime)
    await message.answer(
        "🕐 Введіть дату та час розсилки у форматі:\n"
        "<code>ДД.ММ.РРРР ГГ:ХХ</code>\n\n"
        "Приклад: <code>25.12.2025 14:30</code>",
        parse_mode="HTML"
    )

@advanced_router.message(ScheduleMailingStates.waiting_datetime)
async def schedule_datetime_received(message: Message, state: FSMContext):
    try:
        scheduled_at = datetime.strptime(message.text, "%d.%m.%Y %H:%M")
        if scheduled_at <= datetime.now():
            await message.answer("❌ Дата повинна бути в майбутньому")
            return
        
        data = await state.get_data()
        await state.clear()
        
        from core.mailing_scheduler import mailing_scheduler
        mailing_id = await mailing_scheduler.schedule(
            project_id=str(message.from_user.id),
            name=data['name'],
            message_text=data['text'],
            scheduled_at=scheduled_at,
            created_by=message.from_user.id
        )
        
        await message.answer(
            f"✅ <b>Розсилку заплановано!</b>\n\n"
            f"📝 Назва: {data['name']}\n"
            f"📅 Час: {scheduled_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"🆔 ID: {mailing_id}",
            parse_mode="HTML"
        )
    except ValueError:
        await message.answer("❌ Невірний формат. Введіть у форматі: ДД.ММ.РРРР ГГ:ХХ")

@advanced_router.callback_query(F.data == "schedule_list")
async def schedule_list(query: CallbackQuery):
    await query.answer()
    from core.mailing_scheduler import mailing_scheduler
    
    mailings = mailing_scheduler.get_scheduled(str(query.from_user.id))
    
    if not mailings:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Створити", callback_data="schedule_new")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="adv_scheduler")]
        ])
        await query.message.edit_text(
            "📋 <b>Заплановані розсилки</b>\n\nСписок порожній.",
            reply_markup=kb,
            parse_mode="HTML"
        )
        return
    
    text = "📋 <b>Заплановані розсилки:</b>\n\n"
    for m in mailings[:10]:
        text += f"• {m.name} - {m.scheduled_at.strftime('%d.%m %H:%M')}\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="adv_scheduler")]
    ])
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@advanced_router.callback_query(F.data == "adv_autoresponder")
async def autoresponder_menu(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Додати відповідь", callback_data="auto_add")],
        [InlineKeyboardButton(text="📋 Список відповідей", callback_data="auto_list")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="advanced_features")]
    ])
    await query.message.edit_text(
        "🤖 <b>АВТО-ВІДПОВІДІ</b>\n\n"
        "Налаштуйте автоматичні відповіді за ключовими словами.\n\n"
        "• Точний збіг\n"
        "• Містить слово\n"
        "• Regex патерни",
        reply_markup=kb,
        parse_mode="HTML"
    )

@advanced_router.callback_query(F.data == "auto_add")
async def auto_add(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(AutoResponseStates.waiting_keyword)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="adv_autoresponder")]
    ])
    await query.message.edit_text(
        "🔑 <b>Нова авто-відповідь</b>\n\n"
        "Введіть ключове слово або фразу:",
        reply_markup=kb,
        parse_mode="HTML"
    )

@advanced_router.message(AutoResponseStates.waiting_keyword)
async def auto_keyword_received(message: Message, state: FSMContext):
    await state.update_data(keyword=message.text)
    await state.set_state(AutoResponseStates.waiting_response)
    await message.answer("📝 Введіть текст відповіді:")

@advanced_router.message(AutoResponseStates.waiting_response)
async def auto_response_received(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    
    from core.auto_responder import auto_responder
    response_id = await auto_responder.add_response(
        project_id=str(message.from_user.id),
        keyword=data['keyword'],
        response_text=message.text
    )
    
    await message.answer(
        f"✅ <b>Авто-відповідь додано!</b>\n\n"
        f"🔑 Ключ: {data['keyword']}\n"
        f"📝 Відповідь: {message.text[:50]}...",
        parse_mode="HTML"
    )

@advanced_router.callback_query(F.data == "auto_list")
async def auto_list(query: CallbackQuery):
    await query.answer()
    from core.auto_responder import auto_responder
    
    responses = await auto_responder.get_all_responses(str(query.from_user.id))
    
    if not responses:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Додати", callback_data="auto_add")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="adv_autoresponder")]
        ])
        await query.message.edit_text(
            "📋 <b>Авто-відповіді</b>\n\nСписок порожній.",
            reply_markup=kb,
            parse_mode="HTML"
        )
        return
    
    text = "📋 <b>Авто-відповіді:</b>\n\n"
    for r in responses[:10]:
        text += f"• <code>{r.keyword}</code> → {r.response_text[:30]}...\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="adv_autoresponder")]
    ])
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@advanced_router.callback_query(F.data == "adv_segmentation")
async def segmentation_menu(query: CallbackQuery):
    await query.answer()
    from core.segmentation import segmentation_service
    
    stats = await segmentation_service.get_segment_stats()
    
    text = "🏷️ <b>СЕГМЕНТАЦІЯ АУДИТОРІЇ</b>\n\n"
    if stats:
        text += "Статистика по тегам:\n"
        for tag, count in stats.items():
            text += f"• {tag}: {count} користувачів\n"
    else:
        text += "Немає даних для відображення."
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="adv_segmentation")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="advanced_features")]
    ])
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@advanced_router.callback_query(F.data == "adv_crm_export")
async def crm_export_menu(query: CallbackQuery):
    await query.answer()
    from core.crm_export import crm_export_service
    
    adapters = crm_export_service.get_available_adapters()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Notion", callback_data="crm_notion")],
        [InlineKeyboardButton(text="📊 Google Sheets", callback_data="crm_sheets")],
        [InlineKeyboardButton(text="📋 Airtable", callback_data="crm_airtable")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="advanced_features")]
    ])
    
    text = "📤 <b>CRM ЕКСПОРТ</b>\n\n"
    text += f"Налаштовано: {len(adapters)} інтеграцій\n\n"
    text += "Оберіть платформу для експорту:"
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@advanced_router.callback_query(F.data == "adv_pdf_export")
async def pdf_export_menu(query: CallbackQuery):
    await query.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Аналітика", callback_data="pdf_analytics")],
        [InlineKeyboardButton(text="📋 Аудит", callback_data="pdf_audit")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="advanced_features")]
    ])
    await query.message.edit_text(
        "📄 <b>PDF ЗВІТИ</b>\n\n"
        "Генеруйте брендовані звіти:\n\n"
        "• Аналітичний звіт по проекту\n"
        "• Звіт аудиту дій",
        reply_markup=kb,
        parse_mode="HTML"
    )

@advanced_router.callback_query(F.data == "pdf_analytics")
async def pdf_analytics(query: CallbackQuery):
    await query.answer("⏳ Генерую звіт...")
    try:
        from core.pdf_export import pdf_export_service
        
        pdf_data = await pdf_export_service.generate_analytics_report(
            project_id=str(query.from_user.id),
            days=30
        )
        
        from aiogram.types import BufferedInputFile
        file = BufferedInputFile(pdf_data, filename=f"analytics_{datetime.now().strftime('%Y%m%d')}.pdf")
        
        await query.message.answer_document(
            file,
            caption="📊 Аналітичний звіт згенеровано"
        )
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        await query.message.answer(f"❌ Помилка генерації: {e}")

@advanced_router.callback_query(F.data == "pdf_audit")
async def pdf_audit(query: CallbackQuery):
    await query.answer("⏳ Генерую звіт...")
    try:
        from core.pdf_export import pdf_export_service
        
        pdf_data = await pdf_export_service.generate_audit_report(
            user_id=query.from_user.id,
            days=7
        )
        
        from aiogram.types import BufferedInputFile
        file = BufferedInputFile(pdf_data, filename=f"audit_{datetime.now().strftime('%Y%m%d')}.pdf")
        
        await query.message.answer_document(
            file,
            caption="📋 Звіт аудиту згенеровано"
        )
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        await query.message.answer(f"❌ Помилка генерації: {e}")

@advanced_router.callback_query(F.data == "adv_security")
async def security_menu(query: CallbackQuery):
    await query.answer()
    from core.antifraud import antifraud_service
    from core.login_tracker import login_tracker
    
    stats = antifraud_service.get_user_stats(query.from_user.id)
    history = await login_tracker.get_login_history(query.from_user.id, limit=5)
    
    text = "🔐 <b>БЕЗПЕКА</b>\n\n"
    text += f"• Попереджень: {stats.get('warnings', 0)}\n"
    text += f"• Статус: {'🔴 Заблоковано' if stats.get('is_blocked') else '🟢 Активний'}\n\n"
    
    if history:
        text += "Останні входи:\n"
        for h in history[:3]:
            text += f"• {h.get('country', 'N/A')} - {h.get('created_at', 'N/A')}\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛡️ IP Whitelist", callback_data="sec_whitelist")],
        [InlineKeyboardButton(text="📜 Історія входів", callback_data="sec_history")],
        [InlineKeyboardButton(text="💾 Бекапи", callback_data="sec_backups")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="advanced_features")]
    ])
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@advanced_router.callback_query(F.data == "sec_backups")
async def security_backups(query: CallbackQuery):
    await query.answer()
    from core.encrypted_backup import encrypted_backup_service
    
    backups = await encrypted_backup_service.get_backups(limit=5)
    
    text = "💾 <b>ЗАШИФРОВАНІ БЕКАПИ</b>\n\n"
    if backups:
        for b in backups:
            text += f"• {b['type']} - {b['created_at']}\n"
    else:
        text += "Бекапів ще немає."
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💾 Створити бекап", callback_data="backup_create")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="adv_security")]
    ])
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@advanced_router.callback_query(F.data == "backup_create")
async def create_backup(query: CallbackQuery):
    await query.answer("⏳ Створюю бекап...")
    from core.encrypted_backup import encrypted_backup_service
    
    key_backup = await encrypted_backup_service.backup_keys()
    session_backup = await encrypted_backup_service.backup_sessions()
    
    text = "✅ <b>Бекап створено!</b>\n\n"
    if key_backup:
        text += f"• Ключі: ID {key_backup}\n"
    if session_backup:
        text += f"• Сесії: ID {session_backup}\n"
    
    await query.message.answer(text, parse_mode="HTML")
