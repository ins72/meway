"""
i18n_system Service
Provides business logic for I18N System
"""

import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from core.database import get_database

class I18nSystemService:
    """Service class for I18N System"""
    

    async def create_i18n_system(self, i18n_system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new i18n_system"""
        try:
            # Add metadata
            i18n_system_data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            # Save to database
            result = await self.db["i18n_system"].insert_one(i18n_system_data)
            
            return {
                "success": True,
                "message": f"I18N_System created successfully",
                "data": i18n_system_data,
                "id": i18n_system_data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create i18n_system: {str(e)}"
            }

    def __init__(self):
        self.db = get_database()
        self.collection = self.db["i18n_system"]
    
    async def get_all(self, user_id: str, limit: int = 20, skip: int = 0) -> List[Dict[str, Any]]:
        """Get all records for user"""
        cursor = self.collection.find(
            {"user_id": user_id},
            limit=limit,
            skip=skip,
            sort=[("created_at", -1)]
        )
        return await cursor.to_list(length=limit)
    
    async def get_by_id(self, user_id: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Get record by ID"""
        return await self.collection.find_one({
            "id": record_id,
            "user_id": user_id
        })
    
    async def create(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new record"""
        record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,

    async def update_i18n_system(self, i18n_system_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update i18n_system by ID"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self.db["i18n_system"].update_one(
                {"id": i18n_system_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"I18N_System not found"
                }
            
            # Get updated document
            updated_doc = await self.db["i18n_system"].find_one({"id": i18n_system_id})
            updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"I18N_System updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update i18n_system: {str(e)}"
            }

            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            **data
        }
        
        await self.collection.insert_one(record)
        return record
    
    async def update(self, user_id: str, record_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing record"""
        update_data = {
            **data,
            "updated_at": datetime.utcnow()
        }
        
        result = await self.collection.find_one_and_update(
            {"id": record_id, "user_id": user_id},
            {"$set": update_data},
            return_document=True
        )
        
        return result
    
    async def delete(self, user_id: str, record_id: str) -> bool:
        """Delete record"""
        result = await self.collection.delete_one({
            "id": record_id,
            "user_id": user_id
        })
        
        return result.deleted_count > 0
    

    async def delete_i18n_system(self, i18n_system_id: str) -> Dict[str, Any]:
        """Delete i18n_system by ID"""
        try:
            result = await self.db["i18n_system"].delete_one({"id": i18n_system_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"I18N_System not found"
                }
            
            return {
                "success": True,
                "message": f"I18N_System deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete i18n_system: {str(e)}"
            }

    async def get_stats(self, user_id: str) -> Dict[str, Any]:
        """Get statistics"""
        total = await self.collection.count_documents({"user_id": user_id})
        
        return {
            "total_records": total,
            "service": "i18n_system",
            "last_updated": datetime.utcnow().isoformat()
        }

# Service instance
i18n_system_service = I18nSystemService()

    async def get_item(self, user_id: str, item_id: str):
        """Get specific item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            item = await collections['items'].find_one({
                "_id": item_id,
                "user_id": user_id
            })
            
            if not item:
                return {"success": False, "message": "Item not found"}
            
            return {
                "success": True,
                "data": item,
                "message": "Item retrieved successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def list_items(self, user_id: str, filters: dict = None, page: int = 1, limit: int = 50):
        """List user's items"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            query = {"user_id": user_id}
            if filters:
                query.update(filters)
            
            skip = (page - 1) * limit
            
            cursor = collections['items'].find(query).skip(skip).limit(limit)
            items = await cursor.to_list(length=limit)
            
            total_count = await collections['items'].count_documents(query)
            
            return {
                "success": True,
                "data": {
                    "items": items,
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total_count,
                        "pages": (total_count + limit - 1) // limit
                    }
                },
                "message": "Items retrieved successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}