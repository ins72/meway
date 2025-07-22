"""
Website Builder System API Routes
Professional Mewayz Platform - Migrated from Monolithic Structure
High-Value Feature Addition - Complete Website Creation & Management
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import uuid
import secrets
import string

from core.auth import get_current_active_user
from core.database import get_database
from services.user_service import get_user_service

router = APIRouter()

# Initialize service instances
user_service = get_user_service()

class WebsiteCreate(BaseModel):
    name: str
    title: str
    description: Optional[str] = ""
    domain: Optional[str] = None
    template_id: Optional[str] = None
    theme: Dict[str, Any] = {
        "primary_color": "#3B82F6",
        "secondary_color": "#10B981",
        "font_family": "Inter",
        "background_color": "#FFFFFF"
    }
    seo_settings: Dict[str, Any] = {
        "meta_title": "",
        "meta_description": "",
        "keywords": []
    }
    is_published: bool = False

class WebsiteUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    domain: Optional[str] = None
    theme: Optional[Dict[str, Any]] = None
    seo_settings: Optional[Dict[str, Any]] = None
    is_published: Optional[bool] = None

def get_websites_collection():
    """Get websites collection"""
    db = get_database()
    return db.websites

def get_pages_collection():
    """Get pages collection"""
    db = get_database()
    return db.pages

def get_templates_collection():
    """Get templates collection"""
    db = get_database()
    return db.templates

def get_website_limit(user_plan: str) -> int:
    """Get website creation limit based on user plan"""
    limits = {
        "free": 1,
        "pro": 10,
        "enterprise": -1  # unlimited
    }
    return limits.get(user_plan, 1)

def generate_website_slug(name: str) -> str:
    """Generate URL-safe slug from website name"""
    slug = name.lower().replace(" ", "-")
    # Remove special characters
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')
    return slug

def generate_subdomain() -> str:
    """Generate random subdomain for website"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(8))

@router.get("/dashboard")
async def get_website_builder_dashboard(current_user: dict = Depends(get_current_active_user)):
    """Get website builder dashboard with comprehensive metrics"""
    try:
        websites_collection = get_websites_collection()
        pages_collection = get_pages_collection()
        
        # Get user's websites
        total_websites = await websites_collection.count_documents({"owner_id": current_user["_id"]})
        published_websites = await websites_collection.count_documents({
            "owner_id": current_user["_id"],
            "is_published": True
        })
        
        # Get total pages count
        websites = await websites_collection.find({"owner_id": current_user["_id"]}).to_list(length=None)
        website_ids = [str(website["_id"]) for website in websites]
        
        total_pages = await pages_collection.count_documents({
            "website_id": {"$in": website_ids}
        }) if website_ids else 0
        
        # Get recent websites
        recent_websites = await websites_collection.find({
            "owner_id": current_user["_id"]
        }).sort("created_at", -1).limit(5).to_list(length=None)
        
        # Enhance websites with page count
        for website in recent_websites:
            website["id"] = str(website["_id"])
            
            # Get page count
            page_count = await pages_collection.count_documents({"website_id": website["id"]})
            website["page_count"] = page_count
            website["views"] = 0  # Would be calculated from analytics
        
        # Calculate usage metrics
        user_stats = await user_service.get_user_stats(current_user["_id"])
        user_plan = user_stats["subscription_info"]["plan"]
        max_websites = get_website_limit(user_plan)
        
        dashboard_data = {
            "overview": {
                "total_websites": total_websites,
                "published_websites": published_websites,
                "total_pages": total_pages,
                "website_limit": max_websites,
                "websites_remaining": max_websites - total_websites if max_websites != -1 else -1
            },
            "recent_websites": [
                {
                    "id": website["id"],
                    "name": website["name"],
                    "title": website["title"],
                    "domain": website.get("domain"),
                    "is_published": website.get("is_published", False),
                    "page_count": website["page_count"],
                    "views": website["views"],
                    "created_at": website["created_at"],
                    "website_url": f"https://{website.get('domain', website.get('subdomain', 'example'))}.mewayz.com"
                } for website in recent_websites
            ],
            "quick_stats": {
                "avg_pages_per_website": round(total_pages / max(total_websites, 1), 1),
                "publishing_rate": round((published_websites / max(total_websites, 1)) * 100, 1),
                "plan_utilization": round((total_websites / max_websites * 100), 1) if max_websites != -1 else 0
            }
        }
        
        return {
            "success": True,
            "data": dashboard_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch website builder dashboard: {str(e)}"
        )

