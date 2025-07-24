"""
Usage Tracking Service
Handles real-time tracking of feature usage across all workspaces and bundles
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from core.database import get_database
from services.workspace_subscription_service import get_workspace_subscription_service
import uuid

logger = logging.getLogger(__name__)

class UsageTrackingService:
    def __init__(self):
        self.db = get_database()
        
        # Define trackable features and their units
        self.trackable_features = {
            # Creator Bundle Features
            "ai_content_generation": {"unit": "credits", "reset_period": "monthly"},
            "website_pages": {"unit": "pages", "reset_period": "never"},
            "bio_links": {"unit": "links", "reset_period": "never"},
            "custom_domains": {"unit": "domains", "reset_period": "never"},
            
            # E-commerce Bundle Features
            "products": {"unit": "items", "reset_period": "never"},
            "vendors": {"unit": "users", "reset_period": "never"},
            "transactions": {"unit": "transactions", "reset_period": "monthly"},
            
            # Social Media Bundle Features
            "instagram_searches": {"unit": "searches", "reset_period": "monthly"},
            "scheduled_posts": {"unit": "posts", "reset_period": "monthly"},
            "social_accounts": {"unit": "accounts", "reset_period": "never"},
            
            # Education Bundle Features
            "students": {"unit": "users", "reset_period": "never"},
            "courses": {"unit": "courses", "reset_period": "never"},
            "streaming_hours": {"unit": "hours", "reset_period": "monthly"},
            
            # Business Bundle Features
            "contacts": {"unit": "contacts", "reset_period": "never"},
            "emails_sent": {"unit": "emails", "reset_period": "monthly"},
            "workflows": {"unit": "workflows", "reset_period": "never"},
            "campaigns": {"unit": "campaigns", "reset_period": "never"},
            
            # Operations Bundle Features
            "bookings": {"unit": "bookings", "reset_period": "monthly"},
            "forms": {"unit": "forms", "reset_period": "never"},
            "surveys": {"unit": "surveys", "reset_period": "never"},
            "invoices": {"unit": "invoices", "reset_period": "monthly"}
        }

    async def health_check(self):
        """Health check for usage tracking service"""
        try:
            collection = self.db.usage_tracking
            # Test database connection
            await collection.count_documents({})
            
            return {
                "success": True,
                "healthy": True,
                "service": "usage_tracking",
                "timestamp": datetime.utcnow().isoformat(),
                "trackable_features": len(self.trackable_features)
            }
        except Exception as e:
            logger.error(f"Usage tracking health check failed: {e}")
            return {
                "success": False,
                "healthy": False,
                "error": str(e)
            }

    async def track_usage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Track feature usage for workspace"""
        try:
            workspace_id = data.get("workspace_id")
            feature = data.get("feature")
            amount = data.get("amount", 1)
            user_id = data.get("user_id")
            metadata = data.get("metadata", {})
            
            if not workspace_id or not feature or not user_id:
                return {"success": False, "error": "Workspace ID, feature, and user ID are required"}
            
            if feature not in self.trackable_features:
                return {"success": False, "error": f"Feature '{feature}' is not trackable"}
            
            # Check if usage would exceed limits before tracking
            limit_check = await self.check_usage_limit(workspace_id, feature, amount, user_id)
            if not limit_check.get("allowed", False):
                return {
                    "success": False, 
                    "error": "Usage limit exceeded", 
                    "limit_info": limit_check
                }
            
            # Get current period start based on reset schedule
            period_start = self._get_current_period_start(feature)
            
            # Create usage record
            usage_record = {
                "_id": str(uuid.uuid4()),
                "workspace_id": workspace_id,
                "feature": feature,
                "amount": amount,
                "user_id": user_id,
                "tracked_at": datetime.utcnow(),
                "period_start": period_start,
                "metadata": metadata,
                "feature_config": self.trackable_features[feature]
            }
            
            collection = self.db.usage_tracking
            await collection.insert_one(usage_record)
            
            # Update aggregated usage for quick lookups
            await self._update_usage_aggregate(workspace_id, feature, amount, period_start)
            
            # Check if this puts user near limit and create warning if needed
            await self._check_and_create_warnings(workspace_id, feature)
            
            return {
                "success": True,
                "usage_record": usage_record,
                "current_usage": await self._get_feature_usage(workspace_id, feature, period_start),
                "message": f"Tracked {amount} {self.trackable_features[feature]['unit']} for {feature}"
            }
            
        except Exception as e:
            logger.error(f"Error tracking usage: {e}")
            return {"success": False, "error": str(e)}

    async def check_usage_limit(self, workspace_id: str, feature: str, action_count: int = 1, user_id: str = None) -> Dict[str, Any]:
        """Check if action is allowed within usage limits"""
        try:
            if feature not in self.trackable_features:
                return {"success": False, "error": f"Feature '{feature}' is not trackable"}
            
            # Get workspace limits from subscription service
            subscription_service = get_workspace_subscription_service()
            limits_result = await subscription_service.get_workspace_usage_limits(workspace_id, user_id)
            
            if not limits_result.get("success"):
                # Default to free tier limits if no subscription
                workspace_limits = {"ai_credits": 0, "bio_links": 5, "website_pages": 1}
            else:
                workspace_limits = limits_result.get("limits", {})
            
            # Get feature limit (convert feature name to limit key)
            limit_key = self._get_limit_key(feature)
            feature_limit = workspace_limits.get(limit_key, 0)
            
            # Unlimited features
            if feature_limit == -1:
                return {
                    "success": True,
                    "allowed": True,
                    "feature": feature,
                    "limit": "unlimited",
                    "current_usage": 0,
                    "remaining": "unlimited"
                }
            
            # Get current usage for this period
            period_start = self._get_current_period_start(feature)
            current_usage = await self._get_feature_usage(workspace_id, feature, period_start)
            
            # Check if action would exceed limit
            would_exceed = (current_usage + action_count) > feature_limit
            remaining = max(0, feature_limit - current_usage)
            
            return {
                "success": True,
                "allowed": not would_exceed,
                "feature": feature,
                "limit": feature_limit,
                "current_usage": current_usage,
                "requested_amount": action_count,
                "remaining": remaining,
                "would_exceed": would_exceed,
                "period_start": period_start.isoformat(),
                "reset_period": self.trackable_features[feature]["reset_period"]
            }
            
        except Exception as e:
            logger.error(f"Error checking usage limit: {e}")
            return {"success": False, "error": str(e)}

    async def get_current_usage(self, workspace_id: str, user_id: str) -> Dict[str, Any]:
        """Get current usage statistics for workspace"""
        try:
            # Check permissions
            if not await self._check_workspace_access(workspace_id, user_id):
                return {"success": False, "error": "Access denied"}
            
            usage_stats = {}
            
            # Get usage for each trackable feature
            for feature in self.trackable_features:
                period_start = self._get_current_period_start(feature)
                current_usage = await self._get_feature_usage(workspace_id, feature, period_start)
                
                usage_stats[feature] = {
                    "current_usage": current_usage,
                    "period_start": period_start.isoformat(),
                    "reset_period": self.trackable_features[feature]["reset_period"],
                    "unit": self.trackable_features[feature]["unit"]
                }
            
            return {
                "success": True,
                "workspace_id": workspace_id,
                "usage_stats": usage_stats,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting current usage: {e}")
            return {"success": False, "error": str(e)}

    async def get_workspace_limits(self, workspace_id: str, user_id: str) -> Dict[str, Any]:
        """Get workspace usage limits based on subscription"""
        try:
            # Check permissions
            if not await self._check_workspace_access(workspace_id, user_id):
                return {"success": False, "error": "Access denied"}
            
            # Get subscription info from workspace subscription service
            subscription_service = get_workspace_subscription_service()
            limits_result = await subscription_service.get_workspace_usage_limits(workspace_id, user_id)
            
            return limits_result
            
        except Exception as e:
            logger.error(f"Error getting workspace limits: {e}")
            return {"success": False, "error": str(e)}

    async def get_usage_analytics(self, workspace_id: str, period: str, user_id: str) -> Dict[str, Any]:
        """Get usage analytics for workspace"""
        try:
            # Check permissions
            if not await self._check_workspace_access(workspace_id, user_id):
                return {"success": False, "error": "Access denied"}
            
            # Calculate period start based on requested period
            now = datetime.utcnow()
            if period == "day":
                period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == "week":
                period_start = now - timedelta(days=now.weekday())
                period_start = period_start.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == "month":
                period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif period == "year":
                period_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                return {"success": False, "error": "Invalid period. Use: day, week, month, year"}
            
            # Get usage data for the period
            collection = self.db.usage_tracking
            pipeline = [
                {
                    "$match": {
                        "workspace_id": workspace_id,
                        "tracked_at": {"$gte": period_start}
                    }
                },
                {
                    "$group": {
                        "_id": "$feature",
                        "total_usage": {"$sum": "$amount"},
                        "usage_events": {"$sum": 1},
                        "first_used": {"$min": "$tracked_at"},
                        "last_used": {"$max": "$tracked_at"}
                    }
                }
            ]
            
            usage_data = await collection.aggregate(pipeline).to_list(length=None)
            
            # Format analytics data
            analytics = {
                "period": period,
                "period_start": period_start.isoformat(),
                "period_end": now.isoformat(),
                "total_features_used": len(usage_data),
                "feature_usage": {}
            }
            
            for item in usage_data:
                feature = item["_id"]
                analytics["feature_usage"][feature] = {
                    "total_usage": item["total_usage"],
                    "usage_events": item["usage_events"],
                    "first_used": item["first_used"].isoformat(),
                    "last_used": item["last_used"].isoformat(),
                    "unit": self.trackable_features.get(feature, {}).get("unit", "unknown")
                }
            
            return {
                "success": True,
                "workspace_id": workspace_id,
                "analytics": analytics
            }
            
        except Exception as e:
            logger.error(f"Error getting usage analytics: {e}")
            return {"success": False, "error": str(e)}

    async def reset_usage_counters(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Reset usage counters (admin only)"""
        try:
            workspace_id = data.get("workspace_id")
            features = data.get("features", [])  # Empty list means reset all
            reset_by = data.get("reset_by")
            
            if not workspace_id or not reset_by:
                return {"success": False, "error": "Workspace ID and reset_by are required"}
            
            # Reset aggregated usage
            aggregates_collection = self.db.usage_aggregates
            
            if features:
                # Reset specific features
                await aggregates_collection.delete_many({
                    "workspace_id": workspace_id,
                    "feature": {"$in": features}
                })
            else:
                # Reset all features for workspace
                await aggregates_collection.delete_many({"workspace_id": workspace_id})
            
            # Create reset record for audit
            reset_record = {
                "_id": str(uuid.uuid4()),
                "workspace_id": workspace_id,
                "features_reset": features if features else "all",
                "reset_by": reset_by,
                "reset_at": datetime.utcnow(),
                "reason": data.get("reason", "Manual reset")
            }
            
            resets_collection = self.db.usage_resets
            await resets_collection.insert_one(reset_record)
            
            return {
                "success": True,
                "reset_record": reset_record,
                "message": f"Reset usage counters for {len(features) if features else 'all'} features"
            }
            
        except Exception as e:
            logger.error(f"Error resetting usage counters: {e}")
            return {"success": False, "error": str(e)}

    async def get_usage_warnings(self, workspace_id: str, user_id: str) -> Dict[str, Any]:
        """Get usage warnings for workspace (approaching limits)"""
        try:
            # Check permissions
            if not await self._check_workspace_access(workspace_id, user_id):
                return {"success": False, "error": "Access denied"}
            
            collection = self.db.usage_warnings
            warnings = await collection.find({
                "workspace_id": workspace_id,
                "resolved": False,
                "created_at": {"$gte": datetime.utcnow() - timedelta(days=7)}  # Last 7 days
            }).to_list(length=100)
            
            return {
                "success": True,
                "workspace_id": workspace_id,
                "warnings": warnings,
                "total_warnings": len(warnings)
            }
            
        except Exception as e:
            logger.error(f"Error getting usage warnings: {e}")
            return {"success": False, "error": str(e)}

    async def get_upgrade_suggestions(self, workspace_id: str, user_id: str) -> Dict[str, Any]:
        """Get upgrade suggestions based on usage patterns"""
        try:
            # Check permissions
            if not await self._check_workspace_access(workspace_id, user_id):
                return {"success": False, "error": "Access denied"}
            
            # Get current subscription and usage
            subscription_service = get_workspace_subscription_service()
            limits_result = await subscription_service.get_workspace_usage_limits(workspace_id, user_id)
            
            if not limits_result.get("success"):
                return {"success": False, "error": "Could not get subscription info"}
            
            current_bundles = limits_result.get("active_bundles", [])
            usage_stats = await self.get_current_usage(workspace_id, user_id)
            
            if not usage_stats.get("success"):
                return {"success": False, "error": "Could not get usage stats"}
            
            # Analyze usage patterns and suggest bundles
            suggestions = []
            
            # Check if user is hitting limits frequently
            for feature, stats in usage_stats["usage_stats"].items():
                limit_key = self._get_limit_key(feature)
                feature_limit = limits_result.get("limits", {}).get(limit_key, 0)
                
                if feature_limit > 0:  # Not unlimited
                    usage_percentage = (stats["current_usage"] / feature_limit) * 100
                    
                    if usage_percentage > 80:  # Using more than 80% of limit
                        # Suggest bundle that would help with this feature
                        suggested_bundle = self._get_bundle_for_feature(feature)
                        if suggested_bundle and suggested_bundle not in current_bundles:
                            suggestions.append({
                                "reason": f"High usage of {feature} ({usage_percentage:.1f}% of limit)",
                                "suggested_bundle": suggested_bundle,
                                "feature": feature,
                                "current_usage": stats["current_usage"],
                                "current_limit": feature_limit
                            })
            
            return {
                "success": True,
                "workspace_id": workspace_id,
                "current_bundles": current_bundles,
                "suggestions": suggestions,
                "total_suggestions": len(suggestions)
            }
            
        except Exception as e:
            logger.error(f"Error getting upgrade suggestions: {e}")
            return {"success": False, "error": str(e)}

    async def check_admin_permission(self, workspace_id: str, user_id: str) -> bool:
        """Check if user has admin permissions for workspace"""
        try:
            workspace_collection = self.db.workspace
            workspace = await workspace_collection.find_one({
                "id": workspace_id,
                "$or": [
                    {"owner_id": user_id},
                    {"user_id": user_id},
                    {"admins": {"$in": [user_id]}}
                ]
            })
            
            return workspace is not None
            
        except Exception as e:
            logger.error(f"Error checking admin permission: {e}")
            return False

    # Private helper methods
    
    def _get_current_period_start(self, feature: str) -> datetime:
        """Get the start of the current period for a feature"""
        reset_period = self.trackable_features[feature]["reset_period"]
        now = datetime.utcnow()
        
        if reset_period == "monthly":
            return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif reset_period == "weekly":
            days_since_monday = now.weekday()
            return (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif reset_period == "daily":
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:  # never
            return datetime(2024, 1, 1)  # Fixed start date for cumulative features
    
    async def _get_feature_usage(self, workspace_id: str, feature: str, period_start: datetime) -> int:
        """Get current usage for a feature in the given period"""
        try:
            # Try to get from aggregates first (faster)
            aggregates_collection = self.db.usage_aggregates
            aggregate = await aggregates_collection.find_one({
                "workspace_id": workspace_id,
                "feature": feature,
                "period_start": period_start
            })
            
            if aggregate:
                return aggregate["total_usage"]
            
            # Fall back to calculating from raw usage records
            collection = self.db.usage_tracking
            pipeline = [
                {
                    "$match": {
                        "workspace_id": workspace_id,
                        "feature": feature,
                        "tracked_at": {"$gte": period_start}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total": {"$sum": "$amount"}
                    }
                }
            ]
            
            result = await collection.aggregate(pipeline).to_list(length=1)
            return result[0]["total"] if result else 0
            
        except Exception as e:
            logger.error(f"Error getting feature usage: {e}")
            return 0
    
    async def _update_usage_aggregate(self, workspace_id: str, feature: str, amount: int, period_start: datetime):
        """Update aggregated usage for quick lookups"""
        try:
            collection = self.db.usage_aggregates
            
            await collection.update_one(
                {
                    "workspace_id": workspace_id,
                    "feature": feature,
                    "period_start": period_start
                },
                {
                    "$inc": {"total_usage": amount},
                    "$set": {"last_updated": datetime.utcnow()},
                    "$setOnInsert": {
                        "_id": str(uuid.uuid4()),
                        "workspace_id": workspace_id,
                        "feature": feature,
                        "period_start": period_start,
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Error updating usage aggregate: {e}")
    
    async def _check_and_create_warnings(self, workspace_id: str, feature: str):
        """Check if user is approaching limits and create warnings"""
        try:
            # Get current usage and limits
            limit_check = await self.check_usage_limit(workspace_id, feature, 0)
            
            if not limit_check.get("success") or limit_check.get("limit") == "unlimited":
                return
            
            current_usage = limit_check.get("current_usage", 0)
            limit = limit_check.get("limit", 0)
            
            if limit > 0:
                usage_percentage = (current_usage / limit) * 100
                
                # Create warning at 80% and 95% usage
                warning_thresholds = [
                    {"threshold": 95, "level": "critical"},
                    {"threshold": 80, "level": "warning"}
                ]
                
                for threshold_config in warning_thresholds:
                    if usage_percentage >= threshold_config["threshold"]:
                        # Check if warning already exists for this threshold
                        warnings_collection = self.db.usage_warnings
                        existing_warning = await warnings_collection.find_one({
                            "workspace_id": workspace_id,
                            "feature": feature,
                            "threshold": threshold_config["threshold"],
                            "resolved": False
                        })
                        
                        if not existing_warning:
                            warning = {
                                "_id": str(uuid.uuid4()),
                                "workspace_id": workspace_id,
                                "feature": feature,
                                "threshold": threshold_config["threshold"],
                                "level": threshold_config["level"],
                                "current_usage": current_usage,
                                "limit": limit,
                                "usage_percentage": usage_percentage,
                                "created_at": datetime.utcnow(),
                                "resolved": False
                            }
                            
                            await warnings_collection.insert_one(warning)
                        
                        break  # Only create highest priority warning
            
        except Exception as e:
            logger.error(f"Error checking and creating warnings: {e}")
    
    def _get_limit_key(self, feature: str) -> str:
        """Map feature names to limit keys"""
        feature_to_limit_map = {
            "ai_content_generation": "ai_credits",
            "website_pages": "website_pages",
            "bio_links": "bio_links",
            "custom_domains": "custom_domains",
            "products": "products",
            "vendors": "vendors",
            "transactions": "transactions",
            "instagram_searches": "instagram_searches",
            "scheduled_posts": "scheduled_posts",
            "social_accounts": "social_accounts",
            "students": "students",
            "courses": "courses",
            "streaming_hours": "streaming_hours",
            "contacts": "contacts",
            "emails_sent": "emails_per_month",
            "workflows": "workflows",
            "campaigns": "campaigns",
            "bookings": "bookings",
            "forms": "forms",
            "surveys": "surveys",
            "invoices": "invoices"
        }
        
        return feature_to_limit_map.get(feature, feature)
    
    def _get_bundle_for_feature(self, feature: str) -> str:
        """Get which bundle would help with a specific feature"""
        feature_to_bundle_map = {
            "ai_content_generation": "creator",
            "website_pages": "creator",
            "bio_links": "creator",
            "custom_domains": "creator",
            "products": "ecommerce",
            "vendors": "ecommerce",
            "transactions": "ecommerce",
            "instagram_searches": "social_media",
            "scheduled_posts": "social_media",
            "social_accounts": "social_media",
            "students": "education",
            "courses": "education",
            "streaming_hours": "education",
            "contacts": "business",
            "emails_sent": "business",
            "workflows": "business",
            "campaigns": "business",
            "bookings": "operations",
            "forms": "operations",
            "surveys": "operations",
            "invoices": "operations"
        }
        
        return feature_to_bundle_map.get(feature)
    
    async def _check_workspace_access(self, workspace_id: str, user_id: str) -> bool:
        """Check if user has access to workspace"""
        try:
            workspace_collection = self.db.workspace
            workspace = await workspace_collection.find_one({
                "id": workspace_id,
                "$or": [
                    {"owner_id": user_id},
                    {"user_id": user_id},
                    {"members": {"$in": [user_id]}},
                    {"admins": {"$in": [user_id]}}
                ]
            })
            
            return workspace is not None
            
        except Exception as e:
            logger.error(f"Error checking workspace access: {e}")
            return False


# Service instance
_usage_tracking_service = None

def get_usage_tracking_service() -> UsageTrackingService:
    """Get usage tracking service instance"""
    global _usage_tracking_service
    if _usage_tracking_service is None:
        _usage_tracking_service = UsageTrackingService()
    return _usage_tracking_service