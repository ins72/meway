"""
Workspace Subscription Management API
Handle workspace-specific subscriptions and billing
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from core.auth import get_current_user
from services.workspace_subscription_service import get_workspace_subscription_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check for workspace subscription management"""
    try:
        service = get_workspace_subscription_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

@router.post("/workspace/{workspace_id}/subscription")
async def create_workspace_subscription(
    workspace_id: str = Path(..., description="Workspace ID"),
    data: Dict[str, Any] = Body(..., description="Subscription data"),
    current_user: dict = Depends(get_current_user)
):
    """Create subscription for workspace"""
    try:
        # Check if user has owner/admin role in workspace
        service = get_workspace_subscription_service()
        has_permission = await service.check_billing_permission(workspace_id, current_user.get("id"))
        
        if not has_permission:
            raise HTTPException(status_code=403, detail="Insufficient permissions for billing management")
        
        data["workspace_id"] = workspace_id
        data["created_by"] = current_user.get("id")
        
        result = await service.create_workspace_subscription(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create workspace subscription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workspace/{workspace_id}/subscription")
async def get_workspace_subscription(
    workspace_id: str = Path(..., description="Workspace ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get workspace subscription details"""
    try:
        service = get_workspace_subscription_service()
        result = await service.get_workspace_subscription(workspace_id, current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get workspace subscription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/workspace/{workspace_id}/subscription/bundle")
async def modify_workspace_bundles(
    workspace_id: str = Path(..., description="Workspace ID"),
    data: Dict[str, Any] = Body(..., description="Bundle modification data"),
    current_user: dict = Depends(get_current_user)
):
    """Add or remove bundles from workspace subscription"""
    try:
        service = get_workspace_subscription_service()
        has_permission = await service.check_billing_permission(workspace_id, current_user.get("id"))
        
        if not has_permission:
            raise HTTPException(status_code=403, detail="Insufficient permissions for billing management")
        
        data["workspace_id"] = workspace_id
        data["modified_by"] = current_user.get("id")
        
        result = await service.modify_workspace_bundles(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Modify workspace bundles error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workspace/{workspace_id}/usage-limits")
async def get_workspace_usage_limits(
    workspace_id: str = Path(..., description="Workspace ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get workspace usage limits and current usage"""
    try:
        service = get_workspace_subscription_service()
        result = await service.get_workspace_usage_limits(workspace_id, current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get workspace usage limits error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workspace/{workspace_id}/upgrade")
async def upgrade_workspace_subscription(
    workspace_id: str = Path(..., description="Workspace ID"),
    data: Dict[str, Any] = Body(..., description="Upgrade data"),
    current_user: dict = Depends(get_current_user)
):
    """Upgrade workspace subscription"""
    try:
        service = get_workspace_subscription_service()
        has_permission = await service.check_billing_permission(workspace_id, current_user.get("id"))
        
        if not has_permission:
            raise HTTPException(status_code=403, detail="Insufficient permissions for billing management")
        
        data["workspace_id"] = workspace_id
        data["upgraded_by"] = current_user.get("id")
        
        result = await service.upgrade_workspace_subscription(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upgrade workspace subscription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workspace/{workspace_id}/feature-access")
async def check_feature_access(
    workspace_id: str = Path(..., description="Workspace ID"),
    feature: str = Query(..., description="Feature to check"),
    current_user: dict = Depends(get_current_user)
):
    """Check if workspace has access to specific feature"""
    try:
        service = get_workspace_subscription_service()
        result = await service.check_feature_access(workspace_id, feature, current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=403, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Check feature access error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workspace/{workspace_id}/billing-history")
async def get_workspace_billing_history(
    workspace_id: str = Path(..., description="Workspace ID"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Get workspace billing history"""
    try:
        service = get_workspace_subscription_service()
        has_permission = await service.check_billing_permission(workspace_id, current_user.get("id"))
        
        if not has_permission:
            raise HTTPException(status_code=403, detail="Insufficient permissions to view billing")
        
        result = await service.get_workspace_billing_history(workspace_id, limit, offset)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get workspace billing history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workspace/{workspace_id}/downgrade")
async def downgrade_workspace_subscription(
    workspace_id: str = Path(..., description="Workspace ID"),
    data: Dict[str, Any] = Body(..., description="Downgrade data"),
    current_user: dict = Depends(get_current_user)
):
    """Downgrade workspace subscription"""
    try:
        service = get_workspace_subscription_service()
        has_permission = await service.check_billing_permission(workspace_id, current_user.get("id"))
        
        if not has_permission:
            raise HTTPException(status_code=403, detail="Insufficient permissions for billing management")
        
        data["workspace_id"] = workspace_id
        data["downgraded_by"] = current_user.get("id")
        
        result = await service.downgrade_workspace_subscription(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Downgrade workspace subscription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workspace/{workspace_id}/cancel")
async def cancel_workspace_subscription(
    workspace_id: str = Path(..., description="Workspace ID"),
    data: Dict[str, Any] = Body(..., description="Cancellation data"),
    current_user: dict = Depends(get_current_user)
):
    """Cancel workspace subscription"""
    try:
        service = get_workspace_subscription_service()
        has_permission = await service.check_billing_permission(workspace_id, current_user.get("id"))
        
        if not has_permission:
            raise HTTPException(status_code=403, detail="Insufficient permissions for billing management")
        
        data["workspace_id"] = workspace_id
        data["cancelled_by"] = current_user.get("id")
        
        result = await service.cancel_workspace_subscription(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cancel workspace subscription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pricing/calculate")
async def calculate_pricing(
    bundles: str = Query(..., description="Comma-separated bundle names"),
    billing_cycle: str = Query("monthly", description="monthly or yearly")
):
    """Calculate pricing for bundle combination"""
    try:
        service = get_workspace_subscription_service()
        bundle_list = [b.strip() for b in bundles.split(",")]
        
        result = await service.calculate_pricing(bundle_list, billing_cycle)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Calculate pricing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bundles/available")
async def get_available_bundles():
    """Get all available bundles and their features"""
    try:
        service = get_workspace_subscription_service()
        result = await service.get_available_bundles()
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
            
    except Exception as e:
        logger.error(f"Get available bundles error: {e}")
        raise HTTPException(status_code=500, detail=str(e))