"""
Mobile Pwa API
Auto-generated API file for mobile_pwa service
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field

from core.auth import get_current_user
from services.mobile_pwa_service import MobilePwaService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Service instance
mobile_pwa_service = MobilePwaService()

@router.get("/health", tags=["System"])
async def mobile_pwa_health():
    """Health check for mobile_pwa system"""
    return {
        "status": "healthy",
        "service": "Mobile Pwa",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/", tags=["Mobile Pwa"])
async def get_mobile_pwa(
    current_user: dict = Depends(get_current_user)
):
    """Get mobile_pwa data"""
    try:
        result = await mobile_pwa_service.get_mobile_pwa_data(
            user_id=current_user["_id"]
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Mobile Pwa data retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting mobile_pwa data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
