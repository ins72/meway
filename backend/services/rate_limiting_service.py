"""
Rate Limiting Service
Complete CRUD operations for rate_limiting
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class RateLimitingService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["ratelimiting"]

    async def create_rate_limiting(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new rate_limiting"""
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
                "message": f"Rate Limiting created successfully",
                "data": data,
                "id": data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create rate_limiting: {str(e)}"
            }

    async def get_rate_limiting(self, item_id: str) -> Dict[str, Any]:
        """Get rate_limiting by ID"""
        try:
            doc = await self.collection.find_one({"id": item_id})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"Rate Limiting not found"
                }
            
            doc.pop('_id', None)
            return {
                "success": True,
                "data": doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get rate_limiting: {str(e)}"
            }

    async def list_rate_limitings(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List rate_limitings with pagination"""
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
                "error": f"Failed to list rate_limitings: {str(e)}"
            }

    async def update_rate_limiting(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update rate_limiting by ID"""
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
                    "error": f"Rate Limiting not found"
                }
            
            # Get updated document
            updated_doc = await self.collection.find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Rate Limiting updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update rate_limiting: {str(e)}"
            }

    async def delete_rate_limiting(self, item_id: str) -> Dict[str, Any]:
        """Delete rate_limiting by ID"""
        try:
            result = await self.collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Rate Limiting not found"
                }
            
            return {
                "success": True,
                "message": f"Rate Limiting deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete rate_limiting: {str(e)}"
            }

    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics for rate_limitings"""
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
                    "service": "rate_limiting",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get rate_limiting stats: {str(e)}"
            }

# Service instance
_rate_limiting_service = None

def get_rate_limiting_service():
    """Get rate_limiting service instance"""
    global _rate_limiting_service
    if _rate_limiting_service is None:
        _rate_limiting_service = RateLimitingService()
    return _rate_limiting_service

# For backward compatibility
rate_limiting_service = get_rate_limiting_service()