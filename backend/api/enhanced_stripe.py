"""
Enhanced Stripe API with Customer Management, Payment Methods, and Webhooks
Following Stripe best practices 2025 for comprehensive payment management
"""

from fastapi import APIRouter, HTTPException, Depends, Body, Request, Header
from typing import Dict, Any, List, Optional
from core.auth import get_current_user
from services.stripe_customer_service import StripeCustomerService
from services.stripe_webhook_service import StripeWebhookService
import stripe
import os
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

router = APIRouter()

# Initialize services
customer_service = StripeCustomerService()
webhook_service = StripeWebhookService()

class PaymentIntentRequest(BaseModel):
    amount: int  # Amount in cents
    currency: str = 'usd'
    bundles: Optional[List[str]] = []
    workspace_name: Optional[str] = ''
    save_payment_method: Optional[bool] = True

class SubscriptionRequest(BaseModel):
    price_ids: List[str]
    workspace_name: str
    trial_days: Optional[int] = 14

class PaymentMethodRequest(BaseModel):
    payment_method_id: str
    set_as_default: Optional[bool] = False

@router.post("/create-setup-intent")
async def create_setup_intent(
    current_user: dict = Depends(get_current_user)
):
    """Create setup intent for saving payment methods"""
    try:
        # Create or get Stripe customer
        customer_result = await customer_service.create_or_get_customer(
            user_id=current_user.get("_id", ""),
            user_email=current_user.get("email", ""),
            user_name=current_user.get("full_name", "")
        )
        
        if not customer_result.get("success"):
            raise HTTPException(status_code=400, detail=customer_result.get("error"))
        
        # Create setup intent
        setup_intent = stripe.SetupIntent.create(
            customer=customer_result["stripe_customer"].id,
            payment_method_types=['card'],
            usage='off_session',
            metadata={
                'user_id': current_user.get("_id", ""),
                'purpose': 'save_payment_method'
            }
        )
        
        return {
            "success": True,
            "client_secret": setup_intent.client_secret,
            "setup_intent_id": setup_intent.id
        }
        
    except Exception as e:
        logger.error(f"Setup intent creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-payment-intent")
