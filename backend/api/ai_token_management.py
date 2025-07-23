"""
AI Token Management System API Routes
Professional Mewayz Platform - Migrated from Monolithic Structure
High-Value Feature Addition - Complete AI Token Economy & Usage Tracking
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import uuid
import stripe
import os

from core.auth import get_current_active_user
from core.database import get_database
from services.user_service import get_user_service
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body

router = APIRouter()

# Initialize service instances
user_service = get_user_service()

# Initialize Stripe
stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
if stripe_secret_key:
    stripe.api_key = stripe_secret_key

class TokenPurchaseRequest(BaseModel):
    package_id: str
    workspace_id: str
    payment_method_id: str

class WorkspaceTokenSettings(BaseModel):
    monthly_token_allowance: int = 50
    auto_purchase_enabled: bool = False
    auto_purchase_threshold: int = 10
    auto_purchase_package_id: Optional[str] = None
    user_limits: Dict[str, int] = {}
    feature_costs: Dict[str, int] = {
        "content_generation": 5,
        "image_generation": 10,
        "seo_analysis": 3,
        "content_analysis": 2,
        "course_generation": 15,
        "email_sequence": 8,
        "hashtag_generation": 2,
        "content_improvement": 4
    }

class TokenConsumptionRequest(BaseModel):
    workspace_id: str
    feature: str
    tokens_needed: int
    description: Optional[str] = ""

def get_token_packages_collection():
    """Get token packages collection"""
    db = get_database()
    return db.token_packages

def get_workspace_tokens_collection():
    """Get workspace tokens collection"""
    db = get_database()
    return db.workspace_tokens

def get_token_transactions_collection():
    """Get token transactions collection"""
    db = get_database()
    return db.token_transactions

def get_workspaces_collection():
    """Get workspaces collection"""
    db = get_database()
    return db.workspaces

def get_team_members_collection():
    """Get team members collection"""
    db = get_database()
    return db.team_members

@router.get("/dashboard")
async def get_token_dashboard(
    workspace_id: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Get comprehensive AI token dashboard"""
    try:
        # Get workspace_id if not provided
        if not workspace_id:
            workspaces_collection = get_workspaces_collection()
            workspace = await workspaces_collection.find_one({"owner_id": current_user["_id"]})
            if not workspace:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No workspace found"
                )
            workspace_id = str(workspace["_id"])
        
        # Verify workspace access
        is_accessible = await verify_workspace_access(workspace_id, current_user["_id"])
        if not is_accessible:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to workspace"
            )
        
        workspace_tokens_collection = get_workspace_tokens_collection()
        token_transactions_collection = get_token_transactions_collection()
        
        # Get workspace tokens
        workspace_tokens = await workspace_tokens_collection.find_one({"workspace_id": workspace_id})
        if not workspace_tokens:
            # Create default token data
            workspace_tokens = await create_default_workspace_tokens(workspace_id)
        
        # Calculate current month usage
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_usage = await token_transactions_collection.aggregate([
            {"$match": {
                "workspace_id": workspace_id,
                "type": "usage",
                "created_at": {"$gte": current_month_start}
            }},
            {"$group": {
                "_id": None,
                "total_tokens": {"$sum": "$tokens"}
            }}
        ]).to_list(length=1)
        
        monthly_usage_total = monthly_usage[0]["total_tokens"] if monthly_usage else 0
        
        # Get feature usage breakdown
        feature_usage = await token_transactions_collection.aggregate([
            {"$match": {
                "workspace_id": workspace_id,
                "type": "usage",
                "created_at": {"$gte": current_month_start}
            }},
            {"$group": {
                "_id": "$feature",
                "tokens_used": {"$sum": "$tokens"},
                "usage_count": {"$sum": 1}
            }},
            {"$sort": {"tokens_used": -1}}
        ]).to_list(length=None)
        
        # Get recent transactions
        recent_transactions = await token_transactions_collection.find(
            {"workspace_id": workspace_id}
        ).sort("created_at", -1).limit(10).to_list(length=None)
        
        # Calculate token efficiency metrics
        total_purchased = workspace_tokens.get("total_purchased", 0)
        total_used = workspace_tokens.get("total_used", 0)
        efficiency_rate = (total_used / max(total_purchased, 1)) * 100 if total_purchased > 0 else 0
        
        # Get user-specific usage if not owner
        workspaces_collection = get_workspaces_collection()
        workspace = await workspaces_collection.find_one({"_id": workspace_id})
        is_owner = workspace and workspace.get("owner_id") == current_user["_id"]
        
        user_monthly_usage = 0
        if not is_owner:
            user_usage = await token_transactions_collection.aggregate([
                {"$match": {
                    "workspace_id": workspace_id,
                    "user_id": current_user["_id"],
                    "type": "usage",
                    "created_at": {"$gte": current_month_start}
                }},
                {"$group": {
                    "_id": None,
                    "total_tokens": {"$sum": "$tokens"}
                }}
            ]).to_list(length=1)
            
            user_monthly_usage = user_usage[0]["total_tokens"] if user_usage else 0
        
        dashboard_data = {
            "workspace_id": workspace_id,
            "is_owner": is_owner,
            "current_balance": {
                "purchased_tokens": workspace_tokens.get("balance", 0),
                "monthly_allowance": workspace_tokens.get("monthly_allowance", 50),
                "allowance_used": workspace_tokens.get("allowance_used_this_month", 0),
                "allowance_remaining": max(0, workspace_tokens.get("monthly_allowance", 50) - workspace_tokens.get("allowance_used_this_month", 0)),
                "total_available": workspace_tokens.get("balance", 0) + max(0, workspace_tokens.get("monthly_allowance", 50) - workspace_tokens.get("allowance_used_this_month", 0))
            },
            "usage_statistics": {
                "total_purchased": total_purchased,
                "total_used": total_used,
                "monthly_usage": monthly_usage_total,
                "user_monthly_usage": user_monthly_usage,
                "efficiency_rate": round(efficiency_rate, 1),
                "avg_daily_usage": round(monthly_usage_total / max(datetime.utcnow().day, 1), 1)
            },
            "feature_usage_breakdown": [
                {
                    "feature": usage["_id"] or "Unknown",
                    "tokens_used": usage["tokens_used"],
                    "usage_count": usage["usage_count"],
                    "avg_tokens_per_use": round(usage["tokens_used"] / max(usage["usage_count"], 1), 1)
                } for usage in feature_usage
            ],
            "settings": {
                "auto_purchase_enabled": workspace_tokens.get("auto_purchase_enabled", False),
                "auto_purchase_threshold": workspace_tokens.get("auto_purchase_threshold", 10),
                "user_limit": workspace_tokens.get("user_limits", {}).get(current_user["_id"]),
                "feature_costs": workspace_tokens.get("feature_costs", {})
            },
            "recent_transactions": [
                {
                    "id": str(tx["_id"]),
                    "type": tx["type"],
                    "tokens": tx["tokens"],
                    "feature": tx.get("feature", "N/A"),
                    "description": tx.get("description", ""),
                    "created_at": tx["created_at"]
                } for tx in recent_transactions
            ]
        }
        
        return {
            "success": True,
            "data": dashboard_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch token dashboard: {str(e)}"
        )

