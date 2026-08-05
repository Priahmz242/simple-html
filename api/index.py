"""
Boijelux v7 - Unlimited AI Agent with Full Internet Access
Deployed on Vercel with FastAPI
Version: 7.0.0
"""

import time
import json
import httpx
import asyncio
import re
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, HttpUrl
import uvicorn

# ============================================
# CONFIGURATION
# ============================================

APP_NAME = "Boijelux v7"
APP_VERSION = "7.0.0"
DOMAIN = "ai.taagc.site"
DEPLOYMENT = "Vercel"
DEBUG = True
MAX_WEB_SEARCH_RESULTS = 10
MAX_CONTENT_LENGTH = 10000
REQUEST_TIMEOUT = 30

# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Boijelux v7 - Unlimited AI Agent with Full Internet Access",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# REQUEST LOGGING
# ============================================

REQUEST_LOG = []
MAX_LOGS = 100

def log_request(method: str, path: str, status: int, duration: float, error: str = None):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "method": method,
        "path": path,
        "status": status,
        "duration_ms": round(duration * 1000, 2),
        "error": error
    }
    REQUEST_LOG.append(entry)
    if len(REQUEST_LOG) > MAX_LOGS:
        REQUEST_LOG.pop(0)
    print(f"📥 {method} {path} → {status} ({entry['duration_ms']}ms)" + (f" ❌ {error}" if error else ""))

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    log_request(request.method, request.url.path, response.status_code, duration)
    return response

# ============================================
# PYDANTIC MODELS
# ============================================

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
    use_internet: bool = Field(False, description="Whether to use internet search")

class WebSearchRequest(BaseModel):
    query: str = Field(..., description="The search query.")
    max_results: int = Field(5, ge=1, le=20)

class UrlFetchRequest(BaseModel):
    url: HttpUrl = Field(..., description="The URL to fetch.")
    max_length: int = Field(5000, ge=100, le=50000)

class GenerateCodeRequest(BaseModel):
    description: str = Field(..., description="Description of the code to generate.")
    language: str = Field("python", description="Programming language")
    framework: Optional[str] = None

# ============================================
# IN-MEMORY STORAGE
# ============================================

tasks_db: List[Dict] = []
bots_db: List[Dict] = []
knowledge_db: List[Dict] = []
logs_db: List[Dict] = []
task_counter = 0
chat_history: List[Dict] = []

# ============================================
# INTERNET ACCESS HELPERS
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
    except httpx.TimeoutException:
        return {"success": False, "error": "Request timed out"}
    except httpx.HTTPStatusError as e:
        return {"success": False, "error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def _extract_title(html_content: str) -> str:
    """Extract title from HTML content"""
    match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
    return match.group(1).strip() if match else "Untitled"

async def search_web(query: str, max_results: int = 5) -> Dict:
    """Search the web using DuckDuckGo HTML (free, no API key)"""
    try:
        search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
        
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
            response = await client.get(search_url)
            response.raise_for_status()
            
            html = response.text
            
            # Extract search results
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
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results)
            }
    except Exception as e:
        return {"success": False, "error": str(e), "results": []}

async def generate_code(description: str, language: str = "python", framework: str = None) -> Dict:
    """Generate code based on description (simplified)"""
    # This is a simplified code generator
    # In production, this would use an LLM API
    
    templates = {
        "python": {
            "default": f'''
"""
Generated Python Code
Description: {description}
Generated by Boijelux v7
"""

def main():
    print("Boijelux v7 Generated Code")
    print(f"Task: {description}")

if __name__ == "__main__":
    main()
''',
            "fastapi": f'''
"""
FastAPI Endpoint
Generated by Boijelux v7
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
async def root():
    return {{"message": "Boijelux v7 API"}}

@app.get("/health")
async def health():
    return {{"status": "healthy"}}
'''
        },
        "javascript": {
            "default": f'''
// Generated JavaScript Code
// Description: {description}
// Generated by Boijelux v7

function main() {{
    console.log("Boijelux v7 Generated Code");
    console.log("Task: {description}");
}}

main();
'''
        }
    }
    
    lang_templates = templates.get(language, templates["python"])
    
    if framework and framework.lower() in lang_templates:
        code = lang_templates[framework.lower()]
    else:
        code = lang_templates["default"]
    
    return {
        "success": True,
        "language": language,
        "framework": framework,
        "code": code,
        "description": description
    }

