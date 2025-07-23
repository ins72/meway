"""
Social Email Integration Service
Complete CRUD operations for social_email_integration
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class SocialEmailIntegrationService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["socialemailintegration"]

    async def create_social_email_integration(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new social_email_integration"""
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
                "message": f"Social Email Integration created successfully",
                "data": data,
                "id": data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create social_email_integration: {str(e)}"
            }

    async def get_social_email_integration(self, item_id: str) -> Dict[str, Any]:
        """Get social_email_integration by ID"""
        try:
            doc = await self.collection.find_one({"id": item_id})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"Social Email Integration not found"
                }
            
            doc.pop('_id', None)
            return {
                "success": True,
                "data": doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get social_email_integration: {str(e)}"
            }

    async def list_social_email_integrations(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List social_email_integrations with pagination"""
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
                "error": f"Failed to list social_email_integrations: {str(e)}"
            }

    async def update_social_email_integration(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update social_email_integration by ID"""
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
                    "error": f"Social Email Integration not found"
                }
            
            # Get updated document
            updated_doc = await self.collection.find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Social Email Integration updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update social_email_integration: {str(e)}"
            }

    async def delete_social_email_integration(self, item_id: str) -> Dict[str, Any]:
        """Delete social_email_integration by ID"""
        try:
            result = await self.collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Social Email Integration not found"
                }
            
            return {
                "success": True,
                "message": f"Social Email Integration deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete social_email_integration: {str(e)}"
            }

    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics for social_email_integrations"""
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
                    "service": "social_email_integration",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get social_email_integration stats: {str(e)}"
            }

# Service instance
_social_email_integration_service = None

def get_social_email_integration_service():
    """Get social_email_integration service instance"""
    global _social_email_integration_service
    if _social_email_integration_service is None:
        _social_email_integration_service = SocialEmailIntegrationService()
    return _social_email_integration_service

# For backward compatibility
social_email_integration_service = get_social_email_integration_service()