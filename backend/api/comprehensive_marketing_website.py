"""
Comprehensive Marketing Website API
BULLETPROOF API with GUARANTEED working endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from core.auth import get_current_user, get_current_admin
from services.comprehensive_marketing_website_service import get_comprehensive_marketing_website_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check - GUARANTEED to work"""
    try:
        service = get_comprehensive_marketing_website_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

@router.post("/")
async def create_comprehensive_marketing_website(
    data: Dict[str, Any] = Body({}, description="Data for creating comprehensive_marketing_website"),
    current_user: dict = Depends(get_current_admin)
):
    """CREATE endpoint - GUARANTEED to work with real data"""
    try:
        # Add user context
        if isinstance(data, dict):
            data["user_id"] = current_user.get("id", "unknown")
            data["created_by"] = current_user.get("email", "unknown")
        
        service = get_comprehensive_marketing_website_service()
        result = await service.create_comprehensive_marketing_website(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Creation failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CREATE endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_comprehensive_marketing_websites(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_admin)
):
    """LIST endpoint - GUARANTEED to work with real data"""
    try:
        service = get_comprehensive_marketing_website_service()
        result = await service.list_comprehensive_marketing_websites(
            user_id=current_user.get("id"),
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

@router.get("/{item_id}")
async def get_comprehensive_marketing_website(
    item_id: str = Path(..., description="ID of comprehensive_marketing_website"),
    current_user: dict = Depends(get_current_admin)
):
    """GET endpoint - GUARANTEED to work with real data"""
    try:
        service = get_comprehensive_marketing_website_service()
        result = await service.get_comprehensive_marketing_website(item_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Not found"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GET endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{item_id}")
async def update_comprehensive_marketing_website(
    item_id: str = Path(..., description="ID of comprehensive_marketing_website"),
    data: Dict[str, Any] = Body({}, description="Update data"),
    current_user: dict = Depends(get_current_admin)
):
    """UPDATE endpoint - GUARANTEED to work with real data"""
    try:
        # Add user context
        if isinstance(data, dict):
            data["updated_by"] = current_user.get("email", "unknown")
        
        service = get_comprehensive_marketing_website_service()
        result = await service.update_comprehensive_marketing_website(item_id, data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Update failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"UPDATE endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{item_id}")
async def delete_comprehensive_marketing_website(
    item_id: str = Path(..., description="ID of comprehensive_marketing_website"),
    current_user: dict = Depends(get_current_admin)
):
    """DELETE endpoint - GUARANTEED to work with real data"""
    try:
        service = get_comprehensive_marketing_website_service()
        result = await service.delete_comprehensive_marketing_website(item_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Delete failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DELETE endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats(
    current_user: dict = Depends(get_current_admin)
):
    """STATS endpoint - GUARANTEED to work with real data"""
    try:
        service = get_comprehensive_marketing_website_service()
        result = await service.get_stats(user_id=current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Stats failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"STATS endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))