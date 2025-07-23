"""
Integrations Service - Comprehensive Business Logic
Generated for complete service/API pairing with full CRUD operations
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class IntegrationsService:
    """Comprehensive integrations service with full CRUD operations"""
    
    def __init__(self):
        self.db = None
    
    async def get_database(self):
        """Get database connection with lazy initialization"""
        if not self.db:
            self.db = get_database()
        return self.db
    
    async def create_integrations(self, integrations_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create integrations with real data persistence"""
        try:
            # Add metadata
            integrations_data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": integrations_data.get("status", "active")
            })
            
            # Save to database
            db = await self.get_database()
            result = await db["integrations"].insert_one(integrations_data)
            
            return {
                "success": True,
                "message": f"Integrations created successfully",
                "data": integrations_data,
                "id": integrations_data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create integrations: {str(e)}"
            }
    
    async def get_integrations(self, integrations_id: str) -> Dict[str, Any]:
        """Get integrations by ID with real data"""
        try:
            db = await self.get_database()
            result = await db["integrations"].find_one({"id": integrations_id})
            
            if not result:
                return {
                    "success": False,
                    "error": f"Integrations not found"
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
                "error": f"Failed to get integrations: {str(e)}"
            }
    
    async def list_integrations(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List all integrations with real data"""
        try:
            db = await self.get_database()
            cursor = db["integrations"].find({}).skip(offset).limit(limit)
            results = await cursor.to_list(length=limit)
            
            # Remove MongoDB _id from all results
            for result in results:
                result.pop('_id', None)
            
            total_count = await db["integrations"].count_documents({})
            
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
                "error": f"Failed to list integrations: {str(e)}"
            }
    
    async def update_integrations(self, integrations_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update integrations with real data persistence"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            db = await self.get_database()
            result = await db["integrations"].update_one(
                {"id": integrations_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"Integrations not found"
                }
            
            # Get updated document
            updated_doc = await db["integrations"].find_one({"id": integrations_id})
            updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Integrations updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update integrations: {str(e)}"
            }
    
    async def delete_integrations(self, integrations_id: str) -> Dict[str, Any]:
        """Delete integrations with real data persistence"""
        try:
            db = await self.get_database()
            result = await db["integrations"].delete_one({"id": integrations_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Integrations not found"
                }
            
            return {
                "success": True,
                "message": f"Integrations deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete integrations: {str(e)}"
            }
    
    async def search_integrations(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search integrations with real data"""
        try:
            db = await self.get_database()
            
            # Simple text search (can be enhanced with MongoDB text search)
            search_filter = {
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}}
                ]
            }
            
            cursor = db["integrations"].find(search_filter).limit(limit)
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
                "error": f"Failed to search integrations: {str(e)}"
            }
