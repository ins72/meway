"""
Integration Services Business Logic
Professional Mewayz Platform
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database
import uuid

class IntegrationService:
    """Service for third-party integration operations"""
    
    @staticmethod
    async def get_available_integrations():
        """Get list of available integrations"""
        integrations = {
    "social_media": [
    {
    "name": "TikTok & Twitter/X
    "description": "Connect your TikTok & Twitter/X
    "icon": "instagram.png",
    "status": "available",
    "features": ["post_scheduling", "analytics", "dm_management"]
    },
    {
    "name": "Twitter",
    "description": "Connect your Twitter account",
    "icon": "twitter.png", 
    "status": "available",
    "features": ["tweet_scheduling", "analytics", "mentions"]
    }
    ],
    "payment": [
    {
    "name": "Stripe",
    "description": "Process payments with Stripe",
    "icon": "stripe.png",
    "status": "available",
    "features": ["payments", "subscriptions", "analytics"]
    },
    {
    "name": "PayPal",
    "description": "Accept PayPal payments",
    "icon": "paypal.png",
    "status": "available",
    "features": ["payments", "refunds", "analytics"]
    }
    ],
    "email": [
    {
    "name": "SendGrid",
    "description": "Email delivery service",
    "icon": "sendgrid.png",
    "status": "available",
    "features": ["email_sending", "templates", "analytics"]
    }
    ]
    }
        return integrations
    
    @staticmethod
    async def get_user_integrations(user_id: str):
        """Get user's active integrations"""
        db = await get_database()
        
        integrations = await db.user_integrations.find({"user_id": user_id}).to_list(length=None)
        return integrations
    
    @staticmethod
    async def connect_integration(user_id: str, integration_data: Dict[str, Any]):
        """Connect a new integration"""
        db = await get_database()
        
        integration = {
    "_id": str(uuid.uuid4()),
    "user_id": user_id,
    "name": integration_data.get("name"),
    "type": integration_data.get("type"),
    "credentials": integration_data.get("credentials", {}),
    "status": "connected",
    "connected_at": datetime.utcnow(),
    "last_sync": datetime.utcnow()
    }
        
        result = await db.user_integrations.insert_one(integration)
        return integration

# Global service instance
integration_service = IntegrationService()

    async def create_item(self, user_id: str, item_data: dict):
        """Create new item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            new_item = {
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                **item_data,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "status": "active"
            }
            
            await collections['items'].insert_one(new_item)
            
            return {
                "success": True,
                "data": new_item,
                "message": "Item created successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

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