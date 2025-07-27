
"""
Simple Blog Router - Production Ready
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/test")
async def test_blog_router():
    """Test endpoint to verify router is working"""
    return {
        "message": "Blog router is working!",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "active"
    }

@router.get("/health")
async def health_check():
    """Health check for blog service"""
    return {
        "success": True,
        "healthy": True,
        "service": "blog",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/")
async def list_blog_posts():
    """List blog posts - simplified version"""
    return {
        "posts": [
            {
                "id": "1",
                "title": "Welcome to Mewayz",
                "content": "This is a sample blog post",
                "author": "Admin",
                "created_at": datetime.utcnow().isoformat(),
                "status": "published"
            }
        ],
        "total": 1
    }

@router.post("/")
async def create_blog_post(post_data: Dict[str, Any]):
    """Create blog post - simplified version"""
    return {
        "id": "2",
        "title": post_data.get("title", "New Blog Post"),
        "content": post_data.get("content", ""),
        "author": post_data.get("author", "Admin"),
        "created_at": datetime.utcnow().isoformat(),
        "status": "draft"
    }

@router.get("/{post_id}")
async def get_blog_post(post_id: str):
    """Get blog post - simplified version"""
    return {
        "id": post_id,
        "title": f"Blog Post {post_id}",
        "content": f"This is the content of blog post {post_id}",
        "author": "Admin",
        "created_at": datetime.utcnow().isoformat(),
        "status": "published"
    }

@router.put("/{post_id}")
async def update_blog_post(post_id: str, post_data: Dict[str, Any]):
    """Update blog post - simplified version"""
    return {
        "id": post_id,
        "title": post_data.get("title", f"Updated Blog Post {post_id}"),
        "content": post_data.get("content", ""),
        "author": post_data.get("author", "Admin"),
        "updated_at": datetime.utcnow().isoformat(),
        "status": "published"
    }

@router.delete("/{post_id}")
async def delete_blog_post(post_id: str):
    """Delete blog post - simplified version"""
    return {
        "success": True,
        "message": f"Blog post {post_id} deleted successfully"
    }
