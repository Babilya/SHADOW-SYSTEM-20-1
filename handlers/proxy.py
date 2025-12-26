from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import logging
import aiohttp
import asyncio

from config import ADMIN_IDS
from core.audit_logger import audit_logger, ActionCategory

logger = logging.getLogger(__name__)
proxy_router = Router()

class ProxyStates(StatesGroup):
    waiting_proxy_url = State()
    waiting_proxy_list = State()

def proxy_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Додати проксі", callback_data="proxy_add")],
        [InlineKeyboardButton(text="📋 Мої проксі", callback_data="proxy_list")],
        [InlineKeyboardButton(text="🔄 Перевірити всі", callback_data="proxy_check_all")],
        [InlineKeyboardButton(text="⚙️ Налаштування", callback_data="proxy_settings")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])

async def check_proxy(proxy_url: str, timeout: int = 10) -> dict:
    result = {
        "url": proxy_url,
        "is_working": False,
        "response_time": 0,
        "ip": None,
        "error": None
    }
    
    try:
        start_time = datetime.now()
        
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            proxy_dict = proxy_url if proxy_url.startswith("http") else f"http://{proxy_url}"
            
            async with session.get(
                "http://ip-api.com/json/",
                proxy=proxy_dict,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    result["is_working"] = True
                    result["ip"] = data.get("query")
                    result["response_time"] = (datetime.now() - start_time).total_seconds()
                else:
                    result["error"] = f"HTTP {response.status}"
                    
    except asyncio.TimeoutError:
        result["error"] = "Timeout"
    except aiohttp.ClientProxyConnectionError:
        result["error"] = "Connection failed"
    except Exception as e:
        result["error"] = str(e)[:50]
    
    return result

@proxy_router.callback_query(F.data == "proxy_menu")
async def proxy_menu(query: CallbackQuery):
    await query.answer()
    
    from database.crud import ProxyCRUD
    user_id = query.from_user.id
    user_proxies = await ProxyCRUD.get_user_proxies(user_id)
    active = len([p for p in user_proxies if p.is_active])
    
    text = f"""🌐 <b>УПРАВЛІННЯ ПРОКСІ</b>

<b>📊 Статистика:</b>
├ Всього: {len(user_proxies)}
├ Активних: {active}
└ Неактивних: {len(user_proxies) - active}

<b>⚙️ Можливості:</b>
• Додавання проксі (HTTP/SOCKS5)
• Автоматична перевірка
• Ротація для сесій
• Прив'язка до ботів"""
    
    await query.message.edit_text(text, reply_markup=proxy_kb(), parse_mode="HTML")

@proxy_router.callback_query(F.data == "proxy_add")
async def proxy_add(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(ProxyStates.waiting_proxy_url)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Додати список", callback_data="proxy_add_list")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="proxy_menu")]
    ])
    
    await query.message.edit_text(
        """➕ <b>ДОДАВАННЯ ПРОКСІ</b>

Введіть проксі у форматі:
<code>ip:port</code>
<code>ip:port:user:pass</code>
<code>http://ip:port</code>
<code>socks5://ip:port</code>

Або натисніть "Додати список" для масового додавання.""",
        reply_markup=kb, parse_mode="HTML"
    )

@proxy_router.message(ProxyStates.waiting_proxy_url)
async def proxy_add_process(message: Message, state: FSMContext):
    proxy_url = message.text.strip()
    user_id = message.from_user.id
    await state.clear()
    
    await message.answer("🔍 Перевіряю проксі...")
    
    check_result = await check_proxy(proxy_url)
    
    if check_result["is_working"]:
        from database.crud import ProxyCRUD
        await ProxyCRUD.add_proxy(
            owner_id=user_id,
            url=proxy_url,
            ip=check_result["ip"],
            response_time=check_result["response_time"]
        )
        
        await audit_logger.log(
            user_id=user_id,
            action="proxy_added",
            category=ActionCategory.SETTINGS,
            username=message.from_user.username,
            details={"ip": check_result["ip"]}
        )
        
        text = f"""✅ <b>ПРОКСІ ДОДАНО</b>

<b>IP:</b> {check_result['ip']}
<b>Час відповіді:</b> {check_result['response_time']:.2f}с
<b>Статус:</b> 🟢 Активний"""
    else:
        text = f"""❌ <b>ПРОКСІ НЕ ПРАЦЮЄ</b>

<b>Помилка:</b> {check_result['error']}

Перевірте правильність введених даних."""
    
    await message.answer(text, reply_markup=proxy_kb(), parse_mode="HTML")

@proxy_router.callback_query(F.data == "proxy_add_list")
async def proxy_add_list(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(ProxyStates.waiting_proxy_list)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="proxy_menu")]
    ])
    
    await query.message.edit_text(
        """📋 <b>МАСОВЕ ДОДАВАННЯ</b>

Введіть список проксі (кожен з нової строки):

<code>ip:port
ip:port:user:pass
socks5://ip:port</code>

Максимум 50 проксі за раз.""",
        reply_markup=kb, parse_mode="HTML"
    )

