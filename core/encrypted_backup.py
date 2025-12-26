import asyncio
import logging
import json
import hashlib
import base64
from datetime import datetime
from typing import Optional, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from sqlalchemy import text
import os

logger = logging.getLogger(__name__)

class EncryptedBackupService:
    def __init__(self):
        self._key = self._derive_key()
        self._fernet = Fernet(self._key) if self._key else None
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    def _derive_key(self) -> Optional[bytes]:
        try:
            secret = os.environ.get("SESSION_SECRET")
            if not secret:
                import secrets as sec_module
                secret = sec_module.token_hex(32)
                logger.warning("SESSION_SECRET not set - using generated key (backups won't persist across restarts)")
            
            salt = b"shadow_backup_salt_v2"
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(secret.encode()))
            return key
        except Exception as e:
            logger.error(f"Failed to derive encryption key: {e}")
            return None
    
    async def start(self):
        self._running = True
        self._task = asyncio.create_task(self._backup_loop())
        logger.info("EncryptedBackupService started")
    
    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
    
    async def _backup_loop(self):
        while self._running:
            try:
                await self.backup_keys()
                await self.backup_sessions()
                await asyncio.sleep(86400)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Backup loop error: {e}")
                await asyncio.sleep(3600)
    
    def _encrypt(self, data: str) -> str:
        if not self._fernet:
            return data
        return self._fernet.encrypt(data.encode()).decode()
    
    def _decrypt(self, encrypted_data: str) -> str:
        if not self._fernet:
            return encrypted_data
        return self._fernet.decrypt(encrypted_data.encode()).decode()
    
    def _calculate_checksum(self, data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()
    
    async def backup_keys(self) -> Optional[int]:
        try:
            from database.db import async_session
            async with async_session() as session:
                result = await session.execute(
                    text("SELECT id, code, tariff, user_id, is_used, expires_at, created_at FROM keys")
                )
                rows = result.fetchall()
                
                keys_data = []
                for row in rows:
                    keys_data.append({
                        "id": row.id,
                        "code": row.code,
                        "tariff": row.tariff,
                        "user_id": row.user_id,
                        "is_used": row.is_used,
                        "expires_at": row.expires_at.isoformat() if row.expires_at else None,
                        "created_at": row.created_at.isoformat() if row.created_at else None
                    })
                
                json_data = json.dumps(keys_data, ensure_ascii=False)
                encrypted_data = self._encrypt(json_data)
                checksum = self._calculate_checksum(json_data)
                
                result = await session.execute(
                    text("""
                        INSERT INTO encrypted_backups (backup_type, encrypted_data, checksum, created_at)
                        VALUES ('keys', :data, :checksum, NOW())
                        RETURNING id
                    """),
                    {"data": encrypted_data, "checksum": checksum}
                )
                backup_id = result.fetchone()[0]
                await session.commit()
                
                logger.info(f"Keys backup created: {backup_id} ({len(keys_data)} keys)")
                return backup_id
                
        except Exception as e:
            logger.error(f"Failed to backup keys: {e}")
            return None
    
    async def backup_sessions(self) -> Optional[int]:
        try:
            sessions_dir = "sessions"
            if not os.path.exists(sessions_dir):
                return None
            
            sessions_data = {}
            for filename in os.listdir(sessions_dir):
                if filename.endswith(".session"):
                    filepath = os.path.join(sessions_dir, filename)
                    with open(filepath, "rb") as f:
                        sessions_data[filename] = base64.b64encode(f.read()).decode()
            
            if not sessions_data:
                return None
            
            json_data = json.dumps(sessions_data)
            encrypted_data = self._encrypt(json_data)
            checksum = self._calculate_checksum(json_data)
            
            from database.db import async_session
            async with async_session() as session:
                result = await session.execute(
                    text("""
                        INSERT INTO encrypted_backups (backup_type, encrypted_data, checksum, created_at)
                        VALUES ('sessions', :data, :checksum, NOW())
                        RETURNING id
                    """),
                    {"data": encrypted_data, "checksum": checksum}
                )
                backup_id = result.fetchone()[0]
                await session.commit()
                
                logger.info(f"Sessions backup created: {backup_id} ({len(sessions_data)} sessions)")
                return backup_id
                
        except Exception as e:
            logger.error(f"Failed to backup sessions: {e}")
            return None
    
    async def restore_keys(self, backup_id: int) -> bool:
        try:
            from database.db import async_session
            async with async_session() as session:
                result = await session.execute(
                    text("SELECT encrypted_data, checksum FROM encrypted_backups WHERE id = :id AND backup_type = 'keys'"),
                    {"id": backup_id}
                )
                row = result.fetchone()
                if not row:
                    return False
                
                decrypted_data = self._decrypt(row.encrypted_data)
                
                if self._calculate_checksum(decrypted_data) != row.checksum:
                    logger.error("Checksum mismatch - backup may be corrupted")
                    return False
                
                keys_data = json.loads(decrypted_data)
                logger.info(f"Restored {len(keys_data)} keys from backup {backup_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to restore keys: {e}")
            return False
    
    async def get_backups(self, backup_type: Optional[str] = None, limit: int = 10) -> List[dict]:
        try:
            from database.db import async_session
            async with async_session() as session:
                query = "SELECT id, backup_type, checksum, created_at FROM encrypted_backups"
                params = {"limit": limit}
                
                if backup_type:
                    query += " WHERE backup_type = :backup_type"
                    params["backup_type"] = backup_type
                
                query += " ORDER BY created_at DESC LIMIT :limit"
                
                result = await session.execute(text(query), params)
                return [
                    {
                        "id": row.id,
                        "type": row.backup_type,
                        "checksum": row.checksum[:16] + "..." if row.checksum else None,
                        "created_at": row.created_at.isoformat() if row.created_at else None
                    }
                    for row in result.fetchall()
                ]
        except Exception as e:
            logger.error(f"Failed to get backups: {e}")
            return []

encrypted_backup_service = EncryptedBackupService()
