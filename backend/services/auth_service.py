"""
Auth Service
Auto-generated to complete service/API pairing
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class AuthService:
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

    async def create_auth(self, auth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new auth"""
        try:
            # Add metadata
            auth_data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            # Save to database
            result = await self._get_db()["auth"].insert_one(auth_data)
            
            return {
                "success": True,
                "message": f"Auth created successfully",
                "data": auth_data,
                "id": auth_data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create auth: {str(e)}"
            }

    async def get_auth(self, auth_id: str) -> Dict[str, Any]:
        """Get auth by ID"""
        try:
            result = await self._get_db()["auth"].find_one({"id": auth_id})
            
            if not result:
                return {
                    "success": False,
                    "error": f"Auth not found"
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
                "error": f"Failed to get auth: {str(e)}"
            }

    async def list_auth(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List all auth"""
        try:
            cursor = self._get_db()["auth"].find({}).skip(offset).limit(limit)
            results = await cursor.to_list(length=limit)
            
            # Remove MongoDB _id from all results
            for result in results:
                result.pop('_id', None)
            
            total_count = await self._get_db()["auth"].count_documents({})
            
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
                "error": f"Failed to list auth: {str(e)}"
            }

    async def update_auth(self, auth_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update auth by ID"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self._get_db()["auth"].update_one(
                {"id": auth_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"Auth not found"
                }
            
            # Get updated document
            updated_doc = await self._get_db()["auth"].find_one({"id": auth_id})
            updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Auth updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update auth: {str(e)}"
            }

    async def delete_auth(self, auth_id: str) -> Dict[str, Any]:
        """Delete auth by ID"""
        try:
            result = await self._get_db()["auth"].delete_one({"id": auth_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Auth not found"
                }
            
            return {
                "success": True,
                "message": f"Auth deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete auth: {str(e)}"
            }
