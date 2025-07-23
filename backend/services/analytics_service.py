"""
Analytics Service
Auto-generated to complete service/API pairing
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class AnalyticsService:
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

    async def create_analytic(self, analytic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new analytic"""
        try:
            # Add metadata
            analytic_data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            # Save to database
            result = await self._get_db()["analytics"].insert_one(analytic_data)
            
            return {
                "success": True,
                "message": f"Analytic created successfully",
                "data": analytic_data,
                "id": analytic_data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create analytic: {str(e)}"
            }

    async def get_analytic(self, analytic_id: str) -> Dict[str, Any]:
        """Get analytic by ID"""
        try:
            result = await self._get_db()["analytics"].find_one({"id": analytic_id})
            
            if not result:
                return {
                    "success": False,
                    "error": f"Analytic not found"
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
                "error": f"Failed to get analytic: {str(e)}"
            }

    async def list_analytics(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List all analytics"""
        try:
            cursor = self._get_db()["analytics"].find({}).skip(offset).limit(limit)
            results = await cursor.to_list(length=limit)
            
            # Remove MongoDB _id from all results
            for result in results:
                result.pop('_id', None)
            
            total_count = await self._get_db()["analytics"].count_documents({})
            
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
                "error": f"Failed to list analytics: {str(e)}"
            }

    async def update_analytic(self, analytic_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update analytic by ID"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self._get_db()["analytics"].update_one(
                {"id": analytic_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"Analytic not found"
                }
            
            # Get updated document
            updated_doc = await self._get_db()["analytics"].find_one({"id": analytic_id})
            updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Analytic updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update analytic: {str(e)}"
            }

    async def delete_analytic(self, analytic_id: str) -> Dict[str, Any]:
        """Delete analytic by ID"""
        try:
            result = await self._get_db()["analytics"].delete_one({"id": analytic_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Analytic not found"
                }
            
            return {
                "success": True,
                "message": f"Analytic deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete analytic: {str(e)}"
            }

# Service instance
_analytics_service = None

def get_analytics_service():
    """Get analytics service instance"""
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
    return _analytics_service
