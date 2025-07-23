"""
User API Routes

Provides API endpoints for user management functionality including
user profiles, preferences, and account management.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional, Any
from services.user_service import user_service
from core.auth import get_current_user
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/user", tags=["User Management"])

@router.get("/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile information"""
    user_id = current_user.get("user_id")
    return await user_service.get_user_profile(user_id)

@router.put("/profile")
async def update_user_profile(
    profile_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    user_id = current_user.get("user_id")
    return await user_service.update_user_profile(user_id, profile_data)

@router.get("/preferences")
async def get_user_preferences(current_user: dict = Depends(get_current_user)):
    """Get user preferences"""
    user_id = current_user.get("user_id")
    return await user_service.get_user_preferences(user_id)

@router.put("/preferences")
async def update_user_preferences(
    preferences: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Update user preferences"""
    user_id = current_user.get("user_id")
    return await user_service.update_user_preferences(user_id, preferences)

@router.post("/avatar")
async def upload_user_avatar(
    avatar_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Upload user avatar"""
    user_id = current_user.get("user_id")
    return await user_service.upload_user_avatar(user_id, avatar_data)

@router.get("/activity")
async def get_user_activity(
    current_user: dict = Depends(get_current_user),
    limit: Optional[int] = 20
):
    """Get user activity history"""
    user_id = current_user.get("user_id")
    return await user_service.get_user_activity(user_id, limit)

@router.post("/deactivate")
async def deactivate_account(
    deactivation_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Deactivate user account"""
    user_id = current_user.get("user_id")
    return await user_service.deactivate_account(user_id, deactivation_data)

@router.post("/password/change")
async def change_password(
    password_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Change user password"""
    user_id = current_user.get("user_id")
    return await user_service.change_password(user_id, password_data)

@router.get("/notifications/settings")
async def get_notification_settings(current_user: dict = Depends(get_current_user)):
    """Get user notification settings"""
    user_id = current_user.get("user_id")
    return await user_service.get_notification_settings(user_id)

@router.put("/notifications/settings")
async def update_notification_settings(
    settings: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Update notification settings"""
    user_id = current_user.get("user_id")
    return await user_service.update_notification_settings(user_id, settings)