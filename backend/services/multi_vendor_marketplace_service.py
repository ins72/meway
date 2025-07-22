"""
Multi-Vendor Marketplace Service
Complete seller management, commission automation, and marketplace analytics
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from decimal import Decimal

from core.database import get_database
from core.professional_logger import professional_logger, LogLevel, LogCategory

class SellerStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    SUSPENDED = "suspended"
    REJECTED = "rejected"

class CommissionType(Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"
    TIERED = "tiered"

class MarketplaceService:
    """Complete multi-vendor marketplace management"""
    
    def __init__(self):
        self.commission_rules = {
            "default_rate": 15.0,  # 15% commission
            "tiers": {
                "bronze": {"min_sales": 0, "rate": 15.0},
                "silver": {"min_sales": 10000, "rate": 12.0},
                "gold": {"min_sales": 50000, "rate": 10.0},
                "platinum": {"min_sales": 100000, "rate": 8.0}
            }
        }
    
    async def onboard_seller(self, seller_data: Dict[str, Any]) -> str:
        """Complete seller onboarding process"""
        try:
            db = get_database()
            
            seller_id = str(uuid.uuid4())
            
            seller_profile = {
                "seller_id": seller_id,
                "user_id": seller_data["user_id"],
                "business_name": seller_data["business_name"],
                "business_type": seller_data.get("business_type", "individual"),
                "contact_info": {
                    "email": seller_data["email"],
                    "phone": seller_data.get("phone", ""),
                    "address": seller_data.get("address", {})
                },
                "business_documents": {
                    "tax_id": seller_data.get("tax_id", ""),
                    "business_license": seller_data.get("business_license", ""),
                    "bank_account": seller_data.get("bank_account", {})
                },
                "status": SellerStatus.PENDING.value,
                "verification": {
                    "identity_verified": False,
                    "business_verified": False,
                    "bank_verified": False,
                    "documents_submitted": len([d for d in seller_data.get("documents", []) if d])
                },
                "commission_settings": {
                    "type": CommissionType.PERCENTAGE.value,
                    "rate": self.commission_rules["default_rate"],
                    "tier": "bronze"
                },
                "performance_metrics": {
                    "total_sales": 0,
                    "total_orders": 0,
                    "rating": 0,
                    "response_time_hours": 24,
                    "dispute_rate": 0
                },
                "payout_settings": {
                    "frequency": "weekly",  # weekly, biweekly, monthly
                    "minimum_payout": 100,
                    "currency": "USD",
                    "payment_method": "bank_transfer"
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await db.marketplace_sellers.insert_one(seller_profile)
            
            # Create seller dashboard record
            dashboard_data = {
                "seller_id": seller_id,
                "dashboard_settings": {
                    "notifications_enabled": True,
                    "auto_approval": False,
                    "inventory_alerts": True,
                    "performance_reports": True
                },
                "analytics_preferences": {
                    "daily_reports": True,
                    "weekly_summary": True,
                    "competitor_insights": False
                },
                "created_at": datetime.utcnow()
            }
            
            await db.seller_dashboards.insert_one(dashboard_data)
            
            await professional_logger.log(
                LogLevel.INFO, LogCategory.MARKETPLACE,
                f"Seller onboarded: {seller_data['business_name']}",
                details={"seller_id": seller_id, "status": "pending_verification"}
            )
            
            return seller_id
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.MARKETPLACE,
                f"Seller onboarding failed: {str(e)}",
                error=e
            )
            raise Exception(f"Seller onboarding failed: {str(e)}")
    
    async def verify_seller(self, seller_id: str, verification_data: Dict[str, Any]) -> bool:
        """Process seller verification"""
        try:
            db = get_database()
            
            verification_checks = {
                "identity_verified": verification_data.get("identity_documents_valid", False),
                "business_verified": verification_data.get("business_license_valid", False),
                "bank_verified": verification_data.get("bank_account_valid", False)
            }
            
            all_verified = all(verification_checks.values())
            
            update_data = {
                "verification": verification_checks,
                "status": SellerStatus.APPROVED.value if all_verified else SellerStatus.PENDING.value,
                "verification_date": datetime.utcnow() if all_verified else None,
                "updated_at": datetime.utcnow()
            }
            
            result = await db.marketplace_sellers.update_one(
                {"seller_id": seller_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                await professional_logger.log(
                    LogLevel.INFO, LogCategory.MARKETPLACE,
                    f"Seller verification updated: {seller_id}",
                    details={"verification_status": verification_checks, "approved": all_verified}
                )
                
                # Send notification to seller
                await self._notify_seller(seller_id, "verification_update", {
                    "status": "approved" if all_verified else "pending",
                    "next_steps": "You can now start selling" if all_verified else "Please complete remaining verification steps"
                })
            
            return all_verified
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.MARKETPLACE,
                f"Seller verification failed: {str(e)}",
                error=e
            )
            return False
    
    async def calculate_commission(self, seller_id: str, order_amount: float) -> Dict[str, float]:
        """Calculate commission based on seller tier and performance"""
        try:
            db = get_database()
            
            seller = await db.marketplace_sellers.find_one({"seller_id": seller_id})
            if not seller:
                return {"commission": order_amount * 0.15, "seller_earnings": order_amount * 0.85}
            
            # Get seller's current tier
            total_sales = seller.get("performance_metrics", {}).get("total_sales", 0)
            
            # Determine tier
            current_tier = "bronze"
            for tier, rules in self.commission_rules["tiers"].items():
                if total_sales >= rules["min_sales"]:
                    current_tier = tier
            
            commission_rate = self.commission_rules["tiers"][current_tier]["rate"] / 100
            commission = order_amount * commission_rate
            seller_earnings = order_amount - commission
            
            # Update seller commission tier if changed
            if seller.get("commission_settings", {}).get("tier") != current_tier:
                await db.marketplace_sellers.update_one(
                    {"seller_id": seller_id},
                    {
                        "$set": {
                            "commission_settings.tier": current_tier,
                            "commission_settings.rate": self.commission_rules["tiers"][current_tier]["rate"]
                        }
                    }
                )
            
            return {
                "commission": round(commission, 2),
                "seller_earnings": round(seller_earnings, 2),
                "commission_rate": commission_rate,
                "tier": current_tier
            }
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.MARKETPLACE,
                f"Commission calculation failed: {str(e)}",
                error=e
            )
            # Fallback to default rate
            commission = order_amount * 0.15
            return {"commission": commission, "seller_earnings": order_amount - commission}
    
    async def process_payout(self, seller_id: str, payout_period: str) -> Dict[str, Any]:
        """Process automated seller payout"""
        try:
            db = get_database()
            
            # Get seller payout settings
            seller = await db.marketplace_sellers.find_one({"seller_id": seller_id})
            if not seller:
                raise Exception("Seller not found")
            
            payout_settings = seller.get("payout_settings", {})
            minimum_payout = payout_settings.get("minimum_payout", 100)
            
            # Calculate payout period
            end_date = datetime.utcnow()
            if payout_period == "weekly":
                start_date = end_date - timedelta(days=7)
            elif payout_period == "biweekly":
                start_date = end_date - timedelta(days=14)
            else:  # monthly
                start_date = end_date - timedelta(days=30)
            
            # Get seller earnings for period
            earnings_pipeline = [
                {
                    "$match": {
                        "seller_id": seller_id,
                        "created_at": {"$gte": start_date, "$lte": end_date},
                        "status": "completed"
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_earnings": {"$sum": "$seller_earnings"},
                        "total_orders": {"$sum": 1},
                        "commission_paid": {"$sum": "$commission"}
                    }
                }
            ]
            
            earnings_result = await db.order_commissions.aggregate(earnings_pipeline).to_list(length=1)
            
            if not earnings_result or earnings_result[0]["total_earnings"] < minimum_payout:
                return {
                    "payout_processed": False,
                    "reason": f"Earnings below minimum payout threshold (${minimum_payout})",
                    "earnings": earnings_result[0]["total_earnings"] if earnings_result else 0
                }
            
            earnings_data = earnings_result[0]
            payout_id = str(uuid.uuid4())
            
            # Create payout record
            payout_record = {
                "payout_id": payout_id,
                "seller_id": seller_id,
                "amount": earnings_data["total_earnings"],
                "period_start": start_date,
                "period_end": end_date,
                "orders_count": earnings_data["total_orders"],
                "commission_deducted": earnings_data["commission_paid"],
                "payment_method": payout_settings.get("payment_method", "bank_transfer"),
                "currency": payout_settings.get("currency", "USD"),
                "status": "processing",
                "created_at": datetime.utcnow(),
                "processed_at": None
            }
            
            await db.seller_payouts.insert_one(payout_record)
            
            # Here you would integrate with actual payment processor
            # For now, we'll simulate successful payout
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Update payout status
            await db.seller_payouts.update_one(
                {"payout_id": payout_id},
                {
                    "$set": {
                        "status": "completed",
                        "processed_at": datetime.utcnow(),
                        "transaction_id": f"txn_{payout_id[:8]}"
                    }
                }
            )
            
            await professional_logger.log(
                LogLevel.INFO, LogCategory.MARKETPLACE,
                f"Payout processed: {seller_id}",
                details={"payout_id": payout_id, "amount": earnings_data["total_earnings"]}
            )
            
            return {
                "payout_processed": True,
                "payout_id": payout_id,
                "amount": earnings_data["total_earnings"],
                "transaction_id": f"txn_{payout_id[:8]}"
            }
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.MARKETPLACE,
                f"Payout processing failed: {str(e)}",
                error=e
            )
            return {"payout_processed": False, "error": str(e)}
    
    async def get_seller_analytics(self, seller_id: str, days: int = 30) -> Dict[str, Any]:
        """Comprehensive seller performance analytics"""
        try:
            db = get_database()
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Sales analytics
            sales_pipeline = [
                {
                    "$match": {
                        "seller_id": seller_id,
                        "created_at": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$created_at"},
                            "month": {"$month": "$created_at"},
                            "day": {"$dayOfMonth": "$created_at"}
                        },
                        "daily_sales": {"$sum": "$total_amount"},
                        "daily_orders": {"$sum": 1},
                        "daily_commission": {"$sum": "$commission"}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            sales_data = await db.orders.aggregate(sales_pipeline).to_list(length=None)
            
            # Product performance
            product_pipeline = [
                {
                    "$match": {
                        "seller_id": seller_id,
                        "created_at": {"$gte": start_date}
                    }
                },
                {
                    "$unwind": "$items"
                },
                {
                    "$group": {
                        "_id": "$items.product_id",
                        "units_sold": {"$sum": "$items.quantity"},
                        "revenue": {"$sum": "$items.total_price"},
                        "orders": {"$sum": 1}
                    }
                },
                {"$sort": {"revenue": -1}},
                {"$limit": 10}
            ]
            
            product_performance = await db.orders.aggregate(product_pipeline).to_list(length=10)
            
            # Customer analytics
            customer_pipeline = [
                {
                    "$match": {
                        "seller_id": seller_id,
                        "created_at": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": "$customer_id",
                        "total_spent": {"$sum": "$total_amount"},
                        "order_count": {"$sum": 1},
                        "last_order": {"$max": "$created_at"}
                    }
                }
            ]
            
            customer_data = await db.orders.aggregate(customer_pipeline).to_list(length=None)
            
            # Calculate metrics
            total_sales = sum(day["daily_sales"] for day in sales_data)
            total_orders = sum(day["daily_orders"] for day in sales_data)
            average_order_value = total_sales / total_orders if total_orders > 0 else 0
            
            analytics = {
                "seller_id": seller_id,
                "period_days": days,
                "summary": {
                    "total_sales": total_sales,
                    "total_orders": total_orders,
                    "average_order_value": round(average_order_value, 2),
                    "unique_customers": len(customer_data),
                    "repeat_customers": len([c for c in customer_data if c["order_count"] > 1])
                },
                "daily_sales": sales_data,
                "top_products": product_performance,
                "customer_insights": {
                    "total_customers": len(customer_data),
                    "repeat_rate": (len([c for c in customer_data if c["order_count"] > 1]) / len(customer_data) * 100) if customer_data else 0,
                    "average_customer_value": sum(c["total_spent"] for c in customer_data) / len(customer_data) if customer_data else 0
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.MARKETPLACE,
                f"Seller analytics failed: {str(e)}",
                error=e
            )
            return {"error": str(e)}
    
    async def _notify_seller(self, seller_id: str, notification_type: str, data: Dict[str, Any]):
        """Send notification to seller"""
        try:
            # This would integrate with the notification system
            await professional_logger.log(
                LogLevel.INFO, LogCategory.MARKETPLACE,
                f"Seller notification: {notification_type}",
                details={"seller_id": seller_id, "data": data}
            )
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.MARKETPLACE,
                f"Seller notification failed: {str(e)}",
                error=e
            )

# Global instance
marketplace_service = MarketplaceService()
