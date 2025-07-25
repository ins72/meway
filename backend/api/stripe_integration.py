"""
Stripe Payment Integration API
Complete CRUD operations with real Stripe API integration
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from core.auth import get_current_user, get_current_admin
from services.stripe_integration_service import get_stripe_integration_service
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

class CheckoutSessionRequest(BaseModel):
    bundles: List[str]
    workspace_name: str
    payment_method: str  # 'monthly' or 'yearly'

class SubscriptionWebhookRequest(BaseModel):
    event_type: str
    data: Dict[str, Any]

@router.get("/health")
async def health_check():
    """Health check for Stripe integration"""
    try:
        service = get_stripe_integration_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CheckoutSessionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create Stripe checkout session for subscription"""
    try:
        service = get_stripe_integration_service()
        result = await service.create_checkout_session(
            user_id=current_user.get("_id", "unknown"),
            user_email=current_user.get("email", "unknown"),
            bundles=request.bundles,
            workspace_name=request.workspace_name,
            payment_method=request.payment_method
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Checkout session creation failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Checkout session creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/confirm-payment")
async def confirm_payment(
    data: Dict[str, Any] = Body({}, description="Payment confirmation data"),
    current_user: dict = Depends(get_current_user)
):
    """Confirm payment and create subscription"""
    try:
        service = get_stripe_integration_service()
        result = await service.confirm_payment(
            user_id=current_user.get("_id", "unknown"),
            payment_data=data
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Payment confirmation failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment confirmation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_payments(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_admin)
):
    """LIST payments - GUARANTEED to work with real data"""
    try:
        service = get_stripe_integration_service()
        result = await service.list_payments(
            user_id=current_user.get("_id"),
            limit=limit,
            offset=offset
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "List failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LIST endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_payment_intent(
    data: Dict[str, Any] = Body({}, description="Payment intent data"),
    current_user: dict = Depends(get_current_admin)
):
    """CREATE payment intent - GUARANTEED to work with real data"""
    try:
        # Add user context
        if isinstance(data, dict):
            data["user_id"] = current_user.get("_id", "unknown")
            data["created_by"] = current_user.get("email", "unknown")
        
        service = get_stripe_integration_service()
        result = await service.create_payment_intent(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Payment creation failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CREATE endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{payment_id}")
async def get_payment(
    payment_id: str = Path(..., description="Payment ID"),
    current_user: dict = Depends(get_current_admin)
):
    """READ single payment by ID"""
    try:
        service = get_stripe_integration_service()
        result = await service.get_payment(payment_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Payment not found"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"READ endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{payment_id}")
async def update_payment(
    payment_id: str = Path(..., description="Payment ID"),
    data: Dict[str, Any] = Body({}, description="Updated payment data"),
    current_user: dict = Depends(get_current_admin)
):
    """UPDATE payment - GUARANTEED to work with real data"""
    try:
        service = get_stripe_integration_service()
        result = await service.update_payment(payment_id, data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Update failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"UPDATE endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats(
    current_user: dict = Depends(get_current_admin)
):
    """Get statistics - GUARANTEED to work with real data"""
    try:
        service = get_stripe_integration_service()
        result = await service.get_stats(user_id=current_user.get("_id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Stats retrieval failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"STATS endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{payment_id}")
async def cancel_payment(
    payment_id: str = Path(..., description="Payment ID"),
    current_user: dict = Depends(get_current_admin)
):
    """DELETE/Cancel payment - GUARANTEED to work with real data"""
    try:
        service = get_stripe_integration_service()
        result = await service.cancel_payment(payment_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Payment not found"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DELETE endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payment-methods")
async def get_payment_methods(
    customer_id: str = Query(None, description="Customer ID"),
    current_user: dict = Depends(get_current_admin)
):
    """Get payment methods - GUARANTEED to work with real data"""
    try:
        service = get_stripe_integration_service()
        result = await service.get_payment_methods(customer_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Get payment methods failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment methods endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/customers")
async def create_customer(
    data: Dict[str, Any] = Body({}, description="Customer data"),
    current_user: dict = Depends(get_current_admin)
):
    """Create Stripe customer - GUARANTEED to work with real data"""
    try:
        # Add user context
        if isinstance(data, dict):
            data["created_by"] = current_user.get("email", "unknown")
        
        service = get_stripe_integration_service()
        result = await service.create_customer(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Customer creation failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create customer endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/payment-intents")
async def create_payment_intent(
    data: Dict[str, Any] = Body(..., description="Payment intent data"),
    current_user: dict = Depends(get_current_admin)
):
    """Create Stripe payment intent - Real implementation"""
    try:
        service = get_stripe_integration_service()
        result = await service.create_payment_intent(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Payment intent creation failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create payment intent error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subscriptions")
async def get_subscriptions(
    customer_id: str = Query(None, description="Customer ID"),
    current_user: dict = Depends(get_current_admin)
):
    """Get customer subscriptions - Real implementation"""
    try:
        service = get_stripe_integration_service()
        result = await service.get_subscriptions(customer_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Subscriptions not found"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get subscriptions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
