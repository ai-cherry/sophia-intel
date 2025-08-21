# mcp_servers/research/app.py
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

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

@app.post("/search")
async def search(payload: dict = Body(...)):
    query = (payload or {}).get("query", "")
    k = int((payload or {}).get("k", 5))
    
    if not _provider_ok():
        return norm("failure", query, errors=[{"provider":"research","code":"missing-secret"}])
    
    # Mock search results with proper structure
    results = [
        {
            "title": f"AI Orchestration Platform {i+1}",
            "url": f"https://example.com/platform-{i+1}",
            "snippet": f"Advanced AI orchestration solution for {query} - Platform {i+1} offers comprehensive automation capabilities."
        }
        for i in range(min(k, 3))
    ]
    
    return norm("success", query, results=results, summary=f"Found {len(results)} results for: {query}")

# Optional GET alias for debugging (so GET /search?query=... won't 404)
@app.get("/search")
async def search_get(query: str = ""):
    if not _provider_ok():
        return norm("failure", query, errors=[{"provider":"research","code":"missing-secret"}])
    
    results = [{"title":"Debug Result","url":"https://example.com","snippet":f"Debug query: {query}"}]
    return norm("success", query, results=results, summary=f"Debug search for: {query}")

# Optional root to avoid confusion when hitting "/"
@app.get("/")
def root():
    return {"service":"sophia-research-mcp","endpoints":["/healthz","/search (POST, GET)"]}

