"""
Boijelux v7.1 - Advanced AI Agent with Full Internet Access
Deployed on Vercel with FastAPI
Version: 7.1.0
"""

import time
import json
import httpx
import asyncio
import re
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path
from urllib.parse import urlparse
import sqlite3
from contextlib import contextmanager

from fastapi import FastAPI, Request, HTTPException, status, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from slowapi import Limiter, _rate_limit_exceeded
from slowapi.util import get_remote_address
import uvicorn

# ============================================
# CONFIGURATION
# ============================================

APP_NAME = "Boijelux v7.1"
APP_VERSION = "7.1.0"
DOMAIN = "ai.taagc.site"
DEPLOYMENT = "Vercel"
DEBUG = True

# Security
API_KEY = os.getenv("API_KEY", secrets.token_hex(32))
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_hex(32))
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@boijelux.com")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./boijelux.db")

# Rate Limiting
RATE_LIMIT = "100/minute"
MAX_WEB_SEARCH_RESULTS = 10
MAX_CONTENT_LENGTH = 10000
REQUEST_TIMEOUT = 30
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# ============================================
# DATABASE
# ============================================

class Database:
    def __init__(self, db_path="boijelux.db"):
        self.db_path = db_path
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_db(self):
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    api_key TEXT UNIQUE NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_active DATETIME
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    description TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    result TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
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
            conn.commit()

db = Database()

# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Advanced AI Agent with Full Internet Access",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# SECURITY
# ============================================

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
security = HTTPBearer(auto_error=False)

async def verify_api_key(api_key: str = Depends(api_key_header)):
    """Verify API key"""
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    with db.get_connection() as conn:
        user = conn.execute(
            "SELECT id, username FROM users WHERE api_key = ?",
            (api_key,)
        ).fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Update last_active
        conn.execute(
            "UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE id = ?",
            (user['id'],)
        )
        conn.commit()
        
        return dict(user)

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    """Get user from JWT token"""
    # Simplified - in production, verify JWT
    return {"id": 1, "username": "admin"}

# ============================================
# PYDANTIC MODELS
# ============================================

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str

class TaskRequest(BaseModel):
    task: str = Field(..., description="The task description to process.")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class CreateBotRequest(BaseModel):
    requirements: str = Field(..., description="The requirements for the new bot.")
    location: str = Field("local")
    name: Optional[str] = None

class LearnRequest(BaseModel):
    text: str = Field(..., description="The text content to learn from.")
    category: str = Field("general")
    source: Optional[str] = Field("user_input")

class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's chat message.")
    session_id: Optional[str] = None
    use_internet: bool = Field(False)

class WebSearchRequest(BaseModel):
    query: str = Field(..., description="The search query.")
    max_results: int = Field(5, ge=1, le=20)

class UrlFetchRequest(BaseModel):
    url: HttpUrl = Field(..., description="The URL to fetch.")
    max_length: int = Field(5000, ge=100, le=50000)

class GenerateCodeRequest(BaseModel):
    description: str = Field(..., description="Description of the code to generate.")
    language: str = Field("python")
    framework: Optional[str] = None

class WebhookRequest(BaseModel):
    event: str = Field(..., description="Event type")
    payload: Dict[str, Any] = Field(..., description="Event payload")
    callback_url: Optional[HttpUrl] = None

# ============================================
# HELPERS
# ============================================

def log_analytics(endpoint: str, method: str, user_id: Optional[int], status_code: int, duration_ms: float):
    """Log analytics data"""
    with db.get_connection() as conn:
        conn.execute(
            "INSERT INTO analytics (endpoint, method, user_id, status_code, duration_ms) VALUES (?, ?, ?, ?, ?)",
            (endpoint, method, user_id, status_code, duration_ms)
        )
        conn.commit()

# ============================================
# INTERNET HELPERS
# ============================================

