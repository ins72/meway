"""
Launch Pricing API
Handles time-limited launch specials and promotional pricing for bundle subscriptions
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from core.auth import get_current_user
from services.launch_pricing_service import get_launch_pricing_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check for launch pricing system"""
    try:
        service = get_launch_pricing_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"Launch pricing health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

@router.get("/active-specials")
async def get_active_launch_specials():
    """Get all currently active launch specials"""
    try:
        service = get_launch_pricing_service()
        result = await service.get_active_specials()
        
        return result
        
    except Exception as e:
        logger.error(f"Get active specials error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bundle/{bundle_name}/special")
async def get_bundle_launch_special(
    bundle_name: str = Path(..., description="Bundle name"),
    current_user: dict = Depends(get_current_user)
):
    """Get launch special for specific bundle"""
    try:
        service = get_launch_pricing_service()
        result = await service.get_bundle_special(bundle_name, current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get bundle special error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/claim-special")
async def claim_launch_special(
    data: Dict[str, Any] = Body(..., description="Launch special claim data"),
    current_user: dict = Depends(get_current_user)
):
    """Claim a launch special offer"""
    try:
        bundle_name = data.get("bundle_name")  
        special_code = data.get("special_code")
        workspace_id = data.get("workspace_id")
        
        if not bundle_name or not workspace_id:
            raise HTTPException(status_code=400, detail="Bundle name and workspace ID are required")
        
        service = get_launch_pricing_service()
        data["claimed_by"] = current_user.get("id")
        
        result = await service.claim_launch_special(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Claim launch special error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate-eligibility")
async def validate_special_eligibility(
    data: Dict[str, Any] = Body(..., description="Eligibility validation data"),
    current_user: dict = Depends(get_current_user)
):
    """Validate if user is eligible for launch special"""
    try:
        bundle_name = data.get("bundle_name")
        workspace_id = data.get("workspace_id")
        
        if not bundle_name or not workspace_id:
            raise HTTPException(status_code=400, detail="Bundle name and workspace ID are required")
        
        service = get_launch_pricing_service()
        result = await service.validate_eligibility(bundle_name, workspace_id, current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Validate eligibility error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/claimed-specials/{workspace_id}")
async def get_claimed_specials(
    workspace_id: str = Path(..., description="Workspace ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get all launch specials claimed by workspace"""
    try:
        service = get_launch_pricing_service()
        result = await service.get_claimed_specials(workspace_id, current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get claimed specials error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-promo-code")
async def generate_promo_code(
    data: Dict[str, Any] = Body(..., description="Promo code generation data"),
    current_user: dict = Depends(get_current_user)
):
    """Generate promotional code for launch special (admin only)"""
    try:
        # Check if user is admin (simplified check)
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_launch_pricing_service()
        data["generated_by"] = current_user.get("id")
        
        result = await service.generate_promo_code(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate promo code error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/special-analytics")
async def get_launch_special_analytics(
    bundle_name: str = Query(None, description="Filter by bundle name"),
    current_user: dict = Depends(get_current_user)
):
    """Get analytics for launch specials (admin only)"""
    try:
        # Check if user is admin
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_launch_pricing_service()
        result = await service.get_special_analytics(bundle_name)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get special analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extend-special")
async def extend_launch_special(
    data: Dict[str, Any] = Body(..., description="Special extension data"),
    current_user: dict = Depends(get_current_user)
):
    """Extend or modify launch special (admin only)"""
    try:
        # Check if user is admin
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_launch_pricing_service()
        data["modified_by"] = current_user.get("id")
        
        result = await service.extend_special(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Extend special error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/referral-tracking/{referral_code}")
async def track_referral(
    referral_code: str = Path(..., description="Referral code"),
    current_user: dict = Depends(get_current_user)
):
    """Track referral usage for launch specials"""
    try:
        service = get_launch_pricing_service()
        result = await service.track_referral(referral_code, current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Track referral error: {e}")
        raise HTTPException(status_code=500, detail=str(e))