"""
Boijelux v7.1 - Complete API with All Endpoints
Deployed on Vercel
"""

import time
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, Field
import uvicorn

# ============================================
# APP INITIALIZATION
# ============================================

app = FastAPI(
    title="Boijelux v7.1",
    version="7.1.0",
    description="Complete API with All Endpoints",
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
# DATA STORAGE
# ============================================

tasks_db = []
bots_db = []
knowledge_db = []
conversations_db = []
task_counter = 0

# ============================================
# PYDANTIC MODELS
# ============================================

class TaskRequest(BaseModel):
    task: str = Field(..., description="Task description")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class BotRequest(BaseModel):
    requirements: str = Field(..., description="Bot requirements")
    location: str = Field("local")
    name: Optional[str] = None

class LearnRequest(BaseModel):
    text: str = Field(..., description="Text to learn")
    category: str = Field("general")
    source: Optional[str] = Field("user_input")

class ChatRequest(BaseModel):
    message: str = Field(..., description="Chat message")
    session_id: Optional[str] = None
    use_internet: bool = False

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    max_results: int = Field(5, ge=1, le=20)

class UrlFetchRequest(BaseModel):
    url: str = Field(..., description="URL to fetch")
    max_length: int = Field(5000)

class CodeRequest(BaseModel):
    description: str = Field(..., description="Code description")
    language: str = Field("python")
    framework: Optional[str] = None

# ============================================
# HELPERS
# ============================================

def generate_id() -> str:
    """Generate a simple ID"""
    global task_counter
    task_counter += 1
    return str(task_counter)

def log_request(method: str, path: str):
    """Log request"""
    print(f"📥 {method} {path}")

# ============================================
# ROOT ENDPOINT
# ============================================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "status": "success",
        "name": "Boijelux v7.1",
        "version": "7.1.0",
        "message": "API is running!",
        "timestamp": datetime.now().isoformat(),
        "server": "Vercel",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "API info"},
            {"path": "/api/health", "method": "GET", "description": "Health check"},
            {"path": "/api/status", "method": "GET", "description": "Status"},
            {"path": "/api/version", "method": "GET", "description": "Version"},
            {"path": "/api/test", "method": "GET", "description": "Test endpoint"},
            {"path": "/api/tasks", "method": "GET", "description": "List tasks"},
            {"path": "/api/task", "method": "POST", "description": "Create task"},
            {"path": "/api/bots", "method": "GET", "description": "List bots"},
            {"path": "/api/create_bot", "method": "POST", "description": "Create bot"},
            {"path": "/api/knowledge", "method": "GET", "description": "List knowledge"},
            {"path": "/api/learn", "method": "POST", "description": "Learn text"},
            {"path": "/api/search", "method": "POST", "description": "Search web"},
            {"path": "/api/fetch", "method": "POST", "description": "Fetch URL"},
            {"path": "/api/chat", "method": "POST", "description": "Chat"},
            {"path": "/api/generate_code", "method": "POST", "description": "Generate code"},
            {"path": "/api/metrics", "method": "GET", "description": "Metrics"},
            {"path": "/api/dashboard", "method": "GET", "description": "Dashboard HTML"},
            {"path": "/api/docs", "method": "GET", "description": "API Documentation"},
        ]
    }

# ============================================
# HEALTH & STATUS
# ============================================

@app.get("/api/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "7.1.0",
        "server": "Vercel"
    }

@app.get("/api/status")
async def get_status():
    """Agent status"""
    return {
        "status": "success",
        "domain": "simple-html-phi.vercel.app",
        "server": "Vercel",
        "timestamp": datetime.now().isoformat(),
        "agent": {
            "name": "Boijelux v7.1",
            "version": "7.1.0",
            "state": "online",
            "tasks_completed": len([t for t in tasks_db if t.get('status') == 'completed']),
            "bots_created": len(bots_db),
            "knowledge_items": len(knowledge_db),
            "conversations": len(conversations_db),
            "capabilities": [
                "Task management",
                "Bot creation",
                "Knowledge learning",
                "Web search",
                "URL fetching",
                "Chat",
                "Code generation",
                "Analytics"
            ]
        }
    }

