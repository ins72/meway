"""
Compliance Service
Complete CRUD operations for compliance
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class ComplianceService:
    def __init__(self):
        self.db = None
        self.collection = None
    
    def _get_db(self):
        """Get database connection (lazy initialization)"""
        if self.db is None:
            self.db = get_database()
        return self.db
    
    def _get_collection(self):
        """Get collection (lazy initialization)"""
        if self.collection is None:
            self.collection = self._get_db()["compliance"]
        return self.collection

    async def create_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new compliance"""
        try:
            collection = self._get_collection()
            # Add metadata
            data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            # Save to database
            result = await collection.insert_one(data)
            
            return {
                "success": True,
                "message": f"Compliance created successfully",
                "data": data,
                "id": data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create compliance: {str(e)}"
            }

    async def get_compliance(self, item_id: str) -> Dict[str, Any]:
        """Get compliance by ID"""
        try:
            collection = self._get_collection()
            doc = await collection.find_one({"id": item_id})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"Compliance not found"
                }
            
            doc.pop('_id', None)
            return {
                "success": True,
                "data": doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get compliance: {str(e)}"
            }

    async def list_compliances(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List compliances with pagination"""
        try:
            collection = self._get_collection()
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            cursor = collection.find(query).skip(offset).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            # Remove MongoDB _id field
            for doc in docs:
                doc.pop('_id', None)
            
            total_count = await collection.count_documents(query)
            
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
                "error": f"Failed to list compliances: {str(e)}"
            }

    async def update_compliance(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update compliance by ID"""
        try:
            collection = self._get_collection()
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await collection.update_one(
                {"id": item_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"Compliance not found"
                }
            
            # Get updated document
            updated_doc = await collection.find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Compliance updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update compliance: {str(e)}"
            }

    async def delete_compliance(self, item_id: str) -> Dict[str, Any]:
        """Delete compliance by ID"""
        try:
            collection = self._get_collection()
            result = await collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Compliance not found"
                }
            
            return {
                "success": True,
                "message": f"Compliance deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete compliance: {str(e)}"
            }

    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics for compliances"""
        try:
            collection = self._get_collection()
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            total_count = await collection.count_documents(query)
            active_count = await collection.count_documents({**query, "status": "active"})
            
            return {
                "success": True,
                "data": {
                    "total_count": total_count,
                    "active_count": active_count,
                    "service": "compliance",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get compliance stats: {str(e)}"
            }

# Service instance
_compliance_service = None

def get_compliance_service():
    """Get compliance service instance"""
    global _compliance_service
    if _compliance_service is None:
        _compliance_service = ComplianceService()
    return _compliance_service

# For backward compatibility
compliance_service = get_compliance_service()