"""
Google OAuth Services Business Logic
Professional Mewayz Platform
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from core.database import get_database
import uuid

class GoogleOAuthService:
    """Service for Google OAuth operations"""
    
    @staticmethod
    async def store_oauth_token(user_id: str, token_data: Dict[str, Any]):
        """Store OAuth token for user"""
        db = await get_database()
        
        oauth_token = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "provider": "google",
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token"),
            "expires_at": datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600)),
            "scope": token_data.get("scope", ""),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Upsert token (replace existing)
        await db.oauth_tokens.replace_one(
            {"user_id": user_id, "provider": "google"},
            oauth_token,
            upsert=True
        )
        
        return oauth_token
    
    @staticmethod
    async def get_user_oauth_token(user_id: str):
        """Get user's Google OAuth token"""
        db = await get_database()
        
        token = await db.oauth_tokens.find_one({
            "user_id": user_id,
            "provider": "google"
        })
        
        return token
    
    @staticmethod
    async def refresh_oauth_token(user_id: str):
        """Refresh user's OAuth token if needed"""
        db = await get_database()
        
        token = await GoogleOAuthService.get_user_oauth_token(user_id)
        if not token:
            return None
        
        # Check if token needs refresh
        if datetime.utcnow() < token["expires_at"]:
            return token  # Token still valid
        
        # In real implementation, this would call Google's token refresh endpoint
        # For now, return existing token
        return token
    
    @staticmethod
    async def get_google_profile(user_id: str):
        """Get user's Google profile information"""
        # In real implementation, this would call Google People API
        profile = {
            "id": f"google_{user_id}",
            "name": "Google User",
            "email": "user@gmail.com",
            "picture": "https://ui-avatars.com/api/?name=" + name.replace(" ", "+") + "&background=random",
            "verified_email": True
        }
        
        return profile
    
    @staticmethod
    async def disconnect_google_account(user_id: str):
        """Disconnect user's Google account"""
        db = await get_database()
        
        result = await db.oauth_tokens.delete_one({
            "user_id": user_id,
            "provider": "google"
        })
        
        return result.deleted_count > 0

# Global service instance
google_oauth_service = GoogleOAuthService()
