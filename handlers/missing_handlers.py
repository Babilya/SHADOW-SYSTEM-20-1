from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
missing_router = Router()

class KeyStates(StatesGroup):
    waiting_key = State()

@missing_router.callback_query(F.data == "enter_key")
async def enter_key(query: CallbackQuery, state: FSMContext):
    await state.set_state(KeyStates.waiting_key)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="back_to_menu")]
    ])
    await query.message.edit_text(
        "🔑 <b>ВВЕДЕННЯ КЛЮЧА</b>\n\n"
        "Введіть ваш ліцензійний ключ у форматі:\n"
        "<code>SHADOW-XXXX-XXXX</code>",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.message(KeyStates.waiting_key)
async def process_key(message: Message, state: FSMContext):
    key = message.text.strip().upper()
    if key.startswith("SHADOW-") and len(key) == 16:
        await message.answer("✅ Ключ активовано! Ласкаво просимо.")
    else:
        await message.answer("❌ Невірний формат ключа. Спробуйте ще раз.")
    await state.clear()

@missing_router.callback_query(F.data == "balance_view")
async def balance_view(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="payments_menu")]
    ])
    await query.message.edit_text(
        "💵 <b>ВАШ БАЛАНС</b>\n\n"
        "💰 Баланс: <b>0 ₴</b>\n"
        "🔒 Заморожено: 0 ₴\n"
        "📊 Всього поповнено: 0 ₴",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data == "admin_analytics")
