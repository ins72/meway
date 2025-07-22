"""
Bookings Management Services Business Logic
Professional Mewayz Platform
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from core.database import get_database
import uuid

class BookingsService:
    """Service for bookings management operations"""
    
    @staticmethod
    async def get_user_bookings(user_id: str, booking_type: str = "all"):
        """Get user's bookings"""
        db = await get_database()
        
        query = {"user_id": user_id}
        if booking_type != "all":
            query["status"] = booking_type
        
        bookings = await db.bookings.find(query).sort("booking_date", 1).to_list(length=None)
        return bookings
    
    @staticmethod
    async def create_booking(user_id: str, booking_data: Dict[str, Any]):
        """Create new booking"""
        db = await get_database()
        
        booking = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "service_id": booking_data.get("service_id"),
            "service_name": booking_data.get("service_name"),
            "booking_date": datetime.fromisoformat(booking_data.get("booking_date")),
            "duration": booking_data.get("duration", 60),  # minutes
            "price": booking_data.get("price", 0),
            "currency": booking_data.get("currency", "USD"),
            "customer_info": {
                "name": booking_data.get("customer_name"),
                "email": booking_data.get("customer_email"),
                "phone": booking_data.get("customer_phone"),
                "notes": booking_data.get("customer_notes", "")
            },
            "status": "confirmed",
            "payment_status": booking_data.get("payment_status", "pending"),
            "payment_method": booking_data.get("payment_method"),
            "location": booking_data.get("location"),
            "meeting_link": booking_data.get("meeting_link"),
            "reminder_sent": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.bookings.insert_one(booking)
        return booking
    
    @staticmethod
    async def get_booking_services(user_id: str):
        """Get user's booking services"""
        db = await get_database()
        
        services = await db.booking_services.find({"user_id": user_id}).to_list(length=None)
        if not services:
            # Create default service
            default_service = {
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": "Consultation",
                "description": "30-minute consultation",
                "duration": 30,
                "price": 0,
                "currency": "USD",
                "availability": {
                    "monday": {"enabled": True, "start": "09:00", "end": "17:00"},
                    "tuesday": {"enabled": True, "start": "09:00", "end": "17:00"},
                    "wednesday": {"enabled": True, "start": "09:00", "end": "17:00"},
                    "thursday": {"enabled": True, "start": "09:00", "end": "17:00"},
                    "friday": {"enabled": True, "start": "09:00", "end": "17:00"},
                    "saturday": {"enabled": False},
                    "sunday": {"enabled": False}
                },
                "booking_buffer": 15,  # minutes between bookings
                "advance_booking": 24,  # hours in advance
                "max_advance_booking": 720,  # hours (30 days)
                "status": "active",
                "created_at": datetime.utcnow()
            }
            await db.booking_services.insert_one(default_service)
            services = [default_service]
        
        return services
    
    @staticmethod
    async def get_availability(user_id: str, service_id: str, date: str):
        """Get available time slots for a service on a specific date"""
        db = await get_database()
        
        # Get service details
        service = await db.booking_services.find_one({
            "_id": service_id,
            "user_id": user_id
        })
        if not service:
            return {"available_slots": []}
        
        booking_date = datetime.fromisoformat(date).date()
        day_name = booking_date.strftime("%A").lower()
        
        # Check if service is available on this day
        day_availability = service.get("availability", {}).get(day_name, {})
        if not day_availability.get("enabled", False):
            return {"available_slots": []}
        
        # Get existing bookings for the date
        start_datetime = datetime.combine(booking_date, datetime.min.time())
        end_datetime = start_datetime + timedelta(days=1)
        
        existing_bookings = await db.bookings.find({
            "user_id": user_id,
            "service_id": service_id,
            "booking_date": {"$gte": start_datetime, "$lt": end_datetime},
            "status": {"$in": ["confirmed", "pending"]}
        }).to_list(length=None)
        
        # Generate time slots
        start_time = datetime.strptime(day_availability["start"], "%H:%M").time()
        end_time = datetime.strptime(day_availability["end"], "%H:%M").time()
        duration = service.get("duration", 30)
        buffer_time = service.get("booking_buffer", 15)
        
        slots = []
        current_time = datetime.combine(booking_date, start_time)
        end_datetime_today = datetime.combine(booking_date, end_time)
        
        while current_time < end_datetime_today:
            # Check if slot is available
            slot_end = current_time + timedelta(minutes=duration)
            
            is_available = True
            for booking in existing_bookings:
                booking_end = booking["booking_date"] + timedelta(minutes=booking["duration"])
                if (current_time < booking_end and slot_end > booking["booking_date"]):
                    is_available = False
                    break
            
            if is_available:
                slots.append({
                    "time": current_time.strftime("%H:%M"),
                    "datetime": current_time.isoformat(),
                    "available": True
                })
            
            current_time += timedelta(minutes=duration + buffer_time)
        
        return {
            "date": date,
            "service_id": service_id,
            "available_slots": slots
        }
    
    @staticmethod
    async def update_booking_status(booking_id: str, user_id: str, status: str):
        """Update booking status"""
        db = await get_database()
        
        result = await db.bookings.update_one(
            {"_id": booking_id, "user_id": user_id},
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0

# Global service instance
bookings_service = BookingsService()
