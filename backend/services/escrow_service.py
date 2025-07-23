"""
Escrow Service
Auto-generated service with full CRUD operations
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class EscrowService:
    def __init__(self):
        pass
    
    def _get_db(self):
        """Get database connection"""
        return get_database()
    
    async def create_escrow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new escrow"""
        try:
            db = self._get_db()
            if not db:
                return {"success": False, "error": "Database not available"}
            
            collection = db["escrow"]
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
    
    async def get_escrow(self, item_id: str) -> Dict[str, Any]:
        """Get escrow by ID"""
        try:
            db = self._get_db()
            if not db:
                return {"success": False, "error": "Database not available"}
            
            collection = db["escrow"]
            doc = await collection.find_one({"id": item_id})
            
            if not doc:
                return {"success": False, "error": "Not found"}
            
            doc.pop('_id', None)
            return {"success": True, "data": doc}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_escrows(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List escrows"""
        try:
            db = self._get_db()
            if not db:
                return {"success": False, "error": "Database not available"}
            
            collection = db["escrow"]
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
    
    async def update_escrow(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update escrow"""
        try:
            db = self._get_db()
            if not db:
                return {"success": False, "error": "Database not available"}
            
            collection = db["escrow"]
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
    
    async def delete_escrow(self, item_id: str) -> Dict[str, Any]:
        """Delete escrow"""
        try:
            db = self._get_db()
            if not db:
                return {"success": False, "error": "Database not available"}
            
            collection = db["escrow"]
            result = await collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {"success": False, "error": "Not found"}
            
            return {"success": True, "message": "Deleted successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Service instance
_service_instance = None

def get_escrow_service():
    """Get service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = EscrowService()
    return _service_instance

# Backward compatibility
escrow_service = get_escrow_service()