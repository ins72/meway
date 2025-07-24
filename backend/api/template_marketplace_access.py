"""
Template Marketplace Access Control API
Ensures only users with Creator+ bundles can sell templates
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from core.auth import get_current_user
from services.template_marketplace_access_service import get_template_marketplace_access_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check for template marketplace access control"""
    try:
        service = get_template_marketplace_access_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"Template marketplace access health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

@router.get("/seller-access/{user_id}")
async def check_seller_access(
    user_id: str = Path(..., description="User ID to check"),
    workspace_id: str = Query(..., description="Workspace ID"),
    current_user: dict = Depends(get_current_user)
):
    """Check if user has permission to sell templates"""
    try:
        # Users can only check their own access or if they're admin
        if user_id != current_user.get("id"):
            # Check if current user is admin of the workspace
            service = get_template_marketplace_access_service()
            is_admin = await service.check_admin_access(workspace_id, current_user.get("id"))
            if not is_admin:
                raise HTTPException(status_code=403, detail="Can only check your own seller access")
        
        service = get_template_marketplace_access_service()
        result = await service.check_seller_access(user_id, workspace_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=403, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Check seller access error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enable-selling")
async def enable_template_selling(
    data: Dict[str, Any] = Body(..., description="Enable selling data"),
    current_user: dict = Depends(get_current_user)
):
    """Enable template selling for user (requires Creator+ bundle)"""
    try:
        workspace_id = data.get("workspace_id")
        user_id = data.get("user_id", current_user.get("id"))
        
        if not workspace_id:
            raise HTTPException(status_code=400, detail="Workspace ID is required")
        
        # Users can only enable selling for themselves unless they're admin
        if user_id != current_user.get("id"):
            service = get_template_marketplace_access_service()
            is_admin = await service.check_admin_access(workspace_id, current_user.get("id"))
            if not is_admin:
                raise HTTPException(status_code=403, detail="Can only enable selling for yourself")
        
        service = get_template_marketplace_access_service()
        data["enabled_by"] = current_user.get("id")
        
        result = await service.enable_template_selling(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enable template selling error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/disable-selling")
async def disable_template_selling(
    data: Dict[str, Any] = Body(..., description="Disable selling data"),
    current_user: dict = Depends(get_current_user)
):
    """Disable template selling for user"""
    try:
        workspace_id = data.get("workspace_id")
        user_id = data.get("user_id", current_user.get("id"))
        reason = data.get("reason", "User request")
        
        if not workspace_id:
            raise HTTPException(status_code=400, detail="Workspace ID is required")
        
        # Users can disable for themselves, or admins can disable for others
        if user_id != current_user.get("id"):
            service = get_template_marketplace_access_service()
            is_admin = await service.check_admin_access(workspace_id, current_user.get("id"))
            if not is_admin:
                raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_template_marketplace_access_service()
        data["disabled_by"] = current_user.get("id")
        
        result = await service.disable_template_selling(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Disable template selling error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workspace-sellers/{workspace_id}")
async def get_workspace_sellers(
    workspace_id: str = Path(..., description="Workspace ID"),
    status: str = Query("active", description="Seller status: active, inactive, all"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Get list of template sellers in workspace (admin only)"""
    try:
        service = get_template_marketplace_access_service()
        
        # Check admin access
        is_admin = await service.check_admin_access(workspace_id, current_user.get("id"))
        if not is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = await service.get_workspace_sellers(workspace_id, status, limit, offset)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get workspace sellers error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/selling-requirements")
async def get_selling_requirements():
    """Get requirements for template selling"""
    try:
        service = get_template_marketplace_access_service()
        result = await service.get_selling_requirements()
        
        return result
        
    except Exception as e:
        logger.error(f"Get selling requirements error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate-template")
async def validate_template_for_selling(
    data: Dict[str, Any] = Body(..., description="Template validation data"),
    current_user: dict = Depends(get_current_user)
):
    """Validate template before allowing it to be listed for sale"""
    try:
        workspace_id = data.get("workspace_id")
        template_data = data.get("template_data")
        
        if not workspace_id or not template_data:
            raise HTTPException(status_code=400, detail="Workspace ID and template data are required")
        
        service = get_template_marketplace_access_service()
        
        # Check if user has selling access
        seller_check = await service.check_seller_access(current_user.get("id"), workspace_id)
        if not seller_check.get("has_access"):
            raise HTTPException(status_code=403, detail="Template selling access required")
        
        data["validated_by"] = current_user.get("id")
        result = await service.validate_template_for_selling(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Validate template error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/seller-stats/{user_id}")
async def get_seller_statistics(
    user_id: str = Path(..., description="User ID"),
    workspace_id: str = Query(..., description="Workspace ID"),
    period: str = Query("month", description="Period: week, month, quarter, year"),
    current_user: dict = Depends(get_current_user)
):
    """Get template selling statistics for user"""
    try:
        # Users can view their own stats, or admins can view any user's stats
        if user_id != current_user.get("id"):
            service = get_template_marketplace_access_service()
            is_admin = await service.check_admin_access(workspace_id, current_user.get("id"))
            if not is_admin:
                raise HTTPException(status_code=403, detail="Can only view your own statistics")
        
        service = get_template_marketplace_access_service()
        result = await service.get_seller_statistics(user_id, workspace_id, period)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get seller statistics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/report-template")
async def report_template_issue(
    data: Dict[str, Any] = Body(..., description="Template report data"),
    current_user: dict = Depends(get_current_user)
):
    """Report issues with templates (quality, copyright, etc.)"""
    try:
        template_id = data.get("template_id")
        report_reason = data.get("report_reason")
        description = data.get("description")
        
        if not template_id or not report_reason:
            raise HTTPException(status_code=400, detail="Template ID and report reason are required")
        
        service = get_template_marketplace_access_service()
        data["reported_by"] = current_user.get("id")
        
        result = await service.report_template_issue(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report template error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bundle-requirements/{bundle_name}")
async def get_bundle_selling_requirements(
    bundle_name: str = Path(..., description="Bundle name"),
    current_user: dict = Depends(get_current_user)
):
    """Get specific selling requirements for a bundle"""
    try:
        service = get_template_marketplace_access_service()
        result = await service.get_bundle_selling_requirements(bundle_name)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get bundle requirements error: {e}")
        raise HTTPException(status_code=500, detail=str(e))