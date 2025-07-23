"""
Integration Hub API Routes
Professional Mewayz Platform - Real Integration Management
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from core.auth import get_current_active_user
from core.database import get_database
from services.user_service import get_user_service
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body

router = APIRouter()

# Initialize service instances
user_service = get_user_service()

class IntegrationConnect(BaseModel):
    integration_type: str
    credentials: Dict[str, Any]
    settings: Optional[Dict[str, Any]] = {}

class WebhookCreate(BaseModel):
    integration_id: str
    events: List[str]
    webhook_url: str

def get_integrations_collection():
    """Get integrations collection"""
    db = get_database()
    return db.integrations

def get_webhooks_collection():
    """Get webhooks collection"""
    db = get_database()
    return db.webhooks

def get_integration_logs_collection():
    """Get integration logs collection"""
    db = get_database()
    return db.integration_logs

@router.get("/available")
async def get_available_integrations(current_user: dict = Depends(get_current_active_user)):
    """Get available integrations with real database operations"""
    try:
        # Check user's plan to determine available integrations
        user_stats = await user_service.get_user_stats(current_user["_id"])
        user_plan = user_stats["subscription_info"]["plan"]
        
        # Define available integrations by plan
        integrations = {
            "stripe": {
                "name": "Stripe Payments",
                "description": "Accept payments and manage subscriptions",
                "category": "payments",
                "features": ["Payment processing", "Subscription management", "Invoicing"],
                "available": True,
                "setup_required": ["stripe_public_key", "stripe_secret_key"],
                "documentation_url": "https://stripe.com/docs"
            },
            "google_oauth": {
                "name": "Google OAuth",
                "description": "Allow users to sign in with Google",
                "category": "authentication",
                "features": ["Single sign-on", "User authentication"],
                "available": True,
                "setup_required": ["google_client_id", "google_client_secret"],
                "documentation_url": "https://developers.google.com/identity"
            },
            "sendgrid": {
                "name": "SendGrid Email",
                "description": "Send transactional and marketing emails",
                "category": "email",
                "features": ["Email delivery", "Template management", "Analytics"],
                "available": user_plan in ["pro", "enterprise"],
                "setup_required": ["sendgrid_api_key"],
                "documentation_url": "https://sendgrid.com/docs"
            },
            "mailchimp": {
                "name": "Mailchimp",
                "description": "Email marketing and automation",
                "category": "email",
                "features": ["Email campaigns", "Audience management", "Automation"],
                "available": user_plan in ["pro", "enterprise"],
                "setup_required": ["mailchimp_api_key"],
                "documentation_url": "https://mailchimp.com/developer"
            },
            "slack": {
                "name": "Slack",
                "description": "Team communication and notifications",
                "category": "communication",
                "features": ["Notifications", "Team updates", "Alerts"],
                "available": user_plan in ["pro", "enterprise"],
                "setup_required": ["slack_webhook_url"],
                "documentation_url": "https://api.slack.com"
            },
            "zapier": {
                "name": "Zapier",
                "description": "Connect with 5000+ apps through automation",
                "category": "automation",
                "features": ["Workflow automation", "App connections", "Triggers"],
                "available": user_plan == "enterprise",
                "setup_required": ["zapier_webhook_url"],
                "documentation_url": "https://zapier.com/developer"
            },
            "analytics": {
                "name": "Google Analytics",
                "description": "Advanced website and app analytics",
                "category": "analytics",
                "features": ["Traffic analytics", "User behavior", "Conversion tracking"],
                "available": True,
                "setup_required": ["google_analytics_id"],
                "documentation_url": "https://developers.google.com/analytics"
            },
            "facebook_pixel": {
                "name": "Facebook Pixel",
                "description": "Track conversions and optimize ads",
                "category": "advertising",
                "features": ["Conversion tracking", "Audience building", "Ad optimization"],
                "available": user_plan in ["pro", "enterprise"],
                "setup_required": ["facebook_pixel_id"],
                "documentation_url": "https://developers.facebook.com/docs/facebook-pixel"
            }
        }
        
        return {
            "success": True,
            "data": {
                "integrations": integrations,
                "user_plan": user_plan,
                "total_available": len([i for i in integrations.values() if i["available"]])
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch available integrations: {str(e)}"
        )

@router.get("/connected")
async def get_connected_integrations(current_user: dict = Depends(get_current_active_user)):
    """Get connected integrations with real database operations"""
    try:
        integrations_collection = get_integrations_collection()
        
        # Get user's connected integrations
        integrations = await integrations_collection.find(
            {"user_id": current_user["_id"]}
        ).sort("connected_at", -1).to_list(length=None)
        
        # Get status and health check for each integration
        logs_collection = get_integration_logs_collection()
        for integration in integrations:
            # Get recent logs to determine health
            recent_logs = await logs_collection.find({
                "integration_id": integration["_id"]
            }).sort("timestamp", -1).limit(5).to_list(length=None)
            
            # Calculate health status
            if recent_logs:
                success_count = sum(1 for log in recent_logs if log.get("status") == "success")
                health_score = (success_count / len(recent_logs)) * 100
                integration["health"] = {
                    "score": round(health_score, 1),
                    "status": "healthy" if health_score >= 80 else "warning" if health_score >= 60 else "error",
                    "last_activity": recent_logs[0]["timestamp"]
                }
            else:
                integration["health"] = {
                    "score": 0,
                    "status": "no_activity",
                    "last_activity": None
                }
        
        return {
            "success": True,
            "data": {
                "integrations": integrations,
                "total_connected": len(integrations)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch connected integrations: {str(e)}"
        )

@router.post("/connect")
async def connect_integration(
    integration_data: IntegrationConnect,
    current_user: dict = Depends(get_current_active_user)
):
    """Connect new integration with real database operations"""
    try:
        integrations_collection = get_integrations_collection()
        
        # Check if integration is already connected
        existing_integration = await integrations_collection.find_one({
            "user_id": current_user["_id"],
            "integration_type": integration_data.integration_type
        })
        
        if existing_integration:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Integration already connected"
            )
        
        # Validate integration type
        supported_integrations = [
            "stripe", "google_oauth", "sendgrid", "mailchimp", 
            "slack", "zapier", "analytics", "facebook_pixel"
        ]
        
        if integration_data.integration_type not in supported_integrations:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported integration type. Supported: {', '.join(supported_integrations)}"
            )
        
        # Validate credentials (basic validation - in production, test actual connection)
        required_credentials = get_required_credentials(integration_data.integration_type)
        missing_credentials = [cred for cred in required_credentials if cred not in integration_data.credentials]
        
        if missing_credentials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing credentials: {', '.join(missing_credentials)}"
            )
        
        # Create integration document
        integration_doc = {
            "_id": str(uuid.uuid4()),
            "user_id": current_user["_id"],
            "integration_type": integration_data.integration_type,
            "credentials": integration_data.credentials,  # In production, encrypt these
            "settings": integration_data.settings,
            "is_active": True,
            "connected_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "status": "connected"
        }
        
        # Save to database
        await integrations_collection.insert_one(integration_doc)
        
        # Log the connection
        logs_collection = get_integration_logs_collection()
        log_doc = {
            "_id": str(uuid.uuid4()),
            "user_id": current_user["_id"],
            "integration_id": integration_doc["_id"],
            "integration_type": integration_data.integration_type,
            "action": "connect",
            "status": "success",
            "message": f"{integration_data.integration_type.title()} integration connected successfully",
            "timestamp": datetime.utcnow()
        }
        
        await logs_collection.insert_one(log_doc)
        
        return {
            "success": True,
            "message": f"{integration_data.integration_type.title()} integration connected successfully",
            "data": {
                "integration_id": integration_doc["_id"],
                "integration_type": integration_data.integration_type,
                "status": "connected"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect integration: {str(e)}"
        )

@router.get("/webhooks")
async def get_webhooks(current_user: dict = Depends(get_current_active_user)):
    """Get webhooks with real database operations"""
    try:
        webhooks_collection = get_webhooks_collection()
        
        webhooks = await webhooks_collection.find(
            {"user_id": current_user["_id"]}
        ).sort("created_at", -1).to_list(length=None)
        
        return {
            "success": True,
            "data": {
                "webhooks": webhooks,
                "total_webhooks": len(webhooks)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch webhooks: {str(e)}"
        )

@router.post("/webhooks")
async def create_webhook(
    webhook_data: WebhookCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create webhook with real database operations"""
    try:
        integrations_collection = get_integrations_collection()
        webhooks_collection = get_webhooks_collection()
        
        # Verify integration exists
        integration = await integrations_collection.find_one({
            "_id": webhook_data.integration_id,
            "user_id": current_user["_id"]
        })
        
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )
        
        # Create webhook document
        webhook_doc = {
            "_id": str(uuid.uuid4()),
            "user_id": current_user["_id"],
            "integration_id": webhook_data.integration_id,
            "integration_type": integration["integration_type"],
            "webhook_url": webhook_data.webhook_url,
            "events": webhook_data.events,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_triggered": None,
            "trigger_count": 0
        }
        
        # Save to database
        await webhooks_collection.insert_one(webhook_doc)
        
        return {
            "success": True,
            "message": "Webhook created successfully",
            "data": webhook_doc
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create webhook: {str(e)}"
        )

