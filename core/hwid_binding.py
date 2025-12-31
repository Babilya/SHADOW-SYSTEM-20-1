import logging
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class BindingStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"


@dataclass
class HardwareFingerprint:
    device_id: str
    device_model: Optional[str] = None
    system_version: Optional[str] = None
    app_version: Optional[str] = None
    lang_code: Optional[str] = None
    ip_address: Optional[str] = None
    country_code: Optional[str] = None
    fingerprint_hash: str = ""
    collected_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not self.fingerprint_hash:
            self.fingerprint_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.device_id}:{self.device_model}:{self.system_version}:{self.app_version}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "device_model": self.device_model,
            "system_version": self.system_version,
            "app_version": self.app_version,
            "lang_code": self.lang_code,
            "ip_address": self.ip_address,
            "country_code": self.country_code,
            "fingerprint_hash": self.fingerprint_hash,
            "collected_at": self.collected_at.isoformat()
        }


@dataclass
class KeyBinding:
    key: str
    user_id: int
    telegram_id: int
    primary_fingerprint: HardwareFingerprint
    secondary_fingerprints: List[HardwareFingerprint] = field(default_factory=list)
    status: BindingStatus = BindingStatus.ACTIVE
    max_devices: int = 2
    created_at: datetime = field(default_factory=datetime.now)
    last_validated: Optional[datetime] = None
    validation_count: int = 0
    failed_validations: int = 0
    suspicious_attempts: List[Dict[str, Any]] = field(default_factory=list)


