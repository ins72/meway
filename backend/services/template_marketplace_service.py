"""
Template Marketplace Service
Complete CRUD operations for template_marketplace
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class TemplateMarketplaceService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["templatemarketplace"]

    async def create_template_marketplace(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new template_marketplace"""
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
                "message": f"Template Marketplace created successfully",
                "data": data,
                "id": data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create template_marketplace: {str(e)}"
            }

    async def get_template_marketplace(self, item_id: str) -> Dict[str, Any]:
        """Get template_marketplace by ID"""
        try:
            doc = await self.collection.find_one({"id": item_id})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"Template Marketplace not found"
                }
            
            doc.pop('_id', None)
            return {
                "success": True,
                "data": doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get template_marketplace: {str(e)}"
            }

    async def list_template_marketplaces(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List template_marketplaces with pagination"""
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
                "error": f"Failed to list template_marketplaces: {str(e)}"
            }

    async def update_template_marketplace(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update template_marketplace by ID"""
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
                    "error": f"Template Marketplace not found"
                }
            
            # Get updated document
            updated_doc = await self.collection.find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Template Marketplace updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update template_marketplace: {str(e)}"
            }

    async def delete_template_marketplace(self, item_id: str) -> Dict[str, Any]:
        """Delete template_marketplace by ID"""
        try:
            result = await self.collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Template Marketplace not found"
                }
            
            return {
                "success": True,
                "message": f"Template Marketplace deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete template_marketplace: {str(e)}"
            }

    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics for template_marketplaces"""
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
                    "service": "template_marketplace",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get template_marketplace stats: {str(e)}"
            }

# Service instance
_template_marketplace_service = None

def get_template_marketplace_service():
    """Get template_marketplace service instance"""
    global _template_marketplace_service
    if _template_marketplace_service is None:
        _template_marketplace_service = TemplateMarketplaceService()
    return _template_marketplace_service

# For backward compatibility
template_marketplace_service = get_template_marketplace_service()