"""
Configuration Manager
=====================

Manages all configuration settings for the Boijelux AI Agent.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration manager for the AI agent"""
    
    def __init__(self, config_path: str = 'config/settings.yaml'):
        self.config_path = config_path
        self.data = self._load()
        self._load_env()
    
    def _load(self) -> Dict:
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                        return yaml.safe_load(f) or {}
                    elif self.config_path.endswith('.json'):
                        return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
        return {}
    
    def _load_env(self) -> None:
        """Load environment variables"""
        self.env = {
            "API_KEY": os.getenv("API_KEY"),
            "JWT_SECRET": os.getenv("JWT_SECRET"),
            "DATABASE_URL": os.getenv("DATABASE_URL"),
            "ADMIN_EMAIL": os.getenv("ADMIN_EMAIL"),
            "DOMAIN": os.getenv("DOMAIN", "ai.taagc.site"),
            "DEBUG": os.getenv("DEBUG", "True").lower() == "true",
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key (dot notation supported)"""
        # Check env first
        if key in self.env and self.env[key] is not None:
            return self.env[key]
        
        # Check config file
        keys = key.split('.')
        value = self.data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def get_env(self, key: str, default: Any = None) -> Any:
        """Get an environment variable"""
        return self.env.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value"""
        keys = key.split('.')
        target = self.data
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value
        self._save()
    
    def _save(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    yaml.dump(self.data, f, default_flow_style=False)
                elif self.config_path.endswith('.json'):
                    json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_all(self) -> Dict:
        """Get all configuration data"""
        return {**self.data, **self.env}
    
    def to_dict(self) -> Dict:
        """Convert config to dictionary"""
        return self.get_all()

# Singleton instance
config = Config()
