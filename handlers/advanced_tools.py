"""
Advanced Tools Handler - Обробники розширених інструментів
AI аналіз, спам-аналізатор, каскадні кампанії, профілювання
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from core.ai_pattern_detection import ai_pattern_detector
from core.spam_analyzer import spam_analyzer
from core.drip_campaign import drip_campaign_manager
from core.behavior_profiler import behavior_profiler
from core.keyword_analyzer import keyword_analyzer
from core.enhanced_reports import enhanced_report_generator
from keyboards.advanced_kb import (
    get_ai_analysis_menu, get_spam_analyzer_menu, get_drip_campaign_menu,
    get_behavior_menu, get_keyword_menu, get_reports_menu, get_advanced_tools_menu
)

logger = logging.getLogger(__name__)

advanced_tools_router = Router()


class AdvancedToolsStates(StatesGroup):
    waiting_ai_text = State()
    waiting_spam_text = State()
    waiting_drip_name = State()
    waiting_drip_steps = State()
    waiting_behavior_user = State()
    waiting_keyword_text = State()


@advanced_tools_router.callback_query(F.data == "advanced_tools")
async def show_advanced_tools(callback: CallbackQuery):
    """Показ меню розширених інструментів"""
    await callback.message.edit_text(
        "<b>🛠 РОЗШИРЕНІ ІНСТРУМЕНТИ</b>\n"
        "═══════════════════════\n\n"
        "Оберіть інструмент для роботи:",
        reply_markup=get_advanced_tools_menu()
    )


@advanced_tools_router.callback_query(F.data == "tools_ai")
async def show_ai_menu(callback: CallbackQuery):
    """Меню AI аналізу"""
    await callback.message.edit_text(
        "<b>🤖 AI АНАЛІЗ ЗАГРОЗ</b>\n"
        "═══════════════════════\n\n"
        "Розумний аналіз тексту з використанням AI:\n"
        "├ Виявлення прихованих координат\n"
        "├ Детекція загроз та ключових слів\n"
        "├ Пошук телефонів та криптоадрес\n"
        "└ Повний AI-аналіз з GPT\n\n"
        "Оберіть тип аналізу:",
        reply_markup=get_ai_analysis_menu()
    )


@advanced_tools_router.callback_query(F.data == "ai_analyze_text")
@advanced_tools_router.callback_query(F.data == "ai_full_analysis")
async def request_ai_text(callback: CallbackQuery, state: FSMContext):
    """Запит тексту для AI аналізу"""
    await state.set_state(AdvancedToolsStates.waiting_ai_text)
    await state.update_data(full_analysis=callback.data == "ai_full_analysis")
    
    await callback.message.edit_text(
        "<b>📝 AI АНАЛІЗ</b>\n"
        "═══════════════════════\n\n"
        "Надішліть текст для аналізу.\n\n"
        "Система виявить:\n"
        "├ Приховані координати\n"
        "├ Загрози та ключові слова\n"
        "├ Телефонні номери\n"
        "├ Криптовалютні адреси\n"
        "└ Закодовані дані"
    )


@advanced_tools_router.message(AdvancedToolsStates.waiting_ai_text)
async def process_ai_analysis(message: Message, state: FSMContext):
    """Обробка AI аналізу"""
    data = await state.get_data()
    text = message.text
    
    await message.answer("⏳ Аналізую текст...")
    
    try:
        if data.get('full_analysis'):
            result = await ai_pattern_detector.analyze_with_ai(text)
        else:
            result = ai_pattern_detector.detect_all_patterns(text)
        
        report = ai_pattern_detector.generate_threat_report(result)
        await message.answer(report, reply_markup=get_ai_analysis_menu())
        
    except Exception as e:
        logger.error(f"AI analysis error: {e}")
        await message.answer(
            f"❌ Помилка аналізу: {e}",
            reply_markup=get_ai_analysis_menu()
        )
    
    await state.clear()


@advanced_tools_router.callback_query(F.data == "tools_spam")
async def show_spam_menu(callback: CallbackQuery):
    """Меню спам-аналізатора"""
    await callback.message.edit_text(
        "<b>📊 АНАЛІЗАТОР СПАМУ</b>\n"
        "═══════════════════════\n\n"
        "Перевірка тексту перед розсилкою:\n"
        "├ Аналіз на спам-маркери\n"
        "├ Перевірка читабельності\n"
        "├ Рекомендації покращення\n"
        "└ Оцінка ризику блокування\n\n"
        "Оберіть дію:",
        reply_markup=get_spam_analyzer_menu()
    )


@advanced_tools_router.callback_query(F.data == "spam_check_text")
async def request_spam_text(callback: CallbackQuery, state: FSMContext):
    """Запит тексту для перевірки спаму"""
    await state.set_state(AdvancedToolsStates.waiting_spam_text)
    
    await callback.message.edit_text(
        "<b>📝 ПЕРЕВІРКА СПАМУ</b>\n"
        "═══════════════════════\n\n"
        "Надішліть текст повідомлення для перевірки.\n\n"
        "Буде проаналізовано:\n"
        "├ Великі літери\n"
        "├ Кількість посилань\n"
        "├ Спам-слова\n"
        "├ Емодзі та спецсимволи\n"
        "└ Загальний рейтинг"
    )


@advanced_tools_router.message(AdvancedToolsStates.waiting_spam_text)
async def process_spam_check(message: Message, state: FSMContext):
    """Обробка перевірки спаму"""
    result = spam_analyzer.calculate_spam_score(message.text)
    report = spam_analyzer.format_analysis_report(result)
    
    await message.answer(report, reply_markup=get_spam_analyzer_menu())
    await state.clear()


@advanced_tools_router.callback_query(F.data == "tools_drip")
async def show_drip_menu(callback: CallbackQuery):
    """Меню каскадних кампаній"""
    await callback.message.edit_text(
        "<b>📧 КАСКАДНІ КАМПАНІЇ</b>\n"
        "═══════════════════════\n\n"
        "Автоматичні послідовні розсилки:\n"
        "├ Крок за кроком за розкладом\n"
        "├ Тригери на дії користувача\n"
        "├ Умовні переходи\n"
        "└ Аналітика конверсій\n\n"
        "Оберіть дію:",
        reply_markup=get_drip_campaign_menu()
    )


@advanced_tools_router.callback_query(F.data == "drip_stats")
async def show_drip_stats(callback: CallbackQuery):
    """Статистика каскадних кампаній"""
    campaigns = drip_campaign_manager.campaigns
    
    if not campaigns:
        await callback.message.edit_text(
            "<b>📊 СТАТИСТИКА</b>\n"
            "═══════════════════════\n\n"
            "Немає активних кампаній.\n"
            "Створіть першу каскадну кампанію!",
            reply_markup=get_drip_campaign_menu()
        )
        return
    
    text = "<b>📊 СТАТИСТИКА КАМПАНІЙ</b>\n═══════════════════════\n\n"
    
    for campaign_id in list(campaigns.keys())[:5]:
        stats = drip_campaign_manager.get_campaign_stats(campaign_id)
        text += f"<b>{campaign_id}</b>\n"
        text += f"├ Користувачів: {stats['total_users']}\n"
        text += f"├ Завершили: {stats['completed']}\n"
        text += f"└ Відповідей: {stats['total_responses']}\n\n"
    
    await callback.message.edit_text(text, reply_markup=get_drip_campaign_menu())


@advanced_tools_router.callback_query(F.data == "tools_behavior")
async def show_behavior_menu(callback: CallbackQuery):
    """Меню Dynamic Biometrics та профілювання"""
    text = """<b>🧬 DYNAMIC BIOMETRICS</b>