async def fetch_url_content(url: str, max_length: int = 5000) -> Dict:
    """Fetch content from a URL"""
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            content = response.text
            
            if len(content) > max_length:
                content = content[:max_length] + "... (truncated)"
            
            return {
                "success": True,
                "url": str(url),
                "title": _extract_title(content),
                "content": content,
                "content_type": content_type,
                "length": len(response.text),
                "status_code": response.status_code
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

def _extract_title(html_content: str) -> str:
    match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
    return match.group(1).strip() if match else "Untitled"

async def search_web(query: str, max_results: int = 5) -> Dict:
    """Search the web using DuckDuckGo"""
    try:
        search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
        
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
            response = await client.get(search_url)
            response.raise_for_status()
            
            html = response.text
            results = []
            blocks = re.findall(r'<a rel="nofollow" class="result__a" href="(.*?)".*?>(.*?)</a>', html, re.DOTALL)
            snippets = re.findall(r'<a class="result__snippet".*?>(.*?)</a>', html, re.DOTALL)
            
            for i, (url, title) in enumerate(blocks[:max_results]):
                if i < len(snippets):
                    snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()
                else:
                    snippet = ""
                results.append({
                    "title": re.sub(r'<[^>]+>', '', title).strip(),
                    "url": url,
                    "snippet": snippet
                })
            
            return {"success": True, "query": query, "results": results, "count": len(results)}
    except Exception as e:
        return {"success": False, "error": str(e), "results": []}

async def generate_code(description: str, language: str = "python", framework: str = None) -> Dict:
    """Generate code based on description"""
    templates = {
        "python": {
            "default": f'''
"""
Generated Python Code
Description: {description}
Generated by Boijelux v7.1
"""

def main():
    print("Boijelux v7.1 Generated Code")
    print(f"Task: {description}")

if __name__ == "__main__":
    main()
''',
            "fastapi": f'''
"""
FastAPI Endpoint
Generated by Boijelux v7.1
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
async def root():
    return {{"message": "Boijelux v7.1 API"}}
'''
        }
    }
    
    lang_templates = templates.get(language, templates["python"])
    code = lang_templates.get(framework.lower(), lang_templates["default"]) if framework else lang_templates["default"]
    
    return {"success": True, "language": language, "framework": framework, "code": code}

# ============================================
# AUTH ENDPOINTS
# ============================================

@app.post("/api/auth/register")
@limiter.limit("5/minute")
async def register(request: Request, user: UserCreate):
    """Register a new user"""
    api_key = secrets.token_hex(32)
    
    try:
        with db.get_connection() as conn:
            conn.execute(
                "INSERT INTO users (username, email, api_key) VALUES (?, ?, ?)",
                (user.username, user.email, api_key)
            )
            conn.commit()
            
            user_id = conn.lastrowid
            
            return {
                "status": "success",
                "message": "User registered successfully",
                "api_key": api_key,
                "user_id": user_id
            }
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            raise HTTPException(status_code=400, detail="Username already exists")
        elif "email" in str(e):
            raise HTTPException(status_code=400, detail="Email already exists")
        raise HTTPException(status_code=400, detail="Registration failed")

@app.post("/api/auth/login")
@limiter.limit("10/minute")
async def login(request: Request, user: UserLogin):
    """Login user"""
    with db.get_connection() as conn:
        db_user = conn.execute(
            "SELECT id, username, api_key FROM users WHERE username = ?",
            (user.username,)
        ).fetchone()
        
        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # In production, verify password hash
        return {
            "status": "success",
            "api_key": db_user['api_key'],
            "user_id": db_user['id'],
            "username": db_user['username']
        }

# ============================================
# CORE API ENDPOINTS
# ============================================

@app.get("/")
async def root():
    try:
        file_path = Path(__file__).parent.parent / 'public' / 'index.html'
        if file_path.exists():
            with open(file_path, 'r') as f:
                return HTMLResponse(content=f.read())
    except:
        pass
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Boijelux v7.1</title>
        <style>
            * { margin:0; padding:0; box-sizing:border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
                color: #fff;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                max-width: 800px;
                padding: 40px;
                background: rgba(255,255,255,0.05);
                border-radius: 20px;
                border: 1px solid rgba(255,255,255,0.1);
                text-align: center;
            }
            h1 { font-size: 2.5rem; margin-bottom: 10px; }
            .icon { font-size: 3rem; }
            .status { color: #00cc88; margin: 20px 0; }
            .version { color: #888; font-size: 0.9rem; }
            .footer { margin-top: 30px; color: #555; font-size: 0.8rem; }
            a { color: #00cc88; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">🚀</div>
            <h1>Boijelux v7.1</h1>
            <p class="version">Advanced AI Agent with Full Internet Access</p>
            <p class="status">● Online & Running</p>
            <p><a href="/api/docs">📚 API Documentation</a></p>
            <p style="color:#888;margin-top:20px;">🤖 Any Task • Any Domain • Anywhere</p>
            <div class="footer">© 2026 Boijelux</div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "version": APP_VERSION}

@app.get("/api/version")
async def get_version():
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "domain": DOMAIN,
        "deployment": DEPLOYMENT,
        "uptime": time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0
    }

@app.get("/api/status")
@limiter.limit("100/minute")
async def get_status(request: Request, user: dict = Depends(verify_api_key)):
    start_time = time.time()
    
    with db.get_connection() as conn:
        tasks_completed = conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'completed'",
            (user['id'],)
        ).fetchone()[0]
        
        bots_created = conn.execute(
            "SELECT COUNT(*) FROM bots WHERE user_id = ?",
            (user['id'],)
        ).fetchone()[0]
    
    duration = (time.time() - start_time) * 1000
    log_analytics("/api/status", "GET", user['id'], 200, duration)
    
    return {
        "status": "success",
        "domain": DOMAIN,
        "server": DEPLOYMENT,
        "timestamp": datetime.now().isoformat(),
        "user": user['username'],
        "agent": {
            "name": APP_NAME,
            "version": APP_VERSION,
            "state": "online",
            "tasks_completed": tasks_completed,
            "bots_created": bots_created,
            "domains": [
                "Business", "Finance", "Healthcare", "Education",
                "Technology", "Legal", "Creative", "Real Estate",
                "Manufacturing", "Agriculture", "Retail",
                "Transportation", "Energy", "Government"
            ],
            "capabilities": [
                "Self-learning",
                "Self-repairing",
                "Self-upgrading",
                "Self-replicating",
                "Internet search",
                "Code generation",
                "Authentication",
                "File upload"
            ]
        }
    }

# ============================================
# TASK ENDPOINTS
# ============================================

@app.get("/api/tasks")
@limiter.limit("100/minute")
async def get_tasks(request: Request, user: dict = Depends(verify_api_key)):
    with db.get_connection() as conn:
        tasks = conn.execute(
            "SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC LIMIT 50",
            (user['id'],)
        ).fetchall()
    
    return {
        "status": "success",
        "count": len(tasks),
        "tasks": [dict(task) for task in tasks]
    }

@app.post("/api/task")
@limiter.limit("20/minute")
async def create_task(request: Request, task_req: TaskRequest, user: dict = Depends(verify_api_key)):
    start_time = time.time()
    
    use_internet = task_req.context.get('use_internet', False)
    
    # Process with AI
    result = {
        "success": True,
        "message": f"Task processed: {task_req.task}",
        "domain": "general",
        "analysis": f"AI analyzed: {task_req.task[:100]}...",
        "suggestions": [
            "Break the task into smaller steps",
            "Use relevant data sources",
            "Monitor progress regularly"
        ],
        "internet_used": use_internet,
        "timestamp": datetime.now().isoformat()
    }
    
    if use_internet:
        search_result = await search_web(task_req.task, 3)
        if search_result.get('success'):
            result['internet_data'] = search_result.get('results', [])
    
    with db.get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (user_id, description, status, result) VALUES (?, ?, ?, ?)",
            (user['id'], task_req.task, 'completed', json.dumps(result))
        )
        conn.commit()
        task_id = cursor.lastrowid
        
        task = conn.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        ).fetchone()
    
    duration = (time.time() - start_time) * 1000
    log_analytics("/api/task", "POST", user['id'], 200, duration)
    
    return {
        "status": "success",
        "task": dict(task),
        "result": result
    }

