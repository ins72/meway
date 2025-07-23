"""
Survey API
Auto-generated API file for survey service
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field

from core.auth import get_current_user
from services.survey_service import SurveyService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Service instance
survey_service = SurveyService()

@router.get("/health", tags=["System"])
async def survey_health():
    """Health check for survey system"""
    return {
        "status": "healthy",
        "service": "Survey",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/", tags=["Survey"])
async def get_survey(
    current_user: dict = Depends(get_current_user)
):
    """Get survey data"""
    try:
        result = await survey_service.get_survey_data(
            user_id=current_user["_id"]
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Survey data retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting survey data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