async def admin_analytics(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 Графіки", callback_data="analytics_charts")],
        [InlineKeyboardButton(text="📊 Звіти", callback_data="analytics_reports")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    await query.message.edit_text(
        "📊 <b>АНАЛІТИКА</b>\n\n"
        "├ Користувачів сьогодні: 45\n"
        "├ Активних кампаній: 12\n"
        "├ Повідомлень надіслано: 5,234\n"
        "└ Конверсія: 12.5%",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data == "admin_applications")
async def admin_applications(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Нові", callback_data="apps_new")],
        [InlineKeyboardButton(text="✅ Підтверджені", callback_data="apps_confirmed")],
        [InlineKeyboardButton(text="❌ Відхилені", callback_data="apps_rejected")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    await query.message.edit_text(
        "📝 <b>ЗАЯВКИ</b>\n\n"
        "├ Нових: 3\n"
        "├ Підтверджених: 45\n"
        "└ Відхилених: 8",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data == "admin_bots")
async def admin_bots(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Активні", callback_data="bots_active")],
        [InlineKeyboardButton(text="🔴 Помилки", callback_data="bots_error")],
        [InlineKeyboardButton(text="➕ Додати", callback_data="add_bots")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    await query.message.edit_text(
        "🤖 <b>БОТИ</b>\n\n"
        "├ Всього: 150\n"
        "├ Активних: 142\n"
        "├ З помилками: 8\n"
        "└ Warming: 23",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data == "admin_campaigns")
async def admin_campaigns(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Активні", callback_data="campaigns_active")],
        [InlineKeyboardButton(text="⏸ Пауза", callback_data="campaigns_paused")],
        [InlineKeyboardButton(text="✅ Завершені", callback_data="campaigns_completed")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    await query.message.edit_text(
        "📧 <b>КАМПАНІЇ</b>\n\n"
        "├ Активних: 5\n"
        "├ На паузі: 2\n"
        "├ Завершених: 34\n"
        "└ Чернеток: 3",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data == "admin_keys")
async def admin_keys(query: CallbackQuery):
    from core.encryption import encryption_manager
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Згенерувати ключ", callback_data="gen_new_key")],
        [InlineKeyboardButton(text="📋 Список ключів", callback_data="keys_list")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    await query.message.edit_text(
        "🔑 <b>КЛЮЧІ ДОСТУПУ</b>\n\n"
        "├ Активних: 45\n"
        "├ Використано: 123\n"
        "└ Заблоковано: 5",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data == "gen_new_key")
async def gen_new_key(query: CallbackQuery):
    from core.encryption import encryption_manager
    
    new_key = encryption_manager.generate_secure_key("SHADOW")
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Ще один", callback_data="gen_new_key")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_keys")]
    ])
    await query.message.edit_text(
        f"🔑 <b>НОВИЙ КЛЮЧ ЗГЕНЕРОВАНО</b>\n\n"
        f"<code>{new_key}</code>\n\n"
        f"Скопіюйте та надішліть користувачу.",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data == "admin_security")
async def admin_security(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚫 Заблокувати", callback_data="sec_ban")],
        [InlineKeyboardButton(text="📋 Логи", callback_data="security_logs")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    await query.message.edit_text(
        "🛡️ <b>БЕЗПЕКА</b>\n\n"
        "├ Заблокованих: 8\n"
        "├ Підозрілих: 3\n"
        "└ Інцидентів: 0",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data == "admin_settings")
async def admin_settings(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ CMS", callback_data="config_menu")],
        [InlineKeyboardButton(text="🔔 Сповіщення", callback_data="settings_notifications")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    await query.message.edit_text(
        "⚙️ <b>НАЛАШТУВАННЯ</b>\n\n"
        "Виберіть розділ:",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data.in_(["dur_2", "dur_14", "dur_30"]))
async def duration_select(query: CallbackQuery, state: FSMContext):
    duration_map = {"dur_2": 2, "dur_14": 14, "dur_30": 30}
    days = duration_map.get(query.data, 14)
    
    await state.update_data(duration=days)
    await query.message.edit_text(
        f"✅ Обрано термін: {days} днів\n\n"
        "Тепер введіть ваше ім'я:"
    )
    await query.answer()

@missing_router.callback_query(F.data.in_(["buy_standard", "buy_premium", "buy_elite"]))
async def buy_tier(query: CallbackQuery):
    tier_info = {
        "buy_standard": ("СТАНДАРТ", "12,500 ₴"),
        "buy_premium": ("ПРЕМІУМ", "62,500 ₴"),
        "buy_elite": ("VIP ELITE", "100,000 ₴")
    }
    
    tier_name, price = tier_info.get(query.data, ("N/A", "N/A"))
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатити", callback_data="pay_card")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="subscription_main")]
    ])
    
    await query.message.edit_text(
        f"🛒 <b>КУПІВЛЯ {tier_name}</b>\n\n"
        f"💰 Ціна: {price}/місяць\n\n"
        f"Оберіть спосіб оплати:",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data == "card_payment")
async def card_payment_handler(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Надіслати скріншот", callback_data="send_screenshot")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="payments_menu")]
    ])
    await query.message.edit_text(
        "💳 <b>ОПЛАТА КАРТКОЮ</b>\n\n"
        "<b>Реквізити:</b>\n"
        "Картка: <code>4441 1144 5555 7777</code>\n\n"
        "Після оплати надішліть скріншот квитанції.",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data == "create_invoice")
async def create_invoice(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="payments_menu")]
    ])
    await query.message.edit_text(
        "📄 <b>РАХУНОК СТВОРЕНО</b>\n\n"
        "Номер: INV-2025-001\n"
        "Сума: 12,500 ₴\n"
        "Дійсний: 48 годин",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data.in_(["export_csv", "export_excel", "export_json", "export_pdf"]))
async def export_data(query: CallbackQuery):
    format_name = query.data.replace("export_", "").upper()
    await query.answer(f"📥 Експорт у {format_name} розпочато...")
    await query.message.edit_text(
        f"📥 <b>ЕКСПОРТ ДАНИХ</b>\n\n"
        f"Формат: {format_name}\n"
        f"Статус: ⏳ Підготовка файлу...\n\n"
        f"<i>Файл буде надіслано протягом хвилини.</i>",
        parse_mode="HTML"
    )

@missing_router.callback_query(F.data.in_(["gen_friendly", "gen_informative", "gen_professional"]))
async def generate_text_style(query: CallbackQuery):
    styles = {
        "gen_friendly": "Дружній",
        "gen_informative": "Інформативний", 
        "gen_professional": "Професійний"
    }
    style = styles.get(query.data, "Стандартний")
    
    await query.message.edit_text(
        f"✅ Стиль <b>{style}</b> обрано.\n\n"
        f"Генерую текст...",
        parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data.in_(["alerts_critical", "alerts_financial", "alerts_operational"]))
async def view_alerts(query: CallbackQuery):
    alert_type = query.data.replace("alerts_", "")
    icons = {"critical": "🚨", "financial": "💰", "operational": "⚙️"}
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_alerts")]
    ])
    
    await query.message.edit_text(
        f"{icons.get(alert_type, '📋')} <b>СПОВІЩЕННЯ: {alert_type.upper()}</b>\n\n"
        f"Немає нових сповіщень.",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data == "alerts_read_all")
async def read_all_alerts(query: CallbackQuery):
    await query.answer("✅ Всі сповіщення прочитано")

@missing_router.callback_query(F.data.in_(["broadcast_all", "broadcast_premium"]))
async def broadcast_type(query: CallbackQuery, state: FSMContext):
    audience = "всіх" if query.data == "broadcast_all" else "преміум"
    await state.update_data(broadcast_audience=audience)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_menu")]
    ])
    
    await query.message.edit_text(
        f"📢 <b>РОЗСИЛКА ДЛЯ {audience.upper()}</b>\n\n"
        f"Напишіть текст повідомлення:",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data == "audit_critical")
