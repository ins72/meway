"""
Onboarding API endpoints
Auto-generated to complete service/API pairing
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel
from core.auth import get_current_active_user
from services.complete_onboarding_service import Complete_OnboardingService

router = APIRouter()

# Pydantic models
class OnboardingCreate(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[str] = "active"

class OnboardingUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

# Initialize service
service = Complete_OnboardingService()

@router.post("/onboarding/create")
async def create_onboarding(
    onboarding_data: OnboardingCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new onboarding"""
    try:
        result = await service.create_onboarding(onboarding_data.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/onboarding/{id}")
async def get_onboarding(
    id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get onboarding by ID"""
    try:
        result = await service.get_onboarding(id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/onboarding/list")
async def list_onboarding(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_active_user)
):
    """List onboarding"""
    try:
        result = await service.list_onboarding(limit=limit, offset=offset)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/onboarding/{id}")
async def update_onboarding(
    id: str,
    update_data: OnboardingUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Update onboarding"""
    try:
        result = await service.update_onboarding(id, update_data.dict(exclude_unset=True))
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/onboarding/{id}")
async def delete_onboarding(
    id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Delete onboarding"""
    try:
        result = await service.delete_onboarding(id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
