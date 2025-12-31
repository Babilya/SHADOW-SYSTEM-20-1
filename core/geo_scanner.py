import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class GeoEntity:
    entity_id: int
    name: str
    entity_type: str
    distance_meters: int
    members_count: int = 0
    username: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    last_seen: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GeoScanConfig:
    latitude: float
    longitude: float
    radius_meters: int = 5000
    include_users: bool = True
    include_groups: bool = True
    include_channels: bool = True
    max_results: int = 100
    timeout: int = 30


class GeoScanner:
    def __init__(self):
        self.scan_history: List[Dict[str, Any]] = []
        self.cached_results: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 300
    
    def _get_cache_key(self, lat: float, lng: float, radius: int) -> str:
        lat_rounded = round(lat, 3)
        lng_rounded = round(lng, 3)
        return f"{lat_rounded}:{lng_rounded}:{radius}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        if cache_key not in self.cached_results:
            return False
        cached = self.cached_results[cache_key]
        cached_time = cached.get("timestamp", 0)
        return (datetime.now().timestamp() - cached_time) < self.cache_ttl
    
    async def scan_nearby(self, config: GeoScanConfig) -> Dict[str, Any]:
        cache_key = self._get_cache_key(config.latitude, config.longitude, config.radius_meters)
        
        if self._is_cache_valid(cache_key):
            logger.info(f"Returning cached geo results for {cache_key}")
            return self.cached_results[cache_key]["data"]
        
        result = {
            "status": "success",
            "latitude": config.latitude,
            "longitude": config.longitude,
            "radius_meters": config.radius_meters,
            "timestamp": datetime.now().isoformat(),
            "entities": [],
            "stats": {
                "users": 0,
                "groups": 0,
                "channels": 0,
                "total": 0
            }
        }
        
        try:
            from core.session_manager import session_manager
            
            available_sessions = list(session_manager.imported_sessions.keys())
            
            if not available_sessions:
                result["status"] = "no_sessions"
                result["message"] = "Немає активних сесій для гео-сканування"
                return result
            
            session_hash = available_sessions[0]
            client = await session_manager.connect_client(session_hash)
            
            if not client:
                result["status"] = "connection_failed"
                result["message"] = "Не вдалося підключитися до Telegram"
                return result
            
            entities = await self._scan_with_telethon(client, config)
            
            for entity in entities:
                if entity.entity_type == "user" and not config.include_users:
                    continue
                if entity.entity_type == "group" and not config.include_groups:
                    continue
                if entity.entity_type == "channel" and not config.include_channels:
                    continue
                
                result["entities"].append({
                    "id": entity.entity_id,
                    "name": entity.name,
                    "type": entity.entity_type,
                    "distance_m": entity.distance_meters,
                    "distance_km": round(entity.distance_meters / 1000, 2),
                    "members": entity.members_count,
                    "username": entity.username,
                    "metadata": entity.metadata
                })
                
                if entity.entity_type == "user":
                    result["stats"]["users"] += 1
                elif entity.entity_type == "group":
                    result["stats"]["groups"] += 1
                elif entity.entity_type == "channel":
                    result["stats"]["channels"] += 1
            
            result["stats"]["total"] = len(result["entities"])
            
            self.cached_results[cache_key] = {
                "timestamp": datetime.now().timestamp(),
                "data": result
            }
            
            self.scan_history.append({
                "timestamp": datetime.now().isoformat(),
                "latitude": config.latitude,
                "longitude": config.longitude,
                "radius": config.radius_meters,
                "results_count": len(result["entities"])
            })
            
            logger.info(f"Geo scan completed: {len(result['entities'])} entities found")
            
        except ImportError:
            result["status"] = "telethon_unavailable"
            result["message"] = "Telethon не доступний"
        except Exception as e:
            logger.error(f"Geo scan error: {e}")
            result["status"] = "error"
            result["message"] = str(e)
        
        return result
    
    async def _scan_with_telethon(self, client, config: GeoScanConfig) -> List[GeoEntity]:
        entities = []
        
        try:
            from telethon.tl.functions.contacts import GetLocatedRequest
            from telethon.tl.types import InputGeoPoint, PeerLocated, PeerSelfLocated
            
            geo_point = InputGeoPoint(lat=config.latitude, long=config.longitude)
            
            located_result = await asyncio.wait_for(
                client(GetLocatedRequest(
                    geo_point=geo_point,
                    self_expires=0
                )),
                timeout=config.timeout
            )
            
            if not hasattr(located_result, 'updates') or not located_result.updates:
                return entities
            
            chats_map = {}
            users_map = {}
            
            if hasattr(located_result, 'chats'):
                for chat in located_result.chats:
                    chats_map[chat.id] = chat
            
            if hasattr(located_result, 'users'):
                for user in located_result.users:
                    users_map[user.id] = user
            
            for update in located_result.updates:
                if not hasattr(update, 'peers'):
                    continue
                
                for peer in update.peers:
                    if isinstance(peer, PeerSelfLocated):
                        continue
                    
                    if not isinstance(peer, PeerLocated):
                        continue
                    
                    distance = getattr(peer, 'distance', 0)
                    
                    if distance > config.radius_meters:
                        continue
                    
                    peer_id = peer.peer
                    entity_id = None
                    entity_name = "Unknown"
                    entity_type = "unknown"
                    members = 0
                    username = None
                    
                    if hasattr(peer_id, 'user_id'):
                        entity_id = peer_id.user_id
                        entity_type = "user"
                        if entity_id in users_map:
                            user = users_map[entity_id]
                            entity_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                            username = getattr(user, 'username', None)
                    
                    elif hasattr(peer_id, 'channel_id'):
                        entity_id = peer_id.channel_id
                        entity_type = "channel"
                        if entity_id in chats_map:
                            chat = chats_map[entity_id]
                            entity_name = getattr(chat, 'title', 'Channel')
                            members = getattr(chat, 'participants_count', 0) or 0
                            username = getattr(chat, 'username', None)
                            if getattr(chat, 'megagroup', False):
                                entity_type = "group"
                    
                    elif hasattr(peer_id, 'chat_id'):
                        entity_id = peer_id.chat_id
                        entity_type = "group"
                        if entity_id in chats_map:
                            chat = chats_map[entity_id]
                            entity_name = getattr(chat, 'title', 'Group')
                            members = getattr(chat, 'participants_count', 0) or 0
                    
                    if entity_id:
                        entities.append(GeoEntity(
                            entity_id=entity_id,
                            name=entity_name,
                            entity_type=entity_type,
                            distance_meters=distance,
                            members_count=members,
                            username=username,
                            latitude=config.latitude,
                            longitude=config.longitude
                        ))
            
            entities.sort(key=lambda x: x.distance_meters)
            return entities[:config.max_results]
            
        except asyncio.TimeoutError:
            logger.warning("Geo scan timed out")
        except Exception as e:
            logger.error(f"Telethon geo scan error: {e}")
        
        return entities
    
    async def find_users_nearby(
        self,
        latitude: float,
        longitude: float,
        max_results: int = 50
    ) -> Dict[str, Any]:
        config = GeoScanConfig(
            latitude=latitude,
            longitude=longitude,
            include_users=True,
            include_groups=False,
            include_channels=False,
            max_results=max_results
        )
        
        result = await self.scan_nearby(config)
        result["type"] = "users_only"
        return result
    
    async def find_chats_nearby(
        self,
        latitude: float,
        longitude: float,
        max_results: int = 100
    ) -> Dict[str, Any]:
        config = GeoScanConfig(
            latitude=latitude,
            longitude=longitude,
            include_users=False,
            include_groups=True,
            include_channels=True,
            max_results=max_results
        )
        
        result = await self.scan_nearby(config)
        result["type"] = "chats_only"
        return result
    
    def get_scan_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self.scan_history[-limit:]
    
    def clear_cache(self):
        self.cached_results.clear()
        logger.info("Geo cache cleared")
    
    def format_results(self, result: Dict[str, Any]) -> str:
        lines = []
        lines.append("<b>🌍 РЕЗУЛЬТАТИ ГЕО-СКАНУВАННЯ</b>")
        lines.append("═══════════════════════")
        lines.append("")
        
        if result.get("status") != "success":
            lines.append(f"❌ <b>Помилка:</b> {result.get('message', 'Невідома помилка')}")
            return "\n".join(lines)
        
        lines.append(f"<b>📍 Координати:</b> {result['latitude']:.4f}, {result['longitude']:.4f}")
        lines.append(f"<b>📏 Радіус:</b> {result['radius_meters']}м")
        lines.append("")
        
        stats = result.get("stats", {})
        lines.append("<b>📊 Статистика:</b>")
        lines.append(f"├ 👥 Користувачів: {stats.get('users', 0)}")
        lines.append(f"├ 💬 Груп: {stats.get('groups', 0)}")
        lines.append(f"├ 📢 Каналів: {stats.get('channels', 0)}")
        lines.append(f"└ 📌 Всього: {stats.get('total', 0)}")
        lines.append("")
        
        entities = result.get("entities", [])
        if entities:
            lines.append("<b>🎯 Знайдені об'єкти:</b>")
            for i, entity in enumerate(entities[:15], 1):
                icon = {"user": "👤", "group": "💬", "channel": "📢"}.get(entity["type"], "📍")
                name = entity["name"][:25]
                distance = entity.get("distance_km", 0)
                
                if entity.get("username"):
                    lines.append(f"{i}. {icon} <b>{name}</b> (@{entity['username']})")
                else:
                    lines.append(f"{i}. {icon} <b>{name}</b>")
                
                extra = f"📍 {distance}км"
                if entity.get("members"):
                    extra += f" | 👥 {entity['members']}"
                lines.append(f"   └ {extra}")
            
            if len(entities) > 15:
                lines.append(f"\n<i>...та ще {len(entities) - 15} об'єктів</i>")
        else:
            lines.append("<i>Нічого не знайдено в цьому радіусі</i>")
        
        return "\n".join(lines)


geo_scanner = GeoScanner()
