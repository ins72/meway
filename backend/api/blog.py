"""
Blog API - Complete CRUD Operations
Production-ready blog management
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from core.auth import get_current_user, get_current_admin
from services.blog_service import get_blog_service
from pydantic import BaseModel, Field
import logging
from datetime import datetime
from bson import ObjectId

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for blog operations
class BlogPostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    excerpt: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = Field(default_factory=list)
    category: Optional[str] = None
    featured_image: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=60)
    meta_description: Optional[str] = Field(None, max_length=160)
    is_published: bool = False
    publish_date: Optional[datetime] = None

class BlogPostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    excerpt: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    featured_image: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=60)
    meta_description: Optional[str] = Field(None, max_length=160)
    is_published: Optional[bool] = None
    publish_date: Optional[datetime] = None

class BlogPostResponse(BaseModel):
    id: str
    title: str
    content: str
    excerpt: Optional[str]
    slug: str
    tags: List[str]
    category: Optional[str]
    featured_image: Optional[str]
    meta_title: Optional[str]
    meta_description: Optional[str]
    is_published: bool
    publish_date: Optional[datetime]
    author_id: str
    author_name: str
    views: int
    likes: int
    comments_count: int
    created_at: datetime
    updated_at: datetime

class BlogCommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)
    parent_id: Optional[str] = None

class BlogCommentResponse(BaseModel):
    id: str
    content: str
    author_id: str
    author_name: str
    author_avatar: Optional[str]
    parent_id: Optional[str]
    post_id: str
    likes: int
    created_at: datetime
    updated_at: datetime

class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

@router.get("/health")
async def health_check():
    """Health check for blog service"""
    try:
        service = get_blog_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"Blog health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

# ==================== BLOG POST CRUD OPERATIONS ====================

@router.post("/posts", response_model=BlogPostResponse)
async def create_blog_post(
    post_data: BlogPostCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new blog post"""
    try:
        service = get_blog_service()
        post = await service.create_post(
            author_id=str(current_user["_id"]),
            author_name=current_user.get("full_name", current_user.get("email")),
            post_data=post_data.dict()
        )
        return post
    except Exception as e:
        logger.error(f"Create blog post error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts", response_model=List[BlogPostResponse])
