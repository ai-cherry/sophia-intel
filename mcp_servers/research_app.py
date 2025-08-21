"""
Standalone Research Server App for Deployment
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .research_server import router

# Create FastAPI app
app = FastAPI(
    title="SOPHIA Research Server v4.2",
    description="Multi-source research service",
    version="4.2.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the research router
app.include_router(router, prefix="", tags=["Research"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "SOPHIA Research Server v4.2",
        "version": "4.2.0",
        "status": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

