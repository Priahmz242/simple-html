"""
Encryption
==========

Handles encryption and decryption for the AI agent.
"""

import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Encryption:
    """Encryption system"""
    
    def __init__(self, key: str = None):
        if key:
            self.key = key
        else:
            self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
    
    @classmethod
    def from_password(cls, password: str, salt: bytes = None) -> 'Encryption':
        """Create encryption from password"""
        if salt is None:
            salt = b'\x00' * 16
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return cls(key=key.decode())
    
    def encrypt(self, data: str) -> str:
        """Encrypt data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, data: str) -> str:
        """Decrypt data"""
        return self.cipher.decrypt(data.encode()).decode()
    
    def encrypt_json(self, data: dict) -> str:
        """Encrypt JSON data"""
        import json
        return self.encrypt(json.dumps(data))
    
    def decrypt_json(self, data: str) -> dict:
        """Decrypt JSON data"""
        import json
        return json.loads(self.decrypt(data))
