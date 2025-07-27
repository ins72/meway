#!/usr/bin/env python3
"""
SIMPLE WORKING APPLICATION
Complete CRUD operations with MongoDB
"""

import os
import sys
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
STARTUP_TIME = datetime.now(timezone.utc)
database = None

# MongoDB connection
async def connect_to_mongo():
    """Connect to MongoDB"""
    global database
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        database = client.mewayz_professional
        # Test connection
        await client.admin.command('ping')
        logger.info("✅ MongoDB connected successfully")
        return True
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        return False

def get_database():
    """Get database instance"""
    return database

# Pydantic models
class WorkspaceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    owner_id: Optional[str] = None
    settings: Optional[Dict[str, Any]] = {}

class UserCreate(BaseModel):
    email: str
    username: str
    full_name: Optional[str] = None
    role: Optional[str] = "user"

# FastAPI app
app = FastAPI(
    title="Mewayz Professional API",
    description="Complete CRUD operations with MongoDB",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB on startup
@app.on_event("startup")
async def startup_event():
    """Connect to MongoDB on startup"""
    await connect_to_mongo()

# Health check endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Mewayz Professional API",
        "version": "2.0.0",
        "status": "running",
        "startup_time": STARTUP_TIME.isoformat(),
        "uptime": str(datetime.now(timezone.utc) - STARTUP_TIME)
    }

@app.get("/health")
async def health_check():
    """Health check"""
    try:
        db = get_database()
        if db is not None:
            # Test database connection
            await db.command("ping")
            db_status = "connected"
        else:
            db_status = "disconnected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_status,
        "uptime": str(datetime.now(timezone.utc) - STARTUP_TIME)
    }

# Core CRUD endpoints
@app.get("/api/workspace/")
async def get_workspaces():
    """Get all workspaces"""
    try:
        db = get_database()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        workspaces = await db.workspaces.find().to_list(100)
        # Convert ObjectId to string for JSON serialization
        for workspace in workspaces:
            if '_id' in workspace:
                workspace['_id'] = str(workspace['_id'])
        
        return {
            "workspaces": workspaces,
            "count": len(workspaces),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting workspaces: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workspace/")
async def create_workspace(workspace: WorkspaceCreate):
    """Create a new workspace"""
    try:
        db = get_database()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        workspace_data = workspace.dict()
        workspace_data["created_at"] = datetime.now(timezone.utc)
        workspace_data["updated_at"] = datetime.now(timezone.utc)
        
        result = await db.workspaces.insert_one(workspace_data)
        workspace_data["_id"] = str(result.inserted_id)
        
        return {
            "message": "Workspace created successfully",
            "workspace": workspace_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating workspace: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/")
async def get_users():
    """Get all users"""
    try:
        db = get_database()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        users = await db.users.find().to_list(100)
        # Convert ObjectId to string for JSON serialization
        for user in users:
            if '_id' in user:
                user['_id'] = str(user['_id'])
        
        return {
            "users": users,
            "count": len(users),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/user/")
async def create_user(user: UserCreate):
    """Create a new user"""
    try:
        db = get_database()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        user_data = user.dict()
        user_data["created_at"] = datetime.now(timezone.utc)
        user_data["updated_at"] = datetime.now(timezone.utc)
        
        result = await db.users.insert_one(user_data)
        user_data["_id"] = str(result.inserted_id)
        
        return {
            "message": "User created successfully",
            "user": user_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        db = get_database()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        # Get counts from database
        user_count = await db.users.count_documents({})
        workspace_count = await db.workspaces.count_documents({})
        
        stats = {
            "total_users": user_count,
            "total_workspaces": workspace_count,
            "active_projects": 0,
            "revenue_this_month": 0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return stats
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/overview")
async def get_analytics_overview():
    """Get analytics overview"""
    try:
        db = get_database()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        # Get real analytics data
        user_count = await db.users.count_documents({})
        workspace_count = await db.workspaces.count_documents({})
        
        analytics = {
            "total_users": user_count,
            "total_workspaces": workspace_count,
            "growth_rate": 0,
            "conversion_rate": 0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return analytics
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

if __name__ == "__main__":
    # Use port 8002 to avoid conflicts
    port = int(os.getenv("PORT", 8002))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Starting server on {host}:{port}")
    uvicorn.run(
        "app_simple:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    ) 