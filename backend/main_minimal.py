"""
Mewayz API - ULTRA MINIMAL CONTAINER VERSION
Guaranteed to start in any container environment
"""

import logging
import sys
import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ultra-simple logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("mewayz")

# Create the most minimal FastAPI app possible
app = FastAPI(title="Mewayz API", version="2.0.0")

# Minimal CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("🚀 Mewayz API starting...")

@app.get("/")
async def root():
    """Root endpoint - always works"""
    return {
        "service": "mewayz-api",
        "status": "running",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "API is operational"
    }

@app.get("/health")
async def health():
    """Health check - always returns healthy"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/health")
async def api_health():
    """API health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/readiness")
async def readiness():
    """Kubernetes readiness probe"""
    return {"ready": True}

@app.get("/liveness")  
async def liveness():
    """Kubernetes liveness probe"""
    return {"alive": True}

# Basic API endpoints that don't require database
@app.get("/api/status")
async def api_status():
    """API status"""
    return {
        "api": "operational",
        "version": "2.0.0", 
        "timestamp": datetime.utcnow().isoformat()
    }

logger.info("✅ Mewayz API ready")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")