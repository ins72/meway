"""
Admin Plan Management API
Comprehensive plan control: pricing, features, limits, availability, launch specials
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from core.auth import get_current_user
from services.admin_plan_management_service import get_admin_plan_management_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check for admin plan management"""
    try:
        service = get_admin_plan_management_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"Admin plan management health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

@router.get("/plans")
async def get_all_plans(
    current_user: dict = Depends(get_current_user)
):
    """Get all plans with pricing, features, limits and availability"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_plan_management_service()
        result = await service.get_all_plans()
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get all plans error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plan/{plan_name}")
async def get_plan_details(
    plan_name: str = Path(..., description="Plan name"),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed plan configuration"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_plan_management_service()
        result = await service.get_plan_details(plan_name)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get plan details error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plan/{plan_name}/pricing")
async def update_plan_pricing(
    plan_name: str = Path(..., description="Plan name"),
    data: Dict[str, Any] = Body(..., description="Pricing update data"),
    current_user: dict = Depends(get_current_user)
):
    """Update pricing for a plan"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_plan_management_service()
        data["plan_name"] = plan_name
        data["updated_by"] = current_user.get("id")
        
        result = await service.update_plan_pricing(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update plan pricing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plan/{plan_name}/features")
async def update_plan_features(
    plan_name: str = Path(..., description="Plan name"),
    data: Dict[str, Any] = Body(..., description="Features update data"),
    current_user: dict = Depends(get_current_user)
):
    """Update features included in a plan"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_plan_management_service()
        data["plan_name"] = plan_name
        data["updated_by"] = current_user.get("id")
        
        result = await service.update_plan_features(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update plan features error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plan/{plan_name}/limits")
async def update_plan_limits(
    plan_name: str = Path(..., description="Plan name"),
    data: Dict[str, Any] = Body(..., description="Limits update data"),
    current_user: dict = Depends(get_current_user)
):
    """Update usage limits for a plan"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_plan_management_service()
        data["plan_name"] = plan_name
        data["updated_by"] = current_user.get("id")
        
        result = await service.update_plan_limits(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update plan limits error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plan/{plan_name}/status")
async def update_plan_status(
    plan_name: str = Path(..., description="Plan name"),
    data: Dict[str, Any] = Body(..., description="Status update data"),
    current_user: dict = Depends(get_current_user)
):
    """Enable or disable a plan"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        action = data.get("action")  # "enable" or "disable"
        if action not in ["enable", "disable"]:
            raise HTTPException(status_code=400, detail="Action must be 'enable' or 'disable'")
        
        service = get_admin_plan_management_service()
        data["plan_name"] = plan_name
        data["modified_by"] = current_user.get("id")
        
        result = await service.update_plan_status(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update plan status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plan/{plan_name}/launch-pricing")
async def update_plan_launch_pricing(
    plan_name: str = Path(..., description="Plan name"),
    data: Dict[str, Any] = Body(..., description="Launch pricing data"),
    current_user: dict = Depends(get_current_user)
):
    """Update launch/promotional pricing for a plan"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_plan_management_service()
        data["plan_name"] = plan_name
        data["updated_by"] = current_user.get("id")
        
        result = await service.update_plan_launch_pricing(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update plan launch pricing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plan")
async def create_new_plan(
    data: Dict[str, Any] = Body(..., description="New plan data"),
    current_user: dict = Depends(get_current_user)
):
    """Create a new plan"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_plan_management_service()
        data["created_by"] = current_user.get("id")
        
        result = await service.create_new_plan(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create new plan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/plan/{plan_name}")
async def delete_plan(
    plan_name: str = Path(..., description="Plan name"),
    current_user: dict = Depends(get_current_user)
):
    """Delete a plan (if no active subscriptions)"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_plan_management_service()
        result = await service.delete_plan(plan_name, current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete plan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk-update")
async def bulk_plan_update(
    data: Dict[str, Any] = Body(..., description="Bulk update data"),
    current_user: dict = Depends(get_current_user)
):
    """Update multiple plans at once"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_plan_management_service()
        data["updated_by"] = current_user.get("id")
        
        result = await service.bulk_plan_update(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk plan update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plan-analytics")
async def get_plan_analytics(
    current_user: dict = Depends(get_current_user)
):
    """Get analytics on plan performance"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_plan_management_service()
        result = await service.get_plan_analytics()
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get plan analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plan/{plan_name}/subscriptions")
async def get_plan_subscriptions(
    plan_name: str = Path(..., description="Plan name"),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get workspaces subscribed to a specific plan"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_plan_management_service()
        result = await service.get_plan_subscriptions(plan_name, limit)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get plan subscriptions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plan-change-history")
async def get_plan_change_history(
    plan_name: str = Query(None, description="Filter by plan name"),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get history of plan changes"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_plan_management_service()
        result = await service.get_plan_change_history(plan_name, limit)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get plan change history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))