"""
Template Marketplace Revenue Service
Handle template sales, commissions, and payouts
"""

import uuid
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from core.objectid_serializer import safe_document_return, safe_documents_return, serialize_objectid

logger = logging.getLogger(__name__)

class TemplateMarketplaceRevenueService:
    """Service for managing template marketplace revenue and commissions"""
    
    def __init__(self):
        self.collection_name = "template_sales"
        self.payouts_collection = "template_payouts"
        self.service_name = "template_marketplace_revenue"
        self.mewayz_commission_rate = 0.30  # 30% commission to Mewayz

    async def _get_collection_async(self):
        """Get collection for async database operations"""
        try:
            from core.database import get_database_async
            db = await get_database_async()
            if db is None:
                logger.error("Database not available")
                return None
            return db[self.collection_name]
        except Exception as e:
            logger.error(f"Error getting async collection: {e}")
            return None

    async def _get_payouts_collection_async(self):
        """Get payouts collection for async database operations"""
        try:
            from core.database import get_database_async
            db = await get_database_async()
            if db is None:
                logger.error("Database not available")
                return None
            return db[self.payouts_collection]
        except Exception as e:
            logger.error(f"Error getting async payouts collection: {e}")
            return None

    async def health_check(self) -> dict:
        """Health check for template marketplace revenue service"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "healthy": False, "error": "Database unavailable"}
            
            await collection.count_documents({})
            
            return {
                "success": True,
                "healthy": True,
                "service": self.service_name,
                "features": ["template_sales", "commissions", "payouts", "analytics"],
                "commission_rate": f"{self.mewayz_commission_rate * 100}%",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check error in {self.service_name}: {e}")
            return {"success": False, "healthy": False, "error": str(e)}

    async def process_template_sale(self, data: dict) -> dict:
        """Process template sale and calculate commissions"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            sale_price = float(data.get("sale_price", 0))
            template_id = data.get("template_id")
            seller_id = data.get("seller_id")
            buyer_id = data.get("buyer_id")
            
            # Calculate commissions
            mewayz_commission = sale_price * self.mewayz_commission_rate
            seller_earnings = sale_price - mewayz_commission
            
            # Create sale record
            sale_data = {
                "id": str(uuid.uuid4()),
                "template_id": template_id,
                "seller_id": seller_id,
                "buyer_id": buyer_id,
                "sale_price": sale_price,
                "currency": data.get("currency", "USD"),
                "mewayz_commission": mewayz_commission,
                "seller_earnings": seller_earnings,
                "commission_rate": self.mewayz_commission_rate,
                "payment_method": data.get("payment_method", "stripe"),
                "transaction_id": data.get("transaction_id"),
                "status": "completed",
                "template_info": {
                    "title": data.get("template_title", ""),
                    "category": data.get("template_category", ""),
                    "type": data.get("template_type", "")
                },
                "buyer_info": {
                    "email": data.get("buyer_email", ""),
                    "name": data.get("buyer_name", "")
                },
                "created_at": datetime.utcnow().isoformat(),
                "processed_at": datetime.utcnow().isoformat()
            }
            
            # Store sale record
            result = await collection.insert_one(sale_data)
            
            if result.inserted_id:
                sale_data["_id"] = result.inserted_id
                
                # Update seller's pending earnings
                await self._update_seller_earnings(seller_id, seller_earnings)
                
                return {
                    "success": True,
                    "data": {
                        "sale_id": sale_data["id"],
                        "sale_price": sale_price,
                        "mewayz_commission": mewayz_commission,
                        "seller_earnings": seller_earnings,
                        "commission_rate": f"{self.mewayz_commission_rate * 100}%"
                    },
                    "message": "Template sale processed successfully"
                }
            else:
                return {"success": False, "error": "Failed to process template sale"}
                
        except Exception as e:
            logger.error(f"Process template sale error: {e}")
            return {"success": False, "error": str(e)}

    async def _update_seller_earnings(self, seller_id: str, earnings: float):
        """Update seller's pending earnings"""
        try:
            payouts_collection = await self._get_payouts_collection_async()
            if payouts_collection is None:
                return
            
            # Check if seller has pending payout record
            existing_payout = await payouts_collection.find_one({
                "seller_id": seller_id,
                "status": "pending"
            })
            
            if existing_payout:
                # Update existing pending payout
                await payouts_collection.update_one(
                    {"id": existing_payout["id"]},
                    {
                        "$inc": {
                            "total_earnings": earnings,
                            "sale_count": 1
                        },
                        "$set": {"updated_at": datetime.utcnow().isoformat()}
                    }
                )
            else:
                # Create new pending payout record
                payout_data = {
                    "id": str(uuid.uuid4()),
                    "seller_id": seller_id,
                    "total_earnings": earnings,
                    "sale_count": 1,
                    "currency": "USD",
                    "status": "pending",
                    "minimum_payout": 50.0,  # $50 minimum payout
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "processed_at": None
                }
                
                await payouts_collection.insert_one(payout_data)
                
        except Exception as e:
            logger.error(f"Update seller earnings error: {e}")

    async def get_seller_earnings(self, seller_id: str, period: str = "all") -> dict:
        """Get seller earnings summary"""
        try:
            collection = await self._get_collection_async()
            payouts_collection = await self._get_payouts_collection_async()
            
            if collection is None or payouts_collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            # Build date filter based on period
            date_filter = {}
            if period != "all":
                now = datetime.utcnow()
                if period == "month":
                    start_date = now.replace(day=1)
                elif period == "quarter":
                    start_date = now.replace(month=((now.month-1)//3)*3+1, day=1)
                elif period == "year":
                    start_date = now.replace(month=1, day=1)
                else:
                    start_date = now - timedelta(days=30)
                
                date_filter = {"created_at": {"$gte": start_date.isoformat()}}
            
            # Get sales data
            query = {"seller_id": seller_id, **date_filter}
            cursor = collection.find(query)
            sales = await cursor.to_list(length=None)
            
            # Calculate totals
            total_sales = len(sales)
            total_revenue = sum(sale.get("sale_price", 0) for sale in sales)
            total_earnings = sum(sale.get("seller_earnings", 0) for sale in sales)
            total_commission = sum(sale.get("mewayz_commission", 0) for sale in sales)
            
            # Get pending earnings
            pending_payout = await payouts_collection.find_one({
                "seller_id": seller_id,
                "status": "pending"
            })
            
            pending_earnings = pending_payout.get("total_earnings", 0) if pending_payout else 0
            
            # Get paid earnings
            paid_cursor = payouts_collection.find({
                "seller_id": seller_id,
                "status": "paid"
            })
            paid_payouts = await paid_cursor.to_list(length=None)
            total_paid = sum(payout.get("total_earnings", 0) for payout in paid_payouts)
            
            return {
                "success": True,
                "data": {
                    "seller_id": seller_id,
                    "period": period,
                    "summary": {
                        "total_sales": total_sales,
                        "total_revenue": total_revenue,
                        "total_earnings": total_earnings,
                        "mewayz_commission": total_commission,
                        "commission_rate": f"{self.mewayz_commission_rate * 100}%"
                    },
                    "earnings": {
                        "pending": pending_earnings,
                        "paid": total_paid,
                        "total": pending_earnings + total_paid
                    },
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Get seller earnings error: {e}")
            return {"success": False, "error": str(e)}

    async def get_seller_sales(self, seller_id: str, limit: int = 50, offset: int = 0, status: Optional[str] = None) -> dict:
        """Get seller's template sales"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            query = {"seller_id": seller_id}
            if status:
                query["status"] = status
            
            cursor = collection.find(query).sort("created_at", -1)
            sales = await cursor.skip(offset).limit(limit).to_list(length=limit)
            
            total_count = await collection.count_documents(query)
            
            return {
                "success": True,
                "data": safe_documents_return(sales),
                "total_count": total_count,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"Get seller sales error: {e}")
            return {"success": False, "error": str(e)}

    async def get_marketplace_analytics(self, period: str = "month") -> dict:
        """Get marketplace analytics (admin only)"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            # Build date filter
            now = datetime.utcnow()
            if period == "month":
                start_date = now.replace(day=1)
            elif period == "quarter":
                start_date = now.replace(month=((now.month-1)//3)*3+1, day=1)
            elif period == "year":
                start_date = now.replace(month=1, day=1)
            else:
                start_date = now - timedelta(days=30)
            
            date_filter = {"created_at": {"$gte": start_date.isoformat()}}
            
            # Get all sales in period
            cursor = collection.find(date_filter)
            sales = await cursor.to_list(length=None)
            
            # Calculate analytics
            total_sales = len(sales)
            total_revenue = sum(sale.get("sale_price", 0) for sale in sales)
            total_commission = sum(sale.get("mewayz_commission", 0) for sale in sales)
            
            # Top sellers
            seller_stats = {}
            for sale in sales:
                seller_id = sale.get("seller_id")
                if seller_id not in seller_stats:
                    seller_stats[seller_id] = {"sales": 0, "revenue": 0}
                seller_stats[seller_id]["sales"] += 1
                seller_stats[seller_id]["revenue"] += sale.get("sale_price", 0)
            
            top_sellers = sorted(seller_stats.items(), key=lambda x: x[1]["revenue"], reverse=True)[:10]
            
            # Category breakdown
            category_stats = {}
            for sale in sales:
                category = sale.get("template_info", {}).get("category", "Other")
                if category not in category_stats:
                    category_stats[category] = {"sales": 0, "revenue": 0}
                category_stats[category]["sales"] += 1
                category_stats[category]["revenue"] += sale.get("sale_price", 0)
            
            return {
                "success": True,
                "data": {
                    "period": period,
                    "summary": {
                        "total_sales": total_sales,
                        "total_revenue": total_revenue,
                        "mewayz_commission": total_commission,
                        "seller_earnings": total_revenue - total_commission,
                        "commission_rate": f"{self.mewayz_commission_rate * 100}%"
                    },
                    "top_sellers": [
                        {"seller_id": seller_id, **stats} 
                        for seller_id, stats in top_sellers
                    ],
                    "category_breakdown": category_stats,
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Get marketplace analytics error: {e}")
            return {"success": False, "error": str(e)}

    async def get_commission_summary(self, period: str = "month") -> dict:
        """Get Mewayz commission summary (admin only)"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            # Build date filter
            now = datetime.utcnow()
            if period == "month":
                start_date = now.replace(day=1)
            elif period == "quarter":
                start_date = now.replace(month=((now.month-1)//3)*3+1, day=1)
            elif period == "year":
                start_date = now.replace(month=1, day=1)
            else:
                start_date = now - timedelta(days=30)
            
            date_filter = {"created_at": {"$gte": start_date.isoformat()}}
            
            # Get commission data
            cursor = collection.find(date_filter)
            sales = await cursor.to_list(length=None)
            
            total_commission = sum(sale.get("mewayz_commission", 0) for sale in sales)
            total_revenue = sum(sale.get("sale_price", 0) for sale in sales)
            
            return {
                "success": True,
                "data": {
                    "period": period,
                    "total_sales": len(sales),
                    "total_revenue": total_revenue,
                    "total_commission": total_commission,
                    "commission_rate": f"{self.mewayz_commission_rate * 100}%",
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Get commission summary error: {e}")
            return {"success": False, "error": str(e)}

    async def create_seller_payout(self, data: dict) -> dict:
        """Create payout for seller (admin only)"""
        try:
            payouts_collection = await self._get_payouts_collection_async()
            if payouts_collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            seller_id = data.get("seller_id")
            amount = float(data.get("amount", 0))
            
            # Create payout record
            payout_data = {
                "id": str(uuid.uuid4()),
                "seller_id": seller_id,
                "amount": amount,
                "currency": data.get("currency", "USD"),
                "payment_method": data.get("payment_method", "bank_transfer"),
                "payment_details": data.get("payment_details", {}),
                "status": "processing",
                "notes": data.get("notes", ""),
                "created_at": datetime.utcnow().isoformat(),
                "processed_at": None
            }
            
            result = await payouts_collection.insert_one(payout_data)
            
            if result.inserted_id:
                payout_data["_id"] = result.inserted_id
                return {
                    "success": True,
                    "data": safe_document_return(payout_data),
                    "message": "Payout created successfully"
                }
            else:
                return {"success": False, "error": "Failed to create payout"}
                
        except Exception as e:
            logger.error(f"Create seller payout error: {e}")
            return {"success": False, "error": str(e)}

    async def get_payouts(self, seller_id: Optional[str] = None, status: Optional[str] = None, limit: int = 50, offset: int = 0) -> dict:
        """Get payouts"""
        try:
            payouts_collection = await self._get_payouts_collection_async()
            if payouts_collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            query = {}
            if seller_id:
                query["seller_id"] = seller_id
            if status:
                query["status"] = status
            
            cursor = payouts_collection.find(query).sort("created_at", -1)
            payouts = await cursor.skip(offset).limit(limit).to_list(length=limit)
            
            total_count = await payouts_collection.count_documents(query)
            
            return {
                "success": True,
                "data": safe_documents_return(payouts),
                "total_count": total_count,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"Get payouts error: {e}")
            return {"success": False, "error": str(e)}

    async def process_payout(self, payout_id: str, data: dict) -> dict:
        """Process payout (admin only)"""
        try:
            payouts_collection = await self._get_payouts_collection_async()
            if payouts_collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            update_data = {
                "status": data.get("status", "paid"),
                "processed_at": datetime.utcnow().isoformat(),
                "processed_by": data.get("processed_by"),
                "transaction_id": data.get("transaction_id", ""),
                "notes": data.get("notes", "")
            }
            
            result = await payouts_collection.update_one(
                {"id": payout_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return {
                    "success": True,
                    "message": "Payout processed successfully"
                }
            else:
                return {"success": False, "error": "Payout not found or already processed"}
                
        except Exception as e:
            logger.error(f"Process payout error: {e}")
            return {"success": False, "error": str(e)}

    async def get_template_sales(self, template_id: str, seller_id: str, limit: int = 50, offset: int = 0) -> dict:
        """Get sales for specific template"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            query = {
                "template_id": template_id,
                "seller_id": seller_id
            }
            
            cursor = collection.find(query).sort("created_at", -1)
            sales = await cursor.skip(offset).limit(limit).to_list(length=limit)
            
            total_count = await collection.count_documents(query)
            
            return {
                "success": True,
                "data": safe_documents_return(sales),
                "total_count": total_count,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"Get template sales error: {e}")
            return {"success": False, "error": str(e)}

    async def process_refund(self, data: dict) -> dict:
        """Process template sale refund (admin only)"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            sale_id = data.get("sale_id")
            refund_reason = data.get("refund_reason", "")
            
            # Find the sale
            sale = await collection.find_one({"id": sale_id})
            if not sale:
                return {"success": False, "error": "Sale not found"}
            
            # Update sale status to refunded
            result = await collection.update_one(
                {"id": sale_id},
                {
                    "$set": {
                        "status": "refunded",
                        "refund_reason": refund_reason,
                        "refunded_at": datetime.utcnow().isoformat(),
                        "refunded_by": data.get("processed_by")
                    }
                }
            )
            
            if result.modified_count > 0:
                # Adjust seller earnings (subtract from pending)
                await self._adjust_seller_earnings(
                    sale.get("seller_id"), 
                    -sale.get("seller_earnings", 0)
                )
                
                return {
                    "success": True,
                    "message": "Refund processed successfully"
                }
            else:
                return {"success": False, "error": "Failed to process refund"}
                
        except Exception as e:
            logger.error(f"Process refund error: {e}")
            return {"success": False, "error": str(e)}

    async def _adjust_seller_earnings(self, seller_id: str, adjustment: float):
        """Adjust seller's pending earnings"""
        try:
            payouts_collection = await self._get_payouts_collection_async()
            if payouts_collection is None:
                return
            
            await payouts_collection.update_one(
                {"seller_id": seller_id, "status": "pending"},
                {
                    "$inc": {"total_earnings": adjustment},
                    "$set": {"updated_at": datetime.utcnow().isoformat()}
                }
            )
            
        except Exception as e:
            logger.error(f"Adjust seller earnings error: {e}")


def get_template_marketplace_revenue_service():
    """Get template marketplace revenue service instance"""
    return TemplateMarketplaceRevenueService()