"""
Authentication
==============

Handles authentication and authorization for the AI agent.
"""

import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict

class Auth:
    """Authentication system"""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_hex(32)
    
    def generate_api_key(self) -> str:
        """Generate a new API key"""
        return secrets.token_hex(32)
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256()
        hash_obj.update((salt + password).encode())
        return f"{salt}:{hash_obj.hexdigest()}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        try:
            salt, hash_value = hashed.split(':')
            hash_obj = hashlib.sha256()
            hash_obj.update((salt + password).encode())
            return hash_obj.hexdigest() == hash_value
        except:
            return False
    
    def generate_token(self, user_id: int, expires_in: int = 86400) -> str:
        """Generate a JWT-like token"""
        payload = {
            'user_id': user_id,
            'expires': (datetime.now() + timedelta(seconds=expires_in)).isoformat()
        }
        # Simple token generation (in production, use proper JWT)
        import json
        token = json.dumps(payload)
        signature = hmac.new(
            self.secret_key.encode(),
            token.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{token}.{signature}"
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify a token"""
        try:
            parts = token.split('.')
            if len(parts) != 2:
                return None
            
            payload_str, signature = parts
            expected = hmac.new(
                self.secret_key.encode(),
                payload_str.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected):
                return None
            
            import json
            payload = json.loads(payload_str)
            expires = datetime.fromisoformat(payload['expires'])
            
            if datetime.now() > expires:
                return None
            
            return payload
        except:
            return None