async def audit_critical(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_audit")]
    ])
    await query.message.edit_text(
        "🚨 <b>КРИТИЧНІ ПОДІЇ</b>\n\n"
        "Немає критичних подій за останні 24 години.",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data == "audit_report")
async def audit_report(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Завантажити", callback_data="export_pdf")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_audit")]
    ])
    await query.message.edit_text(
        "📊 <b>ЗВІТ АУДИТУ</b>\n\n"
        "Період: останні 7 днів\n"
        "Подій: 1,234\n"
        "Критичних: 0\n"
        "Попереджень: 12",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data == "copy_text")
async def copy_text(query: CallbackQuery):
    await query.answer("📋 Текст скопійовано!")

@missing_router.callback_query(F.data.startswith("cfg_btn_"))
async def cfg_btn_role(query: CallbackQuery):
    role = query.data.replace("cfg_btn_", "")
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="cfg_buttons")]
    ])
    
    await query.message.edit_text(
        f"🔘 <b>КНОПКИ ДЛЯ {role.upper()}</b>\n\n"
        f"Тут будуть налаштування кнопок.",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data == "cfg_export")
async def cfg_export(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Експорт", callback_data="do_export_config")],
        [InlineKeyboardButton(text="📤 Імпорт", callback_data="do_import_config")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="config_menu")]
    ])
    await query.message.edit_text(
        "💾 <b>ЕКСПОРТ/ІМПОРТ</b>\n\n"
        "Збереження та відновлення конфігурації.",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data == "cfg_visibility")
async def cfg_visibility(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="config_menu")]
    ])
    await query.message.edit_text(
        "👁 <b>ВИДИМІСТЬ РОЛЕЙ</b>\n\n"
        "Налаштування видимості елементів для різних ролей.",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data.startswith("edit_text_welcome_"))
async def edit_welcome_text(query: CallbackQuery, state: FSMContext):
    role = query.data.replace("edit_text_welcome_", "")
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="cfg_texts")]
    ])
    
    await query.message.edit_text(
        f"📝 <b>РЕДАГУВАННЯ ПРИВІТАННЯ {role.upper()}</b>\n\n"
        f"Введіть новий текст привітання:",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data == "admin_tickets_all")
async def admin_tickets_all(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_tickets_menu")]
    ])
    await query.message.edit_text(
        "📋 <b>ВСІ ТІКЕТИ</b>\n\nНемає тікетів.",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data == "admin_tickets_closed")
async def admin_tickets_closed(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_tickets_menu")]
    ])
    await query.message.edit_text(
        "✅ <b>ЗАКРИТІ ТІКЕТИ</b>\n\nНемає закритих тікетів.",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data == "confirmed_payments")
