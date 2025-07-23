"""
User Service
Auto-generated service with proper database initialization
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database
from core.auth import verify_password, get_password_hash

class UserService:
    def __init__(self):
        pass
    
    def _get_db(self):
        """Get database connection"""
        return get_database()
    
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""
        try:
            db = self._get_db()
            if not db:
                return None
            
            # Use 'users' collection (not 'user') based on the database structure
            collection = db["users"]
            user = await collection.find_one({"email": email})
            
            if not user:
                return None
            
            # Verify password
            if not verify_password(password, user.get("password", "")):
                return None
            
            # Remove sensitive data
            user.pop('_id', None)
            user.pop('password', None)
            
            return user
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    async def create_user(self, email: str, password: str, name: str) -> Dict[str, Any]:
        """Create new user with hashed password"""
        try:
            db = self._get_db()
            if not db:
                raise ValueError("Database not available")
            
            # Use 'users' collection (not 'user') based on the database structure
            collection = db["users"]
            
            # Check if user already exists
            existing_user = await collection.find_one({"email": email})
            if existing_user:
                raise ValueError("User with this email already exists")
            
            # Hash password
            hashed_password = get_password_hash(password)
            
            user_data = {
                "_id": str(uuid.uuid4()),
                "email": email,
                "password": hashed_password,
                "name": name,
                "role": "user",
                "status": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "email_verified_at": None,
                "phone": None,
                "avatar": None,
                "timezone": "UTC",
                "language": "en",
                "last_login_at": None,
                "login_attempts": 0,
                "locked_until": None,
                "two_factor_enabled": False,
                "two_factor_secret": None,
                "api_key": None,
                "subscription_plan": "free",
                "subscription_expires_at": None
            }
            
            result = await collection.insert_one(user_data)
            
            # Remove sensitive data from response
            user_data.pop('password', None)
            user_data.pop('_id', None)
            
            return user_data
        except Exception as e:
            raise ValueError(str(e))

    async def get_user(self, item_id: str) -> Dict[str, Any]:
        """Get user by ID"""
        try:
            db = self._get_db()
            if not db:
                return {"success": False, "error": "Database not available"}
            
            collection = db["user"]
            doc = await collection.find_one({"id": item_id})
            
            if not doc:
                return {"success": False, "error": "Not found"}
            
            doc.pop('_id', None)
            return {"success": True, "data": doc}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_users(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List users"""
        try:
            db = self._get_db()
            if not db:
                return {"success": False, "error": "Database not available"}
            
            collection = db["user"]
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            cursor = collection.find(query).skip(offset).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            for doc in docs:
                doc.pop('_id', None)
            
            total_count = await collection.count_documents(query)
            return {"success": True, "data": docs, "total": total_count, "limit": limit, "offset": offset}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_user(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user"""
        try:
            db = self._get_db()
            if not db:
                return {"success": False, "error": "Database not available"}
            
            collection = db["user"]
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await collection.update_one(
                {"id": item_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Not found"}
            
            updated_doc = await collection.find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {"success": True, "data": updated_doc}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_user(self, item_id: str) -> Dict[str, Any]:
        """Delete user"""
        try:
            db = self._get_db()
            if not db:
                return {"success": False, "error": "Database not available"}
            
            collection = db["user"]
            result = await collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {"success": False, "error": "Not found"}
            
            return {"success": True, "message": "Deleted successfully", "deleted_count": result.deleted_count}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Service instance
_service_instance = None

def get_user_service():
    """Get service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = UserService()
    return _service_instance

# Backward compatibility
user_service = get_user_service()