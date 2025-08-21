# mcp_servers/research/app.py
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import asyncio
import httpx
import json
from typing import List, Dict, Any

app = FastAPI(title="sophia-research-mcp", version="4.2.0")

# Allow the dashboard origin
DASHBOARD_ORIGIN = os.getenv("DASHBOARD_ORIGIN", "https://sophia-dashboard.fly.dev")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[DASHBOARD_ORIGIN, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
def healthz():
    return {"status":"ok","service":"sophia-research-mcp","version":"4.2.0"}

def _provider_ok():
    return bool(os.getenv("TAVILY_API_KEY") or os.getenv("SERPER_API_KEY"))

# Normalized response helper
def norm(status, query, results=None, errors=None, summary=""):
    return {
        "status": status,
        "query": query,
        "results": results or [],
        "summary": {"text": summary, "confidence": 0.0, "model": "n/a", "sources":[]},
        "timestamp": "",
        "execution_time_ms": 0,
        "errors": errors or []
    }

async def search_serper(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """Search using Serper API"""
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return []
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
                json={"q": query, "num": k},
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # Process organic results
                for item in data.get("organic", [])[:k]:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", "")
                    })
                
                return results
    except Exception as e:
        print(f"Serper search error: {e}")
    
    return []

async def search_tavily(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """Search using Tavily API"""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return []
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.tavily.com/search",
                headers={"Content-Type": "application/json"},
                json={
                    "api_key": api_key,
                    "query": query,
                    "search_depth": "basic",
                    "include_answer": False,
                    "include_images": False,
                    "include_raw_content": False,
                    "max_results": k
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get("results", [])[:k]:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("content", "")
                    })
                
                return results
    except Exception as e:
        print(f"Tavily search error: {e}")
    
    return []

@app.post("/search")
async def search(payload: dict = Body(...)):
    query = (payload or {}).get("query", "")
    k = int((payload or {}).get("k", 5))
    
    if not _provider_ok():
        return norm("failure", query, errors=[{"provider":"research","code":"missing-secret"}])
    
    # Try Serper first, then Tavily as fallback
    results = []
    
    # Try Serper
    if os.getenv("SERPER_API_KEY"):
        results = await search_serper(query, k)
    
    # If Serper failed or no results, try Tavily
    if not results and os.getenv("TAVILY_API_KEY"):
        results = await search_tavily(query, k)
    
    if results:
        summary = f"Found {len(results)} results for: {query}"
        return norm("success", query, results=results, summary=summary)
    else:
        return norm("failure", query, errors=[{"provider":"research","code":"no-results"}])

# Optional GET alias for debugging
@app.get("/search")
async def search_get(query: str = ""):
    if not _provider_ok():
        return norm("failure", query, errors=[{"provider":"research","code":"missing-secret"}])
    
    # Use the same logic as POST
    results = []
    if os.getenv("SERPER_API_KEY"):
        results = await search_serper(query, 3)
    elif os.getenv("TAVILY_API_KEY"):
        results = await search_tavily(query, 3)
    
    if results:
        return norm("success", query, results=results, summary=f"Debug search for: {query}")
    else:
        return norm("failure", query, errors=[{"provider":"research","code":"no-results"}])

# Optional root to avoid confusion when hitting "/"
@app.get("/")
def root():
    return {"service":"sophia-research-mcp","endpoints":["/healthz","/search (POST, GET)"]}

