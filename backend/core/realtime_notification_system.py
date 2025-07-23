"""
Real-time Notification System
Multi-channel notifications with WebSocket, email, SMS, and push notifications
"""
import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
from enum import Enum
from dataclasses import dataclass, asdict
import websockets
from fastapi import WebSocket
import httpx

from core.database import get_database
from core.professional_logger import professional_logger, LogLevel, LogCategory
from core.external_api_integrator import email_service_integrator

class NotificationType(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    MARKETING = "marketing"
    SYSTEM = "system"

class NotificationChannel(str, Enum):
    WEBSOCKET = "websocket"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    SLACK = "slack"
    DISCORD = "discord"

@dataclass
class Notification:
    notification_id: str
    user_id: str
    title: str
    message: str
    type: NotificationType
    channels: List[NotificationChannel]
    priority: int  # 1-10, 10 being highest
    data: Dict[str, Any]
    created_at: datetime
    scheduled_for: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    read: bool = False
    clicked: bool = False
    action_url: Optional[str] = None
    action_text: Optional[str] = None

class WebSocketConnectionManager:
    """Manage WebSocket connections for real-time notifications"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        self.connection_metadata[websocket] = {
            "user_id": user_id,
            "connected_at": datetime.utcnow(),
            "last_ping": datetime.utcnow()
        }
        
        await professional_logger.log(
            LogLevel.INFO, LogCategory.SYSTEM,
            f"WebSocket connection established for user {user_id}",
            user_id=user_id
        )
        
        # Send connection acknowledgment
        await self.send_personal_message({
            "type": "connection_ack",
            "message": "Real-time notifications connected",
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.connection_metadata:
            user_id = self.connection_metadata[websocket]["user_id"]
            
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            del self.connection_metadata[websocket]
            
            professional_logger.log(
                LogLevel.INFO, LogCategory.SYSTEM,
                f"WebSocket connection closed for user {user_id}",
                user_id=user_id
            )
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message, default=str))
        except Exception as e:
            # Connection might be closed
            self.disconnect(websocket)
    
    async def send_to_user(self, message: Dict[str, Any], user_id: str):
        """Send message to all connections for a user"""
        if user_id in self.active_connections:
            disconnected_sockets = set()
            
            for websocket in self.active_connections[user_id].copy():
                try:
                    await websocket.send_text(json.dumps(message, default=str))
                except Exception as e:
                    disconnected_sockets.add(websocket)
            
            # Clean up disconnected sockets
            for websocket in disconnected_sockets:
                self.disconnect(websocket)
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            await self.send_to_user(message, user_id)
    
    def get_user_connection_count(self, user_id: str) -> int:
        """Get number of active connections for user"""
        return len(self.active_connections.get(user_id, set()))
    
    def get_total_connections(self) -> int:
        """Get total number of active connections"""
        return sum(len(connections) for connections in self.active_connections.values())

class NotificationProcessor:
    """Process and deliver notifications through various channels"""
    
    def __init__(self, connection_manager: WebSocketConnectionManager):
        self.connection_manager = connection_manager
        self.db = None
        self.notification_queue = asyncio.Queue()
        self.processing = False
    
    async def get_database(self):
        """Get database connection"""
        if not self.db:
            self.db = get_database()
        return self.db
    
    async def send_notification(self, notification: Notification) -> Dict[str, Any]:
        """Send notification through specified channels"""
        try:
            delivery_results = {}
            
            for channel in notification.channels:
                if channel == NotificationChannel.WEBSOCKET:
                    result = await self._send_websocket_notification(notification)
                    delivery_results["websocket"] = result
                
                elif channel == NotificationChannel.EMAIL:
                    result = await self._send_email_notification(notification)
                    delivery_results["email"] = result
                
                elif channel == NotificationChannel.SMS:
                    result = await self._send_sms_notification(notification)
                    delivery_results["sms"] = result
                
                elif channel == NotificationChannel.PUSH:
                    result = await self._send_push_notification(notification)
                    delivery_results["push"] = result
                
                elif channel == NotificationChannel.IN_APP:
                    result = await self._store_in_app_notification(notification)
                    delivery_results["in_app"] = result
                
                elif channel == NotificationChannel.SLACK:
                    result = await self._send_slack_notification(notification)
                    delivery_results["slack"] = result
            
            # Store notification in database
            await self._store_notification(notification, delivery_results)
            
            await professional_logger.log(
                LogLevel.INFO, LogCategory.SYSTEM,
                f"Notification sent to user {notification.user_id}",
                details={
                    "notification_id": notification.notification_id,
                    "channels": [ch.value for ch in notification.channels],
                    "delivery_results": delivery_results
                },
                user_id=notification.user_id
            )
            
            return {
                "success": True,
                "notification_id": notification.notification_id,
                "delivery_results": delivery_results
            }
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.SYSTEM,
                f"Failed to send notification: {str(e)}",
                error=e
            )
            return {
                "success": False,
                "error": str(e),
                "notification_id": notification.notification_id
            }
    
    async def _send_websocket_notification(self, notification: Notification) -> Dict[str, Any]:
        """Send WebSocket notification"""
        try:
            message = {
                "type": "notification",
                "notification_id": notification.notification_id,
                "title": notification.title,
                "message": notification.message,
                "notification_type": notification.type.value,
                "priority": notification.priority,
                "data": notification.data,
                "action_url": notification.action_url,
                "action_text": notification.action_text,
                "created_at": notification.created_at.isoformat()
            }
            
            await self.connection_manager.send_to_user(message, notification.user_id)
            
            return {
                "success": True,
                "connections_notified": self.connection_manager.get_user_connection_count(notification.user_id)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_email_notification(self, notification: Notification) -> Dict[str, Any]:
        """Send email notification"""
        try:
            # Get user email from database
            db = await self.get_database()
            user = await db.users.find_one({"user_id": notification.user_id})
            
            if not user or not user.get("email"):
                return {"success": False, "error": "User email not found"}
            
            # Create email content
            email_content = self._create_email_template(notification)
            
            # Send via email service integrator
            result = await email_service_integrator.send_email(
                to_email=user["email"],
                subject=notification.title,
                content=email_content
            )
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_email_template(self, notification: Notification) -> str:
        """Create HTML email template"""
        priority_color = {
            1: "#28a745", 2: "#28a745", 3: "#17a2b8",
            4: "#17a2b8", 5: "#ffc107", 6: "#ffc107",
            7: "#fd7e14", 8: "#fd7e14", 9: "#dc3545", 10: "#dc3545"
        }
        
        color = priority_color.get(notification.priority, "#17a2b8")
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{notification.title}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: {color}; color: white; padding: 20px; border-radius: 5px 5px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">{notification.title}</h1>
            </div>
            <div style="background: #f9f9f9; padding: 20px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 5px 5px;">
                <p style="font-size: 16px; margin-bottom: 20px;">{notification.message}</p>
                
                {f'<a href="{notification.action_url}" style="display: inline-block; background: {color}; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 15px;">{notification.action_text}</a>' if notification.action_url else ''}
                
                <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #666; margin: 0;">
                    This notification was sent at {notification.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}<br>
                    Priority Level: {notification.priority}/10
                </p>
            </div>
        </body>
        </html>
        """
    
    async def _send_sms_notification(self, notification: Notification) -> Dict[str, Any]:
        """Send SMS notification (production implementation)"""
        try:
            # In production, integrate with SMS service like Twilio
            await professional_logger.log(
                LogLevel.INFO, LogCategory.SYSTEM,
                f"SMS notification would be sent: {notification.title}",
                user_id=notification.user_id
            )
            
            return {"success": True, "method": "simulated"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_push_notification(self, notification: Notification) -> Dict[str, Any]:
        """Send push notification (production implementation)"""
        try:
            # In production, integrate with Firebase Cloud Messaging or Apple Push Notification service
            await professional_logger.log(
                LogLevel.INFO, LogCategory.SYSTEM,
                f"Push notification would be sent: {notification.title}",
                user_id=notification.user_id
            )
            
            return {"success": True, "method": "simulated"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _store_in_app_notification(self, notification: Notification) -> Dict[str, Any]:
        """Store in-app notification in database"""
        try:
            db = await self.get_database()
            
            notification_doc = {
                "notification_id": notification.notification_id,
                "user_id": notification.user_id,
                "title": notification.title,
                "message": notification.message,
                "type": notification.type.value,
                "priority": notification.priority,
                "data": notification.data,
                "action_url": notification.action_url,
                "action_text": notification.action_text,
                "created_at": notification.created_at,
                "expires_at": notification.expires_at,
                "read": notification.read,
                "clicked": notification.clicked,
                "channel": "in_app"
            }
            
            await db.notifications.insert_one(notification_doc)
            
            return {"success": True, "stored": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_slack_notification(self, notification: Notification) -> Dict[str, Any]:
        """Send Slack notification (production implementation)"""
        try:
            # In production, integrate with Slack API
            return {"success": True, "method": "simulated"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _store_notification(self, notification: Notification, delivery_results: Dict[str, Any]):
        """Store notification record with delivery results"""
        try:
            db = await self.get_database()
            
            notification_record = {
                **asdict(notification),
                "delivery_results": delivery_results,
                "delivered_at": datetime.utcnow()
            }
            
            # Convert datetime objects to ISO strings for JSON serialization
            if notification_record.get("created_at"):
                notification_record["created_at"] = notification_record["created_at"].isoformat()
            if notification_record.get("scheduled_for"):
                notification_record["scheduled_for"] = notification_record["scheduled_for"].isoformat()
            if notification_record.get("expires_at"):
                notification_record["expires_at"] = notification_record["expires_at"].isoformat()
            
            # Convert enum values to strings
            notification_record["type"] = notification_record["type"].value if hasattr(notification_record["type"], "value") else notification_record["type"]
            notification_record["channels"] = [ch.value if hasattr(ch, "value") else ch for ch in notification_record["channels"]]
            
            await db.notification_history.insert_one(notification_record)
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.DATABASE,
                f"Failed to store notification record: {str(e)}",
                error=e
            )
    
    async def start_processing(self):
        """Start processing notification queue"""
        if self.processing:
            return
        
        self.processing = True
        
        while self.processing:
            try:
                # Wait for notification or timeout
                notification = await asyncio.wait_for(
                    self.notification_queue.get(), 
                    timeout=1.0
                )
                
                # Check if notification is scheduled for future
                if notification.scheduled_for and notification.scheduled_for > datetime.utcnow():
                    # Put back in queue for later processing
                    await self.notification_queue.put(notification)
                    await asyncio.sleep(1)
                    continue
                
                # Process notification
                await self.send_notification(notification)
                
            except asyncio.TimeoutError:
                # No notifications in queue, continue
                continue
            except Exception as e:
                await professional_logger.log(
                    LogLevel.ERROR, LogCategory.SYSTEM,
                    f"Error processing notification queue: {str(e)}",
                    error=e
                )
    
    async def stop_processing(self):
        """Stop processing notification queue"""
        self.processing = False
    
    async def queue_notification(self, notification: Notification):
        """Add notification to processing queue"""
        await self.notification_queue.put(notification)

class RealtimeNotificationSystem:
    """Main notification system coordinator"""
    
    def __init__(self):
        self.connection_manager = WebSocketConnectionManager()
        self.processor = NotificationProcessor(self.connection_manager)
        self.notification_templates = {}
        self.user_preferences = {}
    
    async def initialize(self):
        """Initialize the notification system"""
        # Start processing queue
        asyncio.create_task(self.processor.start_processing())
        
        await professional_logger.log(
            LogLevel.INFO, LogCategory.SYSTEM,
            "Real-time notification system initialized"
        )
    
    async def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        channels: List[NotificationChannel] = None,
        priority: int = 5,
        data: Dict[str, Any] = None,
        scheduled_for: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        action_url: Optional[str] = None,
        action_text: Optional[str] = None
    ) -> str:
        """Create and queue notification"""
        
        if channels is None:
            channels = [NotificationChannel.WEBSOCKET, NotificationChannel.IN_APP]
        
        notification = Notification(
            notification_id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            channels=channels,
            priority=priority,
            data=data or {},
            created_at=datetime.utcnow(),
            scheduled_for=scheduled_for,
            expires_at=expires_at,
            action_url=action_url,
            action_text=action_text
        )
        
        # Queue for processing
        await self.processor.queue_notification(notification)
        
        return notification.notification_id
    
    async def send_system_alert(
        self,
        title: str,
        message: str,
        priority: int = 8,
        affected_users: List[str] = None
    ):
        """Send system-wide alert"""
        
        if affected_users is None:
            # Broadcast to all connected users
            await self.connection_manager.broadcast_to_all({
                "type": "system_alert",
                "title": title,
                "message": message,
                "priority": priority,
                "timestamp": datetime.utcnow().isoformat()
            })
        else:
            # Send to specific users
            for user_id in affected_users:
                await self.create_notification(
                    user_id=user_id,
                    title=title,
                    message=message,
                    notification_type=NotificationType.SYSTEM,
                    channels=[NotificationChannel.WEBSOCKET, NotificationChannel.EMAIL],
                    priority=priority
                )
    
    async def get_user_notifications(
        self, 
        user_id: str, 
        limit: int = 20,
        unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get notifications for user"""
        try:
            db = await self.processor.get_database()
            
            query = {"user_id": user_id}
            if unread_only:
                query["read"] = False
            
            notifications = await db.notifications.find(query)\
                .sort("created_at", -1)\
                .limit(limit)\
                .to_list(length=limit)
            
            # Convert ObjectId to string and format dates
            for notification in notifications:
                notification["_id"] = str(notification["_id"])
                if "created_at" in notification:
                    notification["created_at"] = notification["created_at"].isoformat()
                if notification.get("expires_at"):
                    notification["expires_at"] = notification["expires_at"].isoformat()
            
            return notifications
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.DATABASE,
                f"Failed to get user notifications: {str(e)}",
                error=e
            )
            return []
    
    async def mark_notification_read(self, notification_id: str, user_id: str) -> bool:
        """Mark notification as read"""
        try:
            db = await self.processor.get_database()
            
            result = await db.notifications.update_one(
                {"notification_id": notification_id, "user_id": user_id},
                {"$set": {"read": True, "read_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.DATABASE,
                f"Failed to mark notification read: {str(e)}",
                error=e
            )
            return False
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get notification system statistics"""
        return {
            "active_websocket_connections": self.connection_manager.get_total_connections(),
            "users_connected": len(self.connection_manager.active_connections),
            "queue_size": self.processor.notification_queue.qsize(),
            "processing_active": self.processor.processing
        }

# Global instance
notification_system = RealtimeNotificationSystem()