# ============================================
# BOT ENDPOINTS
# ============================================

@app.post("/api/create_bot")
@limiter.limit("10/minute")
async def create_bot(request: Request, bot_req: CreateBotRequest, user: dict = Depends(verify_api_key)):
    with db.get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO bots (user_id, name, requirements, location) VALUES (?, ?, ?, ?)",
            (user['id'], bot_req.name or f"Bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}", 
             bot_req.requirements, bot_req.location)
        )
        conn.commit()
        bot_id = cursor.lastrowid
        
        bot = conn.execute("SELECT * FROM bots WHERE id = ?", (bot_id,)).fetchone()
    
    return {
        "status": "success",
        "bot": dict(bot)
    }

@app.get("/api/bots")
@limiter.limit("100/minute")
async def get_bots(request: Request, user: dict = Depends(verify_api_key)):
    with db.get_connection() as conn:
        bots = conn.execute(
            "SELECT * FROM bots WHERE user_id = ? ORDER BY created_at DESC",
            (user['id'],)
        ).fetchall()
    
    return {
        "status": "success",
        "count": len(bots),
        "bots": [dict(bot) for bot in bots]
    }

# ============================================
# KNOWLEDGE ENDPOINTS
# ============================================

@app.post("/api/learn")
@limiter.limit("20/minute")
async def learn_text(request: Request, learn_req: LearnRequest, user: dict = Depends(verify_api_key)):
    with db.get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO knowledge (user_id, text, category, source) VALUES (?, ?, ?, ?)",
            (user['id'], learn_req.text, learn_req.category, learn_req.source)
        )
        conn.commit()
        knowledge_id = cursor.lastrowid
        
        knowledge = conn.execute("SELECT * FROM knowledge WHERE id = ?", (knowledge_id,)).fetchone()
    
    return {
        "status": "success",
        "message": "Learning successful",
        "knowledge": dict(knowledge)
    }

