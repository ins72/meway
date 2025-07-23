"""
Course Management Service
Auto-generated service with full CRUD operations
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class CourseManagementService:
    def __init__(self):
        pass
    
    def _get_db(self):
        """Get database connection"""
        return get_database()
    
    async def create_course_management(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new course_management"""
        try:
            db = self._get_db()
            if not db:
                return {"success": False, "error": "Database not available"}
            
            collection = db["course_management"]
            data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            await collection.insert_one(data)
            return {"success": True, "data": data, "id": data["id"]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_course_management(self, item_id: str) -> Dict[str, Any]:
        """Get course_management by ID"""
        try:
            db = self._get_db()
            if not db:
                return {"success": False, "error": "Database not available"}
            
            collection = db["course_management"]
            doc = await collection.find_one({"id": item_id})
            
            if not doc:
                return {"success": False, "error": "Not found"}
            
            doc.pop('_id', None)
            return {"success": True, "data": doc}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_course_managements(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List course_managements"""
        try:
            db = self._get_db()
            if not db:
                return {"success": False, "error": "Database not available"}
            
            collection = db["course_management"]
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            cursor = collection.find(query).skip(offset).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            for doc in docs:
                doc.pop('_id', None)
            
            total_count = await collection.count_documents(query)
            return {"success": True, "data": docs, "total": total_count}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_course_management(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update course_management"""
        try:
            db = self._get_db()
            if not db:
                return {"success": False, "error": "Database not available"}
            
            collection = db["course_management"]
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await collection.update_one(
                {"id": item_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Not found"}
            
            return {"success": True, "message": "Updated successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_course_management(self, item_id: str) -> Dict[str, Any]:
        """Delete course_management"""
        try:
            db = self._get_db()
            if not db:
                return {"success": False, "error": "Database not available"}
            
            collection = db["course_management"]
            result = await collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {"success": False, "error": "Not found"}
            
            return {"success": True, "message": "Deleted successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Service instance
_service_instance = None

def get_course_management_service():
    """Get service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = CourseManagementService()
    return _service_instance

# Backward compatibility
course_management_service = get_course_management_service()