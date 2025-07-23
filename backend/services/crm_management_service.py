"""
crm_management Service
Provides business logic for Crm Management
"""

import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from core.database import get_database

class CrmManagementService:
    """Service class for Crm Management"""

    async def create_crm_management(self, crm_management_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create crm_management with real data persistence"""
        try:
            import uuid
            from datetime import datetime
            
            crm_management_data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            db = await self.get_database()
            result = await db["crm_management"].insert_one(crm_management_data)
            
            return {
                "success": True,
                "message": f"Crm_Management created successfully",
                "data": crm_management_data,
                "id": crm_management_data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create crm_management: {str(e)}"
            }

    async def delete_crm_management(self, crm_management_id: str) -> Dict[str, Any]:
        """Delete crm_management with real data persistence"""
        try:
            db = await self.get_database()
            result = await db["crm_management"].delete_one({"id": crm_management_id})
            
            if result.deleted_count == 0:
                return {"success": False, "error": f"Crm_Management not found"}
            
            return {
                "success": True,
                "message": f"Crm_Management deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to delete crm_management: {str(e)}"}



    async def update_crm_management(self, crm_management_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update crm_management with real data persistence"""
        try:
            from datetime import datetime
            
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            db = await self.get_database()
            result = await db["crm_management"].update_one(
                {"id": crm_management_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": f"Crm_Management not found"}
            
            updated = await db["crm_management"].find_one({"id": crm_management_id})
            updated.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Crm_Management updated successfully",
                "data": updated
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to update crm_management: {str(e)}"}

    

    async def create_crm_management(self, crm_management_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new crm_management"""
        try:
            # Add metadata
            crm_management_data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            # Save to database
            result = await self.db["crm_management"].insert_one(crm_management_data)
            
            return {
                "success": True,
                "message": f"Crm_Management created successfully",
                "data": crm_management_data,
                "id": crm_management_data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create crm_management: {str(e)}"
            }

    def __init__(self):
        self.db = get_database()
        self.collection = self.db["crm_management"]
    
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

    async def update_crm_management(self, crm_management_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update crm_management by ID"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self.db["crm_management"].update_one(
                {"id": crm_management_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"Crm_Management not found"
                }
            
            # Get updated document
            updated_doc = await self.db["crm_management"].find_one({"id": crm_management_id})
            updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Crm_Management updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update crm_management: {str(e)}"
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
    

    async def delete_crm_management(self, crm_management_id: str) -> Dict[str, Any]:
        """Delete crm_management by ID"""
        try:
            result = await self.db["crm_management"].delete_one({"id": crm_management_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Crm_Management not found"
                }
            
            return {
                "success": True,
                "message": f"Crm_Management deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete crm_management: {str(e)}"
            }

    async def get_stats(self, user_id: str) -> Dict[str, Any]:
        """Get statistics"""
        total = await self.collection.count_documents({"user_id": user_id})
        
        return {
            "total_records": total,
            "service": "crm_management",
            "last_updated": datetime.utcnow().isoformat()
        }

# Service instance
crm_management_service = CrmManagementService()

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