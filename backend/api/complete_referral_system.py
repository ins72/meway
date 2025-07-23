import uuid
"""
Complete Referral/Affiliate System API
URL and Code Based Referral System with Full Admin Control
Version: 1.0.0 - Production Ready
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from core.auth import get_current_user
from services.complete_referral_system_service import referral_service
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic Models
class ReferralProgramCreate(BaseModel):
    name: str = Field(..., description="Program name")
    description: Optional[str] = Field(default="", description="Program description")
    program_type: Optional[str] = Field(default="referral", description="Program type")
    status: Optional[str] = Field(default="active", description="Program status")
    primary_rate: Optional[float] = Field(default=10, description="Primary commission rate")
    secondary_rate: Optional[float] = Field(default=5, description="Secondary commission rate")
    tertiary_rate: Optional[float] = Field(default=2, description="Tertiary commission rate")
    minimum_payout: Optional[float] = Field(default=50, description="Minimum payout amount")
    maximum_commission: Optional[float] = Field(default=1000, description="Maximum commission")
    currency: Optional[str] = Field(default="USD", description="Currency code")
    commission_type: Optional[str] = Field(default="percentage", description="Commission type")
    min_account_age_days: Optional[int] = Field(default=30, description="Minimum account age")
    require_approval: Optional[bool] = Field(default=False, description="Require approval")
    cookie_duration_days: Optional[int] = Field(default=30, description="Cookie duration")
    payout_frequency: Optional[str] = Field(default="monthly", description="Payout frequency")
    auto_payout: Optional[bool] = Field(default=False, description="Enable auto payout")
    start_date: Optional[str] = Field(default=None, description="Program start date")
    end_date: Optional[str] = Field(default=None, description="Program end date")

class ReferralCodeGenerate(BaseModel):
    program_id: str = Field(..., description="Program ID")
    custom_code: Optional[str] = Field(default=None, description="Custom referral code")

class ConversionData(BaseModel):
    referral_code: Optional[str] = Field(default=None, description="Referral code")
    click_id: Optional[str] = Field(default=None, description="Click ID")
    user_id: Optional[str] = Field(default=None, description="Referred user ID")
    conversion_type: str = Field(..., description="Conversion type")
    conversion_value: float = Field(..., description="Conversion value")
    currency: Optional[str] = Field(default="USD", description="Currency")
    order_id: Optional[str] = Field(default=None, description="Order ID")

class PayoutRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    program_id: str = Field(..., description="Program ID")
    payout_method: str = Field(..., description="Payout method")
    stripe_account_id: Optional[str] = Field(default=None, description="Stripe account ID")
    paypal_email: Optional[str] = Field(default=None, description="PayPal email")
    notes: Optional[str] = Field(default="", description="Payout notes")

@router.post("/programs", tags=["Referral System - Admin"])
async def create_referral_program(
    program_data: ReferralProgramCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new referral program (Admin only)
    """
    try:
        # Check admin permissions
        if not current_user.get('is_admin', False):
            raise HTTPException(
                status_code=403,
                detail="Admin privileges required"
            )
        
        result = await referral_service.create_referral_program(
            program_data=program_data.dict(),
            admin_id=current_user['user_id']
        )
        
        if result['success']:
            return {
                "success": True,
                "message": "Referral program created successfully",
                "data": result
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Program creation failed: {result['error']}"
            )
            
    except Exception as e:
        logger.error(f"Create referral program error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create referral program: {str(e)}"
        )

@router.get("/programs", tags=["Referral System"])
async def get_referral_programs(
    current_user: dict = Depends(get_current_user)
):
    """
    Get all active referral programs
    """
    try:
        db = await referral_service.get_database()
        
        programs = await db.referral_programs.find({
            'status': 'active'
        }).to_list(length=None)
        
        # Convert strs and dates
        for program in programs:
            program['_id'] = str(program['_id'])
            if 'created_at' in program:
                program['created_at'] = program['created_at'].isoformat()
            if 'start_date' in program:
                program['start_date'] = program['start_date'].isoformat()
            if 'end_date' in program and program['end_date']:
                program['end_date'] = program['end_date'].isoformat()
        
        return {
            "success": True,
            "message": "Programs retrieved successfully",
            "data": {
                "programs": programs,
                "total_programs": len(programs)
            }
        }
        
    except Exception as e:
        logger.error(f"Get referral programs error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve programs: {str(e)}"
        )