@proxy_router.message(ProxyStates.waiting_proxy_list)
async def proxy_add_list_process(message: Message, state: FSMContext):
    proxies = message.text.strip().split('\n')[:50]
    user_id = message.from_user.id
    await state.clear()
    
    await message.answer(f"🔍 Перевіряю {len(proxies)} проксі...")
    
    results = {"added": 0, "failed": 0}
    
    for proxy_url in proxies:
        proxy_url = proxy_url.strip()
        if not proxy_url:
            continue
            
        check_result = await check_proxy(proxy_url, timeout=5)
        
        if check_result["is_working"]:
            from database.crud import ProxyCRUD
            await ProxyCRUD.add_proxy(
                owner_id=user_id,
                url=proxy_url,
                ip=check_result["ip"],
                response_time=check_result["response_time"]
            )
            results["added"] += 1
        else:
            results["failed"] += 1
    
    await message.answer(
        f"""✅ <b>РЕЗУЛЬТАТ</b>

<b>Додано:</b> {results['added']}
<b>Не працюють:</b> {results['failed']}""",
        reply_markup=proxy_kb(), parse_mode="HTML"
    )

@proxy_router.callback_query(F.data == "proxy_list")
async def proxy_list(query: CallbackQuery):
    await query.answer()
    from database.crud import ProxyCRUD
    user_id = query.from_user.id
    user_proxies = await ProxyCRUD.get_user_proxies(user_id)
    
    if not user_proxies:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Додати", callback_data="proxy_add")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="proxy_menu")]
        ])
        await query.message.edit_text(
            "📋 <b>МОЇ ПРОКСІ</b>\n\nСписок порожній. Додайте проксі.",
            reply_markup=kb, parse_mode="HTML"
        )
        return
    
    text = "📋 <b>МОЇ ПРОКСІ</b>\n\n"
    
    buttons = []
    for i, proxy in enumerate(user_proxies[:10]):
        status = "🟢" if proxy.is_active else "🔴"
        ip = (proxy.ip or "Unknown")[:15]
        rt = proxy.response_time or 0
        text += f"{i+1}. {status} {ip} | {rt:.1f}s\n"
        buttons.append([InlineKeyboardButton(
            text=f"🗑 Видалити #{i+1}",
            callback_data=f"proxy_delete_{proxy.id}"
        )])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="proxy_menu")])
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )

@proxy_router.callback_query(F.data.startswith("proxy_delete_"))
async def proxy_delete(query: CallbackQuery):
    await query.answer()
    from database.crud import ProxyCRUD
    proxy_id = int(query.data.replace("proxy_delete_", ""))
    
    deleted = await ProxyCRUD.delete_proxy(proxy_id)
    if deleted:
        await query.message.edit_text(
            "✅ Проксі видалено",
            reply_markup=proxy_kb(),
            parse_mode="HTML"
        )
    else:
        await query.message.edit_text("❌ Проксі не знайдено", reply_markup=proxy_kb())

@proxy_router.callback_query(F.data == "proxy_check_all")
async def proxy_check_all(query: CallbackQuery):
    await query.answer()
    from database.crud import ProxyCRUD
    user_id = query.from_user.id
    user_proxies = await ProxyCRUD.get_user_proxies(user_id)
    
    if not user_proxies:
        await query.message.edit_text(
            "📋 Немає проксі для перевірки",
            reply_markup=proxy_kb()
        )
        return
    
    await query.message.edit_text(f"🔍 Перевіряю {len(user_proxies)} проксі...")
    
    active = 0
    for proxy in user_proxies:
        result = await check_proxy(proxy.url, timeout=5)
        await ProxyCRUD.update_proxy_status(
            proxy.id,
            is_active=result["is_working"],
            response_time=result.get("response_time")
        )
        if result["is_working"]:
            active += 1
    
    await query.message.edit_text(
        f"""✅ <b>ПЕРЕВІРКА ЗАВЕРШЕНА</b>

<b>Всього:</b> {len(user_proxies)}
<b>Активних:</b> {active}
<b>Неактивних:</b> {len(user_proxies) - active}""",
        reply_markup=proxy_kb(),
        parse_mode="HTML"
    )

@proxy_router.callback_query(F.data == "proxy_settings")
async def proxy_settings(query: CallbackQuery):
    await query.answer()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Авто-ротація: ВКЛ", callback_data="proxy_toggle_rotation")],
        [InlineKeyboardButton(text="⏱ Таймаут: 10с", callback_data="proxy_timeout")],
        [InlineKeyboardButton(text="🔁 Макс. спроб: 3", callback_data="proxy_max_retries")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="proxy_menu")]
    ])
    
    await query.message.edit_text(
        """⚙️ <b>НАЛАШТУВАННЯ ПРОКСІ</b>

<b>Авто-ротація:</b> Увімкнено
Автоматично змінює проксі при помилках

<b>Таймаут:</b> 10 секунд
Максимальний час очікування відповіді

<b>Макс. спроб:</b> 3
Кількість спроб перед деактивацією""",
        reply_markup=kb, parse_mode="HTML"
    )
