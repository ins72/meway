"""
AI Content API Routes

Provides API endpoints for AI-powered content generation,
optimization, and content intelligence features.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional, Any
from services.ai_content_service import ai_content_service
from core.auth import get_current_user
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/ai-content", tags=["AI Content"])

@router.post("/generate/text")
async def generate_text_content(
    request: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Generate AI-powered text content"""
    user_id = current_user.get("user_id")
    return await ai_content_service.generate_text_content(user_id, request)

@router.post("/generate/image")
async def generate_image_content(
    request: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Generate AI-powered image content"""
    user_id = current_user.get("user_id")
    return await ai_content_service.generate_image_content(user_id, request)

@router.post("/optimize")
async def optimize_content(
    content: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Optimize existing content using AI"""
    user_id = current_user.get("user_id")
    return await ai_content_service.optimize_content(user_id, content)

@router.post("/analyze/sentiment")
async def analyze_content_sentiment(
    content: Dict[str, str],
    current_user: dict = Depends(get_current_user)
):
    """Analyze content sentiment using AI"""
    return await ai_content_service.analyze_sentiment(content)

@router.post("/translate")
async def translate_content(
    translation_request: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Translate content using AI"""
    user_id = current_user.get("user_id")
    return await ai_content_service.translate_content(user_id, translation_request)

@router.get("/templates")
async def get_content_templates(
    current_user: dict = Depends(get_current_user),
    category: Optional[str] = None
):
    """Get AI content generation templates"""
    return await ai_content_service.get_content_templates(category)

@router.get("/suggestions")
async def get_content_suggestions(
    current_user: dict = Depends(get_current_user),
    context: Optional[str] = None
):
    """Get AI-powered content suggestions"""
    user_id = current_user.get("user_id")
    return await ai_content_service.get_content_suggestions(user_id, context)