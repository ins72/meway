"""
Automation System Service
Complete CRUD operations for automation_system
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class AutomationSystemService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["automationsystem"]

    async def create_automation_system(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new automation_system"""
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
                "message": f"Automation System created successfully",
                "data": data,
                "id": data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create automation_system: {str(e)}"
            }

    async def get_automation_system(self, item_id: str) -> Dict[str, Any]:
        """Get automation_system by ID"""
        try:
            doc = await self.collection.find_one({"id": item_id})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"Automation System not found"
                }
            
            doc.pop('_id', None)
            return {
                "success": True,
                "data": doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get automation_system: {str(e)}"
            }

    async def list_automation_systems(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List automation_systems with pagination"""
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
                "error": f"Failed to list automation_systems: {str(e)}"
            }

    async def update_automation_system(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update automation_system by ID"""
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
                    "error": f"Automation System not found"
                }
            
            # Get updated document
            updated_doc = await self.collection.find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Automation System updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update automation_system: {str(e)}"
            }

    async def delete_automation_system(self, item_id: str) -> Dict[str, Any]:
        """Delete automation_system by ID"""
        try:
            result = await self.collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Automation System not found"
                }
            
            return {
                "success": True,
                "message": f"Automation System deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete automation_system: {str(e)}"
            }

    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics for automation_systems"""
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
                    "service": "automation_system",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get automation_system stats: {str(e)}"
            }

# Service instance
_automation_system_service = None

def get_automation_system_service():
    """Get automation_system service instance"""
    global _automation_system_service
    if _automation_system_service is None:
        _automation_system_service = AutomationSystemService()
    return _automation_system_service

# For backward compatibility
automation_system_service = get_automation_system_service()