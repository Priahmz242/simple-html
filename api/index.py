"""
Unlimited AI Agent - Debug Version
Deployed on Vercel
Full logging for troubleshooting
"""

import time
import json
import traceback
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
import uvicorn

# ============================================
# DEBUG CONFIGURATION
# ============================================

DEBUG = True
REQUEST_LOG = []
MAX_LOGS = 100

def log_request(method: str, path: str, status: int, duration: float, error: str = None):
    """Log all requests with details"""
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
    
    # Print to console (visible in Vercel logs)
    print(f"📥 {method} {path} → {status} ({entry['duration_ms']}ms)" + (f" ❌ {error}" if error else ""))

# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title="Unlimited AI Agent - Debug",
    version="2.0.0",
    description="Debug version with full logging",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Enable CORS with debug headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Debug-Id", "X-Response-Time"],
)

# ============================================
# MIDDLEWARE - Request Logger
# ============================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with timing"""
    start_time = time.time()
    
    # Get request details
    method = request.method
    path = request.url.path
    headers = dict(request.headers)
    
    print(f"\n{'='*70}")
    print(f"🔵 REQUEST: {method} {path}")
    print(f"📋 Headers: {json.dumps(headers, indent=2, default=str)}")
    
    # Get body for POST/PUT
    body = None
    if method in ["POST", "PUT", "PATCH"]:
        try:
            body_bytes = await request.body()
            if body_bytes:
                body = body_bytes.decode('utf-8')
                print(f"📦 Body: {body[:500]}..." if len(body) > 500 else f"📦 Body: {body}")
        except:
            pass
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Log response
        log_request(method, path, response.status_code, duration)
        print(f"✅ RESPONSE: {response.status_code} ({duration*1000:.2f}ms)")
        print("="*70)
        
        # Add debug headers
        response.headers["X-Debug-Id"] = f"req_{int(start_time*1000)}"
        response.headers["X-Response-Time"] = f"{duration*1000:.2f}ms"
        
        return response
    except Exception as e:
        duration = time.time() - start_time
        error_msg = str(e)
        log_request(method, path, 500, duration, error_msg)
        print(f"❌ ERROR: {error_msg}")
        traceback.print_exc()
        print("="*70)
        raise

# ============================================
# PYDANTIC MODELS
# ============================================

class TaskRequest(BaseModel):
    task: str
    context: Optional[Dict[str, Any]] = None

class CreateBotRequest(BaseModel):
    requirements: str
    location: str = "local"
    name: Optional[str] = None

class LearnRequest(BaseModel):
    text: str
    category: str = "general"
    source: str = "user_input"

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

# ============================================
# IN-MEMORY STORAGE
# ============================================

tasks_db = []
bots_db = []
knowledge_db = []
task_counter = 0

# ============================================
# ROUTES
# ============================================

@app.get("/")
async def root():
    """Root endpoint - serves HTML dashboard with debug info"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Unlimited AI Agent - Debug</title>
        <style>
            * { margin:0; padding:0; box-sizing:border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #0a0a0a;
                color: #fff;
                min-height: 100vh;
                padding: 20px;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            header {
                text-align: center;
                padding: 40px 0;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                margin-bottom: 30px;
            }
            h1 { font-size: 2.5rem; }
            .icon { font-size: 3rem; }
            .status {
                display: inline-block;
                padding: 6px 16px;
                background: #00cc88;
                color: #000;
                border-radius: 20px;
                font-weight: bold;
                margin: 10px 0;
            }
            .debug-badge {
                display: inline-block;
                padding: 4px 12px;
                background: #ffaa00;
                color: #000;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: bold;
                margin-left: 10px;
            }
            .grid {
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 20px;
                margin: 30px 0;
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
                font-size: 0.9rem;
            }
            .endpoints .item {
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
            .debug-section {
                background: rgba(255,255,255,0.03);
                border-radius: 12px;
                padding: 20px;
                margin: 20px 0;
            }
            .debug-section h3 { color: #ffaa00; margin-bottom: 10px; }
            .log-entry {
                padding: 4px 0;
                border-bottom: 1px solid rgba(255,255,255,0.03);
                font-family: monospace;
                font-size: 0.8rem;
                color: #888;
            }
            .log-entry .time { color: #555; }
            .log-entry .success { color: #00cc88; }
            .log-entry .error { color: #ff4444; }
            .footer { text-align: center; padding: 20px; color: #555; margin-top: 30px; border-top: 1px solid rgba(255,255,255,0.1); }
            a { color: #00cc88; text-decoration: none; }
            @media (max-width: 768px) {
                .grid { grid-template-columns: 1fr; }
                h1 { font-size: 1.8rem; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div class="icon">🤖</div>
                <h1>Unlimited AI Agent <span class="debug-badge">🔍 DEBUG</span></h1>
                <p style="color:#888;">Powered by FastAPI | Deployed on Vercel</p>
                <div class="status">● Online</div>
            </header>

            <div class="grid">
                <div class="card">
                    <div class="value" id="statTasks">0</div>
                    <div class="label">Tasks Completed</div>
                </div>
                <div class="card">
                    <div class="value" id="statUptime">0s</div>
                    <div class="label">Uptime</div>
                </div>
                <div class="card">
                    <div class="value" id="statLogs">0</div>
                    <div class="label">Requests Logged</div>
                </div>
            </div>

            <div class="debug-section">
                <h3>📡 API Endpoints (Debug Mode)</h3>
                <div class="endpoints">
                    <div class="item"><span class="method get">GET</span> <span class="path">/</span> <span style="color:#888;">— Dashboard</span></div>
                    <div class="item"><span class="method get">GET</span> <span class="path">/api/health</span> <span style="color:#888;">— Health check</span></div>
                    <div class="item"><span class="method get">GET</span> <span class="path">/api/status</span> <span style="color:#888;">— Agent status</span></div>
                    <div class="item"><span class="method get">GET</span> <span class="path">/api/tasks</span> <span style="color:#888;">— List tasks</span></div>
                    <div class="item"><span class="method post">POST</span> <span class="path">/api/task</span> <span style="color:#888;">— Process task</span></div>
                    <div class="item"><span class="method post">POST</span> <span class="path">/api/create_bot</span> <span style="color:#888;">— Create bot</span></div>
                    <div class="item"><span class="method post">POST</span> <span class="path">/api/learn</span> <span style="color:#888;">— Learn</span></div>
                    <div class="item"><span class="method get">GET</span> <span class="path">/api/debug/logs</span> <span style="color:#888;">— View logs</span></div>
                    <div class="item"><span class="method get">GET</span> <span class="path">/api/docs</span> <span style="color:#888;">— API Docs</span></div>
                </div>
            </div>

            <div class="debug-section">
                <h3>📋 Recent Requests</h3>
                <div id="logsContainer">
                    <div style="color:#555;text-align:center;padding:20px;">Loading logs...</div>
                </div>
            </div>

            <div class="footer">
                <p>🤖 Unlimited Autonomous AI Agent — Debug Mode</p>
                <p><a href="https://ai.taagc.site">ai.taagc.site</a> | © 2026 TAAGC</p>
            </div>
        </div>

        <script>
            // Load stats and logs
            async function loadData() {
                try {
                    // Status
                    const res1 = await fetch('/api/status');
                    const data = await res1.json();
                    if (data.status === 'success') {
                        document.getElementById('statTasks').textContent = data.agent?.tasks_completed || 0;
                        document.getElementById('statUptime').textContent = formatUptime(data.agent?.uptime || 0);
                    }
                } catch(e) { console.error('Status error:', e); }

                try {
                    // Logs
                    const res2 = await fetch('/api/debug/logs');
                    const logs = await res2.json();
                    if (logs.status === 'success') {
                        document.getElementById('statLogs').textContent = logs.count || 0;
                        const container = document.getElementById('logsContainer');
                        if (logs.logs && logs.logs.length > 0) {
                            let html = '';
                            logs.logs.slice().reverse().forEach(log => {
                                const statusClass = log.status >= 400 ? 'error' : 'success';
                                html += `
                                    <div class="log-entry">
                                        <span class="time">${log.timestamp}</span>
                                        <span class="${statusClass}">${log.method} ${log.path}</span>
                                        <span style="color:#555;">→ ${log.status} (${log.duration_ms}ms)</span>
                                    </div>
                                `;
                            });
                            container.innerHTML = html;
                        } else {
                            container.innerHTML = '<div style="color:#555;text-align:center;padding:20px;">No requests yet</div>';
                        }
                    }
                } catch(e) { console.error('Logs error:', e); }
            }

            function formatUptime(seconds) {
                if (seconds < 60) return Math.floor(seconds) + 's';
                if (seconds < 3600) return Math.floor(seconds / 60) + 'm';
                if (seconds < 86400) return Math.floor(seconds / 3600) + 'h';
                return Math.floor(seconds / 86400) + 'd';
            }

            // Initial load
            loadData();
            // Refresh every 5 seconds
            setInterval(loadData, 5000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

# ============================================
# API ENDPOINTS
# ============================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "debug": DEBUG
    }

@app.get("/api/status")
async def get_status():
    """Agent status"""
    return {
        "status": "success",
        "domain": "ai.taagc.site",
        "server": "Vercel",
        "timestamp": datetime.now().isoformat(),
        "debug": DEBUG,
        "agent": {
            "name": "UnlimitedAI",
            "version": "2.0.0",
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
                "Self-replicating"
            ]
        }
    }

@app.get("/api/tasks")
async def get_tasks():
    """List all tasks"""
    return {
        "status": "success",
        "count": len(tasks_db),
        "tasks": tasks_db
    }

@app.post("/api/task")
async def create_task(request: TaskRequest):
    """Process a task"""
    global task_counter
    task_counter += 1
    
    # Log the request
    print(f"📝 Processing task: {request.task}")
    print(f"   Context: {request.context}")
    
    # Simple domain detection
    domain = "general"
    domain_keywords = {
        'finance': ['finance', 'trade', 'investment', 'stock', 'market', 'bitcoin', 'crypto'],
        'business': ['business', 'company', 'strategy', 'management'],
        'healthcare': ['health', 'doctor', 'patient', 'medical'],
        'technology': ['technology', 'software', 'programming', 'code']
    }
    for d, keywords in domain_keywords.items():
        if any(kw in request.task.lower() for kw in keywords):
            domain = d
            break
    
    result = {
        "success": True,
        "message": f"Task processed: {request.task}",
        "domain": domain,
        "analysis": f"AI analyzed: {request.task[:100]}",
        "suggestions": [
            "Break the task into smaller steps",
            "Use relevant data sources",
            "Monitor progress regularly"
        ],
        "timestamp": datetime.now().isoformat()
    }
    
    task_entry = {
        "id": str(task_counter),
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

@app.post("/api/create_bot")
async def create_bot(request: CreateBotRequest):
    """Create a new bot"""
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
async def learn(request: LearnRequest):
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
        "knowledge": knowledge_item,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/debug/logs")
async def get_logs():
    """Get all request logs"""
    return {
        "status": "success",
        "count": len(REQUEST_LOG),
        "logs": REQUEST_LOG
    }

@app.get("/api/debug/echo")
async def echo(request: Request):
    """Echo back request details for debugging"""
    return {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "query_params": dict(request.query_params)
    }

@app.get("/api/test")
async def test():
    """Simple test endpoint"""
    return {
        "status": "success",
        "message": "FastAPI is working!",
        "timestamp": datetime.now().isoformat(),
        "debug": DEBUG
    }

# ============================================
# EXCEPTION HANDLERS
# ============================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"❌ Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "detail": exc.errors(),
            "body": exc.body
        },
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"❌ Global Exception: {str(exc)}")
    traceback.print_exc()
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": str(exc),
            "type": type(exc).__name__
        },
    )

# ============================================
# LIFESPAN EVENTS
# ============================================

@app.on_event("startup")
async def startup_event():
    app.state.start_time = time.time()
    print(f"\n{'='*70}")
    print(f"🚀 Unlimited AI Agent v2.0.0 - DEBUG MODE")
    print(f"📅 Started at: {datetime.now().isoformat()}")
    print(f"🌐 Domain: ai.taagc.site")
    print(f"🔍 Debug: {DEBUG}")
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
