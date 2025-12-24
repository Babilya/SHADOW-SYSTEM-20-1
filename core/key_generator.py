import secrets, string
from datetime import datetime, timedelta

def generate_access_key(tariff: str, days: int = 30) -> tuple:
    """Генерує ключ доступу та дату експірації"""
    tariff_map = {"baseus": "BASE", "standard": "STD", "premium": "PRE", "person": "PER"}
    prefix = f"SHADOW-{tariff_map.get(tariff, 'CUS')}"
    
    seg1 = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    seg2 = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    
    key = f"{prefix}-{seg1}-{seg2}"
    expires = datetime.now() + timedelta(days=days)
    
    return key, expires

def generate_ticket_id() -> str:
    """Генерує ID тікету"""
    return ''.join(secrets.choice(string.digits) for _ in range(6))

def generate_manager_key(project_id: int, role: str) -> str:
    """Генерує ключ для менеджера"""
    return f"MGR-{project_id}-{role[:3]}-{secrets.token_hex(4).upper()}"
