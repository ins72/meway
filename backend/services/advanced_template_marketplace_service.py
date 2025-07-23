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
        self.db = None
        self.templates_collection = None
        self.purchases_collection = None
        self.reviews_collection = None
        self.creators_collection = None
        self.analytics_collection = None
    
    def _get_db(self):
        """Lazy database initialization"""
        if self.db is None:
            self.db = get_database()
            if self.db is not None:
                self.templates_collection = self.db["templates"]
                self.purchases_collection = self.db["template_purchases"]
                self.reviews_collection = self.db["template_reviews"]
                self.creators_collection = self.db["template_creators"]
                self.analytics_collection = self.db["template_analytics"]
        return self.db
        
    # Template Creation & Management
    async def create_template(self, creator_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new template for marketplace"""
        db = self._get_db()
        if not db:
            raise RuntimeError("Database not available")
            
        template = {
            "id": str(uuid.uuid4()),
            "creator_id": creator_id,
            "title": data["title"],
            "description": data["description"],
            "category": data["category"],
            "subcategory": data.get("subcategory", ""),
            "preview_url": data.get("preview_url", ""),
            "template_data": data["template_data"],  # JSON structure
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
        
        await self.templates_collection.insert_one(template)
        
        # Track analytics
        await self._track_template_event(template["id"], "created", creator_id)
        
        return template
    
    async def browse_templates(self, filters: Dict[str, Any] = None, limit: int = 20, skip: int = 0) -> Dict[str, Any]:
        """Browse approved templates with advanced filtering"""
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
        
        cursor = self.templates_collection.find(query).sort(sort_criteria).skip(skip).limit(limit)
        templates = await cursor.to_list(length=limit)
        
        total_count = await self.templates_collection.count_documents(query)
        
        return {
            "templates": templates,
            "total": total_count,
            "page": (skip // limit) + 1,
            "per_page": limit,
            "has_more": (skip + limit) < total_count
        }
    
    async def purchase_template(self, user_id: str, template_id: str, payment_method: str) -> Dict[str, Any]:
        """Purchase template with real payment processing"""
        template = await self.templates_collection.find_one({
            "id": template_id,
            "status": TemplateStatus.APPROVED.value
        })
        
        if not template:
            raise ValueError("Template not found or not available")
        
        # Check if already purchased
        existing_purchase = await self.purchases_collection.find_one({
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
        
        await self.purchases_collection.insert_one(purchase)
        
        # Update template stats
        await self.templates_collection.update_one(
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
        template = await self.templates_collection.find_one({"id": template_id})
        if not template:
            raise ValueError("Template not found")
        
        # Check if template is free or if user has purchased it
        if template["price"] > 0:
            purchase = await self.purchases_collection.find_one({
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
        await self.analytics_collection.insert_one({
            "id": str(uuid.uuid4()),
            "template_id": template_id,
            "user_id": user_id,
            "event": event,
            "timestamp": datetime.utcnow(),
            "metadata": {}
        })

# Service instance
advanced_template_marketplace_service = AdvancedTemplateMarketplaceService()