@app.get("/api/version")
async def get_version():
    """Version info"""
    return {
        "name": "Boijelux v7.1",
        "version": "7.1.0",
        "timestamp": datetime.now().isoformat(),
        "server": "Vercel",
        "features": [
            "Task Processing",
            "Bot Creation",
            "Knowledge Learning",
            "Web Search",
            "URL Fetching",
            "Chat with Internet",
            "Code Generation",
            "Analytics"
        ]
    }

@app.get("/api/test")
async def test():
    """Test endpoint"""
    return {
        "status": "success",
        "message": "Test successful!",
        "timestamp": datetime.now().isoformat(),
        "all_endpoints": [
            "/api/health",
            "/api/status",
            "/api/version",
            "/api/test",
            "/api/tasks",
            "/api/task",
            "/api/bots",
            "/api/create_bot",
            "/api/knowledge",
            "/api/learn",
            "/api/search",
            "/api/fetch",
            "/api/chat",
            "/api/generate_code",
            "/api/metrics",
            "/api/dashboard"
        ]
    }

# ============================================
# TASKS
# ============================================

@app.get("/api/tasks")
async def get_tasks():
    """List all tasks"""
    return {
        "status": "success",
        "count": len(tasks_db),
        "tasks": tasks_db[-50:]
    }

@app.post("/api/task")
async def create_task(request: TaskRequest):
    """Create and process a task"""
    global task_counter
    task_counter += 1
    
    task_id = str(task_counter)
    
    result = {
        "success": True,
        "message": f"Task processed: {request.task}",
        "domain": "general",
        "analysis": f"Analyzed: {request.task[:100]}...",
        "suggestions": [
            "Break into smaller steps",
            "Use relevant data sources",
            "Monitor progress"
        ],
        "timestamp": datetime.now().isoformat()
    }
    
    task_entry = {
        "id": task_id,
        "description": request.task,
        "context": request.context,
        "status": "completed",
        "created": datetime.now().isoformat(),
        "result": result
    }
    tasks_db.append(task_entry)
    
    return {
        "status": "success",
        "task": task_entry,
        "result": result
    }

# ============================================
# BOTS
# ============================================

@app.get("/api/bots")
async def get_bots():
    """List all bots"""
    return {
        "status": "success",
        "count": len(bots_db),
        "bots": bots_db
    }

