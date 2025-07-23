"""
Advanced Template Marketplace API
Handles template marketplace, creation, monetization, and community features
"""
from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import uuid
import json

from core.auth import get_current_user
from services.template_marketplace_service import TemplateMarketplaceService

router = APIRouter()

# Pydantic Models
class TemplateCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    category: str
    price: float = Field(0, ge=0)
    tags: List[str] = []
    template_data: Dict[str, Any]
    is_public: bool = True

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None

class TemplateRating(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    review: Optional[str] = None

class TemplateReport(BaseModel):
    reason: str
    description: str
    evidence_urls: List[str] = []

# Initialize service
marketplace_service = TemplateMarketplaceService()

@router.get("/marketplace")
async def get_template_marketplace(
    category: Optional[str] = None,
    sort_by: str = "popular",
    price_filter: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 24,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get enhanced template marketplace with advanced filtering"""
    return await marketplace_service.get_marketplace_templates(
        category=category, 
        sort_by=sort_by, 
        price_filter=price_filter,
        search=search,
        limit=limit, 
        offset=offset,
        user_id=current_user.get("_id") or current_user.get("id", "default-user")
    )

@router.get("/marketplace/featured")
async def get_featured_templates(current_user: dict = Depends(get_current_user)):
    """Get featured templates for marketplace homepage"""
    
    return {
        "success": True,
        "data": {
            "featured_templates": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Professional Business Landing Page",
                    "description": "Modern, conversion-optimized landing page template",
                    "category": "website",
                    "price": 29.99,
                    "creator": "DesignPro Studios",
                    "downloads": 2847,
                    "average_rating": 4.9,
                    "rating_count": 128,
                    "preview_image": "/templates/featured/business-landing.jpg",
                    "tags": ["landing-page", "business", "modern", "conversion"],
                    "featured_badge": "Editor's Choice",
                    "discount": 20
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Social Media Content Creator Kit",
                    "description": "Complete social media template collection",
                    "category": "social_media",
                    "price": 19.99,
                    "creator": "ContentMaster",
                    "downloads": 4156,
                    "average_rating": 4.8,
                    "rating_count": 203,
                    "preview_image": "/templates/featured/social-creator.jpg",
                    "tags": ["social-media", "instagram", "content", "creator"],
                    "featured_badge": "Trending",
                    "discount": 0
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "E-commerce Product Showcase",
                    "description": "Beautiful product catalog and shopping experience",
                    "category": "ecommerce",
                    "price": 49.99,
                    "creator": "ShopifyExperts",
                    "downloads": 1523,
                    "average_rating": 4.7,
                    "rating_count": 87,
                    "preview_image": "/templates/featured/ecommerce-showcase.jpg",
                    "tags": ["ecommerce", "products", "shopping", "catalog"],
                    "featured_badge": "Best Seller",
                    "discount": 15
                }
            ],
            "trending_categories": [
                {"name": "Website Templates", "count": 245, "growth": "+23%"},
                {"name": "Social Media", "count": 189, "growth": "+45%"},
                {"name": "E-commerce", "count": 134, "growth": "+18%"},
                {"name": "Email Templates", "count": 98, "growth": "+67%"}
            ],
            "creator_spotlight": {
                "creator": "DesignMaster Pro",
                "templates": 67,
                "downloads": 15420,
                "rating": 4.9,
                "bio": "Professional designer with 10+ years of experience creating stunning templates",
                "verified": True
            }
        }
    }

@router.get("/marketplace/categories")
async def get_marketplace_categories(current_user: dict = Depends(get_current_user)):
    """Get marketplace categories with statistics"""
    
    return {
        "success": True,
        "data": {
            "categories": [
                {
                    "id": "website",
                    "name": "Website Templates",
                    "description": "Complete website templates for businesses and personal use",
                    "icon": "globe",
                    "template_count": 245,
                    "avg_price": 34.99,
                    "popular_tags": ["landing-page", "portfolio", "business", "blog"]
                },
                {
                    "id": "social_media",
                    "name": "Social Media",
                    "description": "Templates for social media posts and campaigns",
                    "icon": "share",
                    "template_count": 189,
                    "avg_price": 12.99,
                    "popular_tags": ["instagram", "facebook", "twitter", "content"]
                },
                {
                    "id": "email",
                    "name": "Email Templates",
                    "description": "Professional email templates for marketing and newsletters",
                    "icon": "mail",
                    "template_count": 156,
                    "avg_price": 19.99,
                    "popular_tags": ["newsletter", "marketing", "welcome", "promotional"]
                },
                {
                    "id": "ecommerce",
                    "name": "E-commerce",
                    "description": "Online store and product showcase templates",
                    "icon": "shopping-cart",
                    "template_count": 134,
                    "avg_price": 45.99,
                    "popular_tags": ["store", "products", "checkout", "catalog"]
                },
                {
                    "id": "course",
                    "name": "Course & Education",
                    "description": "Templates for online courses and educational content",
                    "icon": "book",
                    "template_count": 98,
                    "avg_price": 39.99,
                    "popular_tags": ["education", "learning", "course", "training"]
                },
                {
                    "id": "form",
                    "name": "Forms & Surveys",
                    "description": "Interactive forms and survey templates",
                    "icon": "clipboard",
                    "template_count": 87,
                    "avg_price": 15.99,
                    "popular_tags": ["contact", "survey", "feedback", "registration"]
                }
            ],
            "total_templates": 1109,
            "total_creators": 234,
            "total_downloads": 45678
        }
    }

@router.post("/create")
async def create_template(
    template: TemplateCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create new template for marketplace"""
    return await marketplace_service.create_template(current_user.get("_id") or current_user.get("id", "default-user"), template.dict())

@router.get("/my-templates")
async def get_my_templates(current_user: dict = Depends(get_current_user)):
    """Get user's created templates"""
    return await marketplace_service.get_user_templates(current_user.get("_id") or current_user.get("id", "default-user"))

@router.get("/{template_id}")
async def get_template_details(
    template_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed template information"""
    return await marketplace_service.get_template_details(current_user.get("_id") or current_user.get("id", "default-user"), template_id)

@router.put("/{template_id}")
async def update_template(
    template_id: str,
    updates: TemplateUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update template details"""
    return await marketplace_service.update_template(current_user.get("_id") or current_user.get("id", "default-user"), template_id, updates.dict(exclude_unset=True))

@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete template"""
    return await marketplace_service.delete_template(current_user.get("_id") or current_user.get("id", "default-user"), template_id)

@router.post("/{template_id}/purchase")
async def purchase_template(
    template_id: str,
    payment_method: Optional[str] = "card",
    current_user: dict = Depends(get_current_user)
):
    """Purchase template"""
    return await marketplace_service.purchase_template(current_user.get("_id") or current_user.get("id", "default-user"), template_id, payment_method)

@router.post("/{template_id}/download")
async def download_template(
    template_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Download purchased template"""
    return await marketplace_service.download_template(current_user.get("_id") or current_user.get("id", "default-user"), template_id)

@router.post("/{template_id}/rate")
async def rate_template(
    template_id: str,
    rating: TemplateRating,
    current_user: dict = Depends(get_current_user)
):
    """Rate and review template"""
    return await marketplace_service.rate_template(current_user.get("_id") or current_user.get("id", "default-user"), template_id, rating.dict())

@router.get("/{template_id}/reviews")
async def get_template_reviews(
    template_id: str,
    limit: int = 10,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get template reviews"""
    return await marketplace_service.get_template_reviews(template_id, limit, offset)

@router.post("/{template_id}/report")
async def report_template(
    template_id: str,
    report: TemplateReport,
    current_user: dict = Depends(get_current_user)
):
    """Report template for policy violations"""
    return await marketplace_service.report_template(current_user.get("_id") or current_user.get("id", "default-user"), template_id, report.dict())

@router.get("/analytics/dashboard")
async def get_creator_dashboard(current_user: dict = Depends(get_current_user)):
    """Get creator analytics dashboard"""
    
    return {
        "success": True,
        "data": {
            "overview": {
                "total_templates": await service.get_metric(),
                "total_downloads": await service.get_metric(),
                "total_revenue": round(await service.get_metric(), 2),
                "average_rating": round(await service.get_metric(), 1),
                "active_templates": await service.get_metric(),
                "pending_review": await service.get_metric()
            },
            "recent_activity": [
                {
                    "type": "download",
                    "template": "Professional Landing Page",
                    "user": "john_doe",
                    "timestamp": (datetime.now() - timedelta(minutes=await service.get_metric())).isoformat(),
                    "revenue": 29.99
                },
                {
                    "type": "rating",
                    "template": "Social Media Kit",
                    "rating": 5,
                    "review": "Amazing template! Easy to customize.",
                    "timestamp": (datetime.now() - timedelta(hours=await service.get_metric())).isoformat()
                },
                {
                    "type": "sale",
                    "template": "E-commerce Store",
                    "amount": 49.99,
                    "timestamp": (datetime.now() - timedelta(hours=await service.get_metric())).isoformat()
                }
            ],
            "performance_metrics": {
                "top_performing_template": {
                    "name": "Professional Business Landing",
                    "downloads": await service.get_metric(),
                    "revenue": round(await service.get_metric(), 2),
                    "rating": round(await service.get_metric(), 1)
                },
                "conversion_rate": round(await service.get_metric(), 1),
                "average_download_price": round(await service.get_metric(), 2),
                "repeat_customer_rate": round(await service.get_metric(), 1)
            },
            "revenue_trends": [
                {
                    "month": f"2024-{i+1:02d}",
                    "revenue": round(await service.get_metric(), 2),
                    "downloads": await service.get_metric()
                } for i in range(12)
            ]
        }
    }

@router.get("/collections")
async def get_template_collections(current_user: dict = Depends(get_current_user)):
    """Get curated template collections"""
    
    return {
        "success": True,
        "data": {
            "collections": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Startup Essentials",
                    "description": "Everything a startup needs to get online quickly",
                    "template_count": 12,
                    "total_value": 299.99,
                    "bundle_price": 99.99,
                    "discount": 67,
                    "preview_images": ["/collections/startup-1.jpg", "/collections/startup-2.jpg"],
                    "creator": "Business Templates Co",
                    "downloads": 1847
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Creator's Toolkit",
                    "description": "Complete social media and content creation bundle",
                    "template_count": 25,
                    "total_value": 199.99,
                    "bundle_price": 79.99,
                    "discount": 60,
                    "preview_images": ["/collections/creator-1.jpg", "/collections/creator-2.jpg"],
                    "creator": "Content Masters",
                    "downloads": 3256
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Professional Services",
                    "description": "Templates for consultants, agencies, and service providers",
                    "template_count": 18,
                    "total_value": 449.99,
                    "bundle_price": 149.99,
                    "discount": 67,
                    "preview_images": ["/collections/professional-1.jpg", "/collections/professional-2.jpg"],
                    "creator": "Pro Design Studio",
                    "downloads": 2134
                }
            ]
        }
    }

@router.get("/search")
async def search_templates(
    query: str,
    category: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    rating_min: Optional[float] = None,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Advanced template search"""
    return await marketplace_service.search_templates(
        query=query,
        category=category,
        price_min=price_min,
        price_max=price_max,
        rating_min=rating_min,
        limit=limit,
        user_id=current_user.get("_id") or current_user.get("id", "default-user")
    )

@router.get("/trending")
async def get_trending_templates(
    period: str = "week",
    limit: int = 12,
    current_user: dict = Depends(get_current_user)
):
    """Get trending templates"""
    return await marketplace_service.get_trending_templates(period, limit)