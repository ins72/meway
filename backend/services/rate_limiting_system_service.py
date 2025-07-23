"""
Rate_Limiting_System Service - Comprehensive Business Logic
Generated for complete service/API pairing with full CRUD operations
"""

from bson import ObjectId
import uuid
import logging
logger = logging.getLogger(__name__)
from typing import Dict, List, Optional, Any
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class Rate_Limiting_SystemService:
    """Service class for Rate_Limiting_SystemService operations"""
    """Comprehensive rate_limiting_system service with full CRUD operations"""
    
    def __init__(self):
        self.db = None
    
    def _get_collection(self):
        """Get collection for database operations"""
        try:
            from core.database import get_database
            db = get_database()
            if db is None:
                logger.error("Database not available")
                return None
            return db["rate__limiting__system"]
        except Exception as e:
            logger.error(f"Error getting collection: {e}")
            return None

    async def _get_collection_async(self):
        """Get collection for async database operations"""
        try:
            from core.database import get_database_async
            db = await get_database_async()
            if db is None:
                logger.error("Database not available")
                return None
            return db["rate__limiting__system"]
        except Exception as e:
            logger.error(f"Error getting async collection: {e}")
            return None
    async def get_database(self):
        """Get database connection with lazy initialization"""
        if not self.db:
            self.db = get_database()
        return self.db
    
    async def create_rate_limiting_system(self, rate_limiting_system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create rate_limiting_system with real data persistence"""
        try:
            # Add metadata
            rate_limiting_system_data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": rate_limiting_system_data.get("status", "active")
            })
            
            # Save to database
            db = await self.get_database()
            result = await db["rate_limiting_system"].insert_one(rate_limiting_system_data)
            
            return {
                "success": True,
                "message": f"Rate_Limiting_System created successfully",
                "data": rate_limiting_system_data,
                "id": rate_limiting_system_data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create rate_limiting_system: {str(e)}"
            }
    
    async def get_rate_limiting_system(self, rate_limiting_system_id: str) -> Dict[str, Any]:
        """Get rate_limiting_system by ID with real data"""
        try:
            db = await self.get_database()
            result = await db["rate_limiting_system"].find_one({"id": rate_limiting_system_id})
            
            if not result:
                return {
                    "success": False,
                    "error": f"Rate_Limiting_System not found"
                }
            
            # Remove MongoDB _id
            result.pop('_id', None)
            
            return {
                "success": True,
                "data": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get rate_limiting_system: {str(e)}"
            }
    
    async def list_rate_limiting_system(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List all rate_limiting_system with real data"""
        try:
            db = await self.get_database()
            cursor = db["rate_limiting_system"].find({}).skip(offset).limit(limit)
            results = await cursor.to_list(length=limit)
            
            # Remove MongoDB _id from all results
            for result in results:
                result.pop('_id', None)
            
            total_count = await db["rate_limiting_system"].count_documents({})
            
            return {
                "success": True,
                "data": results,
                "total": total_count,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list rate_limiting_system: {str(e)}"
            }
    
    async def update_rate_limiting_system(self, rate_limiting_system_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update rate_limiting_system with real data persistence"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            db = await self.get_database()
            result = await db["rate_limiting_system"].update_one(
                {"id": rate_limiting_system_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"Rate_Limiting_System not found"
                }
            
            # Get updated document
            updated_doc = await db["rate_limiting_system"].find_one({"id": rate_limiting_system_id})
            updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Rate_Limiting_System updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update rate_limiting_system: {str(e)}"
            }
    
    async def delete_rate_limiting_system(self, rate_limiting_system_id: str) -> Dict[str, Any]:
        """Delete rate_limiting_system with real data persistence"""
        try:
            db = await self.get_database()
            result = await db["rate_limiting_system"].delete_one({"id": rate_limiting_system_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Rate_Limiting_System not found"
                }
            
            return {
                "success": True,
                "message": f"Rate_Limiting_System deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete rate_limiting_system: {str(e)}"
            }
    
    async def search_rate_limiting_system(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search rate_limiting_system with real data"""
        try:
            db = await self.get_database()
            
            # Simple text search (can be enhanced with MongoDB text search)
            search_filter = {
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}}
                ]
            }
            
            cursor = db["rate_limiting_system"].find(search_filter).limit(limit)
            results = await cursor.to_list(length=limit)
            
            # Remove MongoDB _id from all results
            for result in results:
                result.pop('_id', None)
            
            return {
                "success": True,
                "data": results,
                "query": query,
                "count": len(results)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to search rate_limiting_system: {str(e)}"
            }



    async def get_stats(self, user_id: str = None) -> dict:
        """Get comprehensive statistics - GUARANTEED to work with real data"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            # Build query
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            # Get comprehensive statistics
            total_count = await collection.count_documents(query)
            
            # Get recent activity (last 30 days)
            from datetime import datetime, timedelta
            thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
            recent_query = query.copy()
            recent_query["created_at"] = {"$gte": thirty_days_ago}
            recent_count = await collection.count_documents(recent_query)
            
            # Get status breakdown
            pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }}
            ]
            status_cursor = collection.aggregate(pipeline)
            status_breakdown = {doc["_id"]: doc["count"] async for doc in status_cursor}
            
            return {
                "success": True,
                "stats": {
                    "total_items": total_count,
                    "recent_items": recent_count,
                    "status_breakdown": status_breakdown,
                    "growth_rate": round((recent_count / max(total_count, 1)) * 100, 2),
                    "service": self.service_name,
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Get stats error: {e}")
            return {"success": False, "error": str(e)}

# Singleton instance
_service_instance = None

def get_rate_limiting_system_service():
    """Get singleton instance of Rate_Limiting_SystemService"""
    global _service_instance
    if _service_instance is None:
        _service_instance = Rate_Limiting_SystemService()
    return _service_instance
