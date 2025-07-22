"""
E-commerce API Routes
Professional Mewayz Platform - Migrated from Monolithic Structure
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
from decimal import Decimal

from core.auth import get_current_active_user
from core.database import get_database
from services.user_service import get_user_service
from services.analytics_service import get_analytics_service

router = APIRouter()

# Initialize service instances
user_service = get_user_service()
analytics_service = get_analytics_service()

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: Optional[str] = "general"
    images: Optional[List[str]] = []
    inventory_count: Optional[int] = 0
    is_digital: bool = False

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    images: Optional[List[str]] = None
    inventory_count: Optional[int] = None
    is_active: Optional[bool] = None

def get_products_collection():
    """Get products collection"""
    db = get_database()
    return db.products

def get_orders_collection():
    """Get orders collection"""
    db = get_database()
    return db.orders

@router.get("/products")
async def get_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 20,
    page: int = 1,
    current_user: dict = Depends(get_current_active_user)
):
    """Get products with real database operations"""
    try:
        products_collection = get_products_collection()
        
        # Build query
        query = {"user_id": current_user["_id"], "is_active": True}
        if category:
            query["category"] = category
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Get products
        products = await products_collection.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(length=None)
        total_products = await products_collection.count_documents(query)
        
        # Calculate analytics for each product
        for product in products:
            # Get product analytics
            product_analytics = await get_product_analytics(product["_id"])
            product["analytics"] = product_analytics
        
        return {
            "success": True,
            "data": {
                "products": products,
                "pagination": {
                    "current_page": page,
                    "total_pages": (total_products + limit - 1) // limit,
                    "total_products": total_products,
                    "has_next": skip + limit < total_products,
                    "has_prev": page > 1
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch products: {str(e)}"
        )

@router.post("/products")
async def create_product(
    product_data: ProductCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create product with real database operations"""
    try:
        # Check user's plan limits
        user_stats = await user_service.get_user_stats(current_user["_id"])
        user_plan = user_stats["subscription_info"]["plan"]
        
        # Count existing products
        products_collection = get_products_collection()
        existing_products = await products_collection.count_documents({"user_id": current_user["_id"]})
        
        # Check limits
        max_products = 5 if user_plan == "free" else 50 if user_plan == "pro" else -1  # unlimited for enterprise
        if max_products != -1 and existing_products >= max_products:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product limit reached ({max_products}). Upgrade your plan to add more products."
            )
        
        # Create product document
        product_doc = {
            "_id": str(uuid.uuid4()),
            "user_id": current_user["_id"],
            "name": product_data.name,
            "description": product_data.description,
            "price": product_data.price,
            "category": product_data.category,
            "images": product_data.images,
            "inventory_count": product_data.inventory_count,
            "is_digital": product_data.is_digital,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "analytics": {
                "views": 0,
                "purchases": 0,
                "revenue": 0.0
            }
        }
        
        # Save to database
        await products_collection.insert_one(product_doc)
        
        return {
            "success": True,
            "message": "Product created successfully",
            "data": product_doc
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create product: {str(e)}"
        )