<i>Управління "життям" ботів та профілювання</i>

───────────────

<b>📊 СТАТУС МОДУЛЯ:</b>
├ 🔋 Активність: <code>ON</code>
├ 🧬 Алгоритм: <code>Adaptive Life v2.1</code>
└ 🛡️ Рівень маскування: <code>High</code>

<b>💡 ФУНКЦІЇ:</b>
├ Автопідписка на тематичні канали
├ Імітація читання постів
├ Репости у "Збережене"
└ Аналіз поведінкових патернів

───────────────
<i>Бот виглядає як реальна людина з історією</i>"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_behavior_menu(),
        parse_mode="HTML"
    )


@advanced_tools_router.callback_query(F.data == "behavior_analyze_user")
async def request_behavior_user(callback: CallbackQuery, state: FSMContext):
    """Запит ID користувача для профілювання"""
    await state.set_state(AdvancedToolsStates.waiting_behavior_user)
    
    await callback.message.edit_text(
        "<b>👤 АНАЛІЗ КОРИСТУВАЧА</b>\n"
        "═══════════════════════\n\n"
        "Надішліть ID користувача для аналізу.\n\n"
        "Буде проаналізовано:\n"
        "├ Патерни активності\n"
        "├ Типовий час онлайн\n"
        "├ Поведінкові аномалії\n"
        "└ Прогноз найкращого часу контакту"
    )


