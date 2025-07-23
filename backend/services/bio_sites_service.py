"""
Bio Sites Service
Complete CRUD operations for bio_sites
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class BioSitesService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["biosites"]

    async def create_bio_sites(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new bio_sites"""
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
                "message": f"Bio Sites created successfully",
                "data": data,
                "id": data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create bio_sites: {str(e)}"
            }

    async def get_bio_sites(self, item_id: str) -> Dict[str, Any]:
        """Get bio_sites by ID"""
        try:
            doc = await self.collection.find_one({"id": item_id})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"Bio Sites not found"
                }
            
            doc.pop('_id', None)
            return {
                "success": True,
                "data": doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get bio_sites: {str(e)}"
            }

    async def list_bio_sitess(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List bio_sitess with pagination"""
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
                "error": f"Failed to list bio_sitess: {str(e)}"
            }

    async def update_bio_sites(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update bio_sites by ID"""
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
                    "error": f"Bio Sites not found"
                }
            
            # Get updated document
            updated_doc = await self.collection.find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Bio Sites updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update bio_sites: {str(e)}"
            }

    async def delete_bio_sites(self, item_id: str) -> Dict[str, Any]:
        """Delete bio_sites by ID"""
        try:
            result = await self.collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Bio Sites not found"
                }
            
            return {
                "success": True,
                "message": f"Bio Sites deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete bio_sites: {str(e)}"
            }

    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics for bio_sitess"""
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
                    "service": "bio_sites",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get bio_sites stats: {str(e)}"
            }

# Service instance
_bio_sites_service = None

def get_bio_sites_service():
    """Get bio_sites service instance"""
    global _bio_sites_service
    if _bio_sites_service is None:
        _bio_sites_service = BioSitesService()
    return _bio_sites_service

# For backward compatibility
bio_sites_service = get_bio_sites_service()