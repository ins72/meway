"""
Mobile PWA Features API
Push notifications, offline capabilities, and mobile optimization endpoints
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field

from core.auth import get_current_user
from services.mobile_pwa_service import mobile_pwa_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class PushSubscriptionRequest(BaseModel):
    endpoint: str = Field(..., description="Push service endpoint")
    keys: Dict[str, str] = Field(..., description="Subscription keys (p256dh, auth)")
    user_agent: Optional[str] = None
    platform: str = Field("web", description="Platform type")
    device_type: str = Field("desktop", description="Device type")
    marketing_notifications: bool = True
    update_notifications: bool = True
    reminder_notifications: bool = True

class PushNotificationRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    body: str = Field(..., min_length=1, max_length=300)
    icon: Optional[str] = Field("/icons/icon-192x192.png")
    badge: Optional[str] = Field("/icons/badge-72x72.png")
    image: Optional[str] = None
    url: str = Field("/", description="URL to open when clicked")
    type: str = Field("general", description="Notification type")
    priority: str = Field("normal", pattern="^(low|normal|high)$")
    data: Optional[Dict[str, Any]] = None

class CacheResourceRequest(BaseModel):
    url: str = Field(..., description="Resource URL to cache")
    type: str = Field(..., regex="^(page|api|asset)$")
    content: str = Field(..., description="Resource content")
    content_type: str = Field("text/html")
    strategy: str = Field("cache_first")
    ttl_hours: int = Field(24, ge=1, le=168)

class PWASettingsRequest(BaseModel):
    theme_color: str = Field("#1f2937", regex="^#[0-9A-Fa-f]{6}$")
    background_color: str = Field("#ffffff", regex="^#[0-9A-Fa-f]{6}$")
    display_mode: str = Field("standalone", regex="^(fullscreen|standalone|minimal-ui|browser)$")
    orientation: str = Field("any")
    start_url: str = Field("/")
    scope: str = Field("/")
    offline_enabled: bool = True
    push_notifications_enabled: bool = True
    auto_update: bool = True
    data_saver_mode: bool = False

class DeviceInfoRequest(BaseModel):
    device_id: Optional[str] = None
    platform: str = Field("unknown")
    os_version: str = Field("unknown")
    browser: str = Field("unknown")
    browser_version: str = Field("unknown")
    screen_resolution: str = Field("unknown")
    viewport_size: str = Field("unknown")
    connection_type: str = Field("unknown")
    supports_push: bool = False
    supports_offline: bool = False

class BackgroundSyncRequest(BaseModel):
    type: str = Field(..., description="Type of sync operation")
    data: Dict[str, Any] = Field(..., description="Data to sync")
    endpoint: str = Field(..., description="API endpoint for sync")
    method: str = Field("POST", regex="^(GET|POST|PUT|DELETE|PATCH)$")
    priority: str = Field("normal", regex="^(low|normal|high)$")
    max_attempts: int = Field(3, ge=1, le=10)

# Push Notifications
@router.post("/push/subscribe", tags=["Push Notifications"])
async def subscribe_to_push(
    request: PushSubscriptionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Subscribe device to push notifications"""
    try:
        subscription = await mobile_pwa_service.register_push_subscription(
            user_id=current_user["_id"],
            subscription_data=request.dict()
        )
        
        return {
            "success": True,
            "subscription": subscription,
            "message": "Successfully subscribed to push notifications"
        }
        
    except Exception as e:
        logger.error(f"Error subscribing to push: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/push/send", tags=["Push Notifications"])
