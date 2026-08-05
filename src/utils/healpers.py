"""
Helpers
=======

Helper functions for the AI agent.
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, Optional

class Helpers:
    """Helper functions"""
    
    @staticmethod
    def format_date(date_str: str) -> str:
        """Format a date string"""
        if not date_str:
            return 'N/A'
        try:
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return date_str
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 200) -> str:
        """Truncate text to max length"""
        if not text:
            return ''
        if len(text) <= max_length:
            return text
        return text[:max_length] + '...'
    
    @staticmethod
    def extract_json(text: str) -> Optional[Dict]:
        """Extract JSON from text"""
        try:
            # Try to find JSON in text
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            pass
        return None
    
    @staticmethod
    def safe_json_loads(text: str) -> Any:
        """Safely load JSON"""
        try:
            return json.loads(text)
        except:
            return None
    
    @staticmethod
    def generate_id() -> str:
        """Generate a unique ID"""
        import uuid
        return str(uuid.uuid4())
