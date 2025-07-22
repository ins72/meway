"""
Integration Services Business Logic
Professional Mewayz Platform
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database
import uuid

class IntegrationService:
    """Service for third-party integration operations"""
    
    @staticmethod
    async def get_available_integrations():
        """Get list of available integrations"""
        integrations = {
    "social_media": [
    {
    "name": "TikTok & Twitter/X
    "description": "Connect your TikTok & Twitter/X
    "icon": "instagram.png",
    "status": "available",
    "features": ["post_scheduling", "analytics", "dm_management"]
    },
    {
    "name": "Twitter",
    "description": "Connect your Twitter account",
    "icon": "twitter.png", 
    "status": "available",
    "features": ["tweet_scheduling", "analytics", "mentions"]
    }
    ],
    "payment": [
    {
    "name": "Stripe",
    "description": "Process payments with Stripe",
    "icon": "stripe.png",
    "status": "available",
    "features": ["payments", "subscriptions", "analytics"]
    },
    {
    "name": "PayPal",
    "description": "Accept PayPal payments",
    "icon": "paypal.png",
    "status": "available",
    "features": ["payments", "refunds", "analytics"]
    }
    ],
    "email": [
    {
    "name": "SendGrid",
    "description": "Email delivery service",
    "icon": "sendgrid.png",
    "status": "available",
    "features": ["email_sending", "templates", "analytics"]
    }
    ]
    }
        return integrations
    
    @staticmethod
    async def get_user_integrations(user_id: str):
        """Get user's active integrations"""
        db = await get_database()
        
        integrations = await db.user_integrations.find({"user_id": user_id}).to_list(length=None)
        return integrations
    
    @staticmethod
    async def connect_integration(user_id: str, integration_data: Dict[str, Any]):
        """Connect a new integration"""
        db = await get_database()
        
        integration = {
    "_id": str(uuid.uuid4()),
    "user_id": user_id,
    "name": integration_data.get("name"),
    "type": integration_data.get("type"),
    "credentials": integration_data.get("credentials", {}),
    "status": "connected",
    "connected_at": datetime.utcnow(),
    "last_sync": datetime.utcnow()
    }
        
        result = await db.user_integrations.insert_one(integration)
        return integration

# Global service instance
integration_service = IntegrationService()