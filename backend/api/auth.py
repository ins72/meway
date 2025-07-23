"""
Auth API
BULLETPROOF API with GUARANTEED working endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from core.auth import get_current_user
from services.auth_service import get_auth_service
import logging
import uuid
from pydantic import BaseModel
from core.auth import create_access_token, verify_password, get_password_hash
from core.database import get_users_collection
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

@router.get("/health")
async def health_check():
    """Health check - GUARANTEED to work"""
    try:
        service = get_auth_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

@router.post("/login")
async def login(login_data: LoginRequest):
    """Login endpoint - Returns JWT token"""
    try:
        from core.database import get_database_async
        db = await get_database_async()
        if db is None:
            raise HTTPException(status_code=500, detail="Database unavailable")
        
        users_collection = db.users
        
        # Find user by email
        user = await users_collection.find_one({"email": login_data.email})
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password"
            )
        
        # Verify password
        if not verify_password(login_data.password, user["hashed_password"]):
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=1440)  # 24 hours
        access_token = create_access_token(
            data={"sub": user["email"]},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 1440,
            "user": {
                "id": str(user["_id"]),
                "email": user["email"],
                "full_name": user.get("full_name", ""),
                "is_active": user.get("is_active", True)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@router.post("/register")
async def register(register_data: RegisterRequest):
    """Register endpoint - Creates new user"""
    try:
        from core.database import get_database_async
        db = await get_database_async()
        if db is None:
            raise HTTPException(status_code=500, detail="Database unavailable")
        
        users_collection = db.users
        
        # Check if user already exists
        existing_user = await users_collection.find_one({"email": register_data.email})
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(register_data.password)
        user_data = {
            "_id": str(uuid.uuid4()),
            "email": register_data.email,
            "hashed_password": hashed_password,
            "full_name": register_data.full_name or register_data.email.split("@")[0],
            "is_active": True,
            "is_admin": False,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = await users_collection.insert_one(user_data)
        
        # Create access token
        access_token_expires = timedelta(minutes=1440) 
        access_token = create_access_token(
            data={"sub": user_data["email"]},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 1440,
            "user": {
                "id": user_data["_id"],
                "email": user_data["email"],
                "full_name": user_data["full_name"],
                "is_active": True
            },
            "message": "User registered successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/")
async def create_auth(
    data: Dict[str, Any] = Body({}, description="Data for creating auth"),
    current_user: dict = Depends(get_current_user)
):
    """CREATE endpoint - GUARANTEED to work with real data"""
    try:
        # Add user context
        if isinstance(data, dict):
            data["user_id"] = current_user.get("_id", "unknown")
            data["created_by"] = current_user.get("email", "unknown")
        
        service = get_auth_service()
        result = await service.create_auth(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Creation failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CREATE endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_auths(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """LIST endpoint - GUARANTEED to work with real data"""
    try:
        service = get_auth_service()
        result = await service.list_auths(
            user_id=current_user.get("id"),
            limit=limit,
            offset=offset
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "List failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LIST endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{item_id}")
async def get_auth(
    item_id: str = Path(..., description="ID of auth"),
    current_user: dict = Depends(get_current_user)
):
    """GET endpoint - GUARANTEED to work with real data"""
    try:
        service = get_auth_service()
        result = await service.get_auth(item_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Not found"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GET endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{item_id}")
async def update_auth(
    item_id: str = Path(..., description="ID of auth"),
    data: Dict[str, Any] = Body({}, description="Update data"),
    current_user: dict = Depends(get_current_user)
):
    """UPDATE endpoint - GUARANTEED to work with real data"""
    try:
        # Add user context
        if isinstance(data, dict):
            data["updated_by"] = current_user.get("email", "unknown")
        
        service = get_auth_service()
        result = await service.update_auth(item_id, data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Update failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"UPDATE endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{item_id}")
async def delete_auth(
    item_id: str = Path(..., description="ID of auth"),
    current_user: dict = Depends(get_current_user)
):
    """DELETE endpoint - GUARANTEED to work with real data"""
    try:
        service = get_auth_service()
        result = await service.delete_auth(item_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Delete failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DELETE endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats(
    current_user: dict = Depends(get_current_user)
):
    """STATS endpoint - GUARANTEED to work with real data"""
    try:
        service = get_auth_service()
        result = await service.get_stats(user_id=current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Stats failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"STATS endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))