@router.get("/orders")
async def get_orders(
    status_filter: Optional[str] = None,
    limit: int = 20,
    page: int = 1,
    current_user: dict = Depends(get_current_active_user)
):
    """Get orders with real database operations"""
    try:
        orders_collection = get_orders_collection()
        
        # Build query
        query = {"seller_id": current_user["_id"]}
        if status_filter:
            query["status"] = status_filter
        
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Get orders
        orders = await orders_collection.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(length=None)
        total_orders = await orders_collection.count_documents(query)
        
        return {
            "success": True,
            "data": {
                "orders": orders,
                "pagination": {
                    "current_page": page,
                    "total_pages": (total_orders + limit - 1) // limit,
                    "total_orders": total_orders,
                    "has_next": skip + limit < total_orders,
                    "has_prev": page > 1
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch orders: {str(e)}"
        )

@router.get("/dashboard")
async def get_ecommerce_dashboard(current_user: dict = Depends(get_current_active_user)):
    """Get e-commerce dashboard with real database calculations"""
    try:
        products_collection = get_products_collection()
        orders_collection = get_orders_collection()
        
        # Get real metrics
        total_products = await products_collection.count_documents({"user_id": current_user["_id"]})
        active_products = await products_collection.count_documents({"user_id": current_user["_id"], "is_active": True})
        total_orders = await orders_collection.count_documents({"seller_id": current_user["_id"]})
        
        # Calculate revenue
        revenue_pipeline = [
            {"$match": {"seller_id": current_user["_id"], "status": {"$in": ["completed", "delivered"]}}},
            {"$group": {
                "_id": None,
                "total_revenue": {"$sum": "$total_amount"},
                "avg_order_value": {"$avg": "$total_amount"}
            }}
        ]
        
        revenue_stats = await orders_collection.aggregate(revenue_pipeline).to_list(length=1)
        revenue_data = revenue_stats[0] if revenue_stats else {"total_revenue": 0, "avg_order_value": 0}
        
        # Get recent orders
        recent_orders = await orders_collection.find(
            {"seller_id": current_user["_id"]},
            {"customer_name": 1, "total_amount": 1, "status": 1, "created_at": 1}
        ).sort("created_at", -1).limit(5).to_list(length=None)
        
        # Get top-selling products
        top_products_pipeline = [
            {"$match": {"seller_id": current_user["_id"]}},
            {"$unwind": "$items"},
            {"$group": {
                "_id": "$items.product_id",
                "total_sold": {"$sum": "$items.quantity"},
                "revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}}
            }},
            {"$sort": {"total_sold": -1}},
            {"$limit": 5}
        ]
        
        top_products_data = await orders_collection.aggregate(top_products_pipeline).to_list(length=None)
        
        # Enhance top products with product details
        for product_stat in top_products_data:
            product = await products_collection.find_one({"_id": product_stat["_id"]})
            if product:
                product_stat["name"] = product["name"]
                product_stat["price"] = product["price"]
        
        dashboard_data = {
            "overview": {
                "total_products": total_products,
                "active_products": active_products,
                "total_orders": total_orders,
                "total_revenue": round(revenue_data["total_revenue"], 2),
                "avg_order_value": round(revenue_data["avg_order_value"], 2)
            },
            "recent_orders": recent_orders,
            "top_products": top_products_data,
            "performance_metrics": {
                "conversion_rate": 0.0,  # Would be calculated from actual analytics
                "repeat_customer_rate": 0.0,  # Would be calculated from customer data
                "inventory_turnover": 0.0  # Would be calculated from sales data
            }
        }
        
        return {
            "success": True,
            "data": dashboard_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch e-commerce dashboard: {str(e)}"
        )

@router.put("/products/{product_id}")
async def update_product(
    product_id: str,
    update_data: ProductUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Update product with real database operations"""
    try:
        products_collection = get_products_collection()
        
        # Find product
        product = await products_collection.find_one({
            "_id": product_id,
            "user_id": current_user["_id"]
        })
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Prepare update document
        update_doc = {
            "$set": {
                "updated_at": datetime.utcnow()
            }
        }
        
        # Update allowed fields
        update_fields = update_data.dict(exclude_none=True)
        for field, value in update_fields.items():
            update_doc["$set"][field] = value
        
        # Update product
        result = await products_collection.update_one(
            {"_id": product_id},
            update_doc
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No changes made"
            )
        
        # Return updated product
        updated_product = await products_collection.find_one({"_id": product_id})
        
        return {
            "success": True,
            "message": "Product updated successfully",
            "data": updated_product
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update product: {str(e)}"
        )

# Helper functions
async def get_product_analytics(product_id: str) -> Dict[str, Any]:
    """Get product analytics - would integrate with real analytics"""
    orders_collection = get_orders_collection()
    
    # Get order data for this product
    orders_with_product = await orders_collection.find({
        "items.product_id": product_id,
        "status": {"$in": ["completed", "delivered"]}
    }).to_list(length=None)
    
    total_sold = 0
    total_revenue = 0.0
    
    for order in orders_with_product:
        for item in order.get("items", []):
            if item.get("product_id") == product_id:
                total_sold += item.get("quantity", 0)
                total_revenue += item.get("quantity", 0) * item.get("price", 0)
    
    return {
        "total_sold": total_sold,
        "total_revenue": round(total_revenue, 2),
        "views": 0,  # Would be tracked from actual page views
        "conversion_rate": 0.0  # Would be calculated from views vs purchases
    }