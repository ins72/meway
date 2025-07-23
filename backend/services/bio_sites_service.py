"""
Bio Sites Services Business Logic
Professional Mewayz Platform
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database
import uuid

class BioSitesService:
    """Service for bio sites operations"""
    
    @staticmethod
    async def get_bio_site(user_id: str):
        """Get user's bio site"""
        db = await get_database()
        
        bio_site = await db.bio_sites.find_one({"user_id": user_id})
        if not bio_site:
            # Create default bio site
            bio_site = {
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": "My Bio",
                "bio": "Welcome to my bio site!",
                "links": [],
                "theme": "modern",
                "is_published": False,
                "created_at": datetime.utcnow()
            }
            await db.bio_sites.insert_one(bio_site)
        
        return bio_site
    
    @staticmethod
    async def update_bio_site(user_id: str, site_data: Dict[str, Any]):
        """Update user's bio site"""
        db = await get_database()
        
        update_data = {
            "title": site_data.get("title"),
            "bio": site_data.get("bio"),
            "links": site_data.get("links", []),
            "theme": site_data.get("theme", "modern"),
            "is_published": site_data.get("is_published", False),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.bio_sites.update_one(
            {"user_id": user_id},
            {"$set": update_data},
            upsert=True
        )
        
        return await db.bio_sites.find_one({"user_id": user_id})

# Global service instance
bio_sites_service = BioSitesService()

    async def create_item(self, user_id: str, item_data: dict):
        """Create new item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            new_item = {
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                **item_data,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "status": "active"
            }
            
            await collections['items'].insert_one(new_item)
            
            return {
                "success": True,
                "data": new_item,
                "message": "Item created successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

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

    async def delete_item(self, user_id: str, item_id: str):
        """Delete item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            result = await collections['items'].delete_one({
                "_id": item_id,
                "user_id": user_id
            })
            
            if result.deleted_count == 0:
                return {"success": False, "message": "Item not found"}
            
            return {
                "success": True,
                "message": "Item deleted successfully"
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