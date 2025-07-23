"""
Admin Configuration Service
Complete CRUD operations for admin_configuration
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class AdminConfigurationService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["adminconfiguration"]

    async def create_admin_configuration(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new admin_configuration"""
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
                "message": f"Admin Configuration created successfully",
                "data": data,
                "id": data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create admin_configuration: {str(e)}"
            }

    async def get_admin_configuration(self, item_id: str) -> Dict[str, Any]:
        """Get admin_configuration by ID"""
        try:
            doc = await self.collection.find_one({"id": item_id})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"Admin Configuration not found"
                }
            
            doc.pop('_id', None)
            return {
                "success": True,
                "data": doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get admin_configuration: {str(e)}"
            }

    async def list_admin_configurations(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List admin_configurations with pagination"""
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
                "error": f"Failed to list admin_configurations: {str(e)}"
            }

    async def update_admin_configuration(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update admin_configuration by ID"""
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
                    "error": f"Admin Configuration not found"
                }
            
            # Get updated document
            updated_doc = await self.collection.find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Admin Configuration updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update admin_configuration: {str(e)}"
            }

    async def delete_admin_configuration(self, item_id: str) -> Dict[str, Any]:
        """Delete admin_configuration by ID"""
        try:
            result = await self.collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Admin Configuration not found"
                }
            
            return {
                "success": True,
                "message": f"Admin Configuration deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete admin_configuration: {str(e)}"
            }

    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics for admin_configurations"""
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
                    "service": "admin_configuration",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get admin_configuration stats: {str(e)}"
            }

# Service instance
_admin_configuration_service = None

def get_admin_configuration_service():
    """Get admin_configuration service instance"""
    global _admin_configuration_service
    if _admin_configuration_service is None:
        _admin_configuration_service = AdminConfigurationService()
    return _admin_configuration_service

# For backward compatibility
admin_configuration_service = get_admin_configuration_service()