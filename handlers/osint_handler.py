import logging
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from database.repositories.osint_data_repository import OSINTDataRepository
from database.db import get_session
from core.osint_service import osint_service
from core.osint_tools.evidence_exporter import evidence_exporter
from core.ai_service import ai_service
import os

logger = logging.getLogger(__name__)
osint_router = Router()


@osint_router.message(Command("osint_data"))
async def cmd_osint_data(message: Message):
    """List OSINT data"""
    try:
        async with get_session() as session:
            repo = OSINTDataRepository(session)
            data = await repo.get_user_osint_data(message.from_user.id, limit=20)
            
            if not data:
                await message.answer("❌ OSINT даних не знайдено")
                return
            
            text = f"🔍 <b>Ваші OSINT дані ({len(data)}):</b>\n\n"
            for item in data:
                text += (
                    f"📋 {item.data_type}\n"
                    f"Файл: {item.filename or 'N/A'}\n"
                    f"Дата: {item.created_at.strftime('%d.%m.%Y')}\n"
                    f"─────────────\n"
                )
            
            await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error getting OSINT data: {e}")
        await message.answer(f"❌ Помилка: {e}")


@osint_router.message(Command("scan_chat"))
async def cmd_scan_chat(message: Message):
    """Scan telegram chat"""
    args = message.text.split()
    if len(args) < 2:
        await message.answer("🔍 <b>Сканування чату</b>\n\nВикористання: /scan_chat [username/ID]")
        return
    
    target = args[1]
    await message.answer(f"⏳ Починаю сканування <code>{target}</code>...", parse_mode="HTML")
    
    # Simulate deep analysis for demo purposes
    case_id = f"chat_{message.from_user.id}_{int(os.urandom(2).hex(), 16)}"
    sample_msgs = [
        {"sender": "user1", "text": "Який пароль від сервера?", "date": "2025-12-26T10:00:00"},
        {"sender": "user2", "text": "Спробуй 123456", "date": "2025-12-26T10:01:00"}
    ]
    
    analysis = await evidence_exporter.deep_chat_analysis(sample_msgs, case_id)
    report_path = evidence_exporter.generate_html_report(case_id, f"Звіт сканування {target}")
    
    if os.path.exists(report_path):
        await message.answer_document(
            FSInputFile(report_path),
            caption=f"✅ Сканування завершено!\n\nЗнайдено підозрілих патернів: {len(analysis.get('suspicious_patterns', []))}"
        )
    else:
        await message.answer("❌ Помилка генерації звіту")


@osint_router.message(Command("geo_scan"))
async def cmd_geo_scan(message: Message):
    """Geo scan chats"""
    args = message.text.split()
    if len(args) < 2:
        await message.answer("🗺️ <b>Гео-сканування</b>\n\nВикористання: /geo_scan [IP або координати lat,lon]")
        return
    
    target = args[1]
    await message.answer(f"⏳ Виконую гео-пошук для <code>{target}</code>...", parse_mode="HTML")
    
    if "." in target and "," not in target: # Assume IP
        res = await osint_service.ip_geolocation(target)
        if res.get("status") == "success":
            text = (
                f"📍 <b>Результати для {target}:</b>\n"
                f"Країна: {res.get('country')}\n"
                f"Місто: {res.get('city')}\n"
                f"ISP: {res.get('isp')}\n"
                f"Координати: {res.get('lat')}, {res.get('lon')}"
            )
            await message.answer(text, parse_mode="HTML")
        else:
            await message.answer("❌ Не вдалося отримати дані по IP")
    else:
        await message.answer("📡 Функція пошуку в радіусі координат у розробці")

@osint_router.message(Command("ai_report"))
async def cmd_ai_report(message: Message):
    """Generate AI OSINT report"""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("🤖 <b>AI OSINT Звіт</b>\n\nНапишіть дані про ціль після команди.")
        return
    
    target_info = {"raw_query": args[1], "user_id": message.from_user.id}
    await message.answer("🧠 ШІ аналізує дані...")
    
    report = await ai_service.generate_osint_report(target_info)
    await message.answer(f"📋 <b>Звіт аналізу:</b>\n\n{report}", parse_mode="HTML")
