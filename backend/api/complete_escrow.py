import uuid
"""
Complete Escrow System API
Secure Transaction Platform for Digital Assets and Services
Version: 1.0.0 - Production Ready
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from core.auth import get_current_user
from services.complete_escrow_service import escrow_service
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic Models
class EscrowTransactionCreate(BaseModel):
    seller_id: str = Field(..., description="Seller user ID")
    item_title: str = Field(..., description="Item title")
    item_description: str = Field(..., description="Item description")
    amount: float = Field(..., description="Transaction amount")
    currency: str = Field(default="usd", description="Currency code")
    item_type: Optional[str] = Field(default="digital_product", description="Item type")
    category: Optional[str] = Field(default="general", description="Item category")
    delivery_method: Optional[str] = Field(default="digital", description="Delivery method")
    delivery_timeframe: Optional[str] = Field(default="24_hours", description="Delivery timeframe")
    buyer_terms: Optional[List[str]] = Field(default=[], description="Buyer terms")
    seller_terms: Optional[List[str]] = Field(default=[], description="Seller terms")
    delivery_requirements: Optional[List[str]] = Field(default=[], description="Delivery requirements")
    milestones: Optional[List[Dict]] = Field(default=[], description="Milestone payments")

class PaymentConfirmation(BaseModel):
    payment_method_id: str = Field(..., description="Stripe payment method ID")

class DeliverySubmission(BaseModel):
    delivery_method: Optional[str] = Field(default="digital", description="Delivery method")
    delivery_details: Optional[Dict] = Field(default={}, description="Delivery details")
    digital_assets: Optional[List[Dict]] = Field(default=[], description="Digital assets")
    access_credentials: Optional[Dict] = Field(default={}, description="Access credentials")
    notes: Optional[str] = Field(default="", description="Additional notes")

class DeliveryConfirmation(BaseModel):
    rating: Optional[int] = Field(default=None, description="Seller rating 1-5")
    review: Optional[str] = Field(default=None, description="Review text")

class DisputeCreate(BaseModel):
    dispute_type: str = Field(..., description="Dispute type")
    reason: str = Field(..., description="Dispute reason")
    description: str = Field(..., description="Detailed description")
    evidence: Optional[List[Dict]] = Field(default=[], description="Evidence files")
    requested_resolution: Optional[str] = Field(default="refund", description="Requested resolution")

@router.post("/transactions", tags=["Escrow System"])
async def create_escrow_transaction(
    transaction_data: EscrowTransactionCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new escrow transaction with Stripe payment hold
    """
    try:
        result = await escrow_service.create_escrow_transaction(
            transaction_data=transaction_data.dict(),
            buyer_id=current_user['user_id']
        )
        
        if result['success']:
            return {
                "success": True,
                "message": "Escrow transaction created successfully",
                "data": result
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Transaction creation failed: {result['error']}"
            )
            
    except Exception as e:
        logger.error(f"Create escrow transaction error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create escrow transaction: {str(e)}"
        )

@router.post("/transactions/{transaction_id}/fund", tags=["Escrow System"])
async def fund_escrow_transaction(
    transaction_id: str,
    payment_data: PaymentConfirmation,
    current_user: dict = Depends(get_current_user)
):
    """
    Fund escrow transaction by confirming Stripe payment
    """
    try:
        result = await escrow_service.fund_escrow_transaction(
            transaction_id=transaction_id,
            payment_method_id=payment_data.payment_method_id
        )
        
        if result['success']:
            return {
                "success": True,
                "message": "Transaction funded successfully",
                "data": result
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Transaction funding failed: {result['error']}"
            )
            
    except Exception as e:
        logger.error(f"Fund escrow transaction error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fund transaction: {str(e)}"
        )

