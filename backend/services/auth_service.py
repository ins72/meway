"""
Authentication Services Business Logic
Professional Mewayz Platform
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from core.database import get_database
from passlib.context import CryptContext
import uuid

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Service for authentication operations"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)
    
    @staticmethod
    async def authenticate_user(email: str, password: str):
        """Authenticate user with email and password"""
        db = await get_database()
        
        user = await db.users.find_one({"email": email})
        if not user:
            return False
        
        if not AuthService.verify_password(password, user.get("password", "")):
            return False
        
        return user
    
    @staticmethod
    async def create_user(email: str, password: str, full_name: str = ""):
        """Create new user"""
        db = await get_database()
        
        # Check if user exists
        existing_user = await db.users.find_one({"email": email})
        if existing_user:
            return None
        
        user = {
            "_id": str(uuid.uuid4()),
            "email": email,
            "password": AuthService.get_password_hash(password),
            "full_name": full_name,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_login": datetime.utcnow()
        }
        
        result = await db.users.insert_one(user)
        user.pop("password")  # Remove password from response
        return user
    
    @staticmethod
    async def update_last_login(user_id: str):
        """Update user's last login timestamp"""
        db = await get_database()
        
        await db.users.update_one(
            {"_id": user_id},
            {"$set": {"last_login": datetime.utcnow()}}
        )

# Global service instance
auth_service = AuthService()
    async def delete_user(self, user_id: str) -> bool:
        """Delete user account (soft delete)"""
        try:
            db = get_database()
            if not db:
                return False
            
            result = await db.users.update_one(
                {"_id": user_id},
                {
                    "$set": {
                        "deleted": True,
                        "deleted_at": datetime.utcnow(),
                        "status": "deleted"
                    }
                }
            )
            return result.modified_count > 0
        except Exception:
            return False

    async def delete_user(self, user_id: str) -> bool:
        """Delete user account (soft delete)"""
        try:
            db = get_database()
            if not db:
                return False
            
            result = await db.users.update_one(
                {"_id": user_id},
                {
                    "$set": {
                        "deleted": True,
                        "deleted_at": datetime.utcnow(),
                        "status": "deleted"
                    }
                }
            )
            return result.modified_count > 0
        except Exception:
            return False
