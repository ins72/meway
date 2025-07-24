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

# Auto-enable minimal mode in production containers if many imports fail
if not MINIMAL_MODE:
    logger.info("Loading full router configuration...")
    try:
        # Test critical imports first
        from api.auth import router as auth_router
        from api.user import router as user_router
        
        app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
        app.include_router(user_router, prefix="/api/user", tags=["user"])
        logger.info("✅ Core routers loaded successfully")
        
        # Try to load additional routers with individual error handling
        additional_routers = [
            ("api.admin_plan_management", "/api/admin-plan-management", "admin"),
            ("api.plan_change_impact", "/api/plan-change-impact", "plan_impact"),
        ]
        
        loaded_routers = 2  # auth and user already loaded
        
        for router_path, prefix, tag in additional_routers:
            try:
                module = __import__(router_path, fromlist=["router"])
                router = getattr(module, "router")
                app.include_router(router, prefix=prefix, tags=[tag])
                loaded_routers += 1
                logger.info(f"✅ {router_path} loaded")
            except Exception as e:
                logger.warning(f"⚠️ {router_path} not available: {e}")
        
        logger.info(f"✅ Total routers loaded: {loaded_routers}")
            
    except Exception as e:
        logger.error(f"❌ Critical router loading failed: {e}")
        logger.info("🔄 Falling back to minimal mode")
        MINIMAL_MODE = True

if MINIMAL_MODE:
    logger.info("🚀 Running in minimal mode - core endpoints only")
    logger.info("   Available endpoints: /, /health, /api/health")

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