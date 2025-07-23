"""
Advanced Template Marketplace API
Complete template creation, selling, monetization, and usage endpoints
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
import uuid

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field

from core.auth import get_current_user
from services.advanced_template_marketplace_service import advanced_template_marketplace_service, TemplateCategory, TemplateStatus, AdvancedTemplateMarketplaceService
from typing import Dict, Any, List, Optional
from core.auth import get_current_active_user

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
        # Debug: Check if we have user info
        if not current_user or not current_user.get("_id"):
            raise HTTPException(status_code=401, detail="Invalid user authentication")
        
        # Normalize request data - handle both 'name' and 'title' fields
        data = request.dict()
        if not data.get('title') and data.get('name'):
            data['title'] = data['name']
        elif not data.get('title'):
            data['title'] = "Untitled Template"
        
        # Ensure required fields
        if not data.get('description'):
            raise HTTPException(status_code=400, detail="Description is required")
        if not data.get('category'):
            raise HTTPException(status_code=400, detail="Category is required")
            
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Template creation failed: {str(e)}")

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
    try:
        categories = await advanced_template_marketplace_service.get_categories()
        return {
            "success": True,
            "categories": categories,
            "message": "Categories retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/creator/analytics", tags=["Creator Analytics"])
async def get_creator_analytics(
    period: str = Query("month", pattern="^(week|month|quarter|year)$"),
    current_user: dict = Depends(get_current_user)
):
    """Get REAL creator analytics from database"""
    try:
        analytics = await advanced_template_marketplace_service.get_creator_analytics(
            creator_id=current_user["_id"],
            period=period
        )
        
        return {
            "success": True,
            "analytics": analytics,
            "message": "Real creator analytics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting creator analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-templates", tags=["Creator Analytics"])
async def get_my_templates(
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Get creator's REAL templates from database"""
    try:
        result = await advanced_template_marketplace_service.get_my_templates(
            creator_id=current_user["_id"],
            status=status
        )
        
        return {
            "success": True,
            **result,
            "message": "Real templates retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting my templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/purchases", tags=["Template Usage"])
async def get_my_purchases(
    current_user: dict = Depends(get_current_user)
):
    """Get user's REAL purchases from database"""
    try:
        result = await advanced_template_marketplace_service.get_user_purchases(
            user_id=current_user["_id"]
        )
        
        return {
            "success": True,
            **result,
            "message": "Real purchases retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting purchases: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/marketplace/featured", tags=["Template Browsing"])
async def get_featured_templates(limit: int = Query(10, ge=1, le=50)):
    """Get REAL featured templates from database"""
    try:
        templates = await advanced_template_marketplace_service.get_featured_templates(limit)
        
        return {
            "success": True,
            "templates": templates,
            "count": len(templates),
            "message": "Real featured templates retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting featured templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/creator/revenue", tags=["Creator Analytics"])
async def get_creator_revenue(
    period: str = Query("month", pattern="^(week|month|quarter|year)$"),
    current_user: dict = Depends(get_current_user)
):
    """Get creator revenue breakdown"""
    try:
        revenue_data = await advanced_template_marketplace_service.get_creator_revenue(
            creator_id=current_user["_id"],
            period=period
        )
        
        return {
            "success": True,
            "revenue": revenue_data,
            "message": "Creator revenue retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting creator revenue: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# NEW CRUD OPERATIONS - UPDATE AND DELETE

class TemplateUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = Field(None, min_length=20, max_length=1000)
    category: Optional[str] = None
    subcategory: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    template_data: Optional[Dict[str, Any]] = None
    preview_url: Optional[str] = None
    preview_images: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

@router.put("/templates/{template_id}", tags=["Template Management"])
async def update_template(
    template_id: str,
    request: TemplateUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update existing template (creator only)"""
    try:
        # Verify ownership
        template = await advanced_template_marketplace_service.get_template_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        if template.get("creator_id") != current_user["_id"]:
            raise HTTPException(status_code=403, detail="Not authorized to update this template")
        
        # Update template
        updated_template = await advanced_template_marketplace_service.update_template(
            template_id=template_id,
            updates=request.dict(exclude_unset=True)
        )
        
        return {
            "success": True,
            "template": updated_template,
            "message": "Template updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Template update failed: {str(e)}")

@router.delete("/templates/{template_id}", tags=["Template Management"])
async def delete_template(
    template_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete template (creator only)"""
    try:
        # Verify ownership
        template = await advanced_template_marketplace_service.get_template_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        if template.get("creator_id") != current_user["_id"]:
            raise HTTPException(status_code=403, detail="Not authorized to delete this template")
        
        # Delete template
        result = await advanced_template_marketplace_service.delete_template(template_id)
        
        return {
            "success": True,
            "message": "Template deleted successfully",
            "template_id": template_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Template deletion failed: {str(e)}")

@router.get("/templates", tags=["Template Management"])
async def get_templates(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    creator_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    """Get templates with filtering (READ operation)"""
    try:
        filters = {}
        if category:
            filters["category"] = category
        if status:
            filters["status"] = status
        if creator_id:
            filters["creator_id"] = creator_id
            
        skip = (page - 1) * per_page
        
        result = await advanced_template_marketplace_service.get_templates(
            filters=filters,
            limit=per_page,
            skip=skip
        )
        
        return {
            "success": True,
            **result,
            "message": "Templates retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{template_id}", tags=["Template Management"])
async def get_template_by_id(template_id: str):
    """Get specific template by ID"""
    try:
        template = await advanced_template_marketplace_service.get_template_by_id(template_id)
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "success": True,
            "template": template,
            "message": "Template retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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

# Create a simple service instance
advanced_template_marketplace_service = AdvancedTemplateMarketplaceService()