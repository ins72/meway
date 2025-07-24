"""
Workspace Subscription Service
Handles workspace-specific subscriptions, billing, and feature access control
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from core.database import get_database
import uuid

logger = logging.getLogger(__name__)

class WorkspaceSubscriptionService:
    def __init__(self):
        self.db = get_database()
        
        # Bundle definitions with features and pricing
        self.bundle_definitions = {
            "creator": {
                "name": "Creator Bundle",
                "monthly_price": 19,
                "yearly_price": 190,
                "features": [
                    "advanced_bio_links",
                    "website_builder",
                    "seo_optimization",
                    "ai_content_creation",
                    "template_marketplace_selling",
                    "custom_branding"
                ],
                "limits": {
                    "bio_links": -1,  # unlimited
                    "website_pages": 10,
                    "ai_credits": 500,
                    "custom_domains": 1
                }
            },
            "ecommerce": {
                "name": "E-commerce Bundle",
                "monthly_price": 24,
                "yearly_price": 240,
                "features": [
                    "ecommerce_store",
                    "multi_vendor_marketplace",
                    "promotions_referrals",
                    "payment_processing",
                    "inventory_management",
                    "basic_analytics"
                ],
                "limits": {
                    "products": -1,  # unlimited
                    "vendors": 10,
                    "transactions": -1
                }
            },
            "social_media": {
                "name": "Social Media Bundle",
                "monthly_price": 29,
                "yearly_price": 290,
                "features": [
                    "instagram_lead_database",
                    "social_scheduling",
                    "twitter_tiktok_tools",
                    "social_analytics",
                    "hashtag_research"
                ],
                "limits": {
                    "instagram_searches": 1000,
                    "scheduled_posts": -1,
                    "social_accounts": 10
                }
            },
            "education": {
                "name": "Education Bundle",
                "monthly_price": 29,
                "yearly_price": 290,
                "features": [
                    "course_platform",
                    "student_management",
                    "live_streaming",
                    "certificate_generation",
                    "community_features"
                ],
                "limits": {
                    "students": -1,  # unlimited
                    "courses": -1,
                    "streaming_hours": 100
                }
            },
            "business": {
                "name": "Business Bundle",
                "monthly_price": 39,
                "yearly_price": 390,
                "features": [
                    "advanced_crm",
                    "email_marketing",
                    "lead_management",
                    "workflow_automation",
                    "campaign_management",
                    "business_analytics"
                ],
                "limits": {
                    "contacts": -1,  # unlimited
                    "emails_per_month": 10000,
                    "workflows": 10,
                    "campaigns": -1
                }
            },
            "operations": {
                "name": "Operations Bundle",
                "monthly_price": 24,
                "yearly_price": 240,
                "features": [
                    "booking_appointments",
                    "financial_management",
                    "advanced_forms",
                    "survey_feedback",
                    "basic_reporting"
                ],
                "limits": {
                    "bookings": -1,  # unlimited
                    "forms": -1,
                    "surveys": -1,
                    "invoices": -1
                }
            }
        }
        
        # Multi-bundle discount rates
        self.bundle_discounts = {
            2: 0.20,  # 20% discount for 2 bundles
            3: 0.30,  # 30% discount for 3 bundles
            4: 0.40,  # 40% discount for 4+ bundles
            5: 0.40,
            6: 0.40
        }

    async def health_check(self):
        """Health check for workspace subscription service"""
        try:
            collection = self.db.workspace_subscriptions
            # Test database connection
            await collection.count_documents({})
            
            return {
                "success": True,
                "healthy": True,
                "service": "workspace_subscription",
                "timestamp": datetime.utcnow().isoformat(),
                "bundles_available": len(self.bundle_definitions)
            }
        except Exception as e:
            logger.error(f"Workspace subscription health check failed: {e}")
            return {
                "success": False,
                "healthy": False,
                "error": str(e)
            }

    async def check_billing_permission(self, workspace_id: str, user_id: str) -> bool:
        """Check if user has permission to manage billing for workspace"""
        try:
            # Check if user is owner or admin of workspace
            workspace_collection = self.db.workspace  # Fixed collection name
            workspace = await workspace_collection.find_one({
                "id": workspace_id,  # Fixed field name
                "$or": [
                    {"owner_id": user_id},
                    {"user_id": user_id},  # Also check user_id field
                    {"admins": {"$in": [user_id]}}
                ]
            })
            
            return workspace is not None
            
        except Exception as e:
            logger.error(f"Error checking billing permission: {e}")
            return False

    async def create_workspace_subscription(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workspace subscription"""
        try:
            workspace_id = data.get("workspace_id")
            bundles = data.get("bundles", [])
            billing_cycle = data.get("billing_cycle", "monthly")
            created_by = data.get("created_by")
            
            if not workspace_id or not bundles:
                return {"success": False, "error": "Workspace ID and bundles are required"}
            
            # Validate bundles
            for bundle in bundles:
                if bundle not in self.bundle_definitions:
                    return {"success": False, "error": f"Invalid bundle: {bundle}"}
            
            # Calculate pricing
            pricing_result = await self.calculate_pricing(bundles, billing_cycle)
            if not pricing_result.get("success"):
                return pricing_result
            
            # Create subscription record
            subscription_id = str(uuid.uuid4())
            subscription = {
                "_id": subscription_id,
                "workspace_id": workspace_id,
                "bundles": bundles,
                "billing_cycle": billing_cycle,
                "status": "active",
                "created_by": created_by,
                "created_at": datetime.utcnow(),
                "current_period_start": datetime.utcnow(),
                "current_period_end": datetime.utcnow() + timedelta(days=30 if billing_cycle == "monthly" else 365),
                "pricing": pricing_result["pricing"],
                "next_billing_date": datetime.utcnow() + timedelta(days=30 if billing_cycle == "monthly" else 365),
                "auto_renew": True
            }
            
            collection = self.db.workspace_subscriptions
            await collection.insert_one(subscription)
            
            # Create initial billing record
            billing_record = {
                "_id": str(uuid.uuid4()),
                "workspace_id": workspace_id,
                "subscription_id": subscription_id,
                "amount": pricing_result["pricing"]["total_amount"],
                "billing_cycle": billing_cycle,
                "bundles": bundles,
                "status": "pending_payment",
                "created_at": datetime.utcnow(),
                "due_date": datetime.utcnow() + timedelta(days=7)  # 7 days to pay
            }
            
            billing_collection = self.db.workspace_billing_history
            await billing_collection.insert_one(billing_record)
            
            return {
                "success": True,
                "subscription": subscription,
                "billing_record": billing_record,
                "message": "Workspace subscription created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating workspace subscription: {e}")
            return {"success": False, "error": str(e)}

    async def get_workspace_subscription(self, workspace_id: str, user_id: str) -> Dict[str, Any]:
        """Get workspace subscription details"""
        try:
            # Check permission
            has_permission = await self.check_billing_permission(workspace_id, user_id)
            if not has_permission:
                return {"success": False, "error": "Insufficient permissions"}
            
            collection = self.db.workspace_subscriptions
            subscription = await collection.find_one({"workspace_id": workspace_id})
            
            if not subscription:
                return {"success": False, "error": "No subscription found for workspace"}
            
            # Get current usage
            usage = await self.get_current_usage(workspace_id)
            
            return {
                "success": True,
                "subscription": subscription,
                "usage": usage,
                "available_bundles": self.bundle_definitions
            }
            
        except Exception as e:
            logger.error(f"Error getting workspace subscription: {e}")
            return {"success": False, "error": str(e)}

    async def modify_workspace_bundles(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add or remove bundles from workspace subscription"""
        try:
            workspace_id = data.get("workspace_id")
            action = data.get("action")  # "add" or "remove"
            bundles = data.get("bundles", [])
            modified_by = data.get("modified_by")
            
            if not workspace_id or not action or not bundles:
                return {"success": False, "error": "Workspace ID, action, and bundles are required"}
            
            collection = self.db.workspace_subscriptions
            subscription = await collection.find_one({"workspace_id": workspace_id})
            
            if not subscription:
                return {"success": False, "error": "No subscription found for workspace"}
            
            current_bundles = subscription["bundles"]
            
            if action == "add":
                # Add new bundles
                for bundle in bundles:
                    if bundle not in self.bundle_definitions:
                        return {"success": False, "error": f"Invalid bundle: {bundle}"}
                    if bundle not in current_bundles:
                        current_bundles.append(bundle)
            elif action == "remove":
                # Remove bundles
                for bundle in bundles:
                    if bundle in current_bundles:
                        current_bundles.remove(bundle)
            else:
                return {"success": False, "error": "Action must be 'add' or 'remove'"}
            
            # Recalculate pricing
            billing_cycle = subscription["billing_cycle"]
            pricing_result = await self.calculate_pricing(current_bundles, billing_cycle)
            
            if not pricing_result.get("success"):
                return pricing_result
            
            # Update subscription
            update_data = {
                "bundles": current_bundles,
                "pricing": pricing_result["pricing"],
                "modified_by": modified_by,
                "modified_at": datetime.utcnow()
            }
            
            await collection.update_one(
                {"workspace_id": workspace_id},
                {"$set": update_data}
            )
            
            # Create billing adjustment record
            adjustment_amount = pricing_result["pricing"]["total_amount"] - subscription["pricing"]["total_amount"]
            
            billing_record = {
                "_id": str(uuid.uuid4()),
                "workspace_id": workspace_id,
                "subscription_id": subscription["_id"],
                "type": "bundle_modification",
                "amount": adjustment_amount,
                "bundles_added": bundles if action == "add" else [],
                "bundles_removed": bundles if action == "remove" else [],
                "status": "processed",
                "created_at": datetime.utcnow(),
                "created_by": modified_by
            }
            
            billing_collection = self.db.workspace_billing_history
            await billing_collection.insert_one(billing_record)
            
            return {
                "success": True,
                "updated_subscription": await collection.find_one({"workspace_id": workspace_id}),
                "billing_adjustment": billing_record,
                "message": f"Successfully {action}ed bundles"
            }
            
        except Exception as e:
            logger.error(f"Error modifying workspace bundles: {e}")
            return {"success": False, "error": str(e)}

    async def get_workspace_usage_limits(self, workspace_id: str, user_id: str) -> Dict[str, Any]:
        """Get workspace usage limits and current usage"""
        try:
            # Check permission
            has_permission = await self.check_billing_permission(workspace_id, user_id)
            if not has_permission:
                return {"success": False, "error": "Insufficient permissions"}
            
            collection = self.db.workspace_subscriptions
            subscription = await collection.find_one({"workspace_id": workspace_id})
            
            if not subscription:
                return {"success": False, "error": "No subscription found for workspace"}
            
            # Calculate combined limits from all bundles
            combined_limits = {}
            combined_features = []
            
            for bundle_name in subscription["bundles"]:
                bundle = self.bundle_definitions[bundle_name]
                combined_features.extend(bundle["features"])
                
                for limit_key, limit_value in bundle["limits"].items():
                    if limit_key not in combined_limits:
                        combined_limits[limit_key] = limit_value
                    elif limit_value == -1:  # unlimited
                        combined_limits[limit_key] = -1
                    elif combined_limits[limit_key] != -1:
                        combined_limits[limit_key] = max(combined_limits[limit_key], limit_value)
            
            # Get current usage
            current_usage = await self.get_current_usage(workspace_id)
            
            # Calculate usage percentages
            usage_percentages = {}
            for limit_key, limit_value in combined_limits.items():
                if limit_value == -1:
                    usage_percentages[limit_key] = 0  # unlimited
                else:
                    current = current_usage.get(limit_key, 0)
                    usage_percentages[limit_key] = (current / limit_value) * 100 if limit_value > 0 else 0
            
            return {
                "success": True,
                "workspace_id": workspace_id,
                "active_bundles": subscription["bundles"],
                "available_features": list(set(combined_features)),
                "limits": combined_limits,
                "current_usage": current_usage,
                "usage_percentages": usage_percentages,
                "subscription_status": subscription["status"]
            }
            
        except Exception as e:
            logger.error(f"Error getting workspace usage limits: {e}")
            return {"success": False, "error": str(e)}

    async def get_current_usage(self, workspace_id: str) -> Dict[str, int]:
        """Get current usage statistics for workspace"""
        try:
            # This would typically query various collections to get current usage
            # For now, returning mock data structure that would be populated by real queries
            
            usage = {
                "bio_links": 0,
                "website_pages": 0,
                "ai_credits": 0,
                "custom_domains": 0,
                "products": 0,
                "vendors": 0,
                "transactions": 0,
                "instagram_searches": 0,
                "scheduled_posts": 0,
                "social_accounts": 0,
                "students": 0,
                "courses": 0,
                "streaming_hours": 0,
                "contacts": 0,
                "emails_sent": 0,
                "workflows": 0,
                "campaigns": 0,
                "bookings": 0,
                "forms": 0,
                "surveys": 0,
                "invoices": 0
            }
            
            # TODO: Implement actual usage queries
            # Example:
            # bio_links_count = await self.db.bio_links.count_documents({"workspace_id": workspace_id})
            # usage["bio_links"] = bio_links_count
            
            return usage
            
        except Exception as e:
            logger.error(f"Error getting current usage: {e}")
            return {}

    async def upgrade_workspace_subscription(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Upgrade workspace subscription"""
        try:
            workspace_id = data.get("workspace_id")
            new_bundles = data.get("bundles", [])
            upgraded_by = data.get("upgraded_by")
            
            return await self.modify_workspace_bundles({
                "workspace_id": workspace_id,
                "action": "add",
                "bundles": new_bundles,
                "modified_by": upgraded_by
            })
            
        except Exception as e:
            logger.error(f"Error upgrading workspace subscription: {e}")
            return {"success": False, "error": str(e)}

    async def downgrade_workspace_subscription(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Downgrade workspace subscription"""
        try:
            workspace_id = data.get("workspace_id")
            remove_bundles = data.get("bundles", [])
            downgraded_by = data.get("downgraded_by")
            
            return await self.modify_workspace_bundles({
                "workspace_id": workspace_id,
                "action": "remove",
                "bundles": remove_bundles,
                "modified_by": downgraded_by
            })
            
        except Exception as e:
            logger.error(f"Error downgrading workspace subscription: {e}")
            return {"success": False, "error": str(e)}

    async def cancel_workspace_subscription(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel workspace subscription"""
        try:
            workspace_id = data.get("workspace_id")
            cancelled_by = data.get("cancelled_by")
            cancellation_reason = data.get("reason", "")
            
            collection = self.db.workspace_subscriptions
            subscription = await collection.find_one({"workspace_id": workspace_id})
            
            if not subscription:
                return {"success": False, "error": "No subscription found for workspace"}
            
            # Update subscription status
            await collection.update_one(
                {"workspace_id": workspace_id},
                {
                    "$set": {
                        "status": "cancelled",
                        "cancelled_at": datetime.utcnow(),
                        "cancelled_by": cancelled_by,
                        "cancellation_reason": cancellation_reason,
                        "auto_renew": False
                    }
                }
            )
            
            # Create cancellation record
            cancellation_record = {
                "_id": str(uuid.uuid4()),
                "workspace_id": workspace_id,
                "subscription_id": subscription["_id"],
                "type": "cancellation",
                "reason": cancellation_reason,
                "cancelled_by": cancelled_by,
                "cancelled_at": datetime.utcnow(),
                "refund_amount": 0,  # Implement refund logic if needed
                "status": "processed"
            }
            
            billing_collection = self.db.workspace_billing_history
            await billing_collection.insert_one(cancellation_record)
            
            return {
                "success": True,
                "cancelled_subscription": await collection.find_one({"workspace_id": workspace_id}),
                "cancellation_record": cancellation_record,
                "message": "Subscription cancelled successfully"
            }
            
        except Exception as e:
            logger.error(f"Error cancelling workspace subscription: {e}")
            return {"success": False, "error": str(e)}

    async def get_workspace_billing_history(self, workspace_id: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get workspace billing history"""
        try:
            collection = self.db.workspace_billing_history
            
            # Get total count
            total_count = await collection.count_documents({"workspace_id": workspace_id})
            
            # Get paginated results
            cursor = collection.find({"workspace_id": workspace_id}).sort("created_at", -1).skip(offset).limit(limit)
            billing_history = await cursor.to_list(length=limit)
            
            return {
                "success": True,
                "workspace_id": workspace_id,
                "billing_history": billing_history,
                "pagination": {
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_count
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting workspace billing history: {e}")
            return {"success": False, "error": str(e)}

    async def check_feature_access(self, workspace_id: str, feature: str, user_id: str) -> Dict[str, Any]:
        """Check if workspace has access to specific feature"""
        try:
            collection = self.db.workspace_subscriptions
            subscription = await collection.find_one({"workspace_id": workspace_id})
            
            if not subscription:
                # No subscription = free tier only
                free_features = ["basic_bio_links", "basic_forms", "basic_analytics"]
                has_access = feature in free_features
                
                return {
                    "success": True,
                    "workspace_id": workspace_id,
                    "feature": feature,
                    "has_access": has_access,
                    "subscription_tier": "free",
                    "reason": "Free tier access" if has_access else "Feature requires paid subscription"
                }
            
            # Check if feature is available in any of the workspace's bundles
            available_features = []
            for bundle_name in subscription["bundles"]:
                if bundle_name in self.bundle_definitions:
                    available_features.extend(self.bundle_definitions[bundle_name]["features"])
            
            has_access = feature in available_features
            
            return {
                "success": True,
                "workspace_id": workspace_id,
                "feature": feature,
                "has_access": has_access,
                "subscription_tier": "paid",
                "active_bundles": subscription["bundles"],
                "available_features": list(set(available_features)),
                "reason": "Feature included in subscription" if has_access else "Feature not included in current bundles"
            }
            
        except Exception as e:
            logger.error(f"Error checking feature access: {e}")
            return {"success": False, "error": str(e)}

    async def calculate_pricing(self, bundles: List[str], billing_cycle: str = "monthly") -> Dict[str, Any]:
        """Calculate pricing for bundle combination"""
        try:
            if not bundles:
                return {"success": False, "error": "At least one bundle is required"}
            
            # Validate bundles
            for bundle in bundles:
                if bundle not in self.bundle_definitions:
                    return {"success": False, "error": f"Invalid bundle: {bundle}"}
            
            # Calculate base pricing
            base_total = 0
            bundle_breakdown = []
            
            price_key = "monthly_price" if billing_cycle == "monthly" else "yearly_price"
            
            for bundle_name in bundles:
                bundle = self.bundle_definitions[bundle_name]
                price = bundle[price_key]
                base_total += price
                
                bundle_breakdown.append({
                    "bundle": bundle_name,
                    "name": bundle["name"],
                    "base_price": price,
                    "features_included": len(bundle["features"])
                })
            
            # Apply multi-bundle discount
            discount_rate = 0
            if len(bundles) >= 2:
                discount_rate = self.bundle_discounts.get(len(bundles), self.bundle_discounts[4])  # Max discount for 4+
            
            discount_amount = base_total * discount_rate
            final_total = base_total - discount_amount
            
            # Calculate savings vs buying individual tools
            estimated_competitor_cost = base_total * 2.5  # Conservative estimate
            savings_amount = estimated_competitor_cost - final_total
            savings_percentage = (savings_amount / estimated_competitor_cost) * 100
            
            pricing = {
                "bundles": bundles,
                "billing_cycle": billing_cycle,
                "bundle_breakdown": bundle_breakdown,
                "base_total": base_total,
                "discount_rate": discount_rate,
                "discount_amount": discount_amount,
                "total_amount": final_total,
                "estimated_competitor_cost": estimated_competitor_cost,
                "savings_amount": savings_amount,
                "savings_percentage": round(savings_percentage, 1),
                "currency": "USD",
                "calculated_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "pricing": pricing,
                "message": f"Pricing calculated for {len(bundles)} bundles with {discount_rate*100}% discount"
            }
            
        except Exception as e:
            logger.error(f"Error calculating pricing: {e}")
            return {"success": False, "error": str(e)}

    async def get_available_bundles(self) -> Dict[str, Any]:
        """Get all available bundles and their features"""
        try:
            return {
                "success": True,
                "bundles": self.bundle_definitions,
                "total_bundles": len(self.bundle_definitions),
                "discount_tiers": self.bundle_discounts,
                "message": "Available bundles retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"Error getting available bundles: {e}")
            return {"success": False, "error": str(e)}


# Service instance
_workspace_subscription_service = None

def get_workspace_subscription_service() -> WorkspaceSubscriptionService:
    """Get workspace subscription service instance"""
    global _workspace_subscription_service
    if _workspace_subscription_service is None:
        _workspace_subscription_service = WorkspaceSubscriptionService()
    return _workspace_subscription_service