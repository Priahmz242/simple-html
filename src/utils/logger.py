"""
Logger
======

Logging system for the AI agent.
"""

import logging
from datetime import datetime

class Logger:
    """Logging system"""
    
    def __init__(self, name: str, level: str = 'INFO'):
        self.name = name
        self.level = level
        self.logs = []
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(name)
    
    def log(self, level: str, message: str) -> None:
        """Log a message"""
        timestamp = datetime.now().isoformat()
        self.logs.append({
            'level': level,
            'message': message,
            'timestamp': timestamp
        })
        getattr(self.logger, level.lower())(message)
    
    def info(self, message: str) -> None:
        self.log('INFO', message)
    
    def warning(self, message: str) -> None:
        self.log('WARNING', message)
    
    def error(self, message: str) -> None:
        self.log('ERROR', message)
    
    def debug(self, message: str) -> None:
        self.log('DEBUG', message)
    
    def log_error(self, error: Exception) -> None:
        """Log an exception"""
        self.error(str(error))
    
    def get_logs(self) -> list:
        """Get all logs"""
        return self.logs
