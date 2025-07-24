"""
Simple Stripe Payment Integration
Following official Stripe documentation best practices
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any, List, Optional
from core.auth import get_current_user
import stripe
import os
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

router = APIRouter()

class PaymentIntentRequest(BaseModel):
    amount: int  # Amount in cents
    currency: str = 'usd'
    bundles: Optional[List[str]] = []
    workspace_name: Optional[str] = ''
    automatic_payment_methods: Optional[Dict[str, Any]] = {'enabled': True}

@router.post("/create-payment-intent")
async def create_payment_intent(
    request: PaymentIntentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a PaymentIntent with the order amount and currency"""
    try:
        # Validate amount
        if request.amount < 50:  # Minimum 50 cents
            raise HTTPException(status_code=400, detail="Amount too small")
        
        if request.amount > 99999999:  # Maximum $999,999.99
            raise HTTPException(status_code=400, detail="Amount too large")

        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=request.amount,
            currency=request.currency,
            automatic_payment_methods=request.automatic_payment_methods,
            metadata={
                'user_id': str(current_user.get('_id', '')),
                'user_email': current_user.get('email', ''),
                'bundles': ','.join(request.bundles) if request.bundles else '',
                'workspace_name': request.workspace_name or '',
            }
        )

        return {
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id,
            'amount': intent.amount,
            'currency': intent.currency,
            'status': intent.status
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Payment intent creation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create payment intent")

@router.get("/payment-intent/{payment_intent_id}")
async def get_payment_intent(
    payment_intent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Retrieve a PaymentIntent"""
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        # Verify this payment intent belongs to the current user
        if intent.metadata.get('user_id') != str(current_user.get('_id', '')):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
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

@router.post("/webhook")
async def stripe_webhook(request_body: bytes = Body(...)):
    """Handle Stripe webhooks"""
    try:
        endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        if not endpoint_secret:
            logger.warning("No webhook secret configured")
            return {"received": True}
        
        sig_header = request.headers.get('stripe-signature')
        
        try:
            event = stripe.Webhook.construct_event(
                request_body, sig_header, endpoint_secret
            )
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            raise HTTPException(status_code=400, detail="Invalid signature")

        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            logger.info(f"PaymentIntent succeeded: {payment_intent['id']}")
            
            # TODO: Fulfill the order, update database, send confirmation email, etc.
            await handle_successful_payment(payment_intent)
            
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            logger.info(f"PaymentIntent failed: {payment_intent['id']}")
            
            # TODO: Handle failed payment
            await handle_failed_payment(payment_intent)
            
        else:
            logger.info(f"Unhandled event type: {event['type']}")

        return {"received": True}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

async def handle_successful_payment(payment_intent):
    """Handle successful payment"""
    try:
        user_id = payment_intent['metadata'].get('user_id')
        bundles = payment_intent['metadata'].get('bundles', '').split(',')
        workspace_name = payment_intent['metadata'].get('workspace_name', '')
        
        logger.info(f"Processing successful payment for user {user_id}")
        logger.info(f"Bundles: {bundles}")
        logger.info(f"Workspace: {workspace_name}")
        
        # TODO: Implement your business logic here:
        # 1. Create/update workspace subscription
        # 2. Activate bundles for user
        # 3. Send confirmation email
        # 4. Update user's onboarding status
        # 5. Log transaction in database
        
    except Exception as e:
        logger.error(f"Error handling successful payment: {e}")

async def handle_failed_payment(payment_intent):
    """Handle failed payment"""
    try:
        user_id = payment_intent['metadata'].get('user_id')
        logger.info(f"Processing failed payment for user {user_id}")
        
        # TODO: Implement your business logic here:
        # 1. Log failed payment
        # 2. Send notification to user
        # 3. Update payment status in database
        
    except Exception as e:
        logger.error(f"Error handling failed payment: {e}")

@router.get("/health")
async def health_check():
    """Health check for Stripe integration"""
    try:
        # Test Stripe connection
        stripe.Account.retrieve()
        return {
            "success": True,
            "healthy": True,
            "stripe_connected": True,
            "api_version": stripe.api_version
        }
    except Exception as e:
        logger.error(f"Stripe health check failed: {e}")
        return {
            "success": False,
            "healthy": False,
            "stripe_connected": False,
            "error": str(e)
        }