@router.post("/transactions/{transaction_id}/deliver", tags=["Escrow System"])
async def deliver_item(
    transaction_id: str,
    delivery_data: DeliverySubmission,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark item as delivered by seller
    """
    try:
        result = await escrow_service.deliver_item(
            transaction_id=transaction_id,
            delivery_data=delivery_data.dict(),
            seller_id=current_user['user_id']
        )
        
        if result['success']:
            return {
                "success": True,
                "message": "Item marked as delivered successfully",
                "data": result
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Delivery submission failed: {result['error']}"
            )
            
    except Exception as e:
        logger.error(f"Deliver item error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to mark item as delivered: {str(e)}"
        )

@router.post("/transactions/{transaction_id}/confirm", tags=["Escrow System"])
async def confirm_delivery(
    transaction_id: str,
    confirmation_data: Optional[DeliveryConfirmation] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Buyer confirms receipt and releases funds to seller
    """
    try:
        confirmation_dict = confirmation_data.dict() if confirmation_data else None
        
        result = await escrow_service.confirm_delivery(
            transaction_id=transaction_id,
            buyer_id=current_user['user_id'],
            confirmation_data=confirmation_dict
        )
        
        if result['success']:
            return {
                "success": True,
                "message": "Delivery confirmed and funds released",
                "data": result
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Delivery confirmation failed: {result['error']}"
            )
            
    except Exception as e:
        logger.error(f"Confirm delivery error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to confirm delivery: {str(e)}"
        )

@router.post("/transactions/{transaction_id}/dispute", tags=["Escrow System"])
async def create_dispute(
    transaction_id: str,
    dispute_data: DisputeCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a dispute for a transaction
    """
    try:
        result = await escrow_service.create_dispute(
            transaction_id=transaction_id,
            dispute_data=dispute_data.dict(),
            user_id=current_user['user_id']
        )
        
        if result['success']:
            return {
                "success": True,
                "message": "Dispute created successfully",
                "data": result
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Dispute creation failed: {result['error']}"
            )
            
    except Exception as e:
        logger.error(f"Create dispute error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create dispute: {str(e)}"
        )

@router.get("/transactions/{transaction_id}", tags=["Escrow System"])
async def get_transaction(
    transaction_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get transaction details for authorized user
    """
    try:
        result = await escrow_service.get_transaction(
            transaction_id=transaction_id,
            user_id=current_user['user_id']
        )
        
        if result['success']:
            return {
                "success": True,
                "message": "Transaction retrieved successfully",
                "data": result
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Transaction not found: {result['error']}"
            )
            
    except Exception as e:
        logger.error(f"Get transaction error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve transaction: {str(e)}"
        )

@router.get("/transactions", tags=["Escrow System"])
async def get_user_transactions(
    status: Optional[str] = None,
    role: Optional[str] = None,  # buyer, seller
    page: Optional[int] = 1,
    limit: Optional[int] = 20,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all transactions for a user with filtering
    """
    try:
        filters = {
            'status': status,
            'role': role,
            'page': page,
            'limit': limit,
            'date_from': date_from,
            'date_to': date_to
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        result = await escrow_service.get_user_transactions(
            user_id=current_user['user_id'],
            filters=filters
        )
        
        if result['success']:
            return {
                "success": True,
                "message": "Transactions retrieved successfully",
                "data": result
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve transactions: {result['error']}"
            )
            
    except Exception as e:
        logger.error(f"Get user transactions error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve transactions: {str(e)}"
        )

@router.get("/analytics", tags=["Escrow System"])
async def get_escrow_analytics(
    current_user: dict = Depends(get_current_user)
):
    """
    Get escrow transaction analytics for user
    """
    try:
        db = await escrow_service.get_database()
        
        user_id = current_user['user_id']
        
        # Get transaction counts by status
        pipeline = [
            {'$match': {'$or': [{'buyer_id': user_id}, {'seller_id': user_id}]}},
            {'$group': {
                '_id': '$status',
                'count': {'$sum': 1},
                'total_amount': {'$sum': '$financial_details.amount'}
            }}
        ]
        
        status_stats = await db.escrow_transactions.aggregate(pipeline).to_list(length=None)
        
        # Get total transactions
        total_as_buyer = await db.escrow_transactions.count_documents({'buyer_id': user_id})
        total_as_seller = await db.escrow_transactions.count_documents({'seller_id': user_id})
        
        # Get recent transactions
        recent_transactions = await db.escrow_transactions.find({
            '$or': [{'buyer_id': user_id}, {'seller_id': user_id}]
        }).sort('created_at', -1).limit(5).to_list(length=5)
        
        # Convert strs and dates
        for transaction in recent_transactions:
            transaction['_id'] = str(transaction['_id'])
            if 'created_at' in transaction:
                transaction['created_at'] = transaction['created_at'].isoformat()
        
        # Get user reputation
        reputation = await db.user_reputation.find_one({'user_id': user_id})
        if reputation:
            reputation['_id'] = str(reputation['_id'])
        
        analytics = {
            'user_id': user_id,
            'transaction_summary': {
                'total_as_buyer': total_as_buyer,
                'total_as_seller': total_as_seller,
                'total_transactions': total_as_buyer + total_as_seller
            },
            'status_breakdown': status_stats,
            'recent_transactions': recent_transactions,
            'reputation': reputation,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "message": "Analytics retrieved successfully",
            "data": analytics
        }
        
    except Exception as e:
        logger.error(f"Get escrow analytics error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve analytics: {str(e)}"
        )

@router.get("/categories", tags=["Escrow System"])
async def get_escrow_categories(
    current_user: dict = Depends(get_current_user)
):
    """
    Get available escrow transaction categories
    """
    try:
        categories = [
            {
                'category': 'social_media_accounts',
                'display_name': 'Social Media Accounts',
                'description': 'Instagram, Twitter, TikTok, YouTube accounts',
                'typical_items': ['Instagram accounts', 'Twitter accounts', 'TikTok accounts', 'YouTube channels'],
                'verification_requirements': ['Account access verification', 'Follower authenticity check']
            },
            {
                'category': 'digital_products',
                'display_name': 'Digital Products',
                'description': 'Software, apps, digital content, templates',
                'typical_items': ['Mobile apps', 'Software licenses', 'Digital templates', 'E-books'],
                'verification_requirements': ['Product demonstration', 'Source code review']
            },
            {
                'category': 'websites_domains',
                'display_name': 'Websites & Domains',
                'description': 'Complete websites, domain names, online businesses',
                'typical_items': ['E-commerce websites', 'Premium domains', 'SaaS applications', 'Content websites'],
                'verification_requirements': ['Traffic verification', 'Revenue verification', 'Domain ownership']
            },
            {
                'category': 'services',
                'display_name': 'Professional Services',
                'description': 'Development, design, marketing, consulting services',
                'typical_items': ['Web development', 'Graphic design', 'Marketing campaigns', 'Business consulting'],
                'verification_requirements': ['Portfolio review', 'Client testimonials']
            },
            {
                'category': 'intellectual_property',
                'display_name': 'Intellectual Property',
                'description': 'Patents, trademarks, copyrights, trade secrets',
                'typical_items': ['Patent rights', 'Trademark licenses', 'Copyright assignments', 'Brand assets'],
                'verification_requirements': ['Legal documentation', 'IP ownership verification']
            },
            {
                'category': 'crypto_digital_assets',
                'display_name': 'Crypto & Digital Assets',
                'description': 'Cryptocurrency, NFTs, digital collectibles',
                'typical_items': ['NFT collections', 'Cryptocurrency', 'Digital art', 'Virtual real estate'],
                'verification_requirements': ['Wallet verification', 'Asset authenticity check']
            }
        ]
        
        return {
            "success": True,
            "message": "Categories retrieved successfully",
            "data": {
                "categories": categories,
                "total_categories": len(categories)
            }
        }
        
    except Exception as e:
        logger.error(f"Get categories error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve categories: {str(e)}"
        )

@router.get("/fee-calculator", tags=["Escrow System"])
async def calculate_escrow_fee(
    amount: float,
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate escrow fee for a given amount
    """
    try:
        # Use the same fee calculation logic as the service
        if amount <= 100:
            fee_rate = 0.05  # 5%
        elif amount <= 1000:
            fee_rate = 0.035  # 3.5%
        else:
            fee_rate = 0.025  # 2.5%
        
        escrow_fee = amount * fee_rate
        seller_amount = amount - escrow_fee
        
        fee_info = {
            'transaction_amount': amount,
            'escrow_fee': escrow_fee,
            'fee_rate': fee_rate * 100,  # Convert to percentage
            'seller_receives': seller_amount,
            'fee_structure': {
                'tier_1': {'range': '$0 - $100', 'rate': '5%'},
                'tier_2': {'range': '$101 - $1,000', 'rate': '3.5%'},
                'tier_3': {'range': '$1,001+', 'rate': '2.5%'}
            }
        }
        
        return {
            "success": True,
            "message": "Fee calculated successfully",
            "data": fee_info
        }
        
    except Exception as e:
        logger.error(f"Calculate fee error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate fee: {str(e)}"
        )

@router.get("/health", tags=["Escrow System"])
async def escrow_service_health_check():
    """
    Health check for escrow service
    """
    try:
        return {
            "success": True,
            "message": "Escrow service is operational",
            "data": {
                "service_name": "Complete Escrow System",
                "version": "1.0.0",
                "features": [
                    "Multi-purpose Escrow Transactions",
                    "Stripe Payment Integration with Hold/Release",
                    "Milestone-based Payments",
                    "Dispute Resolution System",
                    "Identity Verification",
                    "Automatic Fund Release",
                    "Transaction History & Audit Trail",
                    "Multi-currency Support",
                    "Real-time Notifications",
                    "User Reputation System"
                ],
                "api_endpoints": 10,
                "status": "operational",
                "supported_categories": [
                    "Social Media Accounts",
                    "Digital Products",
                    "Websites & Domains",
                    "Professional Services",
                    "Intellectual Property",
                    "Crypto & Digital Assets"
                ],
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Escrow health check error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Escrow service health check failed: {str(e)}"
        )

@router.post("/transactions/milestone", tags=["Escrow Transactions"])
async def create_milestone_transaction(
    seller_id: str = Body(...),
    transaction_data: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Create milestone-based escrow transaction"""
    try:
        result = await escrow_service.create_milestone_escrow_transaction(
            buyer_id=current_user["_id"],
            seller_id=seller_id,
            transaction_data=transaction_data
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Milestone escrow transaction created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating milestone transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/disputes/initiate", tags=["Escrow Disputes"])
async def initiate_dispute(
    transaction_id: str = Body(...),
    dispute_data: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Initiate dispute resolution process"""
    try:
        result = await escrow_service.initiate_dispute_comprehensive(
            user_id=current_user["_id"],
            transaction_id=transaction_id,
            dispute_data=dispute_data
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Dispute initiated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error initiating dispute: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transactions", tags=["Escrow Transactions"])
async def get_escrow_transactions(
    status: str = Query(None),
    role: str = Query(None),  # buyer or seller
    current_user: dict = Depends(get_current_user)
):
    """Get user's escrow transactions"""
    try:
        result = await escrow_service.get_user_transactions(
            user_id=current_user["_id"],
            status=status,
            role=role
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Escrow transactions retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting escrow transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fees/calculate", tags=["Escrow Fees"])
async def calculate_escrow_fees(
    amount: float = Body(...),
    transaction_type: str = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Calculate escrow fees for transaction"""
    try:
        result = await escrow_service.calculate_transaction_fees(
            amount=amount,
            transaction_type=transaction_type
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Escrow fees calculated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error calculating escrow fees: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
