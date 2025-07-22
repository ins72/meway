"""
Booking Services Business Logic
Professional Mewayz Platform
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from core.database import get_database
import uuid

class BookingService:
    """Service for booking operations"""
    
    @staticmethod
    async def get_bookings(user_id: str):
        """Get user's bookings"""
        db = await get_database()
        
        bookings = await db.bookings.find({"user_id": user_id}).sort("booking_date", 1).to_list(length=None)
        return bookings
    
    @staticmethod
    async def create_booking(user_id: str, booking_data: Dict[str, Any]):
        """Create new booking"""
        db = await get_database()
        
        booking = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "service_name": booking_data.get("service_name"),
            "booking_date": datetime.fromisoformat(booking_data.get("booking_date")),
            "duration": booking_data.get("duration", 60),
            "status": "confirmed",
            "customer_info": booking_data.get("customer_info"),
            "notes": booking_data.get("notes", ""),
            "created_at": datetime.utcnow()
        }
        
        result = await db.bookings.insert_one(booking)
        return booking
    
    @staticmethod
    async def get_availability(user_id: str, date: str):
        """Get availability for a specific date"""
        db = await get_database()
        
        # Get existing bookings for the date
        start_date = datetime.fromisoformat(date)
        end_date = start_date + timedelta(days=1)
        
        existing_bookings = await db.bookings.find({
            "user_id": user_id,
            "booking_date": {"$gte": start_date, "$lt": end_date}
        }).to_list(length=None)
        
        # Generate available slots (simplified)
        available_slots = []
        for hour in range(9, 17):  # 9 AM to 5 PM
            slot_time = start_date.replace(hour=hour, minute=0)
            is_available = not any(
                booking["booking_date"] <= slot_time < 
                booking["booking_date"] + timedelta(minutes=booking["duration"])
                for booking in existing_bookings
            )
            
            if is_available:
                available_slots.append(slot_time.isoformat())
        
        return {"date": date, "available_slots": available_slots}
    
    @staticmethod
    async def get_booking_services(user_id: str):
        """Get all available booking services"""
        return {
            "success": True,
            "data": {
                "services": [
                    {
                        "id": str(uuid.uuid4()),
                        "name": "Business Consultation",
                        "description": "Strategic business planning and consultation",
                        "duration": 60,
                        "price": 150.00,
                        "category": "consulting",
                        "available": True
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "name": "Technical Support",
                        "description": "Technical assistance and troubleshooting",
                        "duration": 30,
                        "price": 75.00,
                        "category": "support",
                        "available": True
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "name": "Training Session",
                        "description": "Personalized training and skill development",
                        "duration": 90,
                        "price": 200.00,
                        "category": "training",
                        "available": True
                    }
                ],
                "total_services": 3
            }
        }

# Global service instance
booking_service = BookingService()