async def list_blog_posts(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    author_id: Optional[str] = Query(None),
    is_published: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """List blog posts with filtering"""
    try:
        service = get_blog_service()
        posts = await service.list_posts(
            limit=limit,
            offset=offset,
            category=category,
            tag=tag,
            author_id=author_id,
            is_published=is_published,
            search=search,
            user_id=str(current_user["_id"]) if current_user else None
        )
        return posts
    except Exception as e:
        logger.error(f"List blog posts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts/{post_id}", response_model=BlogPostResponse)
async def get_blog_post(
    post_id: str = Path(..., description="Blog post ID"),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Get a specific blog post by ID"""
    try:
        service = get_blog_service()
        post = await service.get_post(
            post_id=post_id,
            user_id=str(current_user["_id"]) if current_user else None
        )
        if not post:
            raise HTTPException(status_code=404, detail="Blog post not found")
        return post
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get blog post error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts/slug/{slug}", response_model=BlogPostResponse)
async def get_blog_post_by_slug(
    slug: str = Path(..., description="Blog post slug"),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Get a blog post by slug"""
    try:
        service = get_blog_service()
        post = await service.get_post_by_slug(
            slug=slug,
            user_id=str(current_user["_id"]) if current_user else None
        )
        if not post:
            raise HTTPException(status_code=404, detail="Blog post not found")
        return post
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get blog post by slug error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/posts/{post_id}", response_model=BlogPostResponse)
async def update_blog_post(
    post_id: str = Path(..., description="Blog post ID"),
    post_data: BlogPostUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a blog post"""
    try:
        service = get_blog_service()
        post = await service.update_post(
            post_id=post_id,
            user_id=str(current_user["_id"]),
            update_data=post_data.dict(exclude_unset=True)
        )
        if not post:
            raise HTTPException(status_code=404, detail="Blog post not found")
        return post
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update blog post error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/posts/{post_id}")
async def delete_blog_post(
    post_id: str = Path(..., description="Blog post ID"),
    current_user: dict = Depends(get_current_user)
):
    """Delete a blog post"""
    try:
        service = get_blog_service()
        success = await service.delete_post(
            post_id=post_id,
            user_id=str(current_user["_id"])
        )
        if not success:
            raise HTTPException(status_code=404, detail="Blog post not found")
        return {"success": True, "message": "Blog post deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete blog post error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== BLOG COMMENTS CRUD ====================

@router.post("/posts/{post_id}/comments", response_model=BlogCommentResponse)
async def create_comment(
    post_id: str = Path(..., description="Blog post ID"),
    comment_data: BlogCommentCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a comment on a blog post"""
    try:
        service = get_blog_service()
        comment = await service.create_comment(
            post_id=post_id,
            author_id=str(current_user["_id"]),
            author_name=current_user.get("full_name", current_user.get("email")),
            author_avatar=current_user.get("avatar_url"),
            comment_data=comment_data.dict()
        )
        return comment
    except Exception as e:
        logger.error(f"Create comment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts/{post_id}/comments", response_model=List[BlogCommentResponse])
async def list_comments(
    post_id: str = Path(..., description="Blog post ID"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List comments for a blog post"""
    try:
        service = get_blog_service()
        comments = await service.list_comments(
            post_id=post_id,
            limit=limit,
            offset=offset
        )
        return comments
    except Exception as e:
        logger.error(f"List comments error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/comments/{comment_id}", response_model=BlogCommentResponse)
async def update_comment(
    comment_id: str = Path(..., description="Comment ID"),
    comment_data: CommentUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a comment"""
    try:
        service = get_blog_service()
        comment = await service.update_comment(
            comment_id=comment_id,
            user_id=str(current_user["_id"]),
            content=comment_data.content
        )
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        return comment
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update comment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: str = Path(..., description="Comment ID"),
    current_user: dict = Depends(get_current_user)
):
    """Delete a comment"""
    try:
        service = get_blog_service()
        success = await service.delete_comment(
            comment_id=comment_id,
            user_id=str(current_user["_id"])
        )
        if not success:
            raise HTTPException(status_code=404, detail="Comment not found")
        return {"success": True, "message": "Comment deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete comment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== BLOG INTERACTIONS ====================

@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: str = Path(..., description="Blog post ID"),
    current_user: dict = Depends(get_current_user)
):
    """Like a blog post"""
    try:
        service = get_blog_service()
        success = await service.like_post(
            post_id=post_id,
            user_id=str(current_user["_id"])
        )
        return {"success": True, "message": "Post liked successfully"}
    except Exception as e:
        logger.error(f"Like post error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/posts/{post_id}/like")
async def unlike_post(
    post_id: str = Path(..., description="Blog post ID"),
    current_user: dict = Depends(get_current_user)
):
    """Unlike a blog post"""
    try:
        service = get_blog_service()
        success = await service.unlike_post(
            post_id=post_id,
            user_id=str(current_user["_id"])
        )
        return {"success": True, "message": "Post unliked successfully"}
    except Exception as e:
        logger.error(f"Unlike post error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/comments/{comment_id}/like")
async def like_comment(
    comment_id: str = Path(..., description="Comment ID"),
    current_user: dict = Depends(get_current_user)
):
    """Like a comment"""
    try:
        service = get_blog_service()
        success = await service.like_comment(
            comment_id=comment_id,
            user_id=str(current_user["_id"])
        )
        return {"success": True, "message": "Comment liked successfully"}
    except Exception as e:
        logger.error(f"Like comment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== BLOG ANALYTICS ====================

@router.get("/analytics")
async def get_blog_analytics(
    current_user: dict = Depends(get_current_user)
):
    """Get blog analytics for the current user"""
    try:
        service = get_blog_service()
        analytics = await service.get_analytics(
            user_id=str(current_user["_id"])
        )
        return analytics
    except Exception as e:
        logger.error(f"Get blog analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts/{post_id}/analytics")
async def get_post_analytics(
    post_id: str = Path(..., description="Blog post ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get analytics for a specific blog post"""
    try:
        service = get_blog_service()
        analytics = await service.get_post_analytics(
            post_id=post_id,
            user_id=str(current_user["_id"])
        )
        return analytics
    except Exception as e:
        logger.error(f"Get post analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== BLOG CATEGORIES & TAGS ====================

@router.get("/categories")
async def list_categories():
    """List all blog categories"""
    try:
        service = get_blog_service()
        categories = await service.list_categories()
        return categories
    except Exception as e:
        logger.error(f"List categories error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tags")
async def list_tags():
    """List all blog tags"""
    try:
        service = get_blog_service()
        tags = await service.list_tags()
        return tags
    except Exception as e:
        logger.error(f"List tags error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ADMIN OPERATIONS ====================

@router.get("/admin/posts", response_model=List[BlogPostResponse])
async def admin_list_all_posts(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_admin)
):
    """Admin: List all blog posts"""
    try:
        service = get_blog_service()
        posts = await service.admin_list_all_posts(
            limit=limit,
            offset=offset
        )
        return posts
    except Exception as e:
        logger.error(f"Admin list posts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/admin/posts/{post_id}")
async def admin_delete_post(
    post_id: str = Path(..., description="Blog post ID"),
    current_user: dict = Depends(get_current_admin)
):
    """Admin: Force delete a blog post"""
    try:
        service = get_blog_service()
        success = await service.admin_delete_post(post_id=post_id)
        if not success:
            raise HTTPException(status_code=404, detail="Blog post not found")
        return {"success": True, "message": "Blog post force deleted by admin"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin delete post error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_blog_stats(
    current_user: dict = Depends(get_current_admin)
):
    """Get blog statistics (admin only)"""
    try:
        service = get_blog_service()
        stats = await service.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Get blog stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))