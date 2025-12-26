import os
import io
import zipfile
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

from core.encryption import encryption_manager

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self):
        self.sessions_dir = Path("sessions")
        self.sessions_dir.mkdir(exist_ok=True)
        self.imported_sessions = {}
    
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
            "by_status": by_status
        }

session_manager = SessionManager()
