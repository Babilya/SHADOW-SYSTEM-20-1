TARIFF_CONFIG = {
    "baseus": {
        "name": "Baseus",
        "emoji": "🔹",
        "description": "Тест/Новачок",
        "bots_limit": 5,
        "managers_limit": 1,
        "osint_enabled": False,
        "prices": {2: 2800, 14: 5900, 30: 8400},
        "period": "terminy"
    },
    "standard": {
        "name": "Standard",
        "emoji": "🔶",
        "description": "Агенція/Арбітраж",
        "bots_limit": 50,
        "managers_limit": 5,
        "osint_enabled": True,
        "prices": {2: 2800, 14: 5900, 30: 8400},
        "period": "terminy"
    },
    "premium": {
        "name": "Premium",
        "emoji": "👑",
        "description": "PRO/Швидкість",
        "bots_limit": 100,
        "managers_limit": 999,
        "osint_enabled": True,
        "prices": {2: 5900, 14: 11800, 30: 16800},
        "period": "terminy"
    },
    "person": {
        "name": "Person",
        "emoji": "💎",
        "description": "Enterprise",
        "bots_limit": 999,
        "managers_limit": 999,
        "osint_enabled": True,
        "prices": {"custom": "узгоджується"},
        "period": "custom"
    }
}

ADMIN_TEMPLATES = {
    "mono_payment": "💳 Реквізити (Карта Monobank)\n\nВітаю! Оплата на карту: 5375 4100 1234 5678",
    "usdt_payment": "🪙 Реквізити (USDT TRC-20)\n\nВітаю! USDT TRC20: TYj8uVx5B9d7C6e5F4g3H2i1J0k9L8m7",
    "clarify_details": "❓ Уточнити деталі\n\nДоброго дня! Уточніть будь ласка детальніше вашу мету використання.",
    "call_manager": "📞 Зателефонувати\n\nДякуємо за заявку! Наш менеджер спеціально зв'яжеться з вами."
}

REJECTION_REASONS = {
    1: "⚠️ Підозріла мета використання",
    2: "💬 Не відповідає на повідомлення",
    3: "🚫 Порушення правил",
    4: "✏️ Інша причина"
}
