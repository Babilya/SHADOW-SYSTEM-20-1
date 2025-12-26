import asyncio
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy import text
import aiohttp

logger = logging.getLogger(__name__)

class LoginTracker:
    def __init__(self):
        self.geoip_cache = {}
        self._cache_ttl = 3600
    
    async def track_login(
        self,
        user_id: int,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True
    ) -> dict:
        geo_data = await self._get_geo_data(ip_address) if ip_address else {}
        
        try:
            from database.db import async_session
            async with async_session() as session:
                await session.execute(
                    text("""
                        INSERT INTO login_attempts 
                        (user_id, username, ip_address, user_agent, country, city, success, created_at)
                        VALUES (:user_id, :username, :ip_address, :user_agent, :country, :city, :success, NOW())
                    """),
                    {
                        "user_id": user_id,
                        "username": username,
                        "ip_address": ip_address,
                        "user_agent": user_agent,
                        "country": geo_data.get("country"),
                        "city": geo_data.get("city"),
                        "success": success
                    }
                )
                await session.commit()
            
            if not success:
                from core.antifraud import antifraud_service
                await antifraud_service.track_activity(user_id, "failed_login", f"IP: {ip_address}")
            
            return {
                "tracked": True,
                "geo": geo_data
            }
        except Exception as e:
            logger.error(f"Failed to track login: {e}")
            return {"tracked": False, "error": str(e)}
    
    async def _get_geo_data(self, ip_address: str) -> dict:
        if ip_address in self.geoip_cache:
            cached = self.geoip_cache[ip_address]
            if (datetime.now() - cached["timestamp"]).seconds < self._cache_ttl:
                return cached["data"]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://ip-api.com/json/{ip_address}?lang=uk") as response:
                    if response.status == 200:
                        data = await response.json()
                        geo_data = {
                            "country": data.get("country"),
                            "country_code": data.get("countryCode"),
                            "city": data.get("city"),
                            "region": data.get("regionName"),
                            "isp": data.get("isp"),
                            "lat": data.get("lat"),
                            "lon": data.get("lon")
                        }
                        self.geoip_cache[ip_address] = {
                            "data": geo_data,
                            "timestamp": datetime.now()
                        }
                        return geo_data
        except Exception as e:
            logger.warning(f"Failed to get geo data for {ip_address}: {e}")
        
        return {}
    
    async def get_login_history(
        self,
        user_id: int,
        limit: int = 50,
        success_only: Optional[bool] = None
    ) -> list:
        try:
            from database.db import async_session
            async with async_session() as session:
                query = "SELECT * FROM login_attempts WHERE user_id = :user_id"
                params = {"user_id": user_id, "limit": limit}
                
                if success_only is not None:
                    query += " AND success = :success"
                    params["success"] = success_only
                
                query += " ORDER BY created_at DESC LIMIT :limit"
                
                result = await session.execute(text(query), params)
                rows = result.fetchall()
                
                return [
                    {
                        "id": row.id,
                        "ip_address": row.ip_address,
                        "country": row.country,
                        "city": row.city,
                        "success": row.success,
                        "created_at": row.created_at.isoformat() if row.created_at else None
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Failed to get login history: {e}")
            return []
    
    async def get_suspicious_logins(self, user_id: int) -> list:
        try:
            from database.db import async_session
            async with async_session() as session:
                result = await session.execute(
                    text("""
                        SELECT DISTINCT country, city, COUNT(*) as count
                        FROM login_attempts 
                        WHERE user_id = :user_id AND success = true
                        GROUP BY country, city
                        ORDER BY count DESC
                    """),
                    {"user_id": user_id}
                )
                usual_locations = result.fetchall()
                
                if not usual_locations:
                    return []
                
                main_country = usual_locations[0].country if usual_locations else None
                
                result = await session.execute(
                    text("""
                        SELECT * FROM login_attempts 
                        WHERE user_id = :user_id 
                        AND country != :main_country
                        ORDER BY created_at DESC
                        LIMIT 20
                    """),
                    {"user_id": user_id, "main_country": main_country}
                )
                
                return [
                    {
                        "ip_address": row.ip_address,
                        "country": row.country,
                        "city": row.city,
                        "created_at": row.created_at.isoformat() if row.created_at else None
                    }
                    for row in result.fetchall()
                ]
        except Exception as e:
            logger.error(f"Failed to get suspicious logins: {e}")
            return []

login_tracker = LoginTracker()
