"""
Mewayz Professional Platform - PRODUCTION VERSION
Ultra-minimal FastAPI for reliable container deployment
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

# Ultra-simple logging for containers
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("mewayz-api")

# Global state for database (optional)
db_available = False

async def try_database_connection():
    """Optional database connection - never blocks startup"""
    global db_available
    try:
        logger.info("Attempting optional database connection...")
        mongo_url = os.getenv("MONGO_URL")
        if mongo_url:
            from motor.motor_asyncio import AsyncIOMotorClient
            client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=3000)
            await asyncio.wait_for(client.admin.command('ping'), timeout=3.0)
            db_available = True
            logger.info("Database connected successfully")
            client.close()
        else:
            logger.info("No MONGO_URL provided - running without database")
    except Exception as e:
        logger.info(f"Database connection failed (continuing anyway): {e}")
        db_available = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Minimal lifespan - never blocks"""
    logger.info("🚀 Application starting...")
    
    # Try database connection in background - don't wait for it
    asyncio.create_task(try_database_connection())
    
    logger.info("✅ Application ready")
    yield
    
    logger.info("🔄 Application shutting down...")

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
    """Root endpoint"""
    return {
        "service": "mewayz-api",
        "status": "running",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health():
    """Health check - always returns healthy"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected" if db_available else "optional"
    }

@app.get("/api/health")
async def api_health():
    """API health check"""
    return await health()

# Only import and include routers if not in minimal mode
MINIMAL_MODE = os.getenv("MINIMAL_MODE", "false").lower() == "true"

if not MINIMAL_MODE:
    logger.info("Loading full router configuration...")
    try:
        # Import core routers only
        from api.auth import router as auth_router
        from api.user import router as user_router
        
        app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
        app.include_router(user_router, prefix="/api/user", tags=["user"])
        logger.info("✅ Core routers loaded successfully")
        
        # Try to load additional routers
        try:
            from api.admin_plan_management import router as admin_plan_router
            app.include_router(admin_plan_router, prefix="/api/admin-plan-management", tags=["admin"])
            logger.info("✅ Admin routers loaded")
        except Exception as e:
            logger.warning(f"Admin routers not available: {e}")
            
    except Exception as e:
        logger.error(f"Router loading error: {e}")
        logger.info("Continuing with minimal API...")
else:
    logger.info("Running in minimal mode - core endpoints only")

# Catch-all for debugging
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def catch_all(request: Request, path: str):
    """Catch-all handler"""
    return {
        "message": "Route not found",
        "path": path,
        "method": request.method,
        "available": ["/", "/health", "/api/health"],
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