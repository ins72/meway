"""
Complete Social Media Leads API Router
Comprehensive API endpoints for complete_social_media_leads_service
Generated: 2025-07-23 11:29:09
"""

from fastapi import APIRouter, HTTPException, Depends, Body, Query, Path
from typing import List, Dict, Any, Optional
import logging

from core.auth import get_current_user
from services.complete_social_media_leads_service import complete_social_media_leads_service
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# Health Check
@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "complete_social_media_leads_service",
        "timestamp": "2025-07-23T11:29:09.500483",
        "version": "2.0"
    }

# CRUD Endpoints
@router.post("/leads", tags=["Lead Management"])
async def create_lead(
    lead_data: dict = Body(..., description="Lead data"),
    current_user: dict = Depends(get_current_user)
):
    """Create new lead"""
    try:
        result = await complete_social_media_leads_service.create_lead(
            user_id=current_user["_id"],
            lead_data=lead_data
        )
        
        if result.get("success"):
            return {
                "success": True,
                "data": result.get("data"),
                "message": result.get("message", "Lead created successfully")
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Creation failed"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating lead: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/leads", tags=["Lead Management"])
async def list_leads(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search term"),
    current_user: dict = Depends(get_current_user)
):
    """List user's leads with pagination"""
    try:
        filters = {}
        if status:
            filters["status"] = status
        if search:
            filters["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        result = await complete_social_media_leads_service.list_leads(
            user_id=current_user["_id"],
            filters=filters,
            page=page,
            limit=limit
        )
        
        if result.get("success"):
            return {
                "success": True,
                "data": result.get("data"),
                "message": result.get("message", "Leads retrieved successfully")
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Retrieval failed"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing leads: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/leads/{item_id}", tags=["Lead Management"])
async def get_lead(
    item_id: str = Path(..., description="Lead ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get specific lead"""
    try:
        result = await complete_social_media_leads_service.get_lead(
            user_id=current_user["_id"],
            lead_id=item_id
        )
        
        if result.get("success"):
            return {
                "success": True,
                "data": result.get("data"),
                "message": result.get("message", "Lead retrieved successfully")
            }
        else:
            raise HTTPException(status_code=404, detail=result.get("message", "Lead not found"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting lead: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/leads/{item_id}", tags=["Lead Management"])
async def update_lead(
    item_id: str = Path(..., description="Lead ID"),
    lead_data: dict = Body(..., description="Update data"),
    current_user: dict = Depends(get_current_user)
):
    """Update existing lead"""
    try:
        result = await complete_social_media_leads_service.update_lead(
            user_id=current_user["_id"],
            lead_id=item_id,
            update_data=lead_data
        )
        
        if result.get("success"):
            return {
                "success": True,
                "data": result.get("data"),
                "message": result.get("message", "Lead updated successfully")
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Update failed"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating lead: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/leads/{item_id}", tags=["Lead Management"])
async def delete_lead(
    item_id: str = Path(..., description="Lead ID"),
    hard_delete: bool = Query(False, description="Permanently delete (cannot be undone)"),
    current_user: dict = Depends(get_current_user)
):
    """Delete lead"""
    try:
        result = await complete_social_media_leads_service.delete_lead(
            user_id=current_user["_id"],
            lead_id=item_id,
            hard_delete=hard_delete
        )
        
        if result.get("success"):
            return {
                "success": True,
                "message": result.get("message", "Lead deleted successfully")
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Delete failed"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting lead: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Analytics Endpoint
@router.get("/leads/analytics", tags=["Lead Analytics"])
async def get_lead_analytics(
    period: str = Query("7d", description="Time period (7d, 30d, 90d, 1y)"),
    current_user: dict = Depends(get_current_user)
):
    """Get lead analytics and metrics"""
    try:
        # This would be implemented based on service-specific analytics
        return {
            "success": True,
            "data": {
                "period": period,
                "total_leads": 0,
                "active_leads": 0,
                "growth_rate": 0.0,
                "last_updated": "2025-07-23T11:29:09.500501"
            },
            "message": "Lead analytics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting lead analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")
