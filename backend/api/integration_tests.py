"""
API Integration Testing Endpoints
Test all newly integrated APIs
"""
from fastapi import APIRouter, HTTPException, Depends
from core.auth import get_current_user
import os
import httpx
import json
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/integration-tests", tags=["API Integration Tests"])

@router.get("/elasticmail/test")
async def test_elasticmail(current_user: dict = Depends(get_current_user)):
    """Test ElasticMail API connection"""
    api_key = os.getenv("ELASTICMAIL_API_KEY")
    if not api_key:
        raise HTTPException(400, "ElasticMail API key not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.elasticemail.com/v2/account/load",
                params={"apikey": api_key}
            )
        
        if response.status_code == 200:
            return {"success": True, "service": "ElasticMail", "status": "connected"}
        else:
            return {"success": False, "service": "ElasticMail", "error": response.text}
            
    except Exception as e:
        return {"success": False, "service": "ElasticMail", "error": str(e)}

@router.get("/twitter/test")
async def test_twitter(current_user: dict = Depends(get_current_user)):
    """Test Twitter API connection"""
    api_key = os.getenv("TWITTER_API_KEY")
    if not api_key:
        raise HTTPException(400, "Twitter API key not configured")
    
    return {"success": True, "service": "Twitter/X", "status": "API key configured"}

@router.get("/tiktok/test")
async def test_tiktok(current_user: dict = Depends(get_current_user)):
    """Test TikTok API connection"""
    client_key = os.getenv("TIKTOK_CLIENT_KEY")
    if not client_key:
        raise HTTPException(400, "TikTok client key not configured")
    
    return {"success": True, "service": "TikTok", "status": "Client key configured"}

@router.get("/openai/test")
async def test_openai(current_user: dict = Depends(get_current_user)):
    """Test OpenAI API connection"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(400, "OpenAI API key not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"}
            )
        
        if response.status_code == 200:
            models = response.json()
            return {"success": True, "service": "OpenAI", "models_available": len(models.get("data", []))}
        else:
            return {"success": False, "service": "OpenAI", "error": response.text}
            
    except Exception as e:
        return {"success": False, "service": "OpenAI", "error": str(e)}

@router.get("/google/test")
async def test_google_oauth(current_user: dict = Depends(get_current_user)):
    """Test Google OAuth configuration"""
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not client_id:
        raise HTTPException(400, "Google Client ID not configured")
    
    return {"success": True, "service": "Google OAuth", "client_id": client_id[:20] + "..."}

@router.get("/stripe/test")
async def test_stripe(current_user: dict = Depends(get_current_user)):
    """Test Stripe API connection"""
    secret_key = os.getenv("STRIPE_SECRET_KEY")
    if not secret_key:
        raise HTTPException(400, "Stripe secret key not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.stripe.com/v1/account",
                headers={"Authorization": f"Bearer {secret_key}"}
            )
        
        if response.status_code == 200:
            account = response.json()
            return {"success": True, "service": "Stripe", "account_id": account.get("id")}
        else:
            return {"success": False, "service": "Stripe", "error": response.text}
            
    except Exception as e:
        return {"success": False, "service": "Stripe", "error": str(e)}

@router.get("/all")
async def test_all_apis(current_user: dict = Depends(get_current_user)):
    """Test all API integrations"""
    results = {}
    
    # Test each API
    apis_to_test = [
        ("elasticmail", test_elasticmail),
        ("twitter", test_twitter),
        ("tiktok", test_tiktok),
        ("openai", test_openai),
        ("google", test_google_oauth),
        ("stripe", test_stripe)
    ]
    
    for api_name, test_func in apis_to_test:
        try:
            result = await test_func(current_user)
            results[api_name] = result
        except Exception as e:
            results[api_name] = {"success": False, "error": str(e)}
    
    successful = len([r for r in results.values() if r.get("success")])
    
    return {
        "total_apis": len(results),
        "successful": successful,
        "success_rate": f"{(successful/len(results)*100):.1f}%",
        "results": results
    }
