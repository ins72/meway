"""
User API - Complete CRUD Operations
Production-ready user management
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from core.auth import get_current_user, get_current_admin
from services.user_service import get_user_service
from pydantic import BaseModel, EmailStr
import logging
from datetime import datetime
from bson import ObjectId

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for user operations
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = "user"

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    avatar_url: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    preferences: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    onboarding_completed: bool
    onboarding_step: int
    has_workspace: bool

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class UserPreferences(BaseModel):
    theme: Optional[str] = "light"
    language: Optional[str] = "en"
    timezone: Optional[str] = "UTC"
    notifications: Optional[Dict[str, bool]] = None

class EmailVerification(BaseModel):
    token: str

@router.get("/health")
async def health_check():
    """Health check for user service"""
    try:
        service = get_user_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"User health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

# ==================== USER CRUD OPERATIONS ====================

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(get_current_admin)
):
    """Create a new user (admin only)"""
    try:
        service = get_user_service()
        user = await service.create_user(user_data.dict())
        return user
    except Exception as e:
        logger.error(f"Create user error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[UserResponse])
async def list_users(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: dict = Depends(get_current_admin)
):
    """List all users (admin only)"""
    try:
        service = get_user_service()
        users = await service.list_users(
            limit=limit,
            offset=offset,
            search=search,
            role=role,
            is_active=is_active
        )
        return users
    except Exception as e:
        logger.error(f"List users error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user)
):
    """Get current user profile"""
    try:
        service = get_user_service()
        user = await service.get_user_by_id(str(current_user["_id"]))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str = Path(..., description="User ID"),
    current_user: dict = Depends(get_current_admin)
):
    """Get a specific user by ID (admin only)"""
    try:
        service = get_user_service()
        user = await service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update current user profile"""
    try:
        service = get_user_service()
        user = await service.update_user(
            user_id=str(current_user["_id"]),
            update_data=user_data.dict(exclude_unset=True)
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update current user error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str = Path(..., description="User ID"),
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_admin)
):
    """Update a user (admin only)"""
    try:
        service = get_user_service()
        user = await service.update_user(
            user_id=user_id,
            update_data=user_data.dict(exclude_unset=True)
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}")
async def delete_user(
    user_id: str = Path(..., description="User ID"),
    current_user: dict = Depends(get_current_admin)
):
    """Delete a user (admin only)"""
    try:
        service = get_user_service()
        success = await service.delete_user(user_id=user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        return {"success": True, "message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete user error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== PASSWORD MANAGEMENT ====================

@router.post("/me/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    """Change current user password"""
    try:
        service = get_user_service()
        success = await service.change_password(
            user_id=str(current_user["_id"]),
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        if not success:
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        return {"success": True, "message": "Password changed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/reset-password")
async def reset_user_password(
    user_id: str = Path(..., description="User ID"),
    current_user: dict = Depends(get_current_admin)
):
    """Reset user password (admin only)"""
    try:
        service = get_user_service()
        new_password = await service.reset_password(user_id=user_id)
        return {
            "success": True, 
            "message": "Password reset successfully",
            "new_password": new_password
        }
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== USER PREFERENCES ====================

@router.get("/me/preferences")
async def get_user_preferences(
    current_user: dict = Depends(get_current_user)
):
    """Get current user preferences"""
    try:
        service = get_user_service()
        preferences = await service.get_preferences(str(current_user["_id"]))
        return preferences
    except Exception as e:
        logger.error(f"Get preferences error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/me/preferences")
async def update_user_preferences(
    preferences: UserPreferences,
    current_user: dict = Depends(get_current_user)
):
    """Update current user preferences"""
    try:
        service = get_user_service()
        updated_preferences = await service.update_preferences(
            user_id=str(current_user["_id"]),
            preferences=preferences.dict(exclude_unset=True)
        )
        return updated_preferences
    except Exception as e:
        logger.error(f"Update preferences error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== USER ACTIVITY ====================

@router.get("/me/activity")
async def get_user_activity(
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get current user activity log"""
    try:
        service = get_user_service()
        activity = await service.get_activity(
            user_id=str(current_user["_id"]),
            limit=limit
        )
        return activity
    except Exception as e:
        logger.error(f"Get activity error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/activity")
async def get_user_activity_admin(
    user_id: str = Path(..., description="User ID"),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_admin)
):
    """Get user activity log (admin only)"""
    try:
        service = get_user_service()
        activity = await service.get_activity(
            user_id=user_id,
            limit=limit
        )
        return activity
    except Exception as e:
        logger.error(f"Get user activity error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== USER VERIFICATION ====================

@router.post("/me/verify-email")
async def verify_email(
    verification_data: EmailVerification,
    current_user: dict = Depends(get_current_user)
):
    """Verify user email"""
    try:
        service = get_user_service()
        success = await service.verify_email(
            user_id=str(current_user["_id"]),
            token=verification_data.token
        )
        if not success:
            raise HTTPException(status_code=400, detail="Invalid verification token")
        return {"success": True, "message": "Email verified successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verify email error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/me/resend-verification")
async def resend_verification_email(
    current_user: dict = Depends(get_current_user)
):
    """Resend verification email"""
    try:
        service = get_user_service()
        success = await service.resend_verification_email(str(current_user["_id"]))
        if not success:
            raise HTTPException(status_code=400, detail="Failed to send verification email")
        return {"success": True, "message": "Verification email sent"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resend verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ADMIN OPERATIONS ====================

@router.post("/{user_id}/activate")
async def activate_user(
    user_id: str = Path(..., description="User ID"),
    current_user: dict = Depends(get_current_admin)
):
    """Activate a user (admin only)"""
    try:
        service = get_user_service()
        success = await service.activate_user(user_id=user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        return {"success": True, "message": "User activated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Activate user error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: str = Path(..., description="User ID"),
    current_user: dict = Depends(get_current_admin)
):
    """Deactivate a user (admin only)"""
    try:
        service = get_user_service()
        success = await service.deactivate_user(user_id=user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        return {"success": True, "message": "User deactivated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deactivate user error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_user_stats(
    current_user: dict = Depends(get_current_admin)
):
    """Get user statistics (admin only)"""
    try:
        service = get_user_service()
        stats = await service.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Get user stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))