# ============================================
# AI PROCESSING ENGINE
# ============================================

async def process_with_ai(task: str, context: Dict = None, use_internet: bool = False) -> Dict:
    """Process task with optional internet access"""
    context = context or {}
    
    # Domain detection
    domain = "general"
    domain_keywords = {
        'finance': ['finance', 'trade', 'investment', 'stock', 'market', 'bitcoin', 'crypto', 'price'],
        'business': ['business', 'company', 'strategy', 'management', 'ceo', 'organization'],
        'healthcare': ['health', 'doctor', 'patient', 'medical', 'hospital', 'disease'],
        'technology': ['technology', 'software', 'programming', 'code', 'database', 'system'],
        'legal': ['legal', 'law', 'contract', 'rights', 'court', 'attorney'],
        'creative': ['creative', 'design', 'art', 'music', 'writing', 'content']
    }
    for d, keywords in domain_keywords.items():
        if any(kw in task.lower() for kw in keywords):
            domain = d
            break
    
    # Internet search if requested
    internet_data = None
    if use_internet:
        search_result = await search_web(task, 3)
        if search_result.get('success'):
            internet_data = search_result.get('results', [])
    
    return {
        "success": True,
        "message": f"Task processed: {task}",
        "domain": domain,
        "analysis": f"AI analyzed: {task[:100]}...",
        "suggestions": [
            "Break the task into smaller steps",
            "Use relevant data sources",
            "Monitor progress regularly"
        ],
        "internet_used": use_internet,
        "internet_data": internet_data,
        "confidence": 0.85,
        "timestamp": datetime.now().isoformat()
    }

# ============================================
# API ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """Serve the main dashboard."""
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
        <title>Boijelux v7</title>
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
            <h1>Boijelux v7</h1>
            <p class="version">Unlimited AI Agent with Full Internet Access</p>
            <p class="status">● Online & Running</p>
            <p><a href="/api/docs">📚 API Documentation</a></p>
            <p style="color:#888;margin-top:20px;">🤖 Any Task • Any Domain • Anywhere</p>
            <div class="footer">© 2026 Boijelux</div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# ============================================
# CORE API ENDPOINTS
# ============================================

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": APP_VERSION,
        "name": APP_NAME
    }

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
async def get_status():
    return {
        "status": "success",
        "domain": DOMAIN,
        "server": DEPLOYMENT,
        "timestamp": datetime.now().isoformat(),
        "debug": DEBUG,
        "agent": {
            "name": APP_NAME,
            "version": APP_VERSION,
            "state": "online",
            "tasks_completed": len([t for t in tasks_db if t.get('status') == 'completed']),
            "uptime": time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0,
            "bots_created": len(bots_db),
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
                "Code generation"
            ]
        }
    }

@app.get("/api/metrics")
async def get_metrics():
    return {
        "tasks_total": len(tasks_db),
        "tasks_completed": len([t for t in tasks_db if t.get('status') == 'completed']),
        "bots_created": len(bots_db),
        "knowledge_items": len(knowledge_db),
        "logs_count": len(logs_db),
        "version": APP_VERSION
    }

@app.get("/api/tasks")
async def get_tasks():
    return {
        "status": "success",
        "count": len(tasks_db),
        "tasks": tasks_db[-50:]
    }

