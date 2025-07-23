"""
Webhook API
Auto-generated API file for webhook service
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field

from core.auth import get_current_user
from services.webhook_service import WebhookService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Service instance
webhook_service = WebhookService()

@router.get("/health", tags=["System"])
async def webhook_health():
    """Health check for webhook system"""
    return {
        "status": "healthy",
        "service": "Webhook",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/", tags=["Webhook"])
async def get_webhook(
    current_user: dict = Depends(get_current_user)
):
    """Get webhook data"""
    try:
        result = await webhook_service.get_webhook_data(
            user_id=current_user["_id"]
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Webhook data retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting webhook data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
