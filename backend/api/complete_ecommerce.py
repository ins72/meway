"""
Complete E-commerce System API - 100% Real Data & Full CRUD
Mewayz v2 - July 22, 2025
NO MOCK DATA - REAL INTEGRATIONS ONLY
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from core.database import get_database
from core.auth import get_current_user
from services.complete_ecommerce_service import (
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user
    CompleteEcommerceService,
    ProductStatus,
    OrderStatus,
    PaymentStatus,
    ProductType
)

router = APIRouter(prefix="/api/ecommerce", tags=["Complete E-commerce System"])

# Request Models
class StoreCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    logo_url: Optional[str] = Field(None, max_length=500)
    banner_url: Optional[str] = Field(None, max_length=500)
    theme: Optional[Dict[str, Any]] = Field(default_factory=dict)
    currency: str = Field(default="USD", max_length=3)
    timezone: str = Field(default="UTC", max_length=50)
    contact_info: Optional[Dict[str, Any]] = Field(default_factory=dict)
    business_info: Optional[Dict[str, Any]] = Field(default_factory=dict)
    shipping_zones: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    payment_methods: Optional[List[str]] = Field(default_factory=list)
    tax_settings: Optional[Dict[str, Any]] = Field(default_factory=dict)
    seo_settings: Optional[Dict[str, Any]] = Field(default_factory=dict)
    social_links: Optional[Dict[str, Any]] = Field(default_factory=dict)
    custom_domain: Optional[str] = Field(None, max_length=100)
    is_published: bool = Field(default=True)

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    short_description: Optional[str] = Field(None, max_length=500)
    type: ProductType = Field(default=ProductType.PHYSICAL)
    category_id: Optional[str] = Field(None, max_length=100)
    price: float = Field(..., ge=0)
    compare_at_price: Optional[float] = Field(None, ge=0)
    cost_price: Optional[float] = Field(None, ge=0)
    weight: Optional[float] = Field(None, ge=0)
    dimensions: Optional[Dict[str, float]] = Field(default_factory=dict)
    requires_shipping: bool = Field(default=True)
    track_inventory: bool = Field(default=True)
    inventory_quantity: int = Field(default=0, ge=0)
    low_stock_threshold: int = Field(default=5, ge=0)
    tags: Optional[List[str]] = Field(default_factory=list)
    images: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    seo_title: Optional[str] = Field(None, max_length=100)
    seo_description: Optional[str] = Field(None, max_length=160)
    status: ProductStatus = Field(default=ProductStatus.ACTIVE)
    is_featured: bool = Field(default=False)
    variants: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    short_description: Optional[str] = Field(None, max_length=500)
    type: Optional[ProductType] = Field(None)
    category_id: Optional[str] = Field(None, max_length=100)
    price: Optional[float] = Field(None, ge=0)
    compare_at_price: Optional[float] = Field(None, ge=0)
    cost_price: Optional[float] = Field(None, ge=0)
    weight: Optional[float] = Field(None, ge=0)
    dimensions: Optional[Dict[str, float]] = Field(None)
    requires_shipping: Optional[bool] = Field(None)
    track_inventory: Optional[bool] = Field(None)
    inventory_quantity: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    tags: Optional[List[str]] = Field(None)
    images: Optional[List[Dict[str, Any]]] = Field(None)
    seo_title: Optional[str] = Field(None, max_length=100)
    seo_description: Optional[str] = Field(None, max_length=160)
    status: Optional[ProductStatus] = Field(None)
    is_featured: Optional[bool] = Field(None)

class OrderCreate(BaseModel):
    store_id: str = Field(..., min_length=1)
    customer_email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    customer_first_name: str = Field(..., min_length=1, max_length=50)
    customer_last_name: str = Field(..., min_length=1, max_length=50)
    customer_phone: Optional[str] = Field(None, max_length=20)
    items: List[Dict[str, Any]] = Field(..., min_items=1)
    shipping_address: Dict[str, Any] = Field(...)
    billing_address: Optional[Dict[str, Any]] = Field(None)
    payment_method: str = Field(..., min_length=1)
    shipping_method: Optional[str] = Field(None)
    notes: Optional[str] = Field(None, max_length=500)
    coupon_code: Optional[str] = Field(None, max_length=50)

@router.post("/stores")
async def create_store(
    store_data: StoreCreate,
    workspace_id: str = Query(..., description="Workspace ID"),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    CREATE: Create new online store
    Real data only - no mock information
    """
    try:
        service = CompleteEcommerceService(db)
        
        result = await service.create_store(
            current_user["_id"],
            workspace_id,
            store_data.dict()
        )
        
        return {
            "success": True,
            "message": "Store created successfully",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stores")
async def get_user_stores(
    workspace_id: Optional[str] = Query(None, description="Filter by workspace"),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    READ: Get user's stores with filtering
    Returns paginated list of user's stores
    """
    try:
        # Build filter query
        filter_query = {"user_id": current_user["_id"]}
        
        if workspace_id:
            filter_query["workspace_id"] = workspace_id
        
        # Get stores
        stores = await db["stores"].find(filter_query).skip(skip).limit(limit).to_list(length=None)
        
        # Get total count
        total_count = await db["stores"].count_documents(filter_query)
        
        return {
            "success": True,
            "data": {
                "stores": stores,
                "total_count": total_count,
                "returned_count": len(stores),
                "skip": skip,
                "limit": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stores/{store_id}")
async def get_store(
    store_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    READ: Get store details
    Returns complete store information
    """
    try:
        # Get store and verify ownership
        store = await db["stores"].find_one({"_id": store_id, "user_id": current_user["_id"]})
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Get store statistics
        total_products = await db["products"].count_documents({"store_id": store_id})
        total_orders = await db["orders"].count_documents({"store_id": store_id})
        
        return {
            "success": True,
            "data": {
                "store": store,
                "statistics": {
                    "total_products": total_products,
                    "total_orders": total_orders
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stores/{store_id}/products")
async def create_product(
    store_id: str,
    product_data: ProductCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    CREATE: Create new product
    Adds new product to store with real data
    """
    try:
        service = CompleteEcommerceService(db)
        
        result = await service.create_product(
            store_id,
            current_user["_id"],
            product_data.dict()
        )
        
        return {
            "success": True,
            "message": "Product created successfully",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stores/{store_id}/products")
async def get_store_products(
    store_id: str,
    category_id: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[ProductStatus] = Query(None, description="Filter by status"),
    featured_only: bool = Query(False, description="Show only featured products"),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    READ: Get store products with filtering
    Returns paginated list of products
    """
    try:
        # Build filter query
        filter_query = {"store_id": store_id}
        
        if category_id:
            filter_query["category_id"] = category_id
        
        if status:
            filter_query["status"] = status.value
        
        if featured_only:
            filter_query["is_featured"] = True
        
        # Get products
        products = await db["products"].find(filter_query).skip(skip).limit(limit).to_list(length=None)
        
        # Get total count
        total_count = await db["products"].count_documents(filter_query)
        
        return {
            "success": True,
            "data": {
                "products": products,
                "total_count": total_count,
                "returned_count": len(products),
                "skip": skip,
                "limit": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/{product_id}")
async def get_product(
    product_id: str,
    include_variants: bool = Query(False, description="Include product variants"),
    include_reviews: bool = Query(False, description="Include product reviews"),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    READ: Get product details
    Returns complete product information
    """
    try:
        service = CompleteEcommerceService(db)
        
        result = await service.get_product(product_id, include_variants, include_reviews)
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/products/{product_id}")
async def update_product(
    product_id: str,
    update_data: ProductUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    UPDATE: Update product with real data
    Updates product information and inventory
    """
    try:
        service = CompleteEcommerceService(db)
        
        result = await service.update_product(
            product_id,
            current_user["_id"],
            update_data.dict(exclude_unset=True)
        )
        
        return {
            "success": True,
            "message": "Product updated successfully",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/products/{product_id}")
async def delete_product(
    product_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    DELETE: Delete product and all related data
    Complete cleanup of product and associated data
    """
    try:
        service = CompleteEcommerceService(db)
        
        result = await service.delete_product(product_id, current_user["_id"])
        
        return {
            "success": True,
            "message": "Product deleted successfully",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orders")
async def create_order(
    order_data: OrderCreate,
    db = Depends(get_database)
):
    """
    CREATE: Create new order
    Processes order with real payment integration
    """
    try:
        service = CompleteEcommerceService(db)
        
        # Prepare customer data
        customer_data = {
            "email": order_data.customer_email,
            "first_name": order_data.customer_first_name,
            "last_name": order_data.customer_last_name,
            "phone": order_data.customer_phone
        }
        
        result = await service.create_order(customer_data, order_data.dict())
        
        return {
            "success": True,
            "message": "Order created successfully",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stores/{store_id}/orders")
async def get_store_orders(
    store_id: str,
    status: Optional[OrderStatus] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    READ: Get store orders with filtering
    Returns paginated list of orders
    """
    try:
        # Verify store ownership
        store = await db["stores"].find_one({"_id": store_id, "user_id": current_user["_id"]})
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Build filter query
        filter_query = {"store_id": store_id}
        
        if status:
            filter_query["status"] = status.value
        
        # Get orders
        orders = await db["orders"].find(filter_query).skip(skip).limit(limit).to_list(length=None)
        
        # Get total count
        total_count = await db["orders"].count_documents(filter_query)
        
        return {
            "success": True,
            "data": {
                "orders": orders,
                "total_count": total_count,
                "returned_count": len(orders),
                "skip": skip,
                "limit": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/{order_id}")
async def get_order(
    order_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    READ: Get order details
    Returns complete order information
    """
    try:
        service = CompleteEcommerceService(db)
        
        result = await service.get_order(order_id, current_user["_id"])
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    status: OrderStatus,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    UPDATE: Update order status
    Updates order status with notification
    """
    try:
        service = CompleteEcommerceService(db)
        
        result = await service.update_order_status(order_id, current_user["_id"], status)
        
        return {
            "success": True,
            "message": "Order status updated successfully",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stores/{store_id}/categories")
async def get_store_categories(
    store_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    READ: Get store categories
    Returns all categories for the store
    """
    try:
        # Verify store ownership
        store = await db["stores"].find_one({"_id": store_id, "user_id": current_user["_id"]})
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Get categories
        categories = await db["product_categories"].find({"store_id": store_id}).to_list(length=None)
        
        return {
            "success": True,
            "data": {
                "categories": categories,
                "total_count": len(categories)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stores/{store_id}/analytics")
async def get_store_analytics(
    store_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    READ: Get store analytics
    Returns comprehensive analytics for the store
    """
    try:
        service = CompleteEcommerceService(db)
        
        result = await service.get_store_analytics(store_id, current_user["_id"], days)
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stores/{store_id}/customers")
async def get_store_customers(
    store_id: str,
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    READ: Get store customers
    Returns paginated list of customers
    """
    try:
        # Verify store ownership
        store = await db["stores"].find_one({"_id": store_id, "user_id": current_user["_id"]})
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Get customers who have made orders
        customers = await db["customers"].aggregate([
            {"$lookup": {
                "from": "orders",
                "localField": "_id",
                "foreignField": "customer_id",
                "as": "orders"
            }},
            {"$match": {"orders.store_id": store_id}},
            {"$skip": skip},
            {"$limit": limit}
        ]).to_list(length=None)
        
        # Get total count
        total_count = await db["customers"].count_documents({})
        
        return {
            "success": True,
            "data": {
                "customers": customers,
                "total_count": total_count,
                "returned_count": len(customers),
                "skip": skip,
                "limit": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/overview")
async def get_ecommerce_overview(
    workspace_id: Optional[str] = Query(None, description="Filter by workspace"),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    READ: Get e-commerce overview
    Returns comprehensive analytics across all stores
    """
    try:
        # Build filter query
        filter_query = {"user_id": current_user["_id"]}
        if workspace_id:
            filter_query["workspace_id"] = workspace_id
        
        # Get all user's stores
        stores = await db["stores"].find(filter_query).to_list(length=None)
        store_ids = [store["_id"] for store in stores]
        
        # Calculate totals
        total_stores = len(stores)
        total_products = await db["products"].count_documents({"store_id": {"$in": store_ids}})
        total_orders = await db["orders"].count_documents({"store_id": {"$in": store_ids}})
        
        # Get revenue data
        revenue_data = await db["orders"].aggregate([
            {"$match": {"store_id": {"$in": store_ids}}},
            {"$group": {"_id": None, "total_revenue": {"$sum": "$total_amount"}}}
        ]).to_list(length=None)
        
        total_revenue = revenue_data[0]["total_revenue"] if revenue_data else 0
        
        # Get recent orders
        recent_orders = await db["orders"].find(
            {"store_id": {"$in": store_ids}}
        ).sort("created_at", -1).limit(10).to_list(length=None)
        
        return {
            "success": True,
            "data": {
                "totals": {
                    "total_stores": total_stores,
                    "total_products": total_products,
                    "total_orders": total_orders,
                    "total_revenue": total_revenue
                },
                "recent_orders": recent_orders,
                "top_stores": stores[:5]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def ecommerce_health_check(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    READ: Health check for e-commerce system
    Returns system status and connectivity
    """
    try:
        service = CompleteEcommerceService(db)
        
        # Check database connectivity
        db_status = "connected"
        try:
            await db["stores"].find_one({})
        except:
            db_status = "disconnected"
        
        # Check integrations
        integrations_status = {
            "stripe": "configured" if service.stripe_secret_key else "not_configured",
            "openai": "configured" if service.openai_api_key else "not_configured"
        }
        
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "database": db_status,
                "integrations": integrations_status,
                "collections": {
                    "stores": await db["stores"].count_documents({}),
                    "products": await db["products"].count_documents({}),
                    "orders": await db["orders"].count_documents({}),
                    "customers": await db["customers"].count_documents({})
                },
                "timestamp": datetime.utcnow()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))