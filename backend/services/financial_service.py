"""
Financial Service
Critical service implementation with full CRUD operations
"""

import uuid
from datetime import datetime
from typing import Dict, Any
from core.database import get_database

class FinancialService:
    def __init__(self):
        pass
    
    def _get_db(self):
        """Get database connection"""
        return get_database()
    
    def _get_collection(self):
        """Get collection"""
        try:
            db = self._get_db()
            return db["financial"] if db else None
        except:
            return None
    
    async def create_financial(self, data: dict) -> dict:
        """Create new financial"""
        try:
            collection = self._get_collection()
            if not collection: return {"success": False, "error": "Database unavailable"}
            
            data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            await collection.insert_one(data)
            data.pop('_id', None)
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_financial(self, item_id: str) -> dict:
        """Get financial by ID"""
        try:
            collection = self._get_collection()
            if not collection: return {"success": False, "error": "Database unavailable"}
            
            doc = await collection.find_one({"id": item_id})
            if not doc: return {"success": False, "error": "Not found"}
            
            doc.pop('_id', None)
            return {"success": True, "data": doc}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_financials(self, user_id: str = None, limit: int = 50, offset: int = 0) -> dict:
        """List financials"""
        try:
            collection = self._get_collection()
            if not collection: return {"success": False, "error": "Database unavailable"}
            
            query = {"user_id": user_id} if user_id else {}
            cursor = collection.find(query).skip(offset).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            for doc in docs:
                doc.pop('_id', None)
            
            total = await collection.count_documents(query)
            return {"success": True, "data": docs, "total": total}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_financial(self, item_id: str, update_data: dict) -> dict:
        """Update financial"""
        try:
            collection = self._get_collection()
            if not collection: return {"success": False, "error": "Database unavailable"}
            
            update_data["updated_at"] = datetime.utcnow().isoformat()
            result = await collection.update_one({"id": item_id}, {"$set": update_data})
            
            if result.matched_count == 0:
                return {"success": False, "error": "Not found"}
            
            return {"success": True, "message": "Updated successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_financial(self, item_id: str) -> dict:
        """Delete financial"""
        try:
            collection = self._get_collection()
            if not collection: return {"success": False, "error": "Database unavailable"}
            
            result = await collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {"success": False, "error": "Not found"}
            
            return {"success": True, "message": "Deleted successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Service instance
_service_instance = None

def get_financial_service():
    """Get service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = FinancialService()
    return _service_instance

# Backward compatibility
financial_service = get_financial_service()