@advanced_tools_router.message(AdvancedToolsStates.waiting_behavior_user)
async def process_behavior_analysis(message: Message, state: FSMContext):
    """Обробка аналізу поведінки"""
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer(
            "❌ Невірний формат. Введіть числовий ID користувача.",
            reply_markup=get_behavior_menu()
        )
        await state.clear()
        return
    
    profile = behavior_profiler.analyze_user_profile(user_id)
    report = behavior_profiler.format_profile_report(profile)
    
    await message.answer(report, reply_markup=get_behavior_menu())
    await state.clear()


@advanced_tools_router.callback_query(F.data == "tools_keywords")
async def show_keywords_menu(callback: CallbackQuery):
    """Меню аналізу ключових слів"""
    await callback.message.edit_text(
        "<b>🔑 АНАЛІЗ КЛЮЧОВИХ СЛІВ</b>\n"
        "═══════════════════════\n\n"
        "Глибокий аналіз тексту:\n"
        "├ Частотний аналіз слів\n"
        "├ Сентимент (настрій)\n"
        "├ Виявлення трендів\n"
        "├ Оцінка читабельності\n"
        "└ Визначення мови\n\n"
        "Оберіть дію:",
        reply_markup=get_keyword_menu()
    )


@advanced_tools_router.callback_query(F.data == "keywords_analyze_text")
async def request_keyword_text(callback: CallbackQuery, state: FSMContext):
    """Запит тексту для аналізу ключових слів"""
    await state.set_state(AdvancedToolsStates.waiting_keyword_text)
    
    await callback.message.edit_text(
        "<b>📝 АНАЛІЗ КЛЮЧОВИХ СЛІВ</b>\n"
        "═══════════════════════\n\n"
        "Надішліть текст для аналізу.\n\n"
        "Можете надіслати:\n"
        "├ Одне повідомлення\n"
        "├ Кілька абзаців\n"
        "└ Великий текст (до 10000 символів)"
    )


@advanced_tools_router.message(AdvancedToolsStates.waiting_keyword_text)
async def process_keyword_analysis(message: Message, state: FSMContext):
    """Обробка аналізу ключових слів"""
    analysis = keyword_analyzer.analyze_text(message.text)
    report = keyword_analyzer.format_analysis_report(analysis)
    
    await message.answer(report, reply_markup=get_keyword_menu())
    await state.clear()


@advanced_tools_router.callback_query(F.data == "tools_reports")
async def show_reports_menu(callback: CallbackQuery):
    """Меню генерації звітів"""
    await callback.message.edit_text(
        "<b>📄 ГЕНЕРАТОР ЗВІТІВ</b>\n"
        "═══════════════════════\n\n"
        "Професійні PDF звіти:\n"
        "├ OSINT звіт з графіками\n"
        "├ Звіт по кампанії\n"
        "├ Профіль користувача\n"
        "└ Аналітичний звіт\n\n"
        "Оберіть тип звіту:",
        reply_markup=get_reports_menu()
    )


