"""
Subscription & Payment Management API Routes
Professional Mewayz Platform - Migrated from Monolithic Structure
High-Value Feature Addition
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import uuid
import stripe
import os

from core.auth import get_current_active_user
from core.database import get_database
from services.user_service import get_user_service

router = APIRouter()

# Initialize Stripe
stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
if stripe_secret_key:
    stripe.api_key = stripe_secret_key

# Initialize service instances
user_service = get_user_service()

class SubscriptionPlanResponse(BaseModel):
    plan_id: str
    name: str
    description: str
    price_monthly: float
    price_yearly: float
    features: List[str]
    max_features: int
    is_popular: bool = False

class CreateSubscriptionRequest(BaseModel):
    plan_id: str
    payment_method_id: str
    billing_cycle: str  # monthly or yearly

class PaymentIntentRequest(BaseModel):
    amount: int  # in cents
    currency: str = "usd"
    description: str
    metadata: Optional[Dict[str, Any]] = None

def get_subscriptions_collection():
    """Get subscriptions collection"""
    db = get_database()
    return db.subscriptions

def get_payments_collection():
    """Get payments collection"""
    db = get_database()
    return db.payments

@router.get("/plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    plans = {
        "free": {
            "plan_id": "free",
            "name": "Free Plan",
            "description": "Perfect for getting started",
            "price_monthly": 0.0,
            "price_yearly": 0.0,
            "features": [
                "1 Bio Site",
                "5 Products",
                "3 Services", 
                "Basic Analytics",
                "Email Support",
                "10 AI Requests/month",
                "Basic Templates"
            ],
            "max_features": 50,
            "is_popular": False,
            "stripe_price_monthly": None,
            "stripe_price_yearly": None
        },
        "pro": {
            "plan_id": "pro",
            "name": "Professional", 
            "description": "Everything you need to grow your business",
            "price_monthly": 29.0,
            "price_yearly": 290.0,  # 2 months free
            "features": [
                "Unlimited Bio Sites",
                "Unlimited Products",
                "Unlimited Services",
                "Advanced Analytics",
                "Priority Support",
                "1000 AI Requests/month",
                "Premium Templates",
                "Social Media Management",
                "Email Marketing (10k contacts)",
                "Custom Branding",
                "Advanced Integrations"
            ],
            "max_features": 500,
            "is_popular": True,
            "stripe_price_monthly": os.getenv("STRIPE_PRO_MONTHLY_PRICE_ID"),
            "stripe_price_yearly": os.getenv("STRIPE_PRO_YEARLY_PRICE_ID")
        },
        "enterprise": {
            "plan_id": "enterprise",
            "name": "Enterprise",
            "description": "Advanced features for large organizations",
            "price_monthly": 99.0,
            "price_yearly": 990.0,  # 2 months free
            "features": [
                "Everything in Professional",
                "Unlimited AI Requests",
                "White-label Solutions",
                "Custom Integrations",
                "Dedicated Support",
                "Advanced Security",
                "Team Management",
                "API Access",
                "Custom Domain",
                "Advanced Automation",
                "Priority Feature Requests"
            ],
            "max_features": -1,  # unlimited
            "is_popular": False,
            "stripe_price_monthly": os.getenv("STRIPE_ENTERPRISE_MONTHLY_PRICE_ID"),
            "stripe_price_yearly": os.getenv("STRIPE_ENTERPRISE_YEARLY_PRICE_ID")
        }
    }
    
    return {
        "success": True,
        "data": {
            "plans": plans,
            "currency": "usd",
            "billing_cycles": ["monthly", "yearly"],
            "features_comparison": {
                "free": ["Basic features", "Limited usage", "Community support"],
                "pro": ["Advanced features", "Higher limits", "Priority support"],
                "enterprise": ["Unlimited usage", "Custom solutions", "Dedicated support"]
            }
        }
    }

@router.get("/current")
async def get_current_subscription(current_user: dict = Depends(get_current_active_user)):
    """Get user's current subscription with real database operations"""
    try:
        subscriptions_collection = get_subscriptions_collection()
        
        # Get active subscription
        subscription = await subscriptions_collection.find_one({
            "user_id": current_user["_id"],
            "status": {"$in": ["active", "trialing"]}
        })
        
        # Get user's plan from user service
        user_stats = await user_service.get_user_stats(current_user["_id"])
        current_plan = user_stats["subscription_info"]["plan"]
        
        # Calculate usage metrics
        usage_stats = user_stats["usage_statistics"]
        plan_features = user_stats["subscription_info"]["features_available"]
        
        subscription_data = {
            "plan": current_plan,
            "status": subscription.get("status", "active") if subscription else "active",
            "billing_cycle": subscription.get("billing_cycle", "monthly") if subscription else "monthly",
            "next_billing_date": subscription.get("current_period_end") if subscription else None,
            "cancel_at_period_end": subscription.get("cancel_at_period_end", False) if subscription else False,
            "usage": {
                "bio_sites_used": usage_stats.get("bio_sites_created", 0),
                "bio_sites_limit": 1 if current_plan == "free" else (-1 if current_plan == "enterprise" else 5),
                "products_used": usage_stats.get("products_created", 0),
                "products_limit": 5 if current_plan == "free" else (-1 if current_plan == "enterprise" else 50),
                "ai_requests_used": usage_stats.get("ai_requests_used", 0),
                "ai_requests_limit": plan_features.get("ai_requests_monthly", 10),
                "storage_used": usage_stats.get("storage_used_mb", 0),
                "storage_limit": 100 if current_plan == "free" else (-1 if current_plan == "enterprise" else 1000)
            },
            "features_available": plan_features
        }
        
        return {
            "success": True,
            "data": subscription_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch subscription: {str(e)}"
        )