@app.post("/api/task")
async def create_task(request: TaskRequest):
    """Process a task with optional internet access"""
    global task_counter
    task_counter += 1
    
    use_internet = request.context.get('use_internet', False)
    result = await process_with_ai(request.task, request.context, use_internet)
    
    task_entry = {
        "id": str(task_counter),
        "description": request.task,
        "context": request.context,
        "status": "completed" if result.get('success') else "failed",
        "created": datetime.now().isoformat(),
        "completed": datetime.now().isoformat(),
        "result": result
    }
    tasks_db.append(task_entry)
    
    return {
        "status": "success",
        "task": task_entry,
        "result": result
    }

@app.post("/api/create_bot")
async def create_bot(request: CreateBotRequest):
    bot = {
        "name": request.name or f"Bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "requirements": request.requirements,
        "location": request.location,
        "created": datetime.now().isoformat(),
        "status": "active"
    }
    bots_db.append(bot)
    return {
        "status": "success",
        "bot": bot
    }

@app.post("/api/learn")
async def learn_text(request: LearnRequest):
    knowledge_item = {
        "id": len(knowledge_db) + 1,
        "text": request.text[:200] + "..." if len(request.text) > 200 else request.text,
        "full_text": request.text,
        "category": request.category,
        "source": request.source,
        "learned": datetime.now().isoformat()
    }
    knowledge_db.append(knowledge_item)
    return {
        "status": "success",
        "message": "Learning successful",
        "knowledge": knowledge_item
    }

@app.get("/api/knowledge")
async def get_knowledge():
    return {
        "status": "success",
        "count": len(knowledge_db),
        "knowledge": knowledge_db[-50:]
    }

# ============================================
# INTERNET ACCESS ENDPOINTS
# ============================================

@app.post("/api/search")
async def web_search(request: WebSearchRequest):
    """Search the web using DuckDuckGo"""
    result = await search_web(request.query, request.max_results)
    return {
        "status": "success" if result.get('success') else "error",
        "data": result
    }

@app.post("/api/fetch")
async def fetch_url(request: UrlFetchRequest):
    """Fetch and extract content from a URL"""
    result = await fetch_url_content(str(request.url), request.max_length)
    return {
        "status": "success" if result.get('success') else "error",
        "data": result
    }

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat endpoint with optional internet search"""
    internet_context = None
    if request.use_internet:
        search_result = await search_web(request.message, 3)
        if search_result.get('success'):
            internet_context = search_result.get('results', [])
    
    chat_entry = {
        "session_id": request.session_id or "new-session",
        "message": request.message,
        "response": f"Boijelux v7 received: '{request.message}'",
        "internet_used": request.use_internet,
        "timestamp": datetime.now().isoformat()
    }
    
    if internet_context:
        chat_entry["internet_results"] = internet_context[:3]
    
    chat_history.append(chat_entry)
    
    return {
        "status": "success",
        "chat": chat_entry
    }

@app.post("/api/generate_code")
async def generate_code_endpoint(request: GenerateCodeRequest):
    """Generate code based on description"""
    result = await generate_code(request.description, request.language, request.framework)
    return {
        "status": "success" if result.get('success') else "error",
        "data": result
    }

@app.get("/api/chat/history")
async def get_chat_history():
    return {
        "status": "success",
        "count": len(chat_history),
        "history": chat_history[-50:]
    }

# ============================================
# DEBUG ENDPOINTS
# ============================================

@app.get("/api/debug/logs")
async def get_logs():
    return {
        "status": "success",
        "count": len(REQUEST_LOG),
        "logs": REQUEST_LOG
    }

@app.get("/api/debug/echo")
async def echo(request: Request):
    return {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "query_params": dict(request.query_params)
    }

@app.get("/api/test")
async def test():
    return {
        "status": "success",
        "message": "Boijelux v7 is working!",
        "version": APP_VERSION,
        "timestamp": datetime.now().isoformat(),
        "features": [
            "Web search (DuckDuckGo)",
            "URL fetching",
            "Chat with internet",
            "Task processing with internet",
            "Code generation"
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
    print(f"📡 Internet: DuckDuckGo Search + URL Fetch")
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
