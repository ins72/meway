"""
Marketing Services Business Logic
Professional Mewayz Platform
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from core.database import get_database
import uuid

class MarketingService:
    """Service for marketing operations"""
    
    @staticmethod
    async def get_campaigns(user_id: str):
        """Get user's marketing campaigns"""
        db = await get_database()
        
        campaigns = await db.marketing_campaigns.find({"user_id": user_id}).sort("created_at", -1).to_list(length=None)
        return campaigns
    
    @staticmethod
    async def create_campaign(user_id: str, campaign_data: Dict[str, Any]):
        """Create new marketing campaign"""
        db = await get_database()
        
        campaign = {
    "_id": str(uuid.uuid4()),
    "user_id": user_id,
    "name": campaign_data.get("name"),
    "type": campaign_data.get("type", "email"),
    "status": "draft",
    "target_audience": campaign_data.get("target_audience", {}),
    "content": campaign_data.get("content", {}),
    "schedule": campaign_data.get("schedule"),
    "metrics": {
    "sent": 0,
    "delivered": 0,
    "opened": 0,
    "clicked": 0
    },
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
    }
        
        result = await db.marketing_campaigns.insert_one(campaign)
        return campaign
    
    @staticmethod
    async def get_campaign_analytics(user_id: str, campaign_id: str):
        """Get campaign analytics"""
        db = await get_database()
        
        campaign = await db.marketing_campaigns.find_one({
    "_id": campaign_id,
    "user_id": user_id
    })
        
        if not campaign:
            return None
        
        # In real implementation, this would aggregate actual metrics
        analytics = {
    "campaign_id": campaign_id,
    "performance": campaign.get("metrics", {}),
    "timeline": [
    {
                    "date": datetime.utcnow() - timedelta(days=i),
    "opens": 10 + i * 2,
    "clicks": 3 + i
    }
                for i in range(7)
    ],
    "top_links": [
    {"url": "https://mewayz.com", "clicks": 45},
    {"url": "https://mewayz.com", "clicks": 32}
    ]
    }
        
        return analytics

# Global service instance
marketing_service = MarketingService()

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