@router.post("/create")
async def create_subscription(
    request: CreateSubscriptionRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Create subscription with Stripe integration"""
    try:
        if not stripe_secret_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Payment processing not configured"
            )
        
        # Get plan details
        plans_response = await get_subscription_plans()
        plans = plans_response["data"]["plans"]
        
        if request.plan_id not in plans:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid plan selected"
            )
        
        if request.plan_id == "free":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create subscription for free plan"
            )
        
        plan = plans[request.plan_id]
        
        # Get or create Stripe customer
        user_service._ensure_collections()
        users_collection = user_service.users_collection
        user = await users_collection.find_one({"_id": current_user["_id"]})
        
        stripe_customer_id = user.get("stripe_customer_id")
        if not stripe_customer_id:
            # Create Stripe customer
            stripe_customer = stripe.Customer.create(
                email=user["email"],
                name=user["name"],
                metadata={"user_id": current_user["_id"]}
            )
            stripe_customer_id = stripe_customer.id
            
            # Update user with Stripe customer ID
            await users_collection.update_one(
                {"_id": current_user["_id"]},
                {"$set": {"stripe_customer_id": stripe_customer_id}}
            )
        
        # Attach payment method to customer
        stripe.PaymentMethod.attach(
            request.payment_method_id,
            customer=stripe_customer_id
        )
        
        # Set as default payment method
        stripe.Customer.modify(
            stripe_customer_id,
            invoice_settings={
                "default_payment_method": request.payment_method_id
            }
        )
        
        # Get the correct price ID based on billing cycle
        price_id = plan[f"stripe_price_{request.billing_cycle}"]
        if not price_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Price not configured for {request.billing_cycle} billing"
            )
        
        # Create Stripe subscription
        stripe_subscription = stripe.Subscription.create(
            customer=stripe_customer_id,
            items=[{"price": price_id}],
            payment_behavior="default_incomplete",
            payment_settings={"save_default_payment_method": "on_subscription"},
            expand=["latest_invoice.payment_intent"],
        )
        
        # Save subscription to database
        subscriptions_collection = get_subscriptions_collection()
        subscription_doc = {
            "_id": str(uuid.uuid4()),
            "user_id": current_user["_id"],
            "stripe_subscription_id": stripe_subscription.id,
            "stripe_customer_id": stripe_customer_id,
            "plan_id": request.plan_id,
            "billing_cycle": request.billing_cycle,
            "status": stripe_subscription.status,
            "current_period_start": datetime.fromtimestamp(stripe_subscription.current_period_start),
            "current_period_end": datetime.fromtimestamp(stripe_subscription.current_period_end),
            "cancel_at_period_end": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await subscriptions_collection.insert_one(subscription_doc)
        
        # Update user's subscription plan
        await users_collection.update_one(
            {"_id": current_user["_id"]},
            {
                "$set": {
                    "subscription_plan": request.plan_id,
                    "subscription_updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "message": "Subscription created successfully",
            "data": {
                "subscription_id": subscription_doc["_id"],
                "stripe_subscription_id": stripe_subscription.id,
                "client_secret": stripe_subscription.latest_invoice.payment_intent.client_secret if stripe_subscription.latest_invoice.payment_intent else None,
                "status": stripe_subscription.status
            }
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment error: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription: {str(e)}"
        )

@router.post("/cancel")
async def cancel_subscription(current_user: dict = Depends(get_current_active_user)):
    """Cancel subscription with Stripe integration"""
    try:
        subscriptions_collection = get_subscriptions_collection()
        
        # Get active subscription
        subscription = await subscriptions_collection.find_one({
            "user_id": current_user["_id"],
            "status": {"$in": ["active", "trialing"]}
        })
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )
        
        # Cancel Stripe subscription (at period end)
        if stripe_secret_key:
            stripe.Subscription.modify(
                subscription["stripe_subscription_id"],
                cancel_at_period_end=True
            )
        
        # Update subscription in database
        await subscriptions_collection.update_one(
            {"_id": subscription["_id"]},
            {
                "$set": {
                    "cancel_at_period_end": True,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "message": "Subscription will be cancelled at the end of the current billing period",
            "data": {
                "cancellation_date": subscription["current_period_end"]
            }
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment error: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )

@router.post("/reactivate")
async def reactivate_subscription(current_user: dict = Depends(get_current_active_user)):
    """Reactivate cancelled subscription"""
    try:
        subscriptions_collection = get_subscriptions_collection()
        
        # Get subscription that's set to cancel
        subscription = await subscriptions_collection.find_one({
            "user_id": current_user["_id"],
            "status": {"$in": ["active", "trialing"]},
            "cancel_at_period_end": True
        })
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No subscription found to reactivate"
            )
        
        # Reactivate Stripe subscription
        if stripe_secret_key:
            stripe.Subscription.modify(
                subscription["stripe_subscription_id"],
                cancel_at_period_end=False
            )
        
        # Update subscription in database
        await subscriptions_collection.update_one(
            {"_id": subscription["_id"]},
            {
                "$set": {
                    "cancel_at_period_end": False,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "message": "Subscription reactivated successfully"
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment error: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reactivate subscription: {str(e)}"
        )

@router.get("/billing-history")
async def get_billing_history(
    limit: int = 20,
    current_user: dict = Depends(get_current_active_user)
):
    """Get billing history with real database operations"""
    try:
        payments_collection = get_payments_collection()
        
        # Get payment history
        payments = await payments_collection.find(
            {"user_id": current_user["_id"]}
        ).sort("created_at", -1).limit(limit).to_list(length=None)
        
        return {
            "success": True,
            "data": {
                "payments": payments,
                "total_payments": len(payments)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch billing history: {str(e)}"
        )

@router.post("/webhook")
async def stripe_webhook(request):
    """Handle Stripe webhooks for subscription events"""
    # This would handle Stripe webhook events in production
    # For now, return success to prevent webhook failures
    return {"success": True}