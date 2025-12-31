"""
Обробники для модулів криміналістики та покращеного моніторингу
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from keyboards.role_menus import (
    forensics_main_kb, forensic_snapshot_kb, ai_sentiment_kb,
    ghost_recovery_kb, xray_metadata_kb, memory_indexer_kb,
    monitoring_main_kb, monitoring_target_kb, monitoring_alerts_kb,
    back_to_forensics_kb, trigger_types_kb, alert_action_kb
)

logger = logging.getLogger(__name__)
forensics_router = Router()

class ForensicsStates(StatesGroup):
    waiting_text_analyze = State()
    waiting_file_analyze = State()
    waiting_search_query = State()
    waiting_target_id = State()
    waiting_keyword = State()
    waiting_regex = State()


@forensics_router.callback_query(F.data == "forensics_menu")
async def forensics_menu(query: CallbackQuery):
    """Головне меню криміналістики"""
    await query.answer()
    if not query.message:
        return
    
    text = """<b>🔬 КРИМІНАЛІСТИКА ТА АНАЛІЗ</b>
<i>Професійні інструменти розслідування</i>

───────────────

<b>📦 ДОСТУПНІ МОДУЛІ:</b>

<b>🔬 Forensic Snapshot</b>
Автоматичне збереження медіа з метаданими

<b>🧠 AI Sentiment</b>
AI-аналіз настрою та емоцій

<b>👻 Anti-Ghost Recovery</b>
Відновлення видалених повідомлень

<b>🔍 X-Ray Metadata</b>
Глибокий аналіз метаданих файлів

<b>💾 Memory Indexer</b>
Швидкий пошук в пам'яті

<b>📡 Enhanced Monitoring</b>
Розширений моніторинг каналів"""
    
    await query.message.edit_text(text, reply_markup=forensics_main_kb(), parse_mode="HTML")


@forensics_router.callback_query(F.data == "forensic_main")
async def forensic_main(query: CallbackQuery):
    """Меню Forensic Snapshot"""
    await query.answer()
    if not query.message:
        return
    
    from core.forensic_snapshot import forensic_snapshot
    text = forensic_snapshot.format_report()
    
    await query.message.edit_text(text, reply_markup=forensic_snapshot_kb(), parse_mode="HTML")


@forensics_router.callback_query(F.data == "forensic_stats")
async def forensic_stats(query: CallbackQuery):
    """Статистика Forensic Snapshot"""
    await query.answer()
    if not query.message:
        return
    
    from core.forensic_snapshot import forensic_snapshot
    text = forensic_snapshot.format_report()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="forensic_stats")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="forensic_main")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@forensics_router.callback_query(F.data == "forensic_list")
async def forensic_list(query: CallbackQuery):
    """Список знімків"""
    await query.answer()
    if not query.message:
        return
    
    from core.forensic_snapshot import forensic_snapshot
    snapshots = forensic_snapshot.get_all_snapshots(limit=10)
    
    text = "<b>📋 FORENSIC SNAPSHOTS</b>\n\n"
    
    if not snapshots:
        text += "<i>Знімків ще немає</i>"
    else:
        for i, s in enumerate(snapshots, 1):
            status = "🗑" if s['deleted'] else "✅"
            text += f"{i}. {status} <code>{s['hash']}</code>\n"
            text += f"   └ {s['type']} | {s['size']} bytes\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="forensic_list")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="forensic_main")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@forensics_router.callback_query(F.data == "sentiment_main")
async def sentiment_main(query: CallbackQuery):
    """Меню AI Sentiment"""
    await query.answer()
    if not query.message:
        return
    
    from core.ai_sentiment import ai_sentiment
    text = ai_sentiment.format_stats_report()
    
    await query.message.edit_text(text, reply_markup=ai_sentiment_kb(), parse_mode="HTML")


@forensics_router.callback_query(F.data == "sentiment_analyze")
async def sentiment_analyze_start(query: CallbackQuery, state: FSMContext):
    """Початок аналізу тексту"""
    await query.answer()
    if not query.message:
        return
    
    await state.set_state(ForensicsStates.waiting_text_analyze)
    
    text = """<b>🧠 AI SENTIMENT ANALYSIS</b>

Надішліть текст для аналізу настрою.

