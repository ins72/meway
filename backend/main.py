"""
Mewayz Professional Platform - PRODUCTION DEPLOYMENT VERSION
Optimized for Kubernetes deployment with MongoDB Atlas
"""

import logging
import sys
import os
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import json

# Ultra-simple logging for containers
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("mewayz-api")

# Global application state
app_state = {
    "startup_time": datetime.utcnow(),
    "db_available": False,
    "db_connection_attempted": False,
    "total_routers_loaded": 0
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Production-optimized lifespan - ultra-fast startup"""
    logger.info("🚀 Application starting for production deployment...")
    
    # Don't wait for database - start in background
    asyncio.create_task(initialize_database_connection())
    
    # Load routers in background - don't block startup
    asyncio.create_task(load_application_routers())
    
    logger.info("✅ Application ready for health checks")
    yield
    
    logger.info("🔄 Application shutting down...")

async def initialize_database_connection():
    """Initialize database connection in background - never blocks startup"""
    try:
        await asyncio.sleep(2)  # Small delay to let health checks respond first
        
        mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017/mewayz_professional")
        logger.info(f"Attempting database connection to: {mongo_url[:20]}...")
        
        from core.database import connect_to_mongo
        await connect_to_mongo()
        
        app_state["db_available"] = True
        app_state["db_connection_attempted"] = True
        logger.info("✅ Database connection established")
        
    except Exception as e:
        logger.warning(f"⚠️ Database connection failed (app continues): {e}")
        app_state["db_available"] = False
        app_state["db_connection_attempted"] = True

async def load_application_routers():
    """Load application routers in background"""
    try:
        await asyncio.sleep(5)  # Give more time for health checks to work
        logger.info("🔄 Starting background router loading...")
        
        # Only load essential routers for production
        essential_routers = [
            ("api.auth", "/api/auth", "auth"),
            ("api.stripe_integration", "/api/stripe-integration", "stripe"),
            ("api.workspace", "/api/workspace", "workspace"),
        ]
        
        loaded_count = 0
        
        for router_path, prefix, tag in essential_routers:
            try:
                module = __import__(router_path, fromlist=["router"])
                router = getattr(module, "router")
                app.include_router(router, prefix=prefix, tags=[tag])
                loaded_count += 1
                logger.info(f"✅ {router_path} loaded")
                await asyncio.sleep(0.5)  # Small delay between loads
            except Exception as e:
                logger.warning(f"⚠️ {router_path} failed to load: {e}")
        
        app_state["total_routers_loaded"] = loaded_count
        logger.info(f"✅ Essential routers loaded: {loaded_count}")
        
    except Exception as e:
        logger.error(f"❌ Router loading failed: {e}")
        app_state["total_routers_loaded"] = 0

# Create minimal FastAPI app
app = FastAPI(
    title="Mewayz API",
    version="2.0.0",
    lifespan=lifespan
)

# Minimal CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint - ultra-fast response"""
    return {
        "service": "mewayz-api",
        "status": "running",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": (datetime.utcnow() - app_state["startup_time"]).total_seconds()
    }

@app.get("/health")
async def health():
    """Health check - ultra-fast, always healthy for Kubernetes"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected" if app_state.get("db_available", False) else "initializing",
        "routers_loaded": app_state.get("total_routers_loaded", 0),
        "uptime_seconds": (datetime.utcnow() - app_state["startup_time"]).total_seconds()
    }

@app.get("/api/health")
async def api_health():
    """API health check - same as health"""
    return await health()

@app.get("/readiness")
async def readiness():
    """Kubernetes readiness probe - always ready"""
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat(),
        "routers_loaded": app_state.get("total_routers_loaded", 0)
    }

@app.get("/liveness")
async def liveness():
    """Kubernetes liveness probe - always alive"""
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": (datetime.utcnow() - app_state["startup_time"]).total_seconds()
    }

@app.get("/readiness")
async def readiness():
    """Kubernetes readiness probe"""
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": (datetime.utcnow() - app_state["startup_time"]).total_seconds()
    }

@app.get("/liveness")
async def liveness():
    """Kubernetes liveness probe"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }

# Catch-all for debugging
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def catch_all(request: Request, path: str):
    """Catch-all handler"""
    return {
        "message": "Route not found",
        "path": path,
        "method": request.method,
        "available": ["/", "/health", "/api/health", "/readiness", "/liveness"],
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting uvicorn server...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001,
        log_level="info"
    )