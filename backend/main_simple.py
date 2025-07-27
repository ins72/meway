"""
Mewayz Professional Platform - SIMPLIFIED VERSION
Basic API without database dependencies for initial testing
"""

import os
import sys
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Minimal logging to stdout only
import logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(message)s')
logger = logging.getLogger("mewayz")

# Global startup time - never changes
STARTUP_TIME = datetime.utcnow()

# Create FastAPI app with production configuration
app = FastAPI(
    title="Mewayz Professional Platform API",
    version="2.0.0",
    description="Simplified API for Mewayz Professional Platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Production CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure specific origins for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# BULLETPROOF HEALTH ENDPOINTS - Zero dependencies, instant response
@app.get("/")
def root():
    """Root endpoint - pure Python, no dependencies"""
    return {
        "service": "mewayz-professional-api",
        "status": "running",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "production_ready": True,
        "database": "simplified_mode"
    }

@app.get("/health")
def health():
    """Health check - guaranteed to work, no dependencies"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": (datetime.utcnow() - STARTUP_TIME).total_seconds(),
        "production_ready": True,
        "database": "simplified_mode"
    }

@app.get("/api/health") 
def api_health():
    """API health check - same as health"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": (datetime.utcnow() - STARTUP_TIME).total_seconds(),
        "production_ready": True,
        "database": "simplified_mode"
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

# SIMPLIFIED API ENDPOINTS - No database dependencies
@app.get("/api/users")
def get_users():
    """Get users - simplified version"""
    return {
        "users": [
            {
                "id": "1",
                "email": "admin@mewayz.com",
                "username": "admin",
                "role": "admin",
                "created_at": datetime.utcnow().isoformat()
            }
        ],
        "total": 1,
        "database": "simplified_mode"
    }

@app.get("/api/workspaces")
def get_workspaces():
    """Get workspaces - simplified version"""
    return {
        "workspaces": [
            {
                "id": "1",
                "name": "Default Workspace",
                "owner_id": "1",
                "created_at": datetime.utcnow().isoformat()
            }
        ],
        "total": 1,
        "database": "simplified_mode"
    }

@app.get("/api/subscription/plans")
def get_subscription_plans():
    """Get subscription plans - simplified version"""
    return {
        "plans": [
            {
                "id": "basic",
                "name": "Basic Plan",
                "price": 9.99,
                "features": ["Basic features", "Email support"]
            },
            {
                "id": "pro",
                "name": "Pro Plan", 
                "price": 29.99,
                "features": ["All basic features", "Priority support", "Advanced analytics"]
            },
            {
                "id": "enterprise",
                "name": "Enterprise Plan",
                "price": 99.99,
                "features": ["All pro features", "Custom integrations", "Dedicated support"]
            }
        ],
        "database": "simplified_mode"
    }

@app.post("/api/auth/login")
def login():
    """Login endpoint - simplified version"""
    return {
        "access_token": "simplified_token_12345",
        "token_type": "bearer",
        "user": {
            "id": "1",
            "email": "admin@mewayz.com",
            "username": "admin",
            "role": "admin"
        },
        "database": "simplified_mode"
    }

@app.get("/api/ai/generate")
def generate_ai_content():
    """AI content generation - simplified version"""
    return {
        "content": "This is AI-generated content from the simplified API.",
        "tokens_used": 10,
        "database": "simplified_mode"
    }

# Log successful startup
logger.info("🚀 Mewayz Simplified API starting - health endpoints ready")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting uvicorn server...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )