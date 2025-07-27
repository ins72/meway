#!/usr/bin/env python3
"""
WORKING APPLICATION
Complete CRUD operations with in-memory storage
Can be easily upgraded to MongoDB later
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
from typing import Optional, Dict, Any, List
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
STARTUP_TIME = datetime.now(timezone.utc)

# In-memory storage (can be replaced with MongoDB later)
workspaces_db = []
users_db = []

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
    description="Complete CRUD operations with in-memory storage",
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
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "in-memory",
        "uptime": str(datetime.now(timezone.utc) - STARTUP_TIME)
    }

# Core CRUD endpoints
@app.get("/api/workspace/")
async def get_workspaces():
    """Get all workspaces"""
    try:
        return {
            "workspaces": workspaces_db,
            "count": len(workspaces_db),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting workspaces: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workspace/")
async def create_workspace(workspace: WorkspaceCreate):
    """Create a new workspace"""
    try:
        workspace_data = workspace.dict()
        workspace_data["id"] = str(uuid.uuid4())
        workspace_data["created_at"] = datetime.now(timezone.utc).isoformat()
        workspace_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        workspaces_db.append(workspace_data)
        
        return {
            "message": "Workspace created successfully",
            "workspace": workspace_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating workspace: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workspace/{workspace_id}")
async def get_workspace(workspace_id: str):
    """Get a specific workspace"""
    try:
        for workspace in workspaces_db:
            if workspace["id"] == workspace_id:
                return workspace
        raise HTTPException(status_code=404, detail="Workspace not found")
    except Exception as e:
        logger.error(f"Error getting workspace: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/workspace/{workspace_id}")
async def update_workspace(workspace_id: str, workspace: WorkspaceCreate):
    """Update a workspace"""
    try:
        for i, existing_workspace in enumerate(workspaces_db):
            if existing_workspace["id"] == workspace_id:
                workspace_data = workspace.dict()
                workspace_data["id"] = workspace_id
                workspace_data["updated_at"] = datetime.now(timezone.utc).isoformat()
                workspace_data["created_at"] = existing_workspace["created_at"]
                
                workspaces_db[i] = workspace_data
                
                return {
                    "message": "Workspace updated successfully",
                    "workspace": workspace_data,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        raise HTTPException(status_code=404, detail="Workspace not found")
    except Exception as e:
        logger.error(f"Error updating workspace: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/workspace/{workspace_id}")
async def delete_workspace(workspace_id: str):
    """Delete a workspace"""
    try:
        for i, workspace in enumerate(workspaces_db):
            if workspace["id"] == workspace_id:
                deleted_workspace = workspaces_db.pop(i)
                return {
                    "message": "Workspace deleted successfully",
                    "workspace": deleted_workspace,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        raise HTTPException(status_code=404, detail="Workspace not found")
    except Exception as e:
        logger.error(f"Error deleting workspace: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/")
async def get_users():
    """Get all users"""
    try:
        return {
            "users": users_db,
            "count": len(users_db),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/user/")
async def create_user(user: UserCreate):
    """Create a new user"""
    try:
        user_data = user.dict()
        user_data["id"] = str(uuid.uuid4())
        user_data["created_at"] = datetime.now(timezone.utc).isoformat()
        user_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        users_db.append(user_data)
        
        return {
            "message": "User created successfully",
            "user": user_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/{user_id}")
async def get_user(user_id: str):
    """Get a specific user"""
    try:
        for user in users_db:
            if user["id"] == user_id:
                return user
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/user/{user_id}")
async def update_user(user_id: str, user: UserCreate):
    """Update a user"""
    try:
        for i, existing_user in enumerate(users_db):
            if existing_user["id"] == user_id:
                user_data = user.dict()
                user_data["id"] = user_id
                user_data["updated_at"] = datetime.now(timezone.utc).isoformat()
                user_data["created_at"] = existing_user["created_at"]
                
                users_db[i] = user_data
                
                return {
                    "message": "User updated successfully",
                    "user": user_data,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/user/{user_id}")
async def delete_user(user_id: str):
    """Delete a user"""
    try:
        for i, user in enumerate(users_db):
            if user["id"] == user_id:
                deleted_user = users_db.pop(i)
                return {
                    "message": "User deleted successfully",
                    "user": deleted_user,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        stats = {
            "total_users": len(users_db),
            "total_workspaces": len(workspaces_db),
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
        analytics = {
            "total_users": len(users_db),
            "total_workspaces": len(workspaces_db),
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
        "WORKING_APP:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    ) 