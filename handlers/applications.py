from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
from typing import Optional

from config import ADMIN_IDS
from core.audit_logger import audit_logger, ActionCategory
from core.alerts import alert_system, AlertType
from core.encryption import encryption_manager

applications_router = Router()

class ApplicationFSM(StatesGroup):
    duration = State()
    name = State()
    purpose = State()
    contact = State()
    confirm = State()

class AdminReplyFSM(StatesGroup):
    waiting_reply = State()
    waiting_requisites = State()
    waiting_key_type = State()

applications_storage = {}
messages_storage = {}

def duration_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="2 дні (тест)", callback_data="dur_2")],
        [InlineKeyboardButton(text="14 днів", callback_data="dur_14")],
        [InlineKeyboardButton(text="30 днів", callback_data="dur_30")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_app")]
    ])

def confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Підтвердити", callback_data="confirm_app")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_app")]
    ])

def admin_app_kb(app_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Відповісти", callback_data=f"admin_reply_{app_id}")],
        [InlineKeyboardButton(text="💳 Надіслати реквізити", callback_data=f"admin_requisites_{app_id}")],
        [InlineKeyboardButton(text="🔑 Згенерувати ключ", callback_data=f"admin_genkey_{app_id}")],
        [InlineKeyboardButton(text="❌ Відхилити", callback_data=f"admin_reject_{app_id}")]
    ])

@applications_router.callback_query(F.data.startswith("apply_"))
async def start_application(query: CallbackQuery, state: FSMContext):
    tariff = query.data.split("_")[1]
    await state.update_data(tariff=tariff, user_id=query.from_user.id, username=query.from_user.username)
    await state.set_state(ApplicationFSM.duration)
    
    await audit_logger.log(
        user_id=query.from_user.id,
        action="application_started",
        category=ActionCategory.AUTH,
        username=query.from_user.username,
        details={"tariff": tariff}
    )
    
    await query.message.edit_text(
        f"📝 <b>ЗАЯВКА НА ПІДКЛЮЧЕННЯ</b>\n\n"
        f"Тариф: <b>{tariff.upper()}</b>\n\n"
        f"Виберіть термін підписки:",
        reply_markup=duration_kb(),
        parse_mode="HTML"
    )
    await query.answer()

