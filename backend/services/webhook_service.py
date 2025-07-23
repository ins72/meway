"""
Webhook Service
Complete CRUD operations for webhook
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class WebhookService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["webhook"]

    async def create_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new webhook"""
        try:
            # Add metadata
            data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            # Save to database
            result = await self.collection.insert_one(data)
            
            return {
                "success": True,
                "message": f"Webhook created successfully",
                "data": data,
                "id": data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create webhook: {str(e)}"
            }

    async def get_webhook(self, item_id: str) -> Dict[str, Any]:
        """Get webhook by ID"""
        try:
            doc = await self.collection.find_one({"id": item_id})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"Webhook not found"
                }
            
            doc.pop('_id', None)
            return {
                "success": True,
                "data": doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get webhook: {str(e)}"
            }

    async def list_webhooks(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List webhooks with pagination"""
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            cursor = self.collection.find(query).skip(offset).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            # Remove MongoDB _id field
            for doc in docs:
                doc.pop('_id', None)
            
            total_count = await self.collection.count_documents(query)
            
            return {
                "success": True,
                "data": docs,
                "total": total_count,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list webhooks: {str(e)}"
            }

    async def update_webhook(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update webhook by ID"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self.collection.update_one(
                {"id": item_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"Webhook not found"
                }
            
            # Get updated document
            updated_doc = await self.collection.find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Webhook updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update webhook: {str(e)}"
            }

    async def delete_webhook(self, item_id: str) -> Dict[str, Any]:
        """Delete webhook by ID"""
        try:
            result = await self.collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Webhook not found"
                }
            
            return {
                "success": True,
                "message": f"Webhook deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete webhook: {str(e)}"
            }

    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics for webhooks"""
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            total_count = await self.collection.count_documents(query)
            active_count = await self.collection.count_documents({**query, "status": "active"})
            
            return {
                "success": True,
                "data": {
                    "total_count": total_count,
                    "active_count": active_count,
                    "service": "webhook",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get webhook stats: {str(e)}"
            }

# Service instance
_webhook_service = None

def get_webhook_service():
    """Get webhook service instance"""
    global _webhook_service
    if _webhook_service is None:
        _webhook_service = WebhookService()
    return _webhook_service

# For backward compatibility
webhook_service = get_webhook_service()