# mcp_servers/context/app.py
from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import List, Dict, Any
import os, re
from .registry import make_index_id, publish_index, latest_index_id, get_index

app = FastAPI(title="sophia-context-mcp", version="4.2.0")

DATA_DIR = Path(os.getenv("CONTEXT_DATA_DIR", "/app/data"))
CACHE_DIR = DATA_DIR / "indexes"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/healthz")
def healthz():
    return {"status":"ok","service":"sophia-context-mcp","version":"4.2.0"}

def _norm_response(status:str, query:str, results:List[Dict[str,Any]]=None, errors:List[Dict[str,str]]=None):
    return {
      "status": status,
      "query": query,
      "results": results or [],
      "summary": {"text":"", "confidence":0.0, "model":"n/a", "sources":[]},
      "timestamp": "",
      "execution_time_ms": 0,
      "errors": errors or []
    }

def _collect_files(root: Path, include: List[str], exclude: List[str]) -> List[Path]:
    # simple glob filter
    files: List[Path] = []
    for pattern in include or ["**/*.py", "**/*.ts", "**/*.tsx", "**/*.js", "**/*.md"]:
        for p in root.glob(pattern):
            if p.is_file():
                skip = False
                for ex in exclude or []:
                    if p.match(ex):
                        skip = True; break
                if not skip:
                    files.append(p)
    return files

@app.post("/context/index")
def index_repo(payload: Dict[str, Any] = Body(...)):
    """
    { repo, include_globs[], exclude_globs[], tags[] }
    For first pass, 'repo' is a local path inside the container (or a mounted workspace).
    Later you can replace this with GitHub API fetch or a read-only checkout.
    """
    repo = (payload or {}).get("repo") or ""
    if not repo:
        # normalized failure, not 404
        return _norm_response("failure", "index", errors=[{"provider":"context","code":"missing-repo"}])

    root = Path(repo)
    if not root.exists():
        return _norm_response("failure", "index", errors=[{"provider":"context","code":"repo-not-found"}])

    include = payload.get("include_globs") or []
    exclude = payload.get("exclude_globs") or []

    files = _collect_files(root, include, exclude)
    idx_id = make_index_id(repo)
    idx_dir = CACHE_DIR / idx_id
    idx_dir.mkdir(parents=True, exist_ok=True)

    # naïve cache: store text content for quick grep-like search
    meta: List[Dict[str, Any]] = []
    for f in files:
        rel = str(f.relative_to(root))
        try:
            text = f.read_text(errors="ignore")
        except Exception:
            text = ""
        (idx_dir / (rel.replace("/", "__") + ".txt")).write_text(text)
        meta.append({"path": rel, "size": len(text)})

    # publish registry entry
    publish_index(
        repo=repo,
        index_id=idx_id,
        meta={"status":"READY","file_count":len(meta),"symbols_count":0, "cache_dir": str(idx_dir)}
    )

    return {"index_id": idx_id, "file_count": len(meta), "symbols_count": 0, "status":"READY"}

@app.get("/context/index/{index_id}")
def get_index_meta(index_id: str):
    meta = get_index(index_id)
    if not meta:
        # consistent normalized failure rather than raw 404
        return _norm_response("failure", "get_index", errors=[{"provider":"context","code":"index-not-found"}])
    return {"index_id": index_id, **meta}

@app.post("/context/search")
def search(payload: Dict[str, Any] = Body(...)):
    query = (payload or {}).get("query") or ""
    k = int((payload or {}).get("k") or 5)
    index_id = (payload or {}).get("index_id")
    repo = (payload or {}).get("repo") or ""

    # resolve index
    idx_id = index_id or (latest_index_id(repo) if repo else None)
    if not idx_id:
        # no index yet → normalized failure
        return _norm_response("failure", query, errors=[{"provider":"context","code":"no-index"}])

    meta = get_index(idx_id)
    if not meta:
        return _norm_response("failure", query, errors=[{"provider":"context","code":"index-not-found"}])

    cache_dir = Path(meta.get("cache_dir",""))
    if not cache_dir.exists():
        return _norm_response("failure", query, errors=[{"provider":"context","code":"cache-missing"}])

    # naïve grep-like search over cached files
    q = query.lower()
    matches: List[Dict[str,Any]] = []
    for txt_file in cache_dir.glob("*.txt"):
        text = txt_file.read_text(errors="ignore").lower()
        if q in text:
            path = txt_file.name.replace("__","/")[:-4]
            # crude line hint
            line_no = 1 + text.split(q,1)[0].count("\n")
            matches.append({"path": path, "lines": [max(1,line_no-2), line_no+2], "symbol": "", "score": 1.0})

    matches = matches[:k]
    return {"matches": matches, "ts": "", "index_id": idx_id, "query": query}