@router.post("/websites")
async def create_website(
    website_data: WebsiteCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create new website with validation"""
    try:
        # Check website creation limits
        user_stats = await user_service.get_user_stats(current_user["_id"])
        user_plan = user_stats["subscription_info"]["plan"]
        
        websites_collection = get_websites_collection()
        existing_websites = await websites_collection.count_documents({
            "owner_id": current_user["_id"]
        })
        
        # Plan-based limits
        max_websites = get_website_limit(user_plan)
        if max_websites != -1 and existing_websites >= max_websites:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Website limit reached ({max_websites}). Upgrade your plan for more websites."
            )
        
        # Generate subdomain if no custom domain
        if not website_data.domain:
            website_slug = generate_website_slug(website_data.name)
            subdomain = f"{website_slug}-{generate_subdomain()}"
        else:
            subdomain = None
        
        # Create website document
        website_doc = {
            "_id": str(uuid.uuid4()),
            "owner_id": current_user["_id"],
            "name": website_data.name,
            "title": website_data.title,
            "description": website_data.description,
            "domain": website_data.domain,
            "subdomain": subdomain,
            "template_id": website_data.template_id,
            "theme": website_data.theme,
            "seo_settings": website_data.seo_settings,
            "is_published": website_data.is_published,
            "ssl_enabled": True,
            "page_count": 0,
            "total_views": 0,
            "last_published_at": datetime.utcnow() if website_data.is_published else None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Save website
        await websites_collection.insert_one(website_doc)
        
        response_website = website_doc.copy()
        response_website["id"] = str(response_website["_id"])
        response_website["website_url"] = f"https://{website_data.domain or subdomain}.mewayz.com"
        
        return {
            "success": True,
            "message": "Website created successfully",
            "data": response_website
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create website: {str(e)}"
        )

@router.get("/websites")
async def get_websites(
    status_filter: Optional[str] = None,
    limit: int = 20,
    page: int = 1,
    current_user: dict = Depends(get_current_active_user)
):
    """Get user's websites with filtering and pagination"""
    try:
        websites_collection = get_websites_collection()
        pages_collection = get_pages_collection()
        
        # Build query
        query = {"owner_id": current_user["_id"]}
        
        if status_filter == "published":
            query["is_published"] = True
        elif status_filter == "draft":
            query["is_published"] = False
        
        # Get total count
        total_websites = await websites_collection.count_documents(query)
        
        # Get websites with pagination
        skip = (page - 1) * limit
        websites = await websites_collection.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(length=None)
        
        # Enhance websites with additional data
        for website in websites:
            website["id"] = str(website["_id"])
            
            # Get page count
            page_count = await pages_collection.count_documents({"website_id": website["id"]})
            website["page_count"] = page_count
            
            # Add website URL
            domain = website.get("domain") or website.get("subdomain", "example")
            website["website_url"] = f"https://{domain}.mewayz.com"
            website["ssl_enabled"] = True
            
        return {
            "success": True,
            "data": {
                "websites": websites,
                "pagination": {
                    "current_page": page,
                    "total_pages": (total_websites + limit - 1) // limit,
                    "total_websites": total_websites,
                    "has_next": skip + limit < total_websites,
                    "has_prev": page > 1
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch websites: {str(e)}"
        )

@router.get("/templates")
async def get_templates(
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Get available website templates"""
    try:
        templates_collection = get_templates_collection()
        
        # Build query
        query = {}
        if category:
            query["category"] = category
        
        # Get templates
        templates = await templates_collection.find(query).sort("created_at", -1).to_list(length=None)
        
        # Check user's premium access
        user_stats = await user_service.get_user_stats(current_user["_id"])
        user_plan = user_stats["subscription_info"]["plan"]
        has_premium_access = user_plan in ["pro", "enterprise"]
        
        for template in templates:
            template["id"] = str(template["_id"])
            template["has_access"] = not template.get("is_premium", False) or has_premium_access
        
        # Get available categories
        all_categories = await templates_collection.distinct("category") if templates else []
        
        return {
            "success": True,
            "data": {
                "templates": templates,
                "categories": all_categories,
                "has_premium_access": has_premium_access
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch templates: {str(e)}"
        )