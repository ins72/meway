"""
Users Management Services Business Logic
Professional Mewayz Platform
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from core.database import get_database
import uuid

class UsersService:
    """Service for user management operations"""
    
    @staticmethod
    async def get_user_profile(user_id: str):
        """Get user profile information"""
        db = await get_database()
        
        user = await db.users.find_one({"_id": user_id})
        if user:
            user.pop("password", None)  # Remove password from response
        return user
    
    @staticmethod
    async def update_user_profile(user_id: str, profile_data: Dict[str, Any]):
        """Update user profile"""
        db = await get_database()
        
        update_data = {
            "full_name": profile_data.get("full_name"),
            "bio": profile_data.get("bio"),
            "phone": profile_data.get("phone"),
            "timezone": profile_data.get("timezone"),
            "language": profile_data.get("language", "en"),
            "avatar": profile_data.get("avatar"),
            "updated_at": datetime.utcnow()
        }
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        result = await db.users.update_one(
            {"_id": user_id},
            {"$set": update_data}
        )
        
        return await db.users.find_one({"_id": user_id})
    
    @staticmethod
    async def get_user_settings(user_id: str):
        """Get user settings"""
        db = await get_database()
        
        settings = await db.user_settings.find_one({"user_id": user_id})
        if not settings:
            # Create default settings
            settings = {
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                "notifications": {
                    "email_marketing": True,
                    "system_updates": True,
                    "security_alerts": True,
                    "weekly_digest": True
                },
                "privacy": {
                    "profile_visibility": "public",
                    "show_email": False,
                    "allow_indexing": True
                },
                "preferences": {
                    "theme": "light",
                    "language": "en",
                    "timezone": "UTC",
                    "date_format": "MM/dd/yyyy"
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await db.user_settings.insert_one(settings)
        
        return settings
    
    @staticmethod
    async def update_user_settings(user_id: str, settings_data: Dict[str, Any]):
        """Update user settings"""
        db = await get_database()
        
        current_settings = await UsersService.get_user_settings(user_id)
        
        # Merge settings
        notifications = {**current_settings.get("notifications", {}), **settings_data.get("notifications", {})}
        privacy = {**current_settings.get("privacy", {}), **settings_data.get("privacy", {})}
        preferences = {**current_settings.get("preferences", {}), **settings_data.get("preferences", {})}
        
        update_data = {
            "notifications": notifications,
            "privacy": privacy,
            "preferences": preferences,
            "updated_at": datetime.utcnow()
        }
        
        result = await db.user_settings.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        
        return await db.user_settings.find_one({"user_id": user_id})
    
    @staticmethod
    async def get_user_activity(user_id: str, days: int = 30):
        """Get user activity history"""
        db = await get_database()
        
        since_date = datetime.utcnow() - timedelta(days=days)
        
        activities = await db.user_activities.find({
            "user_id": user_id,
            "created_at": {"$gte": since_date}
        }).sort("created_at", -1).limit(100).to_list(length=None)
        
        return activities
    
    @staticmethod
    async def log_user_activity(user_id: str, activity_type: str, details: Dict[str, Any] = None):
        """Log user activity"""
        db = await get_database()
        
        activity = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "type": activity_type,
            "details": details or {},
            "ip_address": details.get("ip_address") if details else None,
            "user_agent": details.get("user_agent") if details else None,
            "created_at": datetime.utcnow()
        }
        
        result = await db.user_activities.insert_one(activity)
        return activity

# Global service instance
users_service = UsersService()