async def send_push_notification(
    request: PushNotificationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Send push notification to user's devices"""
    try:
        result = await mobile_pwa_service.send_push_notification(
            user_id=current_user["_id"],
            notification_data=request.dict()
        )
        
        return {
            "success": True,
            **result,
            "message": "Push notification sent successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error sending push notification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Offline Capabilities
@router.post("/offline/cache", tags=["Offline Features"])
async def cache_resource(
    request: CacheResourceRequest,
    current_user: dict = Depends(get_current_user)
):
    """Cache resource for offline access"""
    try:
        cache_entry = await mobile_pwa_service.cache_resource(
            user_id=current_user["_id"],
            resource_data=request.dict()
        )
        
        return {
            "success": True,
            "cache_entry": cache_entry,
            "message": "Resource cached successfully"
        }
        
    except Exception as e:
        logger.error(f"Error caching resource: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/offline/cache/{resource_path:path}", tags=["Offline Features"])
async def get_cached_resource(
    resource_path: str,
    current_user: dict = Depends(get_current_user)
):
    """Get cached resource for offline access"""
    try:
        resource_url = f"/{resource_path}"
        cached_resource = await mobile_pwa_service.get_cached_resource(
            user_id=current_user["_id"],
            resource_url=resource_url
        )
        
        if not cached_resource:
            raise HTTPException(status_code=404, detail="Resource not cached")
        
        return {
            "success": True,
            "resource": cached_resource,
            "message": "Cached resource retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cached resource: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# PWA Configuration
@router.put("/pwa/settings", tags=["PWA Configuration"])
async def update_pwa_settings(
    request: PWASettingsRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update PWA settings for user"""
    try:
        settings = await mobile_pwa_service.update_pwa_settings(
            user_id=current_user["_id"],
            settings=request.dict()
        )
        
        return {
            "success": True,
            "settings": settings,
            "message": "PWA settings updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating PWA settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pwa/manifest", tags=["PWA Configuration"])
async def get_pwa_manifest(
    current_user: dict = Depends(get_current_user)
):
    """Get PWA manifest for user"""
    try:
        manifest = await mobile_pwa_service.get_pwa_manifest(
            user_id=current_user["_id"]
        )
        
        return manifest
        
    except Exception as e:
        logger.error(f"Error getting PWA manifest: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Device Management
@router.post("/device/register", tags=["Device Management"])
async def register_device(
    request: DeviceInfoRequest,
    current_user: dict = Depends(get_current_user)
):
    """Register mobile device information"""
    try:
        device = await mobile_pwa_service.register_device(
            user_id=current_user["_id"],
            device_info=request.dict()
        )
        
        return {
            "success": True,
            "device": device,
            "message": "Device registered successfully"
        }
        
    except Exception as e:
        logger.error(f"Error registering device: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/mobile", tags=["Mobile Analytics"])
async def get_mobile_analytics(
    current_user: dict = Depends(get_current_user)
):
    """Get mobile usage analytics"""
    try:
        analytics = await mobile_pwa_service.get_mobile_analytics(
            user_id=current_user["_id"]
        )
        
        return {
            "success": True,
            "analytics": analytics,
            "message": "Mobile analytics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting mobile analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Background Sync
@router.post("/sync/queue", tags=["Background Sync"])
async def queue_background_sync(
    request: BackgroundSyncRequest,
    current_user: dict = Depends(get_current_user)
):
    """Queue data for background sync"""
    try:
        sync_record = await mobile_pwa_service.queue_background_sync(
            user_id=current_user["_id"],
            sync_data=request.dict()
        )
        
        return {
            "success": True,
            "sync_record": sync_record,
            "message": "Data queued for background sync"
        }
        
    except Exception as e:
        logger.error(f"Error queuing background sync: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync/process", tags=["Background Sync"])
async def process_background_sync(
    current_user: dict = Depends(get_current_user)
):
    """Process pending background sync items"""
    try:
        result = await mobile_pwa_service.process_background_sync(
            user_id=current_user["_id"]
        )
        
        return {
            "success": True,
            **result,
            "message": "Background sync processed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error processing background sync: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", tags=["System"])
async def mobile_pwa_health():
    """Health check for mobile PWA system"""
    return {
        "status": "healthy",
        "service": "Mobile PWA Features",
        "features": [
            "Push Notifications",
            "Offline Caching",
            "Background Sync",
            "PWA Manifest Generation",
            "Device Management",
            "Mobile Analytics",
            "Service Worker Support",
            "Progressive Enhancement"
        ],
        "notification_types": ["general", "marketing", "update", "reminder", "system"],
        "offline_strategies": ["cache_first", "network_first", "cache_only", "network_only"],
        "supported_platforms": ["web", "android", "ios", "desktop"],
        "timestamp": datetime.utcnow().isoformat()
    }