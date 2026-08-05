"""
Task Manager
============

Manages tasks for the AI agent including creation, tracking, and completion.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

class TaskManager:
    """Task management system"""
    
    def __init__(self, agent):
        self.agent = agent
        self.tasks = []
        self.counter = 0
    
    def add_task(self, description: str, priority: int = 3, 
                 context: Optional[Dict] = None, 
                 deadline: Optional[str] = None) -> str:
        """Add a new task"""
        self.counter += 1
        task = {
            'id': str(self.counter),
            'description': description,
            'priority': priority,
            'context': context or {},
            'deadline': deadline,
            'status': 'pending',
            'created': datetime.now().isoformat(),
            'updated': datetime.now().isoformat()
        }
        self.tasks.append(task)
        return task['id']
    
    def get_pending_tasks(self) -> List[Dict]:
        """Get all pending tasks"""
        return [t for t in self.tasks if t.get('status') == 'pending']
    
    def get_task_by_id(self, task_id: str) -> Optional[Dict]:
        """Get a task by ID"""
        for task in self.tasks:
            if task['id'] == task_id:
                return task
        return None
    
    def mark_completed(self, task_id: str, result: Any) -> bool:
        """Mark a task as completed"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['status'] = 'completed'
                task['completed'] = datetime.now().isoformat()
                task['result'] = result
                task['updated'] = datetime.now().isoformat()
                return True
        return False
    
    def get_all_tasks(self) -> List[Dict]:
        """Get all tasks"""
        return self.tasks
    
    def get_summary(self) -> Dict:
        """Get task summary"""
        pending = len([t for t in self.tasks if t.get('status') == 'pending'])
        completed = len([t for t in self.tasks if t.get('status') == 'completed'])
        failed = len([t for t in self.tasks if t.get('status') == 'failed'])
        
        return {
            'total': len(self.tasks),
            'pending': pending,
            'completed': completed,
            'failed': failed
              }