class HWIDBindingService:
    MAX_SUSPICIOUS_ATTEMPTS = 5
    FINGERPRINT_SIMILARITY_THRESHOLD = 0.7
    
    def __init__(self):
        self.bindings: Dict[str, KeyBinding] = {}
        self.user_keys: Dict[int, List[str]] = {}
        self.fingerprint_index: Dict[str, str] = {}
        self.stats = {
            "total_bindings": 0,
            "active_bindings": 0,
            "validations": 0,
            "suspicious_blocked": 0
        }
    
    def collect_fingerprint(
        self,
        device_id: str,
        device_model: Optional[str] = None,
        system_version: Optional[str] = None,
        app_version: Optional[str] = None,
        lang_code: Optional[str] = None,
        ip_address: Optional[str] = None,
        country_code: Optional[str] = None
    ) -> HardwareFingerprint:
        return HardwareFingerprint(
            device_id=device_id,
            device_model=device_model,
            system_version=system_version,
            app_version=app_version,
            lang_code=lang_code,
            ip_address=ip_address,
            country_code=country_code
        )
    
    def bind_key(
        self,
        key: str,
        user_id: int,
        telegram_id: int,
        fingerprint: HardwareFingerprint,
        max_devices: int = 2
    ) -> Dict[str, Any]:
        if key in self.bindings:
            return {"error": "Ключ вже прив'язано", "code": "KEY_ALREADY_BOUND"}
        
        if fingerprint.fingerprint_hash in self.fingerprint_index:
            existing_key = self.fingerprint_index[fingerprint.fingerprint_hash]
            return {
                "error": "Цей пристрій вже прив'язано до іншого ключа",
                "code": "DEVICE_ALREADY_BOUND",
                "existing_key": existing_key[:8] + "..."
            }
        
        binding = KeyBinding(
            key=key,
            user_id=user_id,
            telegram_id=telegram_id,
            primary_fingerprint=fingerprint,
            max_devices=max_devices
        )
        
        self.bindings[key] = binding
        self.fingerprint_index[fingerprint.fingerprint_hash] = key
        
        if user_id not in self.user_keys:
            self.user_keys[user_id] = []
        self.user_keys[user_id].append(key)
        
        self.stats["total_bindings"] += 1
        self.stats["active_bindings"] += 1
        
        logger.info(f"Key {key[:8]}... bound to user {user_id} with device {fingerprint.device_id[:8]}...")
        
        return {
            "success": True,
            "message": "Ключ успішно прив'язано до пристрою",
            "binding_id": key[:8],
            "device_hash": fingerprint.fingerprint_hash[:8]
        }
    
    def add_device(
        self,
        key: str,
        fingerprint: HardwareFingerprint
    ) -> Dict[str, Any]:
        binding = self.bindings.get(key)
        if not binding:
            return {"error": "Ключ не знайдено", "code": "KEY_NOT_FOUND"}
        
        if binding.status != BindingStatus.ACTIVE:
            return {"error": "Ключ заблоковано", "code": "KEY_SUSPENDED"}
        
        total_devices = 1 + len(binding.secondary_fingerprints)
        if total_devices >= binding.max_devices:
            return {
                "error": f"Досягнуто ліміт пристроїв ({binding.max_devices})",
                "code": "MAX_DEVICES_REACHED"
            }
        
        if fingerprint.fingerprint_hash == binding.primary_fingerprint.fingerprint_hash:
            return {"error": "Цей пристрій вже додано", "code": "DEVICE_EXISTS"}
        
        for fp in binding.secondary_fingerprints:
            if fp.fingerprint_hash == fingerprint.fingerprint_hash:
                return {"error": "Цей пристрій вже додано", "code": "DEVICE_EXISTS"}
        
        binding.secondary_fingerprints.append(fingerprint)
        self.fingerprint_index[fingerprint.fingerprint_hash] = key
        
        logger.info(f"Added secondary device to key {key[:8]}...")
        
        return {
            "success": True,
            "message": "Пристрій успішно додано",
            "devices_count": 1 + len(binding.secondary_fingerprints),
            "max_devices": binding.max_devices
        }
    
    def validate_key(
        self,
        key: str,
        fingerprint: HardwareFingerprint
    ) -> Dict[str, Any]:
        binding = self.bindings.get(key)
        if not binding:
            return {"valid": False, "error": "Ключ не знайдено", "code": "KEY_NOT_FOUND"}
        
        if binding.status == BindingStatus.REVOKED:
            return {"valid": False, "error": "Ключ відкликано", "code": "KEY_REVOKED"}
        
        if binding.status == BindingStatus.SUSPENDED:
            return {"valid": False, "error": "Ключ призупинено", "code": "KEY_SUSPENDED"}
        
        self.stats["validations"] += 1
        binding.validation_count += 1
        
        all_fingerprints = [binding.primary_fingerprint] + binding.secondary_fingerprints
        
        for fp in all_fingerprints:
            if fp.fingerprint_hash == fingerprint.fingerprint_hash:
                binding.last_validated = datetime.now()
                return {
                    "valid": True,
                    "message": "Ключ та пристрій підтверджено",
                    "device_type": "primary" if fp == binding.primary_fingerprint else "secondary"
                }
            
            similarity = self._calculate_similarity(fp, fingerprint)
            if similarity >= self.FINGERPRINT_SIMILARITY_THRESHOLD:
                binding.last_validated = datetime.now()
                return {
                    "valid": True,
                    "message": "Ключ підтверджено (схожий пристрій)",
                    "similarity": similarity
                }
        
        binding.failed_validations += 1
        binding.suspicious_attempts.append({
            "fingerprint": fingerprint.to_dict(),
            "timestamp": datetime.now().isoformat(),
            "reason": "unknown_device"
        })
        
        if binding.failed_validations >= self.MAX_SUSPICIOUS_ATTEMPTS:
            binding.status = BindingStatus.SUSPENDED
            self.stats["suspicious_blocked"] += 1
            logger.warning(f"Key {key[:8]}... suspended due to suspicious activity")
            
            return {
                "valid": False,
                "error": "Ключ призупинено через підозрілу активність",
                "code": "SUSPICIOUS_ACTIVITY"
            }
        
        return {
            "valid": False,
            "error": "Невідомий пристрій",
            "code": "UNKNOWN_DEVICE",
            "attempts_remaining": self.MAX_SUSPICIOUS_ATTEMPTS - binding.failed_validations
        }
    
    def _calculate_similarity(
        self,
        fp1: HardwareFingerprint,
        fp2: HardwareFingerprint
    ) -> float:
        matches = 0
        total = 0
        
        if fp1.device_model and fp2.device_model:
            total += 1
            if fp1.device_model == fp2.device_model:
                matches += 1
        
        if fp1.system_version and fp2.system_version:
            total += 1
            if fp1.system_version.split('.')[0] == fp2.system_version.split('.')[0]:
                matches += 0.5
            if fp1.system_version == fp2.system_version:
                matches += 0.5
        
        if fp1.app_version and fp2.app_version:
            total += 1
            if fp1.app_version == fp2.app_version:
                matches += 1
        
        if fp1.lang_code and fp2.lang_code:
            total += 1
            if fp1.lang_code == fp2.lang_code:
                matches += 1
        
        if fp1.country_code and fp2.country_code:
            total += 1
            if fp1.country_code == fp2.country_code:
                matches += 1
        
        return matches / total if total > 0 else 0
    
    def revoke_key(self, key: str, reason: str = "manual") -> bool:
        binding = self.bindings.get(key)
        if not binding:
            return False
        
        binding.status = BindingStatus.REVOKED
        self.stats["active_bindings"] -= 1
        
        logger.info(f"Key {key[:8]}... revoked: {reason}")
        return True
    
    def suspend_key(self, key: str, reason: str = "manual") -> bool:
        binding = self.bindings.get(key)
        if not binding:
            return False
        
        binding.status = BindingStatus.SUSPENDED
        logger.info(f"Key {key[:8]}... suspended: {reason}")
        return True
    
    def reactivate_key(self, key: str) -> bool:
        binding = self.bindings.get(key)
        if not binding or binding.status == BindingStatus.REVOKED:
            return False
        
        binding.status = BindingStatus.ACTIVE
        binding.failed_validations = 0
        binding.suspicious_attempts = []
        
        logger.info(f"Key {key[:8]}... reactivated")
        return True
    
    def remove_device(self, key: str, fingerprint_hash: str) -> Dict[str, Any]:
        binding = self.bindings.get(key)
        if not binding:
            return {"error": "Ключ не знайдено"}
        
        if binding.primary_fingerprint.fingerprint_hash == fingerprint_hash:
            return {"error": "Неможливо видалити основний пристрій"}
        
        for i, fp in enumerate(binding.secondary_fingerprints):
            if fp.fingerprint_hash == fingerprint_hash:
                binding.secondary_fingerprints.pop(i)
                if fingerprint_hash in self.fingerprint_index:
                    del self.fingerprint_index[fingerprint_hash]
                return {"success": True, "message": "Пристрій видалено"}
        
        return {"error": "Пристрій не знайдено"}
    
    def get_binding_info(self, key: str) -> Optional[Dict[str, Any]]:
        binding = self.bindings.get(key)
        if not binding:
            return None
        
        return {
            "key": key[:8] + "...",
            "user_id": binding.user_id,
            "telegram_id": binding.telegram_id,
            "status": binding.status.value,
            "devices": {
                "primary": binding.primary_fingerprint.to_dict(),
                "secondary": [fp.to_dict() for fp in binding.secondary_fingerprints],
                "count": 1 + len(binding.secondary_fingerprints),
                "max": binding.max_devices
            },
            "validation_count": binding.validation_count,
            "failed_validations": binding.failed_validations,
            "suspicious_attempts": len(binding.suspicious_attempts),
            "created_at": binding.created_at.isoformat(),
            "last_validated": binding.last_validated.isoformat() if binding.last_validated else None
        }
    
    def get_user_bindings(self, user_id: int) -> List[Dict[str, Any]]:
        keys = self.user_keys.get(user_id, [])
        return [self.get_binding_info(key) for key in keys if self.get_binding_info(key)]
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            **self.stats,
            "suspended_keys": sum(1 for b in self.bindings.values() if b.status == BindingStatus.SUSPENDED),
            "revoked_keys": sum(1 for b in self.bindings.values() if b.status == BindingStatus.REVOKED)
        }
    
    def format_binding_message(self, key: str) -> str:
        info = self.get_binding_info(key)
        if not info:
            return "❌ Ключ не знайдено"
        
        status_icons = {
            "active": "🟢",
            "suspended": "🟡",
            "revoked": "🔴"
        }
        
        devices_list = ""
        devices_list += f"  └ 📱 Основний: {info['devices']['primary']['device_model'] or 'N/A'}\n"
        for i, dev in enumerate(info['devices']['secondary'], 1):
            devices_list += f"  └ 📱 Додатковий {i}: {dev['device_model'] or 'N/A'}\n"
        
        return f"""🔐 <b>ПРИВ'ЯЗКА КЛЮЧА</b>

<b>Ключ:</b> <code>{info['key']}</code>
<b>Статус:</b> {status_icons.get(info['status'], '⚪')} {info['status'].upper()}

───────────────

<b>📱 Пристрої ({info['devices']['count']}/{info['devices']['max']}):</b>
{devices_list}
<b>📊 Статистика:</b>
├ Валідацій: {info['validation_count']}
├ Невдалих: {info['failed_validations']}
└ Підозрілих: {info['suspicious_attempts']}

<b>📅 Створено:</b> {info['created_at'][:10]}
<b>🕐 Остання перевірка:</b> {info['last_validated'][:10] if info['last_validated'] else 'Ніколи'}"""


hwid_binding_service = HWIDBindingService()
