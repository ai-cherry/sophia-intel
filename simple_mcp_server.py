#!/usr/bin/env python3
"""
Simple MCP Server for testing
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
from datetime import datetime
from loguru import logger

from mcp_servers.memory_service import MemoryService

# Request models
class ContextRequest(BaseModel):
    session_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = {}

class QueryRequest(BaseModel):
    session_id: str
    query: str
    top_k: int = 5

# Create FastAPI app
app = FastAPI(
    title="Sophia Intel MCP Server",
    description="MCP server with contextualized memory",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize memory service
memory_service = MemoryService()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Sophia Intel MCP Server",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "docs": "http://localhost:8001/docs",
            "health": "/health",
            "store_context": "/context/store",
            "query_context": "/context/query",
            "session_history": "/context/history/{session_id}"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    memory_health = await memory_service.health_check()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "memory_service": memory_health
    }

@app.post("/context/store")
async def store_context(request: ContextRequest):
    """Store context in memory"""
    try:
        result = await memory_service.store_context(
            session_id=request.session_id,
            content=request.content,
            metadata=request.metadata
        )
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Failed to store context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/context/query")
async def query_context(request: QueryRequest):
    """Query context from memory"""
    try:
        results = await memory_service.query_context(
            session_id=request.session_id,
            query=request.query,
            top_k=request.top_k
        )
        return {"success": True, "results": results}
    except Exception as e:
        logger.error(f"Failed to query context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/context/history/{session_id}")
async def get_history(session_id: str, limit: int = 100):
    """Get session history"""
    try:
        history = await memory_service.get_session_history(session_id, limit)
        return {"success": True, "session_id": session_id, "history": history}
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/context/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a session's memory"""
    try:
        result = await memory_service.clear_session(session_id)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Failed to clear session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions")
async def list_sessions():
    """List all sessions"""
    try:
        # Get sessions from local memory
        if hasattr(memory_service, 'local_memory'):
            sessions = list(memory_service.local_memory.keys())
            return {
                "success": True,
                "sessions": sessions,
                "count": len(sessions)
            }
        return {"success": True, "sessions": [], "count": 0}
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("Starting Sophia Intel MCP Server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