@applications_router.callback_query(F.data.startswith("dur_"), ApplicationFSM.duration)
async def process_duration(query: CallbackQuery, state: FSMContext):
    duration = int(query.data.split("_")[1])
    await state.update_data(duration=duration)
    await state.set_state(ApplicationFSM.name)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_app")]
    ])
    
    await query.message.edit_text(
        f"📝 <b>ЗАЯВКА</b>\n\n"
        f"Термін: <b>{duration} днів</b>\n\n"
        f"Введіть ваше ім'я або назву компанії:",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await query.answer()

@applications_router.message(ApplicationFSM.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(ApplicationFSM.purpose)
    await message.answer(
        "📝 Опишіть мету використання системи:\n\n"
        "<i>(Маркетинг, OSINT, управління командою тощо)</i>",
        parse_mode="HTML"
    )

@applications_router.message(ApplicationFSM.purpose)
async def process_purpose(message: Message, state: FSMContext):
    await state.update_data(purpose=message.text)
    await state.set_state(ApplicationFSM.contact)
    await message.answer(
        "📱 Вкажіть контактну інформацію:\n\n"
        "<i>(Telegram, Email або телефон для зв'язку)</i>",
        parse_mode="HTML"
    )

@applications_router.message(ApplicationFSM.contact)
async def process_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()
    
    tariff_prices = {
        "basic": 4200,
        "standard": 12500,
        "premium": 62500,
        "personal": 100000
    }
    
    price = tariff_prices.get(data['tariff'], 0)
    
    summary = f"""📋 <b>ПІДТВЕРДЖЕННЯ ЗАЯВКИ</b>

<b>Тариф:</b> {data['tariff'].upper()}
<b>Термін:</b> {data['duration']} днів
<b>Ім'я:</b> {data['name']}
<b>Мета:</b> {data['purpose']}
<b>Контакт:</b> {data['contact']}

<b>💰 Вартість:</b> {price:,} ₴

Підтвердіть заявку:"""
    
    await state.set_state(ApplicationFSM.confirm)
    await message.answer(summary, reply_markup=confirm_kb(), parse_mode="HTML")

@applications_router.callback_query(F.data == "confirm_app", ApplicationFSM.confirm)
async def confirm_application(query: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    
    app_id = len(applications_storage) + 1
    app_data = {
        "id": app_id,
        "user_id": query.from_user.id,
        "username": query.from_user.username,
        "tariff": data['tariff'],
        "duration": data['duration'],
        "name": data['name'],
        "purpose": data['purpose'],
        "contact": data['contact'],
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "messages": []
    }
    applications_storage[app_id] = app_data
    
    await audit_logger.log(
        user_id=query.from_user.id,
        action="application_submitted",
        category=ActionCategory.AUTH,
        username=query.from_user.username,
        details={"app_id": app_id, "tariff": data['tariff']}
    )
    
    await alert_system.send_alert(
        alert_type=AlertType.FINANCIAL,
        title="🎫 Нова заявка на підключення",
        message=f"Користувач @{query.from_user.username or 'N/A'}\nТариф: {data['tariff'].upper()}\nЗаявка #{app_id}"
    )
    
    for admin_id in ADMIN_IDS:
        try:
            admin_text = f"""🎫 <b>НОВА ЗАЯВКА #{app_id}</b>

<b>👤 Користувач:</b> @{query.from_user.username or 'N/A'}
<b>🆔 ID:</b> <code>{query.from_user.id}</code>

<b>📋 Деталі:</b>
├ Тариф: {data['tariff'].upper()}
├ Термін: {data['duration']} днів
├ Ім'я: {data['name']}
├ Мета: {data['purpose']}
└ Контакт: {data['contact']}

<b>🕐 Час:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}"""
            
            await bot.send_message(admin_id, admin_text, reply_markup=admin_app_kb(app_id), parse_mode="HTML")
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")
    
    await query.message.edit_text(
        f"""✅ <b>ЗАЯВКА НАДІСЛАНА</b>

Номер заявки: <b>#{app_id}</b>

Адміністратор зв'яжеться з вами найближчим часом для обговорення деталей оплати.

<i>Ви отримаєте повідомлення коли заявку буде оброблено.</i>""",
        parse_mode="HTML"
    )
    
    await state.clear()
    await query.answer("✅ Заявка відправлена!")

@applications_router.callback_query(F.data == "cancel_app")
async def cancel_application(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.edit_text("❌ Заявка скасована")
    await query.answer()

@applications_router.callback_query(F.data.startswith("admin_reply_"))
async def admin_reply_start(query: CallbackQuery, state: FSMContext):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонений", show_alert=True)
        return
    
    app_id = int(query.data.split("_")[2])
    await state.update_data(app_id=app_id)
    await state.set_state(AdminReplyFSM.waiting_reply)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_cancel")]
    ])
    
    await query.message.edit_text(
        f"💬 <b>ВІДПОВІДЬ НА ЗАЯВКУ #{app_id}</b>\n\n"
        f"Напишіть повідомлення для користувача:",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await query.answer()

@applications_router.message(AdminReplyFSM.waiting_reply)
async def admin_reply_send(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    app_id = data.get('app_id')
    app = applications_storage.get(app_id)
    
    if not app:
        await message.answer("❌ Заявка не знайдена")
        await state.clear()
        return
    
    app['messages'].append({
        "from": "admin",
        "text": message.text,
        "time": datetime.now().isoformat()
    })
    
    try:
        await bot.send_message(
            app['user_id'],
            f"""📩 <b>ПОВІДОМЛЕННЯ ВІД АДМІНІСТРАТОРА</b>

Щодо заявки #{app_id}:

{message.text}

<i>Для відповіді зверніться до підтримки</i>""",
            parse_mode="HTML"
        )
        
        await message.answer(f"✅ Повідомлення надіслано користувачу #{app['user_id']}")
    except Exception as e:
        await message.answer(f"❌ Помилка: {e}")
    
    await state.clear()

@applications_router.callback_query(F.data.startswith("admin_requisites_"))
async def admin_requisites_start(query: CallbackQuery, state: FSMContext):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонений", show_alert=True)
        return
    
    app_id = int(query.data.split("_")[2])
    await state.update_data(app_id=app_id)
    await state.set_state(AdminReplyFSM.waiting_requisites)
    
    app = applications_storage.get(app_id)
    tariff_prices = {"basic": 4200, "standard": 12500, "premium": 62500, "personal": 100000}
    price = tariff_prices.get(app['tariff'], 0) if app else 0
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Шаблон реквізитів", callback_data=f"template_req_{app_id}")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_cancel")]
    ])
    
    await query.message.edit_text(
        f"💳 <b>РЕКВІЗИТИ ДЛЯ ОПЛАТИ</b>\n\n"
        f"Заявка #{app_id}\n"
        f"Сума: {price:,} ₴\n\n"
        f"Введіть реквізити для надсилання користувачу:",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await query.answer()

@applications_router.callback_query(F.data.startswith("template_req_"))
async def template_requisites(query: CallbackQuery, state: FSMContext, bot: Bot):
    app_id = int(query.data.split("_")[2])
    app = applications_storage.get(app_id)
    
    if not app:
        await query.answer("❌ Заявка не знайдена", show_alert=True)
        return
    
    tariff_prices = {"basic": 4200, "standard": 12500, "premium": 62500, "personal": 100000}
    price = tariff_prices.get(app['tariff'], 0)
    
    requisites_text = f"""💳 <b>РЕКВІЗИТИ ДЛЯ ОПЛАТИ</b>

<b>Заявка:</b> #{app_id}
<b>Тариф:</b> {app['tariff'].upper()}
<b>Сума:</b> {price:,} ₴

<b>Реквізити:</b>
Картка: <code>4441 1144 5555 7777</code>
Одержувач: ФОП "Shadow System"

<b>Призначення:</b>
<code>Заявка #{app_id}</code>

⚠️ Після оплати надішліть скріншот квитанції адміністратору.

<i>Ключ буде активовано протягом 24 годин після підтвердження оплати.</i>"""
    
    try:
        await bot.send_message(app['user_id'], requisites_text, parse_mode="HTML")
        app['status'] = 'awaiting_payment'
        await query.message.edit_text(f"✅ Реквізити надіслано користувачу для заявки #{app_id}")
    except Exception as e:
        await query.message.edit_text(f"❌ Помилка: {e}")
    
    await state.clear()
    await query.answer()

@applications_router.callback_query(F.data.startswith("admin_genkey_"))
async def admin_generate_key(query: CallbackQuery, bot: Bot):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонений", show_alert=True)
        return
    
    app_id = int(query.data.split("_")[2])
    app = applications_storage.get(app_id)
    
    if not app:
        await query.answer("❌ Заявка не знайдена", show_alert=True)
        return
    
    key = encryption_manager.generate_secure_key("SHADOW")
    
    app['status'] = 'approved'
    app['license_key'] = key
    
    await audit_logger.log(
        user_id=query.from_user.id,
        action="license_key_generated",
        category=ActionCategory.AUTH,
        username=query.from_user.username,
        details={"app_id": app_id, "tariff": app['tariff']}
    )
    
    try:
        await bot.send_message(
            app['user_id'],
            f"""🔑 <b>ВАШ ЛІЦЕНЗІЙНИЙ КЛЮЧ</b>

<b>Заявка:</b> #{app_id}
<b>Тариф:</b> {app['tariff'].upper()}
<b>Термін:</b> {app['duration']} днів

<b>Ключ активації:</b>
<code>{key}</code>

Для активації введіть команду:
<code>/activate {key}</code>

⚠️ Збережіть ключ у безпечному місці!""",
            parse_mode="HTML"
        )
        
        await query.message.edit_text(
            f"✅ <b>КЛЮЧ ЗГЕНЕРОВАНО</b>\n\n"
            f"Заявка: #{app_id}\n"
            f"Ключ: <code>{key}</code>\n\n"
            f"Надіслано користувачу.",
            parse_mode="HTML"
        )
    except Exception as e:
        await query.message.edit_text(f"❌ Помилка: {e}")
    
    await query.answer("✅ Ключ згенеровано!")

@applications_router.callback_query(F.data.startswith("admin_reject_"))
async def admin_reject_app(query: CallbackQuery, bot: Bot):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонений", show_alert=True)
        return
    
    app_id = int(query.data.split("_")[2])
    app = applications_storage.get(app_id)
    
    if not app:
        await query.answer("❌ Заявка не знайдена", show_alert=True)
        return
    
    app['status'] = 'rejected'
    
    try:
        await bot.send_message(
            app['user_id'],
            f"""❌ <b>ЗАЯВКА ВІДХИЛЕНА</b>

Заявка #{app_id} була відхилена.

Для уточнення причини зверніться до підтримки.""",
            parse_mode="HTML"
        )
        await query.message.edit_text(f"❌ Заявка #{app_id} відхилена")
    except Exception as e:
        await query.message.edit_text(f"❌ Помилка: {e}")
    
    await query.answer()

@applications_router.callback_query(F.data == "admin_cancel")
async def admin_cancel(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.edit_text("❌ Операцію скасовано")
    await query.answer()

import logging
logger = logging.getLogger(__name__)
