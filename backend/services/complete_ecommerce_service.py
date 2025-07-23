"""
Complete Ecommerce Service
Complete CRUD operations for complete_ecommerce
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class CompleteEcommerceService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["completeecommerce"]

    async def create_complete_ecommerce(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new complete_ecommerce"""
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
                "message": f"Complete Ecommerce created successfully",
                "data": data,
                "id": data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create complete_ecommerce: {str(e)}"
            }

    async def get_complete_ecommerce(self, item_id: str) -> Dict[str, Any]:
        """Get complete_ecommerce by ID"""
        try:
            doc = await self.collection.find_one({"id": item_id})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"Complete Ecommerce not found"
                }
            
            doc.pop('_id', None)
            return {
                "success": True,
                "data": doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get complete_ecommerce: {str(e)}"
            }

    async def list_complete_ecommerces(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List complete_ecommerces with pagination"""
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
                "error": f"Failed to list complete_ecommerces: {str(e)}"
            }

    async def update_complete_ecommerce(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update complete_ecommerce by ID"""
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
                    "error": f"Complete Ecommerce not found"
                }
            
            # Get updated document
            updated_doc = await self.collection.find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Complete Ecommerce updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update complete_ecommerce: {str(e)}"
            }

    async def delete_complete_ecommerce(self, item_id: str) -> Dict[str, Any]:
        """Delete complete_ecommerce by ID"""
        try:
            result = await self.collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Complete Ecommerce not found"
                }
            
            return {
                "success": True,
                "message": f"Complete Ecommerce deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete complete_ecommerce: {str(e)}"
            }

    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics for complete_ecommerces"""
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
                    "service": "complete_ecommerce",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get complete_ecommerce stats: {str(e)}"
            }

# Service instance
_complete_ecommerce_service = None

def get_complete_ecommerce_service():
    """Get complete_ecommerce service instance"""
    global _complete_ecommerce_service
    if _complete_ecommerce_service is None:
        _complete_ecommerce_service = CompleteEcommerceService()
    return _complete_ecommerce_service

# For backward compatibility
complete_ecommerce_service = get_complete_ecommerce_service()