from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.role_menus import apply_kb

router = Router()

TARIFF_DETAILS = {
    "baseus": "🔹 BASEUS\n✅ 5 ботів, 1 менеджер\n💰 2д:2800₴ 14д:5900₴ 30д:8400₴",
    "standard": "🔶 STANDARD\n✅ 50 ботів, 5 менеджерів, OSINT\n💰 2д:2800₴ 14д:5900₴ 30д:8400₴"
}

@router.callback_query(F.data.startswith("tariff_"))
async def tariff_detail(query: CallbackQuery):
    tariff = query.data.split("_")[1]
    if tariff in TARIFF_DETAILS:
        await query.message.edit_text(TARIFF_DETAILS[tariff], reply_markup=apply_kb(tariff))
    await query.answer()
