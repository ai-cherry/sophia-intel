# mcp_servers/context/registry.py
import os, json, hashlib, time, threading
from pathlib import Path
from typing import Optional, Dict, Any

_LOCK = threading.Lock()
DATA_DIR = Path(os.getenv("CONTEXT_DATA_DIR", "/app/data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
REG_PATH = DATA_DIR / "index_registry.json"

def _load() -> Dict[str, Any]:
    if REG_PATH.exists():
        return json.loads(REG_PATH.read_text())
    return {"indexes": {}, "per_repo_latest": {}}

def _save(obj: Dict[str, Any]):
    REG_PATH.write_text(json.dumps(obj, indent=2))

def make_index_id(repo: str) -> str:
    h = hashlib.sha1(repo.encode("utf-8")).hexdigest()[:8]
    ts = int(time.time())
    return f"ctx_{h}_{ts}"

def publish_index(repo: str, index_id: str, meta: Dict[str, Any]):
    with _LOCK:
        obj = _load()
        obj["indexes"][index_id] = {"repo": repo, **meta}
        obj["per_repo_latest"][repo] = index_id
        _save(obj)

def latest_index_id(repo: str) -> Optional[str]:
    with _LOCK:
        obj = _load()
        return obj["per_repo_latest"].get(repo)

def get_index(index_id: str) -> Optional[Dict[str, Any]]:
    with _LOCK:
        obj = _load()
        return obj["indexes"].get(index_id)

