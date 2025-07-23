"""
Authentication and Security
Professional Mewayz Platform
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import uuid
import logging

from .config import settings
from .database import get_users_collection

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Fix database connection timing issue
    try:
        from .database import get_database_async, connect_to_mongo
        
        # Ensure database connection is available
        db = await get_database_async()
        if db is None:
            # Try to reinitialize connection if needed
            await connect_to_mongo()
            db = await get_database_async()
            
        if db is None:
            logger.error("Database connection not available during authentication")
            raise credentials_exception
        
        users_collection = db.users
        user = await users_collection.find_one({"email": email})
        if user is None:
            raise credentials_exception
        
        return user
        
    except Exception as e:
        logger.error(f"Database error during authentication: {e}")
        raise credentials_exception

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """Get current active user"""
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin(current_user: dict = Depends(get_current_user)):
    """Get current admin user"""
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Check if user has admin role or bypass RBAC
    if current_user.get("bypass_rbac", False):
        return current_user
    
    # Check multiple admin role patterns
    is_admin = (
        current_user.get("is_admin", False) or 
        current_user.get("role") in ["admin", "super_admin"] or
        current_user.get("access_level") == "full"
    )
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return current_user