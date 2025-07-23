"""
Link_In_Bio API endpoints
Auto-generated to complete service/API pairing
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel
from core.auth import get_current_active_user
from services.complete_link_in_bio_service import Complete_Link_In_BioService

router = APIRouter()

# Pydantic models
class Link_In_BioCreate(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[str] = "active"

class Link_In_BioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

# Initialize service
service = Complete_Link_In_BioService()

@router.post("/link_in_bio/create")
async def create_link_in_bio(
    link_in_bio_data: Link_In_BioCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new link_in_bio"""
    try:
        result = await service.create_link_in_bio(link_in_bio_data.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/link_in_bio/{id}")
async def get_link_in_bio(
    id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get link_in_bio by ID"""
    try:
        result = await service.get_link_in_bio(id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/link_in_bio/list")
async def list_link_in_bio(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_active_user)
):
    """List link_in_bio"""
    try:
        result = await service.list_link_in_bio(limit=limit, offset=offset)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/link_in_bio/{id}")
async def update_link_in_bio(
    id: str,
    update_data: Link_In_BioUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Update link_in_bio"""
    try:
        result = await service.update_link_in_bio(id, update_data.dict(exclude_unset=True))
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/link_in_bio/{id}")
async def delete_link_in_bio(
    id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Delete link_in_bio"""
    try:
        result = await service.delete_link_in_bio(id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
