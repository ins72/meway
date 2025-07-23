"""
Mobile Pwa Service
Complete CRUD operations for mobile_pwa
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class MobilePwaService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["mobilepwa"]

    async def create_mobile_pwa(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new mobile_pwa"""
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
                "message": f"Mobile Pwa created successfully",
                "data": data,
                "id": data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create mobile_pwa: {str(e)}"
            }

    async def get_mobile_pwa(self, item_id: str) -> Dict[str, Any]:
        """Get mobile_pwa by ID"""
        try:
            doc = await self.collection.find_one({"id": item_id})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"Mobile Pwa not found"
                }
            
            doc.pop('_id', None)
            return {
                "success": True,
                "data": doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get mobile_pwa: {str(e)}"
            }

    async def list_mobile_pwas(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List mobile_pwas with pagination"""
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
                "error": f"Failed to list mobile_pwas: {str(e)}"
            }

    async def update_mobile_pwa(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update mobile_pwa by ID"""
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
                    "error": f"Mobile Pwa not found"
                }
            
            # Get updated document
            updated_doc = await self.collection.find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Mobile Pwa updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update mobile_pwa: {str(e)}"
            }

    async def delete_mobile_pwa(self, item_id: str) -> Dict[str, Any]:
        """Delete mobile_pwa by ID"""
        try:
            result = await self.collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Mobile Pwa not found"
                }
            
            return {
                "success": True,
                "message": f"Mobile Pwa deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete mobile_pwa: {str(e)}"
            }

    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics for mobile_pwas"""
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
                    "service": "mobile_pwa",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get mobile_pwa stats: {str(e)}"
            }

# Service instance
_mobile_pwa_service = None

def get_mobile_pwa_service():
    """Get mobile_pwa service instance"""
    global _mobile_pwa_service
    if _mobile_pwa_service is None:
        _mobile_pwa_service = MobilePwaService()
    return _mobile_pwa_service

# For backward compatibility
mobile_pwa_service = get_mobile_pwa_service()