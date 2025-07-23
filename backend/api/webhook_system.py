"""
Advanced Webhook & Event Management API
Comprehensive webhook registry and event-driven architecture
"""

from fastapi import APIRouter, HTTPException, Depends, status, Form, Query, Request, BackgroundTasks
from typing import Optional, List, Dict, Any
import json
import uuid
import secrets
import hmac
import hashlib
from datetime import datetime, timedelta

from core.auth import get_current_user
from core.database import get_database
from services.webhook_service import WebhookService
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user

router = APIRouter()

@router.get("/registry")
async def get_webhook_registry():
    """Get comprehensive webhook registry and event catalog"""
    try:
        registry = await WebhookService.get_webhook_registry()
        return {"success": True, "data": registry}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
async def get_webhooks(
    status: str = Query("all"),
    event_filter: str = Query("all"),
    current_user: dict = Depends(get_current_user)
):
    """Get user's webhooks with filtering"""
    try:
        webhooks = await WebhookService.get_user_webhooks(
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            status_filter=status,
            event_filter=event_filter
        )
        return {"success": True, "data": webhooks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def create_webhook(
    name: str = Form(...),
    url: str = Form(...),
    events: str = Form(...),  # JSON array
    retry_config: str = Form("{}"),  # JSON object
    security_config: str = Form("{}"),  # JSON object
    custom_headers: str = Form("{}"),  # JSON object
    rate_limiting: str = Form("{}"),  # JSON object
    current_user: dict = Depends(get_current_user)
):
    """Create advanced webhook with comprehensive configuration"""
    try:
        events_list = json.loads(events)
        retry_settings = json.loads(retry_config) if retry_config else {}
        security_settings = json.loads(security_config) if security_config else {}
        headers = json.loads(custom_headers) if custom_headers else {}
        rate_limit_config = json.loads(rate_limiting) if rate_limiting else {}
        
        webhook = await WebhookService.create_webhook(
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            name=name,
            url=url,
            events=events_list,
            retry_settings=retry_settings,
            security_settings=security_settings,
            custom_headers=headers,
            rate_limit_config=rate_limit_config
        )
        
        return {"success": True, "data": webhook, "message": "Webhook created successfully"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in configuration")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{webhook_id}")
async def get_webhook_details(
    webhook_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed webhook information"""
    try:
        webhook = await WebhookService.get_webhook_details(
            webhook_id=webhook_id,
            user_id=current_user.get("_id") or current_user.get("id", "default-user")
        )
        
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
            
        return {"success": True, "data": webhook}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{webhook_id}")
async def update_webhook(
    webhook_id: str,
    name: str = Form(None),
    url: str = Form(None),
    events: str = Form(None),  # JSON array
    retry_config: str = Form(None),
    security_config: str = Form(None),
    status: str = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Update webhook configuration"""
    try:
        updates = {}
        if name:
            updates["name"] = name
        if url:
            updates["url"] = url
        if events:
            updates["events"] = json.loads(events)
        if retry_config:
            updates["retry_config"] = json.loads(retry_config)
        if security_config:
            updates["security_config"] = json.loads(security_config)
        if status:
            updates["status"] = status
            
        webhook = await WebhookService.update_webhook(
            webhook_id=webhook_id,
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            updates=updates
        )
        
        return {"success": True, "data": webhook, "message": "Webhook updated successfully"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in configuration")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete webhook"""
    try:
        result = await WebhookService.delete_webhook(
            webhook_id=webhook_id,
            user_id=current_user.get("_id") or current_user.get("id", "default-user")
        )
        
        return {"success": True, "message": "Webhook deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{webhook_id}/test")
async def test_webhook(
    webhook_id: str,
    test_event: str = Form("user.created"),
    custom_payload: str = Form("{}"),
    current_user: dict = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Test webhook with sample payload"""
    try:
        payload_data = json.loads(custom_payload) if custom_payload else {}
        
        result = await WebhookService.test_webhook(
            webhook_id=webhook_id,
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            test_event=test_event,
            custom_payload=payload_data,
            background_tasks=background_tasks
        )
        
        return {"success": True, "data": result, "message": "Webhook test initiated"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in payload")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{webhook_id}/deliveries")
async def get_webhook_deliveries(
    webhook_id: str,
    limit: int = Query(50),
    status_filter: str = Query("all"),
    current_user: dict = Depends(get_current_user)
):
    """Get webhook delivery history"""
    try:
        deliveries = await WebhookService.get_webhook_deliveries(
            webhook_id=webhook_id,
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            limit=limit,
            status_filter=status_filter
        )
        
        return {"success": True, "data": deliveries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{webhook_id}/retry/{delivery_id}")
async def retry_webhook_delivery(
    webhook_id: str,
    delivery_id: str,
    current_user: dict = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Retry failed webhook delivery"""
    try:
        result = await WebhookService.retry_webhook_delivery(
            webhook_id=webhook_id,
            delivery_id=delivery_id,
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            background_tasks=background_tasks
        )
        
        return {"success": True, "data": result, "message": "Webhook delivery retry initiated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{webhook_id}/analytics")
async def get_webhook_analytics(
    webhook_id: str,
    timeframe: str = Query("30d"),
    current_user: dict = Depends(get_current_user)
):
    """Get webhook analytics and performance metrics"""
    try:
        analytics = await WebhookService.get_webhook_analytics(
            webhook_id=webhook_id,
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            timeframe=timeframe
        )
        
        return {"success": True, "data": analytics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/catalog")
async def get_event_catalog():
    """Get comprehensive event catalog with schemas"""
    try:
        catalog = await WebhookService.get_event_catalog()
        return {"success": True, "data": catalog}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events/trigger")
async def trigger_custom_event(
    event_name: str = Form(...),
    payload: str = Form(...),  # JSON object
    current_user: dict = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Trigger custom webhook event (admin only)"""
    try:
        # Check if user has admin privileges
        user_role = current_user.get("role", "user")
        if user_role not in ["admin", "super_admin"]:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        payload_data = json.loads(payload)
        
        result = await WebhookService.trigger_custom_event(
            event_name=event_name,
            payload=payload_data,
            triggered_by=current_user.get("_id") or current_user.get("id", "default-user"),
            background_tasks=background_tasks
        )
        
        return {"success": True, "data": result, "message": "Custom event triggered"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in payload")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/health")
async def get_webhook_system_health():
    """Get webhook system health status"""
    try:
        health = await WebhookService.get_system_health()
        return {"success": True, "data": health}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate-payload")
async def validate_webhook_payload(
    event_type: str = Form(...),
    payload: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Validate webhook payload against event schema"""
    try:
        payload_data = json.loads(payload)
        
        validation_result = await WebhookService.validate_event_payload(
            event_type=event_type,
            payload=payload_data
        )
        
        return {"success": True, "data": validation_result}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in payload")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/overview")
async def get_webhook_stats_overview(
    current_user: dict = Depends(get_current_user)
):
    """Get webhook system statistics overview"""
    try:
        stats = await WebhookService.get_webhook_stats_overview(
            user_id=current_user.get("_id") or current_user.get("id", "default-user")
        )
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))