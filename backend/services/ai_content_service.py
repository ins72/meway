"""
Ai Content Service
Complete CRUD operations for ai_content
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class AiContentService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["aicontent"]

    async def create_ai_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new ai_content"""
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
                "message": f"Ai Content created successfully",
                "data": data,
                "id": data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create ai_content: {str(e)}"
            }

    async def get_ai_content(self, item_id: str) -> Dict[str, Any]:
        """Get ai_content by ID"""
        try:
            doc = await self.collection.find_one({"id": item_id})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"Ai Content not found"
                }
            
            doc.pop('_id', None)
            return {
                "success": True,
                "data": doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get ai_content: {str(e)}"
            }

    async def list_ai_contents(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List ai_contents with pagination"""
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
                "error": f"Failed to list ai_contents: {str(e)}"
            }

    async def update_ai_content(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update ai_content by ID"""
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
                    "error": f"Ai Content not found"
                }
            
            # Get updated document
            updated_doc = await self.collection.find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Ai Content updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update ai_content: {str(e)}"
            }

    async def delete_ai_content(self, item_id: str) -> Dict[str, Any]:
        """Delete ai_content by ID"""
        try:
            result = await self.collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Ai Content not found"
                }
            
            return {
                "success": True,
                "message": f"Ai Content deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete ai_content: {str(e)}"
            }

    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics for ai_contents"""
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
                    "service": "ai_content",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get ai_content stats: {str(e)}"
            }

# Service instance
_ai_content_service = None

def get_ai_content_service():
    """Get ai_content service instance"""
    global _ai_content_service
    if _ai_content_service is None:
        _ai_content_service = AiContentService()
    return _ai_content_service

# For backward compatibility
ai_content_service = get_ai_content_service()