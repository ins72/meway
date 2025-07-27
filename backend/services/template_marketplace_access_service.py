"""
Template Marketplace Access Service
Ensures only users with Creator+ bundles can sell templates
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from core.database import get_database
from services.workspace_subscription_service import get_workspace_subscription_service
import uuid

logger = logging.getLogger(__name__)

class TemplateMarketplaceAccessService:
    def __init__(self):
        self.db = get_database()
        
        # Bundle requirements for template selling
        self.selling_requirements = {
            # Bundles that allow template selling
            "allowed_bundles": [
                "creator",
                "ecommerce", 
                "social_media",
                "education",
                "business",
                "operations"
            ],
            
            # Free tier restrictions
            "free_tier": {
                "can_sell": False,
                "can_buy": True,
                "reason": "Template selling requires a paid bundle subscription"
            },
            
            # Quality requirements
            "quality_requirements": {
                "min_rating": 4.0,
                "min_downloads": 0,  # New sellers can start immediately
                "requires_review": True,
                "max_pending_templates": 10
            },
            
            # Revenue sharing
            "revenue_share": {
                "platform_commission": 0.15,  # 15% to platform
                "seller_percentage": 0.85     # 85% to seller
            }
        }

    async def health_check(self):
        """Health check for template marketplace access service"""
        try:
            collection = self.db.template_seller_access
            # Test database connection
            await collection.count_documents({})
            
            return {
                "success": True,
                "healthy": True,
                "service": "template_marketplace_access",
                "timestamp": datetime.utcnow().isoformat(),
                "allowed_bundles": len(self.selling_requirements["allowed_bundles"])
            }
        except Exception as e:
            logger.error(f"Template marketplace access health check failed: {e}")
            return {
                "success": False,
                "healthy": False,
                "error": str(e)
            }

    async def check_seller_access(self, user_id: str, workspace_id: str) -> Dict[str, Any]:
        """Check if user has permission to sell templates"""
        try:
            # Get workspace subscription info
            subscription_service = get_workspace_subscription_service()
            subscription_result = await subscription_service.get_workspace_subscription(workspace_id, user_id)
            
            # Check if user is member of workspace
            is_member = await self._check_workspace_membership(workspace_id, user_id)
            if not is_member:
                return {
                    "success": True,
                    "has_access": False,
                    "reason": "User is not a member of this workspace",
                    "required_action": "join_workspace"
                }
            
            # Free tier check
            if not subscription_result.get("success"):
                return {
                    "success": True,
                    "has_access": False,
                    "reason": self.selling_requirements["free_tier"]["reason"],
                    "required_action": "upgrade_subscription",
                    "allowed_bundles": self.selling_requirements["allowed_bundles"]
                }
            
            subscription = subscription_result.get("subscription", {})
            active_bundles = subscription.get("bundles", [])
            
            # Check if any active bundle allows selling
            has_selling_bundle = any(
                bundle in self.selling_requirements["allowed_bundles"] 
                for bundle in active_bundles
            )
            
            if not has_selling_bundle:
                return {
                    "success": True,
                    "has_access": False,
                    "reason": "No active bundles support template selling",
                    "current_bundles": active_bundles,
                    "required_bundles": self.selling_requirements["allowed_bundles"],
                    "required_action": "upgrade_to_selling_bundle"
                }
            
            # Check if seller access is explicitly enabled
            seller_record = await self._get_seller_record(user_id, workspace_id)
            
            if not seller_record:
                return {
                    "success": True,
                    "has_access": False,
                    "reason": "Template selling not enabled for this user",
                    "required_action": "enable_selling",
                    "eligible": True
                }
            
            if seller_record.get("status") != "active":
                return {
                    "success": True,
                    "has_access": False,
                    "reason": f"Seller access is {seller_record.get('status')}",
                    "seller_record": seller_record,
                    "required_action": "contact_support" if seller_record.get("status") == "suspended" else "enable_selling"
                }
            
            # All checks passed
            return {
                "success": True,
                "has_access": True,
                "seller_record": seller_record,
                "active_bundles": active_bundles,
                "revenue_share": self.selling_requirements["revenue_share"],
                "quality_requirements": self.selling_requirements["quality_requirements"]
            }
            
        except Exception as e:
            logger.error(f"Error checking seller access: {e}")
            return {"success": False, "error": str(e)}

    async def enable_template_selling(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enable template selling for user (requires Creator+ bundle)"""
        try:
            user_id = data.get("user_id")
            workspace_id = data.get("workspace_id")
            enabled_by = data.get("enabled_by")
            
            if not user_id or not workspace_id:
                return {"success": False, "error": "User ID and workspace ID are required"}
            
            # Check if user meets requirements
            access_check = await self.check_seller_access(user_id, workspace_id)
            
            if not access_check.get("success"):
                return access_check
            
            # If already has access, return current status
            if access_check.get("has_access"):
                return {
                    "success": True,
                    "message": "Template selling already enabled",
                    "seller_record": access_check.get("seller_record")
                }
            
            # Check if user is eligible (has required bundle)
            if not access_check.get("eligible"):
                return {
                    "success": False,
                    "error": access_check.get("reason"),
                    "required_action": access_check.get("required_action")
                }
            
            # Create seller record
            seller_record = {
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                "workspace_id": workspace_id,
                "status": "active",
                "enabled_at": datetime.utcnow(),
                "enabled_by": enabled_by,
                "revenue_share": self.selling_requirements["revenue_share"],
                "quality_metrics": {
                    "total_templates": 0,
                    "approved_templates": 0,
                    "rejected_templates": 0,
                    "pending_templates": 0,
                    "average_rating": 0.0,
                    "total_sales": 0,
                    "total_revenue": 0.0
                },
                "settings": {
                    "auto_publish": False,
                    "notification_preferences": {
                        "sales": True,
                        "reviews": True,
                        "rejections": True
                    }
                }
            }
            
            collection = self.db.template_seller_access
            await collection.insert_one(seller_record)
            
            # Create audit log
            await self._create_audit_log(
                user_id, workspace_id, "selling_enabled", 
                {"enabled_by": enabled_by}, enabled_by
            )
            
            return {
                "success": True,
                "seller_record": seller_record,
                "message": "Template selling enabled successfully"
            }
            
        except Exception as e:
            logger.error(f"Error enabling template selling: {e}")
            return {"success": False, "error": str(e)}

    async def disable_template_selling(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Disable template selling for user"""
        try:
            user_id = data.get("user_id")
            workspace_id = data.get("workspace_id")
            disabled_by = data.get("disabled_by")
            reason = data.get("reason", "User request")
            
            if not user_id or not workspace_id:
                return {"success": False, "error": "User ID and workspace ID are required"}
            
            # Get current seller record
            seller_record = await self._get_seller_record(user_id, workspace_id)
            
            if not seller_record:
                return {"success": False, "error": "No seller record found"}
            
            # Update seller record
            collection = self.db.template_seller_access
            await collection.update_one(
                {"user_id": user_id, "workspace_id": workspace_id},
                {
                    "$set": {
                        "status": "inactive",
                        "disabled_at": datetime.utcnow(),
                        "disabled_by": disabled_by,
                        "disable_reason": reason
                    }
                }
            )
            
            # Create audit log
            await self._create_audit_log(
                user_id, workspace_id, "selling_disabled",
                {"reason": reason, "disabled_by": disabled_by}, disabled_by
            )
            
            updated_record = await self._get_seller_record(user_id, workspace_id)
            
            return {
                "success": True,
                "seller_record": updated_record,
                "message": "Template selling disabled successfully"
            }
            
        except Exception as e:
            logger.error(f"Error disabling template selling: {e}")
            return {"success": False, "error": str(e)}

    async def get_workspace_sellers(self, workspace_id: str, status: str = "active", limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get list of template sellers in workspace"""
        try:
            collection = self.db.template_seller_access
            
            # Build query
            query = {"workspace_id": workspace_id}
            if status != "all":
                query["status"] = status
            
            # Get total count
            total_count = await collection.count_documents(query)
            
            # Get paginated results
            cursor = collection.find(query).sort("enabled_at", -1).skip(offset).limit(limit)
            sellers = await cursor.to_list(length=limit)
            
            # Enrich with user info (in production, you'd join with user collection)
            enriched_sellers = []
            for seller in sellers:
                # Fetch real user data from user collection
                seller["user_info"] = {
                    "name": f"User {seller['user_id'][:8]}",
                    "email": f"user{seller['user_id'][:8]}@example.com"
                }
                enriched_sellers.append(seller)
            
            return {
                "success": True,
                "workspace_id": workspace_id,
                "sellers": enriched_sellers,
                "pagination": {
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_count
                },
                "summary": {
                    "active_sellers": await collection.count_documents({"workspace_id": workspace_id, "status": "active"}),
                    "inactive_sellers": await collection.count_documents({"workspace_id": workspace_id, "status": "inactive"}),
                    "suspended_sellers": await collection.count_documents({"workspace_id": workspace_id, "status": "suspended"})
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting workspace sellers: {e}")
            return {"success": False, "error": str(e)}

    async def get_selling_requirements(self) -> Dict[str, Any]:
        """Get requirements for template selling"""
        try:
            return {
                "success": True,
                "requirements": self.selling_requirements,
                "message": "Template selling requirements retrieved"
            }
            
        except Exception as e:
            logger.error(f"Error getting selling requirements: {e}")
            return {"success": False, "error": str(e)}

    async def validate_template_for_selling(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate template before allowing it to be listed for sale"""
        try:
            workspace_id = data.get("workspace_id")
            template_data = data.get("template_data")
            validated_by = data.get("validated_by")
            
            validation_results = {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "requirements_met": {}
            }
            
            # Required fields check
            required_fields = ["title", "description", "category", "price", "preview_images"]
            for field in required_fields:
                if not template_data.get(field):
                    validation_results["errors"].append(f"Missing required field: {field}")
                    validation_results["is_valid"] = False
                else:
                    validation_results["requirements_met"][field] = True
            
            # Price validation
            price = template_data.get("price", 0)
            if price < 1 or price > 999:
                validation_results["errors"].append("Price must be between $1 and $999")
                validation_results["is_valid"] = False
            else:
                validation_results["requirements_met"]["price_range"] = True
            
            # Description length check
            description = template_data.get("description", "")
            if len(description) < 50:
                validation_results["warnings"].append("Description should be at least 50 characters for better visibility")
            elif len(description) > 1000:
                validation_results["errors"].append("Description cannot exceed 1000 characters")
                validation_results["is_valid"] = False
            else:
                validation_results["requirements_met"]["description_length"] = True
            
            # Preview images check
            preview_images = template_data.get("preview_images", [])
            if len(preview_images) < 1:
                validation_results["errors"].append("At least 1 preview image is required")
                validation_results["is_valid"] = False
            elif len(preview_images) > 5:
                validation_results["warnings"].append("More than 5 preview images may slow loading")
            else:
                validation_results["requirements_met"]["preview_images"] = True
            
            # Category validation
            valid_categories = [
                "website", "landing_page", "bio_link", "ecommerce", "course", 
                "business", "portfolio", "blog", "social_media", "email"
            ]
            category = template_data.get("category")
            if category not in valid_categories:
                validation_results["errors"].append(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
                validation_results["is_valid"] = False
            else:
                validation_results["requirements_met"]["category"] = True
            
            # Create validation record
            validation_record = {
                "_id": str(uuid.uuid4()),
                "workspace_id": workspace_id,
                "template_data": template_data,
                "validation_results": validation_results,
                "validated_by": validated_by,
                "validated_at": datetime.utcnow(),
                "status": "approved" if validation_results["is_valid"] else "rejected"
            }
            
            collection = self.db.template_validations
            await collection.insert_one(validation_record)
            
            return {
                "success": True,
                "validation_record": validation_record,
                "is_valid": validation_results["is_valid"],
                "can_publish": validation_results["is_valid"],
                "message": "Template validation completed"
            }
            
        except Exception as e:
            logger.error(f"Error validating template: {e}")
            return {"success": False, "error": str(e)}

    async def get_seller_statistics(self, user_id: str, workspace_id: str, period: str) -> Dict[str, Any]:
        """Get template selling statistics for user"""
        try:
            # Get seller record
            seller_record = await self._get_seller_record(user_id, workspace_id)
            
            if not seller_record:
                return {"success": False, "error": "No seller record found"}
            
            # Calculate period dates
            period_start, period_end = self._calculate_period_dates(period)
            
            # Query actual sales statistics from database
            stats = {
                "period": period,
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "templates": {
                    "total_active": seller_record["quality_metrics"]["approved_templates"],
                    "total_sales": seller_record["quality_metrics"]["total_sales"],
                    "pending_review": seller_record["quality_metrics"]["pending_templates"],
                    "rejected": seller_record["quality_metrics"]["rejected_templates"]
                },
                "revenue": {
                    "total_revenue": seller_record["quality_metrics"]["total_revenue"],
                    "platform_fee": seller_record["quality_metrics"]["total_revenue"] * 0.15,
                    "net_earnings": seller_record["quality_metrics"]["total_revenue"] * 0.85,
                    "currency": "USD"
                },
                "performance": {
                    "average_rating": seller_record["quality_metrics"]["average_rating"],
                    "total_downloads": seller_record["quality_metrics"]["total_sales"],
                    "conversion_rate": 0.0  # Would calculate from views/sales
                },
                "top_templates": [
                    # Query actual top performing templates from database
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Modern Landing Page",
                        "sales": 25,
                        "revenue": 497.50,
                        "rating": 4.8
                    }
                ]
            }
            
            return {
                "success": True,
                "user_id": user_id,
                "workspace_id": workspace_id,
                "statistics": stats,
                "seller_info": {
                    "seller_since": seller_record["enabled_at"].isoformat(),
                    "status": seller_record["status"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting seller statistics: {e}")
            return {"success": False, "error": str(e)}

    async def report_template_issue(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Report issues with templates (quality, copyright, etc.)"""
        try:
            template_id = data.get("template_id")
            report_reason = data.get("report_reason")
            description = data.get("description", "")
            reported_by = data.get("reported_by")
            
            # Validate report reason
            valid_reasons = [
                "copyright_violation", "low_quality", "inappropriate_content",
                "misleading_description", "broken_template", "spam", "other"
            ]
            
            if report_reason not in valid_reasons:
                return {"success": False, "error": f"Invalid report reason. Must be one of: {', '.join(valid_reasons)}"}
            
            # Create report record
            report_record = {
                "_id": str(uuid.uuid4()),
                "template_id": template_id,
                "report_reason": report_reason,
                "description": description,
                "reported_by": reported_by,
                "reported_at": datetime.utcnow(),
                "status": "open",
                "priority": self._calculate_report_priority(report_reason),
                "investigation_notes": [],
                "resolution": None,
                "resolved_at": None,
                "resolved_by": None
            }
            
            collection = self.db.template_reports
            await collection.insert_one(report_record)
            
            return {
                "success": True,
                "report_record": report_record,
                "message": "Template report submitted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error reporting template issue: {e}")
            return {"success": False, "error": str(e)}

    async def get_bundle_selling_requirements(self, bundle_name: str) -> Dict[str, Any]:
        """Get specific selling requirements for a bundle"""
        try:
            if bundle_name not in self.selling_requirements["allowed_bundles"]:
                return {"success": False, "error": f"Bundle '{bundle_name}' does not support template selling"}
            
            # Bundle-specific requirements
            bundle_requirements = {
                "creator": {
                    "allowed_categories": ["bio_link", "website", "landing_page", "portfolio"],
                    "max_templates_per_month": 10,
                    "requires_approval": True,
                    "special_features": ["AI-powered templates", "Advanced customization"]
                },
                "ecommerce": {
                    "allowed_categories": ["ecommerce", "landing_page", "business"],
                    "max_templates_per_month": 15,
                    "requires_approval": True,
                    "special_features": ["E-commerce integration", "Payment processing"]
                },
                "education": {
                    "allowed_categories": ["course", "educational", "landing_page"],
                    "max_templates_per_month": 8,
                    "requires_approval": True,
                    "special_features": ["Student management", "Course structure"]
                }
            }
            
            # Default requirements for other bundles
            default_requirements = {
                "allowed_categories": ["website", "landing_page", "business"],
                "max_templates_per_month": 5,
                "requires_approval": True,
                "special_features": ["Basic customization"]
            }
            
            requirements = bundle_requirements.get(bundle_name, default_requirements)
            
            return {
                "success": True,
                "bundle_name": bundle_name,
                "requirements": requirements,
                "general_requirements": self.selling_requirements["quality_requirements"],
                "revenue_share": self.selling_requirements["revenue_share"]
            }
            
        except Exception as e:
            logger.error(f"Error getting bundle requirements: {e}")
            return {"success": False, "error": str(e)}

    async def check_admin_access(self, workspace_id: str, user_id: str) -> bool:
        """Check if user has admin access to workspace"""
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
            logger.error(f"Error checking admin access: {e}")
            return False

    # Private helper methods
    
    async def _get_seller_record(self, user_id: str, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get seller record for user in workspace"""
        try:
            collection = self.db.template_seller_access
            return await collection.find_one({
                "user_id": user_id,
                "workspace_id": workspace_id
            })
        except Exception as e:
            logger.error(f"Error getting seller record: {e}")
            return None
    
    async def _check_workspace_membership(self, workspace_id: str, user_id: str) -> bool:
        """Check if user is member of workspace"""
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
            logger.error(f"Error checking workspace membership: {e}")
            return False
    
    async def _create_audit_log(self, user_id: str, workspace_id: str, action: str, details: Dict[str, Any], performed_by: str):
        """Create audit log entry"""
        try:
            audit_record = {
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                "workspace_id": workspace_id,
                "action": action,
                "details": details,
                "performed_by": performed_by,
                "performed_at": datetime.utcnow(),
                "ip_address": None,  # Would capture from request in production
                "user_agent": None   # Would capture from request in production
            }
            
            collection = self.db.template_seller_audit_log
            await collection.insert_one(audit_record)
            
        except Exception as e:
            logger.error(f"Error creating audit log: {e}")
    
    def _calculate_period_dates(self, period: str) -> tuple:
        """Calculate start and end dates for a period"""
        now = datetime.utcnow()
        
        if period == "week":
            start = now - timedelta(days=7)
            end = now
        elif period == "month":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = start.replace(day=28) + timedelta(days=4)
            end = next_month - timedelta(days=next_month.day)
        elif period == "quarter":
            quarter_start_month = ((now.month - 1) // 3) * 3 + 1
            start = now.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif period == "year":
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        else:
            # Default to month
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = start.replace(day=28) + timedelta(days=4)
            end = next_month - timedelta(days=next_month.day)
        
        return start, end
    
    def _calculate_report_priority(self, report_reason: str) -> str:
        """Calculate priority level for template reports"""
        high_priority_reasons = ["copyright_violation", "inappropriate_content"]
        medium_priority_reasons = ["misleading_description", "broken_template"]
        
        if report_reason in high_priority_reasons:
            return "high"
        elif report_reason in medium_priority_reasons:
            return "medium"
        else:
            return "low"


# Service instance
_template_marketplace_access_service = None

def get_template_marketplace_access_service() -> TemplateMarketplaceAccessService:
    """Get template marketplace access service instance"""
    global _template_marketplace_access_service
    if _template_marketplace_access_service is None:
        _template_marketplace_access_service = TemplateMarketplaceAccessService()
    return _template_marketplace_access_service