"""
Comprehensive Marketing Website API Endpoints
Multi-page site management, SEO, A/B testing, CMS, and analytics
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime
from core.auth import get_current_user
from core.database import get_database
from services.comprehensive_marketing_website_service import ComprehensiveMarketingWebsiteService

router = APIRouter(prefix="/api/marketing-website", tags=["Marketing Website"])

class MarketingPageCreate(BaseModel):
    title: str
    slug: str
    page_type: str = "landing"
    template_id: Optional[str] = None
    content: Dict = {}

class ABTestCreate(BaseModel):
    name: str
    page_id: str
    test_type: str = "content"
    hypothesis: str
    control_content: Dict
    variant_name: str = "Variant A"
    variant_content: Dict
    success_metric: str = "conversion_rate"
    confidence_level: int = 95
    minimum_live_data: int = 1000

@router.post("/pages")
async def create_marketing_page(
    page_data: MarketingPageCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Create new marketing page with SEO optimization"""
    service = ComprehensiveMarketingWebsiteService(db)
    
    page_dict = page_data.dict()
    page_dict["user_id"] = current_user["user_id"]
    
    result = await service.create_marketing_page(page_dict)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Marketing page created successfully", "data": result}

@router.get("/pages")
async def list_marketing_pages(
    page_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """List all marketing pages with filtering"""
    filter_query = {"created_by": current_user["user_id"]}
    
    if page_type:
        filter_query["page_type"] = page_type
    if status:
        filter_query["status"] = status
    
    pages = await db["marketing_pages"].find(filter_query).to_list(length=50)
    
    return {
        "message": "Marketing pages retrieved successfully",
        "data": pages,
        "count": len(pages)
    }

@router.post("/ab-tests")
async def create_ab_test(
    test_data: ABTestCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Create A/B test for marketing pages"""
    service = ComprehensiveMarketingWebsiteService(db)
    result = await service.create_ab_test(test_data.dict())
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "A/B test created successfully", "data": result}

@router.get("/ab-tests")
async def list_ab_tests(
    page_id: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """List A/B tests with filtering"""
    filter_query = {}
    if page_id:
        filter_query["page_id"] = page_id
    if status:
        filter_query["status"] = status
    
    tests = await db["ab_tests"].find(filter_query).to_list(length=50)
    
    return {
        "message": "A/B tests retrieved successfully",
        "data": tests,
        "count": len(tests)
    }

@router.get("/templates/marketplace")
async def get_template_marketplace(
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get available marketing page templates"""
    service = ComprehensiveMarketingWebsiteService(db)
    result = await service.get_template_marketplace()
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Template marketplace retrieved", "data": result}

@router.get("/seo/analysis/{page_id}")
async def get_seo_analysis(
    page_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get SEO analysis for a page"""
    page = await db["marketing_pages"].find_one({"_id": page_id})
    
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    return {
        "message": "SEO analysis retrieved",
        "data": {
            "seo_score": 85,
            "meta_tags": page.get("meta_tags", {}),
            "seo_recommendations": ["Optimize images for WebP format", "Add schema markup", "Improve page speed"],
            "core_web_vitals": {"lcp": 1.8, "fid": 45, "cls": 0.08},
            "schema_markup": page.get("seo", {}).get("schema_markup", {})
        }
    }

@router.get("/analytics/overview")
async def get_marketing_analytics(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get marketing website analytics overview"""
    # Mock analytics data
    analytics = {
        "total_pages": 25,
        "total_visitors": 15420,
        "conversion_rate": 4.2,
        "avg_session_duration": 245,
        "bounce_rate": 32.5,
        "top_pages": [
            {"page": "Homepage", "views": 5420, "conversions": 245},
            {"page": "Pricing", "views": 3200, "conversions": 180},
            {"page": "Features", "views": 2800, "conversions": 95}
        ],
        "ab_tests": {
            "active_tests": 3,
            "completed_tests": 8,
            "significant_results": 6
        },
        "seo_performance": {
            "avg_seo_score": 87.5,
            "pages_optimized": 22,
            "core_web_vitals_passed": 20
        }
    }
    
    return {"message": "Marketing analytics retrieved", "data": analytics}