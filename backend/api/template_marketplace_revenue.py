"""
Template Marketplace Revenue API
Handle template sales, commissions, and revenue tracking
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from core.auth import get_current_user
from services.template_marketplace_revenue_service import get_template_marketplace_revenue_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check for template marketplace revenue"""
    try:
        service = get_template_marketplace_revenue_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

@router.post("/template-sale")
async def process_template_sale(
    data: Dict[str, Any] = Body(..., description="Template sale data"),
    current_user: dict = Depends(get_current_user)
):
    """Process template sale and calculate commissions"""
    try:
        service = get_template_marketplace_revenue_service()
        result = await service.process_template_sale(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Process template sale error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/seller/earnings")
async def get_seller_earnings(
    period: str = Query("all", description="Period: month, quarter, year, all"),
    current_user: dict = Depends(get_current_user)
):
    """Get seller earnings summary"""
    try:
        service = get_template_marketplace_revenue_service()
        result = await service.get_seller_earnings(
            seller_id=current_user.get("id"),
            period=period
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get seller earnings error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/seller/sales")
async def get_seller_sales(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None, description="Sale status filter"),
    current_user: dict = Depends(get_current_user)
):
    """Get seller's template sales"""
    try:
        service = get_template_marketplace_revenue_service()
        result = await service.get_seller_sales(
            seller_id=current_user.get("id"),
            limit=limit,
            offset=offset,
            status=status
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get seller sales error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/marketplace/analytics")
async def get_marketplace_analytics(
    period: str = Query("month", description="Analytics period"),
    current_user: dict = Depends(get_current_user)
):
    """Get marketplace analytics (admin only)"""
    try:
        # Check if user is admin
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
            
        service = get_template_marketplace_revenue_service()
        result = await service.get_marketplace_analytics(period=period)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get marketplace analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/commission/summary")
async def get_commission_summary(
    period: str = Query("month", description="Commission period"),
    current_user: dict = Depends(get_current_user)
):
    """Get Mewayz commission summary (admin only)"""
    try:
        # Check if user is admin
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
            
        service = get_template_marketplace_revenue_service()
        result = await service.get_commission_summary(period=period)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get commission summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/payout/create")
async def create_seller_payout(
    data: Dict[str, Any] = Body(..., description="Payout data"),
    current_user: dict = Depends(get_current_user)
):
    """Create payout for seller (admin only)"""
    try:
        # Check if user is admin
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
            
        service = get_template_marketplace_revenue_service()
        result = await service.create_seller_payout(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create seller payout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payouts")
async def get_payouts(
    seller_id: Optional[str] = Query(None, description="Filter by seller ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Get payouts (admin can see all, sellers see their own)"""
    try:
        # If not admin, can only see own payouts
        if not current_user.get("is_admin", False):
            seller_id = current_user.get("id")
            
        service = get_template_marketplace_revenue_service()
        result = await service.get_payouts(
            seller_id=seller_id,
            status=status,
            limit=limit,
            offset=offset
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get payouts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/payout/{payout_id}/process")
async def process_payout(
    payout_id: str = Path(..., description="Payout ID"),
    data: Dict[str, Any] = Body(..., description="Processing data"),
    current_user: dict = Depends(get_current_user)
):
    """Process payout (admin only)"""
    try:
        # Check if user is admin
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
            
        data["processed_by"] = current_user.get("id")
        
        service = get_template_marketplace_revenue_service()
        result = await service.process_payout(payout_id, data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Process payout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/template/{template_id}/sales")
async def get_template_sales(
    template_id: str = Path(..., description="Template ID"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Get sales for specific template"""
    try:
        service = get_template_marketplace_revenue_service()
        result = await service.get_template_sales(
            template_id=template_id,
            seller_id=current_user.get("id"),
            limit=limit,
            offset=offset
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get template sales error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refund")
async def process_refund(
    data: Dict[str, Any] = Body(..., description="Refund data"),
    current_user: dict = Depends(get_current_user)
):
    """Process template sale refund (admin only)"""
    try:
        # Check if user is admin
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
            
        data["processed_by"] = current_user.get("id")
        
        service = get_template_marketplace_revenue_service()
        result = await service.process_refund(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Process refund error: {e}")
        raise HTTPException(status_code=500, detail=str(e))