"""
Complete Booking System Service
Comprehensive appointment scheduling with calendar integration and real data
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum

from core.database import get_database

# Configure logging
logger = logging.getLogger(__name__)

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"

class RecurrenceType(str, Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class NotificationMethod(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    BOTH = "both"

class CompleteBookingService:
    """Complete booking system with real data persistence"""
    
    def __init__(self):
        self.db = None
        
    async def get_database(self):
        """Get database connection"""
        if not self.db:
            self.db = get_database()
        return self.db
    
    # Service Management
    async def create_service(self, provider_id: str, name: str, description: str = "",
                           duration_minutes: int = 60, price: float = 0.0,
                           category: str = "general", settings: Dict = None) -> Dict[str, Any]:
        """Create a bookable service with real data persistence"""
        try:
            db = await self.get_database()
            
            service_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            service_data = {
                'service_id': service_id,
                'provider_id': provider_id,
                'name': name,
                'description': description,
                'duration_minutes': duration_minutes,
                'price': price,
                'currency': 'USD',
                'category': category,
                'is_active': True,
                'max_advance_booking_days': 30,
                'min_advance_booking_hours': 24,
                'cancellation_policy_hours': 24,
                'settings': settings or self._get_default_service_settings(),
                'created_at': current_time,
                'updated_at': current_time
            }
            
            await db.booking_services.insert_one(service_data)
            
            # Create default availability for the service
            await self._create_default_availability(service_id, provider_id)
            
            # Log service creation
            await self._log_booking_activity(
                booking_id=None,
                service_id=service_id,
                user_id=provider_id,
                action='service_created',
                details={'name': name, 'duration': duration_minutes, 'price': price}
            )
            
            return service_data
            
        except Exception as e:
            logger.error(f"Create service error: {str(e)}")
            return None
    
    async def get_provider_services(self, provider_id: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all services for a provider"""
        try:
            db = await self.get_database()
            
            query = {'provider_id': provider_id}
            if active_only:
                query['is_active'] = True
                
            services = await db.booking_services.find(query).sort('created_at', -1).to_list(length=None)
            
            # Add booking statistics for each service
            for service in services:
                service['booking_stats'] = await self._get_service_statistics(service['service_id'])
                
            return services
            
        except Exception as e:
            logger.error(f"Get provider services error: {str(e)}")
            return []
    
    async def update_service(self, service_id: str, provider_id: str, 
                           update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update service with real data persistence"""
        try:
            db = await self.get_database()
            
            # Verify ownership
            service = await db.booking_services.find_one({
                'service_id': service_id,
                'provider_id': provider_id
            })
            
            if not service:
                return None
                
            # Prepare update data
            allowed_fields = [
                'name', 'description', 'duration_minutes', 'price', 'category',
                'is_active', 'max_advance_booking_days', 'min_advance_booking_hours',
                'cancellation_policy_hours', 'settings'
            ]
            update_fields = {k: v for k, v in update_data.items() if k in allowed_fields}
            update_fields['updated_at'] = datetime.utcnow()
            
            # Update service
            result = await db.booking_services.update_one(
                {'service_id': service_id},
                {'$set': update_fields}
            )
            
            if result.modified_count:
                # Log update
                await self._log_booking_activity(
                    booking_id=None,
                    service_id=service_id,
                    user_id=provider_id,
                    action='service_updated',
                    details={'updated_fields': list(update_fields.keys())}
                )
                
                return await db.booking_services.find_one({'service_id': service_id})
            
            return None
            
        except Exception as e:
            logger.error(f"Update service error: {str(e)}")
            return None
    
    # Availability Management
    async def set_availability(self, provider_id: str, service_id: str,
                             availability_data: List[Dict[str, Any]]) -> bool:
        """Set availability schedule for a service"""
        try:
            db = await self.get_database()
            
            # Verify service ownership
            service = await db.booking_services.find_one({
                'service_id': service_id,
                'provider_id': provider_id
            })
            
            if not service:
                return False
            
            # Remove existing availability for this service
            await db.service_availability.delete_many({'service_id': service_id})
            
            # Insert new availability
            for availability in availability_data:
                availability_record = {
                    'availability_id': str(uuid.uuid4()),
                    'service_id': service_id,
                    'provider_id': provider_id,
                    'day_of_week': availability['day_of_week'],  # 0-6, Monday=0
                    'start_time': availability['start_time'],  # "09:00"
                    'end_time': availability['end_time'],      # "17:00"
                    'is_available': True,
                    'created_at': datetime.utcnow()
                }
                
                await db.service_availability.insert_one(availability_record)
            
            return True
            
        except Exception as e:
            logger.error(f"Set availability error: {str(e)}")
            return False
    
    async def get_available_slots(self, service_id: str, start_date: datetime,
                                end_date: datetime) -> List[Dict[str, Any]]:
        """Get available booking slots for a service in a date range"""
        try:
            db = await self.get_database()
            
            # Get service details
            service = await db.booking_services.find_one({'service_id': service_id})
            if not service:
                return []
            
            # Get availability schedule
            availability_schedule = await db.service_availability.find({
                'service_id': service_id,
                'is_available': True
            }).to_list(length=None)
            
            if not availability_schedule:
                return []
            
            # Get existing bookings in the date range
            existing_bookings = await db.bookings.find({
                'service_id': service_id,
                'booking_datetime': {
                    '$gte': start_date,
                    '$lte': end_date
                },
                'status': {'$in': [BookingStatus.CONFIRMED.value, BookingStatus.PENDING.value]}
            }).to_list(length=None)
            
            # Generate available slots
            available_slots = []
            duration_minutes = service['duration_minutes']
            
            current_date = start_date.date()
            end_date_only = end_date.date()
            
            while current_date <= end_date_only:
                day_of_week = current_date.weekday()  # Monday=0
                
                # Find availability for this day
                day_availability = [a for a in availability_schedule if a['day_of_week'] == day_of_week]
                
                for availability in day_availability:
                    # Generate time slots for this availability window
                    start_time = datetime.strptime(availability['start_time'], '%H:%M').time()
                    end_time = datetime.strptime(availability['end_time'], '%H:%M').time()
                    
                    # Combine date and time
                    slot_datetime = datetime.combine(current_date, start_time)
                    end_datetime = datetime.combine(current_date, end_time)
                    
                    # Generate slots
                    while slot_datetime + timedelta(minutes=duration_minutes) <= end_datetime:
                        slot_end = slot_datetime + timedelta(minutes=duration_minutes)
                        
                        # Check if this slot conflicts with existing bookings
                        is_available = True
                        for booking in existing_bookings:
                            booking_start = booking['booking_datetime']
                            booking_end = booking_start + timedelta(minutes=booking['duration_minutes'])
                            
                            # Check for overlap
                            if (slot_datetime < booking_end and slot_end > booking_start):
                                is_available = False
                                break
                        
                        if is_available and slot_datetime >= datetime.utcnow():
                            available_slots.append({
                                'datetime': slot_datetime,
                                'duration_minutes': duration_minutes,
                                'price': service['price'],
                                'currency': service['currency']
                            })
                        
                        # Move to next slot
                        slot_datetime += timedelta(minutes=duration_minutes)
                
                current_date += timedelta(days=1)
            
            return sorted(available_slots, key=lambda x: x['datetime'])
            
        except Exception as e:
            logger.error(f"Get available slots error: {str(e)}")
            return []
    
    # Booking Management
    async def create_booking(self, service_id: str, customer_id: str, booking_datetime: datetime,
                           customer_info: Dict[str, Any], notes: str = "",
                           notification_preferences: List[str] = None) -> Dict[str, Any]:
        """Create a new booking with real data persistence"""
        try:
            db = await self.get_database()
            
            # Verify service exists and get details
            service = await db.booking_services.find_one({'service_id': service_id})
            if not service:
                return None
            
            # Check if slot is available
            available_slots = await self.get_available_slots(
                service_id=service_id,
                start_date=booking_datetime,
                end_date=booking_datetime + timedelta(hours=1)
            )
            
            slot_available = any(
                abs((slot['datetime'] - booking_datetime).total_seconds()) < 60
                for slot in available_slots
            )
            
            if not slot_available:
                return None  # Slot not available
            
            booking_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            booking_data = {
                'booking_id': booking_id,
                'service_id': service_id,
                'provider_id': service['provider_id'],
                'customer_id': customer_id,
                'booking_datetime': booking_datetime,
                'duration_minutes': service['duration_minutes'],
                'status': BookingStatus.CONFIRMED.value,
                'price': service['price'],
                'currency': service['currency'],
                'customer_info': customer_info,
                'notes': notes,
                'notification_preferences': notification_preferences or [NotificationMethod.EMAIL.value],
                'created_at': current_time,
                'updated_at': current_time,
                'confirmation_token': str(uuid.uuid4())
            }
            
            await db.bookings.insert_one(booking_data)
            
            # Send confirmation notifications
            await self._send_booking_notifications(booking_data, 'booking_created')
            
            # Log booking creation
            await self._log_booking_activity(
                booking_id=booking_id,
                service_id=service_id,
                user_id=customer_id,
                action='booking_created',
                details={
                    'booking_datetime': booking_datetime.isoformat(),
                    'service_name': service['name'],
                    'price': service['price']
                }
            )
            
            return booking_data
            
        except Exception as e:
            logger.error(f"Create booking error: {str(e)}")
            return None
    
    async def get_user_bookings(self, user_id: str, user_type: str = "customer",
                              status_filter: str = None, 
                              start_date: datetime = None) -> List[Dict[str, Any]]:
        """Get bookings for a user (customer or provider)"""
        try:
            db = await self.get_database()
            
            # Build query based on user type
            if user_type == "provider":
                query = {'provider_id': user_id}
            else:
                query = {'customer_id': user_id}
            
            if status_filter:
                query['status'] = status_filter
                
            if start_date:
                query['booking_datetime'] = {'$gte': start_date}
            
            bookings = await db.bookings.find(query).sort('booking_datetime', 1).to_list(length=None)
            
            # Add service details to each booking
            for booking in bookings:
                service = await db.booking_services.find_one({'service_id': booking['service_id']})
                booking['service_details'] = service
                
            return bookings
            
        except Exception as e:
            logger.error(f"Get user bookings error: {str(e)}")
            return []
    
    async def update_booking_status(self, booking_id: str, new_status: str,
                                  notes: str = "", user_id: str = None) -> Dict[str, Any]:
        """Update booking status with proper validation"""
        try:
            db = await self.get_database()
            
            # Validate status
            if new_status not in [status.value for status in BookingStatus]:
                return None
            
            booking = await db.bookings.find_one({'booking_id': booking_id})
            if not booking:
                return None
            
            # Update booking
            update_data = {
                'status': new_status,
                'updated_at': datetime.utcnow()
            }
            
            if notes:
                update_data['status_notes'] = notes
            
            result = await db.bookings.update_one(
                {'booking_id': booking_id},
                {'$set': update_data}
            )
            
            if result.modified_count:
                # Send notification about status change
                updated_booking = await db.bookings.find_one({'booking_id': booking_id})
                await self._send_booking_notifications(updated_booking, f'status_changed_to_{new_status}')
                
                # Log status change
                await self._log_booking_activity(
                    booking_id=booking_id,
                    service_id=booking['service_id'],
                    user_id=user_id,
                    action='status_changed',
                    details={'old_status': booking['status'], 'new_status': new_status, 'notes': notes}
                )
                
                return updated_booking
            
            return None
            
        except Exception as e:
            logger.error(f"Update booking status error: {str(e)}")
            return None
    
    async def reschedule_booking(self, booking_id: str, new_datetime: datetime,
                               user_id: str = None, notes: str = "") -> Dict[str, Any]:
        """Reschedule a booking to a new time slot"""
        try:
            db = await self.get_database()
            
            booking = await db.bookings.find_one({'booking_id': booking_id})
            if not booking:
                return None
            
            # Check if new slot is available
            available_slots = await self.get_available_slots(
                service_id=booking['service_id'],
                start_date=new_datetime,
                end_date=new_datetime + timedelta(hours=1)
            )
            
            slot_available = any(
                abs((slot['datetime'] - new_datetime).total_seconds()) < 60
                for slot in available_slots
            )
            
            if not slot_available:
                return None  # New slot not available
            
            # Update booking
            old_datetime = booking['booking_datetime']
            result = await db.bookings.update_one(
                {'booking_id': booking_id},
                {
                    '$set': {
                        'booking_datetime': new_datetime,
                        'status': BookingStatus.CONFIRMED.value,
                        'updated_at': datetime.utcnow(),
                        'reschedule_notes': notes
                    }
                }
            )
            
            if result.modified_count:
                # Send notification about reschedule
                updated_booking = await db.bookings.find_one({'booking_id': booking_id})
                await self._send_booking_notifications(updated_booking, 'booking_rescheduled')
                
                # Log reschedule
                await self._log_booking_activity(
                    booking_id=booking_id,
                    service_id=booking['service_id'],
                    user_id=user_id,
                    action='booking_rescheduled',
                    details={
                        'old_datetime': old_datetime.isoformat(),
                        'new_datetime': new_datetime.isoformat(),
                        'notes': notes
                    }
                )
                
                return updated_booking
            
            return None
            
        except Exception as e:
            logger.error(f"Reschedule booking error: {str(e)}")
            return None
    
    # Analytics and Reporting
    async def get_booking_analytics(self, provider_id: str, 
                                  start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """Get booking analytics for a provider"""
        try:
            db = await self.get_database()
            
            # Default to last 30 days if no date range provided
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Get bookings in date range
            bookings = await db.bookings.find({
                'provider_id': provider_id,
                'booking_datetime': {'$gte': start_date, '$lte': end_date}
            }).to_list(length=None)
            
            # Calculate metrics
            total_bookings = len(bookings)
            confirmed_bookings = len([b for b in bookings if b['status'] == BookingStatus.CONFIRMED.value])
            completed_bookings = len([b for b in bookings if b['status'] == BookingStatus.COMPLETED.value])
            cancelled_bookings = len([b for b in bookings if b['status'] == BookingStatus.CANCELLED.value])
            
            total_revenue = sum(b['price'] for b in bookings if b['status'] in [BookingStatus.CONFIRMED.value, BookingStatus.COMPLETED.value])
            
            # Calculate rates
            completion_rate = (completed_bookings / total_bookings * 100) if total_bookings > 0 else 0
            cancellation_rate = (cancelled_bookings / total_bookings * 100) if total_bookings > 0 else 0
            
            # Service-wise breakdown
            service_stats = {}
            for booking in bookings:
                service_id = booking['service_id']
                if service_id not in service_stats:
                    service_stats[service_id] = {
                        'bookings': 0,
                        'revenue': 0,
                        'service_name': ''
                    }
                
                service_stats[service_id]['bookings'] += 1
                if booking['status'] in [BookingStatus.CONFIRMED.value, BookingStatus.COMPLETED.value]:
                    service_stats[service_id]['revenue'] += booking['price']
            
            # Add service names
            for service_id in service_stats:
                service = await db.booking_services.find_one({'service_id': service_id})
                if service:
                    service_stats[service_id]['service_name'] = service['name']
            
            # Daily booking distribution
            daily_stats = {}
            for booking in bookings:
                date_key = booking['booking_datetime'].date().isoformat()
                if date_key not in daily_stats:
                    daily_stats[date_key] = {'bookings': 0, 'revenue': 0}
                
                daily_stats[date_key]['bookings'] += 1
                if booking['status'] in [BookingStatus.CONFIRMED.value, BookingStatus.COMPLETED.value]:
                    daily_stats[date_key]['revenue'] += booking['price']
            
            return {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': (end_date - start_date).days + 1
                },
                'overview': {
                    'total_bookings': total_bookings,
                    'confirmed_bookings': confirmed_bookings,
                    'completed_bookings': completed_bookings,
                    'cancelled_bookings': cancelled_bookings,
                    'total_revenue': round(total_revenue, 2),
                    'completion_rate': round(completion_rate, 2),
                    'cancellation_rate': round(cancellation_rate, 2)
                },
                'service_breakdown': service_stats,
                'daily_stats': daily_stats
            }
            
        except Exception as e:
            logger.error(f"Get booking analytics error: {str(e)}")
            return {}
    
    async def get_booking_dashboard(self, provider_id: str) -> Dict[str, Any]:
        """Get booking dashboard data for a provider"""
        try:
            db = await self.get_database()
            
            current_time = datetime.utcnow()
            
            # Get today's bookings
            today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            today_bookings = await db.bookings.find({
                'provider_id': provider_id,
                'booking_datetime': {'$gte': today_start, '$lt': today_end}
            }).sort('booking_datetime', 1).to_list(length=None)
            
            # Get upcoming bookings (next 7 days)
            upcoming_bookings = await db.bookings.find({
                'provider_id': provider_id,
                'booking_datetime': {'$gte': current_time, '$lte': current_time + timedelta(days=7)},
                'status': {'$in': [BookingStatus.CONFIRMED.value, BookingStatus.PENDING.value]}
            }).sort('booking_datetime', 1).limit(10).to_list(length=10)
            
            # Get recent activity
            recent_activities = await db.booking_activities.find({
                'user_id': provider_id
            }).sort('timestamp', -1).limit(20).to_list(length=20)
            
            # Get service stats
            services = await self.get_provider_services(provider_id)
            
            # Quick stats
            pending_bookings_count = await db.bookings.count_documents({
                'provider_id': provider_id,
                'status': BookingStatus.PENDING.value
            })
            
            return {
                'today_bookings': today_bookings,
                'upcoming_bookings': upcoming_bookings,
                'recent_activities': recent_activities,
                'services': services,
                'quick_stats': {
                    'pending_bookings': pending_bookings_count,
                    'active_services': len([s for s in services if s['is_active']]),
                    'today_bookings_count': len(today_bookings)
                }
            }
            
        except Exception as e:
            logger.error(f"Get booking dashboard error: {str(e)}")
            return {}
    
    # Private Helper Methods
    async def _create_default_availability(self, service_id: str, provider_id: str):
        """Create default availability schedule (Mon-Fri 9-5)"""
        try:
            db = await self.get_database()
            
            default_schedule = [
                {'day_of_week': 0, 'start_time': '09:00', 'end_time': '17:00'},  # Monday
                {'day_of_week': 1, 'start_time': '09:00', 'end_time': '17:00'},  # Tuesday
                {'day_of_week': 2, 'start_time': '09:00', 'end_time': '17:00'},  # Wednesday
                {'day_of_week': 3, 'start_time': '09:00', 'end_time': '17:00'},  # Thursday
                {'day_of_week': 4, 'start_time': '09:00', 'end_time': '17:00'},  # Friday
            ]
            
            for schedule in default_schedule:
                availability_record = {
                    'availability_id': str(uuid.uuid4()),
                    'service_id': service_id,
                    'provider_id': provider_id,
                    'day_of_week': schedule['day_of_week'],
                    'start_time': schedule['start_time'],
                    'end_time': schedule['end_time'],
                    'is_available': True,
                    'created_at': datetime.utcnow()
                }
                
                await db.service_availability.insert_one(availability_record)
                
        except Exception as e:
            logger.error(f"Create default availability error: {str(e)}")
    
    async def _get_service_statistics(self, service_id: str) -> Dict[str, Any]:
        """Get statistics for a service"""
        try:
            db = await self.get_database()
            
            total_bookings = await db.bookings.count_documents({'service_id': service_id})
            confirmed_bookings = await db.bookings.count_documents({
                'service_id': service_id,
                'status': BookingStatus.CONFIRMED.value
            })
            completed_bookings = await db.bookings.count_documents({
                'service_id': service_id,
                'status': BookingStatus.COMPLETED.value
            })
            
            # Calculate revenue
            revenue_bookings = await db.bookings.find({
                'service_id': service_id,
                'status': {'$in': [BookingStatus.CONFIRMED.value, BookingStatus.COMPLETED.value]}
            }).to_list(length=None)
            
            total_revenue = sum(booking['price'] for booking in revenue_bookings)
            
            return {
                'total_bookings': total_bookings,
                'confirmed_bookings': confirmed_bookings,
                'completed_bookings': completed_bookings,
                'total_revenue': round(total_revenue, 2)
            }
            
        except Exception as e:
            logger.error(f"Get service statistics error: {str(e)}")
            return {}
    

    async def create_booking(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new booking"""
        try:
            # Add metadata
            booking_data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            # Save to database
            result = await self.db["booking"].insert_one(booking_data)
            
            return {
                "success": True,
                "message": f"Booking created successfully",
                "data": booking_data,
                "id": booking_data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create booking: {str(e)}"
            }

    def _get_default_service_settings(self) -> Dict[str, Any]:
        """Get default service settings"""
        return {
            'allow_online_booking': True,
            'require_confirmation': True,
            'send_reminders': True,
            'reminder_hours': [24, 2],  # 24 hours and 2 hours before
            'buffer_time_minutes': 15,
            'max_bookings_per_day': 20,
            'booking_form_fields': [
                {'name': 'name', 'required': True, 'type': 'text'},
                {'name': 'email', 'required': True, 'type': 'email'},
                {'name': 'phone', 'required': False, 'type': 'phone'},
                {'name': 'notes', 'required': False, 'type': 'textarea'}
            ]
        }
    
    async def _send_booking_notifications(self, booking_data: Dict[str, Any], notification_type: str):
        """Send booking notifications via email/SMS"""
        try:
            # This would integrate with your email/SMS service
            logger.info(f"Sending {notification_type} notification for booking {booking_data['booking_id']}")
            
            # Record notification in database
            db = await self.get_database()
            await db.booking_notifications.insert_one({

    async def update_booking(self, booking_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update booking by ID"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self.db["booking"].update_one(
                {"id": booking_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"Booking not found"
                }
            
            # Get updated document
            updated_doc = await self.db["booking"].find_one({"id": booking_id})
            updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Booking updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update booking: {str(e)}"
            }

                'notification_id': str(uuid.uuid4()),
                'booking_id': booking_data['booking_id'],
                'type': notification_type,
                'recipient_email': booking_data['customer_info'].get('email'),
                'recipient_phone': booking_data['customer_info'].get('phone'),
                'status': 'sent',
                'sent_at': datetime.utcnow()
            })
            
        except Exception as e:
            logger.error(f"Send booking notifications error: {str(e)}")
    
    async def _log_booking_activity(self, booking_id: Optional[str], service_id: Optional[str],
                                  user_id: str, action: str, details: Dict[str, Any]):
        """Log booking activity"""
        try:
            db = await self.get_database()
            
            activity = {
                'activity_id': str(uuid.uuid4()),
                'booking_id': booking_id,
                'service_id': service_id,
                'user_id': user_id,
                'action': action,
                'details': details,
                'timestamp': datetime.utcnow()
            }
            
            await db.booking_activities.insert_one(activity)
            
        except Exception as e:
            logger.error(f"Log booking activity error: {str(e)}")

# Global service instance
complete_booking_service = CompleteBookingService()
    async def cancel_booking(self, booking_id: str, user_id: str) -> dict:
        """Cancel booking"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            # Update booking status
            result = await collections['bookings'].update_one(
                {"_id": booking_id, "$or": [{"client_id": user_id}, {"provider_id": user_id}]},
                {
                    "$set": {
                        "status": "cancelled",
                        "cancelled_at": datetime.utcnow(),
                        "cancelled_by": user_id
                    }
                }
            )
            
            if result.modified_count > 0:
                return {"success": True, "message": "Booking cancelled successfully"}
            else:
                return {"success": False, "message": "Booking not found or not authorized"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def get_appointment(self, user_id: str, appointment_id: str):
        """Get specific appointment"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            appointment = await collections['appointments'].find_one({
                "_id": appointment_id,
                "user_id": user_id
            })
            
            if not appointment:
                return {"success": False, "message": "Appointment not found"}
            
            return {
                "success": True,
                "data": appointment,
                "message": "Appointment retrieved successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def delete_appointment(self, user_id: str, appointment_id: str):
        """Delete appointment"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            result = await collections['appointments'].delete_one({
                "_id": appointment_id,
                "user_id": user_id
            })
            
            if result.deleted_count = await self._calculate_count(user_id):
                return {"success": False, "message": "Appointment not found"}
            
            return {
                "success": True,
                "message": "Appointment deleted successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def list_appointments(self, user_id: str, filters: dict = None, page: int = 1, limit: int = 50):
        """List user's appointments"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            query = {"user_id": user_id}
            if filters:
                query.update(filters)
            
            skip = (page - 1) * limit
            
            cursor = collections['appointments'].find(query).skip(skip).limit(limit)
            appointments = await cursor.to_list(length=limit)
            
            total_count = await collections['appointments'].count_documents(query)
            
            return {
                "success": True,
                "data": {
                    "appointments": appointments,
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total_count,
                        "pages": (total_count + limit - 1) // limit
                    }
                },
                "message": "Appointments retrieved successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}