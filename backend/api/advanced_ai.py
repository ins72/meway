"""
Advanced Ai API
RESTful endpoints for advanced_ai
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import Dict, Any, List, Optional
from core.auth import get_current_user
from services.advanced_ai_service import get_advanced_ai_service

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "advanced_ai",
        "message": "Advanced Ai API is operational"
    }

@router.post("/")
async def create_advanced_ai(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Create new advanced_ai"""
    try:
        service = get_advanced_ai_service()
        result = await service.create_advanced_ai(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Creation failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_advanced_ais(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """List advanced_ais with pagination"""
    try:
        service = get_advanced_ai_service()
        result = await service.list_advanced_ais(
            user_id=current_user.get("id"),
            limit=limit,
            offset=offset
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "List failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{item_id}")
async def get_advanced_ai(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get advanced_ai by ID"""
    try:
        service = get_advanced_ai_service()
        result = await service.get_advanced_ai(item_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Not found"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{item_id}")
async def update_advanced_ai(
    item_id: str,
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Update advanced_ai by ID"""
    try:
        service = get_advanced_ai_service()
        result = await service.update_advanced_ai(item_id, data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Update failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{item_id}")
async def delete_advanced_ai(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete advanced_ai by ID"""
    try:
        service = get_advanced_ai_service()
        result = await service.delete_advanced_ai(item_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Delete failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_advanced_ai_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get advanced_ai statistics"""
    try:
        service = get_advanced_ai_service()
        result = await service.get_stats(user_id=current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Stats failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))