"""
Automation API
Auto-generated API file for automation service
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field

from core.auth import get_current_user
from services.automation_service import AutomationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Service instance
automation_service = AutomationService()

@router.get("/health", tags=["System"])
async def automation_health():
    """Health check for automation system"""
    return {
        "status": "healthy",
        "service": "Automation",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/", tags=["Automation"])
async def get_automation(
    current_user: dict = Depends(get_current_user)
):
    """Get automation data"""
    try:
        result = await automation_service.get_automation_data(
            user_id=current_user["_id"]
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Automation data retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting automation data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
