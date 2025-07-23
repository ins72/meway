"""
Content Creation Service
Auto-generated to complete service/API pairing
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class ContentCreationService:
    def __init__(self):
        self.db = None
        self.collection = None
    
    def _get_db(self):
        """Get database connection (lazy initialization)"""
        if self.db is None:
            self.db = get_database()
        return self.db
    
    def _get_collection(self, collection_name: str):
        """Get collection (lazy initialization)"""
        if self.collection is None:
            self.collection = self._get_db()[collection_name]
        return self.collection

    async def create_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new content"""
        try:
            # Add metadata
            content_data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            # Save to database
            result = await self._get_db()["content_creation"].insert_one(content_data)
            
            return {
                "success": True,
                "message": "Content created successfully",
                "data": content_data
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create content: {str(e)}"
            }

    async def get_content(self, content_id: str) -> Dict[str, Any]:
        """Get content by ID"""
        try:
            result = await self._get_db()["content_creation"].find_one({"id": content_id})
            if not result:
                return {
                    "success": False,
                    "error": "Content not found"
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
                "error": f"Failed to get content: {str(e)}"
            }

    async def list_content(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List content with pagination"""
        try:
            cursor = self._get_db()["content_creation"].find().skip(offset).limit(limit)
            results = await cursor.to_list(length=limit)
            
            # Remove MongoDB _id from all results
            for result in results:
                result.pop('_id', None)
            
            total_count = await self._get_db()["content_creation"].count_documents({})
            
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
                "error": f"Failed to list content: {str(e)}"
            }

    async def update_content(self, content_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update content by ID"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self._get_db()["content_creation"].update_one(
                {"id": content_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": "Content not found"
                }
            
            # Get updated document
            updated_doc = await self._get_db()["content_creation"].find_one({"id": content_id})
            updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": "Content updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update content: {str(e)}"
            }

    async def delete_content(self, content_id: str) -> Dict[str, Any]:
        """Delete content by ID"""
        try:
            result = await self._get_db()["content_creation"].delete_one({"id": content_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": "Content not found"
                }
            
            return {
                "success": True,
                "message": "Content deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete content: {str(e)}"
            }

# Service instance
_content_creation_service = None

def get_content_creation_service():
    """Get content creation service instance"""
    global _content_creation_service
    if _content_creation_service is None:
        _content_creation_service = ContentCreationService()
    return _content_creation_service

# For backward compatibility
content_creation_service = get_content_creation_service()