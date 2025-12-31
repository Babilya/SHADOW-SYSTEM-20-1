from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import json
import logging

from config import ADMIN_IDS
from core.audit_logger import audit_logger, ActionCategory

logger = logging.getLogger(__name__)
configurator_router = Router()
router = configurator_router

class ConfigStates(StatesGroup):
    editing_button = State()
    editing_text = State()
    adding_banner = State()
    banner_image = State()
    banner_text = State()

cms_config = {
    "buttons": {
        "guest": {
            "view_tariffs": {"text": "📋 Тарифи", "visible": True, "order": 1},
            "submit_application": {"text": "📝 Подати заявку", "visible": True, "order": 2},
            "enter_key": {"text": "🔑 Ввести ключ", "visible": True, "order": 3},
            "support": {"text": "💬 Підтримка", "visible": True, "order": 4}
        },
        "manager": {
            "campaigns": {"text": "📧 Кампанії", "visible": True, "order": 1},
            "botnet": {"text": "🤖 Ботнет", "visible": True, "order": 2},
            "analytics": {"text": "📊 Аналітика", "visible": True, "order": 3},
            "osint": {"text": "🔍 OSINT", "visible": True, "order": 4}
        },
        "leader": {
            "team": {"text": "👥 Команда", "visible": True, "order": 1},
            "projects": {"text": "📁 Проекти", "visible": True, "order": 2},
            "keys": {"text": "🔑 Ключі", "visible": True, "order": 3}
        },
        "admin": {
            "users": {"text": "👥 Користувачі", "visible": True, "order": 1},
            "payments": {"text": "💰 Платежі", "visible": True, "order": 2},
            "config": {"text": "⚙️ Налаштування", "visible": True, "order": 3},
            "emergency": {"text": "🆘 Екстрена", "visible": True, "order": 4}
        }
    },
    "texts": {
        "welcome_guest": "👋 Ласкаво просимо до SHADOW SYSTEM iO!\n\nОберіть дію:",
        "welcome_manager": "🖥 РОБОЧИЙ СТІЛ МЕНЕДЖЕРА\n\nВаші інструменти:",
        "welcome_leader": "👑 ПАНЕЛЬ ЛІДЕРА\n\nУправління проектом:",
        "welcome_admin": "🛡️ АДМІНІСТРУВАННЯ\n\nПовний контроль:"
    },
    "banners": [],
    "last_updated": datetime.now().isoformat()
}

def save_config():
    cms_config["last_updated"] = datetime.now().isoformat()
    try:
        with open("cms_config.json", "w", encoding="utf-8") as f:
            json.dump(cms_config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving config: {e}")

def load_config():
    global cms_config
    try:
        with open("cms_config.json", "r", encoding="utf-8") as f:
            cms_config = json.load(f)
    except FileNotFoundError:
        save_config()
    except Exception as e:
        logger.error(f"Error loading config: {e}")

load_config()

def get_dynamic_buttons(role: str) -> list:
    role_buttons = cms_config["buttons"].get(role, {})
    visible = [(k, v) for k, v in role_buttons.items() if v.get("visible", True)]
    sorted_buttons = sorted(visible, key=lambda x: x[1].get("order", 99))
    return sorted_buttons

def get_welcome_text(role: str) -> str:
    return cms_config["texts"].get(f"welcome_{role}", "Вітаємо!")

def get_active_banners(section: str = None) -> list:
    banners = cms_config.get("banners", [])
    if section:
        return [b for b in banners if b.get("section") == section and b.get("active", True)]
    return [b for b in banners if b.get("active", True)]

def configurator_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔘 Кнопки", callback_data="cfg_buttons")],
        [InlineKeyboardButton(text="📝 Тексти", callback_data="cfg_texts")],
        [InlineKeyboardButton(text="🎨 Банери", callback_data="cfg_banners")],
        [InlineKeyboardButton(text="👁 Видимість ролей", callback_data="cfg_visibility")],
        [InlineKeyboardButton(text="💾 Експорт/Імпорт", callback_data="cfg_export")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])