@router.get("/logs")
async def get_integration_logs(
    integration_id: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user)
):
    """Get integration logs with real database operations"""
    try:
        logs_collection = get_integration_logs_collection()
        
        # Build query
        query = {"user_id": current_user["_id"]}
        if integration_id:
            query["integration_id"] = integration_id
        
        # Get logs
        logs = await logs_collection.find(query).sort("timestamp", -1).limit(limit).to_list(length=None)
        
        return {
            "success": True,
            "data": {
                "logs": logs,
                "total_logs": len(logs)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch integration logs: {str(e)}"
        )

@router.delete("/{integration_id}")
async def disconnect_integration(
    integration_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Disconnect integration with real database operations"""
    try:
        integrations_collection = get_integrations_collection()
        
        # Delete integration
        result = await integrations_collection.delete_one({
            "_id": integration_id,
            "user_id": current_user["_id"]
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )
        
        return {
            "success": True,
            "message": "Integration disconnected successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect integration: {str(e)}"
        )

# Helper functions
def get_required_credentials(integration_type: str) -> List[str]:
    """Get required credentials for integration type"""
    credentials_map = {
        "stripe": ["stripe_public_key", "stripe_secret_key"],
        "google_oauth": ["google_client_id", "google_client_secret"],
        "sendgrid": ["sendgrid_api_key"],
        "mailchimp": ["mailchimp_api_key"],
        "slack": ["slack_webhook_url"],
        "zapier": ["zapier_webhook_url"],
        "analytics": ["google_analytics_id"],
        "facebook_pixel": ["facebook_pixel_id"]
    }
    
    return credentials_map.get(integration_type, [])