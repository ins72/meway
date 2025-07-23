"""
Unified_Analytics_Gamification Service
Auto-generated to complete service/API pairing
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class Unified_Analytics_GamificationService:
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

    async def create_unified_analytics_gamification(self, unified_analytics_gamification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new unified_analytics_gamification"""
        try:
            # Add metadata
            unified_analytics_gamification_data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            # Save to database
            result = await self._get_db()["unified_analytics_gamification"].insert_one(unified_analytics_gamification_data)
            
            return {
                "success": True,
                "message": f"Unified_Analytics_Gamification created successfully",
                "data": unified_analytics_gamification_data,
                "id": unified_analytics_gamification_data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create unified_analytics_gamification: {str(e)}"
            }

    async def get_unified_analytics_gamification(self, unified_analytics_gamification_id: str) -> Dict[str, Any]:
        """Get unified_analytics_gamification by ID"""
        try:
            result = await self._get_db()["unified_analytics_gamification"].find_one({"id": unified_analytics_gamification_id})
            
            if not result:
                return {
                    "success": False,
                    "error": f"Unified_Analytics_Gamification not found"
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
                "error": f"Failed to get unified_analytics_gamification: {str(e)}"
            }

    async def list_unified_analytics_gamification(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List all unified_analytics_gamification"""
        try:
            cursor = self._get_db()["unified_analytics_gamification"].find({}).skip(offset).limit(limit)
            results = await cursor.to_list(length=limit)
            
            # Remove MongoDB _id from all results
            for result in results:
                result.pop('_id', None)
            
            total_count = await self._get_db()["unified_analytics_gamification"].count_documents({})
            
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
                "error": f"Failed to list unified_analytics_gamification: {str(e)}"
            }

    async def update_unified_analytics_gamification(self, unified_analytics_gamification_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update unified_analytics_gamification by ID"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self._get_db()["unified_analytics_gamification"].update_one(
                {"id": unified_analytics_gamification_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"Unified_Analytics_Gamification not found"
                }
            
            # Get updated document
            updated_doc = await self._get_db()["unified_analytics_gamification"].find_one({"id": unified_analytics_gamification_id})
            updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Unified_Analytics_Gamification updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update unified_analytics_gamification: {str(e)}"
            }

    async def delete_unified_analytics_gamification(self, unified_analytics_gamification_id: str) -> Dict[str, Any]:
        """Delete unified_analytics_gamification by ID"""
        try:
            result = await self._get_db()["unified_analytics_gamification"].delete_one({"id": unified_analytics_gamification_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Unified_Analytics_Gamification not found"
                }
            
            return {
                "success": True,
                "message": f"Unified_Analytics_Gamification deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete unified_analytics_gamification: {str(e)}"
            }
