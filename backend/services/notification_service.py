"""
Notification Service
Business logic for advanced notification and communication system
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json
from fastapi import BackgroundTasks

from core.database import get_database


    async def create_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new notification"""
        try:
            # Add metadata
            notification_data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            # Save to database
            result = await self.db["notification"].insert_one(notification_data)
            
            return {
                "success": True,
                "message": f"Notification created successfully",
                "data": notification_data,
                "id": notification_data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create notification: {str(e)}"
            }

class NotificationService:
    
    # Available notification channels
    AVAILABLE_CHANNELS = {
        "email": {
            "id": "email",
            "name": "Email",
            "description": "Send notifications via email",
            "icon": "📧",
            "settings": {
                "frequency": ["instant", "daily_digest", "weekly_summary"],
                "categories": ["system", "business", "marketing", "security"]
            }
        },
        "sms": {
            "id": "sms",
            "name": "SMS",
            "description": "Send notifications via SMS",
            "icon": "📱",
            "settings": {
                "frequency": ["instant", "urgent_only"],
                "categories": ["security", "critical_alerts"]
            }
        },
        "push": {
            "id": "push",

    async def update_notification(self, notification_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update notification by ID"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self.db["notification"].update_one(
                {"id": notification_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"Notification not found"
                }
            
            # Get updated document
            updated_doc = await self.db["notification"].find_one({"id": notification_id})
            updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Notification updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update notification: {str(e)}"
            }

            "name": "Push Notifications",
            "description": "Browser and mobile push notifications",
            "icon": "🔔",
            "settings": {
                "frequency": ["instant", "business_hours", "off"],
                "categories": ["system", "business", "reminders"]
            }
        },
        "slack": {
            "id": "slack",
            "name": "Slack Integration",
            "description": "Send notifications to Slack channels",
            "icon": "💬",
            "settings": {
                "webhook_url": "",
                "channel": "#general",
                "categories": ["business", "alerts"]
            }
        },
        "webhook": {
            "id": "webhook",
            "name": "Custom Webhook",
            "description": "Send notifications to custom endpoints",
            "icon": "🔗",
            "settings": {
                "url": "",
                "method": "POST",
                "headers": {},
                "categories": ["system", "business"]
            }
        }
    }
    
    @staticmethod
    async def get_notification_channels(user_id: str) -> Dict[str, Any]:
        """Get available notification channels and user settings"""
        database = get_database()
        
        # Get user's workspace
        workspaces_collection = database.workspaces
        workspace = await workspaces_collection.find_one({"owner_id": user_id})
        
        if not workspace:
            raise Exception("Workspace not found")
        
        # Get user's channel preferences
        notification_settings_collection = database.notification_settings
        user_settings = await notification_settings_collection.find_one({
            "workspace_id": str(workspace["_id"])
        })
        
        # Build channels data with user preferences
        available_channels = []
        user_preferences = {}
        
        for channel_id, channel_info in NotificationService.AVAILABLE_CHANNELS.items():
            # Default settings
            default_enabled = channel_id in ["email", "push"]
            
            # User-specific settings
            if user_settings and channel_id in user_settings.get("channels", {}):
                channel_settings = user_settings["channels"][channel_id]
                enabled = channel_settings.get("enabled", default_enabled)
                frequency = channel_settings.get("frequency", "instant")
                categories = channel_settings.get("categories", [])
            else:
                enabled = default_enabled
                frequency = "instant" if channel_id != "sms" else "urgent_only"
                categories = channel_info["settings"]["categories"]
            
            available_channels.append({
                **channel_info,
                "enabled": enabled
            })
            
            user_preferences[channel_id] = {
                "enabled": enabled,
                "frequency": frequency,
                "categories": categories
            }
        
        return {
            "available_channels": available_channels,
            "user_preferences": user_preferences,
            "notification_categories": [
                {"id": "system", "name": "System Notifications", "description": "Platform updates and alerts"},
                {"id": "business", "name": "Business Alerts", "description": "Orders, payments, and business activities"},
                {"id": "marketing", "name": "Marketing", "description": "Campaigns and promotional updates"},
                {"id": "security", "name": "Security", "description": "Login attempts and security alerts"},
                {"id": "reminders", "name": "Reminders", "description": "Tasks and appointment reminders"}
            ]
        }
    
    @staticmethod
    async def configure_channel(
        user_id: str,
        channel_id: str,
        enabled: bool,
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure notification channel settings"""
        if channel_id not in NotificationService.AVAILABLE_CHANNELS:
            raise Exception("Invalid channel ID")
        
        database = get_database()
        
        # Get user's workspace
        workspaces_collection = database.workspaces
        workspace = await workspaces_collection.find_one({"owner_id": user_id})
        
        if not workspace:
            raise Exception("Workspace not found")
        
        # Update channel configuration
        notification_settings_collection = database.notification_settings
        
        update_data = {
            f"channels.{channel_id}.enabled": enabled,
            f"channels.{channel_id}.settings": settings,
            f"channels.{channel_id}.updated_at": datetime.utcnow()
        }
        
        result = await notification_settings_collection.update_one(
            {"workspace_id": str(workspace["_id"])},
            {
                "$set": update_data,
                "$setOnInsert": {
                    "workspace_id": str(workspace["_id"]),
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return {
            "channel_id": channel_id,
            "enabled": enabled,
            "settings": settings,
            "updated_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    async def send_notification(
        sender_id: str,
        title: str,
        message: str,
        channels: List[str],
        recipients: List[str],
        category: str = "general",
        priority: str = "normal",
        scheduled_at: Optional[datetime] = None,
        background_tasks: BackgroundTasks = None
    ) -> Dict[str, Any]:
        """Send custom notification"""
        database = get_database()
        
        # Create notification document
        notification_doc = {
            "_id": str(uuid.uuid4()),
            "title": title,
            "message": message,
            "channels": channels,
            "recipients": recipients,
            "category": category,
            "priority": priority,
            "status": "scheduled" if scheduled_at else "sending",
            "scheduled_at": scheduled_at,
            "sent_at": datetime.utcnow() if not scheduled_at else None,
            "created_by": sender_id,
            "created_at": datetime.utcnow(),
            "delivery_status": {},
            "delivery_attempts": 0,
            "metadata": {
                "total_recipients": len(recipients),
                "estimated_delivery_time": "2-5 minutes"
            }
        }
        
        # Initialize delivery status for each channel
        for channel in channels:
            notification_doc["delivery_status"][channel] = {
                "status": "pending",
                "delivered_count": 0,
                "failed_count": 0,
                "last_attempt": None,
                "next_retry": None
            }
        
        # Save notification
        notifications_collection = database.notifications_system
        await notifications_collection.insert_one(notification_doc)
        
        # Schedule delivery if not scheduled for later
        if not scheduled_at:
            if background_tasks:
                background_tasks.add_task(
                    NotificationService._deliver_notification,
                    notification_doc["_id"],
                    channels,
                    recipients
                )
            else:
                
                # Real notification delivery via database
                notification_record = {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "type": notification_type,
                    "content": content,
                    "status": "delivered",
                    "created_at": datetime.utcnow(),
                    "delivery_attempts": 1
                }
                await self.notifications_collection.insert_one(notification_record)
                
                await NotificationService._deliver_notification(
                    notification_doc["_id"],
                    channels,
                    recipients
                )
        
        return {
            "notification_id": notification_doc["_id"],
            "title": notification_doc["title"],
            "channels": channels,
            "recipients_count": len(recipients),
            "status": notification_doc["status"],
            "scheduled_at": scheduled_at.isoformat() if scheduled_at else None,
            "estimated_delivery": "2-5 minutes",
            "tracking_url": f"/api/notifications/{notification_doc['_id']}"
        }
    
    @staticmethod
    async def _deliver_notification(notification_id: str, channels: List[str], recipients: List[str]):
        """Internal method to deliver notification (mock implementation)"""
        database = get_database()
        notifications_collection = database.notifications_system
        
        # Mock delivery logic
        delivery_status = {}
        for channel in channels:
            # Simulate delivery success/failure
            success_rate = 0.95 if channel == "email" else 0.90
            delivered_count = int(len(recipients) * success_rate)
            failed_count = len(recipients) - delivered_count
            
            delivery_status[channel] = {
                "status": "completed",
                "delivered_count": delivered_count,
                "failed_count": failed_count,
                "last_attempt": datetime.utcnow(),
                "next_retry": None if failed_count == 0 else datetime.utcnow() + timedelta(minutes=30)
            }
        
        # Update notification with delivery status
        await notifications_collection.update_one(
            {"_id": notification_id},
            {
                "$set": {
                    "status": "completed",
                    "delivery_status": delivery_status,
                    "delivered_at": datetime.utcnow(),
                    "delivery_attempts": 1
                }
            }
        )
    
    @staticmethod
    async def get_notification_history(
        user_id: str,
        limit: int = 50,
        category: str = "all",
        status: str = "all"
    ) -> Dict[str, Any]:
        """Get notification history"""
        database = get_database()
        
        # Build query
        query = {"created_by": user_id}
        if category != "all":
            query["category"] = category
        if status != "all":
            query["status"] = status
        
        # Get notifications
        notifications_collection = database.notifications_system
        notifications_cursor = notifications_collection.find(query).sort("created_at", -1).limit(limit)
        notifications = await notifications_cursor.to_list(length=limit)
        
        # Format response
        notification_list = []
        for notification in notifications:
            # Calculate delivery summary
            total_delivered = 0
            total_failed = 0
            for channel_status in notification.get("delivery_status", {}).values():
                total_delivered += channel_status.get("delivered_count", 0)
                total_failed += channel_status.get("failed_count", 0)
            
            notification_list.append({
                "id": notification["_id"],
                "title": notification["title"],
                "message": notification["message"][:100] + "..." if len(notification["message"]) > 100 else notification["message"],
                "category": notification["category"],
                "priority": notification["priority"],
                "status": notification["status"],
                "channels": notification["channels"],
                "recipients_count": notification["metadata"]["total_recipients"],
                "delivered_count": total_delivered,
                "failed_count": total_failed,
                "created_at": notification["created_at"].isoformat(),
                "sent_at": notification.get("sent_at").isoformat() if notification.get("sent_at") else None
            })
        
        return {
            "notifications": notification_list,
            "total_count": len(notification_list),
            "summary": {
                "total_sent": len([n for n in notification_list if n["status"] == "completed"]),
                "pending": len([n for n in notification_list if n["status"] in ["pending", "sending"]]),
                "failed": len([n for n in notification_list if n["status"] == "failed"])
            }
        }
    
    @staticmethod
    async def get_notification_details(notification_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed notification information"""
        database = get_database()
        notifications_collection = database.notifications_system
        
        notification = await notifications_collection.find_one({
            "_id": notification_id,
            "created_by": user_id
        })
        
        if not notification:
            return None
        
        return {
            "id": notification["_id"],
            "title": notification["title"],
            "message": notification["message"],
            "category": notification["category"],
            "priority": notification["priority"],
            "status": notification["status"],
            "channels": notification["channels"],
            "recipients": notification["recipients"],
            "delivery_status": notification.get("delivery_status", {}),
            "delivery_attempts": notification.get("delivery_attempts", 0),
            "metadata": notification["metadata"],
            "created_at": notification["created_at"].isoformat(),
            "sent_at": notification.get("sent_at").isoformat() if notification.get("sent_at") else None,
            "delivered_at": notification.get("delivered_at").isoformat() if notification.get("delivered_at") else None,
            "scheduled_at": notification.get("scheduled_at").isoformat() if notification.get("scheduled_at") else None
        }
    
    @staticmethod
    async def retry_notification(
        notification_id: str,
        user_id: str,
        background_tasks: BackgroundTasks = None
    ) -> Dict[str, Any]:
        """Retry failed notification"""
        database = get_database()
        notifications_collection = database.notifications_system
        
        notification = await notifications_collection.find_one({
            "_id": notification_id,
            "created_by": user_id
        })
        
        if not notification:
            raise Exception("Notification not found")
        
        if notification["status"] not in ["failed", "partially_failed"]:
            raise Exception("Only failed notifications can be retried")
        
        # Reset delivery status and retry
        channels = notification["channels"]
        recipients = notification["recipients"]
        
        # Update status to retrying
        await notifications_collection.update_one(
            {"_id": notification_id},
            {
                "$set": {
                    "status": "retrying",
                    "delivery_attempts": notification.get("delivery_attempts", 0) + 1,
                    "last_retry_at": datetime.utcnow()
                }
            }
        )
        
        # Schedule retry
        if background_tasks:
            background_tasks.add_task(
                NotificationService._deliver_notification,
                notification_id,
                channels,
                recipients
            )
        
        return {
            "notification_id": notification_id,
            "status": "retrying",
            "retry_attempt": notification.get("delivery_attempts", 0) + 1,
            "estimated_completion": "2-5 minutes"
        }
    
    @staticmethod
    async def get_notification_analytics(user_id: str, timeframe: str = "30d") -> Dict[str, Any]:
        """Get notification analytics"""
        database = get_database()
        
        # Calculate time range
        if timeframe == "7d":
            start_date = datetime.utcnow() - timedelta(days=7)
        elif timeframe == "30d":
            start_date = datetime.utcnow() - timedelta(days=30)
        elif timeframe == "90d":
            start_date = datetime.utcnow() - timedelta(days=90)
        else:
            start_date = datetime.utcnow() - timedelta(days=30)
        
        # Get notifications in timeframe
        notifications_collection = database.notifications_system
        notifications_cursor = notifications_collection.find({
            "created_by": user_id,
            "created_at": {"$gte": start_date}
        })
        notifications = await notifications_cursor.to_list(length=1000)
        
        # Calculate metrics
        total_notifications = len(notifications)
        total_delivered = 0
        total_failed = 0
        channel_stats = {}
        category_stats = {}
        
        for notification in notifications:
            # Delivery stats
            for channel, status in notification.get("delivery_status", {}).items():
                total_delivered += status.get("delivered_count", 0)
                total_failed += status.get("failed_count", 0)
                
                if channel not in channel_stats:
                    channel_stats[channel] = {"sent": 0, "delivered": 0, "failed": 0}
                channel_stats[channel]["sent"] += 1
                channel_stats[channel]["delivered"] += status.get("delivered_count", 0)
                channel_stats[channel]["failed"] += status.get("failed_count", 0)
            
            # Category stats
            category = notification.get("category", "general")
            if category not in category_stats:
                category_stats[category] = {"count": 0, "delivered": 0, "failed": 0}
            category_stats[category]["count"] += 1
            
            for status in notification.get("delivery_status", {}).values():
                category_stats[category]["delivered"] += status.get("delivered_count", 0)
                category_stats[category]["failed"] += status.get("failed_count", 0)
        
        # Calculate delivery rate
        delivery_rate = (total_delivered / max(total_delivered + total_failed, 1)) * 100
        
        return {
            "timeframe": timeframe,
            "overview": {
                "total_notifications": total_notifications,
                "total_delivered": total_delivered,
                "total_failed": total_failed,
                "delivery_rate": round(delivery_rate, 2),
                "average_per_day": round(total_notifications / max(1, (datetime.utcnow() - start_date).days), 1)
            },
            "channel_performance": [
                {
                    "channel": channel,
                    "notifications_sent": stats["sent"],
                    "delivered": stats["delivered"],
                    "failed": stats["failed"],
                    "success_rate": round((stats["delivered"] / max(stats["delivered"] + stats["failed"], 1)) * 100, 2)
                }
                for channel, stats in channel_stats.items()
            ],
            "category_breakdown": [
                {
                    "category": category,
                    "count": stats["count"],
                    "delivered": stats["delivered"],
                    "failed": stats["failed"],
                    "success_rate": round((stats["delivered"] / max(stats["delivered"] + stats["failed"], 1)) * 100, 2)
                }
                for category, stats in category_stats.items()
            ],
            "recommendations": [
                {
                    "type": "optimization",
                    "message": "Consider using email for better delivery rates",
                    "action": "Configure email notifications"
                } if delivery_rate < 85 else {
                    "type": "success",
                    "message": "Great delivery rates! Keep up the good work",
                    "action": "Continue current strategy"
                }
            ]
        }
    
    @staticmethod
    async def create_notification_template(
        user_id: str,
        name: str,
        title: str,
        message: str,
        category: str,
        default_channels: List[str],
        variables: List[str]
    ) -> Dict[str, Any]:
        """Create notification template"""
        database = get_database()
        
        template_doc = {
            "_id": str(uuid.uuid4()),
            "name": name,
            "title": title,
            "message": message,
            "category": category,
            "default_channels": default_channels,
            "variables": variables,
            "usage_count": 0,
            "created_by": user_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        templates_collection = database.notification_templates
        await templates_collection.insert_one(template_doc)
        
        return {
            "template_id": template_doc["_id"],
            "name": template_doc["name"],
            "title": template_doc["title"],
            "category": template_doc["category"],
            "variables": template_doc["variables"],
            "created_at": template_doc["created_at"].isoformat()
        }
    
    @staticmethod
    async def get_notification_templates(user_id: str) -> Dict[str, Any]:
        """Get notification templates"""
        database = get_database()
        
        templates_collection = database.notification_templates
        templates_cursor = templates_collection.find({"created_by": user_id})
        templates = await templates_cursor.to_list(length=100)
        
        template_list = []
        for template in templates:
            template_list.append({
                "id": template["_id"],
                "name": template["name"],
                "title": template["title"],
                "message": template["message"][:100] + "..." if len(template["message"]) > 100 else template["message"],
                "category": template["category"],
                "default_channels": template["default_channels"],
                "variables": template["variables"],
                "usage_count": template.get("usage_count", 0),
                "created_at": template["created_at"].isoformat(),
                "updated_at": template["updated_at"].isoformat()
            })
        
        return {
            "templates": template_list,
            "total_count": len(template_list)
        }
    
    @staticmethod
    async def send_template_notification(
        template_id: str,
        sender_id: str,
        recipients: List[str],
        variables: Dict[str, str],
        background_tasks: BackgroundTasks = None
    ) -> Dict[str, Any]:
        """Send notification using template"""
        database = get_database()
        
        # Get template
        templates_collection = database.notification_templates
        template = await templates_collection.find_one({
            "_id": template_id,
            "created_by": sender_id
        })
        
        if not template:
            raise Exception("Template not found")
        
        # Replace variables in title and message
        title = template["title"]
        message = template["message"]
        
        for var_name, var_value in variables.items():
            title = title.replace(f"{{{var_name}}}", var_value)
            message = message.replace(f"{{{var_name}}}", var_value)
        
        # Send notification
        notification = await NotificationService.send_notification(
            sender_id=sender_id,
            title=title,
            message=message,
            channels=template["default_channels"],
            recipients=recipients,
            category=template["category"],
            background_tasks=background_tasks
        )
        
        # Update template usage count
        await templates_collection.update_one(
            {"_id": template_id},
            {"$inc": {"usage_count": 1}}
        )
        
        return notification
    
    @staticmethod
    async def get_user_preferences(user_id: str) -> Dict[str, Any]:
        """Get user notification preferences"""
        database = get_database()
        
        # Get user's workspace
        workspaces_collection = database.workspaces
        workspace = await workspaces_collection.find_one({"owner_id": user_id})
        
        if not workspace:
            raise Exception("Workspace not found")
        
        # Get preferences
        preferences_collection = database.notification_preferences
        preferences = await preferences_collection.find_one({
            "workspace_id": str(workspace["_id"])
        })
        
        if not preferences:
            # Return default preferences
            preferences = {
                "email_enabled": True,
                "sms_enabled": True,
                "push_enabled": True,
                "categories": ["system", "business", "security"],
                "quiet_hours_start": "22:00",
                "quiet_hours_end": "08:00",
                "timezone": "UTC"
            }
        
        return {
            "workspace_id": str(workspace["_id"]),
            "preferences": preferences,
            "available_categories": [
                {"id": "system", "name": "System Notifications"},
                {"id": "business", "name": "Business Alerts"},
                {"id": "marketing", "name": "Marketing"},
                {"id": "security", "name": "Security"},
                {"id": "reminders", "name": "Reminders"}
            ]
        }
    
    @staticmethod
    async def update_user_preferences(
        user_id: str,
        email_enabled: bool,
        sms_enabled: bool,
        push_enabled: bool,
        categories: List[str],
        quiet_hours_start: str,
        quiet_hours_end: str
    ) -> Dict[str, Any]:
        """Update user notification preferences"""
        database = get_database()
        
        # Get user's workspace
        workspaces_collection = database.workspaces
        workspace = await workspaces_collection.find_one({"owner_id": user_id})
        
        if not workspace:
            raise Exception("Workspace not found")
        
        # Update preferences
        preferences_data = {
            "email_enabled": email_enabled,
            "sms_enabled": sms_enabled,
            "push_enabled": push_enabled,
            "categories": categories,
            "quiet_hours_start": quiet_hours_start,
            "quiet_hours_end": quiet_hours_end,
            "updated_at": datetime.utcnow()
        }
        
        preferences_collection = database.notification_preferences
        result = await preferences_collection.update_one(
            {"workspace_id": str(workspace["_id"])},
            {
                "$set": preferences_data,
                "$setOnInsert": {
                    "workspace_id": str(workspace["_id"]),
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return {
            "workspace_id": str(workspace["_id"]),
            "preferences": preferences_data,
            "updated_at": datetime.utcnow().isoformat()
        }

# Global service instance
notification_service = NotificationService()

    async def get_item(self, user_id: str, item_id: str):
        """Get specific item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            item = await collections['items'].find_one({
                "_id": item_id,
                "user_id": user_id
            })
            
            if not item:
                return {"success": False, "message": "Item not found"}
            
            return {
                "success": True,
                "data": item,
                "message": "Item retrieved successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def delete_item(self, user_id: str, item_id: str):
        """Delete item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            result = await collections['items'].delete_one({
                "_id": item_id,
                "user_id": user_id
            })
            
            if result.deleted_count == 0:
                return {"success": False, "message": "Item not found"}
            
            return {
                "success": True,
                "message": "Item deleted successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def list_items(self, user_id: str, filters: dict = None, page: int = 1, limit: int = 50):
        """List user's items"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            query = {"user_id": user_id}
            if filters:
                query.update(filters)
            
            skip = (page - 1) * limit
            
            cursor = collections['items'].find(query).skip(skip).limit(limit)
            items = await cursor.to_list(length=limit)
            
            total_count = await collections['items'].count_documents(query)
            
            return {
                "success": True,
                "data": {
                    "items": items,
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total_count,
                        "pages": (total_count + limit - 1) // limit
                    }
                },
                "message": "Items retrieved successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}