@app.post("/api/create_bot")
async def create_bot(request: BotRequest):
    """Create a new bot"""
    bot = {
        "id": generate_id(),
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

# ============================================
# KNOWLEDGE
# ============================================

@app.get("/api/knowledge")
async def get_knowledge():
    """List knowledge items"""
    return {
        "status": "success",
        "count": len(knowledge_db),
        "knowledge": knowledge_db[-50:]
    }

@app.post("/api/learn")
async def learn_text(request: LearnRequest):
    """Learn from text"""
    knowledge_item = {
        "id": len(knowledge_db) + 1,
        "text": request.text[:200] + "..." if len(request.text) > 200 else request.text,
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

# ============================================
# INTERNET FEATURES
# ============================================

@app.post("/api/search")
async def search_web(request: SearchRequest):
    """Search the web (mock implementation)"""
    # Simulate search results
    results = [
        {
            "title": f"Result 1 for: {request.query}",
            "url": f"https://example.com/result1",
            "snippet": f"This is a search result for {request.query}..."
        },
        {
            "title": f"Result 2 for: {request.query}",
            "url": f"https://example.com/result2",
            "snippet": f"Another result about {request.query}..."
        }
    ]
    
    return {
        "status": "success",
        "query": request.query,
        "results": results[:request.max_results],
        "count": len(results)
    }

@app.post("/api/fetch")
async def fetch_url(request: UrlFetchRequest):
    """Fetch URL content (mock implementation)"""
    return {
        "status": "success",
        "url": request.url,
        "title": f"Content from {request.url}",
        "content": f"This is the content from {request.url}...",
        "content_type": "text/html",
        "length": 150
    }

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat endpoint with internet option"""
    response = f"Boijelux received: '{request.message}'"
    
    if request.use_internet:
        response += "\n\n🔍 Internet search enabled. Would you like me to search for more information?"
    
    chat_entry = {
        "session_id": request.session_id or "new-session",
        "message": request.message,
        "response": response,
        "internet_used": request.use_internet,
        "timestamp": datetime.now().isoformat()
    }
    conversations_db.append(chat_entry)
    
    return {
        "status": "success",
        "chat": chat_entry
    }

@app.post("/api/generate_code")
async def generate_code(request: CodeRequest):
    """Generate code"""
    code = f'''
"""
Generated {request.language} Code
Description: {request.description}
Generated by Boijelux v7.1
"""

def main():
    print("Hello from Boijelux!")
    print(f"Task: {request.description}")

if __name__ == "__main__":
    main()
'''
    
    return {
        "status": "success",
        "language": request.language,
        "framework": request.framework,
        "code": code,
        "description": request.description
    }

# ============================================
# METRICS
# ============================================

@app.get("/api/metrics")
async def get_metrics():
    """Get system metrics"""
    return {
        "status": "success",
        "metrics": {
            "tasks_total": len(tasks_db),
            "tasks_completed": len([t for t in tasks_db if t.get('status') == 'completed']),
            "bots_created": len(bots_db),
            "knowledge_items": len(knowledge_db),
            "conversations": len(conversations_db),
            "uptime": 0,
            "timestamp": datetime.now().isoformat()
        }
    }

# ============================================
# DASHBOARD
# ============================================

@app.get("/api/dashboard")
async def dashboard():
    """HTML Dashboard"""
    html = """
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
                padding: 20px;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            header {
                text-align: center;
                padding: 30px 0;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                margin-bottom: 30px;
            }
            h1 { font-size: 2.5rem; }
            .icon { font-size: 3rem; }
            .status { color: #00cc88; }
            .grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                margin-bottom: 30px;
            }
            .card {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 12px;
                padding: 20px;
                text-align: center;
            }
            .card .value { font-size: 2rem; font-weight: bold; color: #00cc88; }
            .card .label { color: #888; font-size: 0.9rem; margin-top: 5px; }
            .endpoints {
                background: rgba(255,255,255,0.03);
                border-radius: 12px;
                padding: 20px;
                margin: 20px 0;
                font-family: monospace;
            }
            .endpoint {
                padding: 8px 0;
                border-bottom: 1px solid rgba(255,255,255,0.05);
            }
            .method {
                display: inline-block;
                padding: 2px 10px;
                border-radius: 4px;
                font-weight: bold;
                margin-right: 10px;
            }
            .method.get { background: #00cc88; color: #000; }
            .method.post { background: #ffaa00; color: #000; }
            .path { color: #00cc88; }
            .footer { text-align: center; color: #555; margin-top: 30px; padding: 20px; border-top: 1px solid rgba(255,255,255,0.1); }
            @media (max-width: 768px) {
                .grid { grid-template-columns: 1fr 1fr; }
                h1 { font-size: 1.8rem; }
            }
            @media (max-width: 480px) {
                .grid { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div class="icon">🚀</div>
                <h1>Boijelux v7.1</h1>
                <p style="color:#888;">Complete API with All Endpoints</p>
                <p class="status">● Online & Running</p>
            </header>

            <div class="grid" id="stats">
                <div class="card">
                    <div class="value" id="statTasks">0</div>
                    <div class="label">Tasks</div>
                </div>
                <div class="card">
                    <div class="value" id="statBots">0</div>
                    <div class="label">Bots</div>
                </div>
                <div class="card">
                    <div class="value" id="statKnowledge">0</div>
                    <div class="label">Knowledge</div>
                </div>
                <div class="card">
                    <div class="value" id="statVersion">v7.1</div>
                    <div class="label">Version</div>
                </div>
            </div>

            <h2 style="color:#00cc88;margin:20px 0;">📡 All Endpoints</h2>
            <div class="endpoints">
                <div class="endpoint"><span class="method get">GET</span> <span class="path">/</span> <span style="color:#888;">— API info</span></div>
                <div class="endpoint"><span class="method get">GET</span> <span class="path">/api/health</span> <span style="color:#888;">— Health check</span></div>
                <div class="endpoint"><span class="method get">GET</span> <span class="path">/api/status</span> <span style="color:#888;">— Status</span></div>
                <div class="endpoint"><span class="method get">GET</span> <span class="path">/api/version</span> <span style="color:#888;">— Version</span></div>
                <div class="endpoint"><span class="method get">GET</span> <span class="path">/api/test</span> <span style="color:#888;">— Test</span></div>
                <div class="endpoint"><span class="method get">GET</span> <span class="path">/api/tasks</span> <span style="color:#888;">— List tasks</span></div>
                <div class="endpoint"><span class="method post">POST</span> <span class="path">/api/task</span> <span style="color:#888;">— Create task</span></div>
                <div class="endpoint"><span class="method get">GET</span> <span class="path">/api/bots</span> <span style="color:#888;">— List bots</span></div>
                <div class="endpoint"><span class="method post">POST</span> <span class="path">/api/create_bot</span> <span style="color:#888;">— Create bot</span></div>
                <div class="endpoint"><span class="method get">GET</span> <span class="path">/api/knowledge</span> <span style="color:#888;">— List knowledge</span></div>
                <div class="endpoint"><span class="method post">POST</span> <span class="path">/api/learn</span> <span style="color:#888;">— Learn text</span></div>
                <div class="endpoint"><span class="method post">POST</span> <span class="path">/api/search</span> <span style="color:#888;">— Search web</span></div>
                <div class="endpoint"><span class="method post">POST</span> <span class="path">/api/fetch</span> <span style="color:#888;">— Fetch URL</span></div>
                <div class="endpoint"><span class="method post">POST</span> <span class="path">/api/chat</span> <span style="color:#888;">— Chat</span></div>
                <div class="endpoint"><span class="method post">POST</span> <span class="path">/api/generate_code</span> <span style="color:#888;">— Generate code</span></div>
                <div class="endpoint"><span class="method get">GET</span> <span class="path">/api/metrics</span> <span style="color:#888;">— Metrics</span></div>
                <div class="endpoint"><span class="method get">GET</span> <span class="path">/api/dashboard</span> <span style="color:#888;">— Dashboard</span></div>
                <div class="endpoint"><span class="method get">GET</span> <span class="path">/api/docs</span> <span style="color:#888;">— API Docs</span></div>
            </div>

            <div class="footer">
                <p>🚀 Boijelux v7.1 — Complete API</p>
                <p><a href="https://simple-html-phi.vercel.app" style="color:#00cc88;text-decoration:none;">simple-html-phi.vercel.app</a></p>
            </div>
        </div>

        <script>
            async function loadStats() {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    if (data.status === 'success') {
                        document.getElementById('statTasks').textContent = data.agent?.tasks_completed || 0;
                        document.getElementById('statBots').textContent = data.agent?.bots_created || 0;
                        document.getElementById('statKnowledge').textContent = data.agent?.knowledge_items || 0;
                    }
                } catch(e) { console.error(e); }
            }
            loadStats();
            setInterval(loadStats, 10000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

# ============================================
# ERROR HANDLERS
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"❌ Error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": str(exc),
            "type": type(exc).__name__
        }
    )

# ============================================
# VERCEL HANDLER
# ============================================

handler = app

# ============================================
# LOCAL DEVELOPMENT
# ============================================

if __name__ == "__main__":
    uvicorn.run("api.index:app", host="0.0.0.0", port=8000, reload=True)
