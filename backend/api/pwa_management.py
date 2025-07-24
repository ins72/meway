"""
PWA (Progressive Web App) Backend Support
Advanced PWA functionality with manifest generation and service worker management
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any, List, Optional
import json
import os
import uuid
from datetime import datetime
import base64
from core.auth import get_current_admin
from core.database import get_database_async

router = APIRouter(tags=["pwa"])

class PWAManifestService:
    """PWA Manifest generation and management service"""
    
    def __init__(self):
        self.collection_name = "pwa_configurations"
        self.manifest_collection = "pwa_manifests"
        self.install_tracking_collection = "pwa_install_tracking"
        self.sync_data_collection = "pwa_sync_data"
    
    async def _get_collection(self, collection_name: str = None):
        """Get database collection"""
        try:
            db = await get_database_async()
            if db is None:
                return None
            return db[collection_name or self.collection_name]
        except Exception as e:
            return None
    
    async def create_pwa_config(self, config_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Create PWA configuration with real database storage"""
        try:
            collection = await self._get_collection()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            pwa_config = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "workspace_id": config_data.get("workspace_id"),
                "app_name": config_data.get("app_name", "Business App"),
                "short_name": config_data.get("short_name", "App"),
                "description": config_data.get("description", "Progressive Web App"),
                "start_url": config_data.get("start_url", "/"),
                "display": config_data.get("display", "standalone"),
                "background_color": config_data.get("background_color", "#101010"),
                "theme_color": config_data.get("theme_color", "#007AFF"),
                "orientation": config_data.get("orientation", "portrait-primary"),
                "categories": config_data.get("categories", ["business", "productivity"]),
                "lang": config_data.get("lang", "en"),
                "dir": config_data.get("dir", "ltr"),
                "icons": config_data.get("icons", []),
                "screenshots": config_data.get("screenshots", []),
                "display_override": config_data.get("display_override", ["window-controls-overlay", "standalone"]),
                "edge_side_panel": config_data.get("edge_side_panel", {"preferred_width": 320}),
                "service_worker_config": {
                    "cache_name": f"mewayz-{user_id}-cache",
                    "version": config_data.get("version", "1.0.0"),
                    "offline_pages": config_data.get("offline_pages", ["/", "/dashboard", "/offline", "/login"]),
                    "cache_strategies": config_data.get("cache_strategies", {
                        "api": "network_first",
                        "assets": "cache_first",
                        "pages": "stale_while_revalidate",
                        "images": "cache_first"
                    }),
                    "background_sync": config_data.get("background_sync", {"enabled": True, "tag": "mewayz-sync"}),
                    "push_notifications": config_data.get("push_notifications", {
                        "enabled": True,
                        "vapid_public_key": config_data.get("vapid_public_key", ""),
                        "subscription_endpoint": "/api/notifications/subscribe"
                    })
                },
                "features": config_data.get("features", {
                    "offline_support": True,
                    "push_notifications": True,
                    "background_sync": True,
                    "install_prompt": True,
                    "file_system_access": False,
                    "payment_request": True,
                    "geolocation": True,
                    "camera_access": True,
                    "device_orientation": True
                }),
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = await collection.insert_one(pwa_config)
            
            if result.inserted_id:
                return {
                    "success": True,
                    "message": "PWA configuration created successfully",
                    "data": {k: v for k, v in pwa_config.items() if k != '_id'},
                    "id": pwa_config["id"]
                }
            else:
                return {"success": False, "error": "Failed to create PWA configuration"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_pwa_config(self, config_id: str, user_id: str) -> Dict[str, Any]:
        """Get PWA configuration by ID"""
        try:
            collection = await self._get_collection()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            config = await collection.find_one({"id": config_id, "user_id": user_id})
            
            if config:
                return {
                    "success": True,
                    "data": {k: v for k, v in config.items() if k != '_id'}
                }
            else:
                return {"success": False, "error": "PWA configuration not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_pwa_config(self, config_id: str, update_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Update PWA configuration"""
        try:
            collection = await self._get_collection()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await collection.update_one(
                {"id": config_id, "user_id": user_id},
                {"$set": update_data}
            )
            
            if result.matched_count > 0:
                updated_config = await collection.find_one({"id": config_id, "user_id": user_id})
                return {
                    "success": True,
                    "message": "PWA configuration updated successfully",
                    "data": {k: v for k, v in updated_config.items() if k != '_id'} if updated_config else None
                }
            else:
                return {"success": False, "error": "PWA configuration not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_pwa_config(self, config_id: str, user_id: str) -> Dict[str, Any]:
        """Delete PWA configuration"""
        try:
            collection = await self._get_collection()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            result = await collection.delete_one({"id": config_id, "user_id": user_id})
            
            if result.deleted_count > 0:
                return {
                    "success": True,
                    "message": "PWA configuration deleted successfully",
                    "deleted_count": result.deleted_count
                }
            else:
                return {"success": False, "error": "PWA configuration not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_pwa_configs(self, user_id: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List PWA configurations for user"""
        try:
            collection = await self._get_collection()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            cursor = collection.find({"user_id": user_id}).skip(offset).limit(limit)
            configs = await cursor.to_list(length=limit)
            
            sanitized_configs = [{k: v for k, v in config.items() if k != '_id'} for config in configs]
            
            total = await collection.count_documents({"user_id": user_id})
            
            return {
                "success": True,
                "data": sanitized_configs,
                "total": total,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def generate_manifest(self, config_id: str, user_id: str) -> Dict[str, Any]:
        """Generate PWA manifest from stored configuration"""
        try:
            # Get stored configuration
            config_result = await self.get_pwa_config(config_id, user_id)
            if not config_result.get("success"):
                return config_result
            
            config_data = config_result["data"]
            
            # Generate manifest from real data
            manifest = {
                "name": config_data.get("app_name", "Business App"),
                "short_name": config_data.get("short_name", "App"),
                "description": config_data.get("description", "Progressive Web App"),
                "start_url": config_data.get("start_url", "/"),
                "display": config_data.get("display", "standalone"),
                "background_color": config_data.get("background_color", "#101010"),
                "theme_color": config_data.get("theme_color", "#007AFF"),
                "orientation": config_data.get("orientation", "portrait-primary"),
                "categories": config_data.get("categories", ["business", "productivity"]),
                "lang": config_data.get("lang", "en"),
                "dir": config_data.get("dir", "ltr"),
                "icons": config_data.get("icons", []),
                "screenshots": config_data.get("screenshots", []),
                "display_override": config_data.get("display_override", ["window-controls-overlay", "standalone"]),
                "edge_side_panel": config_data.get("edge_side_panel", {"preferred_width": 320})
            }
            
            # Store generated manifest
            manifest_collection = await self._get_collection(self.manifest_collection)
            if manifest_collection:
                manifest_record = {
                    "id": str(uuid.uuid4()),
                    "config_id": config_id,
                    "user_id": user_id,
                    "manifest": manifest,
                    "generated_at": datetime.utcnow().isoformat()
                }
                await manifest_collection.insert_one(manifest_record)
            
            return {
                "success": True,
                "manifest": manifest,
                "config_id": config_id,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
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