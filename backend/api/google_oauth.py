"""
Google OAuth Integration API Routes
Professional Mewayz Platform - Migrated from Monolithic Structure
High-Value Feature Addition
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
import httpx
import secrets
import uuid
import os

from core.auth import create_access_token, get_current_active_user
from core.database import get_database
from services.user_service import get_user_service
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user

router = APIRouter()

# Initialize service instances
user_service = get_user_service()

# OAuth configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

class GoogleOAuthRequest(BaseModel):
    credential: str  # ID token from Google
    
class OAuthUserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    email_verified: bool
    phone: Optional[str]
    avatar: Optional[str]
    timezone: str
    language: str
    subscription_plan: str
    api_key: str
    created_at: datetime
    token: str
    oauth_provider: str

@router.get("/config")
async def get_oauth_config():
    """Get OAuth configuration for frontend"""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured"
        )
    
    return {
        "success": True,
        "data": {
            "google_client_id": GOOGLE_CLIENT_ID,
            "oauth_configured": bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET),
            "redirect_uri": "/api/auth/google/callback"  # Frontend can use this for OAuth flow
        }
    }

@router.post("/google/verify")
async def google_verify_token(oauth_request: GoogleOAuthRequest):
    """Verify Google OAuth credential (for client-side OAuth)"""
    try:
        if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google OAuth not configured"
            )
        
        # Verify the credential with Google
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={oauth_request.credential}"
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid Google credential"
                )
            
            user_info = response.json()
            
            # Verify the token is for our application
            if user_info.get('aud') != GOOGLE_CLIENT_ID:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token audience"
                )
        
        email = user_info.get('email')
        name = user_info.get('name', email.split('@')[0] if email else 'User')
        avatar = user_info.get('picture')
        email_verified = user_info.get('email_verified', False)
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google"
            )
        
        # Get users collection
        user_service._ensure_collections()
        users_collection = user_service.users_collection
        
        # Check if user already exists
        user = await users_collection.find_one({"email": email})
        
        if user:
            # Update existing user with Google info
            update_data = {
                "avatar": avatar,
                "oauth_provider": "google",
                "oauth_id": user_info.get('sub'),
                "last_login_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Only update email verification if Google confirms it
            if email_verified:
                update_data["is_verified"] = True
                update_data["email_verified_at"] = datetime.utcnow()
            
            await users_collection.update_one(
                {"email": email},
                {"$set": update_data}
            )
            
            # Fetch updated user
            user = await users_collection.find_one({"email": email})
        else:
            # Create new user with Google OAuth
            user_doc = {
                "_id": str(uuid.uuid4()),
                "name": name,
                "email": email,
                "password": None,  # No password for OAuth users
                "phone": None,
                "timezone": "UTC",
                "language": "en",
                "role": "user",
                "is_verified": email_verified,
                "email_verified_at": datetime.utcnow() if email_verified else None,
                "avatar": avatar,
                "oauth_provider": "google",
                "oauth_id": user_info.get('sub'),
                "is_active": True,
                "last_login_at": datetime.utcnow(),
                "login_attempts": 0,
                "locked_until": None,
                "two_factor_enabled": False,
                "two_factor_secret": None,
                "api_key": secrets.token_urlsafe(48),
                "subscription_plan": "free",
                "subscription_expires_at": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                # Initialize usage statistics
                "usage_stats": {
                    "bio_sites_created": 0,
                    "products_created": 0,
                    "ai_requests_used": 0,
                    "storage_used_mb": 0,
                    "last_login": datetime.utcnow()
                },
                # Initialize profile
                "profile": {
                    "country": None,
                    "city": None,
                    "company": None,
                    "website": None
                }
            }
            
            await users_collection.insert_one(user_doc)
            user = user_doc
        
        # Create access token
        access_token = create_access_token(data={"sub": email})
        
        # Return comprehensive user data
        user_response = OAuthUserResponse(
            id=str(user["_id"]),
            name=user["name"],
            email=user["email"],
            role=user["role"],
            email_verified=bool(user.get("email_verified_at")),
            phone=user.get("phone"),
            avatar=user.get("avatar"),
            timezone=user.get("timezone", "UTC"),
            language=user.get("language", "en"),
            subscription_plan=user.get("subscription_plan", "free"),
            api_key=user.get("api_key", ""),
            created_at=user["created_at"],
            token=access_token,
            oauth_provider="google"
        )
        
        return {
            "success": True,
            "message": "Google OAuth authentication successful",
            "token": access_token,
            "user": user_response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify Google token: {str(e)}"
        )

@router.post("/google/link")
async def link_google_account(
    oauth_request: GoogleOAuthRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Link Google account to existing user account"""
    try:
        if not GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google OAuth not configured"
            )
        
        # Verify the credential with Google
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={oauth_request.credential}"
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid Google credential"
                )
            
            user_info = response.json()
            
            if user_info.get('aud') != GOOGLE_CLIENT_ID:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token audience"
                )
        
        google_email = user_info.get('email')
        google_id = user_info.get('sub')
        avatar = user_info.get('picture')
        
        if not google_email or not google_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient Google account information"
            )
        
        # Check if Google account is already linked to another user
        user_service._ensure_collections()
        users_collection = user_service.users_collection
        
        existing_linked_user = await users_collection.find_one({
            "oauth_id": google_id,
            "oauth_provider": "google",
            "_id": {"$ne": current_user["_id"]}
        })
        
        if existing_linked_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This Google account is already linked to another user"
            )
        
        # Link Google account to current user
        update_data = {
            "oauth_provider": "google",
            "oauth_id": google_id,
            "google_email": google_email,
            "avatar": avatar,
            "updated_at": datetime.utcnow()
        }
        
        # If Google email is verified, mark user as verified
        if user_info.get('email_verified'):
            update_data["is_verified"] = True
            update_data["email_verified_at"] = datetime.utcnow()
        
        await users_collection.update_one(
            {"_id": current_user["_id"]},
            {"$set": update_data}
        )
        
        return {
            "success": True,
            "message": "Google account linked successfully",
            "data": {
                "google_email": google_email,
                "avatar_updated": bool(avatar),
                "verification_updated": user_info.get('email_verified', False)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to link Google account: {str(e)}"
        )

@router.post("/google/unlink")
async def unlink_google_account(current_user: dict = Depends(get_current_active_user)):
    """Unlink Google account from user"""
    try:
        user_service._ensure_collections()
        users_collection = user_service.users_collection
        
        # Check if user has Google OAuth linked
        user = await users_collection.find_one({"_id": current_user["_id"]})
        
        if not user or user.get("oauth_provider") != "google":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No Google account linked to this user"
            )
        
        # Check if user has password (to ensure they can still log in)
        if not user.get("password"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot unlink Google account. Please set a password first to maintain account access."
            )
        
        # Remove Google OAuth information
        await users_collection.update_one(
            {"_id": current_user["_id"]},
            {
                "$unset": {
                    "oauth_provider": "",
                    "oauth_id": "",
                    "google_email": ""
                },
                "$set": {
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "message": "Google account unlinked successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unlink Google account: {str(e)}"
        )

@router.get("/google/profile")
async def get_google_profile_info(current_user: dict = Depends(get_current_active_user)):
    """Get Google profile information for linked account"""
    try:
        user_service._ensure_collections()
        users_collection = user_service.users_collection
        
        user = await users_collection.find_one({"_id": current_user["_id"]})
        
        if not user or user.get("oauth_provider") != "google":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Google account linked"
            )
        
        google_info = {
            "linked": True,
            "google_email": user.get("google_email"),
            "oauth_id": user.get("oauth_id"),
            "avatar": user.get("avatar"),
            "linked_at": user.get("updated_at"),
            "can_unlink": bool(user.get("password"))  # Can only unlink if user has password
        }
        
        return {
            "success": True,
            "data": google_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch Google profile info: {str(e)}"
        )