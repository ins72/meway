"""
Blog/Content Services Business Logic
Professional Mewayz Platform
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database
import uuid
import re

class BlogService:
    """Service for blog and content operations"""
    
    @staticmethod
    def generate_slug(title: str) -> str:
        """Generate URL-friendly slug from title"""
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s-]+', '-', slug)
        return slug.strip('-')
    
    @staticmethod
    async def get_blog_posts(user_id: str, published_only: bool = False):
        """Get user's blog posts"""
        db = await get_database()
        
        query = {"user_id": user_id}
        if published_only:
            query["status"] = "published"
        
        posts = await db.blog_posts.find(query).sort("created_at", -1).to_list(length=None)
        return posts
    
    @staticmethod
    async def create_blog_post(user_id: str, post_data: Dict[str, Any]):
        """Create new blog post"""
        db = await get_database()
        
        slug = BlogService.generate_slug(post_data.get("title", ""))
        
        post = {
    "_id": str(uuid.uuid4()),
    "user_id": user_id,
    "title": post_data.get("title"),
    "slug": slug,
    "content": post_data.get("content", ""),
    "excerpt": post_data.get("excerpt", ""),
    "featured_image": post_data.get("featured_image"),
    "categories": post_data.get("categories", []),
    "tags": post_data.get("tags", []),
    "status": post_data.get("status", "draft"),
    "seo": {
    "meta_title": post_data.get("meta_title"),
    "meta_description": post_data.get("meta_description"),
    "og_image": post_data.get("og_image")
    },
    "view_count": 0,
    "like_count": 0,
    "comment_count": 0,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
            "published_at": datetime.utcnow() if post_data.get("status") == "published" else None
    }
        
        result = await db.blog_posts.insert_one(post)
        return post
    
    @staticmethod
    async def get_post_by_slug(slug: str, user_id: str = None):
        """Get blog post by slug"""
        db = await get_database()
        
        query = {"slug": slug}
        if user_id:
            query["user_id"] = user_id
        
        post = await db.blog_posts.find_one(query)
        return post
    
    @staticmethod
    async def get_blog_categories(user_id: str):
        """Get blog categories for user"""
        db = await get_database()
        
        # Aggregate categories from posts
        pipeline = [
    {"$match": {"user_id": user_id}},
    {"$unwind": "$categories"},
    {"$group": {"_id": "$categories", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
    ]
        
        categories = await db.blog_posts.aggregate(pipeline).to_list(length=None)
        return [{"name": cat["_id"], "count": cat["count"]} for cat in categories]

    async def update_blog(self, blog_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update blog with real data persistence"""
        try:
            from datetime import datetime
            
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            db = await self.get_database()
            result = await db["blog"].update_one(
                {"id": blog_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": f"Blog not found"}
            
            updated = await db["blog"].find_one({"id": blog_id})
            updated.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Blog updated successfully",
                "data": updated
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to update blog: {str(e)}"}

    async def delete_blog(self, blog_id: str) -> Dict[str, Any]:
        """Delete blog with real data persistence"""
        try:
            db = await self.get_database()
            result = await db["blog"].delete_one({"id": blog_id})
            
            if result.deleted_count == 0:
                return {"success": False, "error": f"Blog not found"}
            
            return {
                "success": True,
                "message": f"Blog deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to delete blog: {str(e)}"}



# Global service instance
blog_service = BlogService()

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

    async def update_item(self, user_id: str, item_id: str, update_data: dict):
        """Update existing item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            result = await collections['items'].update_one(
                {"_id": item_id, "user_id": user_id},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                return {"success": False, "message": "Item not found or no changes made"}
            
            # Get updated item
            updated_item = await collections['items'].find_one({
                "_id": item_id,
                "user_id": user_id
            })
            
            return {
                "success": True,
                "data": updated_item,
                "message": "Item updated successfully"
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