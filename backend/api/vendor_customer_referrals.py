"""
Vendor Customer Referrals API
Allow vendors to create referral programs for their customers
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from core.auth import get_current_user
from services.vendor_customer_referrals_service import get_vendor_customer_referrals_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check for vendor customer referrals"""
    try:
        service = get_vendor_customer_referrals_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

@router.post("/program")
async def create_referral_program(
    data: Dict[str, Any] = Body(..., description="Referral program data"),
    current_user: dict = Depends(get_current_user)
):
    """Create vendor customer referral program"""
    try:
        data["vendor_id"] = current_user.get("id")
        data["workspace_id"] = current_user.get("workspace_id")
        
        service = get_vendor_customer_referrals_service()
        result = await service.create_referral_program(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create referral program error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/program/{program_id}")
async def get_referral_program(
    program_id: str = Path(..., description="Referral program ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get referral program details"""
    try:
        service = get_vendor_customer_referrals_service()
        result = await service.get_referral_program(
            program_id=program_id,
            vendor_id=current_user.get("id")
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get referral program error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/program/{program_id}")
async def update_referral_program(
    program_id: str = Path(..., description="Referral program ID"),
    data: Dict[str, Any] = Body(..., description="Update data"),
    current_user: dict = Depends(get_current_user)
):
    """Update referral program"""
    try:
        data["vendor_id"] = current_user.get("id")
        
        service = get_vendor_customer_referrals_service()
        result = await service.update_referral_program(program_id, data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update referral program error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/program/{program_id}")
async def delete_referral_program(
    program_id: str = Path(..., description="Referral program ID"),
    current_user: dict = Depends(get_current_user)
):
    """Delete referral program"""
    try:
        service = get_vendor_customer_referrals_service()
        result = await service.delete_referral_program(
            program_id=program_id,
            vendor_id=current_user.get("id")
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete referral program error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/programs")
async def list_referral_programs(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """List vendor's referral programs"""
    try:
        service = get_vendor_customer_referrals_service()
        result = await service.list_referral_programs(
            vendor_id=current_user.get("id"),
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
        logger.error(f"List referral programs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/referral/generate")
async def generate_referral_link(
    data: Dict[str, Any] = Body(..., description="Referral link data"),
    current_user: dict = Depends(get_current_user)
):
    """Generate referral link for customer"""
    try:
        service = get_vendor_customer_referrals_service()
        result = await service.generate_referral_link(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate referral link error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/referral/purchase")
async def process_referral_purchase(
    data: Dict[str, Any] = Body(..., description="Referral purchase data"),
    current_user: dict = Depends(get_current_user)
):
    """Process purchase with referral tracking"""
    try:
        service = get_vendor_customer_referrals_service()
        result = await service.process_referral_purchase(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Process referral purchase error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/referral/analytics/{program_id}")
async def get_referral_analytics(
    program_id: str = Path(..., description="Referral program ID"),
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_user)
):
    """Get referral program analytics"""
    try:
        service = get_vendor_customer_referrals_service()
        result = await service.get_referral_analytics(
            program_id=program_id,
            vendor_id=current_user.get("id"),
            days=days
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get referral analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/referral/payouts")
async def get_referral_payouts(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None, description="Payout status filter"),
    current_user: dict = Depends(get_current_user)
):
    """Get referral payouts for vendor"""
    try:
        service = get_vendor_customer_referrals_service()
        result = await service.get_referral_payouts(
            vendor_id=current_user.get("id"),
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
        logger.error(f"Get referral payouts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/referral/payout/{payout_id}/process")
async def process_referral_payout(
    payout_id: str = Path(..., description="Payout ID"),
    current_user: dict = Depends(get_current_user)
):
    """Process referral payout (admin only)"""
    try:
        service = get_vendor_customer_referrals_service()
        result = await service.process_referral_payout(
            payout_id=payout_id,
            processed_by=current_user.get("id")
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Process referral payout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))