@configurator_router.message(Command("config"))
async def config_command(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Доступ заборонено")
        return
    
    text = f"""⚙️ <b>CMS КОНФІГУРАТОР</b>

<b>Статус:</b> Активний
<b>Останнє оновлення:</b> {cms_config.get('last_updated', 'N/A')[:16]}

<b>Налаштування:</b>
├ Кнопок: {sum(len(v) for v in cms_config['buttons'].values())}
├ Текстів: {len(cms_config['texts'])}
└ Банерів: {len(cms_config.get('banners', []))}

Виберіть розділ для редагування:"""
    
    await message.answer(text, reply_markup=configurator_kb(), parse_mode="HTML")

@configurator_router.callback_query(F.data == "cfg_buttons")
async def cfg_buttons(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Guest", callback_data="cfg_btn_guest")],
        [InlineKeyboardButton(text="👷 Manager", callback_data="cfg_btn_manager")],
        [InlineKeyboardButton(text="👑 Leader", callback_data="cfg_btn_leader")],
        [InlineKeyboardButton(text="🛡️ Admin", callback_data="cfg_btn_admin")],
        [InlineKeyboardButton(text="➕ Додати кнопку", callback_data="cfg_btn_add")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="config_menu")]
    ])
    
    await query.message.edit_text(
        "🔘 <b>УПРАВЛІННЯ КНОПКАМИ</b>\n\nВиберіть роль для редагування кнопок:",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@configurator_router.callback_query(F.data.startswith("cfg_btn_"))
async def cfg_btn_role(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    role = query.data.replace("cfg_btn_", "")
    if role in ["add"]:
        await query.answer("Функція в розробці")
        return
    
    buttons = cms_config["buttons"].get(role, {})
    
    kb_buttons = []
    for btn_id, btn_data in buttons.items():
        status = "✅" if btn_data.get("visible", True) else "❌"
        kb_buttons.append([
            InlineKeyboardButton(
                text=f"{status} {btn_data['text']}", 
                callback_data=f"toggle_btn_{role}_{btn_id}"
            )
        ])
    
    kb_buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="cfg_buttons")])
    
    await query.message.edit_text(
        f"🔘 <b>КНОПКИ ДЛЯ {role.upper()}</b>\n\n"
        f"Натисніть на кнопку щоб приховати/показати:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_buttons),
        parse_mode="HTML"
    )
    await query.answer()

