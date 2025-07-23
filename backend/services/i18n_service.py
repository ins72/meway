"""
I18N Service
Complete CRUD operations for i18n
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class I18nService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["i18n"]

    async def create_i18n(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new i18n"""
        try:
            # Add metadata
            data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            # Save to database
            result = await self.collection.insert_one(data)
            
            return {
                "success": True,
                "message": f"I18N created successfully",
                "data": data,
                "id": data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create i18n: {str(e)}"
            }

    async def get_i18n(self, item_id: str) -> Dict[str, Any]:
        """Get i18n by ID"""
        try:
            doc = await self.collection.find_one({"id": item_id})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"I18N not found"
                }
            
            doc.pop('_id', None)
            return {
                "success": True,
                "data": doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get i18n: {str(e)}"
            }

    async def list_i18ns(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List i18ns with pagination"""
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            cursor = self.collection.find(query).skip(offset).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            # Remove MongoDB _id field
            for doc in docs:
                doc.pop('_id', None)
            
            total_count = await self.collection.count_documents(query)
            
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
                "error": f"Failed to list i18ns: {str(e)}"
            }

    async def update_i18n(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update i18n by ID"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self.collection.update_one(
                {"id": item_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"I18N not found"
                }
            
            # Get updated document
            updated_doc = await self.collection.find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"I18N updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update i18n: {str(e)}"
            }

    async def delete_i18n(self, item_id: str) -> Dict[str, Any]:
        """Delete i18n by ID"""
        try:
            result = await self.collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"I18N not found"
                }
            
            return {
                "success": True,
                "message": f"I18N deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete i18n: {str(e)}"
            }

    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics for i18ns"""
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            total_count = await self.collection.count_documents(query)
            active_count = await self.collection.count_documents({**query, "status": "active"})
            
            return {
                "success": True,
                "data": {
                    "total_count": total_count,
                    "active_count": active_count,
                    "service": "i18n",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get i18n stats: {str(e)}"
            }

# Service instance
_i18n_service = None

def get_i18n_service():
    """Get i18n service instance"""
    global _i18n_service
    if _i18n_service is None:
        _i18n_service = I18nService()
    return _i18n_service

# For backward compatibility
i18n_service = get_i18n_service()