@router.get("/packages")
async def get_token_packages():
    """Get available token packages for purchase"""
    try:
        token_packages_collection = get_token_packages_collection()
        packages = await token_packages_collection.find({}).to_list(length=100)
        
        # If no packages exist, create default ones
        if not packages:
            default_packages = [
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Starter Pack",
                    "tokens": 100,
                    "price": 9.99,
                    "currency": "USD",
                    "bonus_tokens": 10,
                    "description": "Perfect for getting started with AI features",
                    "is_popular": False,
                    "created_at": datetime.utcnow()
                },
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Professional Pack",
                    "tokens": 500,
                    "price": 39.99,
                    "currency": "USD",
                    "bonus_tokens": 75,
                    "description": "Great for professional use and small teams",
                    "is_popular": True,
                    "created_at": datetime.utcnow()
                },
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Enterprise Pack",
                    "tokens": 1500,
                    "price": 99.99,
                    "currency": "USD",
                    "bonus_tokens": 300,
                    "description": "Maximum value for heavy AI users and large teams",
                    "is_popular": False,
                    "created_at": datetime.utcnow()
                }
            ]
            
            await token_packages_collection.insert_many(default_packages)
            packages = default_packages
        
        # Format packages for response
        formatted_packages = []
        for pkg in packages:
            formatted_pkg = {
                "id": str(pkg["_id"]),
                "name": pkg["name"],
                "tokens": pkg["tokens"],
                "price": pkg["price"],
                "currency": pkg["currency"],
                "bonus_tokens": pkg["bonus_tokens"],
                "total_tokens": pkg["tokens"] + pkg["bonus_tokens"],
                "description": pkg.get("description"),
                "is_popular": pkg.get("is_popular", False),
                "per_token_price": round(pkg["price"] / pkg["tokens"], 4),
                "savings": round(((pkg["bonus_tokens"] / pkg["tokens"]) * 100), 1) if pkg["bonus_tokens"] > 0 else 0
            }
            formatted_packages.append(formatted_pkg)
        
        return {
            "success": True,
            "data": {
                "packages": formatted_packages,
                "currency": "USD",
                "payment_methods": ["card", "bank_transfer"],
                "auto_purchase_available": True
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch token packages: {str(e)}"
        )

@router.get("/workspace/{workspace_id}/balance")
async def get_workspace_tokens(
    workspace_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get token balance and settings for a workspace"""
    try:
        # Verify workspace access
        is_accessible = await verify_workspace_access(workspace_id, current_user["_id"])
        if not is_accessible:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to workspace"
            )
        
        workspace_tokens_collection = get_workspace_tokens_collection()
        token_transactions_collection = get_token_transactions_collection()
        
        # Get workspace token data
        workspace_tokens = await workspace_tokens_collection.find_one({"workspace_id": workspace_id})
        if not workspace_tokens:
            workspace_tokens = await create_default_workspace_tokens(workspace_id)
        
        # Get recent transactions
        recent_transactions = await token_transactions_collection.find(
            {"workspace_id": workspace_id}
        ).sort("created_at", -1).limit(10).to_list(length=None)
        
        # Calculate monthly usage
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_usage = await token_transactions_collection.aggregate([
            {"$match": {
                "workspace_id": workspace_id,
                "type": "usage",
                "created_at": {"$gte": current_month_start}
            }},
            {"$group": {
                "_id": None,
                "total_tokens": {"$sum": "$tokens"}
            }}
        ]).to_list(length=1)
        
        monthly_usage_total = monthly_usage[0]["total_tokens"] if monthly_usage else 0
        
        # Check if user is owner
        workspaces_collection = get_workspaces_collection()
        workspace = await workspaces_collection.find_one({"_id": workspace_id})
        is_owner = workspace and workspace.get("owner_id") == current_user["_id"]
        
        # Get user's individual limit if set
        user_limit = workspace_tokens.get("user_limits", {}).get(current_user["_id"], None)
        
        token_data = {
            "workspace_id": workspace_id,
            "balance": workspace_tokens.get("balance", 0),
            "monthly_allowance": workspace_tokens.get("monthly_allowance", 50),
            "allowance_used_this_month": workspace_tokens.get("allowance_used_this_month", 0),
            "allowance_remaining": max(0, workspace_tokens.get("monthly_allowance", 50) - workspace_tokens.get("allowance_used_this_month", 0)),
            "total_purchased": workspace_tokens.get("total_purchased", 0),
            "total_used": workspace_tokens.get("total_used", 0),
            "monthly_usage": monthly_usage_total,
            "auto_purchase_enabled": workspace_tokens.get("auto_purchase_enabled", False),
            "auto_purchase_threshold": workspace_tokens.get("auto_purchase_threshold", 10),
            "feature_costs": workspace_tokens.get("feature_costs", {}),
            "user_limit": user_limit,
            "is_owner": is_owner,
            "recent_transactions": [
                {
                    "id": str(tx["_id"]),
                    "type": tx["type"],
                    "tokens": tx["tokens"],
                    "feature": tx.get("feature"),
                    "description": tx.get("description"),
                    "created_at": tx["created_at"]
                } for tx in recent_transactions
            ]
        }
        
        return {
            "success": True,
            "data": token_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch workspace tokens: {str(e)}"
        )

@router.post("/purchase")
async def purchase_tokens(
    purchase_request: TokenPurchaseRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Purchase tokens for a workspace with Stripe integration"""
    try:
        if not stripe_secret_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Payment processing not configured"
            )
        
        # Verify workspace ownership
        workspaces_collection = get_workspaces_collection()
        workspace = await workspaces_collection.find_one({"_id": purchase_request.workspace_id})
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        if workspace.get("owner_id") != current_user["_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only workspace owners can purchase tokens"
            )
        
        # Get token package
        token_packages_collection = get_token_packages_collection()
        package = await token_packages_collection.find_one({"_id": purchase_request.package_id})
        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Token package not found"
            )
        
        # Create Stripe payment intent
        payment_intent = stripe.PaymentIntent.create(
            amount=int(package["price"] * 100),  # Convert to cents
            currency=package["currency"].lower(),
            payment_method=purchase_request.payment_method_id,
            confirmation_method="manual",
            confirm=True,
            description=f"Token Purchase: {package['name']}",
            metadata={
                "workspace_id": purchase_request.workspace_id,
                "user_id": current_user["_id"],
                "package_id": purchase_request.package_id,
                "tokens": package["tokens"],
                "bonus_tokens": package["bonus_tokens"]
            }
        )
        
        if payment_intent.status == "succeeded":
            # Add tokens to workspace
            total_tokens = package["tokens"] + package["bonus_tokens"]
            
            workspace_tokens_collection = get_workspace_tokens_collection()
            await workspace_tokens_collection.update_one(
                {"workspace_id": purchase_request.workspace_id},
                {
                    "$inc": {
                        "balance": total_tokens,
                        "total_purchased": total_tokens
                    },
                    "$set": {
                        "updated_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            # Record transaction
            token_transactions_collection = get_token_transactions_collection()
            transaction_doc = {
                "_id": str(uuid.uuid4()),
                "workspace_id": purchase_request.workspace_id,
                "user_id": current_user["_id"],
                "type": "purchase",
                "tokens": total_tokens,
                "cost": package["price"],
                "description": f"Purchased {package['name']} - {package['tokens']} tokens + {package['bonus_tokens']} bonus",
                "payment_intent_id": payment_intent.id,
                "created_at": datetime.utcnow()
            }
            await token_transactions_collection.insert_one(transaction_doc)
            
            return {
                "success": True,
                "message": "Tokens purchased successfully",
                "data": {
                    "tokens_added": total_tokens,
                    "payment_intent_id": payment_intent.id,
                    "transaction_id": str(transaction_doc["_id"]),
                    "package_name": package["name"]
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment failed with status: {payment_intent.status}"
            )
            
    except stripe.error.CardError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Card error: {e.user_message}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token purchase failed: {str(e)}"
        )

@router.post("/consume")
async def consume_tokens(
    consumption_request: TokenConsumptionRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Internal endpoint to consume tokens for AI features"""
    try:
        # Verify workspace access
        is_accessible = await verify_workspace_access(consumption_request.workspace_id, current_user["_id"])
        if not is_accessible:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to workspace"
            )
        
        workspace_tokens_collection = get_workspace_tokens_collection()
        token_transactions_collection = get_token_transactions_collection()
        
        # Get workspace tokens
        workspace_tokens = await workspace_tokens_collection.find_one({"workspace_id": consumption_request.workspace_id})
        if not workspace_tokens:
            workspace_tokens = await create_default_workspace_tokens(consumption_request.workspace_id)
        
        # Check user limits
        user_limit = workspace_tokens.get("user_limits", {}).get(current_user["_id"])
        if user_limit is not None and user_limit < consumption_request.tokens_needed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User token limit exceeded. Limit: {user_limit}, Needed: {consumption_request.tokens_needed}"
            )
        
        # Check if workspace has enough tokens
        current_balance = workspace_tokens.get("balance", 0)
        allowance_remaining = max(0, workspace_tokens.get("monthly_allowance", 50) - workspace_tokens.get("allowance_used_this_month", 0))
        total_available = current_balance + allowance_remaining
        
        if total_available < consumption_request.tokens_needed:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient tokens. Available: {total_available}, Needed: {consumption_request.tokens_needed}"
            )
        
        # Consume tokens (prefer monthly allowance first, then purchased balance)
        if allowance_remaining >= consumption_request.tokens_needed:
            # Use monthly allowance
            await workspace_tokens_collection.update_one(
                {"workspace_id": consumption_request.workspace_id},
                {
                    "$inc": {
                        "allowance_used_this_month": consumption_request.tokens_needed,
                        "total_used": consumption_request.tokens_needed
                    },
                    "$set": {
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            token_source = "monthly_allowance"
        else:
            # Use combination of allowance and purchased tokens
            purchased_tokens_used = consumption_request.tokens_needed - allowance_remaining
            
            await workspace_tokens_collection.update_one(
                {"workspace_id": consumption_request.workspace_id},
                {
                    "$inc": {
                        "allowance_used_this_month": allowance_remaining,
                        "balance": -purchased_tokens_used,
                        "total_used": consumption_request.tokens_needed
                    },
                    "$set": {
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            token_source = "mixed"
        
        # Record transaction
        transaction_doc = {
            "_id": str(uuid.uuid4()),
            "workspace_id": consumption_request.workspace_id,
            "user_id": current_user["_id"],
            "type": "usage",
            "tokens": consumption_request.tokens_needed,
            "feature": consumption_request.feature,
            "description": consumption_request.description or f"Used {consumption_request.tokens_needed} tokens for {consumption_request.feature}",
            "token_source": token_source,
            "created_at": datetime.utcnow()
        }
        await token_transactions_collection.insert_one(transaction_doc)
        
        return {
            "success": True,
            "message": "Tokens consumed successfully",
            "data": {
                "tokens_consumed": consumption_request.tokens_needed,
                "feature": consumption_request.feature,
                "token_source": token_source,
                "transaction_id": str(transaction_doc["_id"])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to consume tokens: {str(e)}"
        )

@router.put("/workspace/{workspace_id}/settings")
async def update_workspace_token_settings(
    workspace_id: str,
    settings: WorkspaceTokenSettings,
    current_user: dict = Depends(get_current_active_user)
):
    """Update token settings for a workspace (owner only)"""
    try:
        # Verify workspace ownership
        workspaces_collection = get_workspaces_collection()
        workspace = await workspaces_collection.find_one({"_id": workspace_id})
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        if workspace.get("owner_id") != current_user["_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only workspace owners can update token settings"
            )
        
        # Update workspace token settings
        workspace_tokens_collection = get_workspace_tokens_collection()
        await workspace_tokens_collection.update_one(
            {"workspace_id": workspace_id},
            {
                "$set": {
                    "monthly_allowance": settings.monthly_token_allowance,
                    "auto_purchase_enabled": settings.auto_purchase_enabled,
                    "auto_purchase_threshold": settings.auto_purchase_threshold,
                    "auto_purchase_package_id": settings.auto_purchase_package_id,
                    "user_limits": settings.user_limits,
                    "feature_costs": settings.feature_costs,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return {
            "success": True,
            "message": "Token settings updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update token settings: {str(e)}"
        )

@router.get("/analytics/{workspace_id}")
async def get_token_analytics(
    workspace_id: str,
    days: int = 30,
    current_user: dict = Depends(get_current_active_user)
):
    """Get detailed token usage analytics"""
    try:
        # Verify workspace access
        is_accessible = await verify_workspace_access(workspace_id, current_user["_id"])
        if not is_accessible:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to workspace"
            )
        
        token_transactions_collection = get_token_transactions_collection()
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get usage analytics
        usage_pipeline = [
            {"$match": {
                "workspace_id": workspace_id,
                "type": "usage",
                "created_at": {"$gte": start_date, "$lte": end_date}
            }},
            {"$group": {
                "_id": {
                    "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                    "feature": "$feature"
                },
                "tokens": {"$sum": "$tokens"},
                "usage_count": {"$sum": 1}
            }},
            {"$sort": {"_id.date": 1}}
        ]
        
        usage_data = await token_transactions_collection.aggregate(usage_pipeline).to_list(length=None)
        
        # Get top users (if owner viewing)
        workspaces_collection = get_workspaces_collection()
        workspace = await workspaces_collection.find_one({"_id": workspace_id})
        is_owner = workspace and workspace.get("owner_id") == current_user["_id"]
        
        top_users = []
        if is_owner:
            user_pipeline = [
                {"$match": {
                    "workspace_id": workspace_id,
                    "type": "usage",
                    "created_at": {"$gte": start_date, "$lte": end_date}
                }},
                {"$group": {
                    "_id": "$user_id",
                    "tokens_used": {"$sum": "$tokens"},
                    "usage_count": {"$sum": 1}
                }},
                {"$sort": {"tokens_used": -1}},
                {"$limit": 10}
            ]
            
            top_users = await token_transactions_collection.aggregate(user_pipeline).to_list(length=None)
        
        analytics_data = {
            "workspace_id": workspace_id,
            "period_days": days,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "daily_usage": usage_data,
            "top_users": top_users if is_owner else [],
            "is_owner_view": is_owner
        }
        
        return {
            "success": True,
            "data": analytics_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch token analytics: {str(e)}"
        )

# Helper functions
async def verify_workspace_access(workspace_id: str, user_id: str) -> bool:
    """Verify user has access to workspace"""
    try:
        workspaces_collection = get_workspaces_collection()
        team_members_collection = get_team_members_collection()
        
        # Check if user is workspace owner
        workspace = await workspaces_collection.find_one({
            "_id": workspace_id,
            "owner_id": user_id
        })
        if workspace:
            return True
        
        # Check if user is team member
        member = await team_members_collection.find_one({
            "workspace_id": workspace_id,
            "user_id": user_id,
            "status": "active"
        })
        return bool(member)
        
    except Exception:
        return False

async def create_default_workspace_tokens(workspace_id: str) -> dict:
    """Create default token data for workspace"""
    try:
        workspace_tokens_collection = get_workspace_tokens_collection()
        
        default_tokens = {
            "_id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "balance": 0,
            "total_purchased": 0,
            "total_used": 0,
            "monthly_allowance": 50,
            "allowance_used_this_month": 0,
            "allowance_reset_date": datetime.utcnow().replace(day=1) + timedelta(days=32),
            "auto_purchase_enabled": False,
            "auto_purchase_threshold": 10,
            "user_limits": {},
            "feature_costs": {
                "content_generation": 5,
                "image_generation": 10,
                "seo_analysis": 3,
                "content_analysis": 2,
                "course_generation": 15,
                "email_sequence": 8,
                "hashtag_generation": 2,
                "content_improvement": 4
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await workspace_tokens_collection.insert_one(default_tokens)
        return default_tokens
        
    except Exception as e:
        print(f"Failed to create default workspace tokens: {e}")
        return {}