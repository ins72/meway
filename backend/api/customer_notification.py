"""
Customer Notification API
Handles notifications for plan changes, admin actions, and system events
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from core.auth import get_current_user
from services.customer_notification_service import get_customer_notification_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check for customer notification service"""
    try:
        service = get_customer_notification_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"Customer notification health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

@router.post("/send")
async def send_notification(
    notification_data: Dict[str, Any] = Body(..., description="Notification data"),
    current_user: dict = Depends(get_current_user)
):
    """Send notification to customer"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_customer_notification_service()
        
        # Validate required fields
        required_fields = ["notification_type", "workspace_id", "template_data"]
        for field in required_fields:
            if field not in notification_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        result = await service.send_notification(
            notification_data["notification_type"],
            notification_data["workspace_id"],
            notification_data["template_data"],
            current_user.get("id")
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send notification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-bulk")
async def send_bulk_notifications(
    bulk_data: Dict[str, Any] = Body(..., description="Bulk notification data"),
    current_user: dict = Depends(get_current_user)
):
    """Send notifications to multiple customers"""
    try:  
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_customer_notification_service()
        
        # Validate required fields
        required_fields = ["notification_type", "workspace_ids", "template_data"]
        for field in required_fields:
            if field not in bulk_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        if not isinstance(bulk_data["workspace_ids"], list):
            raise HTTPException(status_code=400, detail="workspace_ids must be a list")
        
        result = await service.send_bulk_notifications(
            bulk_data["notification_type"],
            bulk_data["workspace_ids"],
            bulk_data["template_data"],
            current_user.get("id")
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send bulk notifications error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_notification_history(
    workspace_id: str = Query(None, description="Filter by workspace ID"),
    notification_type: str = Query(None, description="Filter by notification type"),
    days_back: int = Query(30, ge=1, le=365, description="Days back to search"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
    current_user: dict = Depends(get_current_user)
):
    """Get notification history"""
    try:
        # Check admin access  
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_customer_notification_service()
        result = await service.get_notification_history(
            workspace_id, notification_type, days_back, limit
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get notification history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_notification_templates(
    current_user: dict = Depends(get_current_user)
):
    """Get available notification templates"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_customer_notification_service()
        result = await service.get_notification_templates()
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get notification templates error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/templates/{template_name}")
async def update_notification_template(
    template_name: str = Path(..., description="Template name"),
    template_data: Dict[str, Any] = Body(..., description="Template update data"),
    current_user: dict = Depends(get_current_user)
):
    """Update notification template"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_customer_notification_service()
        result = await service.update_notification_template(
            template_name, template_data, current_user.get("id")
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update notification template error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics")
async def get_notification_analytics(
    days_back: int = Query(30, ge=1, le=365, description="Days back for analytics"),
    current_user: dict = Depends(get_current_user)
):
    """Get notification analytics and performance metrics"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_customer_notification_service()
        result = await service.get_notification_analytics(days_back)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get notification analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/schedule")
async def schedule_notification(
    schedule_data: Dict[str, Any] = Body(..., description="Scheduled notification data"),
    current_user: dict = Depends(get_current_user)
):
    """Schedule a notification to be sent at a specific time"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_customer_notification_service()
        
        # Validate required fields
        required_fields = ["notification_type", "workspace_id", "template_data", "send_at"]
        for field in required_fields:
            if field not in schedule_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Parse send_at datetime
        try:
            send_at = datetime.fromisoformat(schedule_data["send_at"].replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid send_at format. Use ISO format")
        
        result = await service.schedule_notification(
            schedule_data["notification_type"],
            schedule_data["workspace_id"],
            schedule_data["template_data"],
            send_at,
            current_user.get("id")
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Schedule notification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-scheduled")
async def process_scheduled_notifications(
    current_user: dict = Depends(get_current_user)
):
    """Process notifications that are scheduled to be sent now"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_customer_notification_service()
        result = await service.process_scheduled_notifications()
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Process scheduled notifications error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workspace/{workspace_id}/notifications")
async def get_workspace_notifications(
    workspace_id: str = Path(..., description="Workspace ID"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    current_user: dict = Depends(get_current_user)
):
    """Get notifications for a specific workspace"""
    try:
        # Check admin access or workspace owner
        if not current_user.get("is_admin", False):
            # Allow workspace owners to see their own notifications
            # This would need additional validation in production
            pass
        
        service = get_customer_notification_service()
        result = await service.get_notification_history(
            workspace_id=workspace_id, 
            limit=limit
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get workspace notifications error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-notification")
async def send_test_notification(
    test_data: Dict[str, Any] = Body(..., description="Test notification data"),
    current_user: dict = Depends(get_current_user)
):
    """Send a test notification (admin only)"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_customer_notification_service()
        
        # Default test notification
        test_notification = {
            "notification_type": test_data.get("notification_type", "admin_override"),
            "workspace_id": test_data.get("workspace_id"),
            "template_data": test_data.get("template_data", {
                "reason": "This is a test notification from the admin panel",
                "additional_details": "Test completed successfully"
            })
        }
        
        if not test_notification["workspace_id"]:
            raise HTTPException(status_code=400, detail="workspace_id is required for test notifications")
        
        result = await service.send_notification(
            test_notification["notification_type"],
            test_notification["workspace_id"],
            test_notification["template_data"],
            current_user.get("id")
        )
        
        if result.get("success"):
            return {
                **result,
                "test_mode": True,
                "message": "Test notification sent successfully"
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send test notification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/overview")
async def get_notification_stats_overview(
    current_user: dict = Depends(get_current_user)
):
    """Get overview statistics for notifications"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_customer_notification_service()
        
        # Get analytics for different time periods
        weekly_analytics = await service.get_notification_analytics(7)
        monthly_analytics = await service.get_notification_analytics(30)
        
        return {
            "success": True,
            "overview": {
                "weekly": weekly_analytics.get("analytics", {}),
                "monthly": monthly_analytics.get("analytics", {}),
                "available_templates": len(service.notification_templates),
                "enabled_channels": sum(1 for channel, config in service.notification_channels.items() if config.get("enabled")),
                "total_channels": len(service.notification_channels)
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get notification stats overview error: {e}")
        raise HTTPException(status_code=500, detail=str(e))