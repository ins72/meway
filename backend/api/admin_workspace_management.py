"""
Admin Workspace Management API
Provides admin-level workspace and subscription management endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from core.auth import get_current_user
from services.admin_workspace_management_service import get_admin_workspace_management_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check for admin workspace management"""
    try:
        service = get_admin_workspace_management_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"Admin workspace management health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

@router.get("/workspaces")
async def get_all_workspaces(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    plan_name: str = Query(None, description="Filter by plan name"),
    status: str = Query(None, description="Filter by subscription status"),
    owner_email: str = Query(None, description="Filter by owner email"),
    current_user: dict = Depends(get_current_user)
):
    """Get all workspaces with subscription details for admin view"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_workspace_management_service()
        
        # Build filters
        filters = {}
        if plan_name:
            filters["plan_name"] = plan_name
        if status:
            filters["status"] = status
        if owner_email:
            filters["owner_email"] = owner_email
        
        result = await service.get_all_workspaces(limit, offset, filters)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get all workspaces error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workspaces/search")
async def search_workspaces(
    search_criteria: Dict[str, Any] = Body(..., description="Search criteria"),
    current_user: dict = Depends(get_current_user)
):
    """Advanced workspace search with multiple criteria"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_workspace_management_service()
        result = await service.search_workspaces(search_criteria)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search workspaces error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workspace/{workspace_id}/override-subscription")
async def override_workspace_subscription(
    workspace_id: str = Path(..., description="Workspace ID"),
    override_data: Dict[str, Any] = Body(..., description="Override configuration"),
    current_user: dict = Depends(get_current_user)
):
    """Admin override of workspace subscription settings"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_workspace_management_service()
        result = await service.override_workspace_subscription(
            workspace_id, override_data, current_user.get("id")
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Override workspace subscription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workspace/{workspace_id}/comp-account")
async def grant_comp_account(
    workspace_id: str = Path(..., description="Workspace ID"),
    comp_data: Dict[str, Any] = Body(..., description="Complimentary account configuration"),
    current_user: dict = Depends(get_current_user)
):
    """Grant complimentary account access to workspace"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_workspace_management_service()
        result = await service.grant_comp_account(
            workspace_id, comp_data, current_user.get("id")
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Grant comp account error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workspace/{workspace_id}/manual-discount")
async def apply_manual_discount(
    workspace_id: str = Path(..., description="Workspace ID"),
    discount_data: Dict[str, Any] = Body(..., description="Discount configuration"),
    current_user: dict = Depends(get_current_user)
):
    """Apply manual discount to workspace subscription"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_workspace_management_service()
        result = await service.apply_manual_discount(
            workspace_id, discount_data, current_user.get("id")
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Apply manual discount error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workspace/{workspace_id}/pause")
async def pause_subscription(
    workspace_id: str = Path(..., description="Workspace ID"),
    pause_data: Dict[str, Any] = Body(..., description="Pause configuration"),
    current_user: dict = Depends(get_current_user)
):
    """Pause workspace subscription"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_workspace_management_service()
        result = await service.pause_subscription(
            workspace_id, pause_data, current_user.get("id")
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pause subscription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workspace/{workspace_id}/resume")
async def resume_subscription(
    workspace_id: str = Path(..., description="Workspace ID"),
    resume_data: Dict[str, Any] = Body(..., description="Resume configuration"),
    current_user: dict = Depends(get_current_user)
):
    """Resume paused workspace subscription"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_workspace_management_service()
        result = await service.resume_subscription(
            workspace_id, resume_data, current_user.get("id")
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume subscription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin-actions")
async def get_admin_action_history(
    workspace_id: str = Query(None, description="Filter by workspace ID"),
    admin_user_id: str = Query(None, description="Filter by admin user ID"),
    days_back: int = Query(30, ge=1, le=365, description="Days back to search"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
    current_user: dict = Depends(get_current_user)
):
    """Get history of admin actions"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_workspace_management_service()
        result = await service.get_admin_action_history(
            workspace_id, admin_user_id, days_back, limit
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get admin action history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workspace/{workspace_id}")
async def get_workspace_admin_view(
    workspace_id: str = Path(..., description="Workspace ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed workspace information for admin view"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_workspace_management_service()
        
        # Get workspace with admin enhancements
        result = await service.search_workspaces({"workspace_id": workspace_id})
        
        if result.get("success") and result.get("search_results"):
            workspace = result["search_results"][0]
            return {
                "success": True,
                "workspace": workspace,
                "admin_capabilities": [
                    "subscription_override",
                    "comp_account_grant",
                    "manual_discount",
                    "pause_resume",
                    "billing_adjustment"
                ]
            }
        else:
            raise HTTPException(status_code=404, detail="Workspace not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get workspace admin view error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/overview")
async def get_admin_analytics_overview(
    current_user: dict = Depends(get_current_user)
):
    """Get overview analytics for admin dashboard"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_workspace_management_service()
        
        # Get comprehensive overview
        result = await service.get_all_workspaces(limit=1000)  # Get larger sample for analytics
        
        if result.get("success"):
            workspaces = result.get("workspaces", [])
            
            # Calculate analytics
            analytics = {
                "total_workspaces": len(workspaces),
                "active_subscriptions": len([w for w in workspaces if w.get("admin_analytics", {}).get("status") == "active"]),
                "paused_subscriptions": len([w for w in workspaces if w.get("admin_analytics", {}).get("status") == "paused"]),
                "comp_accounts": len([w for w in workspaces if w.get("admin_analytics", {}).get("is_comp_account")]),
                "overridden_subscriptions": len([w for w in workspaces if w.get("admin_analytics", {}).get("has_overrides")]),
                "total_revenue": sum(w.get("admin_analytics", {}).get("total_revenue", 0) for w in workspaces),
                "recent_admin_actions": sum(w.get("admin_analytics", {}).get("recent_admin_actions", 0) for w in workspaces)
            }
            
            return {
                "success": True,
                "analytics": analytics,
                "generated_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get admin analytics overview error: {e}")
        raise HTTPException(status_code=500, detail=str(e))