async def confirmed_payments(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_payments_menu")]
    ])
    await query.message.edit_text(
        "✅ <b>ПІДТВЕРДЖЕНІ ПЛАТЕЖІ</b>\n\nНемає підтверджених платежів.",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data == "rejected_payments")
async def rejected_payments(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_payments_menu")]
    ])
    await query.message.edit_text(
        "❌ <b>ВІДХИЛЕНІ ПЛАТЕЖІ</b>\n\nНемає відхилених платежів.",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data == "keys_list")
async def keys_list(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_keys")]
    ])
    await query.message.edit_text(
        "📋 <b>СПИСОК КЛЮЧІВ</b>\n\n"
        "1. SHADOW-A1B2-C3D4 | ✅ Активний\n"
        "2. SHADOW-E5F6-G7H8 | ⏳ Очікує\n"
        "3. SHADOW-I9J0-K1L2 | 🔴 Заблоковано",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data == "admin_change_role")
async def admin_change_role(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_users")]
    ])
    await query.message.edit_text(
        "🔄 <b>ЗМІНА РОЛІ</b>\n\n"
        "Введіть User ID користувача:",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@missing_router.callback_query(F.data == "admin_confirm")
async def admin_confirm(query: CallbackQuery):
    await query.answer("✅ Підтверджено!")

@missing_router.callback_query(F.data == "admin_cancel")
async def admin_cancel(query: CallbackQuery):
    await query.answer("❌ Скасовано!")
    await query.message.edit_text("❌ Операцію скасовано")

@missing_router.callback_query(F.data.in_(["analytics_charts", "analytics_reports"]))
async def analytics_sub(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="admin_analytics")]])
    await query.message.edit_text("📊 <b>Дані завантажуються...</b>", reply_markup=kb, parse_mode="HTML")
    await query.answer()

@missing_router.callback_query(F.data.in_(["apps_new", "apps_confirmed", "apps_rejected"]))
async def apps_filter(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="admin_applications")]])
    await query.message.edit_text("📋 <b>Заявки за фільтром</b>\n\nНемає даних.", reply_markup=kb, parse_mode="HTML")
    await query.answer()

@missing_router.callback_query(F.data.in_(["campaigns_active", "campaigns_paused", "campaigns_completed"]))
async def campaigns_filter(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="admin_campaigns")]])
    await query.message.edit_text("📧 <b>Кампанії</b>\n\nНемає даних.", reply_markup=kb, parse_mode="HTML")
    await query.answer()

@missing_router.callback_query(F.data.in_(["do_export_config", "do_import_config"]))
async def config_ops(query: CallbackQuery):
    action = "Експорт" if "export" in query.data else "Імпорт"
    await query.answer(f"⏳ {action}...")

@missing_router.callback_query(F.data.in_(["geo_kyiv", "geo_kharkiv", "geo_odesa", "geo_moscow"]))
async def geo_select(query: CallbackQuery):
    city = query.data.replace("geo_", "").capitalize()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="geo_scan")]])
    await query.message.edit_text(f"📍 <b>Скан: {city}</b>\n\nАналіз регіону...", reply_markup=kb, parse_mode="HTML")
    await query.answer()

@missing_router.callback_query(F.data.in_(["help_analytics", "help_botnet", "help_osint", "help_payments", "help_settings", "help_subscriptions", "help_team"]))
async def help_section(query: CallbackQuery):
    section = query.data.replace("help_", "").upper()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="help_main")]])
    await query.message.edit_text(f"❓ <b>Допомога: {section}</b>\n\nДокументація скоро буде.", reply_markup=kb, parse_mode="HTML")
    await query.answer()

@missing_router.callback_query(F.data.in_(["interval_fast", "interval_normal", "interval_slow", "interval_safe"]))
async def interval_select(query: CallbackQuery, state: FSMContext):
    intervals = {"fast": (1, 3), "normal": (3, 10), "slow": (10, 30), "safe": (30, 60)}
    name = query.data.replace("interval_", "")
    min_i, max_i = intervals.get(name, (5, 15))
    await state.update_data(interval_min=min_i, interval_max=max_i)
    await query.answer(f"✅ Інтервал {name}: {min_i}-{max_i}с")

