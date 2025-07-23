"""
Support API
Auto-generated API file for support service
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field

from core.auth import get_current_user
from services.support_service import SupportService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Service instance
support_service = SupportService()

@router.get("/health", tags=["System"])
async def support_health():
    """Health check for support system"""
    return {
        "status": "healthy",
        "service": "Support",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/", tags=["Support"])
async def get_support(
    current_user: dict = Depends(get_current_user)
):
    """Get support data"""
    try:
        result = await support_service.get_support_data(
            user_id=current_user["_id"]
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Support data retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting support data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
