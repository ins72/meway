"""
Notification API
Production-ready RESTful API with comprehensive CRUD operations and validation
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path, status
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
from core.auth import get_current_user
from services.notification_service import get_notification_service
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class NotificationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Name of the notification")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the notification")
    status: Optional[str] = Field("active", description="Status of the notification")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Name cannot be empty")
        return v.strip()

class NotificationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Name of the notification")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the notification")
    status: Optional[str] = Field(None, description="Status of the notification")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and (not v or v.strip() == ""):
            raise ValueError("Name cannot be empty")
        return v.strip() if v else v

class NotificationResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Health Check
@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Comprehensive health check for notification service"""
    try:
        service = get_notification_service()
        result = await service.health_check()
        return result
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Create Operation
@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    item: item: NotificationCreate = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Create new notification with comprehensive validation"""
    try:
        # Convert Pydantic model to dict
        item_data = item.dict()
        
        # Add user context
        user_id = current_user.get("id") or current_user.get("user_id")
        item_data["created_by"] = current_user.get("email", "unknown")
        
        service = get_notification_service()
        result = await service.create_notification(item_data, user_id=user_id)
        
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
        logger.error(f"Create notification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Read Operations
@router.get("/", response_model=NotificationResponse)
async def list_notifications(
    limit: int = Query(50, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    search: Optional[str] = Query(None, description="Search query"),
    status: Optional[str] = Query(None, description="Filter by status"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    current_user: dict = Depends(get_current_user)
):
    """List notifications with comprehensive filtering and pagination"""
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        
        # Build filters
        filters = {}
        if status:
            filters["status"] = status
        
        # Handle search
        if search:
            service = get_notification_service()
            result = await service.search_notifications(
                search_query=search,
                user_id=user_id,
                limit=limit,
                offset=offset
            )
        else:
            # Regular listing
            service = get_notification_service()
            sort_order_int = -1 if sort_order == "desc" else 1
            result = await service.list_notifications(
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
        logger.error(f"List notifications failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{item_id}", response_model=NotificationResponse)
async def get_notification(
    item_id: str = Path(..., description="ID of the notification to retrieve"),
    current_user: dict = Depends(get_current_user)
):
    """Get notification by ID with comprehensive error handling"""
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        
        service = get_notification_service()
        result = await service.get_notification(item_id, user_id=user_id)
        
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
        logger.error(f"Get notification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Update Operation
@router.put("/{item_id}", response_model=NotificationResponse)
async def update_notification(
    item_id: str = Path(..., description="ID of the notification to update"),
    
    current_user: dict = Depends(get_current_user),
    item: NotificationUpdate,
):
    """Update notification with comprehensive validation"""
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
        
        service = get_notification_service()
        result = await service.update_notification(item_id, item_data, user_id=user_id)
        
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
        logger.error(f"Update notification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Delete Operation
@router.delete("/{item_id}", response_model=NotificationResponse)
async def delete_notification(
    item_id: str = Path(..., description="ID of the notification to delete"),
    permanent: bool = Query(False, description="Permanent delete (true) or soft delete (false)"),
    current_user: dict = Depends(get_current_user)
):
    """Delete notification with comprehensive validation"""
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        
        service = get_notification_service()
        result = await service.delete_notification(
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
        logger.error(f"Delete notification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Statistics
@router.get("/stats", response_model=NotificationResponse)
async def get_notification_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive statistics for notifications"""
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        
        service = get_notification_service()
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
        logger.error(f"Get notification stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Bulk Operations
@router.post("/bulk", response_model=NotificationResponse)
async def bulk_create_notifications(
    items: items: List[NotificationCreate] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Bulk create multiple notifications"""
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
        
        service = get_notification_service()
        result = await service.bulk_create_notifications(items_data, user_id=user_id)
        
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
        logger.error(f"Bulk create notifications failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))