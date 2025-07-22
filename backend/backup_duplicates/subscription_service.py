"""
Subscription Management Services Business Logic
Professional Mewayz Platform
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from core.database import get_database
import uuid

class SubscriptionService:
    """Service for subscription management operations"""
    
    @staticmethod
    async def get_subscription_plans():
        """Get available subscription plans"""
        plans = [
            {
                "id": "free",
                "name": "Free",
                "price": 0,
                "interval": "month",
                "features": [
                    "Up to 3 workspaces",
                    "Basic analytics",
                    "1000 AI tokens/month",
                    "Email support"
                ],
                "limits": {
                    "workspaces": 3,
                    "users": 5,
                    "ai_tokens": 1000
                }
            },
            {
                "id": "pro",
                "name": "Professional",
                "price": 29,
                "interval": "month",
                "features": [
                    "Unlimited workspaces",
                    "Advanced analytics",
                    "10000 AI tokens/month",
                    "Priority support",
                    "Custom branding"
                ],
                "limits": {
                    "workspaces": -1,  # unlimited
                    "users": 25,
                    "ai_tokens": 10000
                }
            },
            {
                "id": "enterprise",
                "name": "Enterprise",
                "price": 99,
                "interval": "month",
                "features": [
                    "Everything in Pro",
                    "Unlimited users",
                    "50000 AI tokens/month",
                    "24/7 support",
                    "API access",
                    "Custom integrations"
                ],
                "limits": {
                    "workspaces": -1,
                    "users": -1,
                    "ai_tokens": 50000
                }
            }
        ]
        return plans
    
    @staticmethod
    async def get_user_subscription(user_id: str):
        """Get user's current subscription"""
        db = await get_database()
        
        subscription = await db.subscriptions.find_one({"user_id": user_id})
        if not subscription:
            # Create free subscription for new users
            subscription = {
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                "plan_id": "free",
                "status": "active",
                "started_at": datetime.utcnow(),
                "current_period_start": datetime.utcnow(),
                "current_period_end": datetime.utcnow() + timedelta(days=30),
                "created_at": datetime.utcnow()
            }
            await db.subscriptions.insert_one(subscription)
        
        return subscription
    
    @staticmethod
    async def upgrade_subscription(user_id: str, plan_id: str):
        """Upgrade user's subscription"""
        db = await get_database()
        
        current_subscription = await SubscriptionService.get_user_subscription(user_id)
        
        # Update subscription
        new_subscription = {
            "plan_id": plan_id,
            "status": "active",
            "started_at": datetime.utcnow(),
            "current_period_start": datetime.utcnow(),
            "current_period_end": datetime.utcnow() + timedelta(days=30),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.subscriptions.update_one(
            {"user_id": user_id},
            {"$set": new_subscription}
        )
        
        return await db.subscriptions.find_one({"user_id": user_id})
    
    @staticmethod
    async def check_subscription_limits(user_id: str, resource_type: str):
        """Check if user has reached subscription limits"""
        db = await get_database()
        
        subscription = await SubscriptionService.get_user_subscription(user_id)
        plans = await SubscriptionService.get_subscription_plans()
        
        current_plan = next(p for p in plans if p["id"] == subscription["plan_id"])
        limit = current_plan["limits"].get(resource_type, 0)
        
        if limit == -1:  # unlimited
            return {"within_limits": True, "limit": "unlimited", "current": 0}
        
        # Count current usage
        if resource_type == "workspaces":
            current_count = await db.workspaces.count_documents({"user_id": user_id})
        elif resource_type == "users":
            current_count = await db.team_members.count_documents({"owner_id": user_id})
        else:
            current_count = 0
        
        return {
            "within_limits": current_count < limit,
            "limit": limit,
            "current": current_count
        }

# Global service instance
subscription_service = SubscriptionService()
