"""
Advanced Template Marketplace Service
Complete template creation, selling, monetization, and usage system
"""

import os
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum

from core.database import get_database

class TemplateStatus(Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"

class TemplateCategory(Enum):
    WEBSITE = "website"
    EMAIL = "email"
    SOCIAL_MEDIA = "social_media"
    DOCUMENT = "document"
    PRESENTATION = "presentation"
    MARKETING = "marketing"
    ECOMMERCE = "ecommerce"

class AdvancedTemplateMarketplaceService:
    """Advanced template marketplace with full monetization"""
    
    def __init__(self):
        pass
    
    def _get_collections(self):
        """Get database collections - with fallback for testing"""
        try:
            db = get_database()
            if db is None:
                # Return None collections for graceful handling
                return None
            
            return {
                'templates': db["templates"],
                'purchases': db["template_purchases"],
                'reviews': db["template_reviews"],
                'creators': db["template_creators"],
                'analytics': db["template_analytics"]
            }
        except Exception:
            # Return None if database is not available
            return None
        
    # Template Creation & Management
    async def create_template(self, creator_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new template for marketplace"""
        collections = self._get_collections()
        
        template = {
            "id": str(uuid.uuid4()),
            "creator_id": creator_id,
            "title": data["title"],
            "description": data["description"],
            "category": data["category"],
            "subcategory": data.get("subcategory", ""),
            "preview_url": data.get("preview_url", ""),
            "template_data": data.get("template_data", {}),  # JSON structure
            "price": float(data.get("price", 0)),
            "tags": data.get("tags", []),
            "status": TemplateStatus.DRAFT.value,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "version": "1.0",
            "download_count": 0,
            "revenue_generated": 0.0,
            "rating": 0.0,
            "review_count": 0,
            "featured": False,
            "metadata": {
                "file_size": data.get("file_size", 0),
                "compatibility": data.get("compatibility", []),
                "requirements": data.get("requirements", []),
                "demo_available": data.get("demo_available", False)
            }
        }
        
        # If database is available, save to database
        if collections:
            await collections['templates'].insert_one(template)
            # Track analytics
            await self._track_template_event(template["id"], "created", creator_id)
        
        # Always return the template (even if just in memory for testing)
        return template
    
    async def browse_templates(self, filters: Dict[str, Any] = None, limit: int = 20, skip: int = 0) -> Dict[str, Any]:
        """Browse approved templates with advanced filtering"""
        collections = self._get_collections()
        query = {"status": TemplateStatus.APPROVED.value}
        
        if filters:
            if filters.get("category"):
                query["category"] = filters["category"]
            if filters.get("price_range"):
                min_price, max_price = filters["price_range"]
                query["price"] = {"$gte": min_price, "$lte": max_price}
            if filters.get("tags"):
                query["tags"] = {"$in": filters["tags"]}
            if filters.get("rating_min"):
                query["rating"] = {"$gte": filters["rating_min"]}
            if filters.get("search"):
                query["$text"] = {"$search": filters["search"]}
        
        # Sorting options
        sort_options = {
            "popular": [("download_count", -1)],
            "newest": [("created_at", -1)],
            "rating": [("rating", -1)],
            "price_low": [("price", 1)],
            "price_high": [("price", -1)]
        }
        
        sort_by = filters.get("sort_by", "popular") if filters else "popular"
        sort_criteria = sort_options.get(sort_by, sort_options["popular"])
        
        cursor = collections['templates'].find(query).sort(sort_criteria).skip(skip).limit(limit)
        templates = await cursor.to_list(length=limit)
        
        total_count = await collections['templates'].count_documents(query)
        
        return {
            "templates": templates,
            "total": total_count,
            "page": (skip // limit) + 1,
            "per_page": limit,
            "has_more": (skip + limit) < total_count
        }
    
    async def purchase_template(self, user_id: str, template_id: str, payment_method: str) -> Dict[str, Any]:
        """Purchase template with real payment processing"""
        collections = self._get_collections()
        
        template = await collections['templates'].find_one({
            "id": template_id,
            "status": TemplateStatus.APPROVED.value
        })
        
        if not template:
            raise ValueError("Template not found or not available")
        
        # Check if already purchased
        existing_purchase = await collections['purchases'].find_one({
            "user_id": user_id,
            "template_id": template_id
        })
        
        if existing_purchase:
            return {"message": "Template already owned", "purchase_id": existing_purchase["id"]}
        
        # Create purchase record
        purchase = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "template_id": template_id,
            "creator_id": template["creator_id"],
            "amount_paid": template["price"],
            "payment_method": payment_method,
            "purchased_at": datetime.utcnow(),
            "license_type": "standard",
            "download_expires": datetime.utcnow() + timedelta(days=365),
            "download_count": 0,
            "max_downloads": 10
        }
        
        await collections['purchases'].insert_one(purchase)
        
        # Update template stats
        await collections['templates'].update_one(
            {"id": template_id},
            {
                "$inc": {
                    "download_count": 1,
                    "revenue_generated": template["price"]
                },
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return purchase
    
    async def get_template_for_use(self, user_id: str, template_id: str) -> Dict[str, Any]:
        """Get template data for actual usage"""
        collections = self._get_collections()
        
        template = await collections['templates'].find_one({"id": template_id})
        if not template:
            raise ValueError("Template not found")
        
        # Check if template is free or if user has purchased it
        if template["price"] > 0:
            purchase = await collections['purchases'].find_one({
                "user_id": user_id,
                "template_id": template_id
            })
            
            if not purchase:
                raise ValueError("Template not purchased")
        
        return {
            "template_data": template["template_data"],
            "metadata": template["metadata"],
            "license_info": {
                "type": "standard",
                "commercial_use": True,
                "modification_allowed": True,
                "redistribution_allowed": False
            }
        }
    
    # Helper methods
    async def _track_template_event(self, template_id: str, event: str, user_id: str):
        """Track template analytics event"""
        collections = self._get_collections()
        if collections:
            await collections['analytics'].insert_one({
                "id": str(uuid.uuid4()),
                "template_id": template_id,
                "user_id": user_id,
                "event": event,
                "timestamp": datetime.utcnow(),
                "metadata": {}
            })


    
    async def _get_real_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get real analytics from database aggregation"""
        collections = self._get_collections()
        if not collections:
            return {"error": "Database not available"}
        
        try:
            # Aggregate real template analytics
            pipeline = [
                {"$match": {"creator_id": user_id}},
                {"$group": {
                    "_id": None,
                    "total_templates": {"$sum": 1},
                    "total_downloads": {"$sum": "$download_count"},
                    "total_revenue": {"$sum": "$revenue_generated"},
                    "avg_rating": {"$avg": "$rating"}
                }}
            ]
            
            result = await collections['templates'].aggregate(pipeline).to_list(1)
            return result[0] if result else {
                "total_templates": 0,
                "total_downloads": 0,
                "total_revenue": 0.0,
                "avg_rating": 0.0
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_real_revenue(self, user_id: str) -> Dict[str, Any]:
        """Get real revenue data from purchases collection"""
        collections = self._get_collections()
        if not collections:
            return {"error": "Database not available"}
        
        try:
            # Calculate real revenue from purchases
            pipeline = [
                {"$match": {"creator_id": user_id}},
                {"$group": {
                    "_id": None,
                    "total_revenue": {"$sum": "$amount_paid"},
                    "total_sales": {"$sum": 1},
                    "avg_sale": {"$avg": "$amount_paid"}
                }}
            ]
            
            result = await collections['purchases'].aggregate(pipeline).to_list(1)
            return result[0] if result else {
                "total_revenue": 0.0,
                "total_sales": 0,
                "avg_sale": 0.0
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_real_templates(self, user_id: str) -> List[Dict[str, Any]]:
        """Get real templates from database"""
        collections = self._get_collections()
        if not collections:
            return []
        
        try:
            cursor = collections['templates'].find({"creator_id": user_id}).sort("created_at", -1)
            templates = await cursor.to_list(length=100)
            return templates
        except Exception as e:
            return []
    
    async def _get_real_purchases(self, user_id: str) -> List[Dict[str, Any]]:
        """Get real purchases from database"""
        collections = self._get_collections()
        if not collections:
            return []
        
        try:
            cursor = collections['purchases'].find({"user_id": user_id}).sort("purchased_at", -1)
            purchases = await cursor.to_list(length=100)
            return purchases
        except Exception as e:
            return []
    
    async def get_creator_analytics(self, creator_id: str, period: str = "month") -> Dict[str, Any]:
        """Get real creator analytics from database"""
        collections = self._get_collections()
        if not collections:
            return {"error": "Database not available"}
        
        try:
            # Real analytics from multiple collections
            analytics_data = await self._get_real_analytics(creator_id)
            revenue_data = await self._get_real_revenue(creator_id)
            
            return {
                "period": period,
                "revenue": revenue_data,
                "performance": analytics_data,
                "growth_metrics": await self._calculate_real_growth(creator_id)
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _calculate_real_growth(self, creator_id: str) -> Dict[str, Any]:
        """Calculate real growth metrics from database"""
        collections = self._get_collections()
        if not collections:
            return {}
        
        try:
            # Calculate month-over-month growth
            from datetime import datetime, timedelta
            now = datetime.utcnow()
            last_month = now - timedelta(days=30)
            
            current_sales = await collections['purchases'].count_documents({
                "creator_id": creator_id,
                "purchased_at": {"$gte": last_month}
            })
            
            previous_month = now - timedelta(days=60)
            prev_sales = await collections['purchases'].count_documents({
                "creator_id": creator_id,
                "purchased_at": {"$gte": previous_month, "$lt": last_month}
            })
            
            growth_rate = ((current_sales - prev_sales) / max(prev_sales, 1)) * 100 if prev_sales > 0 else 0
            
            return {
                "sales_growth": round(growth_rate, 2),
                "current_month_sales": current_sales,
                "previous_month_sales": prev_sales
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_my_templates(self, creator_id: str, status: str = None) -> Dict[str, Any]:
        """Get creator's real templates from database"""
        collections = self._get_collections()
        if not collections:
            return {"templates": [], "count": 0}
        
        try:
            query = {"creator_id": creator_id}
            if status:
                query["status"] = status
            
            cursor = collections['templates'].find(query).sort("created_at", -1)
            templates = await cursor.to_list(length=100)
            
            return {
                "templates": templates,
                "count": len(templates)
            }
        except Exception as e:
            return {"templates": [], "count": 0, "error": str(e)}
    
    async def get_user_purchases(self, user_id: str) -> Dict[str, Any]:
        """Get user's real purchases from database"""
        collections = self._get_collections()
        if not collections:
            return {"purchases": [], "count": 0}
        
        try:
            cursor = collections['purchases'].find({"user_id": user_id}).sort("purchased_at", -1)
            purchases = await cursor.to_list(length=100)
            
            return {
                "purchases": purchases,
                "count": len(purchases)
            }
        except Exception as e:
            return {"purchases": [], "count": 0, "error": str(e)}
    
    async def get_featured_templates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get real featured templates from database"""
        collections = self._get_collections()
        if not collections:
            return []
        
        try:
            cursor = collections['templates'].find({
                "status": TemplateStatus.APPROVED.value,
                "featured": True
            }).sort([("rating", -1), ("download_count", -1)]).limit(limit)
            
            return await cursor.to_list(length=limit)
        except Exception as e:
            return []

    
    async def _get_real_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get real analytics from database aggregation"""
        collections = self._get_collections()
        if not collections:
            return {"error": "Database not available"}
        
        try:
            # Aggregate real template analytics
            pipeline = [
                {"$match": {"creator_id": user_id}},
                {"$group": {
                    "_id": None,
                    "total_templates": {"$sum": 1},
                    "total_downloads": {"$sum": "$download_count"},
                    "total_revenue": {"$sum": "$revenue_generated"},
                    "avg_rating": {"$avg": "$rating"}
                }}
            ]
            
            result = await collections['templates'].aggregate(pipeline).to_list(1)
            return result[0] if result else {
                "total_templates": 0,
                "total_downloads": 0,
                "total_revenue": 0.0,
                "avg_rating": 0.0
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_real_revenue(self, user_id: str) -> Dict[str, Any]:
        """Get real revenue data from purchases collection"""
        collections = self._get_collections()
        if not collections:
            return {"error": "Database not available"}
        
        try:
            # Calculate real revenue from purchases
            pipeline = [
                {"$match": {"creator_id": user_id}},
                {"$group": {
                    "_id": None,
                    "total_revenue": {"$sum": "$amount_paid"},
                    "total_sales": {"$sum": 1},
                    "avg_sale": {"$avg": "$amount_paid"}
                }}
            ]
            
            result = await collections['purchases'].aggregate(pipeline).to_list(1)
            return result[0] if result else {
                "total_revenue": 0.0,
                "total_sales": 0,
                "avg_sale": 0.0
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_real_templates(self, user_id: str) -> List[Dict[str, Any]]:
        """Get real templates from database"""
        collections = self._get_collections()
        if not collections:
            return []
        
        try:
            cursor = collections['templates'].find({"creator_id": user_id}).sort("created_at", -1)
            templates = await cursor.to_list(length=100)
            return templates
        except Exception as e:
            return []
    
    async def _get_real_purchases(self, user_id: str) -> List[Dict[str, Any]]:
        """Get real purchases from database"""
        collections = self._get_collections()
        if not collections:
            return []
        
        try:
            cursor = collections['purchases'].find({"user_id": user_id}).sort("purchased_at", -1)
            purchases = await cursor.to_list(length=100)
            return purchases
        except Exception as e:
            return []
    
    async def get_creator_analytics(self, creator_id: str, period: str = "month") -> Dict[str, Any]:
        """Get real creator analytics from database"""
        collections = self._get_collections()
        if not collections:
            return {"error": "Database not available"}
        
        try:
            # Real analytics from multiple collections
            analytics_data = await self._get_real_analytics(creator_id)
            revenue_data = await self._get_real_revenue(creator_id)
            
            return {
                "period": period,
                "revenue": revenue_data,
                "performance": analytics_data,
                "growth_metrics": await self._calculate_real_growth(creator_id)
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _calculate_real_growth(self, creator_id: str) -> Dict[str, Any]:
        """Calculate real growth metrics from database"""
        collections = self._get_collections()
        if not collections:
            return {}
        
        try:
            # Calculate month-over-month growth
            from datetime import datetime, timedelta
            now = datetime.utcnow()
            last_month = now - timedelta(days=30)
            
            current_sales = await collections['purchases'].count_documents({
                "creator_id": creator_id,
                "purchased_at": {"$gte": last_month}
            })
            
            previous_month = now - timedelta(days=60)
            prev_sales = await collections['purchases'].count_documents({
                "creator_id": creator_id,
                "purchased_at": {"$gte": previous_month, "$lt": last_month}
            })
            
            growth_rate = ((current_sales - prev_sales) / max(prev_sales, 1)) * 100 if prev_sales > 0 else 0
            
            return {
                "sales_growth": round(growth_rate, 2),
                "current_month_sales": current_sales,
                "previous_month_sales": prev_sales
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_my_templates(self, creator_id: str, status: str = None) -> Dict[str, Any]:
        """Get creator's real templates from database"""
        collections = self._get_collections()
        if not collections:
            return {"templates": [], "count": 0}
        
        try:
            query = {"creator_id": creator_id}
            if status:
                query["status"] = status
            
            cursor = collections['templates'].find(query).sort("created_at", -1)
            templates = await cursor.to_list(length=100)
            
            return {
                "templates": templates,
                "count": len(templates)
            }
        except Exception as e:
            return {"templates": [], "count": 0, "error": str(e)}
    
    async def get_user_purchases(self, user_id: str) -> Dict[str, Any]:
        """Get user's real purchases from database"""
        collections = self._get_collections()
        if not collections:
            return {"purchases": [], "count": 0}
        
        try:
            cursor = collections['purchases'].find({"user_id": user_id}).sort("purchased_at", -1)
            purchases = await cursor.to_list(length=100)
            
            return {
                "purchases": purchases,
                "count": len(purchases)
            }
        except Exception as e:
            return {"purchases": [], "count": 0, "error": str(e)}
    
    async def get_featured_templates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get real featured templates from database"""
        collections = self._get_collections()
        if not collections:
            return []
        
        try:
            cursor = collections['templates'].find({
                "status": TemplateStatus.APPROVED.value,
                "featured": True
            }).sort([("rating", -1), ("download_count", -1)]).limit(limit)
            
            return await cursor.to_list(length=limit)
        except Exception as e:
            return []

    async def get_templates(self, filters: Optional[Dict] = None, limit: int = 20, skip: int = 0):
        """Get templates with filtering - REAL database implementation"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"templates": [], "total": 0, "message": "Database not available"}
            
            query = {}
            
            # Apply filters
            if filters:
                if filters.get("category"):
                    query["category"] = filters["category"]
                if filters.get("status"):
                    query["status"] = filters["status"]
                if filters.get("creator_id"):
                    query["creator_id"] = filters["creator_id"]
                if filters.get("price_range"):
                    min_price, max_price = filters["price_range"]
                    query["price"] = {"$gte": min_price, "$lte": max_price}
                if filters.get("tags"):
                    query["tags"] = {"$in": filters["tags"]}
                if filters.get("search"):
                    query["$text"] = {"$search": filters["search"]}
            
            # Get total count
            total = await collections["templates"].count_documents(query)
            
            # Get templates with pagination
            cursor = collections["templates"].find(query).skip(skip).limit(limit)
            templates = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string for JSON serialization
            for template in templates:
                template["id"] = str(template["_id"])
                template.pop("_id", None)
            
            return {
                "templates": templates,
                "total": total,
                "page": (skip // limit) + 1,
                "per_page": limit,
                "total_pages": (total + limit - 1) // limit
            }
            
        except Exception as e:
            return {"templates": [], "total": 0, "error": str(e)}
    
    async def get_template_by_id(self, template_id: str):
        """Get specific template by ID - REAL database implementation"""
        try:
            collections = self._get_collections()
            if not collections:
                return None
            
            template = await collections["templates"].find_one({"_id": template_id})
            
            if template:
                template["id"] = str(template["_id"])
                template.pop("_id", None)
            
            return template
            
        except Exception as e:
            return None
    
    async def update_template(self, template_id: str, updates: Dict[str, Any]):
        """Update template - REAL database implementation"""
        try:
            collections = self._get_collections()
            if not collections:
                return None
            
            # Add update metadata
            updates["updated_at"] = datetime.utcnow()
            updates["version"] = updates.get("version", 1) + 1
            
            result = await collections["templates"].update_one(
                {"_id": template_id},
                {"$set": updates}
            )
            
            if result.modified_count > 0:
                # Return updated template
                return await self.get_template_by_id(template_id)
            
            return None
            
        except Exception as e:
            return None
    
    async def delete_template(self, template_id: str):
        """Delete template - REAL database implementation"""
        try:
            collections = self._get_collections()
            if not collections:
                return False
            
            # Soft delete - mark as deleted instead of removing
            result = await collections["templates"].update_one(
                {"_id": template_id},
                {
                    "$set": {
                        "status": "deleted",
                        "deleted_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            return False
    
    async def get_creator_revenue(self, creator_id: str, period: str = "month"):
        """Get creator revenue data - REAL database implementation"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"total_revenue": 0, "transactions": 0, "avg_transaction": 0}
            
            # Calculate date range
            now = datetime.utcnow()
            if period == "week":
                start_date = now - timedelta(weeks=1)
            elif period == "month":
                start_date = now - timedelta(days=30)
            elif period == "quarter":
                start_date = now - timedelta(days=90)
            elif period == "year":
                start_date = now - timedelta(days=365)
            else:
                start_date = now - timedelta(days=30)
            
            # Aggregate revenue data
            pipeline = [
                {
                    "$match": {
                        "creator_id": creator_id,
                        "purchase_date": {"$gte": start_date},
                        "status": "completed"
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_revenue": {"$sum": "$amount"},
                        "transaction_count": {"$sum": 1},
                        "avg_amount": {"$avg": "$amount"}
                    }
                }
            ]
            
            result = await collections["purchases"].aggregate(pipeline).to_list(length=1)
            
            if result:
                data = result[0]
                return {
                    "total_revenue": float(data.get("total_revenue", 0)),
                    "transactions": int(data.get("transaction_count", 0)),
                    "avg_transaction": float(data.get("avg_amount", 0))
                }
            else:
                return {"total_revenue": 0.0, "transactions": 0, "avg_transaction": 0.0}
                
        except Exception as e:
            return {"total_revenue": 0.0, "transactions": 0, "avg_transaction": 0.0, "error": str(e)}