<i>Можна надіслати будь-який текст українською або англійською мовою.</i>"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="sentiment_main")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@forensics_router.message(ForensicsStates.waiting_text_analyze)
async def sentiment_analyze_process(message: Message, state: FSMContext):
    """Обробка тексту для аналізу"""
    await state.clear()
    
    if not message.text:
        await message.answer("❌ Надішліть текст для аналізу")
        return
    
    from core.ai_sentiment import ai_sentiment
    
    status_msg = await message.answer("🔄 Аналізую...")
    
    result = await ai_sentiment.analyze_sentiment(message.text, use_ai=True)
    report = ai_sentiment.format_result(result)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Ще аналіз", callback_data="sentiment_analyze")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="sentiment_main")]
    ])
    
    await status_msg.edit_text(report, reply_markup=kb, parse_mode="HTML")


@forensics_router.callback_query(F.data == "sentiment_stats")
async def sentiment_stats(query: CallbackQuery):
    """Статистика AI Sentiment"""
    await query.answer()
    if not query.message:
        return
    
    from core.ai_sentiment import ai_sentiment
    text = ai_sentiment.format_stats_report()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="sentiment_stats")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="sentiment_main")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@forensics_router.callback_query(F.data == "ghost_main")
async def ghost_main(query: CallbackQuery):
    """Меню Anti-Ghost Recovery"""
    await query.answer()
    if not query.message:
        return
    
    from core.anti_ghost_recovery import anti_ghost
    text = anti_ghost.format_stats_report()
    
    await query.message.edit_text(text, reply_markup=ghost_recovery_kb(), parse_mode="HTML")


@forensics_router.callback_query(F.data == "ghost_stats")
async def ghost_stats(query: CallbackQuery):
    """Статистика Anti-Ghost"""
    await query.answer()
    if not query.message:
        return
    
    from core.anti_ghost_recovery import anti_ghost
    text = anti_ghost.format_stats_report()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="ghost_stats")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="ghost_main")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@forensics_router.callback_query(F.data == "ghost_deleted")
async def ghost_deleted(query: CallbackQuery):
    """Список видалених повідомлень"""
    await query.answer()
    if not query.message:
        return
    
    from core.anti_ghost_recovery import anti_ghost
    
    text = """<b>🗑 ВИДАЛЕНІ ПОВІДОМЛЕННЯ</b>

<i>Для перегляду видалених повідомлень, виберіть чат.</i>

Видалені повідомлення автоматично зберігаються при активному моніторингу."""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="ghost_deleted")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="ghost_main")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@forensics_router.callback_query(F.data == "xray_main")
async def xray_main(query: CallbackQuery):
    """Меню X-Ray Metadata"""
    await query.answer()
    if not query.message:
        return
    
    from core.xray_metadata import xray_metadata
    text = xray_metadata.format_stats_report()
    
    await query.message.edit_text(text, reply_markup=xray_metadata_kb(), parse_mode="HTML")