async def create_payment_intent(
    request: PaymentIntentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create payment intent with customer creation and payment method saving"""
    try:
        # Validate amount
        if request.amount < 50:
            raise HTTPException(status_code=400, detail="Amount too small")
        if request.amount > 99999999:
            raise HTTPException(status_code=400, detail="Amount too large")

        # Create or get Stripe customer
        customer_result = await customer_service.create_or_get_customer(
            user_id=current_user.get("_id", ""),
            user_email=current_user.get("email", ""),
            user_name=current_user.get("full_name", "")
        )
        
        if not customer_result.get("success"):
            raise HTTPException(status_code=400, detail=customer_result.get("error"))

        # Create payment intent
        payment_intent_data = {
            "amount": request.amount,
            "currency": request.currency,
            "customer": customer_result["stripe_customer"].id,
            "automatic_payment_methods": {"enabled": True},
            "metadata": {
                'user_id': current_user.get("_id", ""),
                'user_email': current_user.get("email", ""),
                'bundles': ','.join(request.bundles) if request.bundles else '',
                'workspace_name': request.workspace_name or '',
            }
        }
        
        if request.save_payment_method:
            payment_intent_data["setup_future_usage"] = "off_session"

        intent = stripe.PaymentIntent.create(**payment_intent_data)

        return {
            'success': True,
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id,
            'amount': intent.amount,
            'currency': intent.currency,
            'status': intent.status,
            'customer_id': customer_result["stripe_customer"].id
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Payment intent creation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create payment intent")

@router.post("/create-subscription")
async def create_subscription(
    request: SubscriptionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create subscription for customer"""
    try:
        subscription_result = await customer_service.create_subscription(
            user_id=current_user.get("_id", ""),
            price_ids=request.price_ids,
            workspace_name=request.workspace_name,
            trial_days=request.trial_days
        )
        
        if not subscription_result.get("success"):
            raise HTTPException(status_code=400, detail=subscription_result.get("error"))
        
        return subscription_result
        
    except Exception as e:
        logger.error(f"Subscription creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payment-methods")
async def get_payment_methods(
    current_user: dict = Depends(get_current_user)
):
    """Get user's saved payment methods"""
    try:
        result = await customer_service.get_customer_payment_methods(
            user_id=current_user.get("_id", "")
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        logger.error(f"Get payment methods error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save-payment-method")
async def save_payment_method(
    request: PaymentMethodRequest,
    current_user: dict = Depends(get_current_user)
):
    """Save payment method to customer account"""
    try:
        result = await customer_service.save_payment_method(
            user_id=current_user.get("_id", ""),
            payment_method_id=request.payment_method_id,
            set_as_default=request.set_as_default
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        logger.error(f"Save payment method error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/default-payment-method/{payment_method_id}")
async def set_default_payment_method(
    payment_method_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Set default payment method for customer"""
    try:
        result = await customer_service.update_default_payment_method(
            user_id=current_user.get("_id", ""),
            payment_method_id=payment_method_id
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        logger.error(f"Update default payment method error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def handle_stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature")
):
    """Handle Stripe webhooks"""
    try:
        if not stripe_signature:
            raise HTTPException(status_code=400, detail="Missing stripe-signature header")
        
        # Get raw body
        body = await request.body()
        
        # Verify webhook signature
        verification_result = await webhook_service.verify_webhook_signature(
            payload=body,
            signature=stripe_signature
        )
        
        if not verification_result.get("success"):
            raise HTTPException(status_code=400, detail=verification_result.get("error"))
        
        # Handle webhook event
        event = verification_result["event"]
        result = await webhook_service.handle_webhook_event(event)
        
        logger.info(f"Webhook processed: {event.get('type')} - {result}")
        
        return {"received": True, "processed": result.get("processed", False)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.get("/customer")
async def get_customer_info(
    current_user: dict = Depends(get_current_user)
):
    """Get customer information and payment status"""
    try:
        # Get customer from service
        customer_result = await customer_service.create_or_get_customer(
            user_id=current_user.get("_id", ""),
            user_email=current_user.get("email", ""),
            user_name=current_user.get("full_name", "")
        )
        
        if not customer_result.get("success"):
            raise HTTPException(status_code=400, detail=customer_result.get("error"))
        
        # Get payment methods
        payment_methods_result = await customer_service.get_customer_payment_methods(
            user_id=current_user.get("_id", "")
        )
        
        return {
            "success": True,
            "customer": customer_result["customer"],
            "stripe_customer": {
                "id": customer_result["stripe_customer"].id,
                "email": customer_result["stripe_customer"].email,
                "created": customer_result["stripe_customer"].created
            },
            "payment_methods": payment_methods_result.get("payment_methods", []),
            "default_payment_method": payment_methods_result.get("default_payment_method")
        }
        
    except Exception as e:
        logger.error(f"Get customer error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payment-intent/{payment_intent_id}")
async def get_payment_intent(
    payment_intent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get payment intent details"""
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        # Verify this payment intent belongs to the current user
        if intent.metadata.get('user_id') != current_user.get("_id", ""):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            'success': True,
            'id': intent.id,
            'amount': intent.amount,
            'currency': intent.currency,
            'status': intent.status,
            'client_secret': intent.client_secret,
            'metadata': intent.metadata
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Payment intent retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve payment intent")

@router.post("/confirm-payment-success")
async def confirm_payment_success(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Confirm payment success and handle post-payment actions"""
    try:
        payment_intent_id = data.get("payment_intent_id")
        
        if not payment_intent_id:
            raise HTTPException(status_code=400, detail="Payment intent ID required")
        
        # Retrieve payment intent
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        # Verify payment intent belongs to user and is successful
        if intent.metadata.get('user_id') != current_user.get("_id", ""):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if intent.status != 'succeeded':
            raise HTTPException(status_code=400, detail="Payment not successful")
        
        # Handle post-payment actions
        workspace_name = intent.metadata.get('workspace_name')
        bundles = intent.metadata.get('bundles', '').split(',')
        
        if workspace_name and bundles:
            # This is an onboarding payment - trigger workspace creation
            workspace_result = await webhook_service._create_onboarding_workspace(
                user_id=current_user.get("_id", ""),
                workspace_name=workspace_name,
                bundles=[b.strip() for b in bundles if b.strip()]
            )
            
            return {
                "success": True,
                "payment_confirmed": True,
                "workspace_created": workspace_result.get("success", False),
                "redirect_url": f"/workspace/{workspace_result.get('workspace_id', 'default')}/dashboard",
                "workspace_name": workspace_name,
                "bundles": bundles
            }
        
        return {
            "success": True,
            "payment_confirmed": True,
            "message": "Payment processed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment confirmation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Enhanced health check for payment system"""
    try:
        # Test Stripe connection
        account = stripe.Account.retrieve()
        
        return {
            "success": True,
            "healthy": True,
            "stripe_connected": True,
            "account_id": account.id,
            "country": account.country,
            "api_version": stripe.api_version,
            "services": {
                "customer_management": True,
                "payment_methods": True,
                "webhooks": True,
                "subscriptions": True
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "success": False,
            "healthy": False,
            "stripe_connected": False,
            "error": str(e)
        }