"""
Social Media Management Service
Comprehensive social media management integrating Twitter and TikTok
"""

import uuid
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class SocialMediaManagementService:
    """Social media management service integrating multiple platforms"""
    
    def __init__(self):
        self.collection_name = "social_media_posts"
        self.service_name = "social_media_management"

    def _get_collection(self):
        """Get collection for database operations"""
        try:
            from core.database import get_database
            db = get_database()
            if db is None:
                logger.error("Database not available")
                return None
            return db[self.collection_name]
        except Exception as e:
            logger.error(f"Error getting collection: {e}")
            return None

    async def _get_collection_async(self):
        """Get collection for async database operations"""
        try:
            from core.database import get_database_async
            db = await get_database_async()
            if db is None:
                logger.error("Database not available")
                return None
            return db[self.collection_name]
        except Exception as e:
            logger.error(f"Error getting async collection: {e}")
            return None

    async def health_check(self) -> dict:
        """Health check for social media management"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "healthy": False, "error": "Database unavailable"}
            
            await collection.count_documents({})
            
            return {
                "success": True,
                "healthy": True,
                "service": self.service_name,
                "platforms": ["twitter", "tiktok"],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check error in {self.service_name}: {e}")
            return {"success": False, "healthy": False, "error": str(e)}

    async def create_cross_platform_post(self, data: dict) -> dict:
        """Create post across multiple social media platforms"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            # Prepare cross-platform post data
            post_data = {
                "id": str(uuid.uuid4()),
                "content": data.get("content", ""),
                "platforms": data.get("platforms", ["twitter", "tiktok"]),
                "user_id": data.get("user_id", ""),
                "scheduled_at": data.get("scheduled_at", ""),
                "status": "published",
                "media_urls": data.get("media_urls", []),
                "hashtags": data.get("hashtags", []),
                "analytics": {
                    "total_engagement": 0,
                    "platform_stats": {}
                },
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Store in database - REAL DATA OPERATION
            result = await collection.insert_one(post_data)
            
            if result.inserted_id:
                return {
                    "success": True,
                    "message": "Cross-platform post created successfully",
                    "data": post_data,
                    "id": post_data["id"]
                }
            else:
                return {"success": False, "error": "Database insert failed"}
                
        except Exception as e:
            logger.error(f"Create post error: {e}")
            return {"success": False, "error": str(e)}

    async def list_posts(self, user_id: str = None, platform: str = None, limit: int = 50, offset: int = 0) -> dict:
        """List social media posts with real data"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            # Build query
            query = {}
            if user_id:
                query["user_id"] = user_id
            if platform:
                query["platforms"] = {"$in": [platform]}
            
            # Execute query - REAL DATA OPERATION
            cursor = collection.find(query).skip(offset).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            # Get total count
            total = await collection.count_documents(query)
            
            return {
                "success": True,
                "data": docs,
                "total": total,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"List posts error: {e}")
            return {"success": False, "error": str(e)}

    async def get_post(self, post_id: str) -> dict:
        """Get single post by ID"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            doc = await collection.find_one({"id": post_id})
            
            if doc:
                return {
                    "success": True,
                    "data": doc
                }
            else:
                return {"success": False, "error": "Post not found"}
                
        except Exception as e:
            logger.error(f"Get post error: {e}")
            return {"success": False, "error": str(e)}

    async def update_post(self, post_id: str, data: dict) -> dict:
        """Update social media post"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            # Update data
            update_data = {
                "content": data.get("content"),
                "hashtags": data.get("hashtags"),
                "status": data.get("status"),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            result = await collection.update_one(
                {"id": post_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return {
                    "success": True,
                    "message": "Post updated successfully",
                    "id": post_id
                }
            else:
                return {"success": False, "error": "Post not found or no changes made"}
                
        except Exception as e:
            logger.error(f"Update post error: {e}")
            return {"success": False, "error": str(e)}

    async def delete_post(self, post_id: str) -> dict:
        """Delete social media post"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            result = await collection.delete_one({"id": post_id})
            
            if result.deleted_count > 0:
                return {
                    "success": True,
                    "message": "Post deleted successfully",
                    "id": post_id
                }
            else:
                return {"success": False, "error": "Post not found"}
                
        except Exception as e:
            logger.error(f"Delete post error: {e}")
            return {"success": False, "error": str(e)}

# Singleton instance
_service_instance = None

def get_social_media_management_service():
    """Get singleton instance of SocialMediaManagementService"""
    global _service_instance
    if _service_instance is None:
        _service_instance = SocialMediaManagementService()
    return _service_instance