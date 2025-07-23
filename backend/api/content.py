"""
Content API Routes

Provides API endpoints for general content management functionality
including content storage, retrieval, and organization.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional, Any
from services.content_service import content_service
from core.auth import get_current_user
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/content", tags=["Content Management"])

@router.get("/")
async def get_content(
    current_user: dict = Depends(get_current_user),
    content_type: Optional[str] = None,
    category: Optional[str] = None
):
    """Get content items"""
    user_id = current_user.get("user_id")
    return await content_service.get_content(user_id, content_type, category)

@router.post("/")
async def create_content(
    content_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Create new content"""
    user_id = current_user.get("user_id")
    return await content_service.create_content(user_id, content_data)

@router.get("/{content_id}")
async def get_content_by_id(
    content_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific content by ID"""
    return await content_service.get_content_by_id(content_id)

@router.put("/{content_id}")
async def update_content(
    content_id: str,
    update_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Update existing content"""
    return await content_service.update_content(content_id, update_data)

@router.delete("/{content_id}")
async def delete_content(
    content_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete content"""
    return await content_service.delete_content(content_id)

@router.get("/categories/list")
async def get_content_categories(current_user: dict = Depends(get_current_user)):
    """Get available content categories"""
    return await content_service.get_content_categories()

@router.post("/search")
async def search_content(
    search_params: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Search content"""
    user_id = current_user.get("user_id")
    return await content_service.search_content(user_id, search_params)

@router.get("/analytics/performance")
async def get_content_analytics(
    current_user: dict = Depends(get_current_user),
    period: Optional[str] = "30d"
):
    """Get content performance analytics"""
    user_id = current_user.get("user_id")
    return await content_service.get_content_analytics(user_id, period)