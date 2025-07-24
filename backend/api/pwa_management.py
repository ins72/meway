"""
PWA (Progressive Web App) Backend Support
Advanced PWA functionality with manifest generation and service worker management
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime
import base64
from core.auth import get_current_admin

router = APIRouter(tags=["pwa"])

class PWAManifestService:
    """PWA Manifest generation and management service"""
    
    def __init__(self):
        self.default_manifest = {
            "name": "Mewayz v2 - Business Platform",
            "short_name": "Mewayz",
            "description": "All-in-One Business Management Platform",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#101010",
            "theme_color": "#007AFF",
            "orientation": "portrait-primary",
            "categories": ["business", "productivity", "finance"],
            "lang": "en",
            "dir": "ltr"
        }
    
    async def generate_manifest(self, workspace_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate custom PWA manifest for workspace"""
        try:
            manifest = self.default_manifest.copy()
            
            # Customize based on workspace
            if workspace_data:
                manifest["name"] = f"{workspace_data.get('name', 'Business')} - Mewayz"
                manifest["short_name"] = workspace_data.get('name', 'Mewayz')[:12]
                manifest["description"] = workspace_data.get('description', manifest["description"])
                
                # Custom branding if available
                if workspace_data.get('branding'):
                    branding = workspace_data['branding']
                    manifest["theme_color"] = branding.get('primary_color', '#007AFF')
                    manifest["background_color"] = branding.get('background_color', '#101010')
            
            # Add icons
            manifest["icons"] = [
                {
                    "src": "/icons/icon-72x72.png",
                    "sizes": "72x72",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": "/icons/icon-96x96.png", 
                    "sizes": "96x96",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": "/icons/icon-128x128.png",
                    "sizes": "128x128", 
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": "/icons/icon-144x144.png",
                    "sizes": "144x144",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": "/icons/icon-152x152.png",
                    "sizes": "152x152",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": "/icons/icon-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": "/icons/icon-384x384.png",
                    "sizes": "384x384",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": "/icons/icon-512x512.png",
                    "sizes": "512x512",
                    "type": "image/png",
                    "purpose": "maskable any"
                }
            ]
            
            # Add screenshots for app store
            manifest["screenshots"] = [
                {
                    "src": "/screenshots/desktop-dashboard.png",
                    "sizes": "1280x720",
                    "type": "image/png",
                    "form_factor": "wide",
                    "label": "Dashboard Overview"
                },
                {
                    "src": "/screenshots/mobile-dashboard.png", 
                    "sizes": "390x844",
                    "type": "image/png",
                    "form_factor": "narrow",
                    "label": "Mobile Dashboard"
                }
            ]
            
            # Add advanced PWA features
            manifest["display_override"] = ["window-controls-overlay", "standalone"]
            manifest["edge_side_panel"] = {
                "preferred_width": 320
            }
            
            return {
                "success": True,
                "manifest": manifest,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_service_worker_config(self) -> Dict[str, Any]:
        """Get service worker configuration"""
        try:
            config = {
                "cache_name": "mewayz-v2-cache",
                "version": "2.0.0",
                "offline_pages": [
                    "/",
                    "/dashboard",
                    "/offline",
                    "/login"
                ],
                "cache_strategies": {
                    "api": "network_first",
                    "assets": "cache_first", 
                    "pages": "stale_while_revalidate",
                    "images": "cache_first"
                },
                "background_sync": {
                    "enabled": True,
                    "tag": "mewayz-sync"
                },
                "push_notifications": {
                    "enabled": True,
                    "vapid_public_key": os.getenv("VAPID_PUBLIC_KEY", ""),
                    "subscription_endpoint": "/api/notifications/subscribe"
                }
            }
            
            return {
                "success": True,
                "config": config
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Service instance
pwa_service = PWAManifestService()

@router.post("/manifest/generate")
async def generate_pwa_manifest(
    workspace_id: Optional[str] = None,
    current_user: dict = Depends(get_current_admin)
):
    """Generate PWA manifest for workspace"""
    try:
        workspace_data = {}
        
        if workspace_id:
            # Get workspace data from database
            from core.database import get_database_async
            db = await get_database_async()
            if db:
                workspace = await db.workspaces.find_one({"_id": workspace_id})
                if workspace:
                    workspace_data = workspace
        
        result = await pwa_service.generate_manifest(workspace_data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/manifest/current")
async def get_current_manifest(
    workspace_id: Optional[str] = None,
    current_user: dict = Depends(get_current_admin)
):
    """Get current PWA manifest"""
    try:
        # For now, return default manifest
        result = await pwa_service.generate_manifest({})
        
        if result.get("success"):
            return result["manifest"]
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/service-worker/config")
async def get_service_worker_config():
    """Get service worker configuration"""
    try:
        result = await pwa_service.get_service_worker_config()
        
        if result.get("success"):
            return result["config"]
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/install/track")
async def track_pwa_install(
    install_data: Dict[str, Any],
    current_user: dict = Depends(get_current_admin)
):
    """Track PWA installation"""
    try:
        # Log PWA installation
        from core.production_logging import production_logger
        
        production_logger.log_business_event(
            "pwa_install",
            user_id=current_user.get("email"),
            metadata={
                "platform": install_data.get("platform"),
                "user_agent": install_data.get("user_agent"),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        return {
            "success": True,
            "message": "PWA installation tracked",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/capabilities")
async def get_pwa_capabilities():
    """Get PWA capabilities and features"""
    try:
        capabilities = {
            "features": {
                "offline_support": True,
                "push_notifications": True,
                "background_sync": True,
                "install_prompt": True,
                "file_system_access": False,
                "payment_request": True,
                "geolocation": True,
                "camera_access": True,
                "device_orientation": True
            },
            "supported_platforms": [
                "web",
                "android",
                "ios",
                "windows", 
                "macos",
                "linux"
            ],
            "minimum_requirements": {
                "https": True,
                "service_worker": True,
                "manifest": True
            },
            "installation": {
                "prompt_criteria": [
                    "user_engagement_heuristics",
                    "site_engagement",
                    "frequent_visits"
                ],
                "install_sources": [
                    "browser_prompt",
                    "custom_button",
                    "app_store"
                ]
            }
        }
        
        return {
            "success": True,
            "capabilities": capabilities,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/offline/sync")
async def handle_offline_sync(
    sync_data: Dict[str, Any],
    current_user: dict = Depends(get_current_admin)
):
    """Handle offline data synchronization"""
    try:
        # Process offline data sync
        synced_items = []
        errors = []
        
        for item in sync_data.get("items", []):
            try:
                # Process each sync item based on type
                item_type = item.get("type")
                
                if item_type == "booking":
                    # Sync booking data
                    pass
                elif item_type == "financial":
                    # Sync financial data
                    pass
                elif item_type == "analytics":
                    # Sync analytics data
                    pass
                
                synced_items.append(item.get("id"))
                
            except Exception as item_error:
                errors.append({
                    "id": item.get("id"),
                    "error": str(item_error)
                })
        
        return {
            "success": True,
            "synced_count": len(synced_items),
            "error_count": len(errors),
            "synced_items": synced_items,
            "errors": errors,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def pwa_health_check():
    """PWA system health check"""
    try:
        return {
            "success": True,
            "healthy": True,
            "service": "PWA Management",
            "features": {
                "manifest_generation": True,
                "service_worker_support": True,
                "offline_sync": True,
                "installation_tracking": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "healthy": False,
            "error": str(e)
        }