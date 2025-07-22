"""
Multi-Vendor Marketplace API
Complete seller management, commission automation, and marketplace operations
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel

from core.auth import get_current_user
from services.multi_vendor_marketplace_service import marketplace_service
from core.professional_logger import professional_logger, LogLevel, LogCategory

router = APIRouter(prefix="/api/marketplace", tags=["Multi-Vendor Marketplace"])

class SellerOnboarding(BaseModel):
    business_name: str
    business_type: str = "individual"
    email: str
    phone: Optional[str] = None
    address: Dict[str, Any] = {}
    tax_id: Optional[str] = None
    business_license: Optional[str] = None
    bank_account: Dict[str, Any] = {}

class SellerVerification(BaseModel):
    identity_documents_valid: bool = False
    business_license_valid: bool = False
    bank_account_valid: bool = False
    verification_notes: Optional[str] = None

@router.post("/sellers/onboard")
async def onboard_new_seller(
    seller_data: SellerOnboarding,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Onboard new seller with complete profile setup"""
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
        seller_dict = seller_data.dict()
        seller_dict["user_id"] = user_id
        
        seller_id = await marketplace_service.onboard_seller(seller_dict)
        
        return {
            "success": True,
            "seller_id": seller_id,
            "message": "Seller onboarding initiated",
            "next_steps": [
                "Upload required documents",
                "Complete identity verification", 
                "Set up bank account details",
                "Wait for approval"
            ],
            "status": "pending_verification"
        }
        
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.MARKETPLACE,
            f"Seller onboarding failed: {str(e)}",
            error=e, user_id=current_user.get("_id")
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/sellers/{seller_id}/verify")
async def verify_seller_documents(
    seller_id: str,
    verification_data: SellerVerification,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Verify seller documents (admin only)"""
    try:
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        verification_result = await marketplace_service.verify_seller(seller_id, verification_data.dict())
        
        return {
            "success": True,
            "seller_id": seller_id,
            "verification_completed": verification_result,
            "status": "approved" if verification_result else "pending",
            "message": "Seller verification updated"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sellers/{seller_id}/dashboard")
async def get_seller_dashboard(
    seller_id: str,
    days: int = Query(30, description="Analytics period in days"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get comprehensive seller dashboard with analytics"""
    try:
        user_id = current_user.get("_id")
        
        # Verify seller access
        from core.database import get_database
        db = get_database()
        
        seller = await db.marketplace_sellers.find_one({"seller_id": seller_id})
        if not seller:
            raise HTTPException(status_code=404, detail="Seller not found")
        
        if seller["user_id"] != user_id and not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get seller analytics
        analytics = await marketplace_service.get_seller_analytics(seller_id, days)
        
        # Get seller profile
        dashboard = {
            "seller_info": {
                "seller_id": seller_id,
                "business_name": seller.get("business_name"),
                "status": seller.get("status"),
                "tier": seller.get("commission_settings", {}).get("tier", "bronze"),
                "commission_rate": seller.get("commission_settings", {}).get("rate", 15.0),
                "verification": seller.get("verification", {})
            },
            "performance": seller.get("performance_metrics", {}),
            "analytics": analytics,
            "payout_settings": seller.get("payout_settings", {})
        }
        
        return {
            "success": True,
            "dashboard": dashboard,
            "period_days": days
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sellers/{seller_id}/payout")
async def process_seller_payout(
    seller_id: str,
    period: str = Query("weekly", description="Payout period: weekly, biweekly, monthly"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Process automated seller payout"""
    try:
        # Verify admin access or seller ownership
        if not current_user.get("is_admin", False):
            from core.database import get_database
            db = get_database()
            seller = await db.marketplace_sellers.find_one({"seller_id": seller_id})
            if not seller or seller["user_id"] != current_user.get("_id"):
                raise HTTPException(status_code=403, detail="Access denied")
        
        payout_result = await marketplace_service.process_payout(seller_id, period)
        
        return {
            "success": payout_result["payout_processed"],
            "payout_result": payout_result,
            "message": "Payout processed successfully" if payout_result["payout_processed"] else "Payout not processed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sellers/analytics/overview")
async def get_marketplace_overview(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get marketplace overview analytics (admin only)"""
    try:
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        from core.database import get_database
        db = get_database()
        
        # Get marketplace statistics
        total_sellers = await db.marketplace_sellers.count_documents({})
        active_sellers = await db.marketplace_sellers.count_documents({"status": "approved"})
        pending_sellers = await db.marketplace_sellers.count_documents({"status": "pending"})
        
        # Get sales overview
        sales_pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_sales": {"$sum": "$total_amount"},
                    "total_orders": {"$sum": 1},
                    "total_commission": {"$sum": "$commission"}
                }
            }
        ]
        
        sales_result = await db.orders.aggregate(sales_pipeline).to_list(length=1)
        sales_data = sales_result[0] if sales_result else {"total_sales": 0, "total_orders": 0, "total_commission": 0}
        
        # Top performing sellers
        top_sellers = await db.marketplace_sellers.find({}).sort("performance_metrics.total_sales", -1).limit(5).to_list(length=5)
        
        for seller in top_sellers:
            seller["_id"] = str(seller["_id"])
        
        overview = {
            "marketplace_stats": {
                "total_sellers": total_sellers,
                "active_sellers": active_sellers,
                "pending_sellers": pending_sellers,
                "approval_rate": (active_sellers / total_sellers * 100) if total_sellers > 0 else 0
            },
            "sales_overview": sales_data,
            "top_performers": top_sellers,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "overview": overview
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/commission/calculate")
async def calculate_order_commission(
    seller_id: str,
    order_amount: float,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Calculate commission for an order"""
    try:
        commission_data = await marketplace_service.calculate_commission(seller_id, order_amount)
        
        return {
            "success": True,
            "commission_breakdown": commission_data,
            "order_amount": order_amount
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sellers/{seller_id}/performance")
async def get_seller_performance_metrics(
    seller_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get detailed seller performance metrics"""
    try:
        from core.database import get_database
        db = get_database()
        
        # Verify access
        seller = await db.marketplace_sellers.find_one({"seller_id": seller_id})
        if not seller:
            raise HTTPException(status_code=404, detail="Seller not found")
        
        if seller["user_id"] != current_user.get("_id") and not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get comprehensive performance data
        performance = seller.get("performance_metrics", {})
        
        # Get recent reviews/ratings
        reviews = await db.seller_reviews.find({"seller_id": seller_id}).sort("created_at", -1).limit(10).to_list(length=10)
        
        for review in reviews:
            review["_id"] = str(review["_id"])
            if "created_at" in review:
                review["created_at"] = review["created_at"].isoformat()
        
        return {
            "success": True,
            "performance": {
                "metrics": performance,
                "commission_tier": seller.get("commission_settings", {}).get("tier"),
                "verification_status": seller.get("verification", {}),
                "recent_reviews": reviews,
                "status": seller.get("status")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
