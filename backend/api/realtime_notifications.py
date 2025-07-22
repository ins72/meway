"""
Real-time Notifications API Endpoints
Multi-channel notifications with WebSocket, email, SMS, and push notifications
"""
from fastapi import APIRouter, HTTPException, Depends, status, WebSocket, WebSocketDisconnect, Query
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel
import uuid

from core.auth import get_current_user
from core.realtime_notification_system import (
    WebSocketConnectionManager, NotificationProcessor, Notification,
    NotificationType, NotificationChannel
)
from core.professional_logger import professional_logger, LogLevel, LogCategory

router = APIRouter(
    prefix="/api/notifications",
    tags=["Real-time Notifications"]
)

# Global instances
connection_manager = WebSocketConnectionManager()
notification_processor = NotificationProcessor(connection_manager)

# Pydantic models
class CreateNotificationRequest(BaseModel):
    title: str
    message: str
    notification_type: str = "info"  # info, success, warning, error, critical, marketing, system
    channels: List[str] = ["websocket", "in_app"]  # websocket, email, sms, push, in_app, slack, discord
    priority: int = 5  # 1-10, 10 being highest
    data: Optional[Dict[str, Any]] = None
    action_url: Optional[str] = None
    action_text: Optional[str] = None
    scheduled_for: Optional[str] = None
    expires_at: Optional[str] = None

class BulkNotificationRequest(BaseModel):
    user_ids: List[str]
    title: str
    message: str
    notification_type: str = "info"
    channels: List[str] = ["websocket", "in_app"]
    priority: int = 5
    data: Optional[Dict[str, Any]] = None

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time notifications
    
    - **user_id**: The ID of the user to receive notifications
    """
    try:
        await connection_manager.connect(websocket, user_id)
        
        while True:
            try:
                # Keep connection alive with ping/pong
                data = await websocket.receive_text()
                
                # Handle ping messages
                if data == "ping":
                    await websocket.send_text("pong")
                
                # Update last ping time
                if websocket in connection_manager.connection_metadata:
                    connection_manager.connection_metadata[websocket]["last_ping"] = datetime.utcnow()
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                await professional_logger.log(
                    LogLevel.ERROR, LogCategory.SYSTEM,
                    f"WebSocket error for user {user_id}: {str(e)}",
                    error=e,
                    user_id=user_id
                )
                break
                
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.SYSTEM,
            f"WebSocket connection error for user {user_id}: {str(e)}",
            error=e
        )
    finally:
        connection_manager.disconnect(websocket)

@router.post("/send", response_model=Dict[str, Any])
async def send_notification(
    notification_request: CreateNotificationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Send notification to the current user through specified channels
    
    - **title**: Notification title
    - **message**: Notification message content
    - **notification_type**: Type of notification (info, success, warning, error, critical, marketing, system)
    - **channels**: Delivery channels (websocket, email, sms, push, in_app, slack, discord)
    - **priority**: Priority level 1-10 (10 being highest)
    - **data**: Optional additional data
    - **action_url**: Optional URL for action button
    - **action_text**: Optional text for action button
    - **scheduled_for**: Optional scheduled delivery time (ISO format)
    - **expires_at**: Optional expiration time (ISO format)
    """
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user authentication"
            )
        
        # Validate notification type
        try:
            notification_type = NotificationType(notification_request.notification_type)
        except ValueError:
            valid_types = [t.value for t in NotificationType]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid notification type. Valid types: {', '.join(valid_types)}"
            )
        
        # Validate channels
        try:
            channels = [NotificationChannel(ch) for ch in notification_request.channels]
        except ValueError:
            valid_channels = [ch.value for ch in NotificationChannel]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid notification channel. Valid channels: {', '.join(valid_channels)}"
            )
        
        # Parse datetime fields
        scheduled_for = None
        expires_at = None
        
        if notification_request.scheduled_for:
            try:
                scheduled_for = datetime.fromisoformat(notification_request.scheduled_for.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid scheduled_for datetime format. Use ISO format."
                )
        
        if notification_request.expires_at:
            try:
                expires_at = datetime.fromisoformat(notification_request.expires_at.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid expires_at datetime format. Use ISO format."
                )
        
        # Create notification
        notification = Notification(
            notification_id=str(uuid.uuid4()),
            user_id=user_id,
            title=notification_request.title,
            message=notification_request.message,
            type=notification_type,
            channels=channels,
            priority=max(1, min(10, notification_request.priority)),  # Clamp between 1-10
            data=notification_request.data or {},
            created_at=datetime.utcnow(),
            scheduled_for=scheduled_for,
            expires_at=expires_at,
            action_url=notification_request.action_url,
            action_text=notification_request.action_text
        )
        
        # Send notification
        result = await notification_processor.send_notification(notification)
        
        await professional_logger.log(
            LogLevel.INFO, LogCategory.SYSTEM,
            f"Notification sent successfully",
            user_id=user_id,
            details={
                "notification_id": notification.notification_id,
                "channels": notification_request.channels,
                "priority": notification_request.priority
            }
        )
        
        return {
            "success": True,
            "notification_id": notification.notification_id,
            "result": result,
            "sent_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.SYSTEM,
            f"Failed to send notification: {str(e)}",
            error=e,
            user_id=current_user.get("_id")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send notification: {str(e)}"
        )

