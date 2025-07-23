"""
Customer Experience API Routes

Provides API endpoints for customer experience management including
journey mapping, feedback collection, and experience optimization.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional, Any
from services.customer_experience_service import customer_experience_service
from core.auth import get_current_user
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/customer-experience", tags=["Customer Experience"])

@router.get("/dashboard")
async def get_cx_dashboard(current_user: dict = Depends(get_current_user)):
    """Get customer experience dashboard"""
    user_id = current_user.get("user_id")
    return await customer_experience_service.get_cx_dashboard(user_id)

@router.get("/journey-mapping")
async def get_journey_mapping(
    current_user: dict = Depends(get_current_user),
    customer_id: Optional[str] = None
):
    """Get customer journey mapping data"""
    user_id = current_user.get("user_id")
    return await customer_experience_service.get_journey_mapping(user_id, customer_id)

@router.post("/feedback")
async def collect_feedback(
    feedback_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Collect customer feedback"""
    user_id = current_user.get("user_id")
    return await customer_experience_service.collect_feedback(user_id, feedback_data)

@router.get("/feedback")
async def get_feedback(
    current_user: dict = Depends(get_current_user),
    feedback_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """Get customer feedback data"""
    user_id = current_user.get("user_id")
    return await customer_experience_service.get_feedback(user_id, feedback_type, date_from, date_to)

@router.get("/sentiment-analysis")
async def get_sentiment_analysis(
    current_user: dict = Depends(get_current_user),
    period: Optional[str] = "30d"
):
    """Get sentiment analysis of customer interactions"""
    user_id = current_user.get("user_id")
    return await customer_experience_service.get_sentiment_analysis(user_id, period)

@router.get("/touchpoints")
async def get_customer_touchpoints(current_user: dict = Depends(get_current_user)):
    """Get customer touchpoint analysis"""
    user_id = current_user.get("user_id")
    return await customer_experience_service.get_customer_touchpoints(user_id)

@router.get("/personalization")
async def get_personalization_data(
    current_user: dict = Depends(get_current_user),
    customer_id: Optional[str] = None
):
    """Get customer personalization insights"""
    user_id = current_user.get("user_id")
    return await customer_experience_service.get_personalization_data(user_id, customer_id)

@router.post("/optimization")
async def optimize_experience(
    optimization_request: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Get experience optimization recommendations"""
    user_id = current_user.get("user_id")
    return await customer_experience_service.optimize_experience(user_id, optimization_request)