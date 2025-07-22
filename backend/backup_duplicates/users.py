"""
User API Routes
Professional Mewayz Platform
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any

from core.auth import get_current_active_user
from services.user_service import get_user_service
from services.analytics_service import get_analytics_service

router = APIRouter()

# Initialize service instances
user_service = get_user_service()
analytics_service = get_analytics_service()

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    profile: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None

@router.get("/profile")
async def get_user_profile(current_user: dict = Depends(get_current_active_user)):
    """Get user profile with real database operations"""
    try:
        profile = await user_service.get_user_profile(current_user["_id"])
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        return {
            "success": True,
            "data": profile
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch profile"
        )

@router.put("/profile")
async def update_user_profile(
    profile_data: ProfileUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Update user profile with real database operations"""
    try:
        # Convert to dict and remove None values
        update_data = profile_data.dict(exclude_none=True)
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields provided for update"
            )
        
        updated_profile = await user_service.update_user_profile(
            user_id=current_user["_id"],
            update_data=update_data
        )
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "data": updated_profile
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

@router.get("/stats")
async def get_user_statistics(current_user: dict = Depends(get_current_active_user)):
    """Get user statistics with real database calculations"""
    try:
        stats = await user_service.get_user_stats(current_user["_id"])
        
        return {
            "success": True,
            "data": stats
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user statistics"
        )

@router.get("/analytics")
async def get_user_analytics(
    days: int = 30,
    current_user: dict = Depends(get_current_active_user)
):
    """Get user analytics with real database operations"""
    try:
        analytics = await analytics_service.get_user_analytics(
            user_id=current_user["_id"],
            days=days
        )
        
        return {
            "success": True,
            "data": analytics
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user analytics"
        )