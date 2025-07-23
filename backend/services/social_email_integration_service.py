"""
Social Email Integration Service

Provides business logic for social email integration functionality
including email campaign integration with social media platforms.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid
from core.database import get_collection

class SocialEmailIntegrationService:
    """Service class for social email integration operations"""
    
    def __init__(self):
        self.collection = get_collection("social_email_integrations")
        self.campaigns_collection = get_collection("social_email_campaigns")
        self.analytics_collection = get_collection("social_email_analytics")
    
    async def get_integrations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all social email integrations for a user"""
        try:
            integrations = []
            cursor = self.collection.find({"user_id": user_id, "is_active": True})
            async for integration in cursor:
                integration["_id"] = str(integration["_id"])
                integrations.append(integration)
            return integrations
        except Exception as e:
            print(f"Error getting integrations: {e}")
            return []
    
    async def create_integration(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new social email integration"""
        try:
            integration = {
                "integration_id": str(uuid.uuid4()),
                "user_id": user_id,
                "platform": data.get("platform"),
                "email_provider": data.get("email_provider"),
                "configuration": data.get("configuration", {}),
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await self.collection.insert_one(integration)
            integration["_id"] = str(result.inserted_id)
            
            return {
                "integration_id": integration["integration_id"],
                "status": "created",
                "platform": integration["platform"],
                "email_provider": integration["email_provider"]
            }
        except Exception as e:
            print(f"Error creating integration: {e}")
            return {"error": "Failed to create integration"}
    
    async def get_integration_details(self, integration_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific integration"""
        try:
            integration = await self.collection.find_one({"integration_id": integration_id})
            if integration:
                integration["_id"] = str(integration["_id"])
                return integration
            return {"error": "Integration not found"}
        except Exception as e:
            print(f"Error getting integration details: {e}")
            return {"error": "Failed to get integration details"}
    
    async def update_integration(self, integration_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing integration"""
        try:
            update_data = {
                **data,
                "updated_at": datetime.utcnow()
            }
            
            result = await self.collection.update_one(
                {"integration_id": integration_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return {"status": "updated", "integration_id": integration_id}
            return {"error": "Integration not found or no changes made"}
        except Exception as e:
            print(f"Error updating integration: {e}")
            return {"error": "Failed to update integration"}
    
    async def delete_integration(self, integration_id: str) -> Dict[str, Any]:
        """Delete an integration (soft delete)"""
        try:
            result = await self.collection.update_one(
                {"integration_id": integration_id},
                {"$set": {"is_active": False, "deleted_at": datetime.utcnow()}}
            )
            
            if result.modified_count > 0:
                return {"status": "deleted", "integration_id": integration_id}
            return {"error": "Integration not found"}
        except Exception as e:
            print(f"Error deleting integration: {e}")
            return {"error": "Failed to delete integration"}
    
    async def sync_campaigns(self, integration_id: str) -> Dict[str, Any]:
        """Sync email campaigns with social media platforms"""
        try:
            integration = await self.collection.find_one({"integration_id": integration_id})
            if not integration:
                return {"error": "Integration not found"}
            
            # Mock sync operation
            sync_result = {
                "integration_id": integration_id,
                "campaigns_synced": 15,
                "social_posts_created": 8,
                "emails_sent": 1250,
                "sync_status": "completed",
                "sync_time": datetime.utcnow().isoformat(),
                "platforms_updated": [integration.get("platform", "facebook")],
                "next_sync": (datetime.utcnow() + timedelta(hours=6)).isoformat()
            }
            
            # Store sync result
            await self.analytics_collection.insert_one({
                **sync_result,
                "created_at": datetime.utcnow()
            })
            
            return sync_result
        except Exception as e:
            print(f"Error syncing campaigns: {e}")
            return {"error": "Failed to sync campaigns"}
    
    async def get_campaign_performance(self, integration_id: str) -> Dict[str, Any]:
        """Get performance metrics for integrated campaigns"""
        try:
            # Mock performance data
            performance = {
                "integration_id": integration_id,
                "total_campaigns": 25,
                "active_campaigns": 12,
                "email_metrics": {
                    "emails_sent": 15500,
                    "emails_opened": 6820,
                    "emails_clicked": 2108,
                    "open_rate": 44.0,
                    "click_rate": 13.6,
                    "conversion_rate": 3.2
                },
                "social_metrics": {
                    "posts_created": 48,
                    "total_reach": 125000,
                    "total_engagement": 8950,
                    "engagement_rate": 7.16,
                    "shares": 1240,
                    "comments": 890
                },
                "integration_effectiveness": {
                    "cross_platform_conversions": 156,
                    "attribution_rate": 12.4,
                    "roi_improvement": 28.5,
                    "customer_journey_completion": 18.7
                },
                "period": "last_30_days",
                "last_updated": datetime.utcnow().isoformat()
            }
            
            return performance
        except Exception as e:
            print(f"Error getting campaign performance: {e}")
            return {"error": "Failed to get campaign performance"}
    
    async def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get available integration templates"""
        try:
            templates = [
                {
                    "template_id": "welcome_series",
                    "name": "Welcome Series Integration",
                    "description": "Automated welcome email series with social media follow-ups",
                    "platforms": ["facebook", "instagram", "twitter"],
                    "email_providers": ["mailchimp", "constant_contact", "sendgrid"],
                    "category": "onboarding"
                },
                {
                    "template_id": "product_launch",
                    "name": "Product Launch Campaign",
                    "description": "Coordinated product launch across email and social channels",
                    "platforms": ["facebook", "instagram", "twitter", "linkedin"],
                    "email_providers": ["mailchimp", "hubspot", "sendgrid"],
                    "category": "marketing"
                },
                {
                    "template_id": "seasonal_promotion",
                    "name": "Seasonal Promotion",
                    "description": "Holiday and seasonal promotional campaign integration",
                    "platforms": ["facebook", "instagram", "pinterest"],
                    "email_providers": ["mailchimp", "constant_contact"],
                    "category": "promotional"
                },
                {
                    "template_id": "customer_retention",
                    "name": "Customer Retention",
                    "description": "Re-engagement campaigns across email and social platforms",
                    "platforms": ["facebook", "instagram", "twitter"],
                    "email_providers": ["mailchimp", "sendgrid", "hubspot"],
                    "category": "retention"
                },
                {
                    "template_id": "event_promotion",
                    "name": "Event Promotion",
                    "description": "Event marketing integration with email and social media",
                    "platforms": ["facebook", "instagram", "twitter", "linkedin"],
                    "email_providers": ["mailchimp", "constant_contact", "sendgrid"],
                    "category": "events"
                }
            ]
            
            return templates
        except Exception as e:
            print(f"Error getting templates: {e}")
            return []

# Global service instance
social_email_integration_service = SocialEmailIntegrationService()

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