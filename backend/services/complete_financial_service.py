"""
Complete Financial Service
Complete CRUD operations for complete_financial
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class CompleteFinancialService:
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
        self.collection = self._get_db()["completefinancial"]

    async def create_complete_financial(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new complete_financial"""
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
                "message": f"Complete Financial created successfully",
                "data": data,
                "id": data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create complete_financial: {str(e)}"
            }

    async def get_complete_financial(self, item_id: str) -> Dict[str, Any]:
        """Get complete_financial by ID"""
        try:
            doc = await self._get_collection("default").find_one({"id": item_id})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"Complete Financial not found"
                }
            
            doc.pop('_id', None)
            return {
                "success": True,
                "data": doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get complete_financial: {str(e)}"
            }

    async def list_complete_financials(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List complete_financials with pagination"""
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
                "error": f"Failed to list complete_financials: {str(e)}"
            }

    async def update_complete_financial(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update complete_financial by ID"""
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
                    "error": f"Complete Financial not found"
                }
            
            # Get updated document
            updated_doc = await self._get_collection("default").find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Complete Financial updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update complete_financial: {str(e)}"
            }

    async def delete_complete_financial(self, item_id: str) -> Dict[str, Any]:
        """Delete complete_financial by ID"""
        try:
            result = await self._get_collection("default").delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Complete Financial not found"
                }
            
            return {
                "success": True,
                "message": f"Complete Financial deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete complete_financial: {str(e)}"
            }

    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics for complete_financials"""
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
                    "service": "complete_financial",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get complete_financial stats: {str(e)}"
            }

# Service instance
_complete_financial_service = None

def get_complete_financial_service():
    """Get complete_financial service instance"""
    global _complete_financial_service
    if _complete_financial_service is None:
        _complete_financial_service = CompleteFinancialService()
    return _complete_financial_service

# For backward compatibility
complete_financial_service = get_complete_financial_service()