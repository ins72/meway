"""
Notification_System Service - Comprehensive Business Logic
Generated for complete service/API pairing with full CRUD operations
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class Notification_SystemService:
    """Comprehensive notification_system service with full CRUD operations"""
    
    def __init__(self):
        self.db = None
    
    async def get_database(self):
        """Get database connection with lazy initialization"""
        if not self.db:
            self.db = get_database()
        return self.db
    
    async def create_notification_system(self, notification_system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create notification_system with real data persistence"""
        try:
            # Add metadata
            notification_system_data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": notification_system_data.get("status", "active")
            })
            
            # Save to database
            db = await self.get_database()
            result = await db["notification_system"].insert_one(notification_system_data)
            
            return {
                "success": True,
                "message": f"Notification_System created successfully",
                "data": notification_system_data,
                "id": notification_system_data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create notification_system: {str(e)}"
            }
    
    async def get_notification_system(self, notification_system_id: str) -> Dict[str, Any]:
        """Get notification_system by ID with real data"""
        try:
            db = await self.get_database()
            result = await db["notification_system"].find_one({"id": notification_system_id})
            
            if not result:
                return {
                    "success": False,
                    "error": f"Notification_System not found"
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
                "error": f"Failed to get notification_system: {str(e)}"
            }
    
    async def list_notification_system(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List all notification_system with real data"""
        try:
            db = await self.get_database()
            cursor = db["notification_system"].find({}).skip(offset).limit(limit)
            results = await cursor.to_list(length=limit)
            
            # Remove MongoDB _id from all results
            for result in results:
                result.pop('_id', None)
            
            total_count = await db["notification_system"].count_documents({})
            
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
                "error": f"Failed to list notification_system: {str(e)}"
            }
    
    async def update_notification_system(self, notification_system_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update notification_system with real data persistence"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            db = await self.get_database()
            result = await db["notification_system"].update_one(
                {"id": notification_system_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"Notification_System not found"
                }
            
            # Get updated document
            updated_doc = await db["notification_system"].find_one({"id": notification_system_id})
            updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Notification_System updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update notification_system: {str(e)}"
            }
    
    async def delete_notification_system(self, notification_system_id: str) -> Dict[str, Any]:
        """Delete notification_system with real data persistence"""
        try:
            db = await self.get_database()
            result = await db["notification_system"].delete_one({"id": notification_system_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Notification_System not found"
                }
            
            return {
                "success": True,
                "message": f"Notification_System deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete notification_system: {str(e)}"
            }
    
    async def search_notification_system(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search notification_system with real data"""
        try:
            db = await self.get_database()
            
            # Simple text search (can be enhanced with MongoDB text search)
            search_filter = {
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}}
                ]
            }
            
            cursor = db["notification_system"].find(search_filter).limit(limit)
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
                "error": f"Failed to search notification_system: {str(e)}"
            }
