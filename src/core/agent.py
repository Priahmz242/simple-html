"""
Agent Module
============

The main AI agent orchestrating all components.
"""

from typing import Dict, Optional
from datetime import datetime

from .memory import Memory
from .brain import Brain
from .database import Database
from .config import Config

class Agent:
    """Main AI Agent"""
    
    def __init__(self, user_id: int = None):
        self.user_id = user_id
        self.config = Config()
        self.memory = Memory()
        self.brain = Brain(self.memory)
        self.database = Database()
        self.start_time = datetime.now()
    
    def process_task(self, task_description: str, context: Optional[Dict] = None) -> Dict:
        """Process a task"""
        result = self.brain.process_task(task_description, context)
        
        if self.user_id:
            task_id = self.database.create_task(
                self.user_id,
                task_description,
                json.dumps(context or {})
            )
            self.database.update_task_status(
                task_id,
                'completed' if result.get('success') else 'failed',
                json.dumps(result)
            )
        
        return result
    
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            'name': self.config.get('agent.name', 'Boijelux AI'),
            'version': self.config.get('agent.version', '7.1.0'),
            'state': 'online',
            'uptime': (datetime.now() - self.start_time).total_seconds(),
            'memory': self.memory.get_summary(),
            'brain': self.brain.get_status()
        }
