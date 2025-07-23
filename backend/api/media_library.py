"""
Media Library & File Management API
Comprehensive file upload, storage, and management system
"""

from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form, Query
from typing import Optional, List
import os
import uuid
from datetime import datetime
import mimetypes
import base64

from core.auth import get_current_user
from core.database import get_database
from services.media_service import MediaService
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user

router = APIRouter()

@router.get("/library")
async def get_media_library(
    folder: str = Query(""),
    file_type: str = Query("all"),
    search: str = Query(""),
    limit: int = Query(50),
    current_user: dict = Depends(get_current_user)
):
    """Get media library with files and folders"""
    try:
        library = await MediaService.get_media_library(
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            folder=folder,
            file_type=file_type,
            search=search,
            limit=limit
        )
        return {"success": True, "data": library}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_media_file(
    file: UploadFile = File(...),
    folder: str = Form(""),
    description: str = Form(""),
    tags: str = Form(""),
    current_user: dict = Depends(get_current_user)
):
    """Upload media file to library"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file selected")
        
        # Check file size (50MB limit)
        file_size = 0
        file_content = await file.read()
        file_size = len(file_content)
        await file.seek(0)  # Reset file pointer
        
        if file_size > 50 * 1024 * 1024:  # 50MB
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 50MB")
        
        # Check file type
        allowed_types = [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'video/mp4', 'video/mov', 'video/avi',
            'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain', 'text/csv'
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        upload_result = await MediaService.upload_file(
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            file=file,
            file_content=file_content,
            folder=folder,
            description=description,
            tags=tags.split(',') if tags else []
        )
        
        return {"success": True, "data": upload_result, "message": "File uploaded successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{file_id}")
async def get_file_details(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get file details"""
    try:
        file_details = await MediaService.get_file_details(
            file_id=file_id,
            user_id=current_user.get("_id") or current_user.get("id", "default-user")
        )
        
        if not file_details:
            raise HTTPException(status_code=404, detail="File not found")
            
        return {"success": True, "data": file_details}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/files/{file_id}")
async def update_file_metadata(
    file_id: str,
    name: str = Form(None),
    description: str = Form(None),
    tags: str = Form(None),
    folder: str = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Update file metadata"""
    try:
        updates = {}
        if name:
            updates["name"] = name
        if description:
            updates["description"] = description
        if tags:
            updates["tags"] = tags.split(',')
        if folder:
            updates["folder"] = folder
            
        result = await MediaService.update_file_metadata(
            file_id=file_id,
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            updates=updates
        )
        
        return {"success": True, "data": result, "message": "File updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete file from library"""
    try:
        result = await MediaService.delete_file(
            file_id=file_id,
            user_id=current_user.get("_id") or current_user.get("id", "default-user")
        )
        
        return {"success": True, "message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/folders")
async def create_folder(
    name: str = Form(...),
    parent_folder: str = Form(""),
    current_user: dict = Depends(get_current_user)
):
    """Create new folder"""
    try:
        folder = await MediaService.create_folder(
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            name=name,
            parent_folder=parent_folder
        )
        
        return {"success": True, "data": folder, "message": "Folder created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/folders/{folder_id}")
async def delete_folder(
    folder_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete folder (must be empty)"""
    try:
        result = await MediaService.delete_folder(
            folder_id=folder_id,
            user_id=current_user.get("_id") or current_user.get("id", "default-user")
        )
        
        return {"success": True, "message": "Folder deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usage")
async def get_storage_usage(
    current_user: dict = Depends(get_current_user)
):
    """Get storage usage statistics"""
    try:
        usage = await MediaService.get_storage_usage(
            user_id=current_user.get("_id") or current_user.get("id", "default-user")
        )
        
        return {"success": True, "data": usage}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_media(
    query: str = Query(...),
    file_type: str = Query("all"),
    folder: str = Query(""),
    limit: int = Query(20),
    current_user: dict = Depends(get_current_user)
):
    """Search media files"""
    try:
        results = await MediaService.search_media(
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            query=query,
            file_type=file_type,
            folder=folder,
            limit=limit
        )
        
        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk-delete")
async def bulk_delete_files(
    file_ids: str = Form(...),  # JSON string of file IDs
    current_user: dict = Depends(get_current_user)
):
    """Delete multiple files"""
    try:
        import json
        ids = json.loads(file_ids)
        
        result = await MediaService.bulk_delete_files(
            file_ids=ids,
            user_id=current_user.get("_id") or current_user.get("id", "default-user")
        )
        
        return {"success": True, "data": result, "message": f"Deleted {result['deleted_count']} files"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in file_ids")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk-move")
async def bulk_move_files(
    file_ids: str = Form(...),  # JSON string of file IDs
    target_folder: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Move multiple files to folder"""
    try:
        import json
        ids = json.loads(file_ids)
        
        result = await MediaService.bulk_move_files(
            file_ids=ids,
            target_folder=target_folder,
            user_id=current_user.get("_id") or current_user.get("id", "default-user")
        )
        
        return {"success": True, "data": result, "message": f"Moved {result['moved_count']} files"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in file_ids")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))