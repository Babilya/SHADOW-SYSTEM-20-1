import logging
from typing import Optional, List, Set
from sqlalchemy import text

logger = logging.getLogger(__name__)

class IPWhitelistService:
    def __init__(self):
        self.whitelist: dict = {}
        self._loaded = False
    
    async def load(self):
        try:
            from database.db import async_session
            async with async_session() as session:
                result = await session.execute(
                    text("SELECT user_id, ip_address FROM admin_ip_whitelist WHERE is_active = true")
                )
                for row in result.fetchall():
                    user_id = int(row.user_id)
                    if user_id not in self.whitelist:
                        self.whitelist[user_id] = set()
                    self.whitelist[user_id].add(row.ip_address)
                
                self._loaded = True
                logger.info(f"Loaded IP whitelist for {len(self.whitelist)} users")
        except Exception as e:
            logger.error(f"Failed to load IP whitelist: {e}")
    
    async def is_allowed(self, user_id: int, ip_address: Optional[str] = None) -> bool:
        if not self._loaded:
            await self.load()
        
        if user_id not in self.whitelist:
            return True
        
        if not ip_address:
            return False
        
        return ip_address in self.whitelist[user_id]
    
    async def add_ip(self, user_id: int, ip_address: str, description: Optional[str] = None) -> bool:
        try:
            from database.db import async_session
            async with async_session() as session:
                await session.execute(
                    text("""
                        INSERT INTO admin_ip_whitelist (user_id, ip_address, description, is_active, created_at)
                        VALUES (:user_id, :ip_address, :description, true, NOW())
                    """),
                    {"user_id": user_id, "ip_address": ip_address, "description": description}
                )
                await session.commit()
            
            if user_id not in self.whitelist:
                self.whitelist[user_id] = set()
            self.whitelist[user_id].add(ip_address)
            
            logger.info(f"Added IP {ip_address} to whitelist for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add IP to whitelist: {e}")
            return False
    
    async def remove_ip(self, user_id: int, ip_address: str) -> bool:
        try:
            from database.db import async_session
            async with async_session() as session:
                await session.execute(
                    text("""
                        UPDATE admin_ip_whitelist 
                        SET is_active = false 
                        WHERE user_id = :user_id AND ip_address = :ip_address
                    """),
                    {"user_id": user_id, "ip_address": ip_address}
                )
                await session.commit()
            
            if user_id in self.whitelist:
                self.whitelist[user_id].discard(ip_address)
            
            return True
        except Exception as e:
            logger.error(f"Failed to remove IP from whitelist: {e}")
            return False
    
    async def get_user_ips(self, user_id: int) -> List[dict]:
        try:
            from database.db import async_session
            async with async_session() as session:
                result = await session.execute(
                    text("SELECT * FROM admin_ip_whitelist WHERE user_id = :user_id AND is_active = true"),
                    {"user_id": user_id}
                )
                return [
                    {
                        "id": row.id,
                        "ip_address": row.ip_address,
                        "description": row.description,
                        "created_at": row.created_at.isoformat() if row.created_at else None
                    }
                    for row in result.fetchall()
                ]
        except Exception as e:
            logger.error(f"Failed to get user IPs: {e}")
            return []
    
    async def enable_whitelist(self, user_id: int, initial_ip: Optional[str] = None) -> bool:
        if initial_ip:
            return await self.add_ip(user_id, initial_ip, "Початковий IP")
        return True
    
    async def disable_whitelist(self, user_id: int) -> bool:
        try:
            from database.db import async_session
            async with async_session() as session:
                await session.execute(
                    text("UPDATE admin_ip_whitelist SET is_active = false WHERE user_id = :user_id"),
                    {"user_id": user_id}
                )
                await session.commit()
            
            if user_id in self.whitelist:
                del self.whitelist[user_id]
            
            return True
        except Exception as e:
            logger.error(f"Failed to disable whitelist: {e}")
            return False

ip_whitelist_service = IPWhitelistService()
