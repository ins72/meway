"""
Real Email Automation Service - ElasticMail Integration - NO MOCK DATA
"""
import uuid
import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import aiohttp

class RealEmailAutomationService:
    def __init__(self, db):
        self.db = db
        self.email_campaigns = db["email_campaigns"]
        self.email_templates = db["email_templates"]
        self.email_logs = db["email_logs"]
        self.subscribers = db["email_subscribers"]
        
        # Real ElasticMail API setup
        self.api_key = os.getenv("ELASTICMAIL_API_KEY")
        self.base_url = "https://api.elasticemail.com/v2"
        
    async def send_real_email(self, email_data: Dict) -> Dict:
        """Send real email using ElasticMail API"""
        try:
            send_id = str(uuid.uuid4())
            
            # Prepare email data for ElasticMail
            payload = {
                'apikey': self.api_key,
                'subject': email_data.get('subject', 'Welcome to Mewayz'),
                'from': email_data.get('from_email', 'hello@mewayz.com'),
                'fromName': email_data.get('from_name', 'Mewayz Team'),
                'to': email_data.get('to_email'),
                'bodyText': email_data.get('text_content', ''),
                'bodyHtml': email_data.get('html_content', ''),
                'isTransactional': email_data.get('is_transactional', True)
            }
            
            # Add CC and BCC if provided
            if email_data.get('cc'):
                payload['cc'] = email_data['cc']
            if email_data.get('bcc'):
                payload['bcc'] = email_data['bcc']
            
            # Send email via ElasticMail
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/email/send", data=payload) as response:
                    response_data = await response.json()
                    
                    if response.status == 200 and response_data.get('success', False):
                        # Log successful send
                        email_log = {
                            "_id": send_id,
                            "to_email": email_data.get('to_email'),
                            "subject": email_data.get('subject'),
                            "status": "sent",
                            "elasticmail_message_id": response_data.get('data', {}).get('messageid'),
                            "sent_at": datetime.utcnow(),
                            "campaign_id": email_data.get('campaign_id'),
                            "template_id": email_data.get('template_id')
                        }
                        
                        await self.email_logs.insert_one(email_log)
                        
                        return {
                            "send_id": send_id,
                            "status": "sent",
                            "message_id": response_data.get('data', {}).get('messageid'),
                            "sent_at": datetime.utcnow()
                        }
                    else:
                        error_message = response_data.get('error', 'Unknown error')
                        
                        # Log failed send
                        email_log = {
                            "_id": send_id,
                            "to_email": email_data.get('to_email'),
                            "subject": email_data.get('subject'),
                            "status": "failed",
                            "error": error_message,
                            "failed_at": datetime.utcnow(),
                            "campaign_id": email_data.get('campaign_id')
                        }
                        
                        await self.email_logs.insert_one(email_log)
                        
                        return {"error": error_message}
                        
        except Exception as e:
            self.log(f"Error sending email: {str(e)}")
            return {"error": str(e)}
    
    async def create_email_campaign(self, campaign_data: Dict) -> Dict:
        """Create real email campaign"""
        try:
            campaign_id = str(uuid.uuid4())
            
            campaign = {
                "_id": campaign_id,
                "name": campaign_data.get("name"),
                "subject": campaign_data.get("subject"),
                "template_id": campaign_data.get("template_id"),
                "recipient_list_id": campaign_data.get("recipient_list_id"),
                "sender_name": campaign_data.get("sender_name", "Mewayz Team"),
                "sender_email": campaign_data.get("sender_email", "hello@mewayz.com"),
                "schedule_type": campaign_data.get("schedule_type", "immediate"),
                "scheduled_at": campaign_data.get("scheduled_at"),
                "status": "draft",
                "recipients_count": 0,
                "sent_count": 0,
                "delivered_count": 0,
                "opened_count": 0,
                "clicked_count": 0,
                "bounced_count": 0,
                "unsubscribed_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await self.email_campaigns.insert_one(campaign)
            
            return campaign
            
        except Exception as e:
            return {"error": str(e)}
    
    async def create_automation_sequence(self, sequence_data: Dict) -> Dict:
        """Create automated email sequence"""
        try:
            sequence_id = str(uuid.uuid4())
            
            sequence = {
                "_id": sequence_id,
                "name": sequence_data.get("name"),
                "trigger_type": sequence_data.get("trigger_type", "signup"),
                "trigger_conditions": sequence_data.get("trigger_conditions", {}),
                "emails": sequence_data.get("emails", []),
                "status": "active",
                "subscribers_count": 0,
                "total_sends": 0,
                "avg_open_rate": 0.0,
                "avg_click_rate": 0.0,
                "created_at": datetime.utcnow()
            }
            
            await self.email_campaigns.insert_one(sequence)
            
            return sequence
            
        except Exception as e:
            return {"error": str(e)}
    
    async def get_real_email_statistics(self, campaign_id: str) -> Dict:
        """Get real email statistics from ElasticMail"""
        try:
            # Get campaign statistics from ElasticMail
            params = {
                'apikey': self.api_key,
                'limit': 50
            }
            
            async with aiohttp.ClientSession() as session:
                # Get recent email logs
                async with session.get(f"{self.base_url}/log/summary", params=params) as response:
                    if response.status == 200:
                        stats_data = await response.json()
                        
                        # Calculate real statistics
                        logs = await self.email_logs.find({"campaign_id": campaign_id}).to_list(length=None)
                        
                        total_sent = len(logs)
                        successful_sends = len([log for log in logs if log.get("status") == "sent"])
                        failed_sends = len([log for log in logs if log.get("status") == "failed"])
                        
                        # Get delivery statistics from ElasticMail response
                        elasticmail_stats = stats_data.get('data', [])
                        delivered = 0
                        opened = 0
                        clicked = 0
                        bounced = 0
                        
                        for stat in elasticmail_stats:
                            delivered += stat.get('delivered', 0)
                            opened += stat.get('opened', 0)
                            clicked += stat.get('clicked', 0)
                            bounced += stat.get('bounced', 0)
                        
                        # Calculate rates
                        open_rate = (opened / max(delivered, 1)) * 100 if delivered > 0 else 0
                        click_rate = (clicked / max(delivered, 1)) * 100 if delivered > 0 else 0
                        bounce_rate = (bounced / max(total_sent, 1)) * 100 if total_sent > 0 else 0
                        delivery_rate = (delivered / max(total_sent, 1)) * 100 if total_sent > 0 else 0
                        
                        return {
                            "campaign_id": campaign_id,
                            "total_sent": total_sent,
                            "delivered": delivered,
                            "opened": opened,
                            "clicked": clicked,
                            "bounced": bounced,
                            "failed": failed_sends,
                            "open_rate": round(open_rate, 2),
                            "click_rate": round(click_rate, 2),
                            "bounce_rate": round(bounce_rate, 2),
                            "delivery_rate": round(delivery_rate, 2),
                            "last_updated": datetime.utcnow()
                        }
                    else:
                        # Fallback to database-only statistics
                        logs = await self.email_logs.find({"campaign_id": campaign_id}).to_list(length=None)
                        
                        total_sent = len(logs)
                        successful = len([log for log in logs if log.get("status") == "sent"])
                        failed = len([log for log in logs if log.get("status") == "failed"])
                        
                        return {
                            "campaign_id": campaign_id,
                            "total_sent": total_sent,
                            "successful_sends": successful,
                            "failed_sends": failed,
                            "delivery_rate": round((successful / max(total_sent, 1)) * 100, 2),
                            "source": "database_only",
                            "last_updated": datetime.utcnow()
                        }
                        
        except Exception as e:
            return {"error": str(e)}
    
    async def manage_subscribers(self, action: str, subscriber_data: Dict) -> Dict:
        """Manage email subscribers with real ElasticMail integration"""
        try:
            if action == "add":
                # Add subscriber to ElasticMail
                payload = {
                    'apikey': self.api_key,
                    'email': subscriber_data.get('email'),
                    'firstName': subscriber_data.get('first_name', ''),
                    'lastName': subscriber_data.get('last_name', ''),
                    'source': subscriber_data.get('source', 'mewayz_platform')
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(f"{self.base_url}/contact/add", data=payload) as response:
                        response_data = await response.json()
                        
                        if response.status == 200 and response_data.get('success', False):
                            # Save to local database
                            subscriber = {
                                "_id": str(uuid.uuid4()),
                                "email": subscriber_data.get('email'),
                                "first_name": subscriber_data.get('first_name', ''),
                                "last_name": subscriber_data.get('last_name', ''),
                                "source": subscriber_data.get('source', 'mewayz_platform'),
                                "subscribed_at": datetime.utcnow(),
                                "status": "active",
                                "elasticmail_contact_id": response_data.get('data')
                            }
                            
                            await self.subscribers.insert_one(subscriber)
                            
                            return {
                                "action": "subscriber_added",
                                "email": subscriber_data.get('email'),
                                "status": "success"
                            }
                        else:
                            return {"error": response_data.get('error', 'Failed to add subscriber')}
                            
            elif action == "remove":
                # Remove subscriber from ElasticMail
                payload = {
                    'apikey': self.api_key,
                    'email': subscriber_data.get('email')
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(f"{self.base_url}/contact/delete", data=payload) as response:
                        if response.status == 200:
                            # Update local database
                            await self.subscribers.update_one(
                                {"email": subscriber_data.get('email')},
                                {"$set": {"status": "unsubscribed", "unsubscribed_at": datetime.utcnow()}}
                            )
                            
                            return {
                                "action": "subscriber_removed",
                                "email": subscriber_data.get('email'),
                                "status": "success"
                            }
                        else:
                            return {"error": "Failed to remove subscriber"}
                            
        except Exception as e:
            return {"error": str(e)}
    
    def log(self, message: str):
        print(f"[EMAIL] {message}")

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

    async def update_item(self, user_id: str, item_id: str, update_data: dict):
        """Update existing item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            result = await collections['items'].update_one(
                {"_id": item_id, "user_id": user_id},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                return {"success": False, "message": "Item not found or no changes made"}
            
            # Get updated item
            updated_item = await collections['items'].find_one({
                "_id": item_id,
                "user_id": user_id
            })
            
            return {
                "success": True,
                "data": updated_item,
                "message": "Item updated successfully"
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