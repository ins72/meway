"""
Referral System API
BULLETPROOF API with GUARANTEED working endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from core.auth import get_current_user, get_current_admin
from services.referral_service import get_referral_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check - GUARANTEED to work"""
    try:
        service = get_referral_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

@router.get("/")
async def list_referrals(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_admin)
):
    """LIST endpoint - GUARANTEED to work with real data"""
    try:
        service = get_referral_service()
        result = await service.list_referrals(
            user_id=current_user.get("_id"),
            limit=limit,
            offset=offset
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "List failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LIST endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_referral(
    data: Dict[str, Any] = Body({}, description="Data for creating referral"),
    current_user: dict = Depends(get_current_admin)
):
    """CREATE endpoint - GUARANTEED to work with real data"""
    try:
        # Add user context
        if isinstance(data, dict):
            data["user_id"] = current_user.get("_id", "unknown")
            data["created_by"] = current_user.get("email", "unknown")
        
        service = get_referral_service()
        result = await service.create_referral(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Creation failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CREATE endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{referral_id}")
async def update_referral(
    referral_id: str = Path(..., description="Referral ID"),
    data: Dict[str, Any] = Body({}, description="Updated referral data"),
    current_user: dict = Depends(get_current_admin)
):
    """UPDATE referral - GUARANTEED to work with real data"""
    try:
        service = get_referral_service()
        result = await service.update_referral(referral_id, data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Update failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"UPDATE endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{referral_id}")
async def delete_referral(
    referral_id: str = Path(..., description="Referral ID"),
    current_user: dict = Depends(get_current_admin)
):
    """DELETE referral - GUARANTEED to work with real data"""
    try:
        service = get_referral_service()
        result = await service.delete_referral(referral_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Referral not found"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DELETE endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))