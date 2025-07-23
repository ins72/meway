"""
Media_Library Service - Comprehensive Business Logic
Generated for complete service/API pairing with full CRUD operations
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class Media_LibraryService:
    """Comprehensive media_library service with full CRUD operations"""
    
    def __init__(self):
        self.db = None
    
    async def get_database(self):
        """Get database connection with lazy initialization"""
        if not self.db:
            self.db = get_database()
        return self.db
    
    async def create_media_library(self, media_library_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create media_library with real data persistence"""
        try:
            # Add metadata
            media_library_data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": media_library_data.get("status", "active")
            })
            
            # Save to database
            db = await self.get_database()
            result = await db["media_library"].insert_one(media_library_data)
            
            return {
                "success": True,
                "message": f"Media_Library created successfully",
                "data": media_library_data,
                "id": media_library_data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create media_library: {str(e)}"
            }
    
    async def get_media_library(self, media_library_id: str) -> Dict[str, Any]:
        """Get media_library by ID with real data"""
        try:
            db = await self.get_database()
            result = await db["media_library"].find_one({"id": media_library_id})
            
            if not result:
                return {
                    "success": False,
                    "error": f"Media_Library not found"
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
                "error": f"Failed to get media_library: {str(e)}"
            }
    
    async def list_media_library(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List all media_library with real data"""
        try:
            db = await self.get_database()
            cursor = db["media_library"].find({}).skip(offset).limit(limit)
            results = await cursor.to_list(length=limit)
            
            # Remove MongoDB _id from all results
            for result in results:
                result.pop('_id', None)
            
            total_count = await db["media_library"].count_documents({})
            
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
                "error": f"Failed to list media_library: {str(e)}"
            }
    
    async def update_media_library(self, media_library_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update media_library with real data persistence"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            db = await self.get_database()
            result = await db["media_library"].update_one(
                {"id": media_library_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"Media_Library not found"
                }
            
            # Get updated document
            updated_doc = await db["media_library"].find_one({"id": media_library_id})
            updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Media_Library updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update media_library: {str(e)}"
            }
    
    async def delete_media_library(self, media_library_id: str) -> Dict[str, Any]:
        """Delete media_library with real data persistence"""
        try:
            db = await self.get_database()
            result = await db["media_library"].delete_one({"id": media_library_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Media_Library not found"
                }
            
            return {
                "success": True,
                "message": f"Media_Library deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete media_library: {str(e)}"
            }
    
    async def search_media_library(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search media_library with real data"""
        try:
            db = await self.get_database()
            
            # Simple text search (can be enhanced with MongoDB text search)
            search_filter = {
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}}
                ]
            }
            
            cursor = db["media_library"].find(search_filter).limit(limit)
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
                "error": f"Failed to search media_library: {str(e)}"
            }
