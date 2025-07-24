"""
Launch Pricing Service
Handles time-limited launch specials and promotional pricing for bundle subscriptions
Based on MEWAYZ_V2_SMART_LAUNCH_PRICING_STRATEGY.md
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from core.database import get_database
import uuid
import random
import string

logger = logging.getLogger(__name__)

class LaunchPricingService:
    def __init__(self):
        self.db = get_database()
        
        # Launch specials configuration based on pricing strategy
        self.launch_specials = {
            "creator": {
                "special_id": "creator_launch_1000",
                "title": "Creator Launch Special",
                "description": "First 1000 users get 3 months for $9/month",
                "original_price": 19.0,
                "special_price": 9.0,
                "duration_months": 3,
                "max_claims": 1000,
                "current_claims": 0,
                "start_date": datetime(2024, 12, 30),
                "end_date": datetime(2025, 3, 31),  # 3 months launch window
                "active": True,
                "terms": "After 3 months, regular pricing of $19/month applies",
                "promo_codes": ["CREATOR9", "LAUNCH9", "CREATE9"]
            },
            
            "ecommerce": {
                "special_id": "ecommerce_launch_500",
                "title": "E-commerce Launch Special",
                "description": "First 500 users get 2 months free",
                "original_price": 24.0,
                "special_price": 0.0,
                "duration_months": 2,
                "max_claims": 500,
                "current_claims": 0,
                "start_date": datetime(2024, 12, 30),
                "end_date": datetime(2025, 2, 28),  # 2 months launch window
                "active": True,
                "terms": "After 2 months, regular pricing of $24/month applies",
                "promo_codes": ["ECOMMFREE", "LAUNCH2FREE", "SHOPFREE"]
            },
            
            "social_media": {
                "special_id": "social_trial_14",
                "title": "Social Media Trial Special",
                "description": "First 2 weeks free trial",
                "original_price": 29.0,
                "special_price": 0.0,
                "duration_months": 0.5,  # 2 weeks = 0.5 months
                "max_claims": 2000,  # Higher limit for trial
                "current_claims": 0,
                "start_date": datetime(2024, 12, 30),
                "end_date": datetime(2025, 6, 30),  # 6 months launch window
                "active": True,
                "terms": "After 2 weeks, regular pricing of $29/month applies",
                "promo_codes": ["SOCIAL14", "TRIAL14", "SOCIALTRIAL"]
            },
            
            "education": {
                "special_id": "education_first_month",
                "title": "Education First Month Free",
                "description": "First month free",
                "original_price": 29.0,
                "special_price": 0.0,
                "duration_months": 1,
                "max_claims": 1500,
                "current_claims": 0,
                "start_date": datetime(2024, 12, 30),
                "end_date": datetime(2025, 12, 31),  # Full year launch window
                "active": True,
                "terms": "After 1 month, regular pricing of $29/month applies",
                "promo_codes": ["EDUFREE", "LEARN1FREE", "EDUCATION"]
            },
            
            "business": {
                "special_id": "business_50_off_3",
                "title": "Business 50% Off Special",
                "description": "50% off first 3 months",
                "original_price": 39.0,
                "special_price": 19.5,
                "duration_months": 3,
                "max_claims": 750,
                "current_claims": 0,
                "start_date": datetime(2024, 12, 30),
                "end_date": datetime(2025, 3, 31),  # 3 months launch window
                "active": True,
                "terms": "After 3 months, regular pricing of $39/month applies",
                "promo_codes": ["BIZ50", "BUSINESS50", "LAUNCH50"]
            },
            
            "operations": {
                "special_id": "ops_first_month",
                "title": "Operations First Month Free",
                "description": "First month free",
                "original_price": 24.0,
                "special_price": 0.0,
                "duration_months": 1,
                "max_claims": 1000,
                "current_claims": 0,
                "start_date": datetime(2024, 12, 30),
                "end_date": datetime(2025, 12, 31),  # Full year launch window
                "active": True,
                "terms": "After 1 month, regular pricing of $24/month applies",
                "promo_codes": ["OPSFREE", "OPS1FREE", "OPERATIONS"]
            }
        }
        
        # Multi-bundle launch specials
        self.multi_bundle_specials = {
            "2_bundle_combo": {
                "title": "2-Bundle Launch Combo",
                "description": "25% off any 2 bundles for first 6 months",
                "discount_percentage": 0.25,
                "duration_months": 6,
                "max_claims": 300,
                "current_claims": 0,
                "min_bundles": 2,
                "promo_codes": ["COMBO25", "2BUNDLE25"]
            },
            
            "3_bundle_combo": {
                "title": "3-Bundle Launch Combo",
                "description": "35% off any 3 bundles for first 6 months",
                "discount_percentage": 0.35,
                "duration_months": 6,
                "max_claims": 200,
                "current_claims": 0,
                "min_bundles": 3,
                "promo_codes": ["COMBO35", "3BUNDLE35"]
            }
        }

    async def health_check(self):
        """Health check for launch pricing service"""
        try:
            collection = self.db.launch_special_claims
            # Test database connection
            await collection.count_documents({})
            
            active_specials = len([s for s in self.launch_specials.values() if s["active"]])
            
            return {
                "success": True,
                "healthy": True,
                "service": "launch_pricing",
                "timestamp": datetime.utcnow().isoformat(),
                "active_specials": active_specials,
                "total_specials": len(self.launch_specials)
            }
        except Exception as e:
            logger.error(f"Launch pricing health check failed: {e}")
            return {
                "success": False,
                "healthy": False,
                "error": str(e)
            }

    async def get_active_specials(self) -> Dict[str, Any]:
        """Get all currently active launch specials"""
        try:
            now = datetime.utcnow()
            active_specials = {}
            
            for bundle_name, special in self.launch_specials.items():
                # Check if special is active and within date range
                if (special["active"] and 
                    special["start_date"] <= now <= special["end_date"] and
                    special["current_claims"] < special["max_claims"]):
                    
                    # Get current claim count from database
                    current_claims = await self._get_current_claims(special["special_id"])
                    special["current_claims"] = current_claims
                    
                    # Calculate remaining spots
                    remaining_spots = special["max_claims"] - current_claims
                    urgency_level = self._calculate_urgency(remaining_spots, special["max_claims"])
                    
                    active_specials[bundle_name] = {
                        **special,
                        "remaining_spots": remaining_spots,
                        "urgency_level": urgency_level,
                        "savings_amount": special["original_price"] - special["special_price"],
                        "savings_percentage": ((special["original_price"] - special["special_price"]) / special["original_price"]) * 100,
                        "days_remaining": (special["end_date"] - now).days,
                        "is_ending_soon": (special["end_date"] - now).days <= 7
                    }
            
            return {
                "success": True,
                "active_specials": active_specials,
                "total_active": len(active_specials),
                "multi_bundle_specials": self.multi_bundle_specials
            }
            
        except Exception as e:
            logger.error(f"Error getting active specials: {e}")
            return {"success": False, "error": str(e)}

    async def get_bundle_special(self, bundle_name: str, user_id: str) -> Dict[str, Any]:
        """Get launch special for specific bundle"""
        try:
            if bundle_name not in self.launch_specials:
                return {"success": False, "error": f"No launch special found for bundle: {bundle_name}"}
            
            special = self.launch_specials[bundle_name].copy()
            now = datetime.utcnow()
            
            # Check if special is active
            if not special["active"]:
                return {"success": False, "error": "Launch special is not active"}
            
            # Check date range
            if not (special["start_date"] <= now <= special["end_date"]):
                return {"success": False, "error": "Launch special has expired"}
            
            # Get current claims
            current_claims = await self._get_current_claims(special["special_id"])
            special["current_claims"] = current_claims
            
            # Check availability
            if current_claims >= special["max_claims"]:
                return {"success": False, "error": "Launch special limit reached"}
            
            # Check if user already claimed this special
            user_claimed = await self._check_user_claimed(special["special_id"], user_id)
            if user_claimed:
                return {"success": False, "error": "You have already claimed this launch special"}
            
            # Calculate additional info
            remaining_spots = special["max_claims"] - current_claims
            savings_amount = special["original_price"] - special["special_price"]
            savings_percentage = (savings_amount / special["original_price"]) * 100
            
            return {
                "success": True,
                "bundle_name": bundle_name,
                "special": {
                    **special,
                    "remaining_spots": remaining_spots,
                    "savings_amount": savings_amount,
                    "savings_percentage": round(savings_percentage, 1),
                    "days_remaining": (special["end_date"] - now).days,
                    "urgency_level": self._calculate_urgency(remaining_spots, special["max_claims"]),
                    "user_eligible": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting bundle special: {e}")
            return {"success": False, "error": str(e)}

    async def claim_launch_special(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Claim a launch special offer"""
        try:
            bundle_name = data.get("bundle_name")
            workspace_id = data.get("workspace_id")
            claimed_by = data.get("claimed_by")
            special_code = data.get("special_code")  # Optional promo code
            
            # Validate bundle special exists and is available
            special_check = await self.get_bundle_special(bundle_name, claimed_by)
            if not special_check.get("success"):
                return special_check
            
            special = self.launch_specials[bundle_name]
            
            # Validate promo code if provided
            if special_code:
                if special_code.upper() not in [code.upper() for code in special["promo_codes"]]:
                    return {"success": False, "error": "Invalid promo code"}
            
            # Create claim record
            claim_record = {
                "_id": str(uuid.uuid4()),
                "special_id": special["special_id"],
                "bundle_name": bundle_name,
                "workspace_id": workspace_id,
                "claimed_by": claimed_by,
                "special_code": special_code.upper() if special_code else None,
                "claimed_at": datetime.utcnow(),
                "original_price": special["original_price"],
                "special_price": special["special_price"],
                "duration_months": special["duration_months"],
                "savings_amount": special["original_price"] - special["special_price"],
                "expires_at": datetime.utcnow() + timedelta(days=special["duration_months"] * 30),
                "status": "active",
                "terms_accepted": True,
                "claim_source": "web_app"
            }
            
            # Store claim
            collection = self.db.launch_special_claims
            await collection.insert_one(claim_record)
            
            # Update claim counter (in production, this would be atomic)
            await self._increment_claim_counter(special["special_id"])
            
            # Create promotional subscription record
            promo_subscription = await self._create_promotional_subscription(claim_record)
            
            return {
                "success": True,
                "claim_record": claim_record,
                "promotional_subscription": promo_subscription,
                "message": f"Successfully claimed {special['title']}!",
                "next_steps": "Your special pricing will be applied to your next billing cycle",
                "savings_summary": {
                    "monthly_savings": special["original_price"] - special["special_price"],
                    "total_savings": (special["original_price"] - special["special_price"]) * special["duration_months"],
                    "special_ends": claim_record["expires_at"].isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error claiming launch special: {e}")
            return {"success": False, "error": str(e)}

    async def validate_eligibility(self, bundle_name: str, workspace_id: str, user_id: str) -> Dict[str, Any]:
        """Validate if user is eligible for launch special"""
        try:
            # Check bundle special availability
            special_check = await self.get_bundle_special(bundle_name, user_id)
            if not special_check.get("success"):
                return {
                    "success": True,
                    "eligible": False,
                    "reason": special_check.get("error"),
                    "alternative_suggestions": await self._get_alternative_specials(bundle_name)
                }
            
            # Check workspace eligibility (new workspaces only for launch specials)
            workspace_age = await self._get_workspace_age(workspace_id)
            if workspace_age > 30:  # Workspace older than 30 days
                return {
                    "success": True,
                    "eligible": False,
                    "reason": "Launch specials are only available for new workspaces (created within 30 days)",
                    "workspace_created": workspace_age
                }
            
            # Check if workspace already has active subscription
            has_active_sub = await self._check_workspace_subscription(workspace_id, bundle_name)
            if has_active_sub:
                return {
                    "success": True,
                    "eligible": False,
                    "reason": "Workspace already has an active subscription for this bundle",
                    "suggestion": "Consider upgrading to additional bundles for multi-bundle discounts"
                }
            
            special = special_check["special"]
            
            return {
                "success": True,
                "eligible": True,
                "bundle_name": bundle_name,
                "special_details": special,
                "eligibility_expires": special["end_date"].isoformat(),
                "estimated_savings": special["savings_amount"] * special["duration_months"]
            }
            
        except Exception as e:
            logger.error(f"Error validating eligibility: {e}")
            return {"success": False, "error": str(e)}

    async def get_claimed_specials(self, workspace_id: str, user_id: str) -> Dict[str, Any]:
        """Get all launch specials claimed by workspace"""
        try:
            # Check access to workspace
            has_access = await self._check_workspace_access(workspace_id, user_id)
            if not has_access:
                return {"success": False, "error": "Access denied to workspace"}
            
            collection = self.db.launch_special_claims
            claims = await collection.find({"workspace_id": workspace_id}).to_list(length=100)
            
            # Enhance claims with current status
            enhanced_claims = []
            for claim in claims:
                enhanced_claim = claim.copy()
                
                # Check if special is still active
                now = datetime.utcnow()
                is_expired = claim["expires_at"] < now
                days_remaining = (claim["expires_at"] - now).days if not is_expired else 0
                
                enhanced_claim.update({
                    "is_expired": is_expired,
                    "days_remaining": days_remaining,
                    "status_display": "Expired" if is_expired else f"Active ({days_remaining} days left)",
                    "total_savings_realized": claim["savings_amount"] * claim["duration_months"]
                })
                
                enhanced_claims.append(enhanced_claim)
            
            # Calculate summary statistics
            total_savings = sum(claim["savings_amount"] * claim["duration_months"] for claim in claims)
            active_claims = [claim for claim in enhanced_claims if not claim["is_expired"]]
            
            return {
                "success": True,
                "workspace_id": workspace_id,
                "claimed_specials": enhanced_claims,
                "summary": {
                    "total_claims": len(claims),
                    "active_claims": len(active_claims),
                    "total_savings": total_savings,
                    "average_savings_per_claim": total_savings / len(claims) if claims else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting claimed specials: {e}")
            return {"success": False, "error": str(e)}

    async def generate_promo_code(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate promotional code for launch special (admin only)"""
        try:
            bundle_name = data.get("bundle_name")
            custom_code = data.get("custom_code")
            max_uses = data.get("max_uses", 100)
            expires_in_days = data.get("expires_in_days", 30)
            generated_by = data.get("generated_by")
            
            # Generate promo code
            if custom_code:
                promo_code = custom_code.upper()
            else:
                promo_code = self._generate_random_code(bundle_name)
            
            # Check if code already exists
            existing_code = await self._check_promo_code_exists(promo_code)
            if existing_code:
                return {"success": False, "error": "Promo code already exists"}
            
            # Create promo code record
            promo_record = {
                "_id": str(uuid.uuid4()),
                "promo_code": promo_code,
                "bundle_name": bundle_name,
                "special_id": self.launch_specials[bundle_name]["special_id"],
                "max_uses": max_uses,
                "current_uses": 0,
                "generated_by": generated_by,
                "generated_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(days=expires_in_days),
                "active": True,
                "code_type": "launch_special"
            }
            
            collection = self.db.launch_promo_codes
            await collection.insert_one(promo_record)
            
            return {
                "success": True,
                "promo_record": promo_record,
                "message": f"Promo code {promo_code} generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error generating promo code: {e}")
            return {"success": False, "error": str(e)}

    async def get_special_analytics(self, bundle_name: str = None) -> Dict[str, Any]:
        """Get analytics for launch specials (admin only)"""
        try:
            collection = self.db.launch_special_claims
            
            # Build query
            query = {}
            if bundle_name:
                query["bundle_name"] = bundle_name
            
            # Get all claims
            claims = await collection.find(query).to_list(length=None)
            
            # Calculate analytics
            analytics = {
                "total_claims": len(claims),
                "total_savings_given": sum(claim["savings_amount"] * claim["duration_months"] for claim in claims),
                "claims_by_bundle": {},
                "claims_by_month": {},
                "average_days_to_claim": 0,
                "most_popular_bundle": "",
                "conversion_metrics": {}
            }
            
            # Analyze by bundle
            for claim in claims:
                bundle = claim["bundle_name"]
                if bundle not in analytics["claims_by_bundle"]:
                    analytics["claims_by_bundle"][bundle] = {
                        "count": 0,
                        "total_savings": 0,
                        "avg_savings": 0
                    }
                
                analytics["claims_by_bundle"][bundle]["count"] += 1
                analytics["claims_by_bundle"][bundle]["total_savings"] += claim["savings_amount"] * claim["duration_months"]
            
            # Calculate averages
            for bundle_stats in analytics["claims_by_bundle"].values():
                bundle_stats["avg_savings"] = bundle_stats["total_savings"] / bundle_stats["count"]
            
            # Find most popular bundle
            if analytics["claims_by_bundle"]:
                analytics["most_popular_bundle"] = max(
                    analytics["claims_by_bundle"].items(),
                    key=lambda x: x[1]["count"]
                )[0]
            
            # Calculate conversion rates
            for bundle_name, special in self.launch_specials.items():
                current_claims = analytics["claims_by_bundle"].get(bundle_name, {}).get("count", 0)
                conversion_rate = (current_claims / special["max_claims"]) * 100
                
                analytics["conversion_metrics"][bundle_name] = {
                    "current_claims": current_claims,
                    "max_claims": special["max_claims"],
                    "conversion_rate": round(conversion_rate, 2),
                    "remaining_spots": special["max_claims"] - current_claims
                }
            
            return {
                "success": True,
                "analytics": analytics,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting special analytics: {e}")
            return {"success": False, "error": str(e)}

    async def extend_special(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extend or modify launch special (admin only)"""
        try:
            bundle_name = data.get("bundle_name")
            action = data.get("action")  # extend_time, increase_limit, modify_price
            value = data.get("value")
            modified_by = data.get("modified_by")
            
            if bundle_name not in self.launch_specials:
                return {"success": False, "error": f"Bundle {bundle_name} not found"}
            
            # Create modification record
            modification_record = {
                "_id": str(uuid.uuid4()),
                "bundle_name": bundle_name,
                "special_id": self.launch_specials[bundle_name]["special_id"],
                "action": action,
                "old_value": None,
                "new_value": value,
                "modified_by": modified_by,
                "modified_at": datetime.utcnow(),
                "reason": data.get("reason", "Admin modification")
            }
            
            # Apply modification
            if action == "extend_time":
                modification_record["old_value"] = self.launch_specials[bundle_name]["end_date"]
                self.launch_specials[bundle_name]["end_date"] = datetime.utcnow() + timedelta(days=value)
                modification_record["new_value"] = self.launch_specials[bundle_name]["end_date"]
                
            elif action == "increase_limit":
                modification_record["old_value"] = self.launch_specials[bundle_name]["max_claims"]
                self.launch_specials[bundle_name]["max_claims"] += value
                modification_record["new_value"] = self.launch_specials[bundle_name]["max_claims"]
                
            elif action == "modify_price":
                modification_record["old_value"] = self.launch_specials[bundle_name]["special_price"]
                self.launch_specials[bundle_name]["special_price"] = value
                modification_record["new_value"] = value
                
            else:
                return {"success": False, "error": f"Invalid action: {action}"}
            
            # Store modification record
            collection = self.db.launch_special_modifications
            await collection.insert_one(modification_record)
            
            return {
                "success": True,
                "modification_record": modification_record,
                "updated_special": self.launch_specials[bundle_name],
                "message": f"Successfully {action} for {bundle_name} special"
            }
            
        except Exception as e:
            logger.error(f"Error extending special: {e}")
            return {"success": False, "error": str(e)}

    async def track_referral(self, referral_code: str, user_id: str) -> Dict[str, Any]:
        """Track referral usage for launch specials"""
        try:
            # Find referral record  
            collection = self.db.referral_codes
            referral = await collection.find_one({"code": referral_code.upper()})
            
            if not referral:
                return {"success": False, "error": "Referral code not found"}
            
            # Check if already used by this user
            usage_collection = self.db.referral_usage
            existing_usage = await usage_collection.find_one({
                "referral_code": referral_code.upper(),
                "used_by": user_id
            })
            
            if existing_usage:
                return {"success": False, "error": "Referral code already used"}
            
            # Create usage record
            usage_record = {
                "_id": str(uuid.uuid4()),
                "referral_code": referral_code.upper(),
                "referrer_id": referral["created_by"],
                "used_by": user_id,
                "used_at": datetime.utcnow(),
                "special_benefits": "Launch special + referral bonus",
                "status": "active"
            }
            
            await usage_collection.insert_one(usage_record)
            
            return {
                "success": True,
                "referral_tracked": True,
                "usage_record": usage_record,
                "benefits": "You and your referrer both get launch special benefits!"
            }
            
        except Exception as e:
            logger.error(f"Error tracking referral: {e}")
            return {"success": False, "error": str(e)}

    # Private helper methods
    
    async def _get_current_claims(self, special_id: str) -> int:
        """Get current number of claims for a special"""
        try:
            collection = self.db.launch_special_claims
            count = await collection.count_documents({"special_id": special_id})
            return count
        except Exception as e:
            logger.error(f"Error getting current claims: {e}")
            return 0
    
    async def _check_user_claimed(self, special_id: str, user_id: str) -> bool:
        """Check if user already claimed this special"""
        try:
            collection = self.db.launch_special_claims
            claim = await collection.find_one({
                "special_id": special_id,
                "claimed_by": user_id
            })
            return claim is not None
        except Exception as e:
            logger.error(f"Error checking user claimed: {e}")
            return False
    
    def _calculate_urgency(self, remaining_spots: int, max_claims: int) -> str:
        """Calculate urgency level for special offers"""
        if remaining_spots <= 0:
            return "sold_out"
        elif remaining_spots <= max_claims * 0.1:  # Less than 10% left
            return "critical"
        elif remaining_spots <= max_claims * 0.25:  # Less than 25% left
            return "high"
        elif remaining_spots <= max_claims * 0.5:  # Less than 50% left
            return "medium"
        else:
            return "low"
    
    async def _increment_claim_counter(self, special_id: str):
        """Increment claim counter for special"""
        try:
            # In production, this would be an atomic operation
            collection = self.db.launch_special_counters
            await collection.update_one(
                {"special_id": special_id},
                {"$inc": {"count": 1}},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error incrementing claim counter: {e}")
    
    async def _create_promotional_subscription(self, claim_record: Dict[str, Any]) -> Dict[str, Any]:
        """Create promotional subscription record"""
        try:
            promo_subscription = {
                "_id": str(uuid.uuid4()),
                "workspace_id": claim_record["workspace_id"],
                "bundle_name": claim_record["bundle_name"],
                "claim_id": claim_record["_id"],
                "promotional_price": claim_record["special_price"],
                "regular_price": claim_record["original_price"],
                "promotion_duration": claim_record["duration_months"],
                "promotion_start": claim_record["claimed_at"],
                "promotion_end": claim_record["expires_at"],
                "status": "active",
                "auto_convert_to_regular": True,
                "created_at": datetime.utcnow()
            }
            
            collection = self.db.promotional_subscriptions
            await collection.insert_one(promo_subscription)
            
            return promo_subscription
            
        except Exception as e:
            logger.error(f"Error creating promotional subscription: {e}")
            return {}
    
    async def _get_workspace_age(self, workspace_id: str) -> int:
        """Get workspace age in days"""
        try:
            collection = self.db.workspace
            workspace = await collection.find_one({"id": workspace_id})
            
            if workspace and workspace.get("created_at"):
                age = (datetime.utcnow() - workspace["created_at"]).days
                return age
            return 0
        except Exception as e:
            logger.error(f"Error getting workspace age: {e}")
            return 999  # Assume old workspace on error
    
    async def _check_workspace_subscription(self, workspace_id: str, bundle_name: str) -> bool:
        """Check if workspace has active subscription for bundle"""
        try:
            collection = self.db.workspace_subscriptions
            subscription = await collection.find_one({
                "workspace_id": workspace_id,
                "bundles": {"$in": [bundle_name]},
                "status": "active"
            })
            return subscription is not None
        except Exception as e:
            logger.error(f"Error checking workspace subscription: {e}")
            return False
    
    async def _check_workspace_access(self, workspace_id: str, user_id: str) -> bool:
        """Check if user has access to workspace"""
        try:
            collection = self.db.workspace
            workspace = await collection.find_one({
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
    
    def _generate_random_code(self, bundle_name: str) -> str:
        """Generate random promo code"""
        prefix = bundle_name[:4].upper()
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"{prefix}{suffix}"
    
    async def _check_promo_code_exists(self, promo_code: str) -> bool:
        """Check if promo code already exists"""
        try:
            collection = self.db.launch_promo_codes
            existing = await collection.find_one({"promo_code": promo_code.upper()})
            return existing is not None
        except Exception as e:
            logger.error(f"Error checking promo code exists: {e}")
            return True  # Assume exists on error to be safe
    
    async def _get_alternative_specials(self, bundle_name: str) -> List[Dict[str, Any]]:
        """Get alternative specials when user is not eligible"""
        try:
            alternatives = []
            for name, special in self.launch_specials.items():
                if name != bundle_name and special["active"]:
                    current_claims = await self._get_current_claims(special["special_id"])
                    if current_claims < special["max_claims"]:
                        alternatives.append({
                            "bundle_name": name,
                            "title": special["title"],
                            "description": special["description"],
                            "savings_amount": special["original_price"] - special["special_price"]
                        })
            
            return alternatives[:3]  # Return top 3 alternatives
        except Exception as e:
            logger.error(f"Error getting alternative specials: {e}")
            return []


# Service instance
_launch_pricing_service = None

def get_launch_pricing_service() -> LaunchPricingService:
    """Get launch pricing service instance"""
    global _launch_pricing_service
    if _launch_pricing_service is None:
        _launch_pricing_service = LaunchPricingService()
    return _launch_pricing_service