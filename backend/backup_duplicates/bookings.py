"""
Booking System API Routes
Professional Mewayz Platform - Migrated from Monolithic Structure
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import uuid

from core.auth import get_current_active_user
from core.database import get_database
from services.user_service import get_user_service

router = APIRouter()

# Initialize service instances
user_service = get_user_service()

class ServiceCreate(BaseModel):
    name: str
    description: str
    duration_minutes: int
    price: float
    category: Optional[str] = "general"
    is_active: bool = True

class BookingCreate(BaseModel):
    service_id: str
    appointment_date: datetime
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    notes: Optional[str] = ""

def get_services_collection():
    """Get services collection"""
    db = get_database()
    return db.services

def get_bookings_collection():
    """Get bookings collection"""
    db = get_database()
    return db.bookings

@router.get("/services")
async def get_services(
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Get services with real database operations"""
    try:
        services_collection = get_services_collection()
        
        # Build query
        query = {"user_id": current_user["_id"], "is_active": True}
        if category:
            query["category"] = category
        
        # Get services
        services = await services_collection.find(query).sort("created_at", -1).to_list(length=None)
        
        # Get booking statistics for each service
        bookings_collection = get_bookings_collection()
        for service in services:
            # Count bookings for this service
            bookings_count = await bookings_collection.count_documents({
                "service_id": service["_id"],
                "status": {"$ne": "cancelled"}
            })
            
            # Calculate revenue
            revenue_pipeline = [
                {"$match": {
                    "service_id": service["_id"],
                    "status": {"$in": ["completed", "confirmed"]}
                }},
                {"$group": {
                    "_id": None,
                    "total_revenue": {"$sum": "$price"}
                }}
            ]
            
            revenue_stats = await bookings_collection.aggregate(revenue_pipeline).to_list(length=1)
            total_revenue = revenue_stats[0]["total_revenue"] if revenue_stats else 0
            
            service["analytics"] = {
                "total_bookings": bookings_count,
                "total_revenue": total_revenue
            }
        
        return {
            "success": True,
            "data": {
                "services": services,
                "total_services": len(services)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch services: {str(e)}"
        )

@router.post("/services")
async def create_service(
    service_data: ServiceCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create service with real database operations"""
    try:
        # Check user's plan limits
        user_stats = await user_service.get_user_stats(current_user["_id"])
        user_plan = user_stats["subscription_info"]["plan"]
        
        # Count existing services
        services_collection = get_services_collection()
        existing_services = await services_collection.count_documents({"user_id": current_user["_id"]})
        
        # Check limits
        max_services = 3 if user_plan == "free" else 20 if user_plan == "pro" else -1  # unlimited for enterprise
        if max_services != -1 and existing_services >= max_services:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Service limit reached ({max_services}). Upgrade your plan to add more services."
            )
        
        # Create service document
        service_doc = {
            "_id": str(uuid.uuid4()),
            "user_id": current_user["_id"],
            "name": service_data.name,
            "description": service_data.description,
            "duration_minutes": service_data.duration_minutes,
            "price": service_data.price,
            "category": service_data.category,
            "is_active": service_data.is_active,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "booking_settings": {
                "advance_booking_days": 30,
                "buffer_time_minutes": 15,
                "auto_confirm": True
            }
        }
        
        # Save to database
        await services_collection.insert_one(service_doc)
        
        return {
            "success": True,
            "message": "Service created successfully",
            "data": service_doc
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create service: {str(e)}"
        )

@router.get("/appointments")
async def get_appointments(
    date: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user)
):
    """Get appointments/bookings with real database operations"""
    try:
        bookings_collection = get_bookings_collection()
        
        # Build query
        query = {"provider_id": current_user["_id"]}
        if status_filter:
            query["status"] = status_filter
        if date:
            # Parse date and get bookings for that day
            try:
                target_date = datetime.strptime(date, "%Y-%m-%d")
                next_day = target_date + timedelta(days=1)
                query["appointment_date"] = {
                    "$gte": target_date,
                    "$lt": next_day
                }
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Use YYYY-MM-DD"
                )
        
        # Get bookings
        bookings = await bookings_collection.find(query).sort("appointment_date", 1).limit(limit).to_list(length=None)
        
        # Enhance bookings with service details
        services_collection = get_services_collection()
        for booking in bookings:
            service = await services_collection.find_one({"_id": booking["service_id"]})
            if service:
                booking["service_name"] = service["name"]
                booking["service_duration"] = service["duration_minutes"]
        
        return {
            "success": True,
            "data": {
                "appointments": bookings,
                "total_appointments": len(bookings)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch appointments: {str(e)}"
        )

@router.post("/appointments")
async def create_appointment(
    booking_data: BookingCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create appointment/booking with real database operations"""
    try:
        services_collection = get_services_collection()
        bookings_collection = get_bookings_collection()
        
        # Find service
        service = await services_collection.find_one({
            "_id": booking_data.service_id,
            "user_id": current_user["_id"]
        })
        
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
        
        # Check if time slot is available
        service_duration = service["duration_minutes"]
        appointment_start = booking_data.appointment_date
        appointment_end = appointment_start + timedelta(minutes=service_duration)
        
        # Check for conflicts
        existing_booking = await bookings_collection.find_one({
            "provider_id": current_user["_id"],
            "status": {"$nin": ["cancelled", "completed"]},
            "$or": [
                {
                    "appointment_date": {"$lt": appointment_end},
                    "appointment_end": {"$gt": appointment_start}
                }
            ]
        })
        
        if existing_booking:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Time slot is not available"
            )
        
        # Create booking document
        booking_doc = {
            "_id": str(uuid.uuid4()),
            "service_id": booking_data.service_id,
            "provider_id": current_user["_id"],
            "customer_name": booking_data.customer_name,
            "customer_email": booking_data.customer_email,
            "customer_phone": booking_data.customer_phone,
            "appointment_date": appointment_start,
            "appointment_end": appointment_end,
            "duration_minutes": service_duration,
            "price": service["price"],
            "status": "confirmed",
            "notes": booking_data.notes,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Save to database
        await bookings_collection.insert_one(booking_doc)
        
        # Update service booking count (for analytics)
        await services_collection.update_one(
            {"_id": booking_data.service_id},
            {"$inc": {"total_bookings": 1}}
        )
        
        return {
            "success": True,
            "message": "Appointment booked successfully",
            "data": booking_doc
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create appointment: {str(e)}"
        )

@router.get("/dashboard")
async def get_booking_dashboard(current_user: dict = Depends(get_current_active_user)):
    """Get booking system dashboard with real database calculations"""
    try:
        services_collection = get_services_collection()
        bookings_collection = get_bookings_collection()
        
        # Get real metrics
        total_services = await services_collection.count_documents({"user_id": current_user["_id"]})
        active_services = await services_collection.count_documents({"user_id": current_user["_id"], "is_active": True})
        
        # Get booking statistics
        total_bookings = await bookings_collection.count_documents({"provider_id": current_user["_id"]})
        confirmed_bookings = await bookings_collection.count_documents({
            "provider_id": current_user["_id"],
            "status": "confirmed"
        })
        completed_bookings = await bookings_collection.count_documents({
            "provider_id": current_user["_id"],
            "status": "completed"
        })
        
        # Calculate revenue
        revenue_pipeline = [
            {"$match": {
                "provider_id": current_user["_id"],
                "status": {"$in": ["completed", "confirmed"]}
            }},
            {"$group": {
                "_id": None,
                "total_revenue": {"$sum": "$price"},
                "avg_booking_value": {"$avg": "$price"}
            }}
        ]
        
        revenue_stats = await bookings_collection.aggregate(revenue_pipeline).to_list(length=1)
        revenue_data = revenue_stats[0] if revenue_stats else {"total_revenue": 0, "avg_booking_value": 0}
        
        # Get upcoming appointments
        now = datetime.utcnow()
        upcoming_appointments = await bookings_collection.find({
            "provider_id": current_user["_id"],
            "appointment_date": {"$gte": now},
            "status": "confirmed"
        }).sort("appointment_date", 1).limit(5).to_list(length=None)
        
        # Enhance with service details
        for appointment in upcoming_appointments:
            service = await services_collection.find_one({"_id": appointment["service_id"]})
            if service:
                appointment["service_name"] = service["name"]
        
        dashboard_data = {
            "overview": {
                "total_services": total_services,
                "active_services": active_services,
                "total_bookings": total_bookings,
                "confirmed_bookings": confirmed_bookings,
                "completed_bookings": completed_bookings,
                "total_revenue": round(revenue_data["total_revenue"], 2),
                "avg_booking_value": round(revenue_data["avg_booking_value"], 2)
            },
            "upcoming_appointments": upcoming_appointments,
            "performance_metrics": {
                "booking_completion_rate": round((completed_bookings / max(total_bookings, 1)) * 100, 1),
                "average_booking_value": round(revenue_data["avg_booking_value"], 2),
                "occupancy_rate": 0.0  # Would be calculated from available vs booked time slots
            }
        }
        
        return {
            "success": True,
            "data": dashboard_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch booking dashboard: {str(e)}"
        )

@router.put("/appointments/{appointment_id}/status")
async def update_appointment_status(
    appointment_id: str,
    status: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Update appointment status with real database operations"""
    try:
        bookings_collection = get_bookings_collection()
        
        # Validate status
        valid_statuses = ["confirmed", "completed", "cancelled", "no_show"]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Update booking status
        result = await bookings_collection.update_one(
            {
                "_id": appointment_id,
                "provider_id": current_user["_id"]
            },
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        return {
            "success": True,
            "message": f"Appointment status updated to {status}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update appointment status: {str(e)}"
        )