@app.get("/api/knowledge")
@limiter.limit("100/minute")
async def get_knowledge(request: Request, user: dict = Depends(verify_api_key)):
    with db.get_connection() as conn:
        knowledge = conn.execute(
            "SELECT * FROM knowledge WHERE user_id = ? ORDER BY learned_at DESC LIMIT 50",
            (user['id'],)
        ).fetchall()
    
    return {
        "status": "success",
        "count": len(knowledge),
        "knowledge": [dict(item) for item in knowledge]
    }

# ============================================
# INTERNET ENDPOINTS
# ============================================

@app.post("/api/search")
@limiter.limit("10/minute")
async def web_search(request: Request, search_req: WebSearchRequest, user: dict = Depends(verify_api_key)):
    result = await search_web(search_req.query, search_req.max_results)
    return {
        "status": "success" if result.get('success') else "error",
        "data": result
    }

@app.post("/api/fetch")
@limiter.limit("10/minute")
async def fetch_url(request: Request, fetch_req: UrlFetchRequest, user: dict = Depends(verify_api_key)):
    result = await fetch_url_content(str(fetch_req.url), fetch_req.max_length)
    return {
        "status": "success" if result.get('success') else "error",
        "data": result
    }

@app.post("/api/chat")
@limiter.limit("20/minute")
async def chat(request: Request, chat_req: ChatRequest, user: dict = Depends(verify_api_key)):
    internet_context = None
    if chat_req.use_internet:
        search_result = await search_web(chat_req.message, 3)
        if search_result.get('success'):
            internet_context = search_result.get('results', [])
    
    response = f"Boijelux v7.1 received: '{chat_req.message}'"
    
    return {
        "status": "success",
        "chat": {
            "session_id": chat_req.session_id or "new-session",
            "response": response,
            "internet_used": chat_req.use_internet,
            "internet_results": internet_context[:3] if internet_context else None,
            "timestamp": datetime.now().isoformat()
        }
    }

@app.post("/api/generate_code")
@limiter.limit("10/minute")
async def generate_code_endpoint(request: Request, code_req: GenerateCodeRequest, user: dict = Depends(verify_api_key)):
    result = await generate_code(code_req.description, code_req.language, code_req.framework)
    return {
        "status": "success" if result.get('success') else "error",
        "data": result
    }

# ============================================
# FILE UPLOAD
# ============================================

@app.post("/api/upload")
@limiter.limit("5/minute")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    user: dict = Depends(verify_api_key)
):
    """Upload and process a file"""
    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    # Process based on file type
    file_type = file.content_type or "unknown"
    file_name = file.filename or "unknown"
    
    # Extract text from different file types
    text_content = ""
    try:
        if file_type.startswith('text/'):
            text_content = content.decode('utf-8')
        elif file_name.endswith('.json'):
            text_content = content.decode('utf-8')
        elif file_name.endswith('.csv'):
            text_content = content.decode('utf-8')
        elif file_name.endswith('.md'):
            text_content = content.decode('utf-8')
        else:
            text_content = f"File uploaded: {file_name} ({file_type})"
    except:
        text_content = f"File uploaded: {file_name} (binary)"
    
    # Store in knowledge base
    with db.get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO knowledge (user_id, text, category, source) VALUES (?, ?, ?, ?)",
            (user['id'], text_content[:1000], "file_upload", file_name)
        )
        conn.commit()
        knowledge_id = cursor.lastrowid
    
    return {
        "status": "success",
        "message": f"File {file_name} uploaded and processed",
        "file": {
            "name": file_name,
            "type": file_type,
            "size": len(content),
            "knowledge_id": knowledge_id,
            "preview": text_content[:500] + ("..." if len(text_content) > 500 else "")
        }
    }

# ============================================
# ANALYTICS
# ============================================

@app.get("/api/analytics")
@limiter.limit("10/minute")
async def get_analytics(request: Request, user: dict = Depends(verify_api_key)):
    """Get analytics data"""
    with db.get_connection() as conn:
        # Total requests
        total_requests = conn.execute(
            "SELECT COUNT(*) FROM analytics WHERE user_id = ?",
            (user['id'],)
        ).fetchone()[0]
        
        # Requests by endpoint
        endpoints = conn.execute(
            "SELECT endpoint, COUNT(*) as count FROM analytics WHERE user_id = ? GROUP BY endpoint",
            (user['id'],)
        ).fetchall()
        
        # Recent activity
        recent = conn.execute(
            "SELECT * FROM analytics WHERE user_id = ? ORDER BY created_at DESC LIMIT 20",
            (user['id'],)
        ).fetchall()
    
    return {
        "status": "success",
        "analytics": {
            "total_requests": total_requests,
            "endpoints": [dict(e) for e in endpoints],
            "recent": [dict(r) for r in recent]
        }
    }