@router.post("/send-bulk", response_model=Dict[str, Any])
async def send_bulk_notification(
    bulk_request: BulkNotificationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Send notification to multiple users (admin only)
    
    - **user_ids**: List of user IDs to send notifications to
    - **title**: Notification title
    - **message**: Notification message content
    - **notification_type**: Type of notification
    - **channels**: Delivery channels
    - **priority**: Priority level 1-10
    - **data**: Optional additional data
    """
    try:
        # Check if current user is admin
        if not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required for bulk notifications"
            )
        
        # Validate notification type
        try:
            notification_type = NotificationType(bulk_request.notification_type)
        except ValueError:
            valid_types = [t.value for t in NotificationType]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid notification type. Valid types: {', '.join(valid_types)}"
            )
        
        # Validate channels
        try:
            channels = [NotificationChannel(ch) for ch in bulk_request.channels]
        except ValueError:
            valid_channels = [ch.value for ch in NotificationChannel]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid notification channel. Valid channels: {', '.join(valid_channels)}"
            )
        
        results = []
        
        # Send notification to each user
        for user_id in bulk_request.user_ids:
            try:
                notification = Notification(
                    notification_id=str(uuid.uuid4()),
                    user_id=user_id,
                    title=bulk_request.title,
                    message=bulk_request.message,
                    type=notification_type,
                    channels=channels,
                    priority=max(1, min(10, bulk_request.priority)),
                    data=bulk_request.data or {},
                    created_at=datetime.utcnow()
                )
                
                result = await notification_processor.send_notification(notification)
                results.append({
                    "user_id": user_id,
                    "notification_id": notification.notification_id,
                    "success": result.get("success", False),
                    "result": result
                })
                
            except Exception as e:
                results.append({
                    "user_id": user_id,
                    "success": False,
                    "error": str(e)
                })
        
        successful = len([r for r in results if r.get("success")])
        
        await professional_logger.log(
            LogLevel.INFO, LogCategory.SYSTEM,
            f"Bulk notification sent to {successful}/{len(bulk_request.user_ids)} users",
            user_id=current_user.get("_id"),
            details={
                "total_users": len(bulk_request.user_ids),
                "successful": successful,
                "channels": bulk_request.channels
            }
        )
        
        return {
            "success": True,
            "total_users": len(bulk_request.user_ids),
            "successful_sends": successful,
            "failed_sends": len(bulk_request.user_ids) - successful,
            "results": results,
            "sent_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.SYSTEM,
            f"Failed to send bulk notification: {str(e)}",
            error=e,
            user_id=current_user.get("_id")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send bulk notification: {str(e)}"
        )

@router.get("/history", response_model=Dict[str, Any])
async def get_notification_history(
    limit: int = Query(20, description="Maximum notifications to return", ge=1, le=100),
    notification_type: Optional[str] = Query(None, description="Filter by notification type"),
    channel: Optional[str] = Query(None, description="Filter by delivery channel"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get notification history for the current user
    
    - **limit**: Maximum number of notifications to return (1-100)
    - **notification_type**: Optional filter by notification type
    - **channel**: Optional filter by delivery channel
    """
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user authentication"
            )
        
        # Get notifications from database
        from core.database import get_database
        db = get_database()
        
        # Build query
        query = {"user_id": user_id}
        
        if notification_type:
            valid_types = [t.value for t in NotificationType]
            if notification_type not in valid_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid notification type. Valid types: {', '.join(valid_types)}"
                )
            query["type"] = notification_type
        
        if channel:
            valid_channels = [ch.value for ch in NotificationChannel]
            if channel not in valid_channels:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid channel. Valid channels: {', '.join(valid_channels)}"
                )
            query["channels"] = {"$in": [channel]}
        
        # Get notifications
        notifications = await db.notifications.find(query)\
            .sort("created_at", -1)\
            .limit(limit)\
            .to_list(length=limit)
        
        # Convert str to string and format dates
        for notification in notifications:
            notification["_id"] = str(notification["_id"])
            if "created_at" in notification:
                notification["created_at"] = notification["created_at"].isoformat()
            if notification.get("scheduled_for"):
                notification["scheduled_for"] = notification["scheduled_for"].isoformat()
            if notification.get("expires_at"):
                notification["expires_at"] = notification["expires_at"].isoformat()
        
        # Get summary statistics
        total_count = await db.notifications.count_documents({"user_id": user_id})
        unread_count = await db.notifications.count_documents({"user_id": user_id, "read": False})
        
        return {
            "success": True,
            "notifications": notifications,
            "total_notifications": total_count,
            "unread_count": unread_count,
            "returned_count": len(notifications),
            "filters": {
                "notification_type": notification_type,
                "channel": channel,
                "limit": limit
            },
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.SYSTEM,
            f"Failed to get notification history: {str(e)}",
            error=e,
            user_id=current_user.get("_id")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notification history: {str(e)}"
        )

