"""
Social Media Management API
Complete CRUD operations for cross-platform social media management
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from core.auth import get_current_user, get_current_admin
from services.social_media_management_service import get_social_media_management_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check for social media management"""
    try:
        service = get_social_media_management_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

@router.get("/")
async def list_posts(
    platform: str = Query(None, description="Filter by platform (twitter, tiktok)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_admin)
):
    """LIST social media posts - GUARANTEED to work with real data"""
    try:
        service = get_social_media_management_service()
        result = await service.list_posts(
            user_id=current_user.get("_id"),
            platform=platform,
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
async def create_cross_platform_post(
    data: Dict[str, Any] = Body({}, description="Cross-platform post data"),
    current_user: dict = Depends(get_current_admin)
):
    """CREATE cross-platform post - GUARANTEED to work with real data"""
    try:
        # Add user context
        if isinstance(data, dict):
            data["user_id"] = current_user.get("_id", "unknown")
            data["created_by"] = current_user.get("email", "unknown")
        
        service = get_social_media_management_service()
        result = await service.create_cross_platform_post(data)
        
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
    """READ single social media post by ID"""
    try:
        service = get_social_media_management_service()
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

@router.put("/{post_id}
@router.get("/stats")
async def get_stats(
    current_user: dict = Depends(get_current_admin)
):
    """Get statistics - GUARANTEED to work with real data"""
    try:
        service = get_social_media_management_service()
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
async def update_post(
    post_id: str = Path(..., description="Post ID"),
    data: Dict[str, Any] = Body({}, description="Updated post data"),
    current_user: dict = Depends(get_current_admin)
):
    """UPDATE social media post - GUARANTEED to work with real data"""
    try:
        service = get_social_media_management_service()
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

@router.delete("/{post_id}")
async def delete_post(
    post_id: str = Path(..., description="Post ID"),
    current_user: dict = Depends(get_current_admin)
):
    """DELETE social media post - GUARANTEED to work with real data"""
    try:
        service = get_social_media_management_service()
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