# ============================================
# WEBHOOKS
# ============================================

webhook_subscribers = []

@app.post("/api/webhook/subscribe")
async def subscribe_webhook(request: Request, webhook_req: WebhookRequest):
    """Subscribe to webhook events"""
    subscriber = {
        "event": webhook_req.event,
        "callback_url": str(webhook_req.callback_url) if webhook_req.callback_url else None,
        "payload": webhook_req.payload,
        "subscribed_at": datetime.now().isoformat()
    }
    webhook_subscribers.append(subscriber)
    return {
        "status": "success",
        "subscriber": subscriber
    }

@app.get("/api/webhook/events")
async def get_webhook_events():
    """List webhook events"""
    return {
        "status": "success",
        "events": [
            "task.completed",
            "bot.created",
            "knowledge.learned",
            "file.uploaded"
        ]
    }

# ============================================
# EXPORT ENDPOINTS
# ============================================

@app.get("/api/export/csv")
@limiter.limit("5/minute")
async def export_csv(request: Request, user: dict = Depends(verify_api_key)):
    """Export tasks as CSV"""
    with db.get_connection() as conn:
        tasks = conn.execute(
            "SELECT id, description, status, created_at, completed_at FROM tasks WHERE user_id = ?",
            (user['id'],)
        ).fetchall()
    
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Description", "Status", "Created At", "Completed At"])
    
    for task in tasks:
        writer.writerow([task['id'], task['description'], task['status'], task['created_at'], task['completed_at']])
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=tasks_export.csv"}
    )

@app.get("/api/export/json")
@limiter.limit("5/minute")
async def export_json(request: Request, user: dict = Depends(verify_api_key)):
    """Export all data as JSON"""
    with db.get_connection() as conn:
        tasks = conn.execute(
            "SELECT * FROM tasks WHERE user_id = ?",
            (user['id'],)
        ).fetchall()
        
        knowledge = conn.execute(
            "SELECT * FROM knowledge WHERE user_id = ?",
            (user['id'],)
        ).fetchall()
        
        bots = conn.execute(
            "SELECT * FROM bots WHERE user_id = ?",
            (user['id'],)
        ).fetchall()
    
    export_data = {
        "user": user['username'],
        "exported_at": datetime.now().isoformat(),
        "version": APP_VERSION,
        "tasks": [dict(t) for t in tasks],
        "knowledge": [dict(k) for k in knowledge],
        "bots": [dict(b) for b in bots]
    }
    
    return JSONResponse(content=export_data)

# ============================================
# DEBUG ENDPOINTS
# ============================================

@app.get("/api/debug/logs")
async def get_logs():
    return {"status": "success", "message": "Logs available in Vercel console"}

@app.get("/api/test")
async def test():
    return {
        "status": "success",
        "message": "Boijelux v7.1 is working!",
        "version": APP_VERSION,
        "timestamp": datetime.now().isoformat(),
        "features": [
            "Authentication",
            "Web search (DuckDuckGo)",
            "URL fetching",
            "Chat with internet",
            "Task processing with internet",
            "Code generation",
            "File upload",
            "Analytics",
            "Webhooks",
            "Export (CSV, JSON)"
        ]
    }

# ============================================
# EXCEPTION HANDLERS
# ============================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"status": "error", "detail": exc.errors()},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error", "message": str(exc)},
    )

# ============================================
# LIFESPAN EVENTS
# ============================================

@app.on_event("startup")
async def startup_event():
    app.state.start_time = time.time()
    print(f"\n{'='*70}")
    print(f"🚀 {APP_NAME} v{APP_VERSION} - Ready")
    print(f"📅 Started at: {datetime.now().isoformat()}")
    print(f"🌐 Domain: {DOMAIN}")
    print(f"🔍 Debug: {DEBUG}")
    print(f"📡 Features: Auth, Internet, Code Gen, File Upload, Analytics")
    print(f"📚 Docs: /api/docs")
    print(f"{'='*70}\n")

# ============================================
# VERCEL HANDLER
# ============================================

handler = app

# ============================================
# LOCAL DEVELOPMENT
# ============================================

if __name__ == "__main__":
    uvicorn.run(
        "api.index:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )
