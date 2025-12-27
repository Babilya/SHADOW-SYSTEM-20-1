"""
X-Ray Metadata - Модуль глибокого аналізу метаданих
Витягує приховану інформацію з файлів та повідомлень
"""

import asyncio
import hashlib
import json
import re
import struct
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class XRayResult:
    """Результат X-Ray аналізу"""
    file_id: str
    file_type: str
    file_size: int
    analysis_time: datetime
    basic_metadata: Dict = field(default_factory=dict)
    hidden_data: Dict = field(default_factory=dict)
    geolocation: Optional[Dict] = None
    device_info: Optional[Dict] = None
    timestamps: Dict = field(default_factory=dict)
    signatures: List[str] = field(default_factory=list)
    anomalies: List[str] = field(default_factory=list)
    risk_score: float = 0.0


class XRayMetadata:
    """Система X-Ray аналізу метаданих"""
    
    FILE_SIGNATURES = {
        b'\xff\xd8\xff\xe0': ('JPEG', 'image'),
        b'\xff\xd8\xff\xe1': ('JPEG/EXIF', 'image'),
        b'\x89PNG\r\n\x1a\n': ('PNG', 'image'),
        b'GIF87a': ('GIF87', 'image'),
        b'GIF89a': ('GIF89', 'image'),
        b'%PDF-': ('PDF', 'document'),
        b'PK\x03\x04': ('ZIP/DOCX', 'archive'),
        b'Rar!\x1a\x07': ('RAR', 'archive'),
        b'\x00\x00\x00\x1c': ('MP4/MOV', 'video'),
        b'\x00\x00\x00\x20': ('MP4', 'video'),
        b'\x1a\x45\xdf\xa3': ('WebM/MKV', 'video'),
        b'OggS': ('OGG', 'audio'),
        b'ID3': ('MP3', 'audio'),
        b'\xff\xfb': ('MP3', 'audio'),
        b'fLaC': ('FLAC', 'audio'),
        b'RIFF': ('WAV/AVI', 'media'),
    }
    
    EXIF_TAGS = {
        0x010F: 'Make',
        0x0110: 'Model',
        0x0112: 'Orientation',
        0x011A: 'XResolution',
        0x011B: 'YResolution',
        0x0132: 'DateTime',
        0x8769: 'ExifOffset',
        0x8825: 'GPSInfo',
        0xA002: 'ExifImageWidth',
        0xA003: 'ExifImageHeight',
        0x9003: 'DateTimeOriginal',
        0x9004: 'DateTimeDigitized',
    }
    
    def __init__(self, storage_path: str = "data/xray_results"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.analysis_cache: Dict[str, XRayResult] = {}
        self.stats = {
            "total_analyzed": 0,
            "by_type": {},
            "anomalies_found": 0,
            "geo_extracted": 0
        }
    
    async def analyze(self, file_data: bytes, file_info: Dict = None) -> XRayResult:
        """Повний X-Ray аналіз файлу"""
        file_info = file_info or {}
        file_id = file_info.get('file_id', hashlib.md5(file_data[:1000]).hexdigest())
        
        if file_id in self.analysis_cache:
            return self.analysis_cache[file_id]
        
        file_type, category = self._detect_file_type(file_data)
        
        result = XRayResult(
            file_id=file_id,
            file_type=file_type,
            file_size=len(file_data),
            analysis_time=datetime.now()
        )
        
        result.basic_metadata = self._extract_basic_metadata(file_data, file_info)
        result.signatures = self._extract_signatures(file_data)
        result.timestamps = self._extract_timestamps(file_data)
        
        if category == 'image':
            exif_data = self._extract_exif(file_data)
            result.basic_metadata.update(exif_data)
            
            if 'gps' in exif_data:
                result.geolocation = exif_data['gps']
                self.stats["geo_extracted"] += 1
            
            if 'device' in exif_data:
                result.device_info = exif_data['device']
        
        result.hidden_data = self._search_hidden_data(file_data)
        
        result.anomalies = self._detect_anomalies(file_data, result)
        result.risk_score = self._calculate_risk_score(result)
        
        if result.anomalies:
            self.stats["anomalies_found"] += len(result.anomalies)
        
        self.analysis_cache[file_id] = result
        
        self.stats["total_analyzed"] += 1
        self.stats["by_type"][file_type] = self.stats["by_type"].get(file_type, 0) + 1
        
        await self._save_result(result)
        
        return result
    
    def _detect_file_type(self, data: bytes) -> Tuple[str, str]:
        """Визначення типу файлу за сигнатурою"""
        for sig, (file_type, category) in self.FILE_SIGNATURES.items():
            if data.startswith(sig):
                return file_type, category
        
        return 'UNKNOWN', 'unknown'
    
    def _extract_basic_metadata(self, data: bytes, file_info: Dict) -> Dict:
        """Витягнення базових метаданих"""
        return {
            "size_bytes": len(data),
            "size_kb": round(len(data) / 1024, 2),
            "hash_md5": hashlib.md5(data).hexdigest(),
            "hash_sha256": hashlib.sha256(data).hexdigest()[:32],
            "magic_bytes": data[:16].hex(),
            "entropy": self._calculate_entropy(data),
            "null_bytes_ratio": data.count(b'\x00') / max(len(data), 1),
            "printable_ratio": sum(1 for b in data if 32 <= b <= 126) / max(len(data), 1),
            **file_info
        }
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Розрахунок ентропії"""
        import math
        if not data:
            return 0.0
        
        freq = {}
        for byte in data:
            freq[byte] = freq.get(byte, 0) + 1
        
        entropy = 0.0
        for count in freq.values():
            p = count / len(data)
            if p > 0:
                entropy -= p * math.log2(p)
        
        return round(entropy, 4)
    
    def _extract_signatures(self, data: bytes) -> List[str]:
        """Витягнення всіх знайдених сигнатур"""
        signatures = []
        
        for sig, (file_type, _) in self.FILE_SIGNATURES.items():
            pos = data.find(sig)
            if pos != -1:
                signatures.append(f"{file_type}@{pos}")
        
        patterns = [
            (b'Photoshop', 'Adobe_Photoshop'),
            (b'GIMP', 'GIMP'),
            (b'Adobe', 'Adobe_Product'),
            (b'Canon', 'Canon_Camera'),
            (b'NIKON', 'Nikon_Camera'),
            (b'Apple', 'Apple_Device'),
            (b'Samsung', 'Samsung_Device'),
            (b'DCIM', 'Camera_Image'),
        ]
        
        for pattern, name in patterns:
            if pattern in data:
                signatures.append(name)
        
        return signatures
    
    def _extract_timestamps(self, data: bytes) -> Dict:
        """Витягнення часових міток"""
        timestamps = {}
        
        datetime_pattern = rb'\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}'
        matches = re.findall(datetime_pattern, data)
        
        for i, match in enumerate(matches[:5]):
            try:
                dt_str = match.decode('ascii')
                timestamps[f"timestamp_{i}"] = dt_str
            except:
                pass
        
        return timestamps
    
    def _extract_exif(self, data: bytes) -> Dict:
        """Витягнення EXIF даних"""
        exif = {}
        
        try:
            exif_start = data.find(b'Exif\x00\x00')
            if exif_start == -1:
                return exif
            
            for pattern, name in [
                (b'Make', 'make'),
                (b'Model', 'model'),
                (b'DateTime', 'datetime'),
                (b'Software', 'software'),
            ]:
                pos = data.find(pattern, exif_start)
                if pos != -1:
                    value_start = pos + len(pattern) + 1
                    value_end = data.find(b'\x00', value_start)
                    if value_end != -1 and value_end - value_start < 100:
                        try:
                            value = data[value_start:value_end].decode('ascii', errors='ignore').strip()
                            if value:
                                exif[name] = value
                        except:
                            pass
            
            gps_pos = data.find(b'GPS')
            if gps_pos != -1:
                exif['gps'] = {'found': True, 'position': gps_pos}
            
            if exif.get('make') or exif.get('model'):
                exif['device'] = {
                    'make': exif.get('make', ''),
                    'model': exif.get('model', '')
                }
        
        except Exception as e:
            logger.warning(f"EXIF extraction error: {e}")
        
        return exif
    
    def _search_hidden_data(self, data: bytes) -> Dict:
        """Пошук прихованих даних"""
        hidden = {}
        
        strings = []
        current = []
        for byte in data:
            if 32 <= byte <= 126:
                current.append(chr(byte))
            else:
                if len(current) >= 8:
                    strings.append(''.join(current))
                current = []
        
        interesting = [s for s in strings if any(kw in s.lower() for kw in 
            ['http', 'www', '@', 'password', 'secret', 'key', 'token', 'api'])]
        
        if interesting:
            hidden['suspicious_strings'] = interesting[:10]
        
        urls = re.findall(rb'https?://[^\s\x00]+', data)
        if urls:
            hidden['embedded_urls'] = [u.decode('ascii', errors='ignore') for u in urls[:5]]
        
        emails = re.findall(rb'[\w\.-]+@[\w\.-]+\.\w+', data)
        if emails:
            hidden['embedded_emails'] = [e.decode('ascii', errors='ignore') for e in emails[:5]]
        
        return hidden
    
    def _detect_anomalies(self, data: bytes, result: XRayResult) -> List[str]:
        """Виявлення аномалій"""
        anomalies = []
        
        entropy = result.basic_metadata.get('entropy', 0)
        if entropy > 7.9:
            anomalies.append("HIGH_ENTROPY: Можливе шифрування або стиснення")
        elif entropy < 1.0 and len(data) > 1000:
            anomalies.append("LOW_ENTROPY: Підозріла однорідність даних")
        
        if len(result.signatures) > 3:
            anomalies.append("MULTI_SIGNATURE: Виявлено декілька типів файлів")
        
        if result.hidden_data.get('embedded_urls'):
            anomalies.append("HIDDEN_URLS: Знайдено вбудовані URL")
        
        if result.hidden_data.get('suspicious_strings'):
            anomalies.append("SUSPICIOUS_STRINGS: Знайдено підозрілі рядки")
        
        null_ratio = result.basic_metadata.get('null_bytes_ratio', 0)
        if null_ratio > 0.5:
            anomalies.append("HIGH_NULL_BYTES: Можливий padding або стеганографія")
        
        return anomalies
    
    def _calculate_risk_score(self, result: XRayResult) -> float:
        """Розрахунок рівня ризику"""
        score = 0.0
        
        score += len(result.anomalies) * 0.15
        
        if result.hidden_data.get('embedded_urls'):
            score += 0.2
        
        if result.hidden_data.get('suspicious_strings'):
            score += 0.15
        
        entropy = result.basic_metadata.get('entropy', 0)
        if entropy > 7.5:
            score += 0.1
        
        return min(round(score, 2), 1.0)
    
    async def _save_result(self, result: XRayResult):
        """Збереження результату"""
        file_path = self.storage_path / f"{result.file_id[:16]}.json"
        
        data = {
            "file_id": result.file_id,
            "file_type": result.file_type,
            "file_size": result.file_size,
            "analysis_time": result.analysis_time.isoformat(),
            "basic_metadata": result.basic_metadata,
            "hidden_data": result.hidden_data,
            "geolocation": result.geolocation,
            "device_info": result.device_info,
            "timestamps": result.timestamps,
            "signatures": result.signatures,
            "anomalies": result.anomalies,
            "risk_score": result.risk_score
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Save error: {e}")
    
    def get_stats(self) -> Dict:
        """Отримання статистики"""
        return {
            **self.stats,
            "cache_size": len(self.analysis_cache)
        }
    
    def format_result(self, result: XRayResult) -> str:
        """Форматування результату"""
        risk_bar = "█" * int(result.risk_score * 10) + "░" * (10 - int(result.risk_score * 10))
        risk_level = "🟢 LOW" if result.risk_score < 0.3 else "🟡 MEDIUM" if result.risk_score < 0.6 else "🔴 HIGH"
        
        text = f"""<b>🔬 X-RAY METADATA ANALYSIS</b>

<b>📁 Файл:</b> <code>{result.file_id[:16]}...</code>
<b>📂 Тип:</b> {result.file_type}
<b>📊 Розмір:</b> {result.basic_metadata.get('size_kb', 0)} KB

───────────────

<b>⚠️ РИЗИК:</b> {risk_bar} {result.risk_score * 100:.0f}%
<b>Рівень:</b> {risk_level}

<b>📋 СИГНАТУРИ:</b>"""
        
        for sig in result.signatures[:5]:
            text += f"\n├ {sig}"
        
        if not result.signatures:
            text += "\n├ <i>Не виявлено</i>"
        
        text += "\n\n<b>🔍 МЕТАДАНІ:</b>"
        text += f"\n├ Ентропія: {result.basic_metadata.get('entropy', 0)}"
        text += f"\n├ MD5: <code>{result.basic_metadata.get('hash_md5', '')[:16]}...</code>"
        
        if result.device_info:
            text += f"\n\n<b>📱 ПРИСТРІЙ:</b>"
            text += f"\n├ {result.device_info.get('make', '')} {result.device_info.get('model', '')}"
        
        if result.geolocation:
            text += f"\n\n<b>📍 ГЕОЛОКАЦІЯ:</b> Знайдено"
        
        if result.anomalies:
            text += f"\n\n<b>⚠️ АНОМАЛІЇ ({len(result.anomalies)}):</b>"
            for anomaly in result.anomalies[:3]:
                text += f"\n├ {anomaly}"
        
        if result.hidden_data.get('embedded_urls'):
            text += f"\n\n<b>🔗 ВБУДОВАНІ URL:</b>"
            for url in result.hidden_data['embedded_urls'][:3]:
                text += f"\n├ {url[:50]}..."
        
        return text
    
    def format_stats_report(self) -> str:
        """Форматування звіту статистики"""
        stats = self.get_stats()
        
        text = f"""<b>🔬 X-RAY METADATA</b>
<i>Глибокий аналіз метаданих</i>

───────────────

<b>📊 СТАТИСТИКА:</b>
├ 🔍 Проаналізовано: <b>{stats['total_analyzed']}</b>
├ ⚠️ Аномалій: <b>{stats['anomalies_found']}</b>
├ 📍 Геолокацій: <b>{stats['geo_extracted']}</b>
└ 💾 В кеші: <b>{stats['cache_size']}</b>

<b>📁 ПО ТИПАХ:</b>"""
        
        for file_type, count in stats.get("by_type", {}).items():
            text += f"\n├ {file_type}: <b>{count}</b>"
        
        if not stats.get("by_type"):
            text += "\n<i>Немає даних</i>"
        
        return text


xray_metadata = XRayMetadata()
