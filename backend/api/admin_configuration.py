"""
Admin Configuration API
Comprehensive admin dashboard for managing all external API integrations and system settings
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime
import json

from core.auth import get_current_admin
from core.admin_config_manager import admin_config_manager, APIConfiguration
from core.professional_logger import professional_logger, LogLevel, LogCategory
from core.external_api_integrator import (
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user
import uuid
    social_media_integrator, 
    payment_processor_integrator, 
    email_service_integrator, 
    file_storage_integrator, 
    ai_service_integrator
)

router = APIRouter()

class ConfigurationUpdateRequest(BaseModel):
    """Request model for configuration updates"""
    # Social Media APIs
    twitter_bearer_token: Optional[str] = None
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    instagram_access_token: Optional[str] = None
    instagram_app_id: Optional[str] = None
    facebook_access_token: Optional[str] = None
    facebook_app_id: Optional[str] = None
    linkedin_client_id: Optional[str] = None
    linkedin_client_secret: Optional[str] = None
    tiktok_client_key: Optional[str] = None
    tiktok_client_secret: Optional[str] = None
    
    # Payment Processors
    stripe_secret_key: Optional[str] = None
    stripe_publishable_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    paypal_client_id: Optional[str] = None
    paypal_client_secret: Optional[str] = None
    paypal_webhook_id: Optional[str] = None
    square_access_token: Optional[str] = None
    square_application_id: Optional[str] = None
    square_webhook_signature_key: Optional[str] = None
    razorpay_key_id: Optional[str] = None
    razorpay_key_secret: Optional[str] = None
    razorpay_webhook_secret: Optional[str] = None
    preferred_payment_processor: Optional[str] = None
    enabled_payment_processors: Optional[List[str]] = None
    
    # Email Services
    sendgrid_api_key: Optional[str] = None
    sendgrid_from_email: Optional[str] = None
    mailgun_api_key: Optional[str] = None
    mailgun_domain: Optional[str] = None
    aws_ses_access_key: Optional[str] = None
    aws_ses_secret_key: Optional[str] = None
    aws_ses_region: Optional[str] = None
    preferred_email_service: Optional[str] = None
    
    # File Storage
    backblaze_b2_key_id: Optional[str] = None
    backblaze_b2_app_key: Optional[str] = None
    backblaze_b2_bucket_id: Optional[str] = None
    backblaze_b2_bucket_name: Optional[str] = None
    
    # AI Services
    openai_api_key: Optional[str] = None
    openai_organization: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_ai_api_key: Optional[str] = None
    preferred_ai_service: Optional[str] = None
    
    # System Settings
    enable_rate_limiting: Optional[bool] = None
    rate_limit_per_minute: Optional[int] = None
    enable_audit_logging: Optional[bool] = None
    log_level: Optional[str] = None
    enable_email_notifications: Optional[bool] = None
    admin_notification_email: Optional[str] = None

@router.get("/configuration")
async def get_current_configuration(
    current_admin: dict = Depends(get_current_admin)
):
    """Get current system configuration (masked sensitive fields)"""
    try:
        config = await admin_config_manager.get_configuration(decrypt_sensitive=False)
        
        await professional_logger.log(
            LogLevel.INFO, LogCategory.ADMIN,
            "Admin retrieved system configuration",
            details={"admin_id": current_admin.get("user_id")},
            user_id=current_admin.get("user_id")
        )
        
        return {
            "success": True,
            "configuration": config,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.ADMIN,
            f"Failed to retrieve configuration: {str(e)}",
            details={"admin_id": current_admin.get("user_id")},
            user_id=current_admin.get("user_id"),
            error=e
        )
        raise HTTPException(status_code=500, detail=f"Failed to retrieve configuration: {str(e)}")

@router.post("/configuration")
async def update_system_configuration(
    config_update: ConfigurationUpdateRequest,
    request: Request,
    current_admin: dict = Depends(get_current_admin)
):
    """Update system configuration"""
    try:
        # Get current configuration
        current_config = await admin_config_manager.get_configuration(decrypt_sensitive=True)
        
        # Update only provided fields
        update_data = config_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            current_config[key] = value
        
        # Create configuration object
        api_config = APIConfiguration(**current_config)
        
        # Save configuration
        result = await admin_config_manager.save_configuration(
            api_config, 
            current_admin.get("user_id")
        )
        
        await professional_logger.log(
            LogLevel.INFO, LogCategory.ADMIN,
            "Admin updated system configuration",
            details={
                "admin_id": current_admin.get("user_id"),
                "updated_fields": list(update_data.keys())
            },
            user_id=current_admin.get("user_id"),
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        
        return result
        
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.ADMIN,
            f"Configuration update failed: {str(e)}",
            details={
                "admin_id": current_admin.get("user_id"),
                "error": str(e)
            },
            user_id=current_admin.get("user_id"),
            error=e
        )
        raise HTTPException(status_code=500, detail=f"Configuration update failed: {str(e)}")

@router.get("/integrations/status")
async def get_integrations_status(
    current_admin: dict = Depends(get_current_admin)
):
    """Get status of all external API integrations"""
    try:
        integration_status = await admin_config_manager.get_integration_status()
        
        await professional_logger.log(
            LogLevel.INFO, LogCategory.ADMIN,
            "Admin checked integration status",
            details={"admin_id": current_admin.get("user_id")},
            user_id=current_admin.get("user_id")
        )
        
        return integration_status
        
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.ADMIN,
            f"Failed to get integration status: {str(e)}",
            details={"admin_id": current_admin.get("user_id")},
            user_id=current_admin.get("user_id"),
            error=e
        )
        raise HTTPException(status_code=500, detail=f"Failed to get integration status: {str(e)}")

@router.post("/integrations/{service}/test")
async def test_integration(
    service: str,
    request: Request,
    current_admin: dict = Depends(get_current_admin)
):
    """Test connection to specific external API service"""
    try:
        result = await admin_config_manager.test_api_connection(
            service, 
            current_admin.get("user_id")
        )
        
        await professional_logger.log(
            LogLevel.INFO, LogCategory.ADMIN,
            f"Admin tested {service} integration",
            details={
                "admin_id": current_admin.get("user_id"),
                "service": service,
                "production_value": result.get("success", False)
            },
            user_id=current_admin.get("user_id"),
            ip_address=request.client.host
        )
        
        return result
        
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.ADMIN,
            f"Integration test failed for {service}: {str(e)}",
            details={
                "admin_id": current_admin.get("user_id"),
                "service": service
            },
            user_id=current_admin.get("user_id"),
            error=e
        )
        raise HTTPException(status_code=500, detail=f"Integration test failed: {str(e)}")

@router.post("/payment-processors/switch")
async def switch_payment_processor(
    processor_data: Dict[str, Any],
    request: Request,
    current_admin: dict = Depends(get_current_admin)
):
    """Switch preferred payment processor and update enabled processors"""
    try:
        preferred_processor = processor_data.get("preferred_processor")
        enabled_processors = processor_data.get("enabled_processors", [])
        
        if not preferred_processor:
            raise HTTPException(status_code=400, detail="preferred_processor is required")
        
        # Get current config and update payment settings
        current_config = await admin_config_manager.get_configuration(decrypt_sensitive=True)
        current_config["preferred_payment_processor"] = preferred_processor
        current_config["enabled_payment_processors"] = enabled_processors
        
        api_config = APIConfiguration(**current_config)
        result = await admin_config_manager.save_configuration(
            api_config, 
            current_admin.get("user_id")
        )
        
        # Re-initialize payment processors
        await payment_processor_integrator.initialize_processors()
        
        await professional_logger.log(
            LogLevel.INFO, LogCategory.ADMIN,
            f"Admin switched payment processor to {preferred_processor}",
            details={
                "admin_id": current_admin.get("user_id"),
                "preferred_processor": preferred_processor,
                "enabled_processors": enabled_processors
            },
            user_id=current_admin.get("user_id"),
            ip_address=request.client.host
        )
        
        return {
            "success": True,
            "message": f"Payment processor switched to {preferred_processor}",
            "preferred_processor": preferred_processor,
            "enabled_processors": enabled_processors
        }
        
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.ADMIN,
            f"Payment processor switch failed: {str(e)}",
            details={"admin_id": current_admin.get("user_id")},
            user_id=current_admin.get("user_id"),
            error=e
        )
        raise HTTPException(status_code=500, detail=f"Payment processor switch failed: {str(e)}")

@router.get("/logs")
async def get_system_logs(
    level: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_admin: dict = Depends(get_current_admin)
):
    """Get system logs with filtering for admin dashboard"""
    try:
        # Parse dates if provided
        start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00')) if start_date else None
        end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00')) if end_date else None
        
        # Convert string enums
        from core.professional_logger import LogLevel as LogLevelEnum, LogCategory as LogCategoryEnum
        log_level = LogLevelEnum(level) if level else None
        log_category = LogCategoryEnum(category) if category else None
        
        logs = await professional_logger.get_admin_logs(
            level=log_level,
            category=log_category,
            start_date=start_datetime,
            end_date=end_datetime,
            search=search,
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        await professional_logger.log(
            LogLevel.INFO, LogCategory.ADMIN,
            "Admin accessed system logs",
            details={
                "admin_id": current_admin.get("user_id"),
                "filters": {
                    "level": level,
                    "category": category,
                    "search": search,
                    "limit": limit
                }
            },
            user_id=current_admin.get("user_id")
        )
        
        return logs
        
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.ADMIN,
            f"Failed to retrieve logs: {str(e)}",
            details={"admin_id": current_admin.get("user_id")},
            user_id=current_admin.get("user_id"),
            error=e
        )
        raise HTTPException(status_code=500, detail=f"Failed to retrieve logs: {str(e)}")

@router.get("/logs/statistics")
async def get_log_statistics(
    current_admin: dict = Depends(get_current_admin)
):
    """Get log statistics for admin dashboard"""
    try:
        stats = await professional_logger.get_log_statistics()
        
        await professional_logger.log(
            LogLevel.INFO, LogCategory.ADMIN,
            "Admin retrieved log statistics",
            details={"admin_id": current_admin.get("user_id")},
            user_id=current_admin.get("user_id")
        )
        
        return stats
        
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.ADMIN,
            f"Failed to get log statistics: {str(e)}",
            details={"admin_id": current_admin.get("user_id")},
            user_id=current_admin.get("user_id"),
            error=e
        )
        raise HTTPException(status_code=500, detail=f"Failed to get log statistics: {str(e)}")

@router.get("/system/health")
async def get_system_health(
    current_admin: dict = Depends(get_current_admin)
):
    """Get comprehensive system health information for admin dashboard"""
    try:
        from core.database import get_database
        
        db = get_database()
        
        # Check database connectivity
        try:
            await db.command("ping")
            database_status = "healthy"
        except Exception as e:
            database_status = f"error: {str(e)}"
        
        # Get integration status
        integration_status = await admin_config_manager.get_integration_status()
        
        # Get recent error rate
        log_stats = await professional_logger.get_log_statistics()
        error_rate = log_stats.get("statistics", {}).get("error_rate", 0) if log_stats.get("success") else 0
        
        # Count configured integrations
        integrations = integration_status.get("integrations", {}) if integration_status.get("success") else {}
        configured_count = 0
        total_possible = 0
        
        for category, services in integrations.items():
            if isinstance(services, dict):
                for service, configured in services.items():
                    if service not in ["preferred", "enabled"]:
                        total_possible += 1
                        if configured:
                            configured_count += 1
        
        health_status = {
            "status": "healthy" if database_status == "healthy" and error_rate < 5 else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "database": {
                "status": database_status,
                "collections_count": len(await db.list_collection_names()) if database_status == "healthy" else 0
            },
            "integrations": {
                "configured": configured_count,
                "total_possible": total_possible,
                "percentage": round((configured_count / total_possible * 100) if total_possible > 0 else 0, 1)
            },
            "logging": {
                "error_rate": error_rate,
                "status": "healthy" if error_rate < 5 else "degraded"
            },
            "external_apis": {
                "social_media": sum([1 for service, configured in integrations.get("social_media", {}).items() if configured]),
                "payment_processors": sum([1 for service, configured in integrations.get("payment_processors", {}).items() if isinstance(configured, bool) and configured]),
                "email_services": sum([1 for service, configured in integrations.get("email_services", {}).items() if isinstance(configured, bool) and configured]),
                "file_storage": integrations.get("file_storage", {}).get("backblaze_b2", False),
                "ai_services": sum([1 for service, configured in integrations.get("ai_services", {}).items() if isinstance(configured, bool) and configured])
            }
        }
        
        await professional_logger.log(
            LogLevel.INFO, LogCategory.ADMIN,
            "Admin checked system health",
            details={
                "admin_id": current_admin.get("user_id"),
                "health_status": health_status["status"]
            },
            user_id=current_admin.get("user_id")
        )
        
        return {
            "success": True,
            "health": health_status
        }
        
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.ADMIN,
            f"System health check failed: {str(e)}",
            details={"admin_id": current_admin.get("user_id")},
            user_id=current_admin.get("user_id"),
            error=e
        )
        raise HTTPException(status_code=500, detail=f"System health check failed: {str(e)}")

@router.get("/analytics/dashboard")
async def get_admin_analytics_dashboard(
    period: str = "24h",
    current_admin: dict = Depends(get_current_admin)
):
    """Get comprehensive admin analytics dashboard"""
    try:
        from core.database import get_database
        from datetime import timedelta
        
        db = get_database()
        
        # Define time period
        if period == "24h":
            since = datetime.utcnow() - timedelta(hours=24)
        elif period == "7d":
            since = datetime.utcnow() - timedelta(days=7)
        elif period == "30d":
            since = datetime.utcnow() - timedelta(days=30)
        else:
            since = datetime.utcnow() - timedelta(hours=24)
        
        # Get API usage statistics
        api_stats = await db.admin_system_logs.aggregate([
            {"$match": {"category": "API", "timestamp": {"$gte": since}}},
            {"$group": {
                "_id": "$endpoint",
                "count": {"$sum": 1},
                "avg_response_time": {"$avg": "$response_time"},
                "error_count": {"$sum": {"$cond": [{"$gte": ["$status_code", 400]}, 1, 0]}}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]).to_list(length=10)
        
        # Get user activity
        user_activity = await db.admin_system_logs.aggregate([
            {"$match": {"timestamp": {"$gte": since}, "user_id": {"$ne": None}}},
            {"$group": {"_id": "$user_id", "activity_count": {"$sum": 1}}},
            {"$sort": {"activity_count": -1}},
            {"$limit": 10}
        ]).to_list(length=10)
        
        # Get error trends
        error_trends = await db.admin_system_logs.aggregate([
            {"$match": {"level": {"$in": ["ERROR", "CRITICAL"]}, "timestamp": {"$gte": since}}},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d-%H", "date": "$timestamp"}},
                "error_count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]).to_list(length=None)
        
        # Get external API usage
        external_api_usage = await db.admin_system_logs.aggregate([
            {"$match": {"category": "EXTERNAL_API", "timestamp": {"$gte": since}}},
            {"$group": {
                "_id": "$details.service",
                "call_count": {"$sum": 1},
                "avg_response_time": {"$avg": "$response_time"},
                "success_rate": {"$avg": {"$cond": [{"$lt": ["$status_code", 400]}, 1, 0]}}
            }},
            {"$sort": {"call_count": -1}}
        ]).to_list(length=None)
        
        dashboard_data = {
            "period": period,
            "timestamp": datetime.utcnow().isoformat(),
            "api_usage": {
                "top_endpoints": [
                    {
                        "endpoint": stat["_id"],
                        "calls": stat["count"],
                        "avg_response_time": round(stat["avg_response_time"] or 0, 3),
                        "error_rate": round((stat["error_count"] / stat["count"] * 100) if stat["count"] > 0 else 0, 2)
                    }
                    for stat in api_stats
                ]
            },
            "user_activity": [
                {
                    "user_id": activity["_id"],
                    "activity_count": activity["activity_count"]
                }
                for activity in user_activity
            ],
            "error_trends": [
                {
                    "hour": trend["_id"],
                    "error_count": trend["error_count"]
                }
                for trend in error_trends
            ],
            "external_apis": [
                {
                    "service": usage["_id"] or "unknown",
                    "calls": usage["call_count"],
                    "avg_response_time": round(usage["avg_response_time"] or 0, 3),
                    "success_rate": round((usage["success_rate"] or 0) * 100, 2)
                }
                for usage in external_api_usage
            ]
        }
        
        await professional_logger.log(
            LogLevel.INFO, LogCategory.ADMIN,
            "Admin accessed analytics dashboard",
            details={
                "admin_id": current_admin.get("user_id"),
                "period": period
            },
            user_id=current_admin.get("user_id")
        )
        
        return {
            "success": True,
            "dashboard": dashboard_data
        }
        
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.ADMIN,
            f"Admin analytics dashboard failed: {str(e)}",
            details={"admin_id": current_admin.get("user_id")},
            user_id=current_admin.get("user_id"),
            error=e
        )
        raise HTTPException(status_code=500, detail=f"Analytics dashboard failed: {str(e)}")

@router.get("/available-services")
async def get_available_services(
    current_admin: dict = Depends(get_current_admin)
):
    """Get list of all available services and their configuration requirements"""
    available_services = {
        "social_media": {
            "twitter": {
                "name": "Twitter API v2",
                "required_fields": ["twitter_bearer_token", "twitter_api_key", "twitter_api_secret"],
                "description": "Access Twitter user data, tweets, and analytics"
            },
            "instagram": {
                "name": "TikTok Business API", "Twitter API v2",
                "required_fields": ["instagram_access_token", "instagram_app_id"],
                "description": "Access Instagram business account data and media"
            },
            "facebook": {
                "name": "Facebook Graph API", 
                "required_fields": ["facebook_access_token", "facebook_app_id"],
                "description": "Access Facebook page data and analytics"
            },
            "linkedin": {
                "name": "LinkedIn API",
                "required_fields": ["linkedin_client_id", "linkedin_client_secret"],
                "description": "Access LinkedIn profile and company data"
            },
            "tiktok": {
                "name": "TikTok API",
                "required_fields": ["tiktok_client_key", "tiktok_client_secret"],
                "description": "Access TikTok user data and video analytics"
            }
        },
        "payment_processors": {
            "stripe": {
                "name": "Stripe",
                "required_fields": ["stripe_secret_key", "stripe_publishable_key"],
                "optional_fields": ["stripe_webhook_secret"],
                "description": "Process payments with Stripe"
            },
            "paypal": {
                "name": "PayPal",
                "required_fields": ["paypal_client_id", "paypal_client_secret"],
                "optional_fields": ["paypal_webhook_id"],
                "description": "Process payments with PayPal"
            },
            "square": {
                "name": "Square",
                "required_fields": ["square_access_token", "square_application_id"],
                "optional_fields": ["square_webhook_signature_key"],
                "description": "Process payments with Square"
            },
            "razorpay": {
                "name": "Razorpay",
                "required_fields": ["razorpay_key_id", "razorpay_key_secret"],
                "optional_fields": ["razorpay_webhook_secret"],
                "description": "Process payments with Razorpay"
            }
        },
        "email_services": {
            "sendgrid": {
                "name": "SendGrid",
                "required_fields": ["sendgrid_api_key", "sendgrid_from_email"],
                "description": "Send emails using SendGrid"
            },
            "mailgun": {
                "name": "Mailgun",
                "required_fields": ["mailgun_api_key", "mailgun_domain"],
                "description": "Send emails using Mailgun"
            },
            "aws_ses": {
                "name": "AWS SES",
                "required_fields": ["aws_ses_access_key", "aws_ses_secret_key", "aws_ses_region"],
                "description": "Send emails using AWS Simple Email Service"
            }
        },
        "file_storage": {
            "backblaze_b2": {
                "name": "Backblaze B2",
                "required_fields": ["backblaze_b2_key_id", "backblaze_b2_app_key", "backblaze_b2_bucket_id"],
                "optional_fields": ["backblaze_b2_bucket_name"],
                "description": "Store files in Backblaze B2 cloud storage"
            }
        },
        "ai_services": {
            "openai": {
                "name": "OpenAI",
                "required_fields": ["openai_api_key"],
                "optional_fields": ["openai_organization"],
                "description": "Generate content using OpenAI GPT models"
            },
            "anthropic": {
                "name": "Anthropic Claude",
                "required_fields": ["anthropic_api_key"],
                "description": "Generate content using Anthropic Claude"
            },
            "google_ai": {
                "name": "Google AI",
                "required_fields": ["google_ai_api_key"],
                "description": "Generate content using Google AI models"
            }
        }
    }
    
    return {
        "success": True,
        "services": available_services
    }