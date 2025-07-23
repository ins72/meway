"""
Advanced Template Marketplace API
Complete template creation, selling, monetization, and usage endpoints
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field

from core.auth import get_current_user
from services.advanced_template_marketplace_service import advanced_template_marketplace_service, TemplateCategory, TemplateStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class TemplateCreateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=100)
    name: Optional[str] = Field(None, min_length=5, max_length=100)  # Alternative field name
    description: str = Field(..., min_length=20, max_length=1000)
    category: str = Field(..., description="Template category")
    subcategory: Optional[str] = Field(None, max_length=50)
    price: float = Field(0.0, ge=0, description="Template price")
    tags: List[str] = Field([], max_items=10)
    template_data: Optional[Dict[str, Any]] = Field(None, description="Template structure/data")
    preview_url: Optional[str] = None
    preview_images: Optional[List[str]] = None  # Additional field for compatibility
    metadata: Optional[Dict[str, Any]] = None
    features: Optional[List[str]] = None  # Additional field for compatibility
    compatibility: Optional[List[str]] = None  # Additional field for compatibility

@router.post("/templates", tags=["Template Creation"])
async def create_template(
    request: TemplateCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create new template for marketplace"""
    try:
        # Normalize request data - handle both 'name' and 'title' fields
        data = request.dict()
        if not data.get('title') and data.get('name'):
            data['title'] = data['name']
        elif not data.get('title'):
            data['title'] = "Untitled Template"
            
        # Set default template_data if not provided
        if not data.get('template_data'):
            data['template_data'] = {
                "html": data.get('html', ''),
                "css": data.get('css', ''),
                "js": data.get('js', ''),
                "components": data.get('components', [])
            }
        
        template = await advanced_template_marketplace_service.create_template(
            creator_id=current_user["_id"],
            data=data
        )
        
        return {
            "success": True,
            "template": template,
            "template_id": template["id"],
            "id": template["id"],  # Alternative field name
            "message": "Template created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/marketplace", tags=["Template Browsing"])
async def browse_templates(
    category: Optional[str] = Query(None),
    price_min: Optional[float] = Query(0),
    price_max: Optional[float] = Query(None),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    rating_min: Optional[float] = Query(None, ge=1, le=5),
    search: Optional[str] = Query(None),
    sort_by: str = Query("popular", pattern="^(popular|newest|rating|price_low|price_high)$"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    """Browse marketplace templates with advanced filtering"""
    try:
        filters = {}
        
        if category:
            filters["category"] = category
        if price_max:
            filters["price_range"] = [price_min, price_max]
        if tags:
            filters["tags"] = [tag.strip() for tag in tags.split(",")]
        if rating_min:
            filters["rating_min"] = rating_min
        if search:
            filters["search"] = search
        if sort_by:
            filters["sort_by"] = sort_by
        
        skip = (page - 1) * per_page
        
        result = await advanced_template_marketplace_service.browse_templates(
            filters=filters if filters else None,
            limit=per_page,
            skip=skip
        )
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        logger.error(f"Error browsing templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/templates/{template_id}/purchase", tags=["Template Usage"])
async def purchase_template(
    template_id: str,
    payment_method: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_user)
):
    """Purchase template with payment processing"""
    try:
        purchase = await advanced_template_marketplace_service.purchase_template(
            user_id=current_user["_id"],
            template_id=template_id,
            payment_method=payment_method
        )
        
        return {
            "success": True,
            "purchase": purchase,
            "message": "Template purchased successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error purchasing template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{template_id}/download", tags=["Template Usage"])
async def download_template(
    template_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Download purchased or free template for usage"""
    try:
        template_data = await advanced_template_marketplace_service.get_template_for_use(
            user_id=current_user["_id"],
            template_id=template_id
        )
        
        return {
            "success": True,
            **template_data
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error downloading template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories", tags=["Template Browsing"])
async def get_template_categories():
    """Get available template categories"""
    return {
        "success": True,
        "categories": [
            {"id": cat.value, "name": cat.value.replace("_", " ").title()}
            for cat in TemplateCategory
        ]
    }

@router.get("/health", tags=["System"])
async def template_marketplace_health():
    """Health check for template marketplace system"""
    return {
        "status": "healthy",
        "service": "Advanced Template Marketplace",
        "features": [
            "Template Creation & Submission",
            "Marketplace Browsing & Search", 
            "Template Purchasing & Licensing",
            "Review & Rating System",
            "Creator Analytics & Revenue",
            "Advanced Filtering & Sorting"
        ],
        "categories": [cat.value for cat in TemplateCategory],
        "supported_operations": ["CREATE", "READ", "UPDATE", "DELETE", "PURCHASE"],
        "timestamp": datetime.utcnow().isoformat()
    }