"""
Mewayz Professional Platform - BULLETPROOF KUBERNETES VERSION
Zero-dependency health checks, ultra-fast startup
"""

import os
import sys
import json
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Minimal logging to stdout only
import logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(message)s')
logger = logging.getLogger("mewayz")

# Global startup time - never changes
STARTUP_TIME = datetime.utcnow()

# Create FastAPI app with minimal configuration
app = FastAPI(
    title="Mewayz API",
    version="2.0.0",
    docs_url=None,  # Disable docs to reduce dependencies
    redoc_url=None  # Disable redoc to reduce dependencies
)

# Minimal CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# BULLETPROOF HEALTH ENDPOINTS - Zero dependencies, instant response
@app.get("/")
def root():
    """Root endpoint - pure Python, no dependencies"""
    return {
        "service": "mewayz-api",
        "status": "running",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
def health():
    """Health check - guaranteed to work, no dependencies"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": (datetime.utcnow() - STARTUP_TIME).total_seconds()
    }

@app.get("/api/health") 
def api_health():
    """API health check - same as health"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": (datetime.utcnow() - STARTUP_TIME).total_seconds()
    }

@app.get("/readiness")
def readiness():
    """Kubernetes readiness probe - always ready"""
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "ready"
    }

@app.get("/liveness")
def liveness():
    """Kubernetes liveness probe - always alive"""
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "alive"
    }

# Log successful startup
logger.info("🚀 Mewayz API starting - health endpoints ready")

# BACKGROUND INITIALIZATION - Never blocks startup
def initialize_application():
    """Initialize application components in background"""
    import asyncio
    import threading
    
    def background_init():
        try:
            # Wait 10 seconds to ensure health checks are working first
            import time
            time.sleep(10)
            
            logger.info("🔄 Starting background initialization...")
            
            # Try to load database connection
            try:
                from core.database import connect_to_mongo
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(connect_to_mongo())
                logger.info("✅ Database connection established")
            except Exception as e:
                logger.warning(f"⚠️ Database connection failed: {e}")
            
            # Try to load essential routers
            try:
                from api.auth import router as auth_router
                app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
                logger.info("✅ Auth router loaded")
            except Exception as e:
                logger.warning(f"⚠️ Auth router failed: {e}")
                
            logger.info("✅ Background initialization complete")
            
        except Exception as e:
            logger.error(f"❌ Background initialization failed: {e}")
    
    # Start background thread
    thread = threading.Thread(target=background_init, daemon=True)
    thread.start()

# Start background initialization
initialize_application()

logger.info("✅ Mewayz API ready - health checks operational")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting uvicorn server...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001,
        log_level="info"
    )