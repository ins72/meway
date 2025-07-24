"""
Admin Plan Management Service  
Comprehensive control over plan definitions: pricing, features, limits, availability
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from core.database import get_database
import uuid
import json

logger = logging.getLogger(__name__)

class AdminPlanManagementService:
    def __init__(self):
        self.db = get_database()
        
        # Default plan structure template
        self.plan_template = {
            "name": "",
            "display_name": "",
            "description": "",
            "pricing": {
                "monthly_price": 0.0,
                "yearly_price": 0.0,
                "yearly_discount_percentage": 0.0,
                "launch_special": {
                    "enabled": False,
                    "special_price": 0.0,
                    "end_date": None,
                    "description": ""
                }
            },
            "features": {
                "included_features": [],
                "excluded_features": []
            },
            "limits": {
                "ai_content_generation": 0,
                "instagram_searches": 0,
                "emails_sent": 0,
                "websites_created": 0,
                "courses_created": 0,
                "templates_access": 0,
                "storage_gb": 0,
                "team_members": 0
            },
            "status": {
                "enabled": True,
                "available_for_new_subscriptions": True,
                "reason": ""
            },
            "metadata": {
                "created_at": None,
                "created_by": None,
                "last_modified": None,
                "modified_by": None,
                "version": 1
            }
        }
        
        # Available features that can be included/excluded
        self.available_features = [
            "link_in_bio_builder",
            "ai_content_generation", 
            "social_media_management",
            "email_marketing",
            "website_builder",
            "booking_system",
            "course_platform",
            "template_marketplace_selling",
            "advanced_analytics",
            "crm_integration",
            "workflow_automation",
            "multi_workspace",
            "team_collaboration",
            "custom_branding",
            "api_access",
            "priority_support",
            "white_label"
        ]

    async def health_check(self):
        """Health check for admin plan management service"""
        try:
            collection = self.db.admin_plans
            # Test database connection
            await collection.count_documents({})
            
            return {
                "success": True,
                "healthy": True,
                "service": "admin_plan_management",
                "timestamp": datetime.utcnow().isoformat(),
                "available_features": len(self.available_features)
            }
        except Exception as e:
            logger.error(f"Admin plan management health check failed: {e}")
            return {
                "success": False,
                "healthy": False,
                "error": str(e)
            }

    async def get_all_plans(self) -> Dict[str, Any]:
        """Get all plans with their complete configuration"""
        try:
            collection = self.db.admin_plans
            plans = await collection.find({"deleted": {"$ne": True}}).to_list(length=100)
            
            # Format plans for admin interface
            formatted_plans = {}
            for plan in plans:
                plan_name = plan.get("name")
                formatted_plans[plan_name] = {
                    "basic_info": {
                        "name": plan.get("name"),
                        "display_name": plan.get("display_name"),
                        "description": plan.get("description")
                    },
                    "pricing": plan.get("pricing", {}),
                    "features": plan.get("features", {}),
                    "limits": plan.get("limits", {}),
                    "status": plan.get("status", {}),
                    "metadata": plan.get("metadata", {}),
                    "subscription_count": await self._count_plan_subscriptions(plan_name)
                }
            
            # Get plan analytics summary
            analytics = await self._get_plans_summary_analytics()
            
            return {
                "success": True,
                "plans": formatted_plans,
                "total_plans": len(plans),
                "analytics": analytics,
                "available_features": self.available_features,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting all plans: {e}")
            return {"success": False, "error": str(e)}

    async def get_plan_details(self, plan_name: str) -> Dict[str, Any]:
        """Get detailed configuration for a specific plan"""
        try:
            collection = self.db.admin_plans
            plan = await collection.find_one({"name": plan_name, "deleted": {"$ne": True}})
            
            if not plan:
                return {"success": False, "error": f"Plan '{plan_name}' not found"}
            
            # Get subscription details
            subscription_count = await self._count_plan_subscriptions(plan_name)
            subscription_revenue = await self._calculate_plan_revenue(plan_name)
            
            # Get change history
            change_history = await self._get_plan_change_history(plan_name, 10)
            
            # Get usage analytics
            usage_analytics = await self._get_plan_usage_analytics(plan_name)
            
            return {
                "success": True,
                "plan": plan,
                "subscription_metrics": {
                    "active_subscriptions": subscription_count,
                    "monthly_revenue": subscription_revenue.get("monthly", 0),
                    "yearly_revenue": subscription_revenue.get("yearly", 0),
                    "total_revenue": subscription_revenue.get("total", 0)
                },
                "change_history": change_history,
                "usage_analytics": usage_analytics,
                "available_features": self.available_features
            }
            
        except Exception as e:
            logger.error(f"Error getting plan details: {e}")
            return {"success": False, "error": str(e)}

    async def update_plan_pricing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update pricing for a plan"""
        try:
            plan_name = data.get("plan_name")
            pricing_updates = data.get("pricing_updates", {})
            updated_by = data.get("updated_by")
            reason = data.get("reason", "Admin pricing update")
            
            # Validate plan exists
            collection = self.db.admin_plans
            plan = await collection.find_one({"name": plan_name, "deleted": {"$ne": True}})
            
            if not plan:
                return {"success": False, "error": f"Plan '{plan_name}' not found"}
            
            # Validate pricing fields
            valid_pricing_fields = ["monthly_price", "yearly_price", "yearly_discount_percentage"]
            invalid_fields = [field for field in pricing_updates.keys() if field not in valid_pricing_fields]
            if invalid_fields:
                return {"success": False, "error": f"Invalid pricing fields: {invalid_fields}"}
            
            # Calculate yearly discount percentage if both prices provided
            if "monthly_price" in pricing_updates and "yearly_price" in pricing_updates:
                monthly = pricing_updates["monthly_price"]
                yearly = pricing_updates["yearly_price"]
                if monthly > 0:
                    yearly_equivalent = monthly * 12
                    discount_pct = ((yearly_equivalent - yearly) / yearly_equivalent) * 100
                    pricing_updates["yearly_discount_percentage"] = round(discount_pct, 1)
            
            # Update plan pricing
            current_pricing = plan.get("pricing", {})
            current_pricing.update(pricing_updates)
            
            # Update metadata
            plan["pricing"] = current_pricing
            plan["metadata"]["last_modified"] = datetime.utcnow()
            plan["metadata"]["modified_by"] = updated_by
            plan["metadata"]["version"] = plan["metadata"].get("version", 1) + 1
            
            await collection.replace_one({"name": plan_name}, plan)
            
            # Log the change
            await self._log_plan_change(
                plan_name, "pricing_update", pricing_updates, updated_by, reason
            )
            
            # Calculate impact
            impact = await self._calculate_pricing_change_impact(plan_name, pricing_updates)
            
            return {
                "success": True,
                "plan_name": plan_name,
                "updated_pricing": current_pricing,
                "impact_analysis": impact,
                "message": f"Pricing updated for {plan_name} plan",
                "affected_subscriptions": impact.get("affected_subscriptions", 0)
            }
            
        except Exception as e:
            logger.error(f"Error updating plan pricing: {e}")
            return {"success": False, "error": str(e)}

    async def update_plan_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update features included in a plan"""
        try:
            plan_name = data.get("plan_name")
            features_to_add = data.get("features_to_add", [])
            features_to_remove = data.get("features_to_remove", [])
            updated_by = data.get("updated_by")
            reason = data.get("reason", "Admin features update")
            
            # Validate plan exists
            collection = self.db.admin_plans
            plan = await collection.find_one({"name": plan_name, "deleted": {"$ne": True}})
            
            if not plan:
                return {"success": False, "error": f"Plan '{plan_name}' not found"}
            
            # Validate features exist
            invalid_features = []
            for feature in features_to_add + features_to_remove:
                if feature not in self.available_features:
                    invalid_features.append(feature)
            
            if invalid_features:
                return {"success": False, "error": f"Invalid features: {invalid_features}"}
            
            # Update plan features
            current_features = plan.get("features", {"included_features": [], "excluded_features": []})
            included = set(current_features.get("included_features", []))
            excluded = set(current_features.get("excluded_features", []))
            
            # Add features
            for feature in features_to_add:
                included.add(feature)
                excluded.discard(feature)  # Remove from excluded if present
            
            # Remove features
            for feature in features_to_remove:
                included.discard(feature)
                excluded.add(feature)
            
            current_features["included_features"] = list(included)
            current_features["excluded_features"] = list(excluded)
            
            # Update plan
            plan["features"] = current_features
            plan["metadata"]["last_modified"] = datetime.utcnow()
            plan["metadata"]["modified_by"] = updated_by
            plan["metadata"]["version"] = plan["metadata"].get("version", 1) + 1
            
            await collection.replace_one({"name": plan_name}, plan)
            
            # Log the change
            change_data = {"features_added": features_to_add, "features_removed": features_to_remove}
            await self._log_plan_change(
                plan_name, "features_update", change_data, updated_by, reason
            )
            
            # Analyze impact on existing subscriptions
            impact = await self._analyze_feature_change_impact(plan_name, features_to_add, features_to_remove)
            
            return {
                "success": True,
                "plan_name": plan_name,
                "updated_features": current_features,
                "impact_analysis": impact,
                "message": f"Features updated for {plan_name} plan",
                "notification_required": impact.get("requires_notification", False)
            }
            
        except Exception as e:
            logger.error(f"Error updating plan features: {e}")
            return {"success": False, "error": str(e)}

    async def update_plan_limits(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update usage limits for a plan"""
        try:
            plan_name = data.get("plan_name")
            limit_updates = data.get("limit_updates", {})
            updated_by = data.get("updated_by")
            reason = data.get("reason", "Admin limits update")
            
            # Validate plan exists
            collection = self.db.admin_plans
            plan = await collection.find_one({"name": plan_name, "deleted": {"$ne": True}})
            
            if not plan:
                return {"success": False, "error": f"Plan '{plan_name}' not found"}
            
            # Validate limit fields
            valid_limit_fields = list(self.plan_template["limits"].keys())
            invalid_fields = [field for field in limit_updates.keys() if field not in valid_limit_fields]
            if invalid_fields:
                return {"success": False, "error": f"Invalid limit fields: {invalid_fields}"}
            
            # Validate limit values are positive integers
            for field, value in limit_updates.items():
                if not isinstance(value, (int, float)) or value < 0:
                    return {"success": False, "error": f"Invalid limit value for {field}: must be positive number"}
            
            # Update plan limits
            current_limits = plan.get("limits", {})
            current_limits.update(limit_updates)
            
            # Update plan
            plan["limits"] = current_limits
            plan["metadata"]["last_modified"] = datetime.utcnow()
            plan["metadata"]["modified_by"] = updated_by
            plan["metadata"]["version"] = plan["metadata"].get("version", 1) + 1
            
            await collection.replace_one({"name": plan_name}, plan)
            
            # Log the change
            await self._log_plan_change(
                plan_name, "limits_update", limit_updates, updated_by, reason
            )
            
            # Analyze impact on users currently over new limits
            impact = await self._analyze_limits_change_impact(plan_name, limit_updates)
            
            return {
                "success": True,
                "plan_name": plan_name,
                "updated_limits": current_limits,
                "impact_analysis": impact,
                "message": f"Limits updated for {plan_name} plan",
                "users_over_limit": impact.get("users_over_new_limits", 0)
            }
            
        except Exception as e:
            logger.error(f"Error updating plan limits: {e}")
            return {"success": False, "error": str(e)}

    async def update_plan_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enable or disable a plan"""
        try:
            plan_name = data.get("plan_name")
            action = data.get("action")  # "enable" or "disable"
            modified_by = data.get("modified_by")
            reason = data.get("reason", f"Admin {action} plan")
            
            # Validate plan exists
            collection = self.db.admin_plans
            plan = await collection.find_one({"name": plan_name, "deleted": {"$ne": True}})
            
            if not plan:
                return {"success": False, "error": f"Plan '{plan_name}' not found"}
            
            enabled = action == "enable"
            
            # Update plan status
            current_status = plan.get("status", {})
            current_status.update({
                "enabled": enabled,
                "available_for_new_subscriptions": enabled,
                "reason": reason,
                "last_status_change": datetime.utcnow(),
                "changed_by": modified_by
            })
            
            # Update plan
            plan["status"] = current_status
            plan["metadata"]["last_modified"] = datetime.utcnow()
            plan["metadata"]["modified_by"] = modified_by
            plan["metadata"]["version"] = plan["metadata"].get("version", 1) + 1
            
            await collection.replace_one({"name": plan_name}, plan)
            
            # Log the change
            await self._log_plan_change(
                plan_name, f"plan_{action}", {"enabled": enabled}, modified_by, reason
            )
            
            # Get impact information
            subscription_count = await self._count_plan_subscriptions(plan_name)
            
            return {
                "success": True,
                "plan_name": plan_name,
                "new_status": "enabled" if enabled else "disabled",
                "existing_subscriptions": subscription_count,
                "message": f"Plan {plan_name} has been {action}d",
                "warning": f"{subscription_count} existing subscriptions will continue unaffected" if not enabled and subscription_count > 0 else None
            }
            
        except Exception as e:
            logger.error(f"Error updating plan status: {e}")
            return {"success": False, "error": str(e)}

    async def update_plan_launch_pricing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update launch/promotional pricing for a plan"""
        try:
            plan_name = data.get("plan_name")
            launch_config = data.get("launch_config", {})
            updated_by = data.get("updated_by")
            reason = data.get("reason", "Admin launch pricing update")
            
            # Validate plan exists
            collection = self.db.admin_plans
            plan = await collection.find_one({"name": plan_name, "deleted": {"$ne": True}})
            
            if not plan:
                return {"success": False, "error": f"Plan '{plan_name}' not found"}
            
            # Validate launch config
            required_fields = ["enabled", "special_price", "end_date", "description"]
            missing_fields = [field for field in required_fields if field not in launch_config]
            if missing_fields:
                return {"success": False, "error": f"Missing launch config fields: {missing_fields}"}
            
            # Parse end date
            if isinstance(launch_config["end_date"], str):
                try:
                    launch_config["end_date"] = datetime.fromisoformat(launch_config["end_date"].replace("Z", "+00:00"))
                except ValueError:
                    return {"success": False, "error": "Invalid end_date format. Use ISO format."}
            
            # Update plan launch pricing
            current_pricing = plan.get("pricing", {})
            current_pricing["launch_special"] = launch_config
            
            # Update plan
            plan["pricing"] = current_pricing
            plan["metadata"]["last_modified"] = datetime.utcnow()
            plan["metadata"]["modified_by"] = updated_by
            plan["metadata"]["version"] = plan["metadata"].get("version", 1) + 1
            
            await collection.replace_one({"name": plan_name}, plan)
            
            # Log the change
            await self._log_plan_change(
                plan_name, "launch_pricing_update", launch_config, updated_by, reason
            )
            
            # Calculate promotional impact
            regular_price = current_pricing.get("monthly_price", 0)
            special_price = launch_config.get("special_price", 0)
            discount_pct = ((regular_price - special_price) / regular_price * 100) if regular_price > 0 else 0
            
            return {
                "success": True,
                "plan_name": plan_name,
                "launch_special": launch_config,
                "discount_percentage": round(discount_pct, 1),
                "regular_price": regular_price,
                "special_price": special_price,
                "message": f"Launch pricing updated for {plan_name} plan",
                "active_until": launch_config["end_date"].isoformat() if launch_config.get("enabled") else None
            }
            
        except Exception as e:
            logger.error(f"Error updating plan launch pricing: {e}")
            return {"success": False, "error": str(e)}

    async def create_new_plan(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new plan"""
        try:
            plan_name = data.get("plan_name")
            plan_config = data.get("plan_config", {})
            created_by = data.get("created_by")
            
            if not plan_name or not plan_config:
                return {"success": False, "error": "Plan name and configuration are required"}
            
            # Check if plan already exists
            collection = self.db.admin_plans
            existing_plan = await collection.find_one({"name": plan_name})
            
            if existing_plan:
                return {"success": False, "error": f"Plan '{plan_name}' already exists"}
            
            # Create new plan from template
            new_plan = self.plan_template.copy()
            new_plan["name"] = plan_name
            new_plan["display_name"] = plan_config.get("display_name", plan_name.title())
            new_plan["description"] = plan_config.get("description", "")
            
            # Set pricing
            if "pricing" in plan_config:
                new_plan["pricing"].update(plan_config["pricing"])
            
            # Set features
            if "features" in plan_config:
                new_plan["features"].update(plan_config["features"])
            
            # Set limits
            if "limits" in plan_config:
                new_plan["limits"].update(plan_config["limits"])
            
            # Set metadata
            new_plan["metadata"] = {
                "created_at": datetime.utcnow(),
                "created_by": created_by,
                "last_modified": datetime.utcnow(),
                "modified_by": created_by,
                "version": 1
            }
            
            # Insert new plan
            new_plan["_id"] = str(uuid.uuid4())
            await collection.insert_one(new_plan)
            
            # Log the creation
            await self._log_plan_change(
                plan_name, "plan_created", plan_config, created_by, "New plan created"
            )
            
            return {
                "success": True,
                "plan": new_plan,
                "message": f"New plan '{plan_name}' created successfully",
                "plan_id": new_plan["_id"]
            }
            
        except Exception as e:
            logger.error(f"Error creating new plan: {e}")
            return {"success": False, "error": str(e)}

    async def delete_plan(self, plan_name: str, deleted_by: str) -> Dict[str, Any]:
        """Delete a plan (soft delete if has subscriptions)"""
        try:
            # Check if plan exists
            collection = self.db.admin_plans
            plan = await collection.find_one({"name": plan_name, "deleted": {"$ne": True}})
            
            if not plan:
                return {"success": False, "error": f"Plan '{plan_name}' not found"}
            
            # Check for active subscriptions
            subscription_count = await self._count_plan_subscriptions(plan_name)
            
            if subscription_count > 0:
                # Soft delete - mark as deleted but keep for existing subscriptions
                plan["deleted"] = True
                plan["deleted_at"] = datetime.utcnow()
                plan["deleted_by"] = deleted_by
                plan["status"]["enabled"] = False
                plan["status"]["available_for_new_subscriptions"] = False
                plan["status"]["reason"] = f"Plan deleted - {subscription_count} active subscriptions remain"
                
                await collection.replace_one({"name": plan_name}, plan)
                
                message = f"Plan soft-deleted. {subscription_count} existing subscriptions will continue."
            else:
                # Hard delete - no active subscriptions
                await collection.delete_one({"name": plan_name})
                message = "Plan permanently deleted - no active subscriptions."
            
            # Log the deletion
            await self._log_plan_change(
                plan_name, "plan_deleted", {"subscription_count": subscription_count}, deleted_by, 
                "Plan deleted by admin"
            )
            
            return {
                "success": True,
                "plan_name": plan_name,
                "deletion_type": "soft" if subscription_count > 0 else "hard",
                "existing_subscriptions": subscription_count,
                "message": message
            }
            
        except Exception as e:
            logger.error(f"Error deleting plan: {e}")
            return {"success": False, "error": str(e)}

    async def bulk_plan_update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update multiple plans at once"""
        try:
            plan_updates = data.get("plan_updates", {})  # {plan_name: {updates}}
            update_type = data.get("update_type", "mixed")  # "pricing", "features", "limits", "mixed"
            updated_by = data.get("updated_by")
            reason = data.get("reason", "Bulk plan update")
            
            if not plan_updates:
                return {"success": False, "error": "No plan updates provided"}
            
            results = []
            total_success = 0
            total_failed = 0
            
            # Process each plan update
            for plan_name, updates in plan_updates.items():
                try:
                    result = None
                    
                    if update_type == "pricing" or "pricing" in updates:
                        result = await self.update_plan_pricing({
                            "plan_name": plan_name,
                            "pricing_updates": updates.get("pricing", updates),
                            "updated_by": updated_by,
                            "reason": f"{reason} (bulk operation)"
                        })
                    elif update_type == "features" or "features" in updates:
                        result = await self.update_plan_features({
                            "plan_name": plan_name,
                            "features_to_add": updates.get("features_to_add", []),
                            "features_to_remove": updates.get("features_to_remove", []),
                            "updated_by": updated_by,
                            "reason": f"{reason} (bulk operation)"
                        })
                    elif update_type == "limits" or "limits" in updates:
                        result = await self.update_plan_limits({
                            "plan_name": plan_name,
                            "limit_updates": updates.get("limits", updates),
                            "updated_by": updated_by,
                            "reason": f"{reason} (bulk operation)"
                        })
                    else:
                        # Mixed update - handle multiple types
                        if "pricing" in updates:
                            result = await self.update_plan_pricing({
                                "plan_name": plan_name,
                                "pricing_updates": updates["pricing"],
                                "updated_by": updated_by,
                                "reason": f"{reason} (bulk operation)"
                            })
                        if "features" in updates and result and result.get("success"):
                            result = await self.update_plan_features({
                                "plan_name": plan_name,
                                "features_to_add": updates["features"].get("add", []),
                                "features_to_remove": updates["features"].get("remove", []),
                                "updated_by": updated_by,
                                "reason": f"{reason} (bulk operation)"
                            })
                        if "limits" in updates and result and result.get("success"):
                            result = await self.update_plan_limits({
                                "plan_name": plan_name,
                                "limit_updates": updates["limits"],
                                "updated_by": updated_by,
                                "reason": f"{reason} (bulk operation)"
                            })
                    
                    if result and result.get("success"):
                        total_success += 1
                        results.append({
                            "plan_name": plan_name,
                            "status": "success",
                            "message": result.get("message", "Updated successfully")
                        })
                    else:
                        total_failed += 1
                        results.append({
                            "plan_name": plan_name,
                            "status": "failed",
                            "error": result.get("error", "Unknown error") if result else "No update performed"
                        })
                        
                except Exception as e:
                    total_failed += 1
                    results.append({
                        "plan_name": plan_name,
                        "status": "failed",
                        "error": str(e)
                    })
            
            # Create bulk operation log
            bulk_log = {
                "_id": str(uuid.uuid4()),
                "operation": "bulk_plan_update",
                "update_type": update_type,
                "total_plans": len(plan_updates),
                "successful_updates": total_success,
                "failed_updates": total_failed,
                "updated_by": updated_by,
                "reason": reason,
                "created_at": datetime.utcnow(),
                "results": results
            }
            
            bulk_ops_collection = self.db.admin_bulk_operations
            await bulk_ops_collection.insert_one(bulk_log)
            
            return {
                "success": total_failed == 0,
                "bulk_operation": bulk_log,
                "summary": {
                    "total_plans": len(plan_updates),
                    "successful": total_success,
                    "failed": total_failed,
                    "success_rate": (total_success / len(plan_updates)) * 100
                },
                "results": results,
                "message": f"Bulk update completed: {total_success} successful, {total_failed} failed"
            }
            
        except Exception as e:
            logger.error(f"Error in bulk plan update: {e}")
            return {"success": False, "error": str(e)}

    async def get_plan_analytics(self) -> Dict[str, Any]:
        """Get analytics on plan performance"""
        try:
            # Get plan subscription distribution
            subscriptions_collection = self.db.workspace_subscriptions
            
            # Plan popularity pipeline
            pipeline = [
                {"$unwind": "$bundles"},
                {"$group": {
                    "_id": "$bundles",
                    "subscription_count": {"$sum": 1},
                    "total_revenue": {"$sum": "$pricing.total_amount"}
                }},
                {"$sort": {"subscription_count": -1}}
            ]
            
            plan_stats = await subscriptions_collection.aggregate(pipeline).to_list(length=20)
            
            # Revenue trends by plan
            revenue_pipeline = [
                {"$unwind": "$bundles"},
                {"$group": {
                    "_id": {
                        "plan": "$bundles",
                        "year": {"$year": "$created_at"},
                        "month": {"$month": "$created_at"}
                    },
                    "monthly_revenue": {"$sum": "$pricing.total_amount"},
                    "subscription_count": {"$sum": 1}
                }},
                {"$sort": {"_id.year": -1, "_id.month": -1}},
                {"$limit": 50}
            ]
            
            revenue_trends = await subscriptions_collection.aggregate(revenue_pipeline).to_list(length=50)
            
            # Get plan change frequency
            changes_collection = self.db.admin_plan_changes
            recent_changes = await changes_collection.find({
                "created_at": {"$gte": datetime.utcnow() - timedelta(days=30)}
            }).to_list(length=100)
            
            # Plan status summary
            plans_collection = self.db.admin_plans
            all_plans = await plans_collection.find({"deleted": {"$ne": True}}).to_list(length=100)
            
            enabled_count = sum(1 for plan in all_plans if plan.get("status", {}).get("enabled", True))
            disabled_count = len(all_plans) - enabled_count
            
            return {
                "success": True,
                "analytics": {
                    "plan_performance": plan_stats,
                    "revenue_trends": revenue_trends,
                    "plan_status_summary": {
                        "total_plans": len(all_plans),
                        "enabled_plans": enabled_count,
                        "disabled_plans": disabled_count
                    },
                    "recent_changes": len(recent_changes),
                    "most_changed_plan": self._get_most_changed_plan(recent_changes),
                    "total_subscriptions": await subscriptions_collection.count_documents({"status": "active"})
                },
                "insights": await self._generate_plan_insights(plan_stats, revenue_trends),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting plan analytics: {e}")
            return {"success": False, "error": str(e)}

    async def get_plan_subscriptions(self, plan_name: str, limit: int = 50) -> Dict[str, Any]:
        """Get workspaces subscribed to a specific plan"""
        try:
            subscriptions_collection = self.db.workspace_subscriptions
            
            # Find subscriptions that include this plan
            subscriptions = await subscriptions_collection.find({
                "bundles": {"$in": [plan_name]},
                "status": "active"
            }).limit(limit).to_list(length=limit)
            
            # Format subscription data for admin view
            formatted_subscriptions = []
            for sub in subscriptions:
                workspace_info = await self._get_workspace_info(sub.get("workspace_id"))
                
                formatted_subscriptions.append({
                    "workspace_id": sub.get("workspace_id"),
                    "workspace_name": workspace_info.get("name", "Unknown"),
                    "subscription_date": sub.get("created_at"),
                    "billing_cycle": sub.get("billing_cycle", "monthly"),
                    "status": sub.get("status"),
                    "current_amount": sub.get("pricing", {}).get("total_amount", 0),
                    "bundles": sub.get("bundles", []),
                    "owner_email": workspace_info.get("owner_email", "Unknown")
                })
            
            return {
                "success": True,
                "plan_name": plan_name,
                "subscriptions": formatted_subscriptions,
                "total_subscriptions": len(formatted_subscriptions),
                "subscription_revenue": sum(sub["current_amount"] for sub in formatted_subscriptions)
            }
            
        except Exception as e:
            logger.error(f"Error getting plan subscriptions: {e}")
            return {"success": False, "error": str(e)}

    async def get_plan_change_history(self, plan_name: str = None, limit: int = 50) -> Dict[str, Any]:
        """Get history of plan changes"""
        try:
            collection = self.db.admin_plan_changes
            
            # Build query
            query = {}
            if plan_name:
                query["plan_name"] = plan_name
            
            # Get change history
            cursor = collection.find(query).sort("created_at", -1).limit(limit)
            change_history = await cursor.to_list(length=limit)
            
            # Enhance with additional info
            enhanced_history = []
            for change in change_history:
                enhanced_change = change.copy()
                
                # Calculate days since change
                days_ago = (datetime.utcnow() - change["created_at"]).days
                enhanced_change["days_ago"] = days_ago
                
                # Add admin user info if available
                admin_info = await self._get_admin_info(change.get("created_by"))
                enhanced_change["admin_name"] = admin_info.get("name", "Unknown Admin")
                
                enhanced_history.append(enhanced_change)
            
            return {
                "success": True,
                "plan_name": plan_name or "All Plans",
                "change_history": enhanced_history,
                "total_changes": len(change_history),
                "filtered": plan_name is not None
            }
            
        except Exception as e:
            logger.error(f"Error getting plan change history: {e}")
            return {"success": False, "error": str(e)}

    # Helper methods
    async def _count_plan_subscriptions(self, plan_name: str) -> int:
        """Count active subscriptions for a plan"""
        try:
            subscriptions_collection = self.db.workspace_subscriptions
            count = await subscriptions_collection.count_documents({
                "bundles": {"$in": [plan_name]},
                "status": "active"
            })
            return count
        except Exception as e:
            logger.error(f"Error counting plan subscriptions: {e}")
            return 0

    async def _calculate_plan_revenue(self, plan_name: str) -> Dict[str, float]:
        """Calculate revenue for a plan"""
        try:
            subscriptions_collection = self.db.workspace_subscriptions
            
            # Get all active subscriptions for this plan
            subscriptions = await subscriptions_collection.find({
                "bundles": {"$in": [plan_name]},
                "status": "active"
            }).to_list(length=1000)
            
            monthly_revenue = 0
            yearly_revenue = 0
            
            for sub in subscriptions:
                billing_cycle = sub.get("billing_cycle", "monthly")
                amount = sub.get("pricing", {}).get("total_amount", 0)
                
                if billing_cycle == "monthly":
                    monthly_revenue += amount
                elif billing_cycle == "yearly":
                    yearly_revenue += amount
            
            return {
                "monthly": monthly_revenue,
                "yearly": yearly_revenue,
                "total": monthly_revenue + yearly_revenue
            }
            
        except Exception as e:
            logger.error(f"Error calculating plan revenue: {e}")
            return {"monthly": 0, "yearly": 0, "total": 0}

    async def _log_plan_change(self, plan_name: str, change_type: str, change_data: Dict[str, Any], 
                             created_by: str, reason: str):
        """Log a plan change"""
        try:
            change_log = {
                "_id": str(uuid.uuid4()),
                "plan_name": plan_name,
                "change_type": change_type,
                "change_data": change_data,
                "reason": reason,
                "created_by": created_by,
                "created_at": datetime.utcnow()
            }
            
            collection = self.db.admin_plan_changes
            await collection.insert_one(change_log)
            
        except Exception as e:
            logger.error(f"Error logging plan change: {e}")

    async def _calculate_pricing_change_impact(self, plan_name: str, pricing_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate impact of pricing changes"""
        try:
            subscription_count = await self._count_plan_subscriptions(plan_name)
            
            # Calculate revenue impact (simplified)
            if "monthly_price" not in pricing_updates:
                return {"affected_subscriptions": subscription_count, "revenue_impact": 0}
            
            # This is a simplified calculation - in production would be more complex
            price_increase = pricing_updates.get("monthly_price", 0)
            estimated_impact = price_increase * subscription_count
            
            return {
                "affected_subscriptions": subscription_count,
                "estimated_monthly_revenue_change": estimated_impact,
                "impact_type": "pricing_change"
            }
            
        except Exception as e:
            logger.error(f"Error calculating pricing impact: {e}")
            return {"affected_subscriptions": 0, "revenue_impact": 0}

    async def _analyze_feature_change_impact(self, plan_name: str, features_added: List[str], 
                                           features_removed: List[str]) -> Dict[str, Any]:
        """Analyze impact of feature changes"""
        try:
            subscription_count = await self._count_plan_subscriptions(plan_name)
            
            # Simplified impact analysis
            requires_notification = len(features_removed) > 0
            impact_level = "high" if features_removed else "low"
            
            return {
                "affected_subscriptions": subscription_count,
                "features_added": len(features_added),
                "features_removed": len(features_removed),
                "requires_notification": requires_notification,
                "impact_level": impact_level
            }
            
        except Exception as e:
            logger.error(f"Error analyzing feature change impact: {e}")
            return {"affected_subscriptions": 0, "requires_notification": False}

    async def _analyze_limits_change_impact(self, plan_name: str, limit_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze impact of limit changes"""
        try:
            subscription_count = await self._count_plan_subscriptions(plan_name)
            
            # Check if any limits were reduced
            limits_reduced = []
            for limit_name, new_value in limit_updates.items():
                # This would need to compare with current plan limits
                # Simplified for now
                limits_reduced.append(limit_name)
            
            return {
                "affected_subscriptions": subscription_count,
                "limits_changed": len(limit_updates),
                "limits_reduced": limits_reduced,
                "users_over_new_limits": 0  # Would calculate in production
            }
            
        except Exception as e:
            logger.error(f"Error analyzing limits change impact: {e}")
            return {"affected_subscriptions": 0, "limits_changed": 0}

    async def _get_plans_summary_analytics(self) -> Dict[str, Any]:
        """Get summary analytics for all plans"""
        try:
            subscriptions_collection = self.db.workspace_subscriptions
            
            total_revenue = await subscriptions_collection.aggregate([
                {"$group": {"_id": None, "total": {"$sum": "$pricing.total_amount"}}}
            ]).to_list(length=1)
            
            return {
                "total_active_subscriptions": await subscriptions_collection.count_documents({"status": "active"}),
                "total_revenue": total_revenue[0]["total"] if total_revenue else 0,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting plans summary analytics: {e}")
            return {}

    async def _get_plan_change_history(self, plan_name: str, limit: int) -> List[Dict[str, Any]]:
        """Get recent change history for a plan"""
        try:
            collection = self.db.admin_plan_changes
            
            changes = await collection.find(
                {"plan_name": plan_name}
            ).sort("created_at", -1).limit(limit).to_list(length=limit)
            
            return changes
            
        except Exception as e:
            logger.error(f"Error getting plan change history: {e}")
            return []

    async def _get_plan_usage_analytics(self, plan_name: str) -> Dict[str, Any]:
        """Get usage analytics for a plan"""
        try:
            # This would integrate with usage tracking system
            # Simplified for now
            return {
                "average_usage": {},
                "top_features": [],
                "usage_trends": []
            }
            
        except Exception as e:
            logger.error(f"Error getting plan usage analytics: {e}")
            return {}

    async def _get_workspace_info(self, workspace_id: str) -> Dict[str, Any]:
        """Get workspace information"""
        try:
            workspaces_collection = self.db.workspaces
            workspace = await workspaces_collection.find_one({"_id": workspace_id})
            
            if workspace:
                return {
                    "name": workspace.get("name", "Unknown"),
                    "owner_email": workspace.get("owner_email", "Unknown")
                }
            return {"name": "Unknown", "owner_email": "Unknown"}
            
        except Exception as e:
            logger.error(f"Error getting workspace info: {e}")
            return {"name": "Unknown", "owner_email": "Unknown"}

    async def _get_admin_info(self, admin_id: str) -> Dict[str, Any]:
        """Get admin user information"""
        try:
            # This would get admin user details
            # Simplified for now
            return {"name": "Admin User"}
            
        except Exception as e:
            logger.error(f"Error getting admin info: {e}")
            return {"name": "Unknown Admin"}

    def _get_most_changed_plan(self, recent_changes: List[Dict[str, Any]]) -> str:
        """Get the plan with most recent changes"""
        try:
            if not recent_changes:
                return "None"
            
            plan_counts = {}
            for change in recent_changes:
                plan_name = change.get("plan_name", "Unknown")
                plan_counts[plan_name] = plan_counts.get(plan_name, 0) + 1
            
            return max(plan_counts, key=plan_counts.get) if plan_counts else "None"
            
        except Exception as e:
            logger.error(f"Error getting most changed plan: {e}")
            return "Unknown"

    async def _generate_plan_insights(self, plan_stats: List[Dict], revenue_trends: List[Dict]) -> List[str]:
        """Generate insights from plan analytics"""
        insights = []
        
        try:
            if plan_stats:
                # Most popular plan
                most_popular = plan_stats[0]
                insights.append(f"Most popular plan: {most_popular['_id']} with {most_popular['subscription_count']} subscriptions")
                
                # Revenue insights
                if len(plan_stats) > 1:
                    total_subs = sum(plan['subscription_count'] for plan in plan_stats)
                    top_plan_percentage = (most_popular['subscription_count'] / total_subs) * 100
                    insights.append(f"Top plan represents {top_plan_percentage:.1f}% of all subscriptions")
            
            # Add more insights based on trends
            if revenue_trends:
                insights.append(f"Revenue data available for {len(revenue_trends)} plan-month combinations")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating plan insights: {e}")
            return ["Analytics data available but insights generation failed"]


# Service instance
_admin_plan_management_service = None

def get_admin_plan_management_service() -> AdminPlanManagementService:
    """Get admin plan management service instance"""
    global _admin_plan_management_service
    if _admin_plan_management_service is None:
        _admin_plan_management_service = AdminPlanManagementService()
    return _admin_plan_management_service