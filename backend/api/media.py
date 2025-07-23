"""
Media API Routes

Provides API endpoints for media management functionality including
file upload, storage, processing, and organization.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Dict, List, Optional, Any
from services.media_service import media_service
from core.auth import get_current_user
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/media", tags=["Media Management"])

@router.get("/files")
async def get_media_files(
    current_user: dict = Depends(get_current_user),
    file_type: Optional[str] = None,
    folder: Optional[str] = None
):
    """Get media files"""
    user_id = current_user.get("user_id")
    return await media_service.get_media_files(user_id, file_type, folder)

@router.post("/upload")
async def upload_media_file(
    file_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Upload a media file"""
    user_id = current_user.get("user_id")
    return await media_service.upload_media_file(user_id, file_data)

@router.get("/{file_id}")
async def get_media_file(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific media file"""
    return await media_service.get_media_file(file_id)

@router.put("/{file_id}")
async def update_media_file(
    file_id: str,
    update_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Update media file metadata"""
    return await media_service.update_media_file(file_id, update_data)

@router.delete("/{file_id}")
async def delete_media_file(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete media file"""
    return await media_service.delete_media_file(file_id)

@router.get("/folders/list")
async def get_media_folders(current_user: dict = Depends(get_current_user)):
    """Get media folders structure"""
    user_id = current_user.get("user_id")
    return await media_service.get_media_folders(user_id)

@router.post("/folders")
async def create_media_folder(
    folder_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Create a new media folder"""
    user_id = current_user.get("user_id")
    return await media_service.create_media_folder(user_id, folder_data)

@router.post("/{file_id}/process")
async def process_media_file(
    file_id: str,
    processing_options: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Process media file (resize, optimize, etc.)"""
    return await media_service.process_media_file(file_id, processing_options)

@router.get("/analytics/usage")
async def get_media_usage_analytics(
    current_user: dict = Depends(get_current_user),
    period: Optional[str] = "30d"
):
    """Get media usage analytics"""
    user_id = current_user.get("user_id")
    return await media_service.get_media_usage_analytics(user_id, period)