"""
Content_Creation_Suite API endpoints
Auto-generated for service content_creation_suite_service
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user
from services.content_creation_suite_service import Content_Creation_SuiteService

router = APIRouter()
service = Content_Creation_SuiteService()

@router.get("/health")
async def health_check():
    """Health check for content_creation_suite service"""
    return {"status": "healthy", "service": "content_creation_suite"}

@router.post("/")
async def create_content_creation_suite(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_active_user)
):
    """Create new content_creation_suite"""
    try:
        result = await service.create_content_creation_suite(data)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_content_creation_suite(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_active_user)
):
    """List content_creation_suite"""
    try:
        result = await service.list_content_creation_suite(limit=limit, offset=offset)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}")
async def get_content_creation_suite(
    id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get content_creation_suite by ID"""
    try:
        result = await service.get_content_creation_suite(id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id}")
async def update_content_creation_suite(
    id: str,
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_active_user)
):
    """Update content_creation_suite"""
    try:
        result = await service.update_content_creation_suite(id, data)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id}")
async def delete_content_creation_suite(
    id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Delete content_creation_suite"""
    try:
        result = await service.delete_content_creation_suite(id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
