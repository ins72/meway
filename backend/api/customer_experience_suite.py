"""
Customer_Experience_Suite API endpoints
Auto-generated for service customer_experience_suite_service
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user
from services.customer_experience_suite_service import Customer_Experience_SuiteService

router = APIRouter()
service = Customer_Experience_SuiteService()

@router.get("/health")
async def health_check():
    """Health check for customer_experience_suite service"""
    return {"status": "healthy", "service": "customer_experience_suite"}

@router.post("/")
async def create_customer_experience_suite(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_active_user)
):
    """Create new customer_experience_suite"""
    try:
        result = await service.create_customer_experience_suite(data)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_customer_experience_suite(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_active_user)
):
    """List customer_experience_suite"""
    try:
        result = await service.list_customer_experience_suite(limit=limit, offset=offset)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}")
async def get_customer_experience_suite(
    id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get customer_experience_suite by ID"""
    try:
        result = await service.get_customer_experience_suite(id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id}")
async def update_customer_experience_suite(
    id: str,
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_active_user)
):
    """Update customer_experience_suite"""
    try:
        result = await service.update_customer_experience_suite(id, data)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id}")
async def delete_customer_experience_suite(
    id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Delete customer_experience_suite"""
    try:
        result = await service.delete_customer_experience_suite(id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
