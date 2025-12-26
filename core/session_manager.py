import os
import io
import zipfile
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

from core.encryption import encryption_manager

logger = logging.getLogger(__name__)

try:
    from telethon import TelegramClient
    from telethon.errors import FloodWaitError, UserDeactivatedBanError, SessionPasswordNeededError
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    logger.warning("Telethon not available - bot operations will be limited")

class SessionManager:
    def __init__(self):
        self.sessions_dir = Path("sessions")
        self.sessions_dir.mkdir(exist_ok=True)
        self.imported_sessions = {}
        self.active_clients: Dict[str, Any] = {}
        self.session_stats: Dict[str, dict] = {}
        self.api_id = int(os.getenv("TELEGRAM_API_ID", "0"))
        self.api_hash = os.getenv("TELEGRAM_API_HASH", "")
    
    def import_from_zip(self, zip_data: bytes, project_id: int) -> Dict[str, Any]:
        result = {
            "project_id": project_id,
            "timestamp": datetime.now().isoformat(),
            "imported": [],
            "failed": [],
            "errors": []
        }
        
        try:
            with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zf:
                for filename in zf.namelist():
                    try:
                        if filename.endswith('.session') or filename.endswith('.json'):
                            content = zf.read(filename)
                            session_result = self._process_session_file(filename, content, project_id)
                            
                            if session_result['success']:
                                result['imported'].append(session_result)
                            else:
                                result['failed'].append(session_result)
                                
                    except Exception as e:
                        result['errors'].append({
                            "file": filename,
                            "error": str(e)
                        })
                        
        except zipfile.BadZipFile:
            result['errors'].append({"error": "Invalid ZIP file"})
        except Exception as e:
            result['errors'].append({"error": str(e)})
        
        logger.info(f"ZIP import completed: {len(result['imported'])} imported, {len(result['failed'])} failed")
        return result
    
    def _process_session_file(self, filename: str, content: bytes, project_id: int) -> Dict[str, Any]:
        result = {
            "filename": filename,
            "success": False,
            "session_type": "unknown"
        }
        
        try:
            if filename.endswith('.session'):
                result['session_type'] = 'telethon'
                session_data = content.decode('utf-8', errors='ignore')
                
                encrypted_session = encryption_manager.encrypt_session(session_data)
                session_hash = encryption_manager.hash_data(session_data)
                
                session_record = {
                    "project_id": project_id,
                    "filename": filename,
                    "session_hash": session_hash,
                    "encrypted_data": encrypted_session,
                    "session_type": "telethon",
                    "status": "pending_validation",
                    "imported_at": datetime.now().isoformat()
                }
                
                self.imported_sessions[session_hash] = session_record
                result['success'] = True
                result['session_hash'] = session_hash
                
            elif filename.endswith('.json'):
                import json
                try:
                    json_data = json.loads(content.decode('utf-8'))
                    
                    if 'session_string' in json_data:
                        result['session_type'] = 'pyrogram'
                        session_string = json_data['session_string']
                        
                        encrypted_session = encryption_manager.encrypt_session(session_string)
                        session_hash = encryption_manager.hash_data(session_string)
                        
                        session_record = {
                            "project_id": project_id,
                            "filename": filename,
                            "session_hash": session_hash,
                            "encrypted_data": encrypted_session,
                            "session_type": "pyrogram",
                            "phone": json_data.get('phone'),
                            "status": "pending_validation",
                            "imported_at": datetime.now().isoformat()
                        }
                        
                        self.imported_sessions[session_hash] = session_record
                        result['success'] = True
                        result['session_hash'] = session_hash
                    else:
                        result['error'] = "No session_string found in JSON"
                        
                except json.JSONDecodeError:
                    result['error'] = "Invalid JSON format"
            else:
                result['error'] = "Unsupported file format"
                
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error processing session file {filename}: {e}")
        
        return result
    
    def validate_session(self, session_hash: str) -> Dict[str, Any]:
        session = self.imported_sessions.get(session_hash)
        if not session:
            return {"valid": False, "error": "Session not found"}
        
        session['status'] = 'validated'
        return {
            "valid": True,
            "session_type": session['session_type'],
            "phone": session.get('phone')
        }
    
    def get_session(self, session_hash: str, decrypt: bool = False) -> Optional[Dict[str, Any]]:
        session = self.imported_sessions.get(session_hash)
        if not session:
            return None
        
        result = {
            "session_hash": session_hash,
            "session_type": session['session_type'],
            "status": session['status'],
            "project_id": session['project_id']
        }
        
        if decrypt:
            decrypted = encryption_manager.decrypt_session(session['encrypted_data'])
            if decrypted:
                result['session_data'] = decrypted
        
        return result
    
    def get_project_sessions(self, project_id: int) -> List[Dict[str, Any]]:
        return [
            {
                "session_hash": h,
                "session_type": s['session_type'],
                "status": s['status'],
                "phone": s.get('phone'),
                "imported_at": s['imported_at']
            }
            for h, s in self.imported_sessions.items()
            if s['project_id'] == project_id
        ]
    
    def deactivate_session(self, session_hash: str) -> bool:
        if session_hash in self.imported_sessions:
            self.imported_sessions[session_hash]['status'] = 'deactivated'
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        total = len(self.imported_sessions)
        by_type = {}
        by_status = {}
        
        for session in self.imported_sessions.values():
            t = session['session_type']
            s = session['status']
            by_type[t] = by_type.get(t, 0) + 1
            by_status[s] = by_status.get(s, 0) + 1
        
        return {
            "total_sessions": total,
            "by_type": by_type,
            "by_status": by_status,
            "active_clients": len(self.active_clients),
            "session_stats": self.session_stats
        }
    
    async def connect_client(self, session_hash: str) -> Optional[Any]:
        if not TELETHON_AVAILABLE:
            logger.error("Telethon not available")
            return None
        
        if session_hash in self.active_clients:
            return self.active_clients[session_hash]
        
        if not self.api_id or not self.api_hash:
            logger.error("TELEGRAM_API_ID or TELEGRAM_API_HASH not set")
            return None
        
        session = self.imported_sessions.get(session_hash)
        if not session:
            logger.error(f"Session {session_hash} not found")
            return None
        
        try:
            session_path = self.sessions_dir / f"{session_hash}.session"
            
            decrypted = encryption_manager.decrypt_session(session['encrypted_data'])
            if decrypted:
                with open(session_path, 'w') as f:
                    f.write(decrypted)
            
            client = TelegramClient(str(session_path), self.api_id, self.api_hash)
            await client.connect()
            
            if not await client.is_user_authorized():
                logger.warning(f"Session {session_hash} not authorized")
                return None
            
            self.active_clients[session_hash] = client
            self.session_stats[session_hash] = {
                "connected_at": datetime.now().isoformat(),
                "messages_sent": 0,
                "errors": 0
            }
            self.imported_sessions[session_hash]['status'] = 'active'
            
            logger.info(f"Client {session_hash} connected")
            return client
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return None
    
    async def disconnect_client(self, session_hash: str) -> bool:
        if session_hash in self.active_clients:
            try:
                await self.active_clients[session_hash].disconnect()
                del self.active_clients[session_hash]
                self.imported_sessions[session_hash]['status'] = 'validated'
                logger.info(f"Client {session_hash} disconnected")
                return True
            except Exception as e:
                logger.error(f"Disconnect error: {e}")
        return False
    
    async def send_message(self, session_hash: str, target: str, message: str) -> Dict[str, Any]:
        if not TELETHON_AVAILABLE:
            return {"status": "error", "message": "Telethon not available"}
        
        client = await self.connect_client(session_hash)
        if not client:
            return {"status": "error", "message": "Session not available"}
        
        try:
            entity = await client.get_entity(target)
            result = await client.send_message(entity, message)
            
            self.session_stats[session_hash]["messages_sent"] += 1
            logger.info(f"Message sent via {session_hash} to {target}")
            return {"status": "success", "message_id": result.id}
        except FloodWaitError as e:
            wait_time = e.seconds
            logger.warning(f"Flood wait: {wait_time}s")
            return {"status": "flood", "wait_seconds": wait_time}
        except UserDeactivatedBanError:
            self.session_stats[session_hash]["errors"] += 1
            self.imported_sessions[session_hash]['status'] = 'banned'
            return {"status": "banned", "message": "Account banned"}
        except Exception as e:
            self.session_stats[session_hash]["errors"] += 1
            logger.error(f"Send error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_user_info(self, session_hash: str, username: str) -> Dict[str, Any]:
        if not TELETHON_AVAILABLE:
            return {"status": "error", "message": "Telethon not available"}
        
        client = await self.connect_client(session_hash)
        if not client:
            return {"status": "error", "message": "Session not available"}
        
        try:
            user = await client.get_entity(username)
            return {
                "status": "success",
                "user_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_bot": user.bot,
                "is_verified": getattr(user, "verified", False)
            }
        except Exception as e:
            logger.error(f"Get user error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def disconnect_all(self):
        for session_hash in list(self.active_clients.keys()):
            await self.disconnect_client(session_hash)

session_manager = SessionManager()
