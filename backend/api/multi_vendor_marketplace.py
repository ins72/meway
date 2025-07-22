"""
Multi-Vendor Marketplace API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Optional
from pydantic import BaseModel
from core.auth import get_current_user
from core.database import get_database
from services.multi_vendor_marketplace_service import MultiVendorMarketplaceService

router = APIRouter(prefix="/api/marketplace", tags=["Multi-Vendor Marketplace"])

class VendorOnboardingRequest(BaseModel):
    business_name: str
    owner_name: str
    email: str
    phone: str
    business_type: str
    tax_id: str
    address: Dict
    bank_details: Dict
    documents: List[str] = []

class DynamicPricingRequest(BaseModel):
    product_id: str
    base_price: float
    demand_factor: float = 1.0
    competition_avg: Optional[float] = None
    inventory_level: int = 100

@router.post("/vendors/onboard")
async def onboard_vendor(
    vendor_data: VendorOnboardingRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Onboard new vendor to marketplace"""
    marketplace_service = MultiVendorMarketplaceService(db)
    result = await marketplace_service.vendor_onboarding(vendor_data.dict())
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Vendor application submitted successfully", "data": result}

@router.post("/vendors/{vendor_id}/approve")
async def approve_vendor(
    vendor_id: str,
    admin_notes: str = "",
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Approve vendor application (Admin only)"""
    # In real implementation, check if user is admin
    marketplace_service = MultiVendorMarketplaceService(db)
    result = await marketplace_service.approve_vendor(vendor_id, admin_notes)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Vendor approved successfully", "data": result}

@router.post("/pricing/dynamic")
async def calculate_dynamic_pricing(
    pricing_request: DynamicPricingRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Calculate AI-optimized dynamic pricing"""
    marketplace_service = MultiVendorMarketplaceService(db)
    
    market_data = pricing_request.dict()
    result = await marketplace_service.calculate_dynamic_pricing(
        pricing_request.product_id, 
        market_data
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Dynamic pricing calculated", "data": result}

@router.post("/vendors/{vendor_id}/payout")
async def process_vendor_payout(
    vendor_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Process automated vendor payout"""
    marketplace_service = MultiVendorMarketplaceService(db)
    result = await marketplace_service.process_vendor_payout(vendor_id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Payout processed successfully", "data": result}

@router.get("/vendors/{vendor_id}/performance")
async def get_vendor_performance(
    vendor_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get comprehensive vendor performance metrics"""
    marketplace_service = MultiVendorMarketplaceService(db)
    result = await marketplace_service.get_seller_performance_metrics(vendor_id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Performance metrics retrieved", "data": result}

@router.get("/vendors")
async def list_vendors(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """List all vendors with optional status filter"""
    filter_query = {}
    if status:
        filter_query["status"] = status
    
    vendors = await db["vendors"].find(filter_query).to_list(length=100)
    
    return {
        "message": "Vendors retrieved successfully",
        "data": vendors,
        "count": len(vendors)
    }

@router.get("/vendors/applications")
async def list_vendor_applications(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """List all vendor applications (Admin only)"""
    applications = await db["vendor_applications"].find({}).sort("submitted_at", -1).to_list(length=50)
    
    return {
        "message": "Vendor applications retrieved",
        "data": applications,
        "count": len(applications)
    }
