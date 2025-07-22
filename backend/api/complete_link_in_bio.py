"""
Complete Link in Bio Builder API - 100% Real Data & Full CRUD
Mewayz v2 - July 22, 2025
NO MOCK DATA - REAL INTEGRATIONS ONLY
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from core.database import get_database
from core.auth import get_current_user
from services.complete_link_in_bio_service import (
    CompleteLinkInBioService,
    PageTemplate,
    LinkType,
    PageStatus
)

router = APIRouter(prefix="/api/link-in-bio", tags=["Complete Link in Bio Builder"])

# Request Models
class BioPageCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    template: PageTemplate = Field(default=PageTemplate.MINIMAL)
    theme: Optional[Dict[str, Any]] = Field(default_factory=dict)
    avatar_url: Optional[str] = Field(None, max_length=500)
    cover_image_url: Optional[str] = Field(None, max_length=500)
    bio_text: Optional[str] = Field(None, max_length=1000)
    contact_info: Optional[Dict[str, Any]] = Field(default_factory=dict)
    social_links: Optional[Dict[str, Any]] = Field(default_factory=dict)
    custom_css: Optional[str] = Field(None, max_length=5000)
    seo_settings: Optional[Dict[str, Any]] = Field(default_factory=dict)
    is_published: bool = Field(default=True)
    custom_domain: Optional[str] = Field(None, max_length=100)
    password_protected: bool = Field(default=False)
    password_hash: Optional[str] = Field(None, max_length=255)
    analytics_enabled: bool = Field(default=True)
    default_links: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

class BioPageUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    template: Optional[PageTemplate] = Field(None)
    theme: Optional[Dict[str, Any]] = Field(None)
    avatar_url: Optional[str] = Field(None, max_length=500)
    cover_image_url: Optional[str] = Field(None, max_length=500)
    bio_text: Optional[str] = Field(None, max_length=1000)
    contact_info: Optional[Dict[str, Any]] = Field(None)
    social_links: Optional[Dict[str, Any]] = Field(None)
    custom_css: Optional[str] = Field(None, max_length=5000)
    seo_settings: Optional[Dict[str, Any]] = Field(None)
    is_published: Optional[bool] = Field(None)
    custom_domain: Optional[str] = Field(None, max_length=100)
    password_protected: Optional[bool] = Field(None)
    password_hash: Optional[str] = Field(None, max_length=255)

class BioLinkCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    url: str = Field(..., min_length=1, max_length=500)
    type: LinkType = Field(default=LinkType.URL)
    description: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = Field(None, max_length=500)
    order: Optional[int] = Field(None, ge=1)
    is_active: bool = Field(default=True)
    custom_styling: Optional[Dict[str, Any]] = Field(default_factory=dict)
    schedule: Optional[Dict[str, Any]] = Field(default_factory=dict)
    password_protected: bool = Field(default=False)
    password_hash: Optional[str] = Field(None, max_length=255)

class BioLinkUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    url: Optional[str] = Field(None, min_length=1, max_length=500)
    type: Optional[LinkType] = Field(None)
    description: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = Field(None, max_length=500)
    order: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = Field(None)
    custom_styling: Optional[Dict[str, Any]] = Field(None)
    schedule: Optional[Dict[str, Any]] = Field(None)
    password_protected: Optional[bool] = Field(None)
    password_hash: Optional[str] = Field(None, max_length=255)

class VisitorData(BaseModel):
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None, max_length=500)
    referrer: Optional[str] = Field(None, max_length=500)
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    device: Optional[str] = Field(None, max_length=100)
    browser: Optional[str] = Field(None, max_length=100)

@router.post("/pages")
async def create_bio_page(
    page_data: BioPageCreate,
    workspace_id: str = Query(..., description="Workspace ID"),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    CREATE: Create new bio page
    Real data only - no mock information
    """
    try:
        service = CompleteLinkInBioService(db)
        
        result = await service.create_bio_page(
            current_user["_id"],
            workspace_id,
            page_data.dict()
        )
        
        return {
            "success": True,
            "message": "Bio page created successfully",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pages/{page_id}")
async def get_bio_page(
    page_id: str,
    include_analytics: bool = Query(False, description="Include analytics data"),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    READ: Get bio page with real data
    Returns complete page information including links and analytics
    """
    try:
        service = CompleteLinkInBioService(db)
        
        result = await service.get_bio_page(
            page_id,
            current_user["_id"],
            include_analytics
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/pages/{page_id}")
async def update_bio_page(
    page_id: str,
    update_data: BioPageUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    UPDATE: Update bio page with real data
    Updates page configuration and settings
    """
    try:
        service = CompleteLinkInBioService(db)
        
        result = await service.update_bio_page(
            page_id,
            current_user["_id"],
            update_data.dict(exclude_unset=True)
        )
        
        return {
            "success": True,
            "message": "Bio page updated successfully",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/pages/{page_id}")
async def delete_bio_page(
    page_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    DELETE: Delete bio page and all related data
    Complete cleanup of page and associated data
    """
    try:
        service = CompleteLinkInBioService(db)
        
        result = await service.delete_bio_page(page_id, current_user["_id"])
        
        return {
            "success": True,
            "message": "Bio page deleted successfully",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pages")
async def get_user_bio_pages(
    workspace_id: Optional[str] = Query(None, description="Filter by workspace"),
    status: Optional[PageStatus] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    READ: Get user's bio pages with filtering
    Returns paginated list of user's bio pages
    """
    try:
        # Build filter query
        filter_query = {"user_id": current_user["_id"]}
        
        if workspace_id:
            filter_query["workspace_id"] = workspace_id
        
        if status:
            filter_query["status"] = status.value
        
        # Get pages
        pages = await db["bio_pages"].find(filter_query).skip(skip).limit(limit).to_list(length=None)
        
        # Get total count
        total_count = await db["bio_pages"].count_documents(filter_query)
        
        return {
            "success": True,
            "data": {
                "pages": pages,
                "total_count": total_count,
                "returned_count": len(pages),
                "skip": skip,
                "limit": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pages/{page_id}/links")
async def create_bio_link(
    page_id: str,
    link_data: BioLinkCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    CREATE: Create new bio link
    Adds new link to bio page with real data
    """
    try:
        service = CompleteLinkInBioService(db)
        
        result = await service.create_bio_link(
            page_id,
            current_user["_id"],
            link_data.dict()
        )
        
        return {
            "success": True,
            "message": "Bio link created successfully",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pages/{page_id}/links")
async def get_bio_links(
    page_id: str,
    active_only: bool = Query(True, description="Show only active links"),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    READ: Get bio links with real data
    Returns all links for a bio page
    """
    try:
        service = CompleteLinkInBioService(db)
        
        result = await service.get_bio_links(
            page_id,
            current_user["_id"],
            active_only
        )
        
        return {
            "success": True,
            "data": {
                "links": result,
                "total_count": len(result)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/links/{link_id}")
async def update_bio_link(
    link_id: str,
    update_data: BioLinkUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    UPDATE: Update bio link with real data
    Updates link configuration and settings
    """
    try:
        service = CompleteLinkInBioService(db)
        
        result = await service.update_bio_link(
            link_id,
            current_user["_id"],
            update_data.dict(exclude_unset=True)
        )
        
        return {
            "success": True,
            "message": "Bio link updated successfully",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/links/{link_id}")
async def delete_bio_link(
    link_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    DELETE: Delete bio link
    Removes link from bio page
    """
    try:
        service = CompleteLinkInBioService(db)
        
        result = await service.delete_bio_link(link_id, current_user["_id"])
        
        return {
            "success": True,
            "message": "Bio link deleted successfully",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_available_templates(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    READ: Get available templates with real data
    Returns template catalog with preview and configurations
    """
    try:
        service = CompleteLinkInBioService(db)
        
        result = await service.get_available_templates()
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pages/{page_id}/analytics")
async def get_page_analytics(
    page_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    READ: Get page analytics with real data
    Returns comprehensive analytics for bio page
    """
    try:
        service = CompleteLinkInBioService(db)
        
        result = await service.get_page_analytics(page_id, current_user["_id"], days)
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pages/{page_id}/visit")
async def track_page_visit(
    page_id: str,
    visitor_data: VisitorData,
    db = Depends(get_database)
):
    """
    CREATE: Track page visit
    Records visitor analytics for bio page
    """
    try:
        service = CompleteLinkInBioService(db)
        
        result = await service.track_page_visit(page_id, visitor_data.dict())
        
        return {
            "success": True,
            "message": "Page visit tracked successfully",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/links/{link_id}/click")
async def track_link_click(
    link_id: str,
    visitor_data: VisitorData,
    db = Depends(get_database)
):
    """
    CREATE: Track link click
    Records click analytics for bio link
    """
    try:
        service = CompleteLinkInBioService(db)
        
        result = await service.track_link_click(link_id, visitor_data.dict())
        
        return {
            "success": True,
            "message": "Link click tracked successfully",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pages/{page_id}/qr-code")
async def get_page_qr_code(
    page_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    READ: Get QR code for bio page
    Returns QR code data for sharing
    """
    try:
        # Verify page ownership
        page = await db["bio_pages"].find_one({"_id": page_id, "user_id": current_user["_id"]})
        if not page:
            raise HTTPException(status_code=404, detail="Bio page not found")
        
        # Get QR code
        qr_code = await db["bio_qr_codes"].find_one({"page_id": page_id})
        
        if not qr_code:
            raise HTTPException(status_code=404, detail="QR code not found")
        
        return {
            "success": True,
            "data": {
                "qr_code": qr_code,
                "page_url": f"https://mewayz.bio/{page['slug']}"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pages/{page_id}/seo")
async def get_page_seo_settings(
    page_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    READ: Get SEO settings for bio page
    Returns SEO configuration and meta tags
    """
    try:
        # Verify page ownership
        page = await db["bio_pages"].find_one({"_id": page_id, "user_id": current_user["_id"]})
        if not page:
            raise HTTPException(status_code=404, detail="Bio page not found")
        
        # Get SEO settings
        seo_settings = await db["bio_seo_settings"].find_one({"page_id": page_id})
        
        return {
            "success": True,
            "data": {
                "seo_settings": seo_settings,
                "page_url": f"https://mewayz.bio/{page['slug']}"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/overview")
async def get_bio_analytics_overview(
    workspace_id: Optional[str] = Query(None, description="Filter by workspace"),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    READ: Get bio analytics overview
    Returns comprehensive analytics across all bio pages
    """
    try:
        # Build filter query
        filter_query = {"user_id": current_user["_id"]}
        if workspace_id:
            filter_query["workspace_id"] = workspace_id
        
        # Get all user's pages
        pages = await db["bio_pages"].find(filter_query).to_list(length=None)
        
        # Calculate totals
        total_pages = len(pages)
        total_views = sum(page.get("view_count", 0) for page in pages)
        total_clicks = sum(page.get("click_count", 0) for page in pages)
        
        # Get recent activity
        recent_visitors = await db["bio_visitors"].find(
            {"page_id": {"$in": [page["_id"] for page in pages]}}
        ).sort("visited_at", -1).limit(10).to_list(length=None)
        
        recent_clicks = await db["bio_link_clicks"].find(
            {"page_id": {"$in": [page["_id"] for page in pages]}}
        ).sort("clicked_at", -1).limit(10).to_list(length=None)
        
        # Get top performing pages
        top_pages = sorted(pages, key=lambda x: x.get("view_count", 0), reverse=True)[:5]
        
        return {
            "success": True,
            "data": {
                "totals": {
                    "total_pages": total_pages,
                    "total_views": total_views,
                    "total_clicks": total_clicks,
                    "conversion_rate": round((total_clicks / max(total_views, 1)) * 100, 2)
                },
                "recent_activity": {
                    "recent_visitors": recent_visitors,
                    "recent_clicks": recent_clicks
                },
                "top_pages": top_pages
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def bio_health_check(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    READ: Health check for bio system
    Returns system status and connectivity
    """
    try:
        service = CompleteLinkInBioService(db)
        
        # Check database connectivity
        db_status = "connected"
        try:
            await db["bio_pages"].find_one({})
        except:
            db_status = "disconnected"
        
        # Check integrations
        integrations_status = {
            "openai": "configured" if service.openai_api_key else "not_configured",
            "stripe": "configured" if service.stripe_secret_key else "not_configured",
            "twitter": "configured" if service.twitter_api_key else "not_configured",
            "tiktok": "configured" if service.tiktok_client_key else "not_configured"
        }
        
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "database": db_status,
                "integrations": integrations_status,
                "collections": {
                    "bio_pages": await db["bio_pages"].count_documents({}),
                    "bio_links": await db["bio_links"].count_documents({}),
                    "bio_analytics": await db["bio_analytics"].count_documents({}),
                    "bio_visitors": await db["bio_visitors"].count_documents({})
                },
                "timestamp": datetime.utcnow()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))