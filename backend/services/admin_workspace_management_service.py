"""
Admin Workspace Management Service
Provides admin-level workspace and subscription management capabilities
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from core.database import get_database
import uuid
import json

logger = logging.getLogger(__name__)

class AdminWorkspaceManagementService:
    def __init__(self):
        self.db = get_database()
        
        # Admin action types for audit trail
        self.admin_actions = {
            "subscription_override": "Admin subscription override",
            "comp_account_granted": "Complimentary account granted",
            "manual_discount_applied": "Manual discount applied",
            "plan_migration": "Plan migration initiated",
            "subscription_pause": "Subscription paused",
            "subscription_resume": "Subscription resumed",
            "billing_adjustment": "Billing adjustment made"
        }

    async def health_check(self):
        """Health check for admin workspace management service"""
        try:
            collection = self.db.workspaces
            await collection.count_documents({})
            
            return {
                "success": True,
                "healthy": True,
                "service": "admin_workspace_management",
                "timestamp": datetime.utcnow().isoformat(),
                "capabilities": list(self.admin_actions.keys())
            }
        except Exception as e:
            logger.error(f"Admin workspace management health check failed: {e}")
            return {
                "success": False,
                "healthy": False,
                "error": str(e)
            }

    async def get_all_workspaces(self, limit: int = 100, offset: int = 0, filters: Dict = None) -> Dict[str, Any]:
        """Get all workspaces with subscription details for admin view"""
        try:
            # Build query based on filters
            query = {}
            if filters:
                if filters.get("plan_name"):
                    query["subscription.bundles"] = {"$in": [filters["plan_name"]]}
                if filters.get("status"):
                    query["subscription.status"] = filters["status"]
                if filters.get("owner_email"):
                    query["owner_email"] = {"$regex": filters["owner_email"], "$options": "i"}
            
            # Get workspaces with pagination
            cursor = self.db.workspaces.find(query).skip(offset).limit(limit)
            workspaces = await cursor.to_list(length=limit)
            
            # Enhance with subscription information
            enhanced_workspaces = []
            for workspace in workspaces:
                enhanced_workspace = await self._enhance_workspace_with_admin_data(workspace)
                enhanced_workspaces.append(enhanced_workspace)
            
            # Get total count for pagination
            total_count = await self.db.workspaces.count_documents(query)
            
            return {
                "success": True,
                "workspaces": enhanced_workspaces,
                "pagination": {
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_count
                },
                "filters_applied": filters or {}
            }
            
        except Exception as e:
            logger.error(f"Error getting all workspaces: {e}")
            return {"success": False, "error": str(e)}

    async def search_workspaces(self, search_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced workspace search with multiple criteria"""
        try:
            query = {}
            
            # Build search query
            if search_criteria.get("workspace_name"):
                query["name"] = {"$regex": search_criteria["workspace_name"], "$options": "i"}
            
            if search_criteria.get("owner_email"):
                query["owner_email"] = {"$regex": search_criteria["owner_email"], "$options": "i"}
            
            if search_criteria.get("subscription_status"):
                query["subscription.status"] = search_criteria["subscription_status"]
            
            if search_criteria.get("plan_names"):
                query["subscription.bundles"] = {"$in": search_criteria["plan_names"]}
            
            if search_criteria.get("created_after"):
                query["created_at"] = {"$gte": datetime.fromisoformat(search_criteria["created_after"])}
            
            if search_criteria.get("revenue_min") or search_criteria.get("revenue_max"):
                revenue_query = {}
                if search_criteria.get("revenue_min"):
                    revenue_query["$gte"] = search_criteria["revenue_min"]
                if search_criteria.get("revenue_max"):
                    revenue_query["$lte"] = search_criteria["revenue_max"]
                query["subscription.pricing.total_amount"] = revenue_query
            
            # Execute search
            limit = search_criteria.get("limit", 50)
            cursor = self.db.workspaces.find(query).limit(limit)
            workspaces = await cursor.to_list(length=limit)
            
            # Enhance results
            enhanced_results = []
            for workspace in workspaces:
                enhanced_workspace = await self._enhance_workspace_with_admin_data(workspace)
                enhanced_results.append(enhanced_workspace)
            
            return {
                "success": True,
                "search_results": enhanced_results,
                "search_criteria": search_criteria,
                "total_found": len(enhanced_results)
            }
            
        except Exception as e:
            logger.error(f"Error searching workspaces: {e}")
            return {"success": False, "error": str(e)}

    async def override_workspace_subscription(self, workspace_id: str, override_data: Dict[str, Any], admin_user_id: str) -> Dict[str, Any]:
        """Admin override of workspace subscription settings"""
        try:
            # Get current workspace
            workspace = await self.db.workspaces.find_one({"_id": workspace_id})
            if not workspace:
                return {"success": False, "error": f"Workspace {workspace_id} not found"}
            
            # Prepare override configuration
            override_config = {
                "override_id": str(uuid.uuid4()),
                "admin_user_id": admin_user_id,
                "override_date": datetime.utcnow(),
                "original_subscription": workspace.get("subscription", {}),
                "override_type": override_data.get("type", "general"),
                "overrides": {},
                "reason": override_data.get("reason", "Admin override"),
                "expires_at": override_data.get("expires_at")
            }
            
            # Apply overrides based on type
            if "plan_override" in override_data:
                override_config["overrides"]["plan"] = override_data["plan_override"]
            
            if "feature_overrides" in override_data:
                override_config["overrides"]["features"] = override_data["feature_overrides"]
            
            if "limit_overrides" in override_data:
                override_config["overrides"]["limits"] = override_data["limit_overrides"]
            
            if "billing_override" in override_data:
                override_config["overrides"]["billing"] = override_data["billing_override"]
            
            # Update workspace with override
            await self.db.workspaces.update_one(
                {"_id": workspace_id},
                {
                    "$set": {
                        "admin_override": override_config,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Log admin action
            await self._log_admin_action(
                admin_user_id, 
                "subscription_override", 
                workspace_id, 
                override_config
            )
            
            return {
                "success": True,
                "override_id": override_config["override_id"],
                "workspace_id": workspace_id,
                "message": "Subscription override applied successfully",
                "override_details": override_config
            }
            
        except Exception as e:
            logger.error(f"Error overriding workspace subscription: {e}")
            return {"success": False, "error": str(e)}

    async def grant_comp_account(self, workspace_id: str, comp_data: Dict[str, Any], admin_user_id: str) -> Dict[str, Any]:
        """Grant complimentary account access to workspace"""
        try:
            # Get current workspace
            workspace = await self.db.workspaces.find_one({"_id": workspace_id})
            if not workspace:
                return {"success": False, "error": f"Workspace {workspace_id} not found"}
            
            # Create comp account configuration
            comp_config = {
                "comp_id": str(uuid.uuid4()),
                "admin_user_id": admin_user_id,
                "granted_date": datetime.utcnow(),
                "expires_at": comp_data.get("expires_at"),
                "reason": comp_data.get("reason", "Complimentary access granted"),
                "features_included": comp_data.get("features", []),
                "plan_equivalent": comp_data.get("plan_equivalent"),
                "usage_limits": comp_data.get("usage_limits", {}),
                "billing_exempt": True,
                "status": "active"
            }
            
            # Update workspace
            await self.db.workspaces.update_one(
                {"_id": workspace_id},
                {
                    "$set": {
                        "comp_account": comp_config,
                        "subscription.status": "comp",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Log admin action
            await self._log_admin_action(
                admin_user_id, 
                "comp_account_granted", 
                workspace_id, 
                comp_config
            )
            
            return {
                "success": True,
                "comp_id": comp_config["comp_id"],
                "workspace_id": workspace_id,
                "message": "Complimentary account granted successfully",
                "comp_details": comp_config
            }
            
        except Exception as e:
            logger.error(f"Error granting comp account: {e}")
            return {"success": False, "error": str(e)}

    async def apply_manual_discount(self, workspace_id: str, discount_data: Dict[str, Any], admin_user_id: str) -> Dict[str, Any]:
        """Apply manual discount to workspace subscription"""
        try:
            # Get current workspace
            workspace = await self.db.workspaces.find_one({"_id": workspace_id})
            if not workspace:
                return {"success": False, "error": f"Workspace {workspace_id} not found"}
            
            # Create discount configuration  
            discount_config = {
                "discount_id": str(uuid.uuid4()),
                "admin_user_id": admin_user_id,
                "applied_date": datetime.utcnow(),
                "discount_type": discount_data.get("type", "percentage"),  # percentage, fixed_amount
                "discount_value": discount_data.get("value", 0),
                "reason": discount_data.get("reason", "Manual discount applied"),
                "expires_at": discount_data.get("expires_at"),
                "applies_to": discount_data.get("applies_to", "all"),  # all, specific_features
                "status": "active",
                "total_saved": 0  # Will be calculated during billing
            }
            
            # Apply discount to subscription
            current_subscription = workspace.get("subscription", {})
            if "discounts" not in current_subscription:
                current_subscription["discounts"] = []
            
            current_subscription["discounts"].append(discount_config)
            
            # Recalculate pricing with discount
            updated_pricing = await self._recalculate_pricing_with_discount(
                current_subscription, discount_config
            )
            current_subscription["pricing"] = updated_pricing
            
            # Update workspace
            await self.db.workspaces.update_one(
                {"_id": workspace_id},
                {
                    "$set": {
                        "subscription": current_subscription,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Log admin action
            await self._log_admin_action(
                admin_user_id, 
                "manual_discount_applied", 
                workspace_id, 
                discount_config
            )
            
            return {
                "success": True,
                "discount_id": discount_config["discount_id"],
                "workspace_id": workspace_id,
                "message": "Manual discount applied successfully",
                "discount_details": discount_config,
                "updated_pricing": updated_pricing
            }
            
        except Exception as e:
            logger.error(f"Error applying manual discount: {e}")
            return {"success": False, "error": str(e)}

    async def pause_subscription(self, workspace_id: str, pause_data: Dict[str, Any], admin_user_id: str) -> Dict[str, Any]:
        """Pause workspace subscription"""
        try:
            # Get current workspace
            workspace = await self.db.workspaces.find_one({"_id": workspace_id})
            if not workspace:
                return {"success": False, "error": f"Workspace {workspace_id} not found"}
            
            current_subscription = workspace.get("subscription", {})
            if current_subscription.get("status") != "active":
                return {"success": False, "error": "Only active subscriptions can be paused"}
            
            # Create pause configuration
            pause_config = {
                "pause_id": str(uuid.uuid4()),
                "admin_user_id": admin_user_id,
                "paused_date": datetime.utcnow(),
                "reason": pause_data.get("reason", "Admin pause"),
                "expected_resume_date": pause_data.get("expected_resume_date"),
                "billing_paused": pause_data.get("pause_billing", True),
                "feature_access": pause_data.get("feature_access", "limited"),  # none, limited, full
                "previous_status": current_subscription.get("status")
            }
            
            # Update subscription status
            current_subscription["status"] = "paused"
            current_subscription["pause_config"] = pause_config
            
            # Update workspace
            await self.db.workspaces.update_one(
                {"_id": workspace_id},
                {
                    "$set": {
                        "subscription": current_subscription,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Log admin action
            await self._log_admin_action(
                admin_user_id, 
                "subscription_pause", 
                workspace_id, 
                pause_config
            )
            
            return {
                "success": True,
                "pause_id": pause_config["pause_id"],
                "workspace_id": workspace_id,
                "message": "Subscription paused successfully",
                "pause_details": pause_config
            }
            
        except Exception as e:
            logger.error(f"Error pausing subscription: {e}")
            return {"success": False, "error": str(e)}

    async def resume_subscription(self, workspace_id: str, resume_data: Dict[str, Any], admin_user_id: str) -> Dict[str, Any]:
        """Resume paused workspace subscription"""
        try:
            # Get current workspace
            workspace = await self.db.workspaces.find_one({"_id": workspace_id})
            if not workspace:
                return {"success": False, "error": f"Workspace {workspace_id} not found"}
            
            current_subscription = workspace.get("subscription", {})
            if current_subscription.get("status") != "paused":
                return {"success": False, "error": "Only paused subscriptions can be resumed"}
            
            pause_config = current_subscription.get("pause_config", {})
            
            # Create resume configuration
            resume_config = {
                "resume_id": str(uuid.uuid4()),
                "admin_user_id": admin_user_id,
                "resumed_date": datetime.utcnow(),
                "reason": resume_data.get("reason", "Admin resume"),
                "pause_duration": datetime.utcnow() - pause_config.get("paused_date", datetime.utcnow()),
                "billing_adjustments": resume_data.get("billing_adjustments", {})
            }
            
            # Restore subscription status
            current_subscription["status"] = pause_config.get("previous_status", "active")
            current_subscription["resume_config"] = resume_config
            
            # Remove pause config but keep for history
            current_subscription["pause_history"] = current_subscription.get("pause_history", [])
            current_subscription["pause_history"].append(pause_config)
            del current_subscription["pause_config"]
            
            # Update workspace
            await self.db.workspaces.update_one(
                {"_id": workspace_id},
                {
                    "$set": {
                        "subscription": current_subscription,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Log admin action
            await self._log_admin_action(
                admin_user_id, 
                "subscription_resume", 
                workspace_id, 
                resume_config
            )
            
            return {
                "success": True,
                "resume_id": resume_config["resume_id"],
                "workspace_id": workspace_id,
                "message": "Subscription resumed successfully",
                "resume_details": resume_config
            }
            
        except Exception as e:
            logger.error(f"Error resuming subscription: {e}")
            return {"success": False, "error": str(e)}

    async def get_admin_action_history(self, workspace_id: str = None, admin_user_id: str = None, 
                                     days_back: int = 30, limit: int = 50) -> Dict[str, Any]:
        """Get history of admin actions"""
        try:
            # Build query
            query = {"created_at": {"$gte": datetime.utcnow() - timedelta(days=days_back)}}
            if workspace_id:
                query["workspace_id"] = workspace_id
            if admin_user_id:
                query["admin_user_id"] = admin_user_id
            
            # Get admin actions
            cursor = self.db.admin_actions.find(query).sort("created_at", -1).limit(limit)
            actions = await cursor.to_list(length=limit)
            
            # Enhance with workspace information
            enhanced_actions = []
            for action in actions:
                workspace_info = await self._get_workspace_basic_info(action.get("workspace_id"))
                action["workspace_info"] = workspace_info
                enhanced_actions.append(action)
            
            return {
                "success": True,
                "admin_actions": enhanced_actions,
                "filter_criteria": {
                    "workspace_id": workspace_id,
                    "admin_user_id": admin_user_id,
                    "days_back": days_back,
                    "limit": limit
                },
                "total_actions": len(enhanced_actions)
            }
            
        except Exception as e:
            logger.error(f"Error getting admin action history: {e}")
            return {"success": False, "error": str(e)}

    # Helper methods
    async def _enhance_workspace_with_admin_data(self, workspace: Dict) -> Dict:
        """Enhance workspace data with admin-relevant information"""
        try:
            enhanced = workspace.copy()
            
            # Add subscription analytics
            subscription = workspace.get("subscription", {})
            enhanced["admin_analytics"] = {
                "total_revenue": subscription.get("pricing", {}).get("total_amount", 0),
                "subscription_age_days": (datetime.utcnow() - workspace.get("created_at", datetime.utcnow())).days,
                "status": subscription.get("status", "unknown"),
                "bundle_count": len(subscription.get("bundles", [])),
                "has_overrides": "admin_override" in workspace,
                "is_comp_account": "comp_account" in workspace,
                "discount_count": len(subscription.get("discounts", []))
            }
            
            # Add recent admin actions count
            recent_actions = await self.db.admin_actions.count_documents({
                "workspace_id": workspace["_id"],
                "created_at": {"$gte": datetime.utcnow() - timedelta(days=30)}
            })
            enhanced["admin_analytics"]["recent_admin_actions"] = recent_actions
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Error enhancing workspace data: {e}")
            return workspace

    async def _log_admin_action(self, admin_user_id: str, action_type: str, workspace_id: str, action_data: Dict):
        """Log admin action for audit trail"""
        try:
            action_record = {
                "_id": str(uuid.uuid4()),
                "admin_user_id": admin_user_id,
                "action_type": action_type,
                "action_description": self.admin_actions.get(action_type, "Unknown action"),
                "workspace_id": workspace_id,
                "action_data": action_data,
                "created_at": datetime.utcnow(),
                "ip_address": None,  # Would be captured from request in production
                "user_agent": None   # Would be captured from request in production
            }
            
            await self.db.admin_actions.insert_one(action_record)
            
        except Exception as e:
            logger.error(f"Error logging admin action: {e}")

    async def _recalculate_pricing_with_discount(self, subscription: Dict, discount: Dict) -> Dict:
        """Recalculate subscription pricing with applied discount"""
        try:
            current_pricing = subscription.get("pricing", {})
            original_amount = current_pricing.get("total_amount", 0)
            
            if discount["discount_type"] == "percentage":
                discount_amount = original_amount * (discount["discount_value"] / 100)
            else:  # fixed_amount
                discount_amount = discount["discount_value"]
            
            new_amount = max(0, original_amount - discount_amount)
            
            return {
                **current_pricing,
                "total_amount": new_amount,
                "discount_applied": discount_amount,
                "original_amount": original_amount,
                "discount_percentage": (discount_amount / original_amount * 100) if original_amount > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error recalculating pricing: {e}")
            return subscription.get("pricing", {})

    async def _get_workspace_basic_info(self, workspace_id: str) -> Dict:
        """Get basic workspace information for admin displays"""
        try:
            workspace = await self.db.workspaces.find_one(
                {"_id": workspace_id}, 
                {"name": 1, "owner_email": 1, "created_at": 1}
            )
            return workspace or {"name": "Unknown", "owner_email": "Unknown"}
        except Exception:
            return {"name": "Unknown", "owner_email": "Unknown"}


# Service instance
_admin_workspace_management_service = None

def get_admin_workspace_management_service() -> AdminWorkspaceManagementService:
    """Get admin workspace management service instance"""
    global _admin_workspace_management_service
    if _admin_workspace_management_service is None:
        _admin_workspace_management_service = AdminWorkspaceManagementService()
    return _admin_workspace_management_service