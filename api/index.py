"""
Minimal Vercel API - Guaranteed to work
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime

# Create app
app = FastAPI()

@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "API is working!",
        "timestamp": datetime.now().isoformat(),
        "server": "Vercel"
    }

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/status")
async def status():
    return {
        "status": "success",
        "message": "Boijelux API is running",
        "timestamp": datetime.now().isoformat()
    }

# Vercel handler
handler = app
