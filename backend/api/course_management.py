"""
Course Management API
RESTful endpoints for course_management
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import Dict, Any, List, Optional
from core.auth import get_current_user
from services.course_management_service import get_course_management_service

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "course_management",
        "message": "Course Management API is operational"
    }

@router.post("/")
async def create_course_management(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Create new course_management"""
    try:
        service = get_course_management_service()
        result = await service.create_course_management(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Creation failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_course_managements(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """List course_managements with pagination"""
    try:
        service = get_course_management_service()
        result = await service.list_course_managements(
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
async def get_course_management(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get course_management by ID"""
    try:
        service = get_course_management_service()
        result = await service.get_course_management(item_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Not found"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{item_id}")
async def update_course_management(
    item_id: str,
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Update course_management by ID"""
    try:
        service = get_course_management_service()
        result = await service.update_course_management(item_id, data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Update failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{item_id}")
async def delete_course_management(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete course_management by ID"""
    try:
        service = get_course_management_service()
        result = await service.delete_course_management(item_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Delete failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_course_management_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get course_management statistics"""
    try:
        service = get_course_management_service()
        result = await service.get_stats(user_id=current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Stats failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))