"""
Content Creation API Routes

Provides API endpoints for content creation functionality including
templates, media management, and collaborative creation tools.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional, Any
from services.content_creation_service import content_creation_service
from core.auth import get_current_user
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/content-creation", tags=["Content Creation"])

@router.get("/projects")
async def get_content_projects(current_user: dict = Depends(get_current_user)):
    """Get all content creation projects"""
    user_id = current_user.get("user_id")
    return await content_creation_service.get_content_projects(user_id)

@router.post("/projects")
async def create_content_project(
    project_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Create a new content creation project"""
    user_id = current_user.get("user_id")
    return await content_creation_service.create_content_project(user_id, project_data)

@router.get("/templates")
async def get_content_templates(
    current_user: dict = Depends(get_current_user),
    category: Optional[str] = None
):
    """Get available content templates"""
    return await content_creation_service.get_content_templates(category)

@router.post("/templates")
async def create_content_template(
    template_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Create a custom content template"""
    user_id = current_user.get("user_id")
    return await content_creation_service.create_content_template(user_id, template_data)

@router.get("/assets")
async def get_content_assets(
    current_user: dict = Depends(get_current_user),
    asset_type: Optional[str] = None
):
    """Get content assets library"""
    user_id = current_user.get("user_id")
    return await content_creation_service.get_content_assets(user_id, asset_type)

@router.post("/assets")
async def upload_content_asset(
    asset_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Upload a new content asset"""
    user_id = current_user.get("user_id")
    return await content_creation_service.upload_content_asset(user_id, asset_data)

@router.post("/collaborate")
async def invite_collaborator(
    collaboration_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Invite collaborator to content project"""
    user_id = current_user.get("user_id")
    return await content_creation_service.invite_collaborator_alt(user_id, collaboration_data)

@router.get("/workflow")
async def get_content_workflow(
    current_user: dict = Depends(get_current_user),
    project_id: Optional[str] = None
):
    """Get content creation workflow"""
    user_id = current_user.get("user_id")
    return await content_creation_service.get_content_workflow(user_id, project_id)