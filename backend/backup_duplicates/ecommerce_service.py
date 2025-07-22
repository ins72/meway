"""
E-commerce Services Business Logic
Professional Mewayz Platform
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database
import uuid

class EcommerceService:
    """Service for e-commerce operations"""
    
    @staticmethod
    async def get_products(user_id: str):
        """Get user's products"""
        db = await get_database()
        
        products = await db.products.find({"user_id": user_id}).to_list(length=None)
        return products
    
    @staticmethod
    async def create_product(user_id: str, product_data: Dict[str, Any]):
        """Create new product"""
        db = await get_database()
        
        product = {
    "_id": str(uuid.uuid4()),
    "user_id": user_id,
    "name": product_data.get("name"),
    "description": product_data.get("description"),
    "price": product_data.get("price"),
    "category": product_data.get("category"),
    "inventory": product_data.get("inventory", 0),
    "status": "active",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
    }
        
        result = await db.products.insert_one(product)
        return product
    
    @staticmethod
    async def get_orders(user_id: str):
        """Get user's orders"""
        db = await get_database()
        
        orders = await db.orders.find({"seller_id": user_id}).sort("created_at", -1).to_list(length=None)
        return orders

# Global service instance
ecommerce_service = EcommerceService()
