"""
Клавіатури для модулів криміналістики та покращеного моніторингу
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional

def forensics_main_kb() -> InlineKeyboardMarkup:
    """Головна клавіатура криміналістики"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔬 Forensic Snapshot", callback_data="forensic_main")],
        [InlineKeyboardButton(text="🧠 AI Sentiment", callback_data="sentiment_main")],
        [InlineKeyboardButton(text="👻 Anti-Ghost Recovery", callback_data="ghost_main")],
        [InlineKeyboardButton(text="🔍 X-Ray Metadata", callback_data="xray_main")],
        [InlineKeyboardButton(text="💾 Memory Indexer", callback_data="indexer_main")],
        [InlineKeyboardButton(text="📡 Enhanced Monitoring", callback_data="monitoring_main")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="user_menu")]
    ])


def forensic_snapshot_kb() -> InlineKeyboardMarkup:
    """Клавіатура Forensic Snapshot"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Захопити медіа", callback_data="forensic_capture")],
        [
            InlineKeyboardButton(text="📋 Всі знімки", callback_data="forensic_list"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="forensic_stats")
        ],
        [InlineKeyboardButton(text="🔄 Відновити видалене", callback_data="forensic_recover")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="forensics_menu")]
    ])


def ai_sentiment_kb() -> InlineKeyboardMarkup:
    """Клавіатура AI Sentiment"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Аналізувати текст", callback_data="sentiment_analyze")],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="sentiment_stats"),
            InlineKeyboardButton(text="📈 Звіт", callback_data="sentiment_report")
        ],
        [InlineKeyboardButton(text="⚙️ Налаштування AI", callback_data="sentiment_settings")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="forensics_menu")]
    ])


def ghost_recovery_kb() -> InlineKeyboardMarkup:
    """Клавіатура Anti-Ghost Recovery"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Видалені повідомлення", callback_data="ghost_deleted")],
        [
            InlineKeyboardButton(text="✏️ Історія редагувань", callback_data="ghost_edits"),
            InlineKeyboardButton(text="🔍 Пошук", callback_data="ghost_search")
        ],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="ghost_stats")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="forensics_menu")]
    ])


def xray_metadata_kb() -> InlineKeyboardMarkup:
    """Клавіатура X-Ray Metadata"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔬 Аналізувати файл", callback_data="xray_analyze")],
        [
            InlineKeyboardButton(text="📋 Результати", callback_data="xray_results"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="xray_stats")
        ],
        [InlineKeyboardButton(text="⚠️ Аномалії", callback_data="xray_anomalies")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="forensics_menu")]
    ])


def memory_indexer_kb() -> InlineKeyboardMarkup:
    """Клавіатура Memory Indexer"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Пошук", callback_data="indexer_search")],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="indexer_stats"),
            InlineKeyboardButton(text="🧹 Очистити", callback_data="indexer_cleanup")
        ],
        [InlineKeyboardButton(text="📁 По типах", callback_data="indexer_by_type")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="forensics_menu")]
    ])


def monitoring_main_kb() -> InlineKeyboardMarkup:
    """Клавіатура Enhanced Monitoring"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Додати ціль", callback_data="monitor_add")],
        [
            InlineKeyboardButton(text="📋 Мої цілі", callback_data="monitor_targets"),
            InlineKeyboardButton(text="⚠️ Сповіщення", callback_data="monitor_alerts")
        ],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="monitor_stats"),
            InlineKeyboardButton(text="📈 Події", callback_data="monitor_events")
        ],
        [InlineKeyboardButton(text="🔔 Тригери", callback_data="monitor_triggers")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="forensics_menu")]
    ])


def monitoring_target_kb(target_id: int, is_active: bool) -> InlineKeyboardMarkup:
    """Клавіатура цілі моніторингу"""
    toggle_text = "⏸ Зупинити" if is_active else "▶️ Запустити"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=toggle_text, callback_data=f"monitor_toggle:{target_id}"),
            InlineKeyboardButton(text="📊 Статистика", callback_data=f"monitor_target_stats:{target_id}")
        ],
        [
            InlineKeyboardButton(text="🔔 Тригери", callback_data=f"monitor_target_triggers:{target_id}"),
            InlineKeyboardButton(text="📋 Події", callback_data=f"monitor_target_events:{target_id}")
        ],
        [InlineKeyboardButton(text="🗑 Видалити", callback_data=f"monitor_delete:{target_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="monitor_targets")]
    ])


def monitoring_alerts_kb(alerts_count: int = 0) -> InlineKeyboardMarkup:
    """Клавіатура сповіщень"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"⚠️ Непрочитані ({alerts_count})", callback_data="monitor_alerts_unread")],
        [InlineKeyboardButton(text="✅ Прочитані", callback_data="monitor_alerts_read")],
        [InlineKeyboardButton(text="🗑 Очистити все", callback_data="monitor_alerts_clear")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="monitoring_main")]
    ])


def alert_action_kb(alert_id: str) -> InlineKeyboardMarkup:
    """Клавіатура дії зі сповіщенням"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Прочитано", callback_data=f"alert_ack:{alert_id}"),
            InlineKeyboardButton(text="🔍 Деталі", callback_data=f"alert_details:{alert_id}")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="monitor_alerts")]
    ])


def trigger_types_kb(target_id: int) -> InlineKeyboardMarkup:
    """Клавіатура типів тригерів"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔤 Ключове слово", callback_data=f"trigger_keyword:{target_id}")],
        [InlineKeyboardButton(text="📝 Регулярний вираз", callback_data=f"trigger_regex:{target_id}")],
        [InlineKeyboardButton(text="📋 Мої тригери", callback_data=f"trigger_list:{target_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"monitor_view:{target_id}")]
    ])


def back_to_forensics_kb() -> InlineKeyboardMarkup:
    """Кнопка повернення до криміналістики"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="forensics_menu")]
    ])


def confirm_action_kb(action: str, item_id: str) -> InlineKeyboardMarkup:
    """Клавіатура підтвердження дії"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Так", callback_data=f"confirm_{action}:{item_id}"),
            InlineKeyboardButton(text="❌ Ні", callback_data=f"cancel_{action}:{item_id}")
        ]
    ])