@advanced_tools_router.callback_query(F.data == "ai_find_coords")
async def find_coordinates(callback: CallbackQuery, state: FSMContext):
    """Пошук координат"""
    await state.set_state(AdvancedToolsStates.waiting_ai_text)
    await state.update_data(mode="coords")
    
    await callback.message.edit_text(
        "<b>📍 ПОШУК КООРДИНАТ</b>\n"
        "═══════════════════════\n\n"
        "Надішліть текст для пошуку координат.\n\n"
        "Підтримуються формати:\n"
        "├ Десяткові (50.4501, 30.5234)\n"
        "├ DMS (50°27'00\"N 30°31'24\"E)\n"
        "├ MGRS (36U XC 12345 67890)\n"
        "├ Google Maps посилання\n"
        "└ Інші приховані формати"
    )


@advanced_tools_router.callback_query(F.data == "ai_detect_threats")
async def detect_threats(callback: CallbackQuery, state: FSMContext):
    """Детекція загроз"""
    await state.set_state(AdvancedToolsStates.waiting_ai_text)
    await state.update_data(mode="threats")
    
    await callback.message.edit_text(
        "<b>⚠️ ДЕТЕКЦІЯ ЗАГРОЗ</b>\n"
        "═══════════════════════\n\n"
        "Надішліть текст для аналізу загроз.\n\n"
        "Виявляються:\n"
        "├ 🔴 Критичні (вибухівка, координати)\n"
        "├ 🟠 Високі (зброя, боєприпаси)\n"
        "├ 🟡 Середні (техніка, бази)\n"
        "└ 🟢 Низькі (персонал)"
    )


@advanced_tools_router.callback_query(F.data == "ai_find_phones")
async def find_phones(callback: CallbackQuery, state: FSMContext):
    """Пошук телефонів"""
    await state.set_state(AdvancedToolsStates.waiting_ai_text)
    await state.update_data(mode="phones")
    await callback.message.edit_text(
        "<b>📱 ПОШУК ТЕЛЕФОНІВ</b>\n═══════════════════════\n\n"
        "Надішліть текст для пошуку телефонних номерів.\n\n"
        "Підтримуються формати:\n├ +380 (Україна)\n├ +7 (Росія)\n├ +375 (Білорусь)\n└ +48 (Польща)"
    )


@advanced_tools_router.callback_query(F.data == "ai_find_crypto")
async def find_crypto(callback: CallbackQuery, state: FSMContext):
    """Пошук криптовалют"""
    await state.set_state(AdvancedToolsStates.waiting_ai_text)
    await state.update_data(mode="crypto")
    await callback.message.edit_text(
        "<b>💰 ПОШУК КРИПТОВАЛЮТ</b>\n═══════════════════════\n\n"
        "Надішліть текст для пошуку криптоадрес.\n\n"
        "Підтримуються:\n├ BTC (Bitcoin)\n├ ETH (Ethereum)\n└ USDT (TRC-20)"
    )


@advanced_tools_router.callback_query(F.data == "behavior_patterns")
async def behavior_patterns_info(callback: CallbackQuery):
    """Інформація про патерни"""
    await callback.message.edit_text(
        "<b>📊 ПАТЕРНИ АКТИВНОСТІ</b>\n═══════════════════════\n\n"
        "Система аналізує:\n├ Добовий ритм (ранок/день/вечір/ніч)\n├ Пікові години активності\n"
        "├ Консистентність поведінки\n└ Використання платформ\n\n"
        "Для аналізу виберіть 'Аналіз користувача'.",
        reply_markup=get_behavior_menu()
    )


@advanced_tools_router.callback_query(F.data == "behavior_anomalies")
async def behavior_anomalies_info(callback: CallbackQuery):
    """Інформація про аномалії"""
    await callback.message.edit_text(
        "<b>⚠️ ВИЯВЛЕННЯ АНОМАЛІЙ</b>\n═══════════════════════\n\n"
        "Типи аномалій:\n├ Сплески активності (незвичайно висока)\n├ Тривала відсутність (>7 днів)\n"
        "├ Зміна патерну поведінки\n└ Нетипові години активності\n\n"
        "Для аналізу виберіть 'Аналіз користувача'.",
        reply_markup=get_behavior_menu()
    )