@forensics_router.callback_query(F.data == "xray_analyze")
async def xray_analyze_start(query: CallbackQuery, state: FSMContext):
    """Початок аналізу файлу"""
    await query.answer()
    if not query.message:
        return
    
    await state.set_state(ForensicsStates.waiting_file_analyze)
    
    text = """<b>🔍 X-RAY METADATA</b>

Надішліть файл для глибокого аналізу.

<b>Підтримуються:</b>
├ 🖼 Зображення (JPEG, PNG, GIF)
├ 📹 Відео (MP4, MOV, WebM)
├ 📄 Документи (PDF, DOCX)
└ 🎵 Аудіо (MP3, OGG)"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="xray_main")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@forensics_router.message(ForensicsStates.waiting_file_analyze)
async def xray_analyze_process(message: Message, state: FSMContext):
    """Обробка файлу для аналізу"""
    await state.clear()
    
    if not message.document and not message.photo:
        await message.answer("❌ Надішліть файл або фото для аналізу")
        return
    
    if not message.bot:
        await message.answer("❌ Помилка бота")
        return
    
    from core.xray_metadata import xray_metadata
    
    status_msg = await message.answer("🔄 Аналізую метадані...")
    
    try:
        if message.photo:
            file = await message.bot.get_file(message.photo[-1].file_id)
            file_info = {"file_id": message.photo[-1].file_id, "mime_type": "image/jpeg"}
        else:
            if not message.document:
                await status_msg.edit_text("❌ Файл не знайдено")
                return
            file = await message.bot.get_file(message.document.file_id)
            file_info = {
                "file_id": message.document.file_id,
                "mime_type": message.document.mime_type or "unknown",
                "file_name": message.document.file_name
            }
        
        if not file.file_path:
            await status_msg.edit_text("❌ Не вдалося отримати файл")
            return
        
        file_content = await message.bot.download_file(file.file_path)
        if not file_content:
            await status_msg.edit_text("❌ Не вдалося завантажити файл")
            return
        
        file_data = file_content.read()
        
        result = await xray_metadata.analyze(file_data, file_info)
        report = xray_metadata.format_result(result)
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Ще аналіз", callback_data="xray_analyze")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="xray_main")]
        ])
        
        await status_msg.edit_text(report, reply_markup=kb, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"X-Ray analysis error: {e}")
        await status_msg.edit_text(f"❌ Помилка аналізу: {e}")


@forensics_router.callback_query(F.data == "xray_stats")
async def xray_stats(query: CallbackQuery):
    """Статистика X-Ray"""
    await query.answer()
    if not query.message:
        return
    
    from core.xray_metadata import xray_metadata
    text = xray_metadata.format_stats_report()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="xray_stats")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="xray_main")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@forensics_router.callback_query(F.data == "indexer_main")
async def indexer_main(query: CallbackQuery):
    """Меню Memory Indexer"""
    await query.answer()
    if not query.message:
        return
    
    from core.memory_indexer import memory_indexer
    text = memory_indexer.format_stats_report()
    
    await query.message.edit_text(text, reply_markup=memory_indexer_kb(), parse_mode="HTML")


@forensics_router.callback_query(F.data == "indexer_search")
async def indexer_search_start(query: CallbackQuery, state: FSMContext):
    """Початок пошуку"""
    await query.answer()
    if not query.message:
        return
    
    await state.set_state(ForensicsStates.waiting_search_query)
    
    text = """<b>🔍 ПОШУК В ІНДЕКСІ</b>

Введіть пошуковий запит.

<i>Пошук здійснюється по повідомленнях, користувачах та медіа.</i>"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="indexer_main")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@forensics_router.message(ForensicsStates.waiting_search_query)
async def indexer_search_process(message: Message, state: FSMContext):
    """Обробка пошукового запиту"""
    await state.clear()
    
    if not message.text:
        await message.answer("❌ Введіть пошуковий запит")
        return
    
    from core.memory_indexer import memory_indexer
    
    results = await memory_indexer.search(message.text, limit=10)
    
    if not results:
        text = f"<b>🔍 Результати пошуку:</b>\n\n<i>Нічого не знайдено за запитом: {message.text}</i>"
    else:
        text = f"<b>🔍 Результати пошуку:</b> ({len(results)})\n\n"
        for r in results[:5]:
            text += memory_indexer.format_search_result(r) + "\n\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Новий пошук", callback_data="indexer_search")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="indexer_main")]
    ])
    
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@forensics_router.callback_query(F.data == "indexer_stats")
async def indexer_stats(query: CallbackQuery):
    """Статистика Memory Indexer"""
    await query.answer()
    if not query.message:
        return
    
    from core.memory_indexer import memory_indexer
    text = memory_indexer.format_stats_report()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="indexer_stats")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="indexer_main")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@forensics_router.callback_query(F.data == "monitoring_main")
async def monitoring_main(query: CallbackQuery):
    """Меню Enhanced Monitoring"""
    await query.answer()
    if not query.message:
        return
    
    from core.enhanced_monitoring import enhanced_monitoring
    text = enhanced_monitoring.format_stats_report()
    
    await query.message.edit_text(text, reply_markup=monitoring_main_kb(), parse_mode="HTML")


