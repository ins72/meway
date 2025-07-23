"""
Business Intelligence Service
Complete CRUD operations for business_intelligence
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class BusinessIntelligenceService:
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
        self.collection = self._get_db()["businessintelligence"]

    async def create_business_intelligence(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new business_intelligence"""
        try:
            # Add metadata
            data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            # Save to database
            result = await self._get_collection("default").insert_one(data)
            
            return {
                "success": True,
                "message": f"Business Intelligence created successfully",
                "data": data,
                "id": data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create business_intelligence: {str(e)}"
            }

    async def get_business_intelligence(self, item_id: str) -> Dict[str, Any]:
        """Get business_intelligence by ID"""
        try:
            doc = await self._get_collection("default").find_one({"id": item_id})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"Business Intelligence not found"
                }
            
            doc.pop('_id', None)
            return {
                "success": True,
                "data": doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get business_intelligence: {str(e)}"
            }

    async def list_business_intelligences(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List business_intelligences with pagination"""
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            cursor = self._get_collection("default").find(query).skip(offset).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            # Remove MongoDB _id field
            for doc in docs:
                doc.pop('_id', None)
            
            total_count = await self._get_collection("default").count_documents(query)
            
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
                "error": f"Failed to list business_intelligences: {str(e)}"
            }

    async def update_business_intelligence(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update business_intelligence by ID"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self._get_collection("default").update_one(
                {"id": item_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"Business Intelligence not found"
                }
            
            # Get updated document
            updated_doc = await self._get_collection("default").find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Business Intelligence updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update business_intelligence: {str(e)}"
            }

    async def delete_business_intelligence(self, item_id: str) -> Dict[str, Any]:
        """Delete business_intelligence by ID"""
        try:
            result = await self._get_collection("default").delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Business Intelligence not found"
                }
            
            return {
                "success": True,
                "message": f"Business Intelligence deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete business_intelligence: {str(e)}"
            }

    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics for business_intelligences"""
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            total_count = await self._get_collection("default").count_documents(query)
            active_count = await self._get_collection("default").count_documents({**query, "status": "active"})
            
            return {
                "success": True,
                "data": {
                    "total_count": total_count,
                    "active_count": active_count,
                    "service": "business_intelligence",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get business_intelligence stats: {str(e)}"
            }

# Service instance
_business_intelligence_service = None

def get_business_intelligence_service():
    """Get business_intelligence service instance"""
    global _business_intelligence_service
    if _business_intelligence_service is None:
        _business_intelligence_service = BusinessIntelligenceService()
    return _business_intelligence_service

# For backward compatibility
business_intelligence_service = get_business_intelligence_service()