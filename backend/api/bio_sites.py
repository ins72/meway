"""
Bio Sites (Link-in-Bio) API Routes
Professional Mewayz Platform - Migrated from Monolithic Structure
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from core.auth import get_current_active_user
from core.database import get_bio_sites_collection
from services.user_service import get_user_service
from services.analytics_service import get_analytics_service
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body

router = APIRouter()

# Initialize service instances
user_service = get_user_service()
analytics_service = get_analytics_service()

class BioSiteCreate(BaseModel):
    name: str
    url_slug: str
    theme: str = "minimal"
    description: Optional[str] = ""
    profile_image: Optional[str] = None

class BioSiteUpdate(BaseModel):
    name: Optional[str] = None
    theme: Optional[str] = None
    description: Optional[str] = None
    profile_image: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class LinkCreate(BaseModel):
    title: str
    url: str
    icon: Optional[str] = None
    is_active: bool = True

@router.get("")
async def get_bio_sites(current_user: dict = Depends(get_current_active_user)):
    """Get user's bio sites with real database operations"""
    try:
        bio_sites_collection = get_bio_sites_collection()
        
        bio_sites = await bio_sites_collection.find(
            {"user_id": current_user["_id"]}
        ).sort("created_at", -1).to_list(length=None)
        
        # Get analytics for each bio site
        for site in bio_sites:
            # Get real analytics data
            analytics = await analytics_service.get_bio_site_analytics(site["_id"])
            site["analytics"] = {
                "total_views": analytics.get("total_views", 0),
                "total_clicks": analytics.get("total_clicks", 0),
                "views_this_month": analytics.get("views_this_month", 0)
            }
        
        return {
            "success": True,
            "data": {
                "bio_sites": bio_sites,
                "total_sites": len(bio_sites)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch bio sites: {str(e)}"
        )

@router.get("/themes")
async def get_bio_site_themes(current_user: dict = Depends(get_current_active_user)):
    """Get available bio site themes"""
    try:
        themes = {
            "minimal": {
                "name": "Minimal",
                "description": "Clean and simple design perfect for professionals",
                "preview_image": "/themes/minimal.png",
                "features": ["Clean typography", "Minimal colors", "Professional layout"],
                "free": True
            },
            "creative": {
                "name": "Creative",
                "description": "Vibrant and artistic design for creators",
                "preview_image": "/themes/creative.png",
                "features": ["Bold colors", "Creative layouts", "Animation effects"],
                "free": True
            },
            "business": {
                "name": "Business",
                "description": "Professional corporate design",
                "preview_image": "/themes/business.png", 
                "features": ["Corporate colors", "Business-focused", "Contact forms"],
                "free": False,
                "requires_plan": "pro"
            },
            "influencer": {
                "name": "Influencer",
                "description": "Perfect for social media influencers",
                "preview_image": "/themes/influencer.png",
                "features": ["Social integration", "Instagram feed", "Engagement tools"],
                "free": False,
                "requires_plan": "pro"
            },
            "portfolio": {
                "name": "Portfolio",
                "description": "Showcase your work and projects",
                "preview_image": "/themes/portfolio.png",
                "features": ["Gallery layouts", "Project showcases", "Contact integration"],
                "free": False,
                "requires_plan": "pro"
            },
            "ecommerce": {
                "name": "E-commerce",
                "description": "Sell products directly from your bio",
                "preview_image": "/themes/ecommerce.png",
                "features": ["Product catalog", "Payment integration", "Order management"],
                "free": False,
                "requires_plan": "enterprise"
            }
        }
        
        # Check user's plan to determine available themes
        user_stats = await user_service.get_user_stats(current_user["_id"])
        user_plan = user_stats["subscription_info"]["plan"]
        
        # Filter themes based on user plan
        available_themes = {}
        for theme_id, theme_data in themes.items():
            if theme_data["free"]:
                theme_data["available"] = True
            else:
                required_plan = theme_data.get("requires_plan", "pro")
                if user_plan == "enterprise" or (user_plan == "pro" and required_plan != "enterprise"):
                    theme_data["available"] = True
                else:
                    theme_data["available"] = False
                    theme_data["upgrade_required"] = required_plan
            
            available_themes[theme_id] = theme_data
        
        return {
            "success": True,
            "data": {
                "themes": available_themes,
                "user_plan": user_plan
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch themes: {str(e)}"
        )

@router.post("")
async def create_bio_site(
    site_data: BioSiteCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create new bio site with real database operations"""
    try:
        bio_sites_collection = get_bio_sites_collection()
        
        # Check if URL slug is already taken
        existing_site = await bio_sites_collection.find_one({"url_slug": site_data.url_slug})
        if existing_site:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL slug already taken. Please choose a different one."
            )
        
        # Check user's plan limits
        user_stats = await user_service.get_user_stats(current_user["_id"])
        user_plan = user_stats["subscription_info"]["plan"]
        plan_features = user_stats["subscription_info"]["features_available"]
        
        # Count existing bio sites
        existing_sites_count = await bio_sites_collection.count_documents({"user_id": current_user["_id"]})
        
        # Check limits
        max_sites = 1 if user_plan == "free" else 5 if user_plan == "pro" else -1  # unlimited for enterprise
        if max_sites != -1 and existing_sites_count >= max_sites:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bio site limit reached ({max_sites}). Upgrade your plan to create more sites."
            )
        
        # Create bio site document
        bio_site_doc = {
            "_id": str(uuid.uuid4()),
            "user_id": current_user["_id"],
            "name": site_data.name,
            "url_slug": site_data.url_slug,
            "theme": site_data.theme,
            "description": site_data.description,
            "profile_image": site_data.profile_image,
            "links": [],
            "settings": {
                "show_profile_image": True,
                "show_description": True,
                "enable_analytics": True,
                "custom_css": "",
                "seo_title": site_data.name,
                "seo_description": site_data.description
            },
            "is_active": True,
            "is_published": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "analytics": {
                "total_views": 0,
                "total_clicks": 0,
                "created_date": datetime.utcnow()
            }
        }
        
        # Save to database
        await bio_sites_collection.insert_one(bio_site_doc)
        
        return {
            "success": True,
            "message": "Bio site created successfully",
            "data": bio_site_doc
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create bio site: {str(e)}"
        )

@router.get("/{site_id}")
async def get_bio_site(
    site_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get bio site details with real database operations"""
    try:
        bio_sites_collection = get_bio_sites_collection()
        
        bio_site = await bio_sites_collection.find_one({
            "_id": site_id,
            "user_id": current_user["_id"]
        })
        
        if not bio_site:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bio site not found"
            )
        
        # Get detailed analytics
        analytics = await analytics_service.get_bio_site_analytics(site_id)
        bio_site["detailed_analytics"] = analytics
        
        return {
            "success": True,
            "data": bio_site
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch bio site: {str(e)}"
        )

@router.put("/{site_id}")
async def update_bio_site(
    site_id: str,
    update_data: BioSiteUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Update bio site with real database operations"""
    try:
        bio_sites_collection = get_bio_sites_collection()
        
        # Find bio site
        bio_site = await bio_sites_collection.find_one({
            "_id": site_id,
            "user_id": current_user["_id"]
        })
        
        if not bio_site:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bio site not found"
            )
        
        # Prepare update document
        update_doc = {
            "$set": {
                "updated_at": datetime.utcnow()
            }
        }
        
        # Update allowed fields
        update_fields = update_data.dict(exclude_none=True)
        for field, value in update_fields.items():
            if field == "settings":
                # Merge settings
                for key, val in value.items():
                    update_doc["$set"][f"settings.{key}"] = val
            else:
                update_doc["$set"][field] = value
        
        # Update bio site
        result = await bio_sites_collection.update_one(
            {"_id": site_id},
            update_doc
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No changes made"
            )
        
        # Return updated bio site
        updated_bio_site = await bio_sites_collection.find_one({"_id": site_id})
        
        return {
            "success": True,
            "message": "Bio site updated successfully",
            "data": updated_bio_site
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update bio site: {str(e)}"
        )

@router.post("/{site_id}/links")
async def add_bio_site_link(
    site_id: str,
    link_data: LinkCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Add link to bio site with real database operations"""
    try:
        bio_sites_collection = get_bio_sites_collection()
        
        # Find bio site
        bio_site = await bio_sites_collection.find_one({
            "_id": site_id,
            "user_id": current_user["_id"]
        })
        
        if not bio_site:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bio site not found"
            )
        
        # Create new link
        new_link = {
            "id": str(uuid.uuid4()),
            "title": link_data.title,
            "url": link_data.url,
            "icon": link_data.icon,
            "is_active": link_data.is_active,
            "clicks": 0,
            "created_at": datetime.utcnow(),
            "order": len(bio_site.get("links", [])) + 1
        }
        
        # Add link to bio site
        await bio_sites_collection.update_one(
            {"_id": site_id},
            {
                "$push": {"links": new_link},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return {
            "success": True,
            "message": "Link added successfully",
            "data": new_link
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add link: {str(e)}"
        )

@router.delete("/{site_id}")
async def delete_bio_site(
    site_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Delete bio site with real database operations"""
    try:
        bio_sites_collection = get_bio_sites_collection()
        
        # Find and delete bio site
        result = await bio_sites_collection.delete_one({
            "_id": site_id,
            "user_id": current_user["_id"]
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bio site not found"
            )
        
        return {
            "success": True,
            "message": "Bio site deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete bio site: {str(e)}"
        )