"""
Integration API
Production-ready RESTful API with comprehensive CRUD operations and validation
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path, status
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
from core.auth import get_current_user
from services.integration_service import get_integration_service
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class IntegrationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Name of the integration")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the integration")
    status: Optional[str] = Field("active", description="Status of the integration")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Name cannot be empty")
        return v.strip()

class IntegrationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Name of the integration")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the integration")
    status: Optional[str] = Field(None, description="Status of the integration")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and (not v or v.strip() == ""):
            raise ValueError("Name cannot be empty")
        return v.strip() if v else v

class IntegrationResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Health Check
@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Comprehensive health check for integration service"""
    try:
        service = get_integration_service()
        result = await service.health_check()
        return result
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Create Operation
@router.post("/", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    item: IntegrationCreate = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Create new integration with comprehensive validation"""
    try:
        # Convert Pydantic model to dict
        item_data = item.dict()
        
        # Add user context
        user_id = current_user.get("id") or current_user.get("user_id")
        item_data["created_by"] = current_user.get("email", "unknown")
        
        service = get_integration_service()
        result = await service.create_integration(item_data, user_id=user_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(
                status_code=400, 
                detail=result.get("error", "Creation failed")
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create integration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Read Operations
@router.get("/", response_model=IntegrationResponse)
async def list_integrations(
    limit: int = Query(50, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    search: Optional[str] = Query(None, description="Search query"),
    status: Optional[str] = Query(None, description="Filter by status"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    current_user: dict = Depends(get_current_user)
):
    """List integrations with comprehensive filtering and pagination"""
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        
        # Build filters
        filters = {}
        if status:
            filters["status"] = status
        
        # Handle search
        if search:
            service = get_integration_service()
            result = await service.search_integrations(
                search_query=search,
                user_id=user_id,
                limit=limit,
                offset=offset
            )
        else:
            # Regular listing
            service = get_integration_service()
            sort_order_int = -1 if sort_order == "desc" else 1
            result = await service.list_integrations(
                user_id=user_id,
                limit=limit,
                offset=offset,
                filters=filters,
                sort_by=sort_by,
                sort_order=sort_order_int
            )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(
                status_code=400, 
                detail=result.get("error", "List failed")
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List integrations failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{item_id}", response_model=IntegrationResponse)
async def get_integration(
    item_id: str = Path(..., description="ID of the integration to retrieve"),
    current_user: dict = Depends(get_current_user)
):
    """Get integration by ID with comprehensive error handling"""
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        
        service = get_integration_service()
        result = await service.get_integration(item_id, user_id=user_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(
                status_code=404, 
                detail=result.get("error", "Not found")
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get integration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Update Operation
@router.put("/{item_id}", response_model=IntegrationResponse)
async def update_integration(
    item_id: str = Path(..., description="ID of the integration to update"),    item: IntegrationUpdate = Body(...),

    
    current_user: dict = Depends(get_current_user),
):
    """Update integration with comprehensive validation"""
    try:
        # Convert Pydantic model to dict, excluding None values
        item_data = item.dict(exclude_none=True)
        
        if not item_data:
            raise HTTPException(
                status_code=400, 
                detail="At least one field must be provided for update"
            )
        
        # Add user context
        user_id = current_user.get("id") or current_user.get("user_id")
        item_data["updated_by"] = current_user.get("email", "unknown")
        
        service = get_integration_service()
        result = await service.update_integration(item_id, item_data, user_id=user_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(
                status_code=404, 
                detail=result.get("error", "Update failed")
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update integration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Delete Operation
@router.delete("/{item_id}", response_model=IntegrationResponse)
async def delete_integration(
    item_id: str = Path(..., description="ID of the integration to delete"),
    permanent: bool = Query(False, description="Permanent delete (true) or soft delete (false)"),
    current_user: dict = Depends(get_current_user)
):
    """Delete integration with comprehensive validation"""
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        
        service = get_integration_service()
        result = await service.delete_integration(
            item_id, 
            user_id=user_id, 
            soft_delete=not permanent
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(
                status_code=404, 
                detail=result.get("error", "Delete failed")
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete integration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Statistics
@router.get("/stats", response_model=IntegrationResponse)
async def get_integration_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive statistics for integrations"""
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        
        service = get_integration_service()
        result = await service.get_stats(user_id=user_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(
                status_code=400, 
                detail=result.get("error", "Stats failed")
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get integration stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Bulk Operations
@router.post("/bulk", response_model=IntegrationResponse)
async def bulk_create_integrations(
    items: List[IntegrationCreate] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Bulk create multiple integrations"""
    try:
        if not items:
            raise HTTPException(
                status_code=400, 
                detail="At least one item must be provided"
            )
        
        if len(items) > 100:
            raise HTTPException(
                status_code=400, 
                detail="Maximum 100 items can be created at once"
            )
        
        # Convert Pydantic models to dicts
        items_data = [item.dict() for item in items]
        
        # Add user context
        user_id = current_user.get("id") or current_user.get("user_id")
        user_email = current_user.get("email", "unknown")
        
        for item_data in items_data:
            item_data["created_by"] = user_email
        
        service = get_integration_service()
        result = await service.bulk_create_integrations(items_data, user_id=user_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(
                status_code=400, 
                detail=result.get("error", "Bulk creation failed")
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk create integrations failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))