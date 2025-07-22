"""
Complete Booking System API
Comprehensive appointment scheduling with calendar integration and real data
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field, EmailStr

from core.auth import get_current_user
from services.complete_booking_service import complete_booking_service, BookingStatus, RecurrenceType, NotificationMethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class ServiceCreateRequest(BaseModel):
    name: str = Field(..., description="Service name", min_length=3, max_length=100)
    description: str = Field("", description="Service description", max_length=500)
    duration_minutes: int = Field(60, description="Service duration in minutes", ge=15, le=480)
    price: float = Field(0.0, description="Service price", ge=0)
    category: str = Field("general", description="Service category")
    settings: Optional[Dict[str, Any]] = Field(None, description="Service settings")

class ServiceUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    price: Optional[float] = Field(None, ge=0)
    category: Optional[str] = None
    is_active: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None

class AvailabilitySetRequest(BaseModel):
    availability_data: List[Dict[str, Any]] = Field(..., description="Availability schedule")

class BookingCreateRequest(BaseModel):
    service_id: str = Field(..., description="Service ID to book")
    booking_datetime: datetime = Field(..., description="Booking date and time")
    customer_info: Dict[str, Any] = Field(..., description="Customer information")
    notes: str = Field("", description="Additional notes", max_length=500)
    notification_preferences: List[str] = Field([NotificationMethod.EMAIL.value], description="Notification preferences")

class BookingUpdateRequest(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    customer_info: Optional[Dict[str, Any]] = None

class BookingRescheduleRequest(BaseModel):
    new_datetime: datetime = Field(..., description="New booking date and time")
    notes: str = Field("", description="Reschedule notes", max_length=500)

# Service Management Endpoints
@router.post("/services", tags=["Booking System"])
async def create_service(
    service_data: ServiceCreateRequest,
    user = Depends(get_current_user)
):
    """Create a bookable service with real data persistence"""
    try:
        result = await complete_booking_service.create_service(
            provider_id=user.get('_id') or user.get('id') or user.get('user_id'),
            name=service_data.name,
            description=service_data.description,
            duration_minutes=service_data.duration_minutes,
            price=service_data.price,
            category=service_data.category,
            settings=service_data.settings
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create service")
        
        return {
            "success": True,
            "message": "Service created successfully",
            "service": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create service error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/services", tags=["Booking System"])
async def get_provider_services(
    user = Depends(get_current_user),
    active_only: bool = Query(True, description="Show only active services")
):
    """Get all services for the current user (provider)"""
    try:
        services = await complete_booking_service.get_provider_services(
            provider_id=user.get('_id') or user.get('id') or user.get('user_id'),
            active_only=active_only
        )
        
        return {
            "success": True,
            "services": services,
            "total_count": len(services),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get provider services error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/services/{service_id}", tags=["Booking System"])
async def update_service(
    service_id: str,
    service_data: ServiceUpdateRequest,
    user = Depends(get_current_user)
):
    """Update service with real data persistence"""
    try:
        result = await complete_booking_service.update_service(
            service_id=service_id,
            provider_id=user.get('_id') or user.get('id') or user.get('user_id'),
            update_data=service_data.dict(exclude_unset=True)
        )
        
        if not result:
            raise HTTPException(
                status_code=404, 
                detail="Service not found or update failed"
            )
        
        return {
            "success": True,
            "message": "Service updated successfully",
            "service": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update service error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Availability Management Endpoints
@router.post("/services/{service_id}/availability", tags=["Booking System"])
async def set_service_availability(
    service_id: str,
    availability_data: AvailabilitySetRequest,
    user = Depends(get_current_user)
):
    """Set availability schedule for a service"""
    try:
        success = await complete_booking_service.set_availability(
            provider_id=user.get('_id') or user.get('id') or user.get('user_id'),
            service_id=service_id,
            availability_data=availability_data.availability_data
        )
        
        if not success:
            raise HTTPException(
                status_code=400, 
                detail="Failed to set availability - service not found or invalid data"
            )
        
        return {
            "success": True,
            "message": "Availability set successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set service availability error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/services/{service_id}/available-slots", tags=["Booking System"])
async def get_available_slots(
    service_id: str,
    start_date: datetime = Query(..., description="Start date for slot search"),
    end_date: datetime = Query(..., description="End date for slot search"),
    user = Depends(get_current_user)
):
    """Get available booking slots for a service in a date range"""
    try:
        # Validate date range
        if end_date <= start_date:
            raise HTTPException(status_code=400, detail="End date must be after start date")
        
        if (end_date - start_date).days > 90:
            raise HTTPException(status_code=400, detail="Date range cannot exceed 90 days")
        
        slots = await complete_booking_service.get_available_slots(
            service_id=service_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "success": True,
            "available_slots": slots,
            "total_slots": len(slots),
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get available slots error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Booking Management Endpoints
@router.post("/bookings", tags=["Booking System"])
async def create_booking(
    booking_data: BookingCreateRequest,
    user = Depends(get_current_user)
):
    """Create a new booking with real data persistence"""
    try:
        result = await complete_booking_service.create_booking(
            service_id=booking_data.service_id,
            customer_id=user.get('_id') or user.get('id') or user.get('user_id'),
            booking_datetime=booking_data.booking_datetime,
            customer_info=booking_data.customer_info,
            notes=booking_data.notes,
            notification_preferences=booking_data.notification_preferences
        )
        
        if not result:
            raise HTTPException(
                status_code=400, 
                detail="Failed to create booking - service not found or slot not available"
            )
        
        return {
            "success": True,
            "message": "Booking created successfully",
            "booking": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create booking error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bookings", tags=["Booking System"])
async def get_user_bookings(
    user = Depends(get_current_user),
    user_type: str = Query("customer", description="User type: customer or provider"),
    status_filter: Optional[str] = Query(None, description="Filter by booking status"),
    start_date: Optional[datetime] = Query(None, description="Filter bookings from this date")
):
    """Get bookings for the current user"""
    try:
        # Validate user_type
        if user_type not in ["customer", "provider"]:
            raise HTTPException(status_code=400, detail="user_type must be 'customer' or 'provider'")
        
        # Validate status_filter
        if status_filter and status_filter not in [status.value for status in BookingStatus]:
            raise HTTPException(status_code=400, detail="Invalid status filter")
        
        bookings = await complete_booking_service.get_user_bookings(
            user_id=user.get('_id') or user.get('id') or user.get('user_id'),
            user_type=user_type,
            status_filter=status_filter,
            start_date=start_date
        )
        
        return {
            "success": True,
            "bookings": bookings,
            "total_count": len(bookings),
            "user_type": user_type,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user bookings error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/bookings/{booking_id}/status", tags=["Booking System"])
async def update_booking_status(
    booking_id: str,
    status_data: Dict[str, str] = Body(..., description="Status update data"),
    user = Depends(get_current_user)
):
    """Update booking status with proper validation"""
    try:
        new_status = status_data.get('status')
        notes = status_data.get('notes', '')
        
        if not new_status:
            raise HTTPException(status_code=400, detail="Status is required")
        
        # Validate status
        if new_status not in [status.value for status in BookingStatus]:
            raise HTTPException(status_code=400, detail="Invalid booking status")
        
        result = await complete_booking_service.update_booking_status(
            booking_id=booking_id,
            new_status=new_status,
            notes=notes,
            user_id=user.get('_id') or user.get('id') or user.get('user_id')
        )
        
        if not result:
            raise HTTPException(
                status_code=404, 
                detail="Booking not found or status update failed"
            )
        
        return {
            "success": True,
            "message": "Booking status updated successfully",
            "booking": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update booking status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/bookings/{booking_id}/reschedule", tags=["Booking System"])
async def reschedule_booking(
    booking_id: str,
    reschedule_data: BookingRescheduleRequest,
    user = Depends(get_current_user)
):
    """Reschedule a booking to a new time slot"""
    try:
        result = await complete_booking_service.reschedule_booking(
            booking_id=booking_id,
            new_datetime=reschedule_data.new_datetime,
            user_id=user.get('_id') or user.get('id') or user.get('user_id'),
            notes=reschedule_data.notes
        )
        
        if not result:
            raise HTTPException(
                status_code=400, 
                detail="Failed to reschedule booking - booking not found or new slot not available"
            )
        
        return {
            "success": True,
            "message": "Booking rescheduled successfully",
            "booking": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reschedule booking error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics and Reporting Endpoints
@router.get("/analytics/provider", tags=["Booking System"])
async def get_booking_analytics(
    user = Depends(get_current_user),
    start_date: Optional[datetime] = Query(None, description="Analytics start date"),
    end_date: Optional[datetime] = Query(None, description="Analytics end date")
):
    """Get booking analytics for a provider"""
    try:
        analytics = await complete_booking_service.get_booking_analytics(
            provider_id=user.get('_id') or user.get('id') or user.get('user_id'),
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "success": True,
            "analytics": analytics,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get booking analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard", tags=["Booking System"])
async def get_booking_dashboard(
    user = Depends(get_current_user)
):
    """Get booking dashboard data for a provider"""
    try:
        dashboard = await complete_booking_service.get_booking_dashboard(
            provider_id=user.get('_id') or user.get('id') or user.get('user_id')
        )
        
        return {
            "success": True,
            "dashboard": dashboard,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get booking dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Status and Information Endpoints
@router.get("/statuses", tags=["Booking System"])
async def get_booking_statuses():
    """Get all available booking statuses"""
    try:
        statuses = [
            {
                "status": status.value,
                "description": f"{status.value.title()} booking status"
            }
            for status in BookingStatus
        ]
        
        return {
            "success": True,
            "statuses": statuses,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get booking statuses error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notification-methods", tags=["Booking System"])
async def get_notification_methods():
    """Get all available notification methods"""
    try:
        methods = [
            {
                "method": method.value,
                "description": f"{method.value.title()} notifications"
            }
            for method in NotificationMethod
        ]
        
        return {
            "success": True,
            "notification_methods": methods,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get notification methods error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", tags=["Booking System"])
async def booking_health_check():
    """Health check for booking system"""
    return {
        "status": "healthy",
        "service": "Complete Booking System",
        "features": [
            "Service Management",
            "Availability Scheduling",
            "Booking Management",
            "Real-time Slot Availability",
            "Notification System",
            "Analytics & Reporting",
            "Provider Dashboard",
            "Multi-status Booking Workflow"
        ],
        "supported_statuses": [status.value for status in BookingStatus],
        "notification_methods": [method.value for method in NotificationMethod],
        "timestamp": datetime.utcnow().isoformat()
    }