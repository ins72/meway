"""
Media Library Service
Auto-generated service with proper database initialization
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class MediaLibraryService:
    def __init__(self):
        pass
    
    def _get_db(self):
        """Get database connection"""
        return get_database()
    
    async def create_media_library(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new media_library"""
        try:
            db = self._get_db()
            if not db:
                return {"success": False, "error": "Database not available"}
            
            collection = db["media_library"]
            data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            result = await collection.insert_one(data)
            return {"success": True, "data": data, "id": data["id"]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_media_library(self, item_id: str) -> Dict[str, Any]:
        """Get media_library by ID"""
        try:
            db = self._get_db()
            if not db:
                return {"success": False, "error": "Database not available"}
            
            collection = db["media_library"]
            doc = await collection.find_one({"id": item_id})
            
            if not doc:
                return {"success": False, "error": "Not found"}
            
            doc.pop('_id', None)
            return {"success": True, "data": doc}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_media_librarys(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List media_librarys"""
        try:
            db = self._get_db()
            if not db:
                return {"success": False, "error": "Database not available"}
            
            collection = db["media_library"]
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            cursor = collection.find(query).skip(offset).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            for doc in docs:
                doc.pop('_id', None)
            
            total_count = await collection.count_documents(query)
            return {"success": True, "data": docs, "total": total_count, "limit": limit, "offset": offset}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_media_library(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update media_library"""
        try:
            db = self._get_db()
            if not db:
                return {"success": False, "error": "Database not available"}
            
            collection = db["media_library"]
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await collection.update_one(
                {"id": item_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Not found"}
            
            updated_doc = await collection.find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {"success": True, "data": updated_doc}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_media_library(self, item_id: str) -> Dict[str, Any]:
        """Delete media_library"""
        try:
            db = self._get_db()
            if not db:
                return {"success": False, "error": "Database not available"}
            
            collection = db["media_library"]
            result = await collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {"success": False, "error": "Not found"}
            
            return {"success": True, "message": "Deleted successfully", "deleted_count": result.deleted_count}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Service instance
_service_instance = None

def get_media_library_service():
    """Get service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = MediaLibraryService()
    return _service_instance

# Backward compatibility
media_library_service = get_media_library_service()