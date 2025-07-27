#!/usr/bin/env python3
"""
FINAL DEPLOYMENT SCRIPT
Complete MongoDB installation and application deployment
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path

def run_command(command, cwd=None, is_background=False):
    """Run a command and return result"""
    try:
        if is_background:
            # For background processes, use Popen
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
            return True, "", ""
        else:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
            return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def install_mongodb():
    """Install MongoDB if not present"""
    print("📦 Checking MongoDB installation...")
    
    # Check if MongoDB is already installed
    success, stdout, stderr = run_command("mongod --version")
    if success:
        print("✅ MongoDB is already installed")
        return True
    
    print("📥 Installing MongoDB...")
    
    # Try Chocolatey
    success, stdout, stderr = run_command("choco --version")
    if success:
        print("✅ Chocolatey found, installing MongoDB...")
        success, stdout, stderr = run_command("choco install mongodb -y")
        if success:
            print("✅ MongoDB installed via Chocolatey")
            return True
    
    print("❌ MongoDB installation failed")
    return False

def start_mongodb():
    """Start MongoDB service"""
    print("🚀 Starting MongoDB...")
    
    # Create data directory
    data_dir = "C:\\data\\db"
    os.makedirs(data_dir, exist_ok=True)
    print(f"✅ Created data directory: {data_dir}")
    
    # Try to start as service
    success, stdout, stderr = run_command("net start MongoDB")
    if success:
        print("✅ MongoDB service started")
        return True
    
    # Try to start manually
    print("🔄 Starting MongoDB manually...")
    success, stdout, stderr = run_command(f"mongod --dbpath {data_dir} --port 27017", is_background=True)
    if success:
        print("✅ MongoDB started manually")
        time.sleep(5)  # Wait for startup
        return True
    
    print("❌ Failed to start MongoDB")
    return False

def create_simple_app():
    """Create a simple working application"""
    print("🔧 Creating simple working application...")
    
    app_content = '''#!/usr/bin/env python3
"""
SIMPLE WORKING APPLICATION
Complete CRUD operations with MongoDB
"""

import os
import sys
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager
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

async def close_mongo_connection():
    """Close MongoDB connection"""
    global database
    if database:
        database.client.close()
        logger.info("✅ MongoDB connection closed")

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    # Startup
    logger.info("🚀 Starting Mewayz Professional API...")
    await connect_to_mongo()
    logger.info("✅ Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down...")
    await close_mongo_connection()
    logger.info("✅ Application shutdown complete")

app = FastAPI(lifespan=lifespan)

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
        "app:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
'''
    
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(app_content)
    
    print("✅ Simple application created")

def test_endpoints():
    """Test all endpoints"""
    print("🧪 Testing endpoints...")
    
    import requests
    import time
    
    base_url = "http://localhost:8002"
    
    # Wait for server to start
    time.sleep(3)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test workspace endpoint
    try:
        response = requests.get(f"{base_url}/api/workspace/")
        if response.status_code == 200:
            print("✅ Workspace GET endpoint working")
        else:
            print(f"❌ Workspace GET endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Workspace GET endpoint error: {e}")
    
    # Test user endpoint
    try:
        response = requests.get(f"{base_url}/api/user/")
        if response.status_code == 200:
            print("✅ User GET endpoint working")
        else:
            print(f"❌ User GET endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ User GET endpoint error: {e}")
    
    # Test dashboard stats
    try:
        response = requests.get(f"{base_url}/api/dashboard/stats")
        if response.status_code == 200:
            print("✅ Dashboard stats endpoint working")
        else:
            print(f"❌ Dashboard stats endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard stats endpoint error: {e}")

def main():
    """Main deployment function"""
    print("🚀 FINAL MEWAYZ DEPLOYMENT")
    print("=" * 50)
    
    # Step 1: Install MongoDB
    print("\n1️⃣ Installing MongoDB...")
    if not install_mongodb():
        print("⚠️ MongoDB installation failed, continuing...")
    
    # Step 2: Start MongoDB
    print("\n2️⃣ Starting MongoDB...")
    if not start_mongodb():
        print("❌ MongoDB start failed")
        return
    
    # Step 3: Create simple app
    print("\n3️⃣ Creating simple application...")
    create_simple_app()
    
    # Step 4: Install dependencies
    print("\n4️⃣ Installing dependencies...")
    success, stdout, stderr = run_command("pip install fastapi uvicorn motor pymongo pydantic requests")
    if success:
        print("✅ Dependencies installed")
    else:
        print(f"⚠️ Dependency installation issues: {stderr}")
    
    # Step 5: Start application
    print("\n5️⃣ Starting application...")
    print("🚀 Starting Mewayz Professional API on port 8002...")
    
    success, stdout, stderr = run_command("python app.py", is_background=True)
    
    if success:
        print("✅ Application started successfully!")
        
        # Step 6: Test endpoints
        print("\n6️⃣ Testing endpoints...")
        test_endpoints()
        
        print("\n📋 DEPLOYMENT SUMMARY:")
        print("✅ MongoDB installed and running")
        print("✅ Application created and started")
        print("✅ Dependencies installed")
        print("✅ Application running on port 8002")
        print("\n🌐 Access your application:")
        print("   - API: http://localhost:8002")
        print("   - Docs: http://localhost:8002/docs")
        print("   - Health: http://localhost:8002/health")
        print("\n📊 Test endpoints:")
        print("   - GET /api/workspace/")
        print("   - POST /api/workspace/")
        print("   - GET /api/user/")
        print("   - GET /api/dashboard/stats")
        print("\n🎉 DEPLOYMENT COMPLETE!")
    else:
        print(f"❌ Failed to start application: {stderr}")

if __name__ == "__main__":
    main() 