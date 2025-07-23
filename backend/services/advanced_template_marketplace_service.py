"""
Advanced Template Marketplace Service
Complete CRUD operations for advanced_template_marketplace
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class AdvancedTemplateMarketplaceService:
    def __init__(self):
        self.db = None
        self.collection = None
    
    def _get_db(self):
        """Get database connection (lazy initialization)"""
        if self.db is None:
            self.db = get_database()
        return self.db
    
    def _get_collection(self, collection_name: str):
        """Get collection (lazy initialization)"""
        if self.collection is None:
            self.collection = self._get_db()[collection_name]
        return self.collection
        self.collection = self._get_db()["advancedtemplatemarketplace"]

    async def create_advanced_template_marketplace(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new advanced_template_marketplace"""
        try:
            # Add metadata
            data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            # Save to database
            result = await self._get_collection("default").insert_one(data)
            
            return {
                "success": True,
                "message": f"Advanced Template Marketplace created successfully",
                "data": data,
                "id": data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create advanced_template_marketplace: {str(e)}"
            }

    async def get_advanced_template_marketplace(self, item_id: str) -> Dict[str, Any]:
        """Get advanced_template_marketplace by ID"""
        try:
            doc = await self._get_collection("default").find_one({"id": item_id})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"Advanced Template Marketplace not found"
                }
            
            doc.pop('_id', None)
            return {
                "success": True,
                "data": doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get advanced_template_marketplace: {str(e)}"
            }

    async def list_advanced_template_marketplaces(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List advanced_template_marketplaces with pagination"""
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            cursor = self._get_collection("default").find(query).skip(offset).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            # Remove MongoDB _id field
            for doc in docs:
                doc.pop('_id', None)
            
            total_count = await self._get_collection("default").count_documents(query)
            
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
                "error": f"Failed to list advanced_template_marketplaces: {str(e)}"
            }

    async def update_advanced_template_marketplace(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update advanced_template_marketplace by ID"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self._get_collection("default").update_one(
                {"id": item_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"Advanced Template Marketplace not found"
                }
            
            # Get updated document
            updated_doc = await self._get_collection("default").find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Advanced Template Marketplace updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update advanced_template_marketplace: {str(e)}"
            }

    async def delete_advanced_template_marketplace(self, item_id: str) -> Dict[str, Any]:
        """Delete advanced_template_marketplace by ID"""
        try:
            result = await self._get_collection("default").delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Advanced Template Marketplace not found"
                }
            
            return {
                "success": True,
                "message": f"Advanced Template Marketplace deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete advanced_template_marketplace: {str(e)}"
            }

    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics for advanced_template_marketplaces"""
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            total_count = await self._get_collection("default").count_documents(query)
            active_count = await self._get_collection("default").count_documents({**query, "status": "active"})
            
            return {
                "success": True,
                "data": {
                    "total_count": total_count,
                    "active_count": active_count,
                    "service": "advanced_template_marketplace",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get advanced_template_marketplace stats: {str(e)}"
            }

# Service instance
_advanced_template_marketplace_service = None

def get_advanced_template_marketplace_service():
    """Get advanced_template_marketplace service instance"""
    global _advanced_template_marketplace_service
    if _advanced_template_marketplace_service is None:
        _advanced_template_marketplace_service = AdvancedTemplateMarketplaceService()
    return _advanced_template_marketplace_service

# For backward compatibility
advanced_template_marketplace_service = get_advanced_template_marketplace_service()