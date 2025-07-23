"""
Complete Social Media Leads Service
Complete CRUD operations for complete_social_media_leads
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class CompleteSocialMediaLeadsService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["completesocialmedialeads"]

    async def create_complete_social_media_leads(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new complete_social_media_leads"""
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
                "message": f"Complete Social Media Leads created successfully",
                "data": data,
                "id": data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create complete_social_media_leads: {str(e)}"
            }

    async def get_complete_social_media_leads(self, item_id: str) -> Dict[str, Any]:
        """Get complete_social_media_leads by ID"""
        try:
            doc = await self.collection.find_one({"id": item_id})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"Complete Social Media Leads not found"
                }
            
            doc.pop('_id', None)
            return {
                "success": True,
                "data": doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get complete_social_media_leads: {str(e)}"
            }

    async def list_complete_social_media_leadss(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List complete_social_media_leadss with pagination"""
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
                "error": f"Failed to list complete_social_media_leadss: {str(e)}"
            }

    async def update_complete_social_media_leads(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update complete_social_media_leads by ID"""
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
                    "error": f"Complete Social Media Leads not found"
                }
            
            # Get updated document
            updated_doc = await self.collection.find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Complete Social Media Leads updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update complete_social_media_leads: {str(e)}"
            }

    async def delete_complete_social_media_leads(self, item_id: str) -> Dict[str, Any]:
        """Delete complete_social_media_leads by ID"""
        try:
            result = await self.collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Complete Social Media Leads not found"
                }
            
            return {
                "success": True,
                "message": f"Complete Social Media Leads deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete complete_social_media_leads: {str(e)}"
            }

    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics for complete_social_media_leadss"""
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
                    "service": "complete_social_media_leads",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get complete_social_media_leads stats: {str(e)}"
            }

# Service instance
_complete_social_media_leads_service = None

def get_complete_social_media_leads_service():
    """Get complete_social_media_leads service instance"""
    global _complete_social_media_leads_service
    if _complete_social_media_leads_service is None:
        _complete_social_media_leads_service = CompleteSocialMediaLeadsService()
    return _complete_social_media_leads_service

# For backward compatibility
complete_social_media_leads_service = get_complete_social_media_leads_service()