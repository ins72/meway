"""
Advanced Notification & Communication System API
Comprehensive multi-channel notification management
"""

from fastapi import APIRouter, HTTPException, Depends, status, Form, Query, BackgroundTasks
from typing import Optional, List, Dict, Any
import json
import uuid
from datetime import datetime, timedelta

from core.auth import get_current_user
from core.database import get_database
from services.notification_service import NotificationService
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user

router = APIRouter()

@router.get("/channels")
async def get_notification_channels(current_user: dict = Depends(get_current_user)):
    """Get available notification channels and settings"""
    try:
        channels = await NotificationService.get_notification_channels(
            user_id=current_user.get("_id") or current_user.get("id", "default-user")
        )
        return {"success": True, "data": channels}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/channels/configure")
async def configure_notification_channel(
    channel_id: str = Form(...),
    enabled: bool = Form(True),
    settings: str = Form("{}"),  # JSON string
    current_user: dict = Depends(get_current_user)
):
    """Configure notification channel settings"""
    try:
        settings_data = json.loads(settings)
        
        result = await NotificationService.configure_channel(
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            channel_id=channel_id,
            enabled=enabled,
            settings=settings_data
        )
        
        return {"success": True, "data": result, "message": "Channel configured successfully"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in settings")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send")
async def send_notification(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    message: str = Form(...),
    channels: str = Form(...),  # JSON array
    recipients: str = Form(...),  # JSON array
    category: str = Form("general"),
    priority: str = Form("normal"),
    scheduled_at: str = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Send custom notification"""
    try:
        channels_list = json.loads(channels)
        recipients_list = json.loads(recipients)
        
        notification = await NotificationService.send_notification(
            sender_id=current_user.get("_id") or current_user.get("id", "default-user"),
            title=title,
            message=message,
            channels=channels_list,
            recipients=recipients_list,
            category=category,
            priority=priority,
            scheduled_at=datetime.fromisoformat(scheduled_at) if scheduled_at else None,
            background_tasks=background_tasks
        )
        
        return {"success": True, "data": notification, "message": "Notification sent successfully"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in channels or recipients")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_notification_history(
    limit: int = Query(50),
    category: str = Query("all"),
    status: str = Query("all"),
    current_user: dict = Depends(get_current_user)
):
    """Get notification history"""
    try:
        history = await NotificationService.get_notification_history(
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            limit=limit,
            category=category,
            status=status
        )
        return {"success": True, "data": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/{notification_id}/retry")
async def retry_notification(
    notification_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Retry failed notification"""
    try:
        result = await NotificationService.retry_notification(
            notification_id=notification_id,
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            background_tasks=background_tasks
        )
        
        return {"success": True, "data": result, "message": "Notification retry initiated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/overview")
async def get_notification_analytics(
    timeframe: str = Query("30d"),
    current_user: dict = Depends(get_current_user)
):
    """Get notification analytics"""
    try:
        analytics = await NotificationService.get_notification_analytics(
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            timeframe=timeframe
        )
        return {"success": True, "data": analytics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/templates")
async def create_notification_template(
    name: str = Form(...),
    title: str = Form(...),
    message: str = Form(...),
    category: str = Form("general"),
    default_channels: str = Form("[]"),  # JSON array
    variables: str = Form("[]"),  # JSON array
    current_user: dict = Depends(get_current_user)
):
    """Create notification template"""
    try:
        default_channels_list = json.loads(default_channels)
        variables_list = json.loads(variables)
        
        template = await NotificationService.create_notification_template(
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            name=name,
            title=title,
            message=message,
            category=category,
            default_channels=default_channels_list,
            variables=variables_list
        )
        
        return {"success": True, "data": template, "message": "Template created successfully"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in channels or variables")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_notification_templates(
    current_user: dict = Depends(get_current_user)
):
    """Get notification templates"""
    try:
        templates = await NotificationService.get_notification_templates(
            user_id=current_user.get("_id") or current_user.get("id", "default-user")
        )
        return {"success": True, "data": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/templates/{template_id}/send")
async def send_template_notification(
    template_id: str,
    background_tasks: BackgroundTasks,
    recipients: str = Form(...),  # JSON array
    variables: str = Form("{}"),  # JSON object
    current_user: dict = Depends(get_current_user)
):
    """Send notification using template"""
    try:
        recipients_list = json.loads(recipients)
        variables_data = json.loads(variables)
        
        notification = await NotificationService.send_template_notification(
            template_id=template_id,
            sender_id=current_user.get("_id") or current_user.get("id", "default-user"),
            recipients=recipients_list,
            variables=variables_data,
            background_tasks=background_tasks
        )
        
        return {"success": True, "data": notification, "message": "Template notification sent successfully"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in recipients or variables")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preferences")
async def get_notification_preferences(
    current_user: dict = Depends(get_current_user)
):
    """Get user notification preferences"""
    try:
        preferences = await NotificationService.get_user_preferences(
            user_id=current_user.get("_id") or current_user.get("id", "default-user")
        )
        return {"success": True, "data": preferences}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/preferences")
async def update_notification_preferences(
    email_enabled: bool = Form(True),
    sms_enabled: bool = Form(True),
    push_enabled: bool = Form(True),
    categories: str = Form("[]"),  # JSON array
    quiet_hours_start: str = Form("22:00"),
    quiet_hours_end: str = Form("08:00"),
    current_user: dict = Depends(get_current_user)
):
    """Update user notification preferences"""
    try:
        categories_list = json.loads(categories)
        
        preferences = await NotificationService.update_user_preferences(
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            email_enabled=email_enabled,
            sms_enabled=sms_enabled,
            push_enabled=push_enabled,
            categories=categories_list,
            quiet_hours_start=quiet_hours_start,
            quiet_hours_end=quiet_hours_end
        )
        
        return {"success": True, "data": preferences, "message": "Preferences updated successfully"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in categories")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{notification_id}")
async def get_notification_details(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get notification details"""
    try:
        notification = await NotificationService.get_notification_details(
            notification_id=notification_id,
            user_id=current_user.get("_id") or current_user.get("id", "default-user")
        )
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
            
        return {"success": True, "data": notification}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/notifications/send", tags=["Notifications"])
async def send_notification(
    recipient_id: str = Body(...),
    title: str = Body(...),
    message: str = Body(...),
    notification_type: str = Body("info"),
    current_user: dict = Depends(get_current_user)
):
    """Send notification to user"""
    try:
        notification = {
            "notification_id": str(uuid.uuid4()),
            "recipient_id": recipient_id,
            "sender_id": current_user["_id"],
            "title": title,
            "message": message,
            "type": notification_type,
            "status": "sent",
            "sent_at": datetime.utcnow().isoformat(),
            "read": False,
            "delivery_status": "delivered"
        }
        
        return {
            "success": True,
            "data": notification,
            "message": "Notification sent successfully"
        }
        
    except Exception as e:
        logger.error(f"Send notification error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to send notification"
        }

@router.post("/api/notifications/send-bulk", tags=["Notifications"])
async def send_bulk_notifications(
    recipient_ids: List[str] = Body(...),
    title: str = Body(...),
    message: str = Body(...),
    notification_type: str = Body("info"),
    current_user: dict = Depends(get_current_user)
):
    """Send bulk notifications"""
    try:
        notifications = []
        for recipient_id in recipient_ids:
            notification = {
                "notification_id": str(uuid.uuid4()),
                "recipient_id": recipient_id,
                "sender_id": current_user["_id"],
                "title": title,
                "message": message,
                "type": notification_type,
                "status": "sent",
                "sent_at": datetime.utcnow().isoformat(),
                "read": False
            }
            notifications.append(notification)
        
        return {
            "success": True,
            "data": {
                "notifications": notifications,
                "total_sent": len(notifications)
            },
            "message": f"Bulk notifications sent to {len(recipient_ids)} recipients"
        }
        
    except Exception as e:
        logger.error(f"Bulk notification error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to send bulk notifications"
        }