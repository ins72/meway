"""
Form Builder Service
Complete CRUD operations for form_builder
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class FormBuilderService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["formbuilder"]

    async def create_form_builder(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new form_builder"""
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
                "message": f"Form Builder created successfully",
                "data": data,
                "id": data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create form_builder: {str(e)}"
            }

    async def get_form_builder(self, item_id: str) -> Dict[str, Any]:
        """Get form_builder by ID"""
        try:
            doc = await self.collection.find_one({"id": item_id})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"Form Builder not found"
                }
            
            doc.pop('_id', None)
            return {
                "success": True,
                "data": doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get form_builder: {str(e)}"
            }

    async def list_form_builders(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List form_builders with pagination"""
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
                "error": f"Failed to list form_builders: {str(e)}"
            }

    async def update_form_builder(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update form_builder by ID"""
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
                    "error": f"Form Builder not found"
                }
            
            # Get updated document
            updated_doc = await self.collection.find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Form Builder updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update form_builder: {str(e)}"
            }

    async def delete_form_builder(self, item_id: str) -> Dict[str, Any]:
        """Delete form_builder by ID"""
        try:
            result = await self.collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Form Builder not found"
                }
            
            return {
                "success": True,
                "message": f"Form Builder deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete form_builder: {str(e)}"
            }

    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics for form_builders"""
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
                    "service": "form_builder",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get form_builder stats: {str(e)}"
            }

# Service instance
_form_builder_service = None

def get_form_builder_service():
    """Get form_builder service instance"""
    global _form_builder_service
    if _form_builder_service is None:
        _form_builder_service = FormBuilderService()
    return _form_builder_service

# For backward compatibility
form_builder_service = get_form_builder_service()