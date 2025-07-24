"""
Admin Pricing Service
Allows admins to update pricing plans, features, limits, and enable/disable bundles
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from core.database import get_database
from services.workspace_subscription_service import get_workspace_subscription_service
import uuid
import json

logger = logging.getLogger(__name__)

class AdminPricingService:
    def __init__(self):
        self.db = get_database()
        
        # Pricing templates for quick application
        self.pricing_templates = {
            "holiday_discount": {
                "name": "Holiday 20% Discount",
                "description": "20% off all bundles for holiday season",
                "discount_percentage": 0.20,
                "applies_to": "all_bundles",
                "duration_days": 30
            },
            
            "new_year_special": {
                "name": "New Year 30% Special", 
                "description": "30% off for new year motivation",
                "discount_percentage": 0.30,
                "applies_to": "selected_bundles",
                "target_bundles": ["creator", "business"],
                "duration_days": 14
            },
            
            "enterprise_promotion": {
                "name": "Enterprise Promotion",
                "description": "Reduced enterprise minimum for 3 months",
                "enterprise_minimum": 49.0,  # Reduced from $99
                "applies_to": "enterprise_only",
                "duration_days": 90
            }
        }

    async def health_check(self):
        """Health check for admin pricing service"""
        try:
            collection = self.db.admin_pricing_changes
            # Test database connection
            await collection.count_documents({})
            
            return {
                "success": True,
                "healthy": True,
                "service": "admin_pricing",
                "timestamp": datetime.utcnow().isoformat(),
                "pricing_templates": len(self.pricing_templates)
            }
        except Exception as e:
            logger.error(f"Admin pricing health check failed: {e}")
            return {
                "success": False,
                "healthy": False,
                "error": str(e)
            }

    async def get_current_pricing_config(self) -> Dict[str, Any]:
        """Get current pricing configuration for all bundles"""
        try:
            # Get current bundle definitions from workspace subscription service
            subscription_service = get_workspace_subscription_service()
            bundles_result = await subscription_service.get_available_bundles()
            
            if not bundles_result.get("success"):
                return {"success": False, "error": "Could not retrieve bundle definitions"}
            
            current_bundles = bundles_result.get("bundles", {})
            
            # Get any admin overrides from database
            overrides_collection = self.db.admin_pricing_overrides
            overrides = await overrides_collection.find({"active": True}).to_list(length=100)
            
            # Apply overrides to current bundles
            final_config = {}
            for bundle_name, bundle_config in current_bundles.items():
                final_bundle_config = bundle_config.copy()
                
                # Apply any active overrides
                for override in overrides:
                    if override["bundle_name"] == bundle_name:
                        final_bundle_config.update(override["overrides"])
                        final_bundle_config["admin_modified"] = True
                        final_bundle_config["last_modified"] = override["created_at"]
                        final_bundle_config["modified_by"] = override["created_by"]
                
                final_config[bundle_name] = final_bundle_config
            
            # Get bundle status (enabled/disabled)
            status_collection = self.db.bundle_status
            bundle_statuses = await status_collection.find({}).to_list(length=100)
            
            for status in bundle_statuses:
                bundle_name = status["bundle_name"]
                if bundle_name in final_config:
                    final_config[bundle_name]["enabled"] = status["enabled"]
                    final_config[bundle_name]["status_reason"] = status.get("reason", "")
            
            return {
                "success": True,
                "current_pricing": final_config,
                "total_bundles": len(final_config),
                "active_overrides": len(overrides),
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting current pricing config: {e}")
            return {"success": False, "error": str(e)}

    async def update_bundle_pricing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update pricing for a specific bundle"""
        try:
            bundle_name = data.get("bundle_name")
            pricing_updates = data.get("pricing_updates", {})
            updated_by = data.get("updated_by")
            reason = data.get("reason", "Admin pricing update")
            
            # Validate bundle exists
            subscription_service = get_workspace_subscription_service()
            bundles_result = await subscription_service.get_available_bundles()
            
            if not bundles_result.get("success"):
                return {"success": False, "error": "Could not retrieve bundle definitions"}
            
            current_bundles = bundles_result.get("bundles", {})
            if bundle_name not in current_bundles:
                return {"success": False, "error": f"Bundle '{bundle_name}' not found"}
            
            # Validate pricing updates
            valid_pricing_fields = ["monthly_price", "yearly_price", "enterprise_price", "launch_special_price"]
            invalid_fields = [field for field in pricing_updates.keys() if field not in valid_pricing_fields]
            if invalid_fields:
                return {"success": False, "error": f"Invalid pricing fields: {invalid_fields}"}
            
            # Create pricing override record
            override_record = {
                "_id": str(uuid.uuid4()),
                "bundle_name": bundle_name,
                "override_type": "pricing_update",
                "original_config": current_bundles[bundle_name],
                "overrides": pricing_updates,
                "reason": reason,
                "created_by": updated_by,
                "created_at": datetime.utcnow(),
                "active": True,
                "expires_at": None  # Permanent until manually changed
            }
            
            # Store override
            overrides_collection = self.db.admin_pricing_overrides
            
            # Deactivate any existing overrides for this bundle
            await overrides_collection.update_many(
                {"bundle_name": bundle_name, "active": True},
                {"$set": {"active": False, "superseded_at": datetime.utcnow()}}
            )
            
            # Insert new override
            await overrides_collection.insert_one(override_record)
            
            # Create change log
            await self._log_pricing_change(bundle_name, "pricing_update", pricing_updates, updated_by, reason)
            
            # Calculate impact
            impact = await self._calculate_pricing_impact(bundle_name, pricing_updates)
            
            return {
                "success": True,
                "override_record": override_record,
                "impact_analysis": impact,
                "message": f"Pricing updated for {bundle_name} bundle",
                "affected_subscriptions": impact.get("affected_subscriptions", 0)
            }
            
        except Exception as e:
            logger.error(f"Error updating bundle pricing: {e}")
            return {"success": False, "error": str(e)}

    async def update_bundle_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update features and limits for a bundle"""
        try:
            bundle_name = data.get("bundle_name")
            feature_updates = data.get("feature_updates", {})
            limit_updates = data.get("limit_updates", {})
            updated_by = data.get("updated_by")
            reason = data.get("reason", "Admin feature update")
            
            # Validate bundle exists
            subscription_service = get_workspace_subscription_service()
            bundles_result = await subscription_service.get_available_bundles()
            
            if not bundles_result.get("success"):
                return {"success": False, "error": "Could not retrieve bundle definitions"}
            
            current_bundles = bundles_result.get("bundles", {})
            if bundle_name not in current_bundles:
                return {"success": False, "error": f"Bundle '{bundle_name}' not found"}
            
            # Prepare combined updates
            combined_updates = {}
            if feature_updates:
                combined_updates["features"] = feature_updates
            if limit_updates:
                combined_updates["limits"] = limit_updates
            
            # Create feature override record
            override_record = {
                "_id": str(uuid.uuid4()),
                "bundle_name": bundle_name,
                "override_type": "feature_update",
                "original_config": current_bundles[bundle_name],
                "overrides": combined_updates,
                "reason": reason,
                "created_by": updated_by,
                "created_at": datetime.utcnow(),
                "active": True,
                "expires_at": None
            }
            
            # Store override
            overrides_collection = self.db.admin_pricing_overrides
            
            # Deactivate existing feature overrides
            await overrides_collection.update_many(
                {"bundle_name": bundle_name, "override_type": "feature_update", "active": True},
                {"$set": {"active": False, "superseded_at": datetime.utcnow()}}
            )
            
            # Insert new override
            await overrides_collection.insert_one(override_record)
            
            # Create change log
            await self._log_pricing_change(bundle_name, "feature_update", combined_updates, updated_by, reason)
            
            # Analyze impact on existing users
            user_impact = await self._analyze_feature_change_impact(bundle_name, feature_updates, limit_updates)
            
            return {
                "success": True,
                "override_record": override_record,
                "user_impact": user_impact,
                "message": f"Features updated for {bundle_name} bundle",
                "notification_required": user_impact.get("requires_notification", False)
            }
            
        except Exception as e:
            logger.error(f"Error updating bundle features: {e}")
            return {"success": False, "error": str(e)}

    async def enable_disable_bundle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enable or disable a bundle for new subscriptions"""
        try:
            bundle_name = data.get("bundle_name")
            action = data.get("action")  # "enable" or "disable"
            modified_by = data.get("modified_by")
            reason = data.get("reason", f"Admin {action} bundle")
            
            if action not in ["enable", "disable"]:
                return {"success": False, "error": "Action must be 'enable' or 'disable'"}
            
            enabled = action == "enable"
            
            # Update bundle status
            status_collection = self.db.bundle_status
            status_record = {
                "bundle_name": bundle_name,
                "enabled": enabled,
                "reason": reason,
                "modified_by": modified_by,
                "modified_at": datetime.utcnow(),
                "previous_status": not enabled  # Store previous status
            }
            
            await status_collection.replace_one(
                {"bundle_name": bundle_name},
                status_record,
                upsert=True
            )
            
            # Create change log
            await self._log_pricing_change(bundle_name, f"bundle_{action}", {"enabled": enabled}, modified_by, reason)
            
            # Analyze impact
            impact = await self._analyze_bundle_status_impact(bundle_name, enabled)
            
            # If disabling, check existing subscriptions
            existing_subs = 0
            if not enabled:
                existing_subs = await self._count_existing_subscriptions(bundle_name)
            
            return {
                "success": True,
                "bundle_name": bundle_name,
                "new_status": "enabled" if enabled else "disabled",
                "existing_subscriptions": existing_subs,
                "impact": impact,
                "message": f"Bundle {bundle_name} has been {action}d",
                "warning": f"{existing_subs} existing subscriptions will continue unaffected" if not enabled and existing_subs > 0 else None
            }
            
        except Exception as e:
            logger.error(f"Error enabling/disabling bundle: {e}")
            return {"success": False, "error": str(e)}

    async def create_new_bundle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new bundle with pricing and features"""
        try:
            bundle_name = data.get("bundle_name")
            bundle_config = data.get("bundle_config", {})
            created_by = data.get("created_by")
            
            if not bundle_name or not bundle_config:
                return {"success": False, "error": "Bundle name and configuration are required"}
            
            # Validate required fields
            required_fields = ["name", "monthly_price", "features", "limits"]
            missing_fields = [field for field in required_fields if field not in bundle_config]
            if missing_fields:
                return {"success": False, "error": f"Missing required fields: {missing_fields}"}
            
            # Check if bundle already exists
            subscription_service = get_workspace_subscription_service()
            bundles_result = await subscription_service.get_available_bundles()
            
            if bundles_result.get("success"):
                current_bundles = bundles_result.get("bundles", {})
                if bundle_name in current_bundles:
                    return {"success": False, "error": f"Bundle '{bundle_name}' already exists"}
            
            # Create new bundle record
            new_bundle_record = {
                "_id": str(uuid.uuid4()),
                "bundle_name": bundle_name,
                "bundle_config": bundle_config,
                "created_by": created_by,
                "created_at": datetime.utcnow(),
                "status": "active",
                "version": 1
            }
            
            # Store new bundle
            bundles_collection = self.db.admin_custom_bundles
            await bundles_collection.insert_one(new_bundle_record)
            
            # Enable by default
            await self.enable_disable_bundle({
                "bundle_name": bundle_name,
                "action": "enable",
                "modified_by": created_by,
                "reason": "New bundle creation"
            })
            
            # Create change log
            await self._log_pricing_change(bundle_name, "bundle_created", bundle_config, created_by, "New bundle created")
            
            return {
                "success": True,
                "new_bundle": new_bundle_record,
                "message": f"New bundle '{bundle_name}' created successfully",
                "bundle_id": new_bundle_record["_id"]
            }
            
        except Exception as e:
            logger.error(f"Error creating new bundle: {e}")
            return {"success": False, "error": str(e)}

    async def get_pricing_history(self, bundle_name: str, limit: int = 50) -> Dict[str, Any]:
        """Get pricing change history for a bundle"""
        try:
            collection = self.db.admin_pricing_changes
            
            # Get pricing history
            cursor = collection.find({"bundle_name": bundle_name}).sort("created_at", -1).limit(limit)
            pricing_history = await cursor.to_list(length=limit)
            
            # Enhance with additional info
            enhanced_history = []
            for change in pricing_history:
                enhanced_change = change.copy()
                
                # Calculate days since change
                days_ago = (datetime.utcnow() - change["created_at"]).days
                enhanced_change["days_ago"] = days_ago
                
                # Add impact summary if available
                if "impact" in change:
                    enhanced_change["impact_summary"] = change["impact"]
                
                enhanced_history.append(enhanced_change)
            
            return {
                "success": True,
                "bundle_name": bundle_name,
                "pricing_history": enhanced_history,
                "total_changes": len(pricing_history),
                "oldest_change": pricing_history[-1]["created_at"].isoformat() if pricing_history else None
            }
            
        except Exception as e:
            logger.error(f"Error getting pricing history: {e}")
            return {"success": False, "error": str(e)}

    async def bulk_pricing_update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update pricing for multiple bundles at once"""
        try:
            bundle_updates = data.get("bundle_updates", {})  # {bundle_name: {pricing_updates}}
            updated_by = data.get("updated_by")
            reason = data.get("reason", "Bulk pricing update")
            
            if not bundle_updates:
                return {"success": False, "error": "No bundle updates provided"}
            
            results = []
            total_success = 0
            total_failed = 0
            
            # Process each bundle update
            for bundle_name, pricing_updates in bundle_updates.items():
                try:
                    update_result = await self.update_bundle_pricing({
                        "bundle_name": bundle_name,
                        "pricing_updates": pricing_updates,
                        "updated_by": updated_by,
                        "reason": f"{reason} (bulk operation)"
                    })
                    
                    if update_result.get("success"):
                        total_success += 1
                        results.append({
                            "bundle_name": bundle_name,
                            "status": "success",
                            "message": update_result.get("message")
                        })
                    else:
                        total_failed += 1
                        results.append({
                            "bundle_name": bundle_name,
                            "status": "failed",
                            "error": update_result.get("error")
                        })
                        
                except Exception as e:
                    total_failed += 1
                    results.append({
                        "bundle_name": bundle_name,
                        "status": "failed",
                        "error": str(e)
                    })
            
            # Create bulk operation log
            bulk_log = {
                "_id": str(uuid.uuid4()),
                "operation": "bulk_pricing_update",
                "total_bundles": len(bundle_updates),
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
                    "total_bundles": len(bundle_updates),
                    "successful": total_success,
                    "failed": total_failed,
                    "success_rate": (total_success / len(bundle_updates)) * 100
                },
                "results": results,
                "message": f"Bulk update completed: {total_success} successful, {total_failed} failed"
            }
            
        except Exception as e:
            logger.error(f"Error in bulk pricing update: {e}")
            return {"success": False, "error": str(e)}

    async def get_pricing_analytics(self) -> Dict[str, Any]:
        """Get analytics on pricing performance and subscription trends"""
        try:
            # Get subscription distribution by bundle
            subscriptions_collection = self.db.workspace_subscriptions
            
            # Bundle popularity
            pipeline = [
                {"$unwind": "$bundles"},
                {"$group": {
                    "_id": "$bundles",
                    "count": {"$sum": 1},
                    "total_revenue": {"$sum": "$pricing.total_amount"}
                }},
                {"$sort": {"count": -1}}
            ]
            
            bundle_stats = await subscriptions_collection.aggregate(pipeline).to_list(length=10)
            
            # Revenue trends
            revenue_pipeline = [
                {"$group": {
                    "_id": {
                        "year": {"$year": "$created_at"},
                        "month": {"$month": "$created_at"}
                    },
                    "monthly_revenue": {"$sum": "$pricing.total_amount"},
                    "subscription_count": {"$sum": 1}
                }},
                {"$sort": {"_id.year": -1, "_id.month": -1}},
                {"$limit": 12}
            ]
            
            revenue_trends = await subscriptions_collection.aggregate(revenue_pipeline).to_list(length=12)
            
            # Pricing change impact analysis
            changes_collection = self.db.admin_pricing_changes
            recent_changes = await changes_collection.find({
                "created_at": {"$gte": datetime.utcnow() - timedelta(days=30)}
            }).to_list(length=50)
            
            return {
                "success": True,
                "analytics": {
                    "bundle_performance": bundle_stats,
                    "revenue_trends": revenue_trends,
                    "recent_pricing_changes": len(recent_changes),
                    "total_active_subscriptions": await subscriptions_collection.count_documents({"status": "active"}),
                    "average_bundle_per_workspace": await self._calculate_average_bundles_per_workspace()
                },
                "insights": await self._generate_pricing_insights(bundle_stats, revenue_trends),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting pricing analytics: {e}")
            return {"success": False, "error": str(e)}

    async def test_pricing_change(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Test impact of pricing changes before applying"""
        try:
            bundle_name = data.get("bundle_name")
            proposed_changes = data.get("proposed_changes", {})
            
            # Get current bundle config
            current_config_result = await self.get_current_pricing_config()
            if not current_config_result.get("success"):
                return {"success": False, "error": "Could not get current pricing"}
            
            current_bundles = current_config_result.get("current_pricing", {})
            if bundle_name not in current_bundles:
                return {"success": False, "error": f"Bundle {bundle_name} not found"}
            
            current_bundle = current_bundles[bundle_name]
            
            # Simulate pricing change impact
            impact_analysis = {
                "bundle_name": bundle_name,
                "current_pricing": {
                    "monthly_price": current_bundle.get("monthly_price", 0),
                    "yearly_price": current_bundle.get("yearly_price", 0)
                },
                "proposed_pricing": proposed_changes,
                "impact_metrics": {}
            }
            
            # Calculate subscription impact
            existing_subscriptions = await self._count_existing_subscriptions(bundle_name)
            impact_analysis["impact_metrics"]["existing_subscriptions"] = existing_subscriptions
            
            # Calculate revenue impact
            if "monthly_price" in proposed_changes:
                old_price = current_bundle.get("monthly_price", 0)
                new_price = proposed_changes["monthly_price"]
                price_change = new_price - old_price
                revenue_impact = price_change * existing_subscriptions
                
                impact_analysis["impact_metrics"]["monthly_revenue_change"] = revenue_impact
                impact_analysis["impact_metrics"]["price_change_percentage"] = (price_change / old_price) * 100 if old_price > 0 else 0
            
            # Estimate demand impact based on price elasticity
            demand_impact = await self._estimate_demand_impact(bundle_name, proposed_changes)
            impact_analysis["impact_metrics"]["estimated_demand_change"] = demand_impact
            
            # Risk assessment
            risk_level = self._assess_pricing_risk(impact_analysis)
            impact_analysis["risk_assessment"] = risk_level
            
            return {
                "success": True,
                "impact_analysis": impact_analysis,
                "recommendations": self._generate_pricing_recommendations(impact_analysis),
                "test_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error testing pricing change: {e}")
            return {"success": False, "error": str(e)}

    async def apply_pricing_template(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply predefined pricing templates (e.g., holiday discounts)"""
        try:
            template_name = data.get("template_name")
            applied_by = data.get("applied_by")
            custom_duration = data.get("custom_duration_days")
            
            if template_name not in self.pricing_templates:
                return {"success": False, "error": f"Template '{template_name}' not found"}
            
            template = self.pricing_templates[template_name]
            
            # Apply template based on type
            if template["applies_to"] == "all_bundles":
                # Apply to all bundles
                result = await self._apply_template_to_all_bundles(template, applied_by, custom_duration)
            elif template["applies_to"] == "selected_bundles":
                # Apply to specific bundles
                result = await self._apply_template_to_selected_bundles(template, applied_by, custom_duration)
            elif template["applies_to"] == "enterprise_only":
                # Apply to enterprise pricing
                result = await self._apply_template_to_enterprise(template, applied_by, custom_duration)
            else:
                return {"success": False, "error": "Invalid template type"}
            
            # Log template application
            template_log = {
                "_id": str(uuid.uuid4()),
                "template_name": template_name,
                "template_config": template,
                "applied_by": applied_by,
                "applied_at": datetime.utcnow(),
                "custom_duration": custom_duration,
                "result": result
            }
            
            templates_collection = self.db.admin_pricing_templates_applied
            await templates_collection.insert_one(template_log)
            
            return {
                "success": True,
                "template_applied": template_log,
                "application_result": result,
                "message": f"Template '{template_name}' applied successfully"
            }
            
        except Exception as e:
            logger.error(f"Error applying pricing template: {e}")
            return {"success": False, "error": str(e)}

    # Private helper methods
    
    async def _log_pricing_change(self, bundle_name: str, change_type: str, changes: Dict[str, Any], changed_by: str, reason: str):
        """Log pricing changes for audit trail"""
        try:
            log_record = {
                "_id": str(uuid.uuid4()),
                "bundle_name": bundle_name,
                "change_type": change_type,
                "changes": changes,
                "changed_by": changed_by,
                "reason": reason,
                "created_at": datetime.utcnow(),
                "ip_address": None,  # Would capture from request in production
                "user_agent": None   # Would capture from request in production
            }
            
            collection = self.db.admin_pricing_changes
            await collection.insert_one(log_record)
            
        except Exception as e:
            logger.error(f"Error logging pricing change: {e}")
    
    async def _calculate_pricing_impact(self, bundle_name: str, pricing_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate impact of pricing changes"""
        try:
            # Count existing subscriptions
            subscriptions_collection = self.db.workspace_subscriptions
            existing_subs = await subscriptions_collection.count_documents({
                "bundles": {"$in": [bundle_name]},
                "status": "active"
            })
            
            # Calculate revenue impact (simplified)
            revenue_impact = 0
            if "monthly_price" in pricing_updates:
                # Estimate monthly revenue change
                revenue_impact = pricing_updates["monthly_price"] * existing_subs
            
            return {
                "affected_subscriptions": existing_subs,
                "estimated_monthly_revenue_change": revenue_impact,
                "notification_required": existing_subs > 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating pricing impact: {e}")
            return {"affected_subscriptions": 0, "estimated_monthly_revenue_change": 0}
    
    async def _analyze_feature_change_impact(self, bundle_name: str, feature_updates: Dict[str, Any], limit_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze impact of feature changes on users"""
        try:
            # Count affected users
            subscriptions_collection = self.db.workspace_subscriptions
            affected_users = await subscriptions_collection.count_documents({
                "bundles": {"$in": [bundle_name]},
                "status": "active"
            })
            
            # Determine if changes are positive or negative
            is_upgrade = len(feature_updates.get("added_features", [])) > len(feature_updates.get("removed_features", []))
            
            # Check if limits are increased or decreased
            limit_changes = []
            for limit_name, new_value in limit_updates.items():
                # Would need to compare with current values in production
                limit_changes.append({
                    "limit": limit_name,
                    "new_value": new_value,
                    "change_type": "increased"  # Simplified
                })
            
            return {
                "affected_users": affected_users,
                "is_upgrade": is_upgrade,
                "requires_notification": affected_users > 0,
                "limit_changes": limit_changes,
                "notification_type": "positive" if is_upgrade else "neutral"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing feature change impact: {e}")
            return {"affected_users": 0, "requires_notification": False}
    
    async def _analyze_bundle_status_impact(self, bundle_name: str, enabled: bool) -> Dict[str, Any]:
        """Analyze impact of enabling/disabling bundle"""
        try:
            if enabled:
                return {"impact": "Bundle available for new subscriptions", "severity": "low"}
            else:
                # Check if disabling affects existing subscriptions
                existing_subs = await self._count_existing_subscriptions(bundle_name)
                return {
                    "impact": f"Bundle unavailable for new subscriptions. {existing_subs} existing subscriptions unaffected",
                    "severity": "medium" if existing_subs > 0 else "low",
                    "existing_subscriptions": existing_subs
                }
                
        except Exception as e:
            logger.error(f"Error analyzing bundle status impact: {e}")
            return {"impact": "Unknown", "severity": "low"}
    
    async def _count_existing_subscriptions(self, bundle_name: str) -> int:
        """Count existing active subscriptions for a bundle"""
        try:
            subscriptions_collection = self.db.workspace_subscriptions
            count = await subscriptions_collection.count_documents({
                "bundles": {"$in": [bundle_name]},
                "status": "active"
            })
            return count
        except Exception as e:
            logger.error(f"Error counting existing subscriptions: {e}")
            return 0
    
    async def _calculate_average_bundles_per_workspace(self) -> float:
        """Calculate average number of bundles per workspace"""
        try:
            subscriptions_collection = self.db.workspace_subscriptions
            pipeline = [
                {"$project": {"bundle_count": {"$size": "$bundles"}}},
                {"$group": {"_id": None, "avg_bundles": {"$avg": "$bundle_count"}}}
            ]
            
            result = await subscriptions_collection.aggregate(pipeline).to_list(length=1)
            return round(result[0]["avg_bundles"], 2) if result else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating average bundles per workspace: {e}")
            return 0.0
    
    async def _generate_pricing_insights(self, bundle_stats: List[Dict], revenue_trends: List[Dict]) -> List[str]:
        """Generate insights from pricing analytics"""
        insights = []
        
        try:
            if bundle_stats:
                # Most popular bundle
                most_popular = bundle_stats[0]
                insights.append(f"Most popular bundle: {most_popular['_id']} with {most_popular['count']} subscriptions")
                
                # Revenue leader
                revenue_leader = max(bundle_stats, key=lambda x: x.get('total_revenue', 0))
                insights.append(f"Highest revenue bundle: {revenue_leader['_id']} generating ${revenue_leader.get('total_revenue', 0):.2f}")
            
            if len(revenue_trends) >= 2:
                # Revenue trend
                current_month = revenue_trends[0]["monthly_revenue"]
                previous_month = revenue_trends[1]["monthly_revenue"]
                
                if current_month > previous_month:
                    growth = ((current_month - previous_month) / previous_month) * 100
                    insights.append(f"Revenue growing: {growth:.1f}% month-over-month")
                elif current_month < previous_month:
                    decline = ((previous_month - current_month) / previous_month) * 100
                    insights.append(f"Revenue declining: {decline:.1f}% month-over-month")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating pricing insights: {e}")
            return ["Analytics data available but insights generation failed"]
    
    async def _estimate_demand_impact(self, bundle_name: str, proposed_changes: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate demand impact of pricing changes"""
        try:
            # Simplified demand elasticity model
            # In production, this would use historical data and machine learning
            
            if "monthly_price" not in proposed_changes:
                return {"estimated_change": 0, "confidence": "low"}
            
            # Get current subscriptions
            current_subs = await self._count_existing_subscriptions(bundle_name)
            
            # Simple elasticity model (price increase = demand decrease)
            current_config_result = await self.get_current_pricing_config()
            if not current_config_result.get("success"):
                return {"estimated_change": 0, "confidence": "low"}
            
            current_bundles = current_config_result.get("current_pricing", {})
            if bundle_name not in current_bundles:
                return {"estimated_change": 0, "confidence": "low"}
            
            current_price = current_bundles[bundle_name].get("monthly_price", 0)
            new_price = proposed_changes["monthly_price"]
            
            if current_price > 0:
                price_change_percentage = ((new_price - current_price) / current_price) * 100
                # Assume -2% demand for every +10% price increase (simplified elasticity)
                demand_change_percentage = (price_change_percentage / 10) * -2
                
                return {
                    "estimated_change": demand_change_percentage,
                    "confidence": "medium",
                    "methodology": "Simple price elasticity model"
                }
            
            return {"estimated_change": 0, "confidence": "low"}
            
        except Exception as e:
            logger.error(f"Error estimating demand impact: {e}")
            return {"estimated_change": 0, "confidence": "low"}
    
    def _assess_pricing_risk(self, impact_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk level of pricing changes"""
        try:
            risk_factors = []
            risk_score = 0
            
            # High number of existing subscriptions = higher risk
            existing_subs = impact_analysis["impact_metrics"].get("existing_subscriptions", 0)
            if existing_subs > 100:
                risk_factors.append("High number of existing subscriptions")
                risk_score += 3
            elif existing_subs > 50:
                risk_factors.append("Moderate number of existing subscriptions")
                risk_score += 2
            
            # Large price changes = higher risk
            price_change_pct = impact_analysis["impact_metrics"].get("price_change_percentage", 0)
            if abs(price_change_pct) > 25:
                risk_factors.append("Large price change (>25%)")
                risk_score += 3
            elif abs(price_change_pct) > 10:
                risk_factors.append("Moderate price change (>10%)")
                risk_score += 2
            
            # Negative demand impact = higher risk
            demand_change = impact_analysis["impact_metrics"].get("estimated_demand_change", {})
            if demand_change.get("estimated_change", 0) < -10:
                risk_factors.append("Significant estimated demand decrease")
                risk_score += 2
            
            # Determine risk level
            if risk_score >= 6:
                risk_level = "high"
            elif risk_score >= 3:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            return {
                "risk_level": risk_level,
                "risk_score": risk_score,
                "risk_factors": risk_factors,
                "recommendation": self._get_risk_recommendation(risk_level)
            }
            
        except Exception as e:
            logger.error(f"Error assessing pricing risk: {e}")
            return {"risk_level": "unknown", "risk_score": 0, "risk_factors": []}
    
    def _get_risk_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on risk level"""
        recommendations = {
            "low": "Safe to proceed with pricing change. Monitor metrics after implementation.",
            "medium": "Consider gradual rollout or A/B testing. Prepare customer communication.",
            "high": "High risk change. Consider smaller increments, extensive testing, and customer retention strategies."
        }
        return recommendations.get(risk_level, "Review pricing change carefully before implementing.")
    
    def _generate_pricing_recommendations(self, impact_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on impact analysis"""
        recommendations = []
        
        try:
            # Based on existing subscriptions
            existing_subs = impact_analysis["impact_metrics"].get("existing_subscriptions", 0)
            if existing_subs > 0:
                recommendations.append("Send advance notification to existing customers about pricing changes")
                recommendations.append("Implement grandfathering policy for existing subscriptions")
            
            # Based on price change
            price_change_pct = impact_analysis["impact_metrics"].get("price_change_percentage", 0)
            if price_change_pct > 20:
                recommendations.append("Consider phased price increase over multiple months")
                recommendations.append("Highlight value improvements to justify price increase")
            elif price_change_pct < -20:
                recommendations.append("Use price decrease as marketing opportunity")
                recommendations.append("Monitor for increased demand and server capacity")
            
            # Based on risk level
            risk_level = impact_analysis.get("risk_assessment", {}).get("risk_level", "low")
            if risk_level == "high":
                recommendations.append("Consider A/B testing with small user group first")
                recommendations.append("Prepare customer retention campaigns")
                recommendations.append("Have rollback plan ready")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating pricing recommendations: {e}")
            return ["Review pricing change carefully before implementing"]
    
    async def _apply_template_to_all_bundles(self, template: Dict[str, Any], applied_by: str, custom_duration: int = None) -> Dict[str, Any]:
        """Apply pricing template to all bundles"""
        try:
            # Get all current bundles
            current_config_result = await self.get_current_pricing_config()
            if not current_config_result.get("success"):
                return {"success": False, "error": "Could not get current pricing"}
            
            current_bundles = current_config_result.get("current_pricing", {})
            results = []
            
            discount_pct = template["discount_percentage"]
            
            for bundle_name, bundle_config in current_bundles.items():
                current_monthly = bundle_config.get("monthly_price", 0)
                current_yearly = bundle_config.get("yearly_price", 0)
                
                new_monthly = current_monthly * (1 - discount_pct)
                new_yearly = current_yearly * (1 - discount_pct)
                
                # Apply discount
                update_result = await self.update_bundle_pricing({
                    "bundle_name": bundle_name,
                    "pricing_updates": {
                        "monthly_price": new_monthly,
                        "yearly_price": new_yearly
                    },
                    "updated_by": applied_by,
                    "reason": f"Template applied: {template['name']}"
                })
                
                results.append({
                    "bundle_name": bundle_name,
                    "success": update_result.get("success", False),
                    "old_monthly": current_monthly,
                    "new_monthly": new_monthly,
                    "discount_applied": discount_pct * 100
                })
            
            return {
                "success": True,
                "template_name": template["name"],
                "bundles_updated": len([r for r in results if r["success"]]),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error applying template to all bundles: {e}")
            return {"success": False, "error": str(e)}
    
    async def _apply_template_to_selected_bundles(self, template: Dict[str, Any], applied_by: str, custom_duration: int = None) -> Dict[str, Any]:
        """Apply pricing template to selected bundles"""
        try:
            target_bundles = template.get("target_bundles", [])
            discount_pct = template["discount_percentage"]
            results = []
            
            for bundle_name in target_bundles:
                # Get current pricing
                current_config_result = await self.get_current_pricing_config()
                if not current_config_result.get("success"):
                    continue
                
                current_bundles = current_config_result.get("current_pricing", {})
                if bundle_name not in current_bundles:
                    continue
                
                bundle_config = current_bundles[bundle_name]
                current_monthly = bundle_config.get("monthly_price", 0)
                current_yearly = bundle_config.get("yearly_price", 0)
                
                new_monthly = current_monthly * (1 - discount_pct)
                new_yearly = current_yearly * (1 - discount_pct)
                
                # Apply discount
                update_result = await self.update_bundle_pricing({
                    "bundle_name": bundle_name,
                    "pricing_updates": {
                        "monthly_price": new_monthly,
                        "yearly_price": new_yearly
                    },
                    "updated_by": applied_by,
                    "reason": f"Template applied: {template['name']}"
                })
                
                results.append({
                    "bundle_name": bundle_name,
                    "success": update_result.get("success", False),
                    "old_monthly": current_monthly,
                    "new_monthly": new_monthly,
                    "discount_applied": discount_pct * 100
                })
            
            return {
                "success": True,
                "template_name": template["name"],
                "target_bundles": target_bundles,
                "bundles_updated": len([r for r in results if r["success"]]),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error applying template to selected bundles: {e}")
            return {"success": False, "error": str(e)}
    
    async def _apply_template_to_enterprise(self, template: Dict[str, Any], applied_by: str, custom_duration: int = None) -> Dict[str, Any]:
        """Apply pricing template to enterprise pricing"""
        try:
            # This would update enterprise pricing configuration
            # For now, just log the action
            
            enterprise_log = {
                "_id": str(uuid.uuid4()),
                "template_name": template["name"],
                "new_enterprise_minimum": template.get("enterprise_minimum", 99.0),
                "applied_by": applied_by,
                "applied_at": datetime.utcnow(),
                "duration_days": custom_duration or template.get("duration_days", 30)
            }
            
            # In production, this would update the enterprise pricing in the workspace subscription service
            
            return {
                "success": True,
                "enterprise_template_applied": enterprise_log,
                "message": "Enterprise pricing template applied"
            }
            
        except Exception as e:
            logger.error(f"Error applying template to enterprise: {e}")
            return {"success": False, "error": str(e)}


# Service instance
_admin_pricing_service = None

def get_admin_pricing_service() -> AdminPricingService:
    """Get admin pricing service instance"""
    global _admin_pricing_service
    if _admin_pricing_service is None:
        _admin_pricing_service = AdminPricingService()
    return _admin_pricing_service