@missing_router.callback_query(F.data.in_(["lang_uk", "lang_en"]))
async def lang_select(query: CallbackQuery):
    lang = "Українська" if "uk" in query.data else "English"
    await query.answer(f"✅ Мова: {lang}")

@missing_router.callback_query(F.data == "liqpay_payment")
async def liqpay_payment(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="payments_menu")]])
    await query.message.edit_text("💳 <b>LIQPAY</b>\n\nЦей метод тимчасово недоступний.", reply_markup=kb, parse_mode="HTML")
    await query.answer()

@missing_router.callback_query(F.data == "mailing_settings")
async def mailing_settings(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="mailing_menu")]])
    await query.message.edit_text("⚙️ <b>НАЛАШТУВАННЯ РОЗСИЛОК</b>", reply_markup=kb, parse_mode="HTML")
    await query.answer()

@missing_router.callback_query(F.data.in_(["monitor_chats", "monitor_start", "monitor_stop"]))
async def monitor_ops(query: CallbackQuery):
    action = query.data.replace("monitor_", "")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="monitor_menu")]])
    await query.message.edit_text(f"🔍 <b>Моніторинг: {action}</b>", reply_markup=kb, parse_mode="HTML")
    await query.answer()

@missing_router.callback_query(F.data == "payments_history")
async def payments_history(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="payments_menu")]])
    await query.message.edit_text("📋 <b>ІСТОРІЯ ПЛАТЕЖІВ</b>\n\nНемає платежів.", reply_markup=kb, parse_mode="HTML")
    await query.answer()

@missing_router.callback_query(F.data == "refund_request")
async def refund_request(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="payments_menu")]])
    await query.message.edit_text("💸 <b>ПОВЕРНЕННЯ КОШТІВ</b>\n\nЗверніться в підтримку.", reply_markup=kb, parse_mode="HTML")
    await query.answer()

@missing_router.callback_query(F.data.in_(["confirm_payment", "reject_payment"]))
async def payment_decision(query: CallbackQuery):
    action = "підтверджено" if "confirm" in query.data else "відхилено"
    await query.answer(f"✅ Платіж {action}!")

@missing_router.callback_query(F.data == "renew_premium")
async def renew_premium(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="subscription_main")]])
    await query.message.edit_text("🔄 <b>ОНОВЛЕННЯ ПІДПИСКИ</b>", reply_markup=kb, parse_mode="HTML")
    await query.answer()

@missing_router.callback_query(F.data == "restart_bot")
async def restart_bot(query: CallbackQuery):
    await query.answer("🔄 Перезапуск бота...")

@missing_router.callback_query(F.data == "security_logs")
async def security_logs(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="admin_security")]])
    await query.message.edit_text("📋 <b>ЛОГИ БЕЗПЕКИ</b>\n\nОстанні події...", reply_markup=kb, parse_mode="HTML")
    await query.answer()

@missing_router.callback_query(F.data == "send_emergency")
async def send_emergency(query: CallbackQuery):
    await query.answer("🚨 Екстрене сповіщення надіслано!")

@missing_router.callback_query(F.data == "settings_notifications")
async def settings_notifications(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="admin_settings")]])
    await query.message.edit_text("🔔 <b>СПОВІЩЕННЯ</b>", reply_markup=kb, parse_mode="HTML")
    await query.answer()

@missing_router.callback_query(F.data.in_(["stars_100", "stars_250", "stars_1250", "stars_payment"]))
async def stars_ops(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="payments_menu")]])
    await query.message.edit_text("⭐ <b>TELEGRAM STARS</b>", reply_markup=kb, parse_mode="HTML")
    await query.answer()