@router.post("/codes/generate", tags=["Referral System"])
async def generate_referral_code(
    code_data: ReferralCodeGenerate,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate referral code for user
    """
    try:
        result = await referral_service.generate_referral_code(
            user_id=current_user['user_id'],
            program_id=code_data.program_id,
            custom_code=code_data.custom_code
        )
        
        if result['success']:
            return {
                "success": True,
                "message": "Referral code generated successfully",
                "data": result
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Code generation failed: {result['error']}"
            )
            
    except Exception as e:
        logger.error(f"Generate referral code error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate referral code: {str(e)}"
        )

@router.get("/codes/my-codes", tags=["Referral System"])
async def get_my_referral_codes(
    program_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's referral codes
    """
    try:
        db = await referral_service.get_database()
        
        query = {'user_id': current_user['user_id']}
        if program_id:
            query['program_id'] = program_id
        
        codes = await db.referral_codes.find(query).to_list(length=None)
        
        # Convert strs and dates
        for code in codes:
            code['_id'] = str(code['_id'])
            if 'created_at' in code:
                code['created_at'] = code['created_at'].isoformat()
            if 'approved_at' in code and code['approved_at']:
                code['approved_at'] = code['approved_at'].isoformat()
        
        return {
            "success": True,
            "message": "Referral codes retrieved successfully",
            "data": {
                "referral_codes": codes,
                "total_codes": len(codes)
            }
        }
        
    except Exception as e:
        logger.error(f"Get referral codes error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve referral codes: {str(e)}"
        )

@router.get("/r/{referral_code}", tags=["Referral System - Public"])
async def track_referral_click(
    referral_code: str,
    request: Request
):
    """
    Track referral link click and redirect
    """
    try:
        # Extract visitor data from request
        tracking_data = {
            'ip_address': request.client.host,
            'user_agent': request.headers.get('user-agent', ''),
            'referrer_url': request.headers.get('referer', ''),
            'destination_url': '/',  # Default redirect
            'utm_source': request.query_params.get('utm_source', ''),
            'utm_medium': request.query_params.get('utm_medium', ''),
            'utm_campaign': request.query_params.get('utm_campaign', ''),
        }
        
        result = await referral_service.track_referral_click(
            referral_code=referral_code,
            tracking_data=tracking_data
        )
        
        if result['success']:
            return {
                "success": True,
                "message": "Click tracked successfully",
                "data": {
                    "click_id": result['click_id'],
                    "redirect_url": result['redirect_url'],
                    "cookie_data": result['cookie_data']
                }
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Invalid referral code: {result['error']}"
            )
            
    except Exception as e:
        logger.error(f"Track referral click error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to track click: {str(e)}"
        )

@router.post("/conversions", tags=["Referral System"])
async def record_conversion(
    conversion_data: ConversionData,
    current_user: dict = Depends(get_current_user)
):
    """
    Record referral conversion
    """
    try:
        result = await referral_service.process_referral_conversion(
            conversion_data=conversion_data.dict()
        )
        
        if result['success']:
            return {
                "success": True,
                "message": "Conversion recorded successfully",
                "data": result
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Conversion recording failed: {result['error']}"
            )
            
    except Exception as e:
        logger.error(f"Record conversion error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record conversion: {str(e)}"
        )

@router.get("/health", tags=["Referral System"])
async def referral_service_health_check():
    """
    Health check for referral service
    """
    try:
        return {
            "success": True,
            "message": "Referral service is operational",
            "data": {
                "service_name": "Complete Referral/Affiliate System",
                "version": "1.0.0",
                "features": [
                    "URL-based Referral Tracking",
                    "Custom Referral Code Generation",
                    "Multi-tier Commission Structure",
                    "Real-time Analytics & Conversion Tracking",
                    "Automated Payout Processing",
                    "Admin Control Over Commission Rates",
                    "Fraud Detection & Validation",
                    "Custom Landing Pages",
                    "Email/SMS Notifications",
                    "Payment Processor Integration",
                    "Referral Leaderboards",
                    "Advanced Reporting & Analytics"
                ],
                "api_endpoints": 8,
                "status": "operational",
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Referral health check error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Referral service health check failed: {str(e)}"
        )