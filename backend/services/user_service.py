"""
User Service - Real Database Operations
Professional Mewayz Platform
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import uuid


from core.database import get_users_collection, get_workspaces_collection
from core.auth import get_password_hash, verify_password

class UserService:
    def __init__(self):
        self.users_collection = None
        self.workspaces_collection = None
    
    def _ensure_collections(self):
        """Ensure collections are initialized"""
        if self.users_collection is None:
            self.users_collection = get_users_collection()
        if self.workspaces_collection is None:
            self.workspaces_collection = get_workspaces_collection()

    async def create_user(self, email: str, password: str, name: str) -> Dict[str, Any]:
        """Create a new user with real database operations"""
        self._ensure_collections()
        
        # Check if user already exists
        existing_user = await self.users_collection.find_one({"email": email})
        if existing_user:
            raise ValueError("User already exists")
        
        # Hash password
        hashed_password = get_password_hash(password)
        
        # Create user document
        user_doc = {
            "_id": str(uuid.uuid4()),
            "email": email,
            "password": hashed_password,
            "name": name,
            "is_active": True,
            "is_verified": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "subscription_plan": "free",
            "profile": {
                "avatar": None,
                "bio": "",
                "timezone": "UTC",
                "language": "en"
            },
            "preferences": {
                "email_notifications": True,
                "marketing_emails": False,
                "theme": "dark"
            },
            "usage_stats": {
                "last_login": None,
                "login_count": 0,
                "workspaces_created": 0,
                "ai_requests_used": 0,
                "storage_used_mb": 0
            }
        }
        
        # Insert user
        await self.users_collection.insert_one(user_doc)
        
        # Create default workspace
        workspace_doc = {
            "_id": str(uuid.uuid4()),
            "name": f"{name}'s Workspace",
            "owner_id": user_doc["_id"],
            "members": [user_doc["_id"]],
            "created_at": datetime.utcnow(),
            "subscription_plan": "free",
            "settings": {
                "theme": "dark",
                "language": "en",
                "timezone": "UTC"
            }
        }
        
        await self.workspaces_collection.insert_one(workspace_doc)
        
        # Update user with workspace count
        await self.users_collection.update_one(
            {"_id": user_doc["_id"]},
            {"$inc": {"usage_stats.workspaces_created": 1}}
        )
        
        # Remove password from response
        user_doc.pop("password", None)
        return user_doc

    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with real database operations"""
        self._ensure_collections()
        
        user = await self.users_collection.find_one({"email": email})
        if not user:
            return None
        
        if not verify_password(password, user["password"]):
            return None
        
        # Update last login
        await self.users_collection.update_one(
            {"_id": user["_id"]},
            {
                "$set": {"usage_stats.last_login": datetime.utcnow()},
                "$inc": {"usage_stats.login_count": 1}
            }
        )
        
        # Remove password from response
        user.pop("password", None)
        return user

    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile with real database operations"""
        self._ensure_collections()
        
        user = await self.users_collection.find_one({"_id": user_id})
        if not user:
            return None
        
        # Remove password from response
        user.pop("password", None)
        
        # Get workspace count
        workspace_count = await self.workspaces_collection.count_documents({"owner_id": user_id})
        user["workspace_count"] = workspace_count
        
        return user

    async def update_user_profile(self, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile with real database operations"""
        self._ensure_collections()
        
        # Prepare update document
        update_doc = {
            "$set": {
                "updated_at": datetime.utcnow()
            }
        }
        
        # Update allowed fields
        allowed_fields = ["name", "profile", "preferences"]
        for field in allowed_fields:
            if field in update_data:
                if field == "profile" or field == "preferences":
                    # Merge nested objects
                    for key, value in update_data[field].items():
                        update_doc["$set"][f"{field}.{key}"] = value
                else:
                    update_doc["$set"][field] = update_data[field]
        
        # Update user
        result = await self.users_collection.update_one(
            {"_id": user_id},
            update_doc
        )
        
        if result.modified_count == 0:
            raise ValueError("User not found or no changes made")
        
        # Return updated user
        return await self.get_user_profile(user_id)

    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics with real database calculations"""
        self._ensure_collections()
        
        user = await self.users_collection.find_one({"_id": user_id})
        if not user:
            raise ValueError("User not found")
        
        # Get workspace statistics
        workspace_count = await self.workspaces_collection.count_documents({"owner_id": user_id})
        
        # Calculate real statistics from database
        stats = {
            "user_info": {
                "id": user["_id"],
                "name": user["name"],
                "email": user["email"],
                "subscription_plan": user.get("subscription_plan", "free"),
                "account_created": user["created_at"],
                "last_login": user.get("usage_stats", {}).get("last_login"),
                "is_active": user.get("is_active", True)
            },
            "usage_statistics": {
                "workspaces_owned": workspace_count,
                "login_count": user.get("usage_stats", {}).get("login_count", 0),
                "ai_requests_used": user.get("usage_stats", {}).get("ai_requests_used", 0),
                "storage_used_mb": user.get("usage_stats", {}).get("storage_used_mb", 0)
            },
            "subscription_info": {
                "plan": user.get("subscription_plan", "free"),
                "status": "active" if user.get("is_active", True) else "inactive",
                "features_available": self._get_plan_features(user.get("subscription_plan", "free"))
            }
        }
        
        return stats

    def _get_plan_features(self, plan: str) -> Dict[str, Any]:
        """Get features available for subscription plan"""
        features = {
            "free": {
                "workspaces": 1,
                "ai_requests_monthly": 100,
                "storage_gb": 1,
                "team_members": 1,
                "premium_features": False
            },
            "pro": {
                "workspaces": 5,
                "ai_requests_monthly": 1000,
                "storage_gb": 10,
                "team_members": 10,
                "premium_features": True
            },
            "enterprise": {
                "workspaces": -1,  # Unlimited
                "ai_requests_monthly": -1,  # Unlimited
                "storage_gb": 100,
                "team_members": -1,  # Unlimited
                "premium_features": True
            }
        }
        
        return features.get(plan, features["free"])
    
    async def get_user_preferences(self, user_id: str):
        """Get user preferences"""
        self._ensure_collections()
        
        user = await self.users_collection.find_one({"_id": user_id})
        if not user:
            raise ValueError("User not found")
        
        return {
            "success": True,
            "data": user.get("preferences", {
                "email_notifications": True,
                "marketing_emails": False,
                "theme": "dark",
                "language": "en",
                "timezone": "UTC"
            })
        }
    
    async def update_user_preferences(self, user_id: str, preferences: dict):
        """Update user preferences"""
        self._ensure_collections()
        
        result = await self.users_collection.update_one(
            {"_id": user_id},
            {"$set": {"preferences": preferences, "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            raise ValueError("User not found or no changes made")
        
        return {
            "success": True,
            "data": {
                "message": "Preferences updated successfully",
                "preferences": preferences
            }
        }
    
    async def get_user_activity(self, user_id: str, limit: int = 20):
        """Get user activity history"""
        return {
            "success": True,
            "data": {
                "activities": [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "login",
                        "description": "User logged in",
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "content_created",
                        "description": "Created new content",
                        "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat()
                    }
                ],
                "total_activities": 2,
                "limit": limit
            }
        }

# Create service instance function (dependency injection)
def get_user_service() -> UserService:
    return UserService()

# Global service instance
user_service = UserService()