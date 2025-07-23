"""
Authentication API Routes
Professional Mewayz Platform
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import timedelta

from core.auth import create_access_token, get_current_active_user
from core.config import settings
from services.user_service import get_user_service
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user
import uuid
from datetime import datetime

router = APIRouter()

class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    name: str
    terms_accepted: bool = True

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

@router.post("/register", response_model=dict)
async def register_user(user_data: UserRegistration):
    """Register a new user with real database operations"""
    if not user_data.terms_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Terms and conditions must be accepted"
        )
    
    try:
        user_service = get_user_service()
        user = await user_service.create_user(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name
        )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["email"]},
            expires_delta=access_token_expires
        )
        
        return {
            "success": True,
            "message": "User registered successfully",
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )

@router.post("/login", response_model=LoginResponse)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user with real database operations"""
    try:
        user_service = get_user_service()
        user = await user_service.authenticate_user(
            email=form_data.username,
            password=form_data.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["email"]},
            expires_delta=access_token_expires
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=user
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )

@router.get("/verify")
async def verify_token(current_user: dict = Depends(get_current_active_user)):
    """Verify JWT token and return user info"""
    return {
        "success": True,
        "message": "Token is valid",
        "user": current_user
    }

@router.post("/logout")
async def logout_user(current_user: dict = Depends(get_current_active_user)):
    """Logout user (client should remove token)"""
    return {
        "success": True,
        "message": "Logged out successfully"
    }