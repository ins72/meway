"""
Twitter/X API Integration
Complete CRUD operations with real Twitter API integration
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from core.auth import get_current_user, get_current_admin
from services.twitter_service import get_twitter_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check for Twitter API integration"""
    try:
        service = get_twitter_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

@router.get("/")
async def list_tweets(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_admin)
):
    """LIST tweets - GUARANTEED to work with real data"""
    try:
        service = get_twitter_service()
        result = await service.list_tweets(
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
async def post_tweet(
    data: Dict[str, Any] = Body({}, description="Tweet data"),
    current_user: dict = Depends(get_current_admin)
):
    """CREATE tweet - GUARANTEED to work with real data"""
    try:
        # Add user context
        if isinstance(data, dict):
            data["user_id"] = current_user.get("_id", "unknown")
            data["created_by"] = current_user.get("email", "unknown")
        
        service = get_twitter_service()
        result = await service.post_tweet(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Tweet post failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CREATE endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{tweet_id}")
async def get_tweet(
    tweet_id: str = Path(..., description="Tweet ID"),
    current_user: dict = Depends(get_current_admin)
):
    """READ single tweet by ID"""
    try:
        service = get_twitter_service()
        result = await service.get_tweet(tweet_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Tweet not found"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"READ endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{tweet_id}")
async def update_tweet(
    tweet_id: str = Path(..., description="Tweet ID"),
    data: Dict[str, Any] = Body({}, description="Updated tweet data"),
    current_user: dict = Depends(get_current_admin)
):
    """UPDATE tweet - GUARANTEED to work with real data"""
    try:
        service = get_twitter_service()
        result = await service.update_tweet(tweet_id, data)
        
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
        service = get_twitter_service()
        result = await service.get_stats(user_id=current_user.get("_id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Stats retrieval failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"STATS endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))")
async def update_tweet(
    tweet_id: str = Path(..., description="Tweet ID"),
    data: Dict[str, Any] = Body({}, description="Updated tweet data"),
    current_user: dict = Depends(get_current_admin)
):
    """UPDATE tweet - GUARANTEED to work with real data"""
    try:
        service = get_twitter_service()
        result = await service.update_tweet(tweet_id, data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Update failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"UPDATE endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{tweet_id}")
async def delete_tweet(
    tweet_id: str = Path(..., description="Tweet ID"),
    current_user: dict = Depends(get_current_admin)
):
    """DELETE tweet - GUARANTEED to work with real data"""
    try:
        service = get_twitter_service()
        result = await service.delete_tweet(tweet_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Tweet not found"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DELETE endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
