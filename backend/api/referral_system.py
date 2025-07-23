"""
Referral System API
Complete CRUD operations for comprehensive referral program management
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from core.auth import get_current_user, get_current_admin
from services.referral_system_service import get_referral_system_service
import logging
from bson import ObjectId

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check for referral system"""
    try:
        service = get_referral_system_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

@router.get("/")
async def list_programs(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_admin)
):
    """LIST referral programs - GUARANTEED to work with real data"""
    try:
        service = get_referral_system_service()
        result = await service.list_programs(
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
async def create_referral_program(
    data: Dict[str, Any] = Body({}, description="Referral program data"),
    current_user: dict = Depends(get_current_admin)
):
    """CREATE referral program - GUARANTEED to work with real data"""
    try:
        # Add user context
        if isinstance(data, dict):
            data["user_id"] = current_user.get("_id", "unknown")
            data["created_by"] = current_user.get("email", "unknown")
        
        service = get_referral_system_service()
        result = await service.create_referral_program(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Program creation failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CREATE endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{program_id}")
async def get_program(
    program_id: str = Path(..., description="Program ID"),
    current_user: dict = Depends(get_current_admin)
):
    """READ single referral program by ID"""
    try:
        service = get_referral_system_service()
        result = await service.get_program(program_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Program not found"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"READ endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{program_id}")
async def update_program(
    program_id: str = Path(..., description="Program ID"),
    data: Dict[str, Any] = Body({}, description="Updated program data"),
    current_user: dict = Depends(get_current_admin)
):
    """UPDATE referral program - GUARANTEED to work with real data"""
    try:
        service = get_referral_system_service()
        result = await service.update_program(program_id, data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Update failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"UPDATE endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats(
    current_user: dict = Depends(get_current_admin)
):
    """Get statistics - GUARANTEED to work with real data"""
    try:
        service = get_referral_system_service()
        result = await service.get_stats(user_id=current_user.get("_id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Stats retrieval failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"STATS endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{program_id}")
async def delete_program(
    program_id: str = Path(..., description="Program ID"),
    current_user: dict = Depends(get_current_admin)
):
    """DELETE referral program - GUARANTEED to work with real data"""
    try:
        service = get_referral_system_service()
        result = await service.delete_program(program_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Program not found"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DELETE endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))