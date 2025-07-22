"""
Website Builder Services Business Logic
Professional Mewayz Platform
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database
import uuid

class WebsiteBuilderService:
    """Service for website builder operations"""
    
    @staticmethod
    async def get_user_websites(user_id: str):
        """Get user's websites"""
        db = await get_database()
        
        websites = await db.websites.find({"user_id": user_id}).sort("created_at", -1).to_list(length=None)
        return websites
    
    @staticmethod
    async def create_website(user_id: str, website_data: Dict[str, Any]):
        """Create new website"""
        db = await get_database()
        
        website = {
    "_id": str(uuid.uuid4()),
    "user_id": user_id,
    "name": website_data.get("name"),
    "domain": website_data.get("domain"),
    "template": website_data.get("template", "default"),
    "pages": [
    {
    "id": "home",
    "title": "Home",
    "content": {"sections": []},
    "slug": "/"
    }
    ],
    "settings": {
    "theme": website_data.get("theme", "light"),
    "fonts": website_data.get("fonts", "default"),
    "colors": website_data.get("colors", {}),
    "seo": website_data.get("seo", {})
    },
    "status": "draft",
    "published_at": None,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
    }
        
        result = await db.websites.insert_one(website)
        return website
    
    @staticmethod
    async def get_templates():
        """Get available website templates"""
        templates = [
    {
    "id": "modern-business",
    "name": "Modern Business",
    "category": "business",
    "preview": "modern-business-preview.jpg",
    "features": ["responsive", "contact-forms", "gallery"]
    },
    {
    "id": "portfolio",
    "name": "Portfolio",
    "category": "personal",
    "preview": "portfolio-preview.jpg", 
    "features": ["responsive", "gallery", "blog"]
    },
    {
    "id": "ecommerce",
    "name": "E-commerce",
    "category": "shop",
    "preview": "ecommerce-preview.jpg",
    "features": ["responsive", "product-catalog", "cart", "payment"]
    }
    ]
        return templates

# Global service instance
website_builder_service = WebsiteBuilderService()