@advanced_tools_router.callback_query(F.data == "behavior_predict")
async def behavior_predict_info(callback: CallbackQuery):
    """Інформація про прогнози"""
    await callback.message.edit_text(
        "<b>🔮 ПРОГНОЗ АКТИВНОСТІ</b>\n═══════════════════════\n\n"
        "Система прогнозує:\n├ Найкращий час для контакту\n├ Ймовірні години онлайн\n"
        "├ Домінантний період дня\n└ Очікувана активність\n\n"
        "Для аналізу виберіть 'Аналіз користувача'.",
        reply_markup=get_behavior_menu()
    )


@advanced_tools_router.callback_query(F.data == "keywords_top")
async def keywords_top_info(callback: CallbackQuery, state: FSMContext):
    """ТОП слова"""
    await state.set_state(AdvancedToolsStates.waiting_keyword_text)
    await callback.message.edit_text(
        "<b>📊 ТОП КЛЮЧОВИХ СЛІВ</b>\n═══════════════════════\n\n"
        "Надішліть текст для аналізу найчастіших слів."
    )


@advanced_tools_router.callback_query(F.data == "keywords_sentiment")
async def keywords_sentiment_info(callback: CallbackQuery, state: FSMContext):
    """Сентимент"""
    await state.set_state(AdvancedToolsStates.waiting_keyword_text)
    await callback.message.edit_text(
        "<b>😊 АНАЛІЗ СЕНТИМЕНТУ</b>\n═══════════════════════\n\n"
        "Надішліть текст для визначення емоційного забарвлення."
    )


@advanced_tools_router.callback_query(F.data == "keywords_trends")
async def keywords_trends_info(callback: CallbackQuery):
    """Тренди"""
    await callback.message.edit_text(
        "<b>📈 АНАЛІЗ ТРЕНДІВ</b>\n═══════════════════════\n\n"
        "Для аналізу трендів потрібен набір повідомлень за різні періоди.\n"
        "Використовуйте функцію аналізу тексту з великим обсягом даних.",
        reply_markup=get_keyword_menu()
    )


@advanced_tools_router.callback_query(F.data == "spam_recommendations")
async def spam_recommendations_info(callback: CallbackQuery):
    """Рекомендації по спаму"""
    await callback.message.edit_text(
        "<b>📋 РЕКОМЕНДАЦІЇ</b>\n═══════════════════════\n\n"
        "Щоб уникнути спам-фільтрів:\n"
        "├ Уникайте ВЕЛИКИХ ЛІТЕР\n├ Мінімізуйте посилання\n├ Не використовуйте слова: безкоштовно, акція, знижка\n"
        "├ Обмежте емодзі до 2-3 на повідомлення\n├ Тримайте текст коротким (до 500 символів)\n"
        "└ Персоналізуйте повідомлення\n\nПеревірте текст через 'Перевірити текст'.",
        reply_markup=get_spam_analyzer_menu()
    )


@advanced_tools_router.callback_query(F.data == "spam_check_campaign")
async def spam_check_campaign(callback: CallbackQuery):
    """Перевірка кампанії"""
    await callback.message.edit_text(
        "<b>📊 АНАЛІЗ КАМПАНІЇ</b>\n═══════════════════════\n\n"
        "Для повного аналізу кампанії:\n1. Перейдіть у розділ Кампанії\n2. Виберіть кампанію\n"
        "3. Використовуйте 'Перевірити текст' для кожного повідомлення",
        reply_markup=get_spam_analyzer_menu()
    )


