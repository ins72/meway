"""
Multi_Vendor_Marketplace API endpoints
Auto-generated to complete service/API pairing
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel
from core.auth import get_current_active_user
from services.multi_vendor_marketplace_service import Multi_Vendor_MarketplaceService
import uuid
from datetime import datetime

router = APIRouter()

# Pydantic models
class Multi_Vendor_MarketplaceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[str] = "active"

class Multi_Vendor_MarketplaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

# Initialize service
service = Multi_Vendor_MarketplaceService()

@router.post("/multi_vendor_marketplace/create")
async def create_multi_vendor_marketplace(
    multi_vendor_marketplace_data: Multi_Vendor_MarketplaceCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new multi_vendor_marketplace"""
    try:
        result = await service.create_multi_vendor_marketplace(multi_vendor_marketplace_data.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/multi_vendor_marketplace/{id}")
async def get_multi_vendor_marketplace(
    id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get multi_vendor_marketplace by ID"""
    try:
        result = await service.get_multi_vendor_marketplace(id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/multi_vendor_marketplace/list")
async def list_multi_vendor_marketplace(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_active_user)
):
    """List multi_vendor_marketplace"""
    try:
        result = await service.list_multi_vendor_marketplace(limit=limit, offset=offset)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/multi_vendor_marketplace/{id}")
async def update_multi_vendor_marketplace(
    id: str,
    update_data: Multi_Vendor_MarketplaceUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Update multi_vendor_marketplace"""
    try:
        result = await service.update_multi_vendor_marketplace(id, update_data.dict(exclude_unset=True))
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/multi_vendor_marketplace/{id}")
async def delete_multi_vendor_marketplace(
    id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Delete multi_vendor_marketplace"""
    try:
        result = await service.delete_multi_vendor_marketplace(id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
