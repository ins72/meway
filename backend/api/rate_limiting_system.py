"""
API Rate Limiting & Throttling System API
Comprehensive rate limiting and usage analytics
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query, Request
from typing import Optional, List, Dict, Any
import json
import uuid
from datetime import datetime, timedelta

from core.auth import get_current_user
from core.database import get_database
from services.rate_limiting_service import RateLimitingService
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user

router = APIRouter()

@router.get("/status")
async def get_rate_limit_status(current_user: dict = Depends(get_current_user)):
    """Get current rate limit status for user"""
    try:
        status_data = await RateLimitingService.get_rate_limit_status(
            user_id=current_user.get("_id") or current_user.get("id", "default-user")
        )
        return {"success": True, "data": status_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_rate_limit_metrics(
    timeframe: str = Query("24h"),
    current_user: dict = Depends(get_current_user)
):
    """Get rate limiting metrics and analytics"""
    try:
        metrics = await RateLimitingService.get_rate_limit_metrics(
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            timeframe=timeframe
        )
        return {"success": True, "data": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usage")
async def get_api_usage(
    timeframe: str = Query("24h"),
    endpoint: str = Query("all"),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed API usage statistics"""
    try:
        usage = await RateLimitingService.get_api_usage(
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            timeframe=timeframe,
            endpoint=endpoint
        )
        return {"success": True, "data": usage}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check")
async def check_rate_limit(
    request: Request,
    endpoint: str = Query(...),
    action: str = Query("api_call"),
    current_user: dict = Depends(get_current_user)
):
    """Check if request is within rate limits"""
    try:
        result = await RateLimitingService.check_rate_limit(
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            endpoint=endpoint,
            action=action,
            ip_address=request.client.host if request.client else "unknown"
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/record")
async def record_api_usage(
    request: Request,
    endpoint: str = Query(...),
    method: str = Query(...),
    response_time: float = Query(...),
    status_code: int = Query(...),
    current_user: dict = Depends(get_current_user)
):
    """Record API usage for analytics"""
    try:
        result = await RateLimitingService.record_api_usage(
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            endpoint=endpoint,
            method=method,
            response_time=response_time,
            status_code=status_code,
            ip_address=request.client.host if request.client else "unknown"
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quotas")
async def get_user_quotas(current_user: dict = Depends(get_current_user)):
    """Get user's rate limit quotas and subscription limits"""
    try:
        quotas = await RateLimitingService.get_user_quotas(
            user_id=current_user.get("_id") or current_user.get("id", "default-user")
        )
        return {"success": True, "data": quotas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_rate_limit_alerts(
    current_user: dict = Depends(get_current_user)
):
    """Get rate limit alerts and warnings"""
    try:
        alerts = await RateLimitingService.get_rate_limit_alerts(
            user_id=current_user.get("_id") or current_user.get("id", "default-user")
        )
        return {"success": True, "data": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-endpoints")
async def get_top_endpoints(
    limit: int = Query(10),
    timeframe: str = Query("24h"),
    current_user: dict = Depends(get_current_user)
):
    """Get top API endpoints by usage"""
    try:
        endpoints = await RateLimitingService.get_top_endpoints(
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            limit=limit,
            timeframe=timeframe
        )
        return {"success": True, "data": endpoints}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_performance_metrics(
    timeframe: str = Query("24h"),
    current_user: dict = Depends(get_current_user)
):
    """Get API performance metrics"""
    try:
        performance = await RateLimitingService.get_performance_metrics(
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            timeframe=timeframe
        )
        return {"success": True, "data": performance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/optimization")
async def get_optimization_suggestions(
    current_user: dict = Depends(get_current_user)
):
    """Get API usage optimization suggestions"""
    try:
        suggestions = await RateLimitingService.get_optimization_suggestions(
            user_id=current_user.get("_id") or current_user.get("id", "default-user")
        )
        return {"success": True, "data": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset")
async def reset_rate_limits(
    limit_type: str = Query(...),  # minute, hour, day
    current_user: dict = Depends(get_current_user)
):
    """Reset rate limits (admin only)"""
    try:
        # Check if user has admin privileges
        user_role = current_user.get("role", "user")
        if user_role not in ["admin", "super_admin"]:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = await RateLimitingService.reset_rate_limits(
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            limit_type=limit_type
        )
        return {"success": True, "data": result, "message": f"{limit_type} rate limits reset"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def get_rate_limiting_health():
    """Get rate limiting system health status"""
    try:
        health = await RateLimitingService.get_system_health()
        return {"success": True, "data": health}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))