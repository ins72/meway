"""
Import Api Service - Real Implementation
Professional service with complete CRUD operations and real data persistence
"""

import uuid
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from core.database import get_database_async
from core.objectid_serializer import safe_document_return, safe_documents_return

logger = logging.getLogger(__name__)

class ImportapiService:
    """Professional service for import api operations"""
    
    def __init__(self):
        self.collection_name = "import_api"
    
    async def _get_collection_async(self):
        """Get MongoDB collection"""
        try:
            db = await get_database_async()
            if db is not None:
                return db[self.collection_name]
            return None
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return None
    
    async def create(self, data: dict, user_id: str = None) -> dict:
        """Create new import api - Real data operation"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            # Create real data record
            item_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                **data,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            result = await collection.insert_one(item_data)
            
            if result.inserted_id:
                item_data["_id"] = result.inserted_id
                return {
                    "success": True,
                    "data": safe_document_return(item_data),
                    "message": "Import Api created successfully"
                }
            else:
                return {"success": False, "error": "Creation failed"}
                
        except Exception as e:
            logger.error(f"Create import_api error: {e}")
            return {"success": False, "error": str(e)}
    
    async def list(self, user_id: str = None, limit: int = 50, offset: int = 0) -> dict:
        """List import api items - Real data operation"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            # Build query
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            # Execute query with real data
            cursor = collection.find(query).skip(offset).limit(limit)
            items = await cursor.to_list(length=limit)
            
            # Convert ObjectIds to strings
            items = safe_documents_return(items)
            
            # Get total count
            total = await collection.count_documents(query)
            
            return {
                "success": True,
                "data": items,
                "total": total,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"List import_api error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get(self, item_id: str, user_id: str = None) -> dict:
        """Get single import api - Real data operation"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            # Build query
            query = {"id": item_id}
            if user_id:
                query["user_id"] = user_id
            
            # Find item
            item = await collection.find_one(query)
            
            if item:
                return {
                    "success": True,
                    "data": safe_document_return(item)
                }
            else:
                return {"success": False, "error": "Import Api not found"}
                
        except Exception as e:
            logger.error(f"Get import_api error: {e}")
            return {"success": False, "error": str(e)}
    
    async def update(self, item_id: str, data: dict, user_id: str = None) -> dict:
        """Update import api - Real data operation"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            # Build query
            query = {"id": item_id}
            if user_id:
                query["user_id"] = user_id
            
            # Prepare update data
            update_data = {
                **data,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Update item
            result = await collection.update_one(
                query,
                {"$set": update_data}
            )
            
            if result.matched_count > 0:
                # Get updated item
                updated_item = await collection.find_one(query)
                return {
                    "success": True,
                    "data": safe_document_return(updated_item),
                    "message": "Import Api updated successfully"
                }
            else:
                return {"success": False, "error": "Import Api not found"}
                
        except Exception as e:
            logger.error(f"Update import_api error: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete(self, item_id: str, user_id: str = None) -> dict:
        """Delete import api - Real data operation"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            # Build query
            query = {"id": item_id}
            if user_id:
                query["user_id"] = user_id
            
            # Delete item
            result = await collection.delete_one(query)
            
            if result.deleted_count > 0:
                return {
                    "success": True,
                    "message": "Import Api deleted successfully"
                }
            else:
                return {"success": False, "error": "Import Api not found"}
                
        except Exception as e:
            logger.error(f"Delete import_api error: {e}")
            return {"success": False, "error": str(e)}

# Service instance getter
_service_instance = None

def get_import_api_service():
    """Get service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = ImportapiService()
    return _service_instance