@missing_router.callback_query(F.data == "stats_detailed")
async def stats_detailed(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="admin_stats")]])
    await query.message.edit_text("📊 <b>ДЕТАЛЬНА СТАТИСТИКА</b>", reply_markup=kb, parse_mode="HTML")
    await query.answer()

@missing_router.callback_query(F.data == "submit_application")
async def submit_application(query: CallbackQuery):
    await query.answer("✅ Заявку надіслано!")

@missing_router.callback_query(F.data == "support")
async def support(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]])
    await query.message.edit_text("💬 <b>ПІДТРИМКА</b>\n\nНапишіть /support для створення тікету.", reply_markup=kb, parse_mode="HTML")
    await query.answer()

@missing_router.callback_query(F.data.in_(["system_clear_cache", "system_restart"]))
async def system_ops(query: CallbackQuery):
    action = "Кеш очищено" if "cache" in query.data else "Перезапуск..."
    await query.answer(f"⚙️ {action}")

@missing_router.callback_query(F.data.in_(["target_all", "target_filter", "target_list"]))
async def target_select(query: CallbackQuery, state: FSMContext):
    target = query.data.replace("target_", "")
    await state.update_data(audience_type=target)
    await query.answer(f"✅ Аудиторія: {target}")

@missing_router.callback_query(F.data.in_(["tariff_baseus", "tariff_standard"]))
async def tariff_select(query: CallbackQuery):
    tariff = "БАЗОВИЙ" if "baseus" in query.data else "СТАНДАРТ"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="subscription_main")]])
    await query.message.edit_text(f"📦 <b>ТАРИФ {tariff}</b>", reply_markup=kb, parse_mode="HTML")
    await query.answer()

@missing_router.callback_query(F.data.in_(["text_ab", "text_detail_1", "text_detail_2", "text_detail_3", "text_edit", "text_resend", "text_segmentation", "text_stats", "text_time"]))
async def text_ops(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="my_texts")]])
    await query.message.edit_text("📝 <b>ОПЕРАЦІЯ З ТЕКСТОМ</b>", reply_markup=kb, parse_mode="HTML")
    await query.answer()

@missing_router.callback_query(F.data == "user_menu")
async def user_menu(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]])
    await query.message.edit_text("👤 <b>МЕНЮ КОРИСТУВАЧА</b>", reply_markup=kb, parse_mode="HTML")
    await query.answer()

@missing_router.callback_query(F.data.in_(["users_admins", "users_leaders", "users_managers"]))
async def users_filter(query: CallbackQuery):
    role = query.data.replace("users_", "").upper()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="admin_users")]])
    await query.message.edit_text(f"👥 <b>{role}</b>\n\nСписок користувачів...", reply_markup=kb, parse_mode="HTML")
    await query.answer()

@missing_router.callback_query(F.data == "view_tariffs")
async def view_tariffs(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 БАЗОВИЙ", callback_data="tariff_baseus")],
        [InlineKeyboardButton(text="⭐ СТАНДАРТ", callback_data="tariff_standard")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])
    await query.message.edit_text("💰 <b>ТАРИФИ</b>\n\n📦 БАЗОВИЙ - 4,200 ₴\n⭐ СТАНДАРТ - 12,500 ₴\n💎 ПРЕМІУМ - 62,500 ₴", reply_markup=kb, parse_mode="HTML")
    await query.answer()

@missing_router.callback_query(F.data == "input_name")
async def input_name(query: CallbackQuery):
    await query.message.edit_text("📝 Введіть ваше ім'я:")
    await query.answer()

@missing_router.callback_query(F.data == "gen_urgent")
async def gen_urgent(query: CallbackQuery):
    await query.message.edit_text("⚡ Стиль <b>Терміновий</b> обрано.\n\nГенерую текст...", parse_mode="HTML")
    await query.answer()

@missing_router.callback_query(F.data == "cfg_btn_add")
async def cfg_btn_add(query: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="cfg_buttons")]])
    await query.message.edit_text("➕ <b>ДОДАТИ КНОПКУ</b>\n\nВведіть назву кнопки:", reply_markup=kb, parse_mode="HTML")
    await query.answer()
