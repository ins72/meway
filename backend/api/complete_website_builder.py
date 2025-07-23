"""
Website_Builder API endpoints
Auto-generated to complete service/API pairing
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel
from core.auth import get_current_active_user
from services.complete_website_builder_service import Complete_Website_BuilderService

router = APIRouter()

# Pydantic models
class Website_BuilderCreate(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[str] = "active"

class Website_BuilderUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

# Initialize service
service = Complete_Website_BuilderService()

@router.post("/website_builder/create")
async def create_website_builder(
    website_builder_data: Website_BuilderCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new website_builder"""
    try:
        result = await service.create_website_builder(website_builder_data.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/website_builder/{id}")
async def get_website_builder(
    id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get website_builder by ID"""
    try:
        result = await service.get_website_builder(id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/website_builder/list")
async def list_website_builder(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_active_user)
):
    """List website_builder"""
    try:
        result = await service.list_website_builder(limit=limit, offset=offset)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/website_builder/{id}")
async def update_website_builder(
    id: str,
    update_data: Website_BuilderUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Update website_builder"""
    try:
        result = await service.update_website_builder(id, update_data.dict(exclude_unset=True))
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/website_builder/{id}")
async def delete_website_builder(
    id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Delete website_builder"""
    try:
        result = await service.delete_website_builder(id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
