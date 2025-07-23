"""
Analytics API Routes
Professional Mewayz Platform
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any

from core.auth import get_current_active_user
from services.analytics_service import get_analytics_service
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
import uuid
from datetime import datetime

router = APIRouter()

# Initialize service instance
analytics_service = get_analytics_service()

class EventData(BaseModel):
    event_type: str
    properties: Optional[Dict[str, Any]] = {}
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None

@router.get("/overview")
async def get_analytics_overview(
    days: int = 7,
    current_user: dict = Depends(get_current_active_user)
):
    """Get analytics overview with real database calculations"""
    try:
        overview = await analytics_service.get_user_analytics_overview(
            current_user["_id"], days
        )
        
        return {
            "success": True,
            "data": overview
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch analytics overview: {str(e)}"
        )

@router.post("/track")
async def track_event(
    event_data: EventData,
    current_user: dict = Depends(get_current_active_user)
):
    """Track analytics event with real database operations"""
    try:
        # Add user context to event
        event_dict = event_data.dict()
        event_dict["user_id"] = current_user["_id"]
        
        event_id = await analytics_service.track_event(event_dict)
        
        return {
            "success": True,
            "message": "Event tracked successfully",
            "event_id": event_id
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track event"
        )

@router.get("/user/{user_id}")
async def get_user_analytics(
    user_id: str,
    days: int = 30,
    current_user: dict = Depends(get_current_active_user)
):
    """Get analytics for specific user (admin only or own data)"""
    try:
        # Check if user is requesting their own data or is admin
        if user_id != current_user["_id"] and not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        analytics = await analytics_service.get_user_analytics(user_id, days)
        
        return {
            "success": True,
            "data": analytics
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user analytics"
        )

@router.get("/workspace/{workspace_id}")
async def get_workspace_analytics(
    workspace_id: str,
    days: int = 30,
    current_user: dict = Depends(get_current_active_user)
):
    """Get analytics for specific workspace"""
    try:
        analytics = await analytics_service.get_workspace_analytics(workspace_id, days)
        
        return {
            "success": True,
            "data": analytics
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch workspace analytics"
        )

@router.get("/platform/overview")
async def get_platform_overview(current_user: dict = Depends(get_current_active_user)):
    """Get platform-wide analytics (admin only)"""
    try:
        if not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        overview = await analytics_service.get_platform_overview()
        
        return {
            "success": True,
            "data": overview
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch platform overview"
        )

@router.get("/features/usage")
async def get_feature_usage_analytics(
    user_id: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Get feature usage analytics"""
    try:
        # If user_id specified, check permissions
        if user_id and user_id != current_user["_id"] and not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Use current user if no user_id specified
        target_user_id = user_id or current_user["_id"]
        
        analytics = await analytics_service.get_feature_usage_analytics(target_user_id)
        
        return {
            "success": True,
            "data": analytics
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch feature usage analytics"
        )