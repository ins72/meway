"""
AI Token Purchase Service
Handles purchasing additional AI tokens beyond bundle limits
Smart pricing with volume discounts and usage-based recommendations
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from core.database import get_database
from services.workspace_subscription_service import get_workspace_subscription_service
from services.usage_tracking_service import get_usage_tracking_service
import uuid

logger = logging.getLogger(__name__)

class AITokenPurchaseService:
    def __init__(self):
        self.db = get_database()
        
        # AI Token pricing packages with volume discounts
        self.token_packages = {
            "starter_100": {
                "id": "starter_100",
                "name": "Starter Pack",
                "tokens": 100,
                "price": 9.99,
                "price_per_token": 0.0999,
                "popular": False,
                "best_for": "Light usage",
                "features": ["Valid for 6 months", "No expiry rollover"]
            },
            "popular_500": {
                "id": "popular_500", 
                "name": "Popular Pack",
                "tokens": 500,
                "price": 39.99,
                "price_per_token": 0.0799,  # 20% discount
                "popular": True,
                "best_for": "Regular users",
                "features": ["Valid for 6 months", "20% discount", "Priority support"]
            },
            "professional_1000": {
                "id": "professional_1000",
                "name": "Professional Pack", 
                "tokens": 1000,
                "price": 69.99,
                "price_per_token": 0.0699,  # 30% discount
                "popular": False,
                "best_for": "Heavy users",
                "features": ["Valid for 12 months", "30% discount", "Priority support", "Usage analytics"]
            },
            "business_2500": {
                "id": "business_2500",
                "name": "Business Pack",
                "tokens": 2500, 
                "price": 149.99,
                "price_per_token": 0.0599,  # 40% discount
                "popular": False,
                "best_for": "Small teams",
                "features": ["Valid for 12 months", "40% discount", "Priority support", "Usage analytics", "Bulk gifting"]
            },
            "enterprise_5000": {
                "id": "enterprise_5000",
                "name": "Enterprise Pack",
                "tokens": 5000,
                "price": 249.99,
                "price_per_token": 0.0499,  # 50% discount
                "popular": False,
                "best_for": "Large teams",
                "features": ["Valid for 12 months", "50% discount", "Priority support", "Usage analytics", "Bulk gifting", "Custom integrations"]
            },
            "unlimited_monthly": {
                "id": "unlimited_monthly",
                "name": "Unlimited Monthly",
                "tokens": -1,  # Unlimited
                "price": 199.99,
                "price_per_token": 0,
                "popular": False,
                "best_for": "Power users",
                "features": ["Unlimited tokens for 30 days", "Priority support", "Advanced analytics", "API access"]
            }
        }
        
        # Token usage tracking
        self.token_usage_categories = {
            "content_generation": {"description": "Blog posts, articles, copy", "weight": 1.0},
            "image_generation": {"description": "AI-generated images", "weight": 2.0},
            "code_generation": {"description": "Code snippets, automation", "weight": 1.5},
            "translation": {"description": "Multi-language translation", "weight": 0.8},
            "optimization": {"description": "SEO, performance suggestions", "weight": 1.2},
            "analysis": {"description": "Data analysis, insights", "weight": 1.3}
        }

    async def health_check(self):
        """Health check for AI token purchase service"""
        try:
            collection = self.db.ai_token_balances
            # Test database connection
            await collection.count_documents({})
            
            return {
                "success": True,
                "healthy": True,
                "service": "ai_token_purchase",
                "timestamp": datetime.utcnow().isoformat(),
                "available_packages": len(self.token_packages)
            }
        except Exception as e:
            logger.error(f"AI token purchase health check failed: {e}")
            return {
                "success": False,
                "healthy": False,
                "error": str(e)
            }

    async def get_token_pricing(self) -> Dict[str, Any]:
        """Get AI token pricing tiers with volume discounts"""
        try:
            # Calculate savings for each package
            base_price_per_token = 0.10  # $0.10 per token at regular price
            
            enhanced_packages = {}
            for package_id, package_info in self.token_packages.items():
                enhanced_package = {**package_info}
                
                if package_info["tokens"] > 0:  # Not unlimited
                    regular_price = package_info["tokens"] * base_price_per_token
                    savings = regular_price - package_info["price"]
                    savings_percentage = (savings / regular_price) * 100 if regular_price > 0 else 0
                    
                    enhanced_package.update({
                        "regular_price": regular_price,
                        "savings": round(savings, 2),
                        "savings_percentage": round(savings_percentage, 0),
                        "monthly_equivalent": round(package_info["price"] / 6, 2) if "6 months" in str(package_info.get("features", [])) else round(package_info["price"] / 12, 2)
                    })
                
                enhanced_packages[package_id] = enhanced_package
            
            return {
                "success": True,
                "packages": enhanced_packages,
                "currency": "USD",
                "base_price_per_token": base_price_per_token,
                "volume_discounts": {
                    "100_tokens": "0% discount",
                    "500_tokens": "20% discount", 
                    "1000_tokens": "30% discount",
                    "2500_tokens": "40% discount",
                    "5000_tokens": "50% discount"
                },
                "payment_methods": ["credit_card", "paypal", "stripe"],
                "refund_policy": "30-day money-back guarantee for unused tokens"
            }
            
        except Exception as e:
            logger.error(f"Error getting token pricing: {e}")
            return {"success": False, "error": str(e)}

    async def get_token_balance(self, workspace_id: str, user_id: str) -> Dict[str, Any]:
        """Get current AI token balance for workspace"""
        try:
            # Check workspace access
            if not await self._check_workspace_access(workspace_id, user_id):
                return {"success": False, "error": "Access denied"}
            
            # Get current balance
            balance_collection = self.db.ai_token_balances
            balance_record = await balance_collection.find_one({"workspace_id": workspace_id})
            
            if not balance_record:
                # Create initial balance record
                balance_record = await self._create_initial_balance(workspace_id)
            
            # Get bundle allocation
            bundle_allocation = await self._get_bundle_token_allocation(workspace_id, user_id)
            
            # Calculate usage this month
            current_month_usage = await self._get_current_month_usage(workspace_id)
            
            return {
                "success": True,
                "workspace_id": workspace_id,
                "token_balance": {
                    "purchased_tokens": balance_record.get("purchased_tokens", 0),
                    "bundle_tokens": bundle_allocation.get("monthly_tokens", 0),
                    "bonus_tokens": balance_record.get("bonus_tokens", 0),
                    "total_available": balance_record.get("total_tokens", 0),
                    "used_this_month": current_month_usage,
                    "remaining": max(0, balance_record.get("total_tokens", 0) - current_month_usage)
                },
                "bundle_info": bundle_allocation,
                "usage_analytics": await self._get_usage_breakdown(workspace_id),
                "expiry_info": {
                    "purchased_tokens_expire": balance_record.get("purchased_tokens_expire_at"),
                    "bundle_tokens_reset": self._get_next_month_start().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting token balance: {e}")
            return {"success": False, "error": str(e)}

    async def purchase_tokens(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Purchase additional AI tokens"""
        try:
            workspace_id = data.get("workspace_id")
            package_id = data.get("package_id")
            payment_method = data.get("payment_method", "stripe")
            purchased_by = data.get("purchased_by")
            
            # Validate package
            if package_id not in self.token_packages:
                return {"success": False, "error": f"Invalid package ID: {package_id}"}
            
            package_info = self.token_packages[package_id]
            
            # Check workspace access
            if not await self._check_workspace_access(workspace_id, purchased_by):
                return {"success": False, "error": "Access denied"}
            
            # Create purchase record
            purchase_record = {
                "_id": str(uuid.uuid4()),
                "workspace_id": workspace_id,
                "package_id": package_id,
                "package_info": package_info,
                "tokens_purchased": package_info["tokens"],
                "price_paid": package_info["price"],
                "payment_method": payment_method,
                "purchased_by": purchased_by,
                "purchased_at": datetime.utcnow(),
                "status": "pending_payment",
                "expires_at": self._calculate_expiry_date(package_info),
                "payment_reference": f"tok_{workspace_id[:8]}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            }
            
            # Store purchase record
            purchases_collection = self.db.ai_token_purchases
            await purchases_collection.insert_one(purchase_record)
            
            # Simulate payment processing (integrate with Stripe in production)
            payment_result = await self._process_payment(purchase_record)
            
            if payment_result.get("success"):
                # Update token balance
                await self._add_tokens_to_balance(workspace_id, package_info["tokens"], purchase_record["_id"])
                
                # Update purchase record
                await purchases_collection.update_one(
                    {"_id": purchase_record["_id"]},
                    {
                        "$set": {
                            "status": "completed",
                            "payment_confirmed_at": datetime.utcnow(),
                            "payment_details": payment_result.get("payment_details", {})
                        }
                    }
                )
                
                return {
                    "success": True,
                    "purchase_record": purchase_record,
                    "tokens_added": package_info["tokens"],
                    "new_balance": await self._get_current_balance(workspace_id),
                    "message": f"Successfully purchased {package_info['tokens']} AI tokens"
                }
            else:
                # Update purchase record with failure
                await purchases_collection.update_one(
                    {"_id": purchase_record["_id"]},
                    {"$set": {"status": "failed", "failure_reason": payment_result.get("error")}}
                )
                
                return {
                    "success": False,
                    "error": f"Payment failed: {payment_result.get('error')}",
                    "purchase_reference": purchase_record["payment_reference"]
                }
            
        except Exception as e:
            logger.error(f"Error purchasing tokens: {e}")
            return {"success": False, "error": str(e)}

    async def get_token_usage_history(self, workspace_id: str, period: str, limit: int, offset: int, user_id: str) -> Dict[str, Any]:
        """Get AI token usage history for workspace"""
        try:
            # Check access
            if not await self._check_workspace_access(workspace_id, user_id):
                return {"success": False, "error": "Access denied"}
            
            # Calculate period dates
            period_start, period_end = self._calculate_period_dates(period)
            
            # Get usage records
            usage_collection = self.db.ai_token_usage
            
            # Build query
            query = {
                "workspace_id": workspace_id,
                "used_at": {"$gte": period_start, "$lte": period_end}
            }
            
            # Get total count
            total_count = await usage_collection.count_documents(query)
            
            # Get paginated results
            cursor = usage_collection.find(query).sort("used_at", -1).skip(offset).limit(limit)
            usage_records = await cursor.to_list(length=limit)
            
            # Aggregate usage by category
            pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$category",
                    "total_tokens": {"$sum": "$tokens_used"},
                    "usage_count": {"$sum": 1}
                }}
            ]
            
            category_usage = await usage_collection.aggregate(pipeline).to_list(length=None)
            
            return {
                "success": True,
                "workspace_id": workspace_id,
                "period": {
                    "start": period_start.isoformat(),
                    "end": period_end.isoformat(),
                    "description": period
                },
                "usage_history": usage_records,
                "pagination": {
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_count
                },
                "category_breakdown": {
                    category["_id"]: {
                        "tokens_used": category["total_tokens"],
                        "usage_count": category["usage_count"],
                        "category_info": self.token_usage_categories.get(category["_id"], {})
                    }
                    for category in category_usage
                },
                "total_tokens_used": sum(record.get("tokens_used", 0) for record in usage_records)
            }
            
        except Exception as e:
            logger.error(f"Error getting token usage history: {e}")
            return {"success": False, "error": str(e)}

    async def get_purchase_history(self, workspace_id: str, limit: int, offset: int, user_id: str) -> Dict[str, Any]:
        """Get token purchase history for workspace"""
        try:
            # Check access
            if not await self._check_workspace_access(workspace_id, user_id):
                return {"success": False, "error": "Access denied"}
            
            collection = self.db.ai_token_purchases
            
            # Get total count
            total_count = await collection.count_documents({"workspace_id": workspace_id})
            
            # Get paginated results
            cursor = collection.find({"workspace_id": workspace_id}).sort("purchased_at", -1).skip(offset).limit(limit)
            purchases = await cursor.to_list(length=limit)
            
            # Calculate summary stats
            total_spent = sum(purchase.get("price_paid", 0) for purchase in purchases if purchase.get("status") == "completed")
            total_tokens_purchased = sum(purchase.get("tokens_purchased", 0) for purchase in purchases if purchase.get("status") == "completed")
            
            return {
                "success": True,
                "workspace_id": workspace_id,
                "purchase_history": purchases,
                "pagination": {
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_count
                },
                "summary": {
                    "total_purchases": len([p for p in purchases if p.get("status") == "completed"]),
                    "total_spent": total_spent,
                    "total_tokens_purchased": total_tokens_purchased,
                    "average_purchase": total_spent / len(purchases) if purchases else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting purchase history: {e}")
            return {"success": False, "error": str(e)}

    async def gift_tokens(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Gift AI tokens to another workspace"""
        try:
            from_workspace_id = data.get("from_workspace_id")
            to_workspace_id = data.get("to_workspace_id")
            token_amount = data.get("token_amount")
            message = data.get("message", "")
            gifted_by = data.get("gifted_by")
            
            # Check if sender has enough tokens
            from_balance = await self._get_current_balance(from_workspace_id)
            if from_balance < token_amount:
                return {"success": False, "error": "Insufficient token balance"}
            
            # Check access to both workspaces
            if not await self._check_workspace_access(from_workspace_id, gifted_by):
                return {"success": False, "error": "Access denied to sender workspace"}
            
            # Verify recipient workspace exists
            to_workspace_exists = await self._workspace_exists(to_workspace_id)
            if not to_workspace_exists:
                return {"success": False, "error": "Recipient workspace not found"}
            
            # Create gift record
            gift_record = {
                "_id": str(uuid.uuid4()),
                "from_workspace_id": from_workspace_id,
                "to_workspace_id": to_workspace_id,
                "token_amount": token_amount,
                "message": message,
                "gifted_by": gifted_by,
                "gifted_at": datetime.utcnow(),
                "status": "completed",
                "gift_reference": f"gift_{from_workspace_id[:8]}_to_{to_workspace_id[:8]}_{datetime.utcnow().strftime('%Y%m%d')}"
            }
            
            # Deduct tokens from sender
            await self._deduct_tokens_from_balance(from_workspace_id, token_amount, "gift_sent", gift_record["_id"])
            
            # Add tokens to recipient
            await self._add_tokens_to_balance(to_workspace_id, token_amount, gift_record["_id"], "gift_received")
            
            # Store gift record
            gifts_collection = self.db.ai_token_gifts
            await gifts_collection.insert_one(gift_record)
            
            return {
                "success": True,
                "gift_record": gift_record,
                "message": f"Successfully gifted {token_amount} tokens to workspace {to_workspace_id}"
            }
            
        except Exception as e:
            logger.error(f"Error gifting tokens: {e}")
            return {"success": False, "error": str(e)}

    async def setup_auto_refill(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Setup automatic token refill when balance gets low"""
        try:
            workspace_id = data.get("workspace_id")
            trigger_threshold = data.get("trigger_threshold", 50)  # Refill when < 50 tokens
            refill_package_id = data.get("refill_package_id", "popular_500")
            configured_by = data.get("configured_by")
            
            # Validate refill package
            if refill_package_id not in self.token_packages:
                return {"success": False, "error": f"Invalid refill package: {refill_package_id}"}
            
            # Create auto-refill configuration
            auto_refill_config = {
                "_id": str(uuid.uuid4()),
                "workspace_id": workspace_id,
                "trigger_threshold": trigger_threshold,
                "refill_package_id": refill_package_id,
                "refill_package_info": self.token_packages[refill_package_id],
                "configured_by": configured_by,
                "configured_at": datetime.utcnow(),
                "status": "active",
                "last_triggered": None,
                "total_auto_purchases": 0,
                "total_auto_spent": 0.0
            }
            
            # Store configuration (replace existing if any)
            collection = self.db.ai_token_auto_refill
            await collection.replace_one(
                {"workspace_id": workspace_id},
                auto_refill_config,
                upsert=True
            )
            
            return {
                "success": True,
                "auto_refill_config": auto_refill_config,
                "message": f"Auto-refill configured: {self.token_packages[refill_package_id]['tokens']} tokens when balance < {trigger_threshold}"
            }
            
        except Exception as e:
            logger.error(f"Error setting up auto-refill: {e}")
            return {"success": False, "error": str(e)}

    async def get_token_recommendations(self, workspace_id: str, user_id: str) -> Dict[str, Any]:
        """Get personalized token purchase recommendations based on usage patterns"""
        try:
            # Check access
            if not await self._check_workspace_access(workspace_id, user_id):
                return {"success": False, "error": "Access denied"}
            
            # Get usage history for last 3 months
            usage_data = await self._get_usage_analytics(workspace_id, 90)
            current_balance = await self._get_current_balance(workspace_id)
            
            recommendations = []
            
            # Analyze usage patterns
            avg_monthly_usage = usage_data.get("average_monthly_usage", 0)
            usage_trend = usage_data.get("trend", "stable")  # growing, stable, declining
            
            # Recommendation 1: Based on current usage
            if avg_monthly_usage > 0:
                months_remaining = current_balance / avg_monthly_usage if avg_monthly_usage > 0 else 12
                
                if months_remaining < 1:
                    # Urgent recommendation
                    recommended_package = self._find_best_package_for_usage(avg_monthly_usage * 3)  # 3 months worth
                    recommendations.append({
                        "type": "urgent",
                        "title": "Running Low on Tokens",
                        "description": f"Based on your usage of {avg_monthly_usage:.0f} tokens/month, you'll run out in {months_remaining:.1f} months",
                        "recommended_package": recommended_package,
                        "priority": "high",
                        "savings": self._calculate_savings(recommended_package)
                    })
                elif months_remaining < 2:
                    # Standard recommendation
                    recommended_package = self._find_best_package_for_usage(avg_monthly_usage * 6)  # 6 months worth
                    recommendations.append({
                        "type": "standard",
                        "title": "Stock Up for Better Value",
                        "description": f"Buy in bulk and save {self._calculate_savings_percentage(recommended_package):.0f}%",
                        "recommended_package": recommended_package,
                        "priority": "medium",
                        "savings": self._calculate_savings(recommended_package)
                    })
            
            # Recommendation 2: Based on usage trend
            if usage_trend == "growing":
                growth_package = self._find_best_package_for_usage(avg_monthly_usage * 8)  # Accommodate growth
                recommendations.append({
                    "type": "growth",
                    "title": "Usage is Growing",
                    "description": "Your AI usage has increased recently. Consider a larger package to avoid frequent purchases",
                    "recommended_package": growth_package,
                    "priority": "medium",
                    "trend_data": usage_data.get("trend_details", {})
                })
            
            # Recommendation 3: Seasonal/promotional
            current_month = datetime.utcnow().month
            if current_month in [11, 12, 1]:  # Holiday season
                recommendations.append({
                    "type": "seasonal",
                    "title": "Holiday Special",
                    "description": "Get extra tokens for your holiday campaigns and content creation",
                    "recommended_package": self.token_packages["business_2500"],
                    "priority": "low",
                    "special_offer": "10% extra tokens on Business and Enterprise packages"
                })
            
            return {
                "success": True,
                "workspace_id": workspace_id,
                "current_balance": current_balance,
                "usage_analytics": usage_data,
                "recommendations": recommendations,
                "personalization_factors": {
                    "avg_monthly_usage": avg_monthly_usage,
                    "usage_trend": usage_trend,
                    "months_remaining": months_remaining if 'months_remaining' in locals() else None,
                    "primary_use_cases": usage_data.get("top_categories", [])
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting token recommendations: {e}")
            return {"success": False, "error": str(e)}

    async def redeem_promo_code(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redeem promotional code for free tokens"""
        try:
            workspace_id = data.get("workspace_id")
            promo_code = data.get("promo_code").upper()
            redeemed_by = data.get("redeemed_by")
            
            # Check if promo code exists and is valid
            promo_collection = self.db.ai_token_promo_codes
            promo_record = await promo_collection.find_one({"code": promo_code})
            
            if not promo_record:
                return {"success": False, "error": "Invalid promo code"}
            
            # Check if code is still valid
            if promo_record.get("expires_at") and datetime.utcnow() > promo_record["expires_at"]:
                return {"success": False, "error": "Promo code has expired"}
            
            # Check usage limits
            if promo_record.get("max_uses") and promo_record.get("times_used", 0) >= promo_record["max_uses"]:
                return {"success": False, "error": "Promo code usage limit reached"}
            
            # Check if already used by this workspace
            if promo_record.get("one_per_workspace", True):
                existing_redemption = await self.db.ai_token_promo_redemptions.find_one({
                    "promo_code": promo_code,
                    "workspace_id": workspace_id
                })
                if existing_redemption:
                    return {"success": False, "error": "Promo code already used by this workspace"}
            
            # Create redemption record
            redemption_record = {
                "_id": str(uuid.uuid4()),
                "promo_code": promo_code,
                "workspace_id": workspace_id,
                "redeemed_by": redeemed_by,
                "tokens_granted": promo_record["token_value"],
                "redeemed_at": datetime.utcnow(),
                "promo_details": promo_record
            }
            
            # Add tokens to balance
            await self._add_tokens_to_balance(
                workspace_id, 
                promo_record["token_value"], 
                redemption_record["_id"], 
                "promo_redemption"
            )
            
            # Store redemption
            await self.db.ai_token_promo_redemptions.insert_one(redemption_record)
            
            # Update promo usage count
            await promo_collection.update_one(
                {"code": promo_code},
                {"$inc": {"times_used": 1}}
            )
            
            return {
                "success": True,
                "redemption_record": redemption_record,
                "tokens_granted": promo_record["token_value"],
                "new_balance": await self._get_current_balance(workspace_id),
                "message": f"Successfully redeemed {promo_record['token_value']} free tokens!"
            }
            
        except Exception as e:
            logger.error(f"Error redeeming promo code: {e}")
            return {"success": False, "error": str(e)}

    async def get_token_analytics(self, workspace_id: str, period: str, user_id: str) -> Dict[str, Any]:
        """Get AI token usage analytics and insights"""
        try:
            # Check access
            if not await self._check_workspace_access(workspace_id, user_id):
                return {"success": False, "error": "Access denied"}
            
            # Get detailed analytics
            analytics_data = await self._get_usage_analytics(workspace_id, self._period_to_days(period))
            
            return {
                "success": True,
                "workspace_id": workspace_id,
                "analytics": analytics_data,
                "insights": await self._generate_usage_insights(workspace_id, analytics_data),
                "cost_analysis": await self._analyze_token_costs(workspace_id, analytics_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting token analytics: {e}")
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
    
    async def _create_initial_balance(self, workspace_id: str) -> Dict[str, Any]:
        """Create initial token balance record for workspace"""
        try:
            balance_record = {
                "_id": str(uuid.uuid4()),
                "workspace_id": workspace_id,
                "purchased_tokens": 0,
                "bundle_tokens": 0,
                "bonus_tokens": 0,
                "total_tokens": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "purchased_tokens_expire_at": None
            }
            
            collection = self.db.ai_token_balances
            await collection.insert_one(balance_record)
            
            return balance_record
            
        except Exception as e:
            logger.error(f"Error creating initial balance: {e}")
            return {}
    
    async def _get_bundle_token_allocation(self, workspace_id: str, user_id: str) -> Dict[str, Any]:
        """Get token allocation from workspace subscription bundles"""
        try:
            subscription_service = get_workspace_subscription_service()
            subscription_result = await subscription_service.get_workspace_subscription(workspace_id, user_id)
            
            if not subscription_result.get("success"):
                return {"monthly_tokens": 0, "bundle_type": "free"}
            
            subscription = subscription_result.get("subscription", {})
            bundles = subscription.get("bundles", [])
            
            # Calculate token allocation based on bundles
            monthly_tokens = 0
            bundle_benefits = []
            
            for bundle in bundles:
                if bundle == "creator":
                    monthly_tokens += 500  # Creator bundle gets 500 tokens/month
                    bundle_benefits.append("500 AI tokens/month")
                elif bundle in ["business", "ecommerce"]:
                    monthly_tokens += 300  # Business bundles get 300 tokens/month
                    bundle_benefits.append("300 AI tokens/month")
                elif bundle in ["education", "social_media"]:
                    monthly_tokens += 200  # Other bundles get 200 tokens/month
                    bundle_benefits.append("200 AI tokens/month")
            
            return {
                "monthly_tokens": monthly_tokens,
                "bundle_type": "paid" if bundles else "free",
                "active_bundles": bundles,
                "bundle_benefits": bundle_benefits,
                "resets_on": self._get_next_month_start().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting bundle token allocation: {e}")
            return {"monthly_tokens": 0, "bundle_type": "free"}
    
    def _get_next_month_start(self) -> datetime:
        """Get the start of next month"""
        now = datetime.utcnow()
        if now.month == 12:
            return datetime(now.year + 1, 1, 1)
        else:
            return datetime(now.year, now.month + 1, 1)
    
    async def _get_current_month_usage(self, workspace_id: str) -> int:
        """Get current month token usage"""
        try:
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            usage_collection = self.db.ai_token_usage
            pipeline = [
                {
                    "$match": {
                        "workspace_id": workspace_id,
                        "used_at": {"$gte": month_start}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_used": {"$sum": "$tokens_used"}
                    }
                }
            ]
            
            result = await usage_collection.aggregate(pipeline).to_list(length=1)
            return result[0]["total_used"] if result else 0
            
        except Exception as e:
            logger.error(f"Error getting current month usage: {e}")
            return 0
    
    def _calculate_expiry_date(self, package_info: Dict[str, Any]) -> datetime:
        """Calculate token expiry date based on package"""
        now = datetime.utcnow()
        
        # Check package features for validity period
        features = package_info.get("features", [])
        
        if "Valid for 12 months" in features:
            return now + timedelta(days=365)
        elif "Valid for 6 months" in features:
            return now + timedelta(days=180)
        elif "Valid for 30 days" in features or package_info.get("tokens") == -1:
            return now + timedelta(days=30)
        else:
            return now + timedelta(days=180)  # Default 6 months
    
    async def _process_payment(self, purchase_record: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment for token purchase (mock for now)"""
        try:
            # Mock payment processing - integrate with Stripe in production
            import random
            
            # Simulate payment processing delay
            await asyncio.sleep(0.1)
            
            # Mock success (95% success rate)
            if random.random() < 0.95:
                return {
                    "success": True,
                    "payment_details": {
                        "transaction_id": f"txn_{uuid.uuid4().hex[:16]}",
                        "payment_method": purchase_record["payment_method"],
                        "amount": purchase_record["price_paid"],
                        "currency": "USD",
                        "processed_at": datetime.utcnow()
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Payment declined by bank"
                }
                
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            return {"success": False, "error": str(e)}
    
    async def _add_tokens_to_balance(self, workspace_id: str, tokens: int, transaction_id: str, transaction_type: str = "purchase"):
        """Add tokens to workspace balance"""
        try:
            collection = self.db.ai_token_balances
            
            # Update balance
            await collection.update_one(
                {"workspace_id": workspace_id},
                {
                    "$inc": {
                        "purchased_tokens": tokens if transaction_type == "purchase" else 0,
                        "bonus_tokens": tokens if transaction_type in ["gift_received", "promo_redemption"] else 0,
                        "total_tokens": tokens
                    },
                    "$set": {"updated_at": datetime.utcnow()},
                    "$setOnInsert": {
                        "_id": str(uuid.uuid4()),
                        "workspace_id": workspace_id,
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            # Create transaction log
            await self._log_token_transaction(workspace_id, tokens, "credit", transaction_type, transaction_id)
            
        except Exception as e:
            logger.error(f"Error adding tokens to balance: {e}")
    
    async def _get_current_balance(self, workspace_id: str) -> int:
        """Get current token balance for workspace"""
        try:
            collection = self.db.ai_token_balances
            balance_record = await collection.find_one({"workspace_id": workspace_id})
            
            return balance_record.get("total_tokens", 0) if balance_record else 0
            
        except Exception as e:
            logger.error(f"Error getting current balance: {e}")
            return 0
    
    def _find_best_package_for_usage(self, target_tokens: int) -> Dict[str, Any]:
        """Find the best package for target token amount"""
        best_package = None
        best_value = float('inf')
        
        for package_id, package_info in self.token_packages.items():
            if package_info["tokens"] > 0 and package_info["tokens"] >= target_tokens:
                value_score = package_info["price"] / package_info["tokens"]  # Price per token
                if value_score < best_value:
                    best_value = value_score
                    best_package = package_info
        
        return best_package or self.token_packages["popular_500"]  # Fallback
    
    def _calculate_savings(self, package_info: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate savings for a package"""
        if not package_info or package_info.get("tokens", 0) <= 0:
            return {"amount": 0, "percentage": 0}
        
        base_price = package_info["tokens"] * 0.10  # $0.10 per token base price
        actual_price = package_info["price"]
        savings = base_price - actual_price
        
        return {
            "amount": round(savings, 2),
            "percentage": round((savings / base_price) * 100, 0) if base_price > 0 else 0
        }
    
    def _period_to_days(self, period: str) -> int:
        """Convert period string to days"""
        period_map = {
            "week": 7,
            "month": 30,
            "quarter": 90,
            "year": 365
        }
        return period_map.get(period, 30)
    
    async def _log_token_transaction(self, workspace_id: str, tokens: int, transaction_type: str, category: str, reference_id: str):
        """Log token transaction for audit trail"""
        try:
            log_record = {
                "_id": str(uuid.uuid4()),
                "workspace_id": workspace_id,
                "tokens": tokens,
                "transaction_type": transaction_type,  # credit, debit
                "category": category,  # purchase, usage, gift, etc.
                "reference_id": reference_id,
                "timestamp": datetime.utcnow()
            }
            
            collection = self.db.ai_token_transaction_log
            await collection.insert_one(log_record)
            
        except Exception as e:
            logger.error(f"Error logging token transaction: {e}")


# Service instance
_ai_token_purchase_service = None

def get_ai_token_purchase_service() -> AITokenPurchaseService:
    """Get AI token purchase service instance"""
    global _ai_token_purchase_service
    if _ai_token_purchase_service is None:
        _ai_token_purchase_service = AITokenPurchaseService()
    return _ai_token_purchase_service