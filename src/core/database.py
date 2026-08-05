"""
Database Manager
================

Manages database connections and operations for the Boijelux AI Agent.
"""

import sqlite3
import json
from pathlib import Path
from contextlib import contextmanager
from typing import Dict, List, Any, Optional
from datetime import datetime

class Database:
    """Database manager with SQLite support"""
    
    def __init__(self, db_path: str = "boijelux.db"):
        self.db_path = db_path
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        """Get a database connection with context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_db(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            # Users table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    api_key TEXT UNIQUE NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_active DATETIME,
                    is_admin BOOLEAN DEFAULT 0
                )
            """)
            
            # Tasks table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    description TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    result TEXT,
                    context TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Knowledge table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    text TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    source TEXT,
                    learned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Bots table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT NOT NULL,
                    requirements TEXT NOT NULL,
                    location TEXT DEFAULT 'local',
                    status TEXT DEFAULT 'active',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Analytics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    endpoint TEXT NOT NULL,
                    method TEXT NOT NULL,
                    user_id INTEGER,
                    status_code INTEGER,
                    duration_ms REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Conversations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    session_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    response TEXT,
                    internet_used BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Webhooks table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS webhooks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    event TEXT NOT NULL,
                    callback_url TEXT NOT NULL,
                    active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            conn.commit()
    
    def execute(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute a query and return results"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Execute a query and return one result"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an insert query and return the last row id"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    
    def get_user_by_api_key(self, api_key: str) -> Optional[Dict]:
        """Get user by API key"""
        return self.execute_one(
            "SELECT id, username, email, is_admin FROM users WHERE api_key = ?",
            (api_key,)
        )
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        return self.execute_one(
            "SELECT id, username, email, password_hash, api_key, is_admin FROM users WHERE username = ?",
            (username,)
        )
    
    def create_user(self, username: str, email: str, password_hash: str, api_key: str) -> int:
        """Create a new user"""
        return self.execute_insert(
            "INSERT INTO users (username, email, password_hash, api_key) VALUES (?, ?, ?, ?)",
            (username, email, password_hash, api_key)
        )
    
    def update_user_active(self, user_id: int):
        """Update user's last active timestamp"""
        self.execute(
            "UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE id = ?",
            (user_id,)
        )
    
    def create_task(self, user_id: int, description: str, context: str = None) -> int:
        """Create a new task"""
        return self.execute_insert(
            "INSERT INTO tasks (user_id, description, context) VALUES (?, ?, ?)",
            (user_id, description, context)
        )
    
    def update_task_status(self, task_id: int, status: str, result: str = None):
        """Update task status"""
        self.execute(
            "UPDATE tasks SET status = ?, result = ?, completed_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, result, task_id)
        )
    
    def get_tasks(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get tasks for a user"""
        return self.execute(
            "SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        )
    
    def create_knowledge(self, user_id: int, text: str, category: str = "general", source: str = None) -> int:
        """Create a knowledge entry"""
        return self.execute_insert(
            "INSERT INTO knowledge (user_id, text, category, source) VALUES (?, ?, ?, ?)",
            (user_id, text, category, source)
        )
    
    def get_knowledge(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get knowledge for a user"""
        return self.execute(
            "SELECT * FROM knowledge WHERE user_id = ? ORDER BY learned_at DESC LIMIT ?",
            (user_id, limit)
        )
    
    def create_bot(self, user_id: int, name: str, requirements: str, location: str = "local") -> int:
        """Create a new bot"""
        return self.execute_insert(
            "INSERT INTO bots (user_id, name, requirements, location) VALUES (?, ?, ?, ?)",
            (user_id, name, requirements, location)
        )
    
    def get_bots(self, user_id: int) -> List[Dict]:
        """Get bots for a user"""
        return self.execute(
            "SELECT * FROM bots WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
    
    def log_analytics(self, endpoint: str, method: str, user_id: int, status_code: int, duration_ms: float):
        """Log analytics data"""
        self.execute_insert(
            "INSERT INTO analytics (endpoint, method, user_id, status_code, duration_ms) VALUES (?, ?, ?, ?, ?)",
            (endpoint, method, user_id, status_code, duration_ms)
        )
    
    def get_analytics(self, user_id: int) -> Dict:
        """Get analytics for a user"""
        total = self.execute_one(
            "SELECT COUNT(*) as total FROM analytics WHERE user_id = ?",
            (user_id,)
        )
        
        endpoints = self.execute(
            "SELECT endpoint, COUNT(*) as count FROM analytics WHERE user_id = ? GROUP BY endpoint",
            (user_id,)
        )
        
        recent = self.execute(
            "SELECT * FROM analytics WHERE user_id = ? ORDER BY created_at DESC LIMIT 20",
            (user_id,)
        )
        
        return {
            "total_requests": total.get("total", 0) if total else 0,
            "endpoints": endpoints,
            "recent": recent
        }

# Singleton instance
database = Database()