@forensics_router.callback_query(F.data == "monitor_add")
async def monitor_add_start(query: CallbackQuery, state: FSMContext):
    """Початок додавання цілі"""
    await query.answer()
    if not query.message:
        return
    
    await state.set_state(ForensicsStates.waiting_target_id)
    
    text = """<b>➕ ДОДАВАННЯ ЦІЛІ МОНІТОРИНГУ</b>

Надішліть ID або @username каналу/чату/користувача.

<b>Приклади:</b>
├ @channel_name
├ @username
└ -1001234567890"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="monitoring_main")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@forensics_router.message(ForensicsStates.waiting_target_id)
async def monitor_add_process(message: Message, state: FSMContext):
    """Обробка ID цілі"""
    await state.clear()
    
    if not message.text:
        await message.answer("❌ Введіть ID або username")
        return
    
    from core.enhanced_monitoring import enhanced_monitoring
    
    target_input = message.text.strip()
    
    if target_input.startswith("@"):
        target_type = "channel"
        name = target_input
        target_id = hash(target_input) % 10000000000
        username = target_input[1:]
    elif target_input.lstrip("-").isdigit():
        target_id = int(target_input)
        if target_id < 0:
            target_type = "chat" if target_id > -1000000000000 else "channel"
        else:
            target_type = "user"
        name = f"Target {target_id}"
        username = ""
    else:
        await message.answer("❌ Невірний формат. Використовуйте @username або ID")
        return
    
    target = await enhanced_monitoring.add_target(
        target_id=target_id,
        target_type=target_type,
        name=name,
        username=username
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔔 Додати тригери", callback_data=f"monitor_target_triggers:{target_id}")],
        [InlineKeyboardButton(text="◀️ До списку", callback_data="monitor_targets")]
    ])
    
    await message.answer(
        f"✅ <b>Ціль додано!</b>\n\n"
        f"<b>Тип:</b> {target_type}\n"
        f"<b>ID:</b> <code>{target_id}</code>\n"
        f"<b>Статус:</b> 🟢 Активний",
        reply_markup=kb,
        parse_mode="HTML"
    )


@forensics_router.callback_query(F.data == "monitor_targets")
async def monitor_targets(query: CallbackQuery):
    """Список цілей моніторингу"""
    await query.answer()
    if not query.message:
        return
    
    from core.enhanced_monitoring import enhanced_monitoring
    
    targets = list(enhanced_monitoring.targets.values())
    
    text = "<b>🎯 МОЇ ЦІЛІ МОНІТОРИНГУ</b>\n\n"
    
    if not targets:
        text += "<i>Цілей ще немає. Додайте першу!</i>"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Додати ціль", callback_data="monitor_add")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="monitoring_main")]
        ])
    else:
        buttons = []
        for t in targets[:10]:
            status = "🟢" if t.is_active else "🔴"
            type_icon = {"channel": "📢", "chat": "💬", "user": "👤"}.get(t.target_type, "📝")
            buttons.append([InlineKeyboardButton(
                text=f"{status} {type_icon} {t.name[:30]}",
                callback_data=f"monitor_view:{t.target_id}"
            )])
        
        buttons.append([InlineKeyboardButton(text="➕ Додати ціль", callback_data="monitor_add")])
        buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="monitoring_main")])
        
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@forensics_router.callback_query(F.data.startswith("monitor_view:"))
async def monitor_view(query: CallbackQuery):
    """Перегляд цілі"""
    await query.answer()
    if not query.message or not query.data:
        return
    
    target_id = int(query.data.split(":")[1])
    
    from core.enhanced_monitoring import enhanced_monitoring
    
    if target_id not in enhanced_monitoring.targets:
        await query.message.edit_text("❌ Ціль не знайдено")
        return
    
    target = enhanced_monitoring.targets[target_id]
    text = enhanced_monitoring.format_target_info(target)
    
    await query.message.edit_text(
        text, 
        reply_markup=monitoring_target_kb(target_id, target.is_active),
        parse_mode="HTML"
    )


@forensics_router.callback_query(F.data.startswith("monitor_toggle:"))
async def monitor_toggle(query: CallbackQuery):
    """Увімкнення/вимкнення моніторингу"""
    await query.answer()
    if not query.message or not query.data:
        return
    
    target_id = int(query.data.split(":")[1])
    
    from core.enhanced_monitoring import enhanced_monitoring
    
    is_active = await enhanced_monitoring.toggle_target(target_id)
    status = "🟢 Активовано" if is_active else "🔴 Вимкнено"
    
    await query.answer(f"Моніторинг {status}")
    
    if target_id in enhanced_monitoring.targets:
        target = enhanced_monitoring.targets[target_id]
        text = enhanced_monitoring.format_target_info(target)
        await query.message.edit_text(
            text,
            reply_markup=monitoring_target_kb(target_id, is_active),
            parse_mode="HTML"
        )


@forensics_router.callback_query(F.data.startswith("monitor_delete:"))
async def monitor_delete(query: CallbackQuery):
    """Видалення цілі"""
    await query.answer("Ціль видалено!")
    if not query.message or not query.data:
        return
    
    target_id = int(query.data.split(":")[1])
    
    from core.enhanced_monitoring import enhanced_monitoring
    await enhanced_monitoring.remove_target(target_id)
    
    await query.message.edit_text(
        "✅ <b>Ціль видалено!</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ До списку", callback_data="monitor_targets")]
        ]),
        parse_mode="HTML"
    )


@forensics_router.callback_query(F.data == "monitor_alerts")
async def monitor_alerts(query: CallbackQuery):
    """Сповіщення моніторингу"""
    await query.answer()
    if not query.message:
        return
    
    from core.enhanced_monitoring import enhanced_monitoring
    
    alerts = enhanced_monitoring.get_recent_alerts(unacknowledged_only=True, limit=10)
    
    text = "<b>⚠️ СПОВІЩЕННЯ</b>\n\n"
    
    if not alerts:
        text += "<i>Немає нових сповіщень</i>"
    else:
        for alert in alerts[:5]:
            text += enhanced_monitoring.format_alert(alert) + "\n\n"
    
    await query.message.edit_text(
        text,
        reply_markup=monitoring_alerts_kb(len(alerts)),
        parse_mode="HTML"
    )


@forensics_router.callback_query(F.data == "monitor_stats")
async def monitor_stats(query: CallbackQuery):
    """Статистика моніторингу"""
    await query.answer()
    if not query.message:
        return
    
    from core.enhanced_monitoring import enhanced_monitoring
    text = enhanced_monitoring.format_stats_report()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Оновити", callback_data="monitor_stats")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="monitoring_main")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@forensics_router.callback_query(F.data.startswith("monitor_target_triggers:"))
async def monitor_target_triggers(query: CallbackQuery):
    """Тригери цілі"""
    await query.answer()
    if not query.message or not query.data:
        return
    
    target_id = int(query.data.split(":")[1])
    
    from core.enhanced_monitoring import enhanced_monitoring
    
    keywords = enhanced_monitoring.keyword_triggers.get(target_id, [])
    
    text = f"<b>🔔 ТРИГЕРИ ЦІЛІ</b>\n\n"
    text += f"<b>🔤 Ключові слова ({len(keywords)}):</b>\n"
    
    if keywords:
        for kw in keywords[:10]:
            text += f"├ {kw}\n"
    else:
        text += "<i>Немає тригерів</i>\n"
    
    await query.message.edit_text(text, reply_markup=trigger_types_kb(target_id), parse_mode="HTML")


@forensics_router.callback_query(F.data.startswith("trigger_keyword:"))
async def trigger_keyword_start(query: CallbackQuery, state: FSMContext):
    """Додавання тригера ключового слова"""
    await query.answer()
    if not query.message or not query.data:
        return
    
    target_id = int(query.data.split(":")[1])
    await state.update_data(trigger_target_id=target_id)
    await state.set_state(ForensicsStates.waiting_keyword)
    
    text = """<b>🔤 ДОДАВАННЯ КЛЮЧОВОГО СЛОВА</b>

Введіть ключове слово для тригера.

<i>При знаходженні цього слова в повідомленні, ви отримаєте сповіщення.</i>"""
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data=f"monitor_target_triggers:{target_id}")]
    ])
    
    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@forensics_router.message(ForensicsStates.waiting_keyword)
async def trigger_keyword_save(message: Message, state: FSMContext):
    """Збереження тригера"""
    data = await state.get_data()
    target_id = data.get("trigger_target_id")
    await state.clear()
    
    if not message.text or not target_id:
        await message.answer("❌ Введіть ключове слово")
        return
    
    from core.enhanced_monitoring import enhanced_monitoring
    await enhanced_monitoring.add_keyword_trigger(target_id, message.text)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Ще тригер", callback_data=f"trigger_keyword:{target_id}")],
        [InlineKeyboardButton(text="◀️ До тригерів", callback_data=f"monitor_target_triggers:{target_id}")]
    ])
    
    await message.answer(
        f"✅ <b>Тригер додано!</b>\n\n"
        f"<b>Ключове слово:</b> {message.text}",
        reply_markup=kb,
        parse_mode="HTML"
    )
