"""
Complete Booking API Router
Comprehensive API endpoints for complete_booking_service
Generated: 2025-07-23 11:29:09
"""

from fastapi import APIRouter, HTTPException, Depends, Body, Query, Path
from typing import List, Dict, Any, Optional
import logging

from core.auth import get_current_user
from services.complete_booking_service import complete_booking_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Health Check
@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "complete_booking_service",
        "timestamp": "2025-07-23T11:29:09.500827",
        "version": "2.0"
    }

# CRUD Endpoints
@router.post("/appointments", tags=["Appointment Management"])
async def create_appointment(
    appointment_data: dict = Body(..., description="Appointment data"),
    current_user: dict = Depends(get_current_user)
):
    """Create new appointment"""
    try:
        result = await complete_booking_service.create_appointment(
            user_id=current_user["_id"],
            appointment_data=appointment_data
        )
        
        if result.get("success"):
            return {
                "success": True,
                "data": result.get("data"),
                "message": result.get("message", "Appointment created successfully")
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Creation failed"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating appointment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/appointments", tags=["Appointment Management"])
async def list_appointments(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search term"),
    current_user: dict = Depends(get_current_user)
):
    """List user's appointments with pagination"""
    try:
        filters = {}
        if status:
            filters["status"] = status
        if search:
            filters["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        result = await complete_booking_service.list_appointments(
            user_id=current_user["_id"],
            filters=filters,
            page=page,
            limit=limit
        )
        
        if result.get("success"):
            return {
                "success": True,
                "data": result.get("data"),
                "message": result.get("message", "Appointments retrieved successfully")
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Retrieval failed"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing appointments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/appointments/{item_id}", tags=["Appointment Management"])
async def get_appointment(
    item_id: str = Path(..., description="Appointment ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get specific appointment"""
    try:
        result = await complete_booking_service.get_appointment(
            user_id=current_user["_id"],
            appointment_id=item_id
        )
        
        if result.get("success"):
            return {
                "success": True,
                "data": result.get("data"),
                "message": result.get("message", "Appointment retrieved successfully")
            }
        else:
            raise HTTPException(status_code=404, detail=result.get("message", "Appointment not found"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting appointment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/appointments/{item_id}", tags=["Appointment Management"])
async def update_appointment(
    item_id: str = Path(..., description="Appointment ID"),
    appointment_data: dict = Body(..., description="Update data"),
    current_user: dict = Depends(get_current_user)
):
    """Update existing appointment"""
    try:
        result = await complete_booking_service.update_appointment(
            user_id=current_user["_id"],
            appointment_id=item_id,
            update_data=appointment_data
        )
        
        if result.get("success"):
            return {
                "success": True,
                "data": result.get("data"),
                "message": result.get("message", "Appointment updated successfully")
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Update failed"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating appointment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/appointments/{item_id}", tags=["Appointment Management"])
async def delete_appointment(
    item_id: str = Path(..., description="Appointment ID"),
    hard_delete: bool = Query(False, description="Permanently delete (cannot be undone)"),
    current_user: dict = Depends(get_current_user)
):
    """Delete appointment"""
    try:
        result = await complete_booking_service.delete_appointment(
            user_id=current_user["_id"],
            appointment_id=item_id,
            hard_delete=hard_delete
        )
        
        if result.get("success"):
            return {
                "success": True,
                "message": result.get("message", "Appointment deleted successfully")
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Delete failed"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting appointment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Analytics Endpoint
@router.get("/appointments/analytics", tags=["Appointment Analytics"])
async def get_appointment_analytics(
    period: str = Query("7d", description="Time period (7d, 30d, 90d, 1y)"),
    current_user: dict = Depends(get_current_user)
):
    """Get appointment analytics and metrics"""
    try:
        # This would be implemented based on service-specific analytics
        return {
            "success": True,
            "data": {
                "period": period,
                "total_appointments": 0,
                "active_appointments": 0,
                "growth_rate": 0.0,
                "last_updated": "2025-07-23T11:29:09.500836"
            },
            "message": "Appointment analytics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting appointment analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")
