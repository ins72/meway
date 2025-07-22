"""
Complete Website Builder API
No-code website builder with real data persistence and full CRUD operations
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4
import logging

from fastapi import APIRouter, HTTPException, Depends, Query, Body, File, UploadFile
from pydantic import BaseModel, Field

from core.auth import get_current_user
from services.complete_website_builder_service import complete_website_builder_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class WebsiteCreateRequest(BaseModel):
    name: str = Field(..., description="Website name")
    template_id: Optional[str] = Field(None, description="Template ID to use")
    domain: Optional[str] = Field(None, description="Custom domain")
    theme: str = Field("modern", description="Website theme")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Additional metadata")

class WebsiteUpdateRequest(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    theme: Optional[str] = None
    favicon_url: Optional[str] = None
    custom_css: Optional[str] = None
    seo_settings: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class PageCreateRequest(BaseModel):
    title: str = Field(..., description="Page title")
    slug: str = Field(..., description="Page URL slug")
    content: Dict[str, Any] = Field(..., description="Page content structure")
    meta_description: Optional[str] = Field(None, description="SEO meta description")
    meta_keywords: Optional[str] = Field(None, description="SEO meta keywords")
    is_homepage: bool = Field(False, description="Set as homepage")

class PageUpdateRequest(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    is_homepage: Optional[bool] = None
    is_published: Optional[bool] = None

class ComponentCreateRequest(BaseModel):
    name: str = Field(..., description="Component name")
    type: str = Field(..., description="Component type")
    content: Dict[str, Any] = Field(..., description="Component structure")
    styles: Optional[Dict[str, Any]] = Field({}, description="Component styles")
    is_global: bool = Field(False, description="Available globally")

class TemplateCreateRequest(BaseModel):
    name: str = Field(..., description="Template name")
    category: str = Field(..., description="Template category")
    description: str = Field(..., description="Template description")
    preview_image: Optional[str] = Field(None, description="Preview image URL")
    pages: List[Dict[str, Any]] = Field(..., description="Template pages")
    styles: Dict[str, Any] = Field(..., description="Template styles")
    is_public: bool = Field(False, description="Make template public")

# Website Management Endpoints
@router.post("/websites", tags=["Website Builder"])
async def create_website(
    website_data: WebsiteCreateRequest,
    user = Depends(get_current_user)
):
    """Create a new website with real data persistence"""
    try:
        result = await complete_website_builder_service.create_website(
            user_id=user['id'],
            name=website_data.name,
            template_id=website_data.template_id,
            domain=website_data.domain,
            theme=website_data.theme,
            metadata=website_data.metadata
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create website")
            
        return {
            "success": True,
            "message": "Website created successfully",
            "website": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Create website error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/websites", tags=["Website Builder"])
async def get_websites(
    user = Depends(get_current_user),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, description="Number of websites to return"),
    offset: int = Query(0, description="Offset for pagination")
):
    """Get user websites with real data"""
    try:
        result = await complete_website_builder_service.get_user_websites(
            user_id=user['id'],
            status=status,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "websites": result.get('websites', []),
            "total_count": result.get('total_count', 0),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get websites error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/websites/{website_id}", tags=["Website Builder"])
async def get_website(
    website_id: str,
    user = Depends(get_current_user)
):
    """Get specific website details"""
    try:
        result = await complete_website_builder_service.get_website(
            website_id=website_id,
            user_id=user['id']
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Website not found")
            
        return {
            "success": True,
            "website": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get website error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/websites/{website_id}", tags=["Website Builder"])
async def update_website(
    website_id: str,
    website_data: WebsiteUpdateRequest,
    user = Depends(get_current_user)
):
    """Update website with real data persistence"""
    try:
        result = await complete_website_builder_service.update_website(
            website_id=website_id,
            user_id=user['id'],
            update_data=website_data.dict(exclude_unset=True)
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Website not found or update failed")
            
        return {
            "success": True,
            "message": "Website updated successfully",
            "website": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Update website error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/websites/{website_id}", tags=["Website Builder"])
async def delete_website(
    website_id: str,
    user = Depends(get_current_user)
):
    """Delete website and all associated data"""
    try:
        result = await complete_website_builder_service.delete_website(
            website_id=website_id,
            user_id=user['id']
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Website not found")
            
        return {
            "success": True,
            "message": "Website deleted successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Delete website error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/websites/{website_id}/publish", tags=["Website Builder"])
async def publish_website(
    website_id: str,
    user = Depends(get_current_user)
):
    """Publish website to live domain"""
    try:
        result = await complete_website_builder_service.publish_website(
            website_id=website_id,
            user_id=user['id']
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Website not found or publish failed")
            
        return {
            "success": True,
            "message": "Website published successfully",
            "publish_url": result.get('publish_url'),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Publish website error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Page Management Endpoints
@router.post("/websites/{website_id}/pages", tags=["Website Builder"])
async def create_page(
    website_id: str,
    page_data: PageCreateRequest,
    user = Depends(get_current_user)
):
    """Create a new page for the website"""
    try:
        result = await complete_website_builder_service.create_page(
            website_id=website_id,
            user_id=user['id'],
            title=page_data.title,
            slug=page_data.slug,
            content=page_data.content,
            meta_description=page_data.meta_description,
            meta_keywords=page_data.meta_keywords,
            is_homepage=page_data.is_homepage
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create page")
            
        return {
            "success": True,
            "message": "Page created successfully",
            "page": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Create page error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/websites/{website_id}/pages", tags=["Website Builder"])
async def get_pages(
    website_id: str,
    user = Depends(get_current_user),
    published_only: bool = Query(False, description="Show only published pages")
):
    """Get website pages"""
    try:
        result = await complete_website_builder_service.get_website_pages(
            website_id=website_id,
            user_id=user['id'],
            published_only=published_only
        )
        
        return {
            "success": True,
            "pages": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get pages error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/websites/{website_id}/pages/{page_id}", tags=["Website Builder"])
async def update_page(
    website_id: str,
    page_id: str,
    page_data: PageUpdateRequest,
    user = Depends(get_current_user)
):
    """Update page with real data persistence"""
    try:
        result = await complete_website_builder_service.update_page(
            page_id=page_id,
            website_id=website_id,
            user_id=user['id'],
            update_data=page_data.dict(exclude_unset=True)
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Page not found or update failed")
            
        return {
            "success": True,
            "message": "Page updated successfully",
            "page": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Update page error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/websites/{website_id}/pages/{page_id}", tags=["Website Builder"])
async def delete_page(
    website_id: str,
    page_id: str,
    user = Depends(get_current_user)
):
    """Delete page"""
    try:
        result = await complete_website_builder_service.delete_page(
            page_id=page_id,
            website_id=website_id,
            user_id=user['id']
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Page not found")
            
        return {
            "success": True,
            "message": "Page deleted successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Delete page error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Component Management Endpoints
@router.post("/components", tags=["Website Builder"])
async def create_component(
    component_data: ComponentCreateRequest,
    user = Depends(get_current_user)
):
    """Create a reusable component"""
    try:
        result = await complete_website_builder_service.create_component(
            user_id=user['id'],
            name=component_data.name,
            component_type=component_data.type,
            content=component_data.content,
            styles=component_data.styles,
            is_global=component_data.is_global
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create component")
            
        return {
            "success": True,
            "message": "Component created successfully",
            "component": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Create component error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/components", tags=["Website Builder"])
async def get_components(
    user = Depends(get_current_user),
    component_type: Optional[str] = Query(None, description="Filter by component type"),
    include_global: bool = Query(True, description="Include global components")
):
    """Get user components"""
    try:
        result = await complete_website_builder_service.get_user_components(
            user_id=user['id'],
            component_type=component_type,
            include_global=include_global
        )
        
        return {
            "success": True,
            "components": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get components error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Template Management Endpoints
@router.post("/templates", tags=["Website Builder"])
async def create_template(
    template_data: TemplateCreateRequest,
    user = Depends(get_current_user)
):
    """Create a website template"""
    try:
        result = await complete_website_builder_service.create_template(
            user_id=user['id'],
            name=template_data.name,
            category=template_data.category,
            description=template_data.description,
            preview_image=template_data.preview_image,
            pages=template_data.pages,
            styles=template_data.styles,
            is_public=template_data.is_public
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create template")
            
        return {
            "success": True,
            "message": "Template created successfully",
            "template": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Create template error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates", tags=["Website Builder"])
async def get_templates(
    user = Depends(get_current_user),
    category: Optional[str] = Query(None, description="Filter by category"),
    public_only: bool = Query(False, description="Show only public templates")
):
    """Get available templates"""
    try:
        result = await complete_website_builder_service.get_templates(
            user_id=user['id'] if not public_only else None,
            category=category,
            public_only=public_only
        )
        
        return {
            "success": True,
            "templates": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get templates error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Media Management Endpoints
@router.post("/websites/{website_id}/media/upload", tags=["Website Builder"])
async def upload_media(
    website_id: str,
    file: UploadFile = File(...),
    user = Depends(get_current_user)
):
    """Upload media file for website"""
    try:
        # Read file content
        file_content = await file.read()
        
        result = await complete_website_builder_service.upload_media(
            website_id=website_id,
            user_id=user['id'],
            filename=file.filename,
            file_content=file_content,
            content_type=file.content_type
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to upload media")
            
        return {
            "success": True,
            "message": "Media uploaded successfully",
            "media": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Upload media error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/websites/{website_id}/media", tags=["Website Builder"])
async def get_media(
    website_id: str,
    user = Depends(get_current_user),
    media_type: Optional[str] = Query(None, description="Filter by media type")
):
    """Get website media files"""
    try:
        result = await complete_website_builder_service.get_website_media(
            website_id=website_id,
            user_id=user['id'],
            media_type=media_type
        )
        
        return {
            "success": True,
            "media": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get media error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Domain Management Endpoints
@router.post("/websites/{website_id}/domains", tags=["Website Builder"])
async def add_custom_domain(
    website_id: str,
    domain_data: Dict[str, Any] = Body(...),
    user = Depends(get_current_user)
):
    """Add custom domain to website"""
    try:
        result = await complete_website_builder_service.add_custom_domain(
            website_id=website_id,
            user_id=user['id'],
            domain=domain_data.get('domain'),
            ssl_enabled=domain_data.get('ssl_enabled', True)
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to add custom domain")
            
        return {
            "success": True,
            "message": "Custom domain added successfully",
            "domain_config": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Add custom domain error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/websites/{website_id}/domains", tags=["Website Builder"])
async def get_website_domains(
    website_id: str,
    user = Depends(get_current_user)
):
    """Get website domains"""
    try:
        result = await complete_website_builder_service.get_website_domains(
            website_id=website_id,
            user_id=user['id']
        )
        
        return {
            "success": True,
            "domains": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get website domains error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics and SEO Endpoints
@router.get("/websites/{website_id}/analytics", tags=["Website Builder"])
async def get_website_analytics(
    website_id: str,
    user = Depends(get_current_user),
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics")
):
    """Get website analytics data"""
    try:
        result = await complete_website_builder_service.get_website_analytics(
            website_id=website_id,
            user_id=user['id'],
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "success": True,
            "analytics": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get website analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/websites/{website_id}/seo-audit", tags=["Website Builder"])
async def run_seo_audit(
    website_id: str,
    user = Depends(get_current_user)
):
    """Run SEO audit for website"""
    try:
        result = await complete_website_builder_service.run_seo_audit(
            website_id=website_id,
            user_id=user['id']
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Website not found")
            
        return {
            "success": True,
            "seo_audit": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Run SEO audit error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard", tags=["Website Builder"])
async def get_builder_dashboard(
    user = Depends(get_current_user)
):
    """Get website builder dashboard data"""
    try:
        result = await complete_website_builder_service.get_builder_dashboard(
            user_id=user['id']
        )
        
        return {
            "success": True,
            "dashboard": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get builder dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", tags=["Website Builder"])
async def builder_health_check():
    """Health check for website builder system"""
    return {
        "status": "healthy",
        "service": "Complete Website Builder",
        "features": [
            "Website Management",
            "Page Builder",
            "Component Library",
            "Template System",
            "Media Management",
            "Custom Domains",
            "SEO Tools",
            "Analytics Integration"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }