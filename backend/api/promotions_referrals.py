"""
Discount Codes & Referral System API Routes
Professional Mewayz Platform - Migrated from Monolithic Structure
High-Value Feature Addition - Complete Promotional & Referral Management
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import secrets
import string

from core.auth import get_current_active_user
from core.database import get_database
from services.user_service import get_user_service
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body

router = APIRouter()

# Initialize service instances
user_service = get_user_service()

class DiscountCodeCreate(BaseModel):
    code: Optional[str] = None  # Auto-generate if not provided
    name: str
    description: Optional[str] = ""
    type: str = "percentage"  # percentage, fixed_amount, free_shipping
    value: float  # Percentage (0-100) or fixed amount
    minimum_purchase_amount: Optional[float] = 0
    maximum_discount_amount: Optional[float] = None
    usage_limit: Optional[int] = None  # Total usage limit
    usage_limit_per_customer: Optional[int] = 1
    starts_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: bool = True

class ReferralProgramCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    referrer_reward_type: str = "percentage"  # percentage, fixed_amount, credits
    referrer_reward_value: float
    referee_reward_type: str = "percentage"
    referee_reward_value: float
    minimum_purchase_amount: Optional[float] = 0
    maximum_referrals_per_user: Optional[int] = None
    expires_at: Optional[datetime] = None
    is_active: bool = True

class ReferralCodeGenerate(BaseModel):
    program_id: str
    custom_code: Optional[str] = None

def get_discount_codes_collection():
    """Get discount codes collection"""
    db = get_database()
    return db.discount_codes

def get_discount_usage_collection():
    """Get discount code usage collection"""
    db = get_database()
    return db.discount_usage

def get_referral_programs_collection():
    """Get referral programs collection"""
    db = get_database()
    return db.referral_programs

def get_referral_codes_collection():
    """Get referral codes collection"""
    db = get_database()
    return db.referral_codes

def get_referral_tracking_collection():
    """Get referral tracking collection"""
    db = get_database()
    return db.referral_tracking

def generate_discount_code(length: int = 8) -> str:
    """Generate random discount code"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def generate_referral_code(user_name: str, length: int = 6) -> str:
    """Generate referral code based on user name"""
    # Use first 3 chars of name + random 3 chars
    name_part = ''.join(c.upper() for c in user_name[:3] if c.isalnum())
    while len(name_part) < 3:
        name_part += 'X'
    
    sequential_part = ''.join(secrets.choice(string.digits) for _ in range(length - 3))
    return name_part + sequential_part

@router.get("/dashboard")
async def get_promotions_dashboard(current_user: dict = Depends(get_current_active_user)):
    """Get promotions and referrals dashboard"""
    try:
        discount_codes_collection = get_discount_codes_collection()
        discount_usage_collection = get_discount_usage_collection()
        referral_programs_collection = get_referral_programs_collection()
        referral_tracking_collection = get_referral_tracking_collection()
        
        # Get discount code stats
        total_discount_codes = await discount_codes_collection.count_documents({
            "created_by": current_user["_id"]
        })
        active_discount_codes = await discount_codes_collection.count_documents({
            "created_by": current_user["_id"],
            "is_active": True
        })
        
        # Get discount code usage stats
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        discount_usage_30d = await discount_usage_collection.count_documents({
            "merchant_id": current_user["_id"],
            "used_at": {"$gte": thirty_days_ago}
        })
        
        # Calculate total savings provided
        savings_pipeline = [
            {"$match": {
                "merchant_id": current_user["_id"],
                "used_at": {"$gte": thirty_days_ago}
            }},
            {"$group": {
                "_id": None,
                "total_savings": {"$sum": "$discount_amount"}
            }}
        ]
        
        savings_result = await discount_usage_collection.aggregate(savings_pipeline).to_list(length=1)
        total_savings = savings_result[0]["total_savings"] if savings_result else 0
        
        # Get referral program stats
        total_referral_programs = await referral_programs_collection.count_documents({
            "created_by": current_user["_id"]
        })
        
        # Get referral success stats
        successful_referrals = await referral_tracking_collection.count_documents({
            "merchant_id": current_user["_id"],
            "status": "completed",
            "created_at": {"$gte": thirty_days_ago}
        })
        
        # Get top performing discount codes
        top_codes_pipeline = [
            {"$match": {"merchant_id": current_user["_id"]}},
            {"$group": {
                "_id": "$discount_code_id",
                "usage_count": {"$sum": 1},
                "total_savings": {"$sum": "$discount_amount"},
                "code_name": {"$first": "$code"}
            }},
            {"$sort": {"usage_count": -1}},
            {"$limit": 5}
        ]
        
        top_codes = await discount_usage_collection.aggregate(top_codes_pipeline).to_list(length=None)
        
        dashboard_data = {
            "overview": {
                "total_discount_codes": total_discount_codes,
                "active_discount_codes": active_discount_codes,
                "discount_usage_30d": discount_usage_30d,
                "total_savings_provided": round(total_savings, 2),
                "total_referral_programs": total_referral_programs,
                "successful_referrals_30d": successful_referrals
            },
            "top_performing_codes": [
                {
                    "code_id": code["_id"],
                    "code": code.get("code_name", "Unknown"),
                    "usage_count": code["usage_count"],
                    "total_savings": round(code["total_savings"], 2)
                } for code in top_codes
            ]
        }
        
        return {
            "success": True,
            "data": dashboard_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch promotions dashboard: {str(e)}"
        )

