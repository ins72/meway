"""
Admin Pricing Management API
Allows admins to update pricing plans, features, limits, and enable/disable bundles
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from core.auth import get_current_user
from services.admin_pricing_service import get_admin_pricing_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check for admin pricing management"""
    try:
        service = get_admin_pricing_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"Admin pricing health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

@router.get("/current-pricing")
async def get_current_pricing_config(
    current_user: dict = Depends(get_current_user)
):
    """Get current pricing configuration for all bundles"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_pricing_service()
        result = await service.get_current_pricing_config()
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current pricing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-bundle-pricing")
async def update_bundle_pricing(
    data: Dict[str, Any] = Body(..., description="Bundle pricing update data"),
    current_user: dict = Depends(get_current_user)
):
    """Update pricing for a specific bundle"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        bundle_name = data.get("bundle_name")
        if not bundle_name:
            raise HTTPException(status_code=400, detail="Bundle name is required")
        
        service = get_admin_pricing_service()
        data["updated_by"] = current_user.get("id")
        
        result = await service.update_bundle_pricing(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update bundle pricing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-bundle-features")
async def update_bundle_features(
    data: Dict[str, Any] = Body(..., description="Bundle features update data"),
    current_user: dict = Depends(get_current_user)
):
    """Update features and limits for a bundle"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        bundle_name = data.get("bundle_name")
        if not bundle_name:
            raise HTTPException(status_code=400, detail="Bundle name is required")
        
        service = get_admin_pricing_service()
        data["updated_by"] = current_user.get("id")
        
        result = await service.update_bundle_features(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update bundle features error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enable-disable-bundle")
async def enable_disable_bundle(
    data: Dict[str, Any] = Body(..., description="Bundle enable/disable data"),
    current_user: dict = Depends(get_current_user)
):
    """Enable or disable a bundle for new subscriptions"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        bundle_name = data.get("bundle_name")
        action = data.get("action")  # "enable" or "disable"
        
        if not bundle_name or not action:
            raise HTTPException(status_code=400, detail="Bundle name and action are required")
        
        service = get_admin_pricing_service()
        data["modified_by"] = current_user.get("id")
        
        result = await service.enable_disable_bundle(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enable/disable bundle error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-new-bundle")
async def create_new_bundle(
    data: Dict[str, Any] = Body(..., description="New bundle creation data"),
    current_user: dict = Depends(get_current_user)
):
    """Create a new bundle with pricing and features"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_pricing_service()
        data["created_by"] = current_user.get("id")
        
        result = await service.create_new_bundle(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create new bundle error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pricing-history/{bundle_name}")
async def get_pricing_history(
    bundle_name: str = Path(..., description="Bundle name"),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get pricing change history for a bundle"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_pricing_service()
        result = await service.get_pricing_history(bundle_name, limit)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get pricing history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk-pricing-update")
async def bulk_pricing_update(
    data: Dict[str, Any] = Body(..., description="Bulk pricing update data"),
    current_user: dict = Depends(get_current_user)
):
    """Update pricing for multiple bundles at once"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_pricing_service()
        data["updated_by"] = current_user.get("id")
        
        result = await service.bulk_pricing_update(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk pricing update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pricing-analytics")
async def get_pricing_analytics(
    current_user: dict = Depends(get_current_user)
):
    """Get analytics on pricing performance and subscription trends"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_pricing_service()
        result = await service.get_pricing_analytics()
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get pricing analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-pricing-change")
async def test_pricing_change(
    data: Dict[str, Any] = Body(..., description="Pricing change test data"),
    current_user: dict = Depends(get_current_user)
):
    """Test impact of pricing changes before applying"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_pricing_service()
        result = await service.test_pricing_change(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Test pricing change error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply-pricing-template")
async def apply_pricing_template(
    data: Dict[str, Any] = Body(..., description="Pricing template data"),
    current_user: dict = Depends(get_current_user)
):
    """Apply predefined pricing templates (e.g., holiday discounts)"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_admin_pricing_service()
        data["applied_by"] = current_user.get("id")
        
        result = await service.apply_pricing_template(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Apply pricing template error: {e}")
        raise HTTPException(status_code=500, detail=str(e))