@configurator_router.callback_query(F.data.startswith("toggle_btn_"))
async def toggle_button(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    parts = query.data.split("_")
    role = parts[2]
    btn_id = parts[3]
    
    if role in cms_config["buttons"] and btn_id in cms_config["buttons"][role]:
        current = cms_config["buttons"][role][btn_id].get("visible", True)
        cms_config["buttons"][role][btn_id]["visible"] = not current
        save_config()
        
        await audit_logger.log(
            user_id=query.from_user.id,
            action="cms_button_toggle",
            category=ActionCategory.SYSTEM,
            username=query.from_user.username,
            details={"role": role, "button": btn_id, "visible": not current}
        )
        
        status = "показано" if not current else "приховано"
        await query.answer(f"Кнопку {status}!")
        
        await cfg_btn_role(query)
    else:
        await query.answer("Кнопку не знайдено")

@configurator_router.callback_query(F.data == "cfg_texts")
async def cfg_texts(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Привітання Guest", callback_data="edit_text_welcome_guest")],
        [InlineKeyboardButton(text="👷 Привітання Manager", callback_data="edit_text_welcome_manager")],
        [InlineKeyboardButton(text="👑 Привітання Leader", callback_data="edit_text_welcome_leader")],
        [InlineKeyboardButton(text="🛡️ Привітання Admin", callback_data="edit_text_welcome_admin")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="config_menu")]
    ])
    
    await query.message.edit_text(
        "📝 <b>УПРАВЛІННЯ ТЕКСТАМИ</b>\n\nВиберіть текст для редагування:",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@configurator_router.callback_query(F.data.startswith("edit_text_"))
async def edit_text_start(query: CallbackQuery, state: FSMContext):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    text_key = query.data.replace("edit_text_", "")
    current_text = cms_config["texts"].get(text_key, "")
    
    await state.update_data(text_key=text_key)
    await state.set_state(ConfigStates.editing_text)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="cfg_texts")]
    ])
    
    await query.message.edit_text(
        f"📝 <b>РЕДАГУВАННЯ ТЕКСТУ</b>\n\n"
        f"<b>Поточний текст:</b>\n<i>{current_text[:200]}...</i>\n\n"
        f"Надішліть новий текст:",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@configurator_router.message(ConfigStates.editing_text)
async def save_edited_text(message: Message, state: FSMContext):
    data = await state.get_data()
    text_key = data.get("text_key")
    
    cms_config["texts"][text_key] = message.text
    save_config()
    
    await audit_logger.log(
        user_id=message.from_user.id,
        action="cms_text_updated",
        category=ActionCategory.SYSTEM,
        username=message.from_user.username,
        details={"text_key": text_key}
    )
    
    await message.answer(f"✅ Текст <b>{text_key}</b> оновлено!", parse_mode="HTML")
    await state.clear()

@configurator_router.callback_query(F.data == "cfg_banners")
async def cfg_banners(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    banners = cms_config.get("banners", [])
    
    kb_buttons = []
    for i, banner in enumerate(banners):
        status = "🟢" if banner.get("active", True) else "🔴"
        kb_buttons.append([
            InlineKeyboardButton(
                text=f"{status} {banner.get('title', f'Банер {i+1}')[:20]}", 
                callback_data=f"banner_toggle_{i}"
            )
        ])
    
    kb_buttons.append([InlineKeyboardButton(text="➕ Додати банер", callback_data="banner_add")])
    kb_buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="config_menu")])
    
    await query.message.edit_text(
        f"🎨 <b>УПРАВЛІННЯ БАНЕРАМИ</b>\n\n"
        f"Активних банерів: {sum(1 for b in banners if b.get('active', True))}/{len(banners)}\n\n"
        f"Виберіть банер для редагування:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_buttons),
        parse_mode="HTML"
    )
    await query.answer()

@configurator_router.callback_query(F.data == "banner_add")
async def banner_add(query: CallbackQuery, state: FSMContext):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    await state.set_state(ConfigStates.adding_banner)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="cfg_banners")]
    ])
    
    await query.message.edit_text(
        "🎨 <b>ДОДАВАННЯ БАНЕРА</b>\n\n"
        "Введіть назву банера:",
        reply_markup=kb, parse_mode="HTML"
    )
    await query.answer()

@configurator_router.message(ConfigStates.adding_banner)
async def banner_title(message: Message, state: FSMContext):
    await state.update_data(banner_title=message.text)
    await state.set_state(ConfigStates.banner_text)
    await message.answer("📝 Введіть текст банера:")

@configurator_router.message(ConfigStates.banner_text)
async def banner_text_save(message: Message, state: FSMContext):
    data = await state.get_data()
    
    new_banner = {
        "title": data.get("banner_title"),
        "text": message.text,
        "image_url": None,
        "section": "main",
        "active": True,
        "created_at": datetime.now().isoformat()
    }
    
    if "banners" not in cms_config:
        cms_config["banners"] = []
    cms_config["banners"].append(new_banner)
    save_config()
    
    await message.answer("✅ Банер додано!\n\nМожете надіслати зображення або натисніть /skip")
    await state.clear()

@configurator_router.callback_query(F.data.startswith("banner_toggle_"))
async def banner_toggle(query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("❌ Доступ заборонено", show_alert=True)
        return
    
    idx = int(query.data.split("_")[2])
    if 0 <= idx < len(cms_config.get("banners", [])):
        current = cms_config["banners"][idx].get("active", True)
        cms_config["banners"][idx]["active"] = not current
        save_config()
        await query.answer(f"Банер {'активовано' if not current else 'деактивовано'}!")
        await cfg_banners(query)
    else:
        await query.answer("Банер не знайдено")

@configurator_router.callback_query(F.data == "config_menu")
async def config_menu(query: CallbackQuery):
    await query.message.edit_text(
        f"⚙️ <b>CMS КОНФІГУРАТОР</b>\n\n"
        f"Виберіть розділ:",
        reply_markup=configurator_kb(),
        parse_mode="HTML"
    )
    await query.answer()
