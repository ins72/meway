"""
Ai Token Management Service
Complete CRUD operations for ai_token_management
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class AiTokenManagementService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["aitokenmanagement"]

    async def create_ai_token_management(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new ai_token_management"""
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
                "message": f"Ai Token Management created successfully",
                "data": data,
                "id": data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create ai_token_management: {str(e)}"
            }

    async def get_ai_token_management(self, item_id: str) -> Dict[str, Any]:
        """Get ai_token_management by ID"""
        try:
            doc = await self.collection.find_one({"id": item_id})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"Ai Token Management not found"
                }
            
            doc.pop('_id', None)
            return {
                "success": True,
                "data": doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get ai_token_management: {str(e)}"
            }

    async def list_ai_token_managements(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List ai_token_managements with pagination"""
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
                "error": f"Failed to list ai_token_managements: {str(e)}"
            }

    async def update_ai_token_management(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update ai_token_management by ID"""
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
                    "error": f"Ai Token Management not found"
                }
            
            # Get updated document
            updated_doc = await self.collection.find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Ai Token Management updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update ai_token_management: {str(e)}"
            }

    async def delete_ai_token_management(self, item_id: str) -> Dict[str, Any]:
        """Delete ai_token_management by ID"""
        try:
            result = await self.collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Ai Token Management not found"
                }
            
            return {
                "success": True,
                "message": f"Ai Token Management deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete ai_token_management: {str(e)}"
            }

    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics for ai_token_managements"""
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
                    "service": "ai_token_management",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get ai_token_management stats: {str(e)}"
            }

# Service instance
_ai_token_management_service = None

def get_ai_token_management_service():
    """Get ai_token_management service instance"""
    global _ai_token_management_service
    if _ai_token_management_service is None:
        _ai_token_management_service = AiTokenManagementService()
    return _ai_token_management_service

# For backward compatibility
ai_token_management_service = get_ai_token_management_service()