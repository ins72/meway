"""
Complete Website Builder Service
Complete CRUD operations for complete_website_builder
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class CompleteWebsiteBuilderService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["completewebsitebuilder"]

    async def create_complete_website_builder(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new complete_website_builder"""
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
                "message": f"Complete Website Builder created successfully",
                "data": data,
                "id": data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create complete_website_builder: {str(e)}"
            }

    async def get_complete_website_builder(self, item_id: str) -> Dict[str, Any]:
        """Get complete_website_builder by ID"""
        try:
            doc = await self.collection.find_one({"id": item_id})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"Complete Website Builder not found"
                }
            
            doc.pop('_id', None)
            return {
                "success": True,
                "data": doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get complete_website_builder: {str(e)}"
            }

    async def list_complete_website_builders(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List complete_website_builders with pagination"""
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
                "error": f"Failed to list complete_website_builders: {str(e)}"
            }

    async def update_complete_website_builder(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update complete_website_builder by ID"""
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
                    "error": f"Complete Website Builder not found"
                }
            
            # Get updated document
            updated_doc = await self.collection.find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Complete Website Builder updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update complete_website_builder: {str(e)}"
            }

    async def delete_complete_website_builder(self, item_id: str) -> Dict[str, Any]:
        """Delete complete_website_builder by ID"""
        try:
            result = await self.collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Complete Website Builder not found"
                }
            
            return {
                "success": True,
                "message": f"Complete Website Builder deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete complete_website_builder: {str(e)}"
            }

    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics for complete_website_builders"""
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
                    "service": "complete_website_builder",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get complete_website_builder stats: {str(e)}"
            }

# Service instance
_complete_website_builder_service = None

def get_complete_website_builder_service():
    """Get complete_website_builder service instance"""
    global _complete_website_builder_service
    if _complete_website_builder_service is None:
        _complete_website_builder_service = CompleteWebsiteBuilderService()
    return _complete_website_builder_service

# For backward compatibility
complete_website_builder_service = get_complete_website_builder_service()