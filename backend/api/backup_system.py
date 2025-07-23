"""
Backup System API
RESTful endpoints for backup_system
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import Dict, Any, List, Optional
from core.auth import get_current_user
from services.backup_system_service import get_backup_system_service

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "backup_system",
        "message": "Backup System API is operational"
    }

@router.post("/")
async def create_backup_system(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Create new backup_system"""
    try:
        service = get_backup_system_service()
        result = await service.create_backup_system(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Creation failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_backup_systems(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """List backup_systems with pagination"""
    try:
        service = get_backup_system_service()
        result = await service.list_backup_systems(
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
async def get_backup_system(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get backup_system by ID"""
    try:
        service = get_backup_system_service()
        result = await service.get_backup_system(item_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Not found"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{item_id}")
async def update_backup_system(
    item_id: str,
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Update backup_system by ID"""
    try:
        service = get_backup_system_service()
        result = await service.update_backup_system(item_id, data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Update failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{item_id}")
async def delete_backup_system(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete backup_system by ID"""
    try:
        service = get_backup_system_service()
        result = await service.delete_backup_system(item_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Delete failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_backup_system_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get backup_system statistics"""
    try:
        service = get_backup_system_service()
        result = await service.get_stats(user_id=current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Stats failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))