@router.put("/mark-read/{notification_id}", response_model=Dict[str, Any])
async def mark_notification_read(
    notification_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Mark a notification as read
    
    - **notification_id**: The ID of the notification to mark as read
    """
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user authentication"
            )
        
        # Update notification in database
        from core.database import get_database
        db = get_database()
        
        result = await db.notifications.update_one(
            {
                "notification_id": notification_id,
                "user_id": user_id
            },
            {
                "$set": {
                    "read": True,
                    "read_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found or already read"
            )
        
        return {
            "success": True,
            "message": "Notification marked as read",
            "notification_id": notification_id,
            "read_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.SYSTEM,
            f"Failed to mark notification as read: {str(e)}",
            error=e,
            user_id=current_user.get("_id")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )

@router.put("/mark-all-read", response_model=Dict[str, Any])
async def mark_all_notifications_read(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Mark all notifications as read for the current user
    """
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user authentication"
            )
        
        # Update all unread notifications
        from core.database import get_database
        db = get_database()
        
        result = await db.notifications.update_many(
            {
                "user_id": user_id,
                "read": False
            },
            {
                "$set": {
                    "read": True,
                    "read_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "message": f"Marked {result.modified_count} notifications as read",
            "notifications_updated": result.modified_count,
            "updated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.SYSTEM,
            f"Failed to mark all notifications as read: {str(e)}",
            error=e,
            user_id=current_user.get("_id")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark all notifications as read: {str(e)}"
        )

@router.get("/stats", response_model=Dict[str, Any])
async def get_notification_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get notification statistics for the current user
    """
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user authentication"
            )
        
        from core.database import get_database
        db = get_database()
        
        # Get statistics
        total_notifications = await db.notifications.count_documents({"user_id": user_id})
        unread_notifications = await db.notifications.count_documents({"user_id": user_id, "read": False})
        clicked_notifications = await db.notifications.count_documents({"user_id": user_id, "clicked": True})
        
        # Get notifications by type
        type_stats = await db.notifications.aggregate([
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$type", "count": {"$sum": 1}}}
        ]).to_list(length=None)
        
        # Get notifications by channel
        channel_stats = await db.notifications.aggregate([
            {"$match": {"user_id": user_id}},
            {"$unwind": "$channels"},
            {"$group": {"_id": "$channels", "count": {"$sum": 1}}}
        ]).to_list(length=None)
        
        # Get recent activity (last 30 days)
        from datetime import timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_notifications = await db.notifications.count_documents({
            "user_id": user_id,
            "created_at": {"$gte": thirty_days_ago}
        })
        
        # Calculate statistics
        read_percentage = (total_notifications - unread_notifications) / total_notifications * 100 if total_notifications > 0 else 0
        click_percentage = clicked_notifications / total_notifications * 100 if total_notifications > 0 else 0
        
        # Get active WebSocket connections count
        active_connections = connection_manager.get_user_connection_count(user_id)
        
        return {
            "success": True,
            "stats": {
                "total_notifications": total_notifications,
                "unread_notifications": unread_notifications,
                "read_notifications": total_notifications - unread_notifications,
                "clicked_notifications": clicked_notifications,
                "read_percentage": round(read_percentage, 1),
                "click_percentage": round(click_percentage, 1),
                "recent_notifications_30d": recent_notifications,
                "active_websocket_connections": active_connections,
                "notifications_by_type": type_stats,
                "notifications_by_channel": channel_stats
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.SYSTEM,
            f"Failed to get notification stats: {str(e)}",
            error=e,
            user_id=current_user.get("_id")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notification stats: {str(e)}"
        )

@router.get("/connection-status", response_model=Dict[str, Any])
async def get_connection_status(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get real-time connection status for the current user
    """
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user authentication"
            )
        
        # Get connection information
        active_connections = connection_manager.get_user_connection_count(user_id)
        total_connections = connection_manager.get_total_connections()
        
        # Get connection metadata if user has active connections
        connection_details = []
        if user_id in connection_manager.active_connections:
            for websocket in connection_manager.active_connections[user_id]:
                if websocket in connection_manager.connection_metadata:
                    metadata = connection_manager.connection_metadata[websocket]
                    connection_details.append({
                        "connected_at": metadata["connected_at"].isoformat(),
                        "last_ping": metadata["last_ping"].isoformat()
                    })
        
        return {
            "success": True,
            "connection_status": {
                "user_id": user_id,
                "active_connections": active_connections,
                "is_connected": active_connections > 0,
                "connection_details": connection_details,
                "total_platform_connections": total_connections
            },
            "checked_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.SYSTEM,
            f"Failed to get connection status: {str(e)}",
            error=e,
            user_id=current_user.get("_id")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get connection status: {str(e)}"
        )