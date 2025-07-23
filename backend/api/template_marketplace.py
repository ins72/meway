"""
Template Marketplace API
Auto-generated API file for template_marketplace service
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field

from core.auth import get_current_user
from services.template_marketplace_service import TemplateMarketplaceService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Service instance
template_marketplace_service = TemplateMarketplaceService()

@router.get("/health", tags=["System"])
async def template_marketplace_health():
    """Health check for template_marketplace system"""
    return {
        "status": "healthy",
        "service": "Template Marketplace",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/", tags=["Template Marketplace"])
async def get_template_marketplace(
    current_user: dict = Depends(get_current_user)
):
    """Get template_marketplace data"""
    try:
        result = await template_marketplace_service.get_template_marketplace_data(
            user_id=current_user["_id"]
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Template Marketplace data retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting template_marketplace data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
