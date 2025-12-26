import secrets, string
from datetime import datetime, timedelta

def generate_access_key(tariff: str, days: int = 30) -> tuple:
    """Генерує ключ доступу та дату експірації"""
    tariff_map = {"basic": "BASE", "standard": "STD", "premium": "PRE", "personal": "PER"}
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

def generate_invite_code(leader_id: int) -> str:
    """Генерує INV-код для запрошення менеджера"""
    seg1 = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    seg2 = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    return f"INV-{seg1}-{seg2}"

def generate_shadow_key(tariff: str = "standard") -> str:
    """Генерує SHADOW ключ для ліцензії"""
    tariff_map = {"basic": "BASE", "standard": "STD", "premium": "PRE", "personal": "PER"}
    prefix = tariff_map.get(tariff, "STD")
    seg1 = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    seg2 = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    return f"SHADOW-{prefix}-{seg1}-{seg2}"

invite_codes_storage = {}
license_keys_storage = {}

def store_invite_code(code: str, leader_id: int, project_id: int = None):
    """Зберігає invite-код (in-memory + DB fallback)"""
    invite_codes_storage[code] = {
        "leader_id": leader_id,
        "project_id": project_id or leader_id,
        "created_at": datetime.now().isoformat(),
        "used": False,
        "used_by": None
    }

def validate_invite_code(code: str) -> dict:
    """Валідує invite-код"""
    if code in invite_codes_storage:
        data = invite_codes_storage[code]
        if not data["used"]:
            return data
    return None

def use_invite_code(code: str, manager_id: int) -> bool:
    """Використовує invite-код"""
    if code in invite_codes_storage:
        invite_codes_storage[code]["used"] = True
        invite_codes_storage[code]["used_by"] = manager_id
        invite_codes_storage[code]["used_at"] = datetime.now().isoformat()
        return True
    return False

def store_license_key(key: str, user_id: int, tariff: str, days: int):
    """Зберігає ліцензійний ключ (in-memory)"""
    license_keys_storage[key] = {
        "user_id": user_id,
        "tariff": tariff,
        "days": days,
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(days=days)).isoformat(),
        "activated": False,
        "activated_by": None
    }

def validate_license_key(key: str) -> dict:
    """Валідує ліцензійний ключ"""
    if key in license_keys_storage:
        data = license_keys_storage[key]
        if not data["activated"]:
            return data
    return None

def activate_license_key(key: str, user_id: int) -> bool:
    """Активує ліцензійний ключ"""
    if key in license_keys_storage:
        license_keys_storage[key]["activated"] = True
        license_keys_storage[key]["activated_by"] = user_id
        license_keys_storage[key]["activated_at"] = datetime.now().isoformat()
        return True
    return False

async def create_key_in_db(tariff: str, days: int) -> str:
    """Створює ключ в базі даних"""
    from database.crud import KeyCRUD
    expires = datetime.now() + timedelta(days=days)
    key = await KeyCRUD.create_async(tariff=tariff, expires_at=expires)
    license_keys_storage[key.code] = {
        "user_id": None,
        "tariff": tariff,
        "days": days,
        "expires_at": expires.isoformat(),
        "activated": False
    }
    return key.code

async def validate_key_from_db(code: str) -> dict:
    """Валідує ключ з бази даних"""
    from database.crud import KeyCRUD
    key = await KeyCRUD.validate_key(code)
    if key:
        return {
            "tariff": key.tariff,
            "expires_at": key.expires_at.isoformat() if key.expires_at else None,
            "user_id": key.user_id
        }
    if code in license_keys_storage:
        data = license_keys_storage[code]
        if not data.get("activated"):
            return data
    return None

async def activate_key_in_db(code: str, user_id: int) -> bool:
    """Активує ключ в базі даних"""
    from database.crud import KeyCRUD
    success = await KeyCRUD.use_key(code, str(user_id))
    if success:
        if code in license_keys_storage:
            license_keys_storage[code]["activated"] = True
            license_keys_storage[code]["activated_by"] = user_id
        return True
    if code in license_keys_storage:
        license_keys_storage[code]["activated"] = True
        license_keys_storage[code]["activated_by"] = user_id
        return True
    return False
