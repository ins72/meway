"""
Booking API Routes

Provides API endpoints for booking system functionality including
appointment scheduling, availability management, and booking analytics.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional, Any
from services.booking_service import booking_service
from core.auth import get_current_user

router = APIRouter(prefix="/api/booking", tags=["Booking System"])

@router.get("/services")
async def get_booking_services(current_user: dict = Depends(get_current_user)):
    """Get all available booking services"""
    user_id = current_user.get("user_id")
    return await booking_service.get_booking_services(user_id)

@router.post("/services")
async def create_booking_service(
    service_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Create a new booking service"""
    user_id = current_user.get("user_id")
    return await booking_service.create_booking_service(user_id, service_data)

@router.get("/availability")
async def get_availability(
    current_user: dict = Depends(get_current_user),
    service_id: Optional[str] = None,
    date: Optional[str] = None
):
    """Get availability for booking services"""
    user_id = current_user.get("user_id")
    return await booking_service.get_availability(user_id, service_id, date)

@router.post("/appointments")
async def create_appointment(
    appointment_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Create a new appointment booking"""
    user_id = current_user.get("user_id")
    return await booking_service.create_appointment(user_id, appointment_data)

@router.get("/appointments")
async def get_appointments(
    current_user: dict = Depends(get_current_user),
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """Get user's appointments"""
    user_id = current_user.get("user_id")
    return await booking_service.get_appointments(user_id, status, date_from, date_to)

@router.put("/appointments/{appointment_id}")
async def update_appointment(
    appointment_id: str,
    update_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Update an existing appointment"""
    return await booking_service.update_appointment(appointment_id, update_data)

@router.delete("/appointments/{appointment_id}")
async def cancel_appointment(
    appointment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Cancel an appointment"""
    return await booking_service.cancel_appointment(appointment_id)

@router.get("/calendar")
async def get_booking_calendar(
    current_user: dict = Depends(get_current_user),
    month: Optional[str] = None,
    year: Optional[int] = None
):
    """Get booking calendar view"""
    user_id = current_user.get("user_id")
    return await booking_service.get_booking_calendar(user_id, month, year)

@router.get("/analytics")
async def get_booking_analytics(
    current_user: dict = Depends(get_current_user),
    period: Optional[str] = "30d"
):
    """Get booking analytics and statistics"""
    user_id = current_user.get("user_id")
    return await booking_service.get_booking_analytics(user_id, period)