"""
Customer Notification Service
Handles automated notifications for plan changes, admin actions, and system events
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from core.database import get_database
import uuid
import json

logger = logging.getLogger(__name__)

class CustomerNotificationService:
    def __init__(self):
        self.db = get_database()
        
        # Notification templates
        self.notification_templates = {
            "plan_change": {
                "subject": "Your subscription plan has been updated",
                "template": "Your subscription plan has been changed to {plan_name}. {additional_details}",
                "priority": "high",
                "channels": ["email", "in_app"]
            },
            "admin_override": {
                "subject": "Account settings updated by admin",
                "template": "Your account settings have been updated by our admin team. {reason}",
                "priority": "medium",
                "channels": ["email", "in_app"]
            },
            "comp_account_granted": {
                "subject": "Complimentary access granted",
                "template": "You've been granted complimentary access to {features}. This access expires on {expires_at}.",
                "priority": "high",
                "channels": ["email", "in_app"]
            },
            "discount_applied": {
                "subject": "Discount applied to your account",
                "template": "A {discount_value}% discount has been applied to your subscription. {reason}",
                "priority": "medium",
                "channels": ["email", "in_app"]
            },
            "subscription_paused": {
                "subject": "Your subscription has been paused",
                "template": "Your subscription has been temporarily paused. {reason} Expected resume date: {expected_resume_date}",
                "priority": "high",
                "channels": ["email", "in_app"]
            },
            "subscription_resumed": {
                "subject": "Your subscription has been resumed",
                "template": "Your subscription has been resumed and is now active. Welcome back!",
                "priority": "high",
                "channels": ["email", "in_app"]
            },
            "payment_issue": {
                "subject": "Payment issue with your subscription",
                "template": "We encountered an issue processing your payment. Please update your payment method to continue your subscription.",
                "priority": "critical",
                "channels": ["email", "in_app", "sms"]
            },
            "subscription_expiring": {
                "subject": "Your subscription is expiring soon",
                "template": "Your subscription expires on {expiry_date}. Renew now to continue accessing your features.",
                "priority": "high",
                "channels": ["email", "in_app"]
            }
        }
        
        # Notification channels configuration
        self.notification_channels = {
            "email": {"enabled": True, "provider": "sendgrid"},
            "in_app": {"enabled": True, "provider": "internal"},
            "sms": {"enabled": False, "provider": "twilio"},  # Disabled by default
            "push": {"enabled": False, "provider": "firebase"}  # Disabled by default
        }

    async def health_check(self):
        """Health check for customer notification service"""
        try:
            collection = self.db.customer_notifications
            await collection.count_documents({})
            
            return {
                "success": True,
                "healthy": True,
                "service": "customer_notification",
                "timestamp": datetime.utcnow().isoformat(),
                "templates_available": len(self.notification_templates),
                "channels_configured": list(self.notification_channels.keys())
            }
        except Exception as e:
            logger.error(f"Customer notification service health check failed: {e}")
            return {
                "success": False,
                "healthy": False,
                "error": str(e)
            }

    async def send_notification(self, notification_type: str, workspace_id: str, 
                              template_data: Dict[str, Any], admin_user_id: str = None) -> Dict[str, Any]:
        """Send notification to customer"""
        try:
            # Get notification template
            template = self.notification_templates.get(notification_type)
            if not template:
                return {"success": False, "error": f"Unknown notification type: {notification_type}"}
            
            # Get workspace and user information
            workspace = await self.db.workspaces.find_one({"_id": workspace_id})
            if not workspace:
                return {"success": False, "error": f"Workspace {workspace_id} not found"}
            
            # Create notification record
            notification_record = {
                "_id": str(uuid.uuid4()),
                "notification_type": notification_type,
                "workspace_id": workspace_id,
                "recipient_email": workspace.get("owner_email"),
                "subject": template["subject"],
                "content": template["template"].format(**template_data),
                "priority": template["priority"],
                "channels": template["channels"],
                "template_data": template_data,
                "admin_user_id": admin_user_id,
                "created_at": datetime.utcnow(),
                "status": "pending",
                "delivery_attempts": 0,
                "delivery_status": {}
            }
            
            # Send through configured channels
            delivery_results = {}
            for channel in template["channels"]:
                if self.notification_channels.get(channel, {}).get("enabled", False):
                    result = await self._send_via_channel(channel, notification_record)
                    delivery_results[channel] = result
                else:
                    delivery_results[channel] = {"success": False, "reason": "Channel disabled"}
            
            # Update notification record with delivery results
            notification_record["delivery_status"] = delivery_results
            notification_record["status"] = "sent" if any(r.get("success") for r in delivery_results.values()) else "failed"
            notification_record["sent_at"] = datetime.utcnow()
            
            # Store notification record
            await self.db.customer_notifications.insert_one(notification_record)
            
            return {
                "success": True,
                "notification_id": notification_record["_id"],
                "notification_type": notification_type,
                "delivery_results": delivery_results,
                "status": notification_record["status"]
            }
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return {"success": False, "error": str(e)}

    async def send_bulk_notifications(self, notification_type: str, workspace_ids: List[str], 
                                    template_data: Dict[str, Any], admin_user_id: str = None) -> Dict[str, Any]:
        """Send notifications to multiple customers"""
        try:
            results = []
            successful = 0
            failed = 0
            
            for workspace_id in workspace_ids:
                result = await self.send_notification(notification_type, workspace_id, template_data, admin_user_id)
                results.append({
                    "workspace_id": workspace_id,
                    "success": result.get("success", False),
                    "notification_id": result.get("notification_id"),
                    "error": result.get("error")
                })
                
                if result.get("success"):
                    successful += 1
                else:
                    failed += 1
            
            # Create bulk notification record
            bulk_record = {
                "_id": str(uuid.uuid4()),
                "notification_type": notification_type,
                "workspace_count": len(workspace_ids),
                "successful_deliveries": successful,
                "failed_deliveries": failed,
                "template_data": template_data,
                "admin_user_id": admin_user_id,
                "created_at": datetime.utcnow(),
                "individual_results": results
            }
            
            await self.db.bulk_notifications.insert_one(bulk_record)
            
            return {
                "success": True,
                "bulk_notification_id": bulk_record["_id"],
                "summary": {
                    "total_sent": len(workspace_ids),
                    "successful": successful,
                    "failed": failed,
                    "success_rate": (successful / len(workspace_ids) * 100) if workspace_ids else 0
                },
                "individual_results": results
            }
            
        except Exception as e:
            logger.error(f"Error sending bulk notifications: {e}")
            return {"success": False, "error": str(e)}

    async def get_notification_history(self, workspace_id: str = None, notification_type: str = None, 
                                     days_back: int = 30, limit: int = 50) -> Dict[str, Any]:
        """Get notification history"""
        try:
            # Build query
            query = {"created_at": {"$gte": datetime.utcnow() - timedelta(days=days_back)}}
            if workspace_id:
                query["workspace_id"] = workspace_id
            if notification_type:
                query["notification_type"] = notification_type
            
            # Get notifications
            cursor = self.db.customer_notifications.find(query).sort("created_at", -1).limit(limit)
            notifications = await cursor.to_list(length=limit)
            
            # Enhance with workspace information
            enhanced_notifications = []
            for notification in notifications:
                workspace_info = await self._get_workspace_basic_info(notification.get("workspace_id"))
                notification["workspace_info"] = workspace_info
                enhanced_notifications.append(notification)
            
            return {
                "success": True,
                "notification_history": enhanced_notifications,
                "filter_criteria": {
                    "workspace_id": workspace_id,
                    "notification_type": notification_type,
                    "days_back": days_back,
                    "limit": limit
                },
                "total_notifications": len(enhanced_notifications)
            }
            
        except Exception as e:
            logger.error(f"Error getting notification history: {e}")
            return {"success": False, "error": str(e)}

    async def get_notification_templates(self) -> Dict[str, Any]:
        """Get available notification templates"""
        try:
            return {
                "success": True,
                "templates": self.notification_templates,
                "total_templates": len(self.notification_templates)
            }
        except Exception as e:
            logger.error(f"Error getting notification templates: {e}")
            return {"success": False, "error": str(e)}

    async def update_notification_template(self, template_name: str, template_data: Dict[str, Any], 
                                         admin_user_id: str) -> Dict[str, Any]:
        """Update notification template"""
        try:
            if template_name not in self.notification_templates:
                return {"success": False, "error": f"Template {template_name} not found"}
            
            # Store original template for rollback
            original_template = self.notification_templates[template_name].copy()
            
            # Update template
            self.notification_templates[template_name].update(template_data)
            
            # Log template change
            template_change = {
                "_id": str(uuid.uuid4()),
                "template_name": template_name,
                "original_template": original_template,
                "updated_template": self.notification_templates[template_name],
                "admin_user_id": admin_user_id,
                "updated_at": datetime.utcnow()
            }
            
            await self.db.template_changes.insert_one(template_change)
            
            return {
                "success": True,
                "template_name": template_name,
                "updated_template": self.notification_templates[template_name],
                "change_id": template_change["_id"]
            }
            
        except Exception as e:
            logger.error(f"Error updating notification template: {e}")
            return {"success": False, "error": str(e)}

    async def get_notification_analytics(self, days_back: int = 30) -> Dict[str, Any]:
        """Get notification analytics and performance metrics"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Get notification statistics
            total_notifications = await self.db.customer_notifications.count_documents({
                "created_at": {"$gte": start_date}
            })
            
            successful_notifications = await self.db.customer_notifications.count_documents({
                "created_at": {"$gte": start_date},
                "status": "sent"
            })
            
            failed_notifications = await self.db.customer_notifications.count_documents({
                "created_at": {"$gte": start_date},
                "status": "failed"
            })
            
            # Get notifications by type
            pipeline = [
                {"$match": {"created_at": {"$gte": start_date}}},
                {"$group": {"_id": "$notification_type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            notifications_by_type = await self.db.customer_notifications.aggregate(pipeline).to_list(length=20)
            
            # Get channel performance
            channel_performance = {}
            for channel in self.notification_channels.keys():
                if self.notification_channels[channel]["enabled"]:
                    channel_success = await self.db.customer_notifications.count_documents({
                        "created_at": {"$gte": start_date},
                        f"delivery_status.{channel}.success": True
                    })
                    channel_total = await self.db.customer_notifications.count_documents({
                        "created_at": {"$gte": start_date},
                        f"delivery_status.{channel}": {"$exists": True}
                    })
                    
                    channel_performance[channel] = {
                        "total": channel_total,
                        "successful": channel_success,
                        "success_rate": (channel_success / channel_total * 100) if channel_total > 0 else 0
                    }
            
            return {
                "success": True,
                "analytics": {
                    "total_notifications": total_notifications,
                    "successful": successful_notifications,
                    "failed": failed_notifications,
                    "success_rate": (successful_notifications / total_notifications * 100) if total_notifications > 0 else 0,
                    "notifications_by_type": {item["_id"]: item["count"] for item in notifications_by_type},
                    "channel_performance": channel_performance
                },
                "period": {
                    "days_back": days_back,
                    "start_date": start_date.isoformat(),
                    "end_date": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting notification analytics: {e}")
            return {"success": False, "error": str(e)}

    async def schedule_notification(self, notification_type: str, workspace_id: str, 
                                  template_data: Dict[str, Any], send_at: datetime, 
                                  admin_user_id: str = None) -> Dict[str, Any]:
        """Schedule a notification to be sent at a specific time"""
        try:
            scheduled_notification = {
                "_id": str(uuid.uuid4()),
                "notification_type": notification_type,
                "workspace_id": workspace_id,
                "template_data": template_data,
                "admin_user_id": admin_user_id,
                "scheduled_at": send_at,
                "created_at": datetime.utcnow(),
                "status": "scheduled"
            }
            
            await self.db.scheduled_notifications.insert_one(scheduled_notification)
            
            return {
                "success": True,
                "scheduled_notification_id": scheduled_notification["_id"],
                "notification_type": notification_type,
                "workspace_id": workspace_id,
                "scheduled_for": send_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scheduling notification: {e}")
            return {"success": False, "error": str(e)}

    async def process_scheduled_notifications(self) -> Dict[str, Any]:
        """Process notifications that are scheduled to be sent now"""
        try:
            # Get notifications scheduled for now or earlier
            query = {
                "scheduled_at": {"$lte": datetime.utcnow()},
                "status": "scheduled"
            }
            
            scheduled_notifications = await self.db.scheduled_notifications.find(query).to_list(length=100)
            
            processed = 0
            successful = 0
            failed = 0
            
            for notification in scheduled_notifications:
                try:
                    # Send the notification
                    result = await self.send_notification(
                        notification["notification_type"],
                        notification["workspace_id"],
                        notification["template_data"],
                        notification.get("admin_user_id")
                    )
                    
                    # Update scheduled notification status
                    new_status = "sent" if result.get("success") else "failed"
                    await self.db.scheduled_notifications.update_one(
                        {"_id": notification["_id"]},
                        {
                            "$set": {
                                "status": new_status,
                                "processed_at": datetime.utcnow(),
                                "result": result
                            }
                        }
                    )
                    
                    processed += 1
                    if result.get("success"):
                        successful += 1
                    else:
                        failed += 1
                        
                except Exception as e:
                    logger.error(f"Error processing scheduled notification {notification['_id']}: {e}")
                    failed += 1
            
            return {
                "success": True,
                "processed_notifications": processed,
                "successful_sends": successful,
                "failed_sends": failed
            }
            
        except Exception as e:
            logger.error(f"Error processing scheduled notifications: {e}")
            return {"success": False, "error": str(e)}

    # Helper methods
    async def _send_via_channel(self, channel: str, notification_record: Dict) -> Dict[str, Any]:
        """Send notification via specific channel"""
        try:
            if channel == "email":
                return await self._send_email(notification_record)
            elif channel == "in_app":
                return await self._send_in_app(notification_record)
            elif channel == "sms":
                return await self._send_sms(notification_record)
            elif channel == "push":
                return await self._send_push(notification_record)
            else:
                return {"success": False, "reason": f"Unknown channel: {channel}"}
                
        except Exception as e:
            logger.error(f"Error sending via {channel}: {e}")
            return {"success": False, "reason": str(e)}

    async def _send_email(self, notification_record: Dict) -> Dict[str, Any]:
        """Send email notification (simplified implementation)"""
        try:
            # In production, this would integrate with SendGrid or similar
            logger.info(f"📧 EMAIL SENT: {notification_record['subject']} to {notification_record['recipient_email']}")
            
            return {
                "success": True,
                "channel": "email",
                "sent_at": datetime.utcnow().isoformat(),
                "provider": "sendgrid"
            }
            
        except Exception as e:
            return {"success": False, "reason": str(e)}

    async def _send_in_app(self, notification_record: Dict) -> Dict[str, Any]:
        """Send in-app notification"""
        try:
            # Store in-app notification in database
            in_app_notification = {
                "_id": str(uuid.uuid4()),
                "workspace_id": notification_record["workspace_id"],
                "title": notification_record["subject"],
                "message": notification_record["content"],
                "priority": notification_record["priority"],
                "read": False,
                "created_at": datetime.utcnow()
            }
            
            await self.db.in_app_notifications.insert_one(in_app_notification)
            
            return {
                "success": True,
                "channel": "in_app",
                "notification_id": in_app_notification["_id"],
                "sent_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "reason": str(e)}

    async def _send_sms(self, notification_record: Dict) -> Dict[str, Any]:
        """Send SMS notification (simplified implementation)"""
        try:
            # In production, this would integrate with Twilio or similar
            logger.info(f"📱 SMS SENT: {notification_record['content'][:50]}... to workspace {notification_record['workspace_id']}")
            
            return {
                "success": True,
                "channel": "sms",
                "sent_at": datetime.utcnow().isoformat(),
                "provider": "twilio"
            }
            
        except Exception as e:
            return {"success": False, "reason": str(e)}

    async def _send_push(self, notification_record: Dict) -> Dict[str, Any]:
        """Send push notification (simplified implementation)"""
        try:
            # In production, this would integrate with Firebase or similar
            logger.info(f"🔔 PUSH SENT: {notification_record['subject']} to workspace {notification_record['workspace_id']}")
            
            return {
                "success": True,
                "channel": "push",
                "sent_at": datetime.utcnow().isoformat(),
                "provider": "firebase"
            }
            
        except Exception as e:
            return {"success": False, "reason": str(e)}

    async def _get_workspace_basic_info(self, workspace_id: str) -> Dict:
        """Get basic workspace information"""
        try:
            workspace = await self.db.workspaces.find_one(
                {"_id": workspace_id}, 
                {"name": 1, "owner_email": 1, "created_at": 1}
            )
            return workspace or {"name": "Unknown", "owner_email": "Unknown"}
        except Exception:
            return {"name": "Unknown", "owner_email": "Unknown"}


# Service instance
_customer_notification_service = None

def get_customer_notification_service() -> CustomerNotificationService:
    """Get customer notification service instance"""
    global _customer_notification_service
    if _customer_notification_service is None:
        _customer_notification_service = CustomerNotificationService()
    return _customer_notification_service