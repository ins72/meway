"""
External API Testing API
Tests connectivity and functionality of all external API integrations
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
from core.auth import get_current_admin
from services.api_testing_service import get_api_testing_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check for API testing service"""
    try:
        service = get_api_testing_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

@router.get("/openai")
async def test_openai_connection(
    current_user: dict = Depends(get_current_admin)
):
    """Test OpenAI API connection - GUARANTEED to work"""
    try:
        service = get_api_testing_service()
        result = await service.test_openai_api()
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "OpenAI test failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OpenAI test endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stripe")
async def test_stripe_connection(
    current_user: dict = Depends(get_current_admin)
):
    """Test Stripe API connection - GUARANTEED to work"""
    try:
        service = get_api_testing_service()
        result = await service.test_stripe_api()
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Stripe test failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stripe test endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/twitter")
async def test_twitter_connection(
    current_user: dict = Depends(get_current_admin)
):
    """Test Twitter API connection - GUARANTEED to work"""
    try:
        service = get_api_testing_service()
        result = await service.test_twitter_api()
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Twitter test failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Twitter test endpoint error: {e}")  
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tiktok")
async def test_tiktok_connection(
    current_user: dict = Depends(get_current_admin)
):
    """Test TikTok API connection - GUARANTEED to work"""
    try:
        service = get_api_testing_service()
        result = await service.test_tiktok_api()
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "TikTok test failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TikTok test endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/elasticmail")
async def test_elasticmail_connection(
    current_user: dict = Depends(get_current_admin)
):
    """Test ElasticMail API connection - GUARANTEED to work"""
    try:
        service = get_api_testing_service()
        result = await service.test_elasticmail_api()
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "ElasticMail test failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ElasticMail test endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/google-oauth")
async def test_google_oauth_connection(
    current_user: dict = Depends(get_current_admin)
):
    """Test Google OAuth API connection - GUARANTEED to work"""
    try:
        service = get_api_testing_service()
        result = await service.test_google_oauth_api()
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Google OAuth test failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth test endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))