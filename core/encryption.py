import os
import base64
import hashlib
import hmac
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class EncryptionManager:
    def __init__(self):
        self._key = None
        self._init_encryption()
    
    def _init_encryption(self):
        secret = os.getenv("ENCRYPTION_SECRET", "shadow_system_default_key_2025")
        salt = os.getenv("ENCRYPTION_SALT", "shadow_salt_v2")
        
        key_material = f"{secret}{salt}".encode()
        self._key = hashlib.pbkdf2_hmac('sha256', secret.encode(), salt.encode(), 100000)
        logger.info("EncryptionManager initialized (basic mode)")
    
    def _xor_encrypt(self, data: bytes, key: bytes) -> bytes:
        key_len = len(key)
        return bytes([data[i] ^ key[i % key_len] for i in range(len(data))])
    
    def encrypt(self, data: str) -> str:
        if not data:
            return ""
        try:
            data_bytes = data.encode('utf-8')
            encrypted = self._xor_encrypt(data_bytes, self._key)
            
            signature = hmac.new(self._key, encrypted, hashlib.sha256).digest()[:8]
            
            result = signature + encrypted
            return base64.urlsafe_b64encode(result).decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return ""
    
    def decrypt(self, encrypted_data: str) -> Optional[str]:
        if not encrypted_data:
            return None
        try:
            raw = base64.urlsafe_b64decode(encrypted_data.encode())
            
            stored_signature = raw[:8]
            encrypted = raw[8:]
            
            expected_signature = hmac.new(self._key, encrypted, hashlib.sha256).digest()[:8]
            if not hmac.compare_digest(stored_signature, expected_signature):
                logger.warning("Signature verification failed")
                return None
            
            decrypted = self._xor_encrypt(encrypted, self._key)
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return None
    
    def encrypt_session(self, session_string: str) -> str:
        return self.encrypt(session_string)
    
    def decrypt_session(self, encrypted_session: str) -> Optional[str]:
        return self.decrypt(encrypted_session)
    
    def hash_data(self, data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_hash(self, data: str, hash_value: str) -> bool:
        return hmac.compare_digest(self.hash_data(data), hash_value)
    
    def generate_secure_key(self, prefix: str = "SHADOW") -> str:
        import secrets
        random_part = secrets.token_hex(8).upper()
        return f"{prefix}-{random_part[:4]}-{random_part[4:]}"

encryption_manager = EncryptionManager()
