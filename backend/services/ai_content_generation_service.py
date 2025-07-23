"""
Ai_Content_Generation Service - Comprehensive Business Logic
Generated for complete service/API pairing with full CRUD operations
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class Ai_Content_GenerationService:
    """Comprehensive ai_content_generation service with full CRUD operations"""
    
    def __init__(self):
        self.db = None
    
    async def get_database(self):
        """Get database connection with lazy initialization"""
        if not self.db:
            self.db = get_database()
        return self.db
    
    async def create_ai_content_generation(self, ai_content_generation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create ai_content_generation with real data persistence"""
        try:
            # Add metadata
            ai_content_generation_data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": ai_content_generation_data.get("status", "active")
            })
            
            # Save to database
            db = await self.get_database()
            result = await db["ai_content_generation"].insert_one(ai_content_generation_data)
            
            return {
                "success": True,
                "message": f"Ai_Content_Generation created successfully",
                "data": ai_content_generation_data,
                "id": ai_content_generation_data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create ai_content_generation: {str(e)}"
            }
    
    async def get_ai_content_generation(self, ai_content_generation_id: str) -> Dict[str, Any]:
        """Get ai_content_generation by ID with real data"""
        try:
            db = await self.get_database()
            result = await db["ai_content_generation"].find_one({"id": ai_content_generation_id})
            
            if not result:
                return {
                    "success": False,
                    "error": f"Ai_Content_Generation not found"
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
                "error": f"Failed to get ai_content_generation: {str(e)}"
            }
    
    async def list_ai_content_generation(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List all ai_content_generation with real data"""
        try:
            db = await self.get_database()
            cursor = db["ai_content_generation"].find({}).skip(offset).limit(limit)
            results = await cursor.to_list(length=limit)
            
            # Remove MongoDB _id from all results
            for result in results:
                result.pop('_id', None)
            
            total_count = await db["ai_content_generation"].count_documents({})
            
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
                "error": f"Failed to list ai_content_generation: {str(e)}"
            }
    
    async def update_ai_content_generation(self, ai_content_generation_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update ai_content_generation with real data persistence"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            db = await self.get_database()
            result = await db["ai_content_generation"].update_one(
                {"id": ai_content_generation_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"Ai_Content_Generation not found"
                }
            
            # Get updated document
            updated_doc = await db["ai_content_generation"].find_one({"id": ai_content_generation_id})
            updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Ai_Content_Generation updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update ai_content_generation: {str(e)}"
            }
    
    async def delete_ai_content_generation(self, ai_content_generation_id: str) -> Dict[str, Any]:
        """Delete ai_content_generation with real data persistence"""
        try:
            db = await self.get_database()
            result = await db["ai_content_generation"].delete_one({"id": ai_content_generation_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Ai_Content_Generation not found"
                }
            
            return {
                "success": True,
                "message": f"Ai_Content_Generation deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete ai_content_generation: {str(e)}"
            }
    
    async def search_ai_content_generation(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search ai_content_generation with real data"""
        try:
            db = await self.get_database()
            
            # Simple text search (can be enhanced with MongoDB text search)
            search_filter = {
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}}
                ]
            }
            
            cursor = db["ai_content_generation"].find(search_filter).limit(limit)
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
                "error": f"Failed to search ai_content_generation: {str(e)}"
            }