@router.get("/discount-codes")
async def get_discount_codes(
    status_filter: Optional[str] = None,
    limit: int = 20,
    page: int = 1,
    current_user: dict = Depends(get_current_active_user)
):
    """Get user's discount codes with filtering"""
    try:
        discount_codes_collection = get_discount_codes_collection()
        discount_usage_collection = get_discount_usage_collection()
        
        # Build query
        query = {"created_by": current_user["_id"]}
        
        if status_filter == "active":
            query["is_active"] = True
            query["$or"] = [
                {"expires_at": {"$gt": datetime.utcnow()}},
                {"expires_at": None}
            ]
        elif status_filter == "expired":
            query["expires_at"] = {"$lt": datetime.utcnow()}
        elif status_filter == "inactive":
            query["is_active"] = False
        
        # Get total count
        total_codes = await discount_codes_collection.count_documents(query)
        
        # Get codes with pagination
        skip = (page - 1) * limit
        codes = await discount_codes_collection.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(length=None)
        
        # Enhance codes with usage data
        for code in codes:
            code["id"] = str(code["_id"])
            
            # Get usage count
            usage_count = await discount_usage_collection.count_documents({
                "discount_code_id": code["id"]
            })
            code["usage_count"] = usage_count
            
            # Calculate usage percentage
            if code.get("usage_limit"):
                code["usage_percentage"] = round((usage_count / code["usage_limit"]) * 100, 1)
            else:
                code["usage_percentage"] = 0
            
            # Check if expired
            code["is_expired"] = (
                code.get("expires_at") and code["expires_at"] < datetime.utcnow()
            )
            
            # Calculate total savings provided
            savings_result = await discount_usage_collection.aggregate([
                {"$match": {"discount_code_id": code["id"]}},
                {"$group": {"_id": None, "total": {"$sum": "$discount_amount"}}}
            ]).to_list(length=1)
            
            code["total_savings_provided"] = round(
                savings_result[0]["total"] if savings_result else 0, 2
            )
        
        return {
            "success": True,
            "data": {
                "codes": codes,
                "pagination": {
                    "current_page": page,
                    "total_pages": (total_codes + limit - 1) // limit,
                    "total_codes": total_codes,
                    "has_next": skip + limit < total_codes,
                    "has_prev": page > 1
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch discount codes: {str(e)}"
        )

@router.post("/discount-codes")
async def create_discount_code(
    code_data: DiscountCodeCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create new discount code with validation"""
    try:
        # Check user's discount code creation limits
        user_stats = await user_service.get_user_stats(current_user["_id"])
        user_plan = user_stats["subscription_info"]["plan"]
        
        discount_codes_collection = get_discount_codes_collection()
        existing_codes = await discount_codes_collection.count_documents({
            "created_by": current_user["_id"]
        })
        
        # Plan-based limits
        max_codes = get_discount_code_limit(user_plan)
        if max_codes != -1 and existing_codes >= max_codes:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Discount code limit reached ({max_codes}). Upgrade your plan for more codes."
            )
        
        # Validate discount type and value
        if code_data.type not in ["percentage", "fixed_amount", "free_shipping"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid discount type. Use: percentage, fixed_amount, or free_shipping"
            )
        
        if code_data.type == "percentage" and (code_data.value <= 0 or code_data.value > 100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Percentage discount must be between 0 and 100"
            )
        
        if code_data.type == "fixed_amount" and code_data.value <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fixed amount discount must be positive"
            )
        
        # Generate or validate code
        if code_data.code:
            # Check if code already exists for this user
            existing_code = await discount_codes_collection.find_one({
                "created_by": current_user["_id"],
                "code": code_data.code.upper()
            })
            if existing_code:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Discount code already exists"
                )
            discount_code = code_data.code.upper()
        else:
            # Generate unique code
            attempts = 0
            while attempts < 10:
                discount_code = generate_discount_code()
                existing = await discount_codes_collection.find_one({
                    "created_by": current_user["_id"],
                    "code": discount_code
                })
                if not existing:
                    break
                attempts += 1
            
            if attempts >= 10:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate unique discount code"
                )
        
        # Set default dates
        starts_at = code_data.starts_at or datetime.utcnow()
        expires_at = code_data.expires_at
        
        # Create discount code document
        code_doc = {
            "_id": str(uuid.uuid4()),
            "created_by": current_user["_id"],
            "code": discount_code,
            "name": code_data.name,
            "description": code_data.description,
            "type": code_data.type,
            "value": code_data.value,
            "minimum_purchase_amount": code_data.minimum_purchase_amount,
            "maximum_discount_amount": code_data.maximum_discount_amount,
            "usage_limit": code_data.usage_limit,
            "usage_limit_per_customer": code_data.usage_limit_per_customer,
            "usage_count": 0,
            "starts_at": starts_at,
            "expires_at": expires_at,
            "is_active": code_data.is_active,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Save discount code
        await discount_codes_collection.insert_one(code_doc)
        
        response_code = code_doc.copy()
        response_code["id"] = str(response_code["_id"])
        
        return {
            "success": True,
            "message": "Discount code created successfully",
            "data": response_code
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create discount code: {str(e)}"
        )

@router.post("/discount-codes/{code}/validate")
async def validate_discount_code(
    code: str,
    purchase_amount: float,
    customer_email: Optional[str] = None
):
    """Validate discount code and calculate discount"""
    try:
        discount_codes_collection = get_discount_codes_collection()
        discount_usage_collection = get_discount_usage_collection()
        
        # Find discount code
        discount_code = await discount_codes_collection.find_one({
            "code": code.upper(),
            "is_active": True
        })
        
        if not discount_code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid or inactive discount code"
            )
        
        # Check if code has started
        if discount_code.get("starts_at") and discount_code["starts_at"] > datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount code is not yet active"
            )
        
        # Check if code has expired
        if discount_code.get("expires_at") and discount_code["expires_at"] < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount code has expired"
            )
        
        # Check minimum purchase amount
        min_purchase = discount_code.get("minimum_purchase_amount", 0)
        if purchase_amount < min_purchase:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Minimum purchase amount is ${min_purchase}"
            )
        
        # Check usage limits
        if discount_code.get("usage_limit"):
            if discount_code["usage_count"] >= discount_code["usage_limit"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Discount code usage limit reached"
                )
        
        # Check per-customer usage limit
        if customer_email and discount_code.get("usage_limit_per_customer"):
            customer_usage = await discount_usage_collection.count_documents({
                "discount_code_id": str(discount_code["_id"]),
                "customer_email": customer_email
            })
            
            if customer_usage >= discount_code["usage_limit_per_customer"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Discount code usage limit per customer reached"
                )
        
        # Calculate discount amount
        discount_amount = 0
        if discount_code["type"] == "percentage":
            discount_amount = purchase_amount * (discount_code["value"] / 100)
        elif discount_code["type"] == "fixed_amount":
            discount_amount = discount_code["value"]
        elif discount_code["type"] == "free_shipping":
            discount_amount = 0  # Would calculate shipping cost in real implementation
        
        # Apply maximum discount limit
        if discount_code.get("maximum_discount_amount"):
            discount_amount = min(discount_amount, discount_code["maximum_discount_amount"])
        
        # Ensure discount doesn't exceed purchase amount
        discount_amount = min(discount_amount, purchase_amount)
        
        final_amount = purchase_amount - discount_amount
        
        return {
            "success": True,
            "data": {
                "code": discount_code["code"],
                "name": discount_code["name"],
                "type": discount_code["type"],
                "value": discount_code["value"],
                "original_amount": purchase_amount,
                "discount_amount": round(discount_amount, 2),
                "final_amount": round(final_amount, 2),
                "savings_percentage": round((discount_amount / purchase_amount) * 100, 1)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate discount code: {str(e)}"
        )

@router.get("/referral-programs")
async def get_referral_programs(current_user: dict = Depends(get_current_active_user)):
    """Get user's referral programs"""
    try:
        referral_programs_collection = get_referral_programs_collection()
        referral_tracking_collection = get_referral_tracking_collection()
        
        # Get referral programs
        programs = await referral_programs_collection.find({
            "created_by": current_user["_id"]
        }).sort("created_at", -1).to_list(length=None)
        
        # Enhance programs with statistics
        for program in programs:
            program["id"] = str(program["_id"])
            
            # Get referral statistics
            total_referrals = await referral_tracking_collection.count_documents({
                "program_id": program["id"]
            })
            successful_referrals = await referral_tracking_collection.count_documents({
                "program_id": program["id"],
                "status": "completed"
            })
            
            program["total_referrals"] = total_referrals
            program["successful_referrals"] = successful_referrals
            program["conversion_rate"] = round(
                (successful_referrals / max(total_referrals, 1)) * 100, 1
            )
        
        return {
            "success": True,
            "data": {
                "programs": programs
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch referral programs: {str(e)}"
        )

@router.post("/referral-programs")
async def create_referral_program(
    program_data: ReferralProgramCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create new referral program"""
    try:
        # Validate reward types
        valid_reward_types = ["percentage", "fixed_amount", "credits"]
        if program_data.referrer_reward_type not in valid_reward_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid referrer reward type. Use: {', '.join(valid_reward_types)}"
            )
        
        if program_data.referee_reward_type not in valid_reward_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid referee reward type. Use: {', '.join(valid_reward_types)}"
            )
        
        # Create referral program document
        program_doc = {
            "_id": str(uuid.uuid4()),
            "created_by": current_user["_id"],
            "name": program_data.name,
            "description": program_data.description,
            "referrer_reward_type": program_data.referrer_reward_type,
            "referrer_reward_value": program_data.referrer_reward_value,
            "referee_reward_type": program_data.referee_reward_type,
            "referee_reward_value": program_data.referee_reward_value,
            "minimum_purchase_amount": program_data.minimum_purchase_amount,
            "maximum_referrals_per_user": program_data.maximum_referrals_per_user,
            "expires_at": program_data.expires_at,
            "is_active": program_data.is_active,
            "total_referrals": 0,
            "successful_referrals": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Save referral program
        referral_programs_collection = get_referral_programs_collection()
        await referral_programs_collection.insert_one(program_doc)
        
        response_program = program_doc.copy()
        response_program["id"] = str(response_program["_id"])
        
        return {
            "success": True,
            "message": "Referral program created successfully",
            "data": response_program
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create referral program: {str(e)}"
        )

@router.post("/referral-codes")
async def generate_referral_code(
    code_data: ReferralCodeGenerate,
    current_user: dict = Depends(get_current_active_user)
):
    """Generate referral code for user"""
    try:
        referral_programs_collection = get_referral_programs_collection()
        referral_codes_collection = get_referral_codes_collection()
        
        # Verify program exists and is active
        program = await referral_programs_collection.find_one({
            "_id": code_data.program_id,
            "created_by": current_user["_id"],
            "is_active": True
        })
        
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Referral program not found or inactive"
            )
        
        # Check if user already has a code for this program
        existing_code = await referral_codes_collection.find_one({
            "program_id": code_data.program_id,
            "user_id": current_user["_id"]
        })
        
        if existing_code:
            return {
                "success": True,
                "message": "Referral code already exists",
                "data": {
                    "id": str(existing_code["_id"]),
                    "code": existing_code["code"],
                    "program_name": program["name"],
                    "referral_url": f"/ref/{existing_code['code']}"
                }
            }
        
        # Generate or validate referral code
        if code_data.custom_code:
            referral_code = code_data.custom_code.upper()
            # Check if custom code is available
            existing_custom = await referral_codes_collection.find_one({"code": referral_code})
            if existing_custom:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Custom referral code already exists"
                )
        else:
            # Generate unique code based on user name
            attempts = 0
            while attempts < 10:
                referral_code = generate_referral_code(current_user["name"])
                existing = await referral_codes_collection.find_one({"code": referral_code})
                if not existing:
                    break
                attempts += 1
            
            if attempts >= 10:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate unique referral code"
                )
        
        # Create referral code document
        code_doc = {
            "_id": str(uuid.uuid4()),
            "program_id": code_data.program_id,
            "user_id": current_user["_id"],
            "user_name": current_user["name"],
            "user_email": current_user["email"],
            "code": referral_code,
            "clicks": 0,
            "conversions": 0,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        # Save referral code
        await referral_codes_collection.insert_one(code_doc)
        
        return {
            "success": True,
            "message": "Referral code generated successfully",
            "data": {
                "id": code_doc["_id"],
                "code": referral_code,
                "program_name": program["name"],
                "referral_url": f"/ref/{referral_code}",
                "rewards": {
                    "referrer_reward": f"{program['referrer_reward_value']}{'%' if program['referrer_reward_type'] == 'percentage' else '$' if program['referrer_reward_type'] == 'fixed_amount' else ' credits'}",
                    "referee_reward": f"{program['referee_reward_value']}{'%' if program['referee_reward_type'] == 'percentage' else '$' if program['referee_reward_type'] == 'fixed_amount' else ' credits'}"
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate referral code: {str(e)}"
        )

# Helper functions
def get_discount_code_limit(user_plan: str) -> int:
    """Get discount code creation limit based on user plan"""
    limits = {
        "free": 5,
        "pro": 50,
        "enterprise": -1  # unlimited
    }
    return limits.get(user_plan, 5)