@advanced_tools_router.callback_query(F.data == "drip_create")
async def drip_create(callback: CallbackQuery):
    """Створення каскадної кампанії"""
    await callback.message.edit_text(
        "<b>➕ СТВОРЕННЯ КАМПАНІЇ</b>\n═══════════════════════\n\n"
        "Каскадна кампанія складається з кроків.\nКожен крок має:\n"
        "├ Текст повідомлення\n├ Затримку (години)\n├ Тригер переходу\n└ Умови\n\n"
        "⚠️ Функція в розробці.\nВикористовуйте воронки для послідовних розсилок.",
        reply_markup=get_drip_campaign_menu()
    )


@advanced_tools_router.callback_query(F.data == "drip_list")
async def drip_list(callback: CallbackQuery):
    """Список кампаній"""
    campaigns = drip_campaign_manager.campaigns
    if not campaigns:
        text = "<b>📋 МОЇ КАМПАНІЇ</b>\n═══════════════════════\n\nНемає активних каскадних кампаній."
    else:
        text = "<b>📋 МОЇ КАМПАНІЇ</b>\n═══════════════════════\n\n"
        for cid in list(campaigns.keys())[:10]:
            text += f"├ {cid}\n"
    await callback.message.edit_text(text, reply_markup=get_drip_campaign_menu())


@advanced_tools_router.callback_query(F.data == "drip_templates")
async def drip_templates(callback: CallbackQuery):
    """Шаблони каскадних кампаній"""
    await callback.message.edit_text(
        "<b>⚙️ ШАБЛОНИ КАМПАНІЙ</b>\n═══════════════════════\n\n"
        "Готові шаблони:\n├ 🎯 Welcome-серія (3 кроки)\n├ 📧 Реактивація (5 кроків)\n"
        "├ 🛒 Покинутий кошик (3 кроки)\n└ 📰 Новинна розсилка (7 кроків)\n\n"
        "⚠️ Функція в розробці.",
        reply_markup=get_drip_campaign_menu()
    )


@advanced_tools_router.callback_query(F.data == "report_osint")
async def report_osint(callback: CallbackQuery):
    """OSINT звіт"""
    await callback.message.edit_text(
        "<b>📄 OSINT ЗВІТ</b>\n═══════════════════════\n\n"
        "Для генерації PDF звіту:\n1. Проведіть OSINT аналіз\n2. Збережіть результати\n"
        "3. Згенеруйте звіт\n\n⚠️ PDF генерація потребує бібліотеку ReportLab.",
        reply_markup=get_reports_menu()
    )


@advanced_tools_router.callback_query(F.data == "report_campaign")
async def report_campaign(callback: CallbackQuery):
    """Звіт кампанії"""
    await callback.message.edit_text(
        "<b>📊 ЗВІТ КАМПАНІЇ</b>\n═══════════════════════\n\n"
        "Звіт включає:\n├ Загальна статистика\n├ Доставка та відкриття\n"
        "├ Відповіді та конверсії\n└ Графіки активності\n\n"
        "Виберіть кампанію в розділі Кампанії для генерації звіту.",
        reply_markup=get_reports_menu()
    )


@advanced_tools_router.callback_query(F.data == "report_user")
async def report_user(callback: CallbackQuery):
    """Звіт користувача"""
    await callback.message.edit_text(
        "<b>👤 ЗВІТ КОРИСТУВАЧА</b>\n═══════════════════════\n\n"
        "Профіль включає:\n├ Поведінкові патерни\n├ Історія активності\n"
        "├ Аналіз комунікації\n└ Прогноз поведінки\n\n"
        "Використовуйте Профілювання поведінки для аналізу.",
        reply_markup=get_reports_menu()
    )


@advanced_tools_router.callback_query(F.data == "report_analytics")
async def report_analytics(callback: CallbackQuery):
    """Аналітичний звіт"""
    await callback.message.edit_text(
        "<b>📈 АНАЛІТИЧНИЙ ЗВІТ</b>\n═══════════════════════\n\n"
        "Комплексний звіт:\n├ Загальна статистика проекту\n├ Ефективність кампаній\n"
        "├ Активність команди\n└ Тренди та прогнози\n\n"
        "Доступно для Лідерів та Адмінів.",
        reply_markup=get_reports_menu()
    )
