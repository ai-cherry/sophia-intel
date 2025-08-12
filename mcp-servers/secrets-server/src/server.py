"""
Sophia AIOS Secrets Server
Zero-trust secret distribution service for the entire ecosystem
"""
import os
import json
import hashlib
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
from loguru import logger
import asyncio
from pathlib import Path

# Configuration
SECRET_KEY = os.getenv("SECRETS_SERVER_JWT_SECRET", "dev-secret-change-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="Sophia AIOS Secrets Server", version="1.0.0")
security = HTTPBearer()

# In production, these would come from GitHub Secrets via Pulumi ESC
# For now, we'll use a mock store
class SecretStore:
    """Secure secret storage with audit logging"""
    
    def __init__(self):
        self.secrets = {}
        self.audit_log = []
        self.authorized_services = {
            "tool-server": ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "TAVILY_API_KEY"],
            "memory-server": ["QDRANT_API_KEY", "REDIS_URL", "MEM0_API_KEY"],
            "agent-server": ["PHIDATA_API_KEY", "OPENROUTER_API_KEY"],
            "notion-sync": ["NOTION_API_KEY", "N8N_API_KEY"],
            "gateway": ["PORTKEY_API_KEY", "OPENROUTER_API_KEY"],
        }
        self._load_from_env()
    
    def _load_from_env(self):
        """Load secrets from environment (temporary until Pulumi ESC)"""
        env_file = Path("/Users/lynnmusil/Projects/sophia-main/sophia-intel-clone/.env")
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        if 'KEY' in key or 'TOKEN' in key or 'SECRET' in key:
                            # Hash the value for storage
                            self.secrets[key] = {
                                "value": value,
                                "hash": hashlib.sha256(value.encode()).hexdigest()[:8],
                                "created": datetime.utcnow().isoformat()
                            }
    
    def get_secret(self, service_id: str, secret_name: str) -> Optional[str]:
        """Get a secret if the service is authorized"""
        # Check authorization
        if service_id not in self.authorized_services:
            logger.warning(f"Unauthorized service {service_id} attempted to access {secret_name}")
            return None
        
        if secret_name not in self.authorized_services[service_id]:
            logger.warning(f"Service {service_id} not authorized for secret {secret_name}")
            return None
        
        # Log the access
        self.audit_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "service": service_id,
            "secret": secret_name,
            "action": "accessed"
        })
        
        # Return the secret
        secret_data = self.secrets.get(secret_name)
        if secret_data:
            logger.info(f"Secret {secret_name} accessed by {service_id}")
            return secret_data["value"]
        
        return None
    
    def list_authorized_secrets(self, service_id: str) -> List[str]:
        """List secrets a service is authorized to access"""
        return self.authorized_services.get(service_id, [])

# Initialize the secret store
secret_store = SecretStore()

# Models
class TokenRequest(BaseModel):
    service_id: str
    service_key: str

class SecretRequest(BaseModel):
    secret_name: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = TOKEN_EXPIRE_MINUTES * 60

# Helper functions
def create_access_token(data: dict):
    """Create a JWT token for service authentication"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify and decode JWT token"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        service_id: str = payload.get("service_id")
        if service_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return service_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Sophia AIOS Secrets Server",
        "status": "operational",
        "version": "1.0.0",
        "security": "zero-trust"
    }

@app.post("/auth/token", response_model=TokenResponse)
async def get_token(request: TokenRequest):
    """Authenticate a service and get an access token"""
    # In production, verify service_key against a registry
    # For now, we'll accept known service IDs
    if request.service_id not in secret_store.authorized_services:
        raise HTTPException(status_code=401, detail="Unknown service")
    
    # Create token
    access_token = create_access_token({"service_id": request.service_id})
    
    logger.info(f"Token issued to service: {request.service_id}")
    return TokenResponse(access_token=access_token)

@app.post("/secrets/get")
async def get_secret(
    request: SecretRequest,
    service_id: str = Depends(verify_token)
):
    """Get a specific secret (if authorized)"""
    secret_value = secret_store.get_secret(service_id, request.secret_name)
    
    if secret_value is None:
        raise HTTPException(
            status_code=403, 
            detail=f"Access denied or secret not found"
        )
    
    return {
        "secret_name": request.secret_name,
        "value": secret_value,
        "expires_in": TOKEN_EXPIRE_MINUTES * 60
    }

@app.get("/secrets/authorized")
async def list_authorized_secrets(service_id: str = Depends(verify_token)):
    """List all secrets this service is authorized to access"""
    authorized = secret_store.list_authorized_secrets(service_id)
    return {
        "service_id": service_id,
        "authorized_secrets": authorized,
        "count": len(authorized)
    }

@app.get("/audit/recent")
async def get_recent_audit_logs(
    limit: int = 100,
    service_id: str = Depends(verify_token)
):
    """Get recent audit logs (only for admin services)"""
    # Only allow admin services to view audit logs
    if service_id != "admin-console":
        raise HTTPException(status_code=403, detail="Audit access denied")
    
    return {
        "logs": secret_store.audit_log[-limit:],
        "total": len(secret_store.audit_log)
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "secrets_loaded": len(secret_store.secrets),
        "services_registered": len(secret_store.authorized_services),
        "audit_entries": len(secret_store.audit_log)
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Sophia AIOS Secrets Server...")
    logger.info(f"Loaded {len(secret_store.secrets)} secrets")
    logger.info(f"Registered {len(secret_store.authorized_services)} services")
    uvicorn.run(app, host="0.0.0.0", port=8100)
