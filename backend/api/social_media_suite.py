"""
Social Media Suite API
RESTful endpoints for social_media_suite
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import Dict, Any, List, Optional
from core.auth import get_current_user
from services.social_media_suite_service import get_social_media_suite_service

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "social_media_suite",
        "message": "Social Media Suite API is operational"
    }

@router.post("/")
async def create_social_media_suite(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Create new social_media_suite"""
    try:
        service = get_social_media_suite_service()
        result = await service.create_social_media_suite(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Creation failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_social_media_suites(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """List social_media_suites with pagination"""
    try:
        service = get_social_media_suite_service()
        result = await service.list_social_media_suites(
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
async def get_social_media_suite(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get social_media_suite by ID"""
    try:
        service = get_social_media_suite_service()
        result = await service.get_social_media_suite(item_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Not found"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{item_id}")
async def update_social_media_suite(
    item_id: str,
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Update social_media_suite by ID"""
    try:
        service = get_social_media_suite_service()
        result = await service.update_social_media_suite(item_id, data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Update failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{item_id}")
async def delete_social_media_suite(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete social_media_suite by ID"""
    try:
        service = get_social_media_suite_service()
        result = await service.delete_social_media_suite(item_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Delete failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_social_media_suite_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get social_media_suite statistics"""
    try:
        service = get_social_media_suite_service()
        result = await service.get_stats(user_id=current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Stats failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))