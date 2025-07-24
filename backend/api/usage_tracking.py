"""
Usage Tracking API
Handles real-time tracking of feature usage across all workspaces and bundles
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from core.auth import get_current_user
from services.usage_tracking_service import get_usage_tracking_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check for usage tracking system"""
    try:
        service = get_usage_tracking_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"Usage tracking health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

@router.post("/track")
async def track_usage(
    data: Dict[str, Any] = Body(..., description="Usage tracking data"),
    current_user: dict = Depends(get_current_user)
):
    """Track feature usage for workspace"""
    try:
        service = get_usage_tracking_service()
        data["user_id"] = current_user.get("id")
        
        result = await service.track_usage(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Track usage error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-limit")
async def check_usage_limit(
    data: Dict[str, Any] = Body(..., description="Limit check data"),
    current_user: dict = Depends(get_current_user)
):
    """Check if action is allowed within usage limits"""
    try:
        workspace_id = data.get("workspace_id")
        feature = data.get("feature")
        action_count = data.get("action_count", 1)
        
        if not workspace_id or not feature:
            raise HTTPException(status_code=400, detail="Workspace ID and feature are required")
        
        service = get_usage_tracking_service()
        result = await service.check_usage_limit(workspace_id, feature, action_count, current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=403, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Check usage limit error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/current/{workspace_id}")
async def get_current_usage(
    workspace_id: str = Path(..., description="Workspace ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get current usage statistics for workspace"""
    try:
        service = get_usage_tracking_service()
        result = await service.get_current_usage(workspace_id, current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current usage error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/limits/{workspace_id}")
async def get_workspace_limits(
    workspace_id: str = Path(..., description="Workspace ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get workspace usage limits based on subscription"""
    try:
        service = get_usage_tracking_service()
        result = await service.get_workspace_limits(workspace_id, current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get workspace limits error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/{workspace_id}")
async def get_usage_analytics(
    workspace_id: str = Path(..., description="Workspace ID"),
    period: str = Query("month", description="Time period: day, week, month, year"),
    current_user: dict = Depends(get_current_user)
):
    """Get usage analytics for workspace"""
    try:
        service = get_usage_tracking_service()
        result = await service.get_usage_analytics(workspace_id, period, current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get usage analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset/{workspace_id}")
async def reset_usage_counters(
    workspace_id: str = Path(..., description="Workspace ID"),
    data: Dict[str, Any] = Body(..., description="Reset data"),
    current_user: dict = Depends(get_current_user)
):
    """Reset usage counters (admin only)"""
    try:
        service = get_usage_tracking_service()
        
        # Check if user has admin permissions
        has_permission = await service.check_admin_permission(workspace_id, current_user.get("id"))
        if not has_permission:
            raise HTTPException(status_code=403, detail="Admin permissions required")
        
        data["workspace_id"] = workspace_id
        data["reset_by"] = current_user.get("id")
        
        result = await service.reset_usage_counters(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset usage counters error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/warnings/{workspace_id}")
async def get_usage_warnings(
    workspace_id: str = Path(..., description="Workspace ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get usage warnings for workspace (approaching limits)"""
    try:
        service = get_usage_tracking_service()
        result = await service.get_usage_warnings(workspace_id, current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get usage warnings error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upgrade-suggestion/{workspace_id}")
async def get_upgrade_suggestions(
    workspace_id: str = Path(..., description="Workspace ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get upgrade suggestions based on usage patterns"""
    try:
        service = get_usage_tracking_service()
        result = await service.get_upgrade_suggestions(workspace_id, current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get upgrade suggestions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))