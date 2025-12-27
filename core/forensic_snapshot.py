"""
Forensic Snapshot - Модуль медіа-криміналістики
Автоматично створює дзеркало всіх медіа-файлів з оригінальними метаданими
"""

import asyncio
import hashlib
import json
import math
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class MediaForensicData:
    """Форензичні дані медіа-файлу"""
    file_id: str
    original_hash: str
    forensic_hash: str
    timestamp: datetime
    user_id: int
    chat_id: int
    message_id: int
    media_type: str
    original_metadata: Dict = field(default_factory=dict)
    extracted_metadata: Dict = field(default_factory=dict)
    file_size: int = 0
    file_path: str = ""
    deleted: bool = False
    deletion_time: Optional[datetime] = None
    snapshot_path: str = ""


class ForensicSnapshot:
    """Система форензичного знімку медіа-файлів"""
    
    def __init__(self, storage_path: str = "data/forensic_snapshots"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.media_registry: Dict[str, MediaForensicData] = {}
        self.capture_stats = {
            "total_captured": 0,
            "total_size_bytes": 0,
            "by_type": {},
            "recovered": 0
        }
    
    async def capture_media(self, file_data: bytes, file_info: Dict, 
                          context: Dict) -> MediaForensicData:
        """Захоплення медіа-файлу з створенням форензичного знімку"""
        original_hash = hashlib.sha256(file_data).hexdigest()
        forensic_hash = hashlib.sha512(file_data).hexdigest()
        
        extracted_metadata = await self._extract_all_metadata(file_data, file_info)
        
        snapshot_id = f"{forensic_hash[:16]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        snapshot_path = self.storage_path / f"{snapshot_id}.forensic"
        
        with open(snapshot_path, 'wb') as f:
            f.write(file_data)
        
        media_type = file_info.get('mime_type', 'unknown').split('/')[0]
        
        forensic_data = MediaForensicData(
            file_id=file_info.get('file_id', ''),
            original_hash=original_hash,
            forensic_hash=forensic_hash,
            timestamp=datetime.now(),
            user_id=context.get('user_id', 0),
            chat_id=context.get('chat_id', 0),
            message_id=context.get('message_id', 0),
            media_type=media_type,
            original_metadata=file_info.get('metadata', {}),
            extracted_metadata=extracted_metadata,
            file_size=len(file_data),
            file_path=str(snapshot_path),
            snapshot_path=str(snapshot_path)
        )
        
        self.media_registry[forensic_hash] = forensic_data
        
        self.capture_stats["total_captured"] += 1
        self.capture_stats["total_size_bytes"] += len(file_data)
        self.capture_stats["by_type"][media_type] = self.capture_stats["by_type"].get(media_type, 0) + 1
        
        await self._save_metadata(forensic_data)
        
        logger.info(f"Captured media: {forensic_hash[:16]}...")
        return forensic_data
    
    async def _extract_all_metadata(self, file_data: bytes, file_info: Dict) -> Dict:
        """Витягнення всіх можливих метаданих"""
        metadata = {
            "basic": {
                "size": len(file_data),
                "hash_sha256": hashlib.sha256(file_data).hexdigest(),
                "hash_md5": hashlib.md5(file_data).hexdigest(),
                "timestamp": datetime.now().isoformat()
            },
            "forensic": {
                "entropy": self._calculate_entropy(file_data),
                "magic_bytes": file_data[:8].hex() if len(file_data) >= 8 else '',
                "file_signature": self._analyze_file_signature(file_data)
            }
        }
        
        if 'location' in file_info:
            metadata["geolocation"] = file_info['location']
        
        return metadata
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Розрахунок ентропії даних"""
        if not data:
            return 0.0
        
        entropy = 0.0
        for x in range(256):
            p_x = float(data.count(bytes([x]))) / len(data)
            if p_x > 0:
                entropy += - p_x * math.log(p_x, 2)
        
        return round(entropy, 4)
    
    def _analyze_file_signature(self, data: bytes) -> str:
        """Аналіз сигнатури файлу"""
        signatures = {
            b'\xff\xd8\xff': 'JPEG',
            b'\x89PNG': 'PNG',
            b'GIF8': 'GIF',
            b'%PDF': 'PDF',
            b'PK\x03\x04': 'ZIP',
            b'\x00\x00\x00\x1c': 'MP4',
            b'\x1a\x45\xdf\xa3': 'WEBM',
            b'OggS': 'OGG',
            b'ID3': 'MP3',
        }
        
        for sig, fmt in signatures.items():
            if data.startswith(sig):
                return fmt
        
        return 'UNKNOWN'
    
    async def _save_metadata(self, forensic_data: MediaForensicData):
        """Збереження метаданих у JSON"""
        meta_path = self.storage_path / f"{forensic_data.forensic_hash[:16]}.json"
        
        data = asdict(forensic_data)
        data['timestamp'] = forensic_data.timestamp.isoformat()
        if forensic_data.deletion_time:
            data['deletion_time'] = forensic_data.deletion_time.isoformat()
        
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    async def recover_deleted_media(self, forensic_hash: str) -> Optional[bytes]:
        """Відновлення видаленого медіа-файлу"""
        if forensic_hash not in self.media_registry:
            for key in self.media_registry:
                if key.startswith(forensic_hash):
                    forensic_hash = key
                    break
            else:
                return None
        
        forensic_data = self.media_registry[forensic_hash]
        
        try:
            with open(forensic_data.file_path, 'rb') as f:
                data = f.read()
            
            forensic_data.deleted = True
            forensic_data.deletion_time = datetime.now()
            self.capture_stats["recovered"] += 1
            
            logger.info(f"Recovered media: {forensic_hash[:16]}...")
            return data
            
        except Exception as e:
            logger.error(f"Recovery failed: {e}")
            return None
    
    def get_media_forensic_report(self, forensic_hash: str) -> Dict:
        """Отримання форензичного звіту"""
        if forensic_hash not in self.media_registry:
            for key in self.media_registry:
                if key.startswith(forensic_hash):
                    forensic_hash = key
                    break
            else:
                return {"error": "Медіа не знайдено"}
        
        forensic_data = self.media_registry[forensic_hash]
        data = asdict(forensic_data)
        data['timestamp'] = forensic_data.timestamp.isoformat()
        
        return {
            "forensic_data": data,
            "integrity": self._verify_integrity(forensic_data)
        }
    
    def _verify_integrity(self, forensic_data: MediaForensicData) -> Dict:
        """Перевірка цілісності даних"""
        try:
            with open(forensic_data.file_path, 'rb') as f:
                current_data = f.read()
            
            current_hash = hashlib.sha256(current_data).hexdigest()
            
            return {
                "verified": current_hash == forensic_data.original_hash,
                "current_hash": current_hash[:16],
                "original_hash": forensic_data.original_hash[:16],
                "tampered": current_hash != forensic_data.original_hash
            }
        except Exception as e:
            return {"error": str(e), "verified": False}
    
    def get_all_snapshots(self, limit: int = 50) -> List[Dict]:
        """Отримання списку всіх знімків"""
        snapshots = []
        for hash_id, data in list(self.media_registry.items())[:limit]:
            snapshots.append({
                "hash": hash_id[:16],
                "type": data.media_type,
                "size": data.file_size,
                "timestamp": data.timestamp.isoformat(),
                "deleted": data.deleted
            })
        return snapshots
    
    def get_stats(self) -> Dict:
        """Отримання статистики"""
        return {
            **self.capture_stats,
            "registry_size": len(self.media_registry)
        }
    
    def format_report(self) -> str:
        """Форматування звіту"""
        stats = self.get_stats()
        size_mb = round(stats["total_size_bytes"] / (1024 * 1024), 2)
        
        text = f"""<b>🔬 FORENSIC SNAPSHOT</b>
<i>Медіа-криміналістика</i>

───────────────

<b>📊 СТАТИСТИКА:</b>
├ 📸 Захоплено: <b>{stats['total_captured']}</b>
├ 💾 Розмір: <b>{size_mb} MB</b>
├ 🔄 Відновлено: <b>{stats['recovered']}</b>
└ 📁 В реєстрі: <b>{stats['registry_size']}</b>

<b>📁 ПО ТИПАХ:</b>"""
        
        for media_type, count in stats.get("by_type", {}).items():
            text += f"\n├ {media_type}: <b>{count}</b>"
        
        if not stats.get("by_type"):
            text += "\n<i>Немає даних</i>"
        
        return text


forensic_snapshot = ForensicSnapshot()
