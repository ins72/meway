"""
Notification API Router
Generated automatically to pair with notification_service
"""

from fastapi import APIRouter, HTTPException, Depends, Body, Query
from typing import List, Dict, Any, Optional
import logging

from core.auth import get_current_user
from services.notification_service import notification_service
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "notification",
        "timestamp": "2025-06-23T10:00:00Z"
    }

@router.post("/items", tags=["Item Management"])
async def create_item(
    item_data: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Create new item"""
    try:
        result = await notification_service.create_item(
            user_id=current_user["_id"],
            item_data=item_data
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Item created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/items", tags=["Item Management"])
async def list_items(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """List user's items"""
    try:
        result = await notification_service.list_items(
            user_id=current_user["_id"],
            page=page,
            limit=limit
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Items retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error listing items: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/items/{item_id}", tags=["Item Management"])
async def get_item(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific item"""
    try:
        result = await notification_service.get_item(
            user_id=current_user["_id"],
            item_id=item_id
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Item retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/items/{item_id}", tags=["Item Management"])
async def update_item(
    item_id: str,
    item_data: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Update existing item"""
    try:
        result = await notification_service.update_item(
            user_id=current_user["_id"],
            item_id=item_id,
            update_data=item_data
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Item updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/items/{item_id}", tags=["Item Management"])
async def delete_item(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete item"""
    try:
        result = await notification_service.delete_item(
            user_id=current_user["_id"],
            item_id=item_id
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Item deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error deleting item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
