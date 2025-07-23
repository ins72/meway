"""
Subscription API endpoints
Auto-generated to complete service/API pairing
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel
from core.auth import get_current_active_user
from services.complete_subscription_service import Complete_SubscriptionService
import uuid
from datetime import datetime

router = APIRouter()

# Pydantic models
class SubscriptionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[str] = "active"

class SubscriptionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

# Initialize service
service = Complete_SubscriptionService()

@router.post("/subscription/create")
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new subscription"""
    try:
        result = await service.create_subscription(subscription_data.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subscription/{id}")
async def get_subscription(
    id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get subscription by ID"""
    try:
        result = await service.get_subscription(id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subscription/list")
async def list_subscription(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_active_user)
):
    """List subscription"""
    try:
        result = await service.list_subscription(limit=limit, offset=offset)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/subscription/{id}")
async def update_subscription(
    id: str,
    update_data: SubscriptionUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Update subscription"""
    try:
        result = await service.update_subscription(id, update_data.dict(exclude_unset=True))
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/subscription/{id}")
async def delete_subscription(
    id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Delete subscription"""
    try:
        result = await service.delete_subscription(id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
