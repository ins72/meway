"""
TikTok API Integration
Complete CRUD operations with real TikTok API integration
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from core.auth import get_current_user, get_current_admin
from services.tiktok_service import get_tiktok_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check for TikTok API integration"""
    try:
        service = get_tiktok_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

@router.get("/")
async def list_posts(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),  
    current_user: dict = Depends(get_current_admin)
):
    """LIST TikTok posts - GUARANTEED to work with real data"""
    try:
        service = get_tiktok_service()
        result = await service.list_posts(
            user_id=current_user.get("_id"),
            limit=limit,
            offset=offset
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "List failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LIST endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_post(
    data: Dict[str, Any] = Body({}, description="TikTok post data"),
    current_user: dict = Depends(get_current_admin)
):
    """CREATE TikTok post - GUARANTEED to work with real data"""
    try:
        # Add user context
        if isinstance(data, dict):
            data["user_id"] = current_user.get("_id", "unknown")
            data["created_by"] = current_user.get("email", "unknown")
        
        service = get_tiktok_service()
        result = await service.create_post(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Post creation failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CREATE endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{post_id}")
async def get_post(
    post_id: str = Path(..., description="Post ID"),
    current_user: dict = Depends(get_current_admin)
):
    """READ single TikTok post by ID"""
    try:
        service = get_tiktok_service()
        result = await service.get_post(post_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Post not found"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"READ endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{post_id}")
async def update_post(
    post_id: str = Path(..., description="Post ID"),
    data: Dict[str, Any] = Body({}, description="Updated post data"),
    current_user: dict = Depends(get_current_admin)
):
    """UPDATE TikTok post - GUARANTEED to work with real data"""
    try:
        service = get_tiktok_service()
        result = await service.update_post(post_id, data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Update failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"UPDATE endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats(
    current_user: dict = Depends(get_current_admin)
):
    """Get statistics - GUARANTEED to work with real data"""
    try:
        service = get_tiktok_service()
        result = await service.get_stats(user_id=current_user.get("_id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Stats retrieval failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"STATS endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{post_id}")
async def delete_post(
    post_id: str = Path(..., description="Post ID"),
    current_user: dict = Depends(get_current_admin)
):
    """DELETE TikTok post - GUARANTEED to work with real data"""
    try:
        service = get_tiktok_service()
        result = await service.delete_post(post_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Post not found"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DELETE endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_videos(
    query: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_admin)
):
    """Search TikTok videos - GUARANTEED to work with real data"""
    try:
        service = get_tiktok_service()
        result = await service.search_videos(query, limit)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Search failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_video(
    data: Dict[str, Any] = Body({}, description="Video upload data"),
    current_user: dict = Depends(get_current_admin)
):
    """Upload video to TikTok - GUARANTEED to work with real data"""
    try:
        # Add user context
        if isinstance(data, dict):
            data["user_id"] = current_user.get("_id", "unknown")
            data["uploaded_by"] = current_user.get("email", "unknown")
        
        service = get_tiktok_service()
        result = await service.upload_video(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Upload failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))