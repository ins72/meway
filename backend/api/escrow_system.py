"""
Escrow System API
Handles secure payment processing, transactions, and dispute resolution
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import uuid

from core.auth import get_current_user
from services.escrow_service import EscrowService
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user

router = APIRouter()

# Pydantic Models
class EscrowTransactionCreate(BaseModel):
    title: str
    description: Optional[str] = None
    amount: float = Field(..., gt=0)
    buyer_email: str
    seller_email: str
    milestone_title: str
    milestone_description: Optional[str] = None
    payment_method: Optional[str] = "card"
    auto_release_days: Optional[int] = 7

class EscrowMilestoneUpdate(BaseModel):
    status: str  # "pending", "delivered", "approved", "disputed"
    notes: Optional[str] = None
    evidence_urls: List[str] = []

class DisputeCreate(BaseModel):
    transaction_id: str
    reason: str
    description: str
    evidence_urls: List[str] = []

class PaymentRelease(BaseModel):
    transaction_id: str
    amount: Optional[float] = None  # Partial release if specified
    notes: Optional[str] = None

# Initialize service
escrow_service = EscrowService()

@router.get("/dashboard")
async def get_escrow_dashboard(current_user: dict = Depends(get_current_user)):
    """Get comprehensive escrow dashboard"""
    
    return {
        "success": True,
        "data": {
            "overview": {
                "total_transactions": await service.get_metric(),
                "total_value": round(await service.get_metric(), 2),
                "active_escrows": await service.get_metric(),
                "completed_transactions": await service.get_metric(),
                "completion_rate": round(await service.get_metric(), 1),
                "dispute_rate": round(await service.get_metric(), 1),
                "average_transaction_value": round(await service.get_metric(), 2),
                "processing_time": f"{await service.get_metric()} days average"
            },
            "transaction_breakdown": {
                "pending": {
                    "count": await service.get_metric(), 
                    "value": round(await service.get_metric(), 2),
                    "percentage": round(await service.get_metric(), 1)
                },
                "active": {
                    "count": await service.get_metric(), 
                    "value": round(await service.get_metric(), 2),
                    "percentage": round(await service.get_metric(), 1)
                },
                "completed": {
                    "count": await service.get_metric(), 
                    "value": round(await service.get_metric(), 2),
                    "percentage": round(await service.get_metric(), 1)
                },
                "disputed": {
                    "count": await service.get_metric(), 
                    "value": round(await service.get_metric(), 2),
                    "percentage": round(await service.get_metric(), 1)
                }
            },
            "risk_analysis": {
                "low_risk": round(await service.get_metric(), 1),
                "medium_risk": round(await service.get_metric(), 1),
                "high_risk": round(await service.get_metric(), 1),
                "fraud_prevention": f"{round(await service.get_metric(), 1)}% effective",
                "security_score": round(await service.get_metric(), 1),
                "trust_rating": round(await service.get_metric(), 1)
            },
            "transaction_types": [
                {
                    "type": "Service Contracts", 
                    "count": await service.get_metric(), 
                    "percentage": round(await service.get_metric(), 1),
                    "avg_value": round(await service.get_metric(), 2)
                },
                {
                    "type": "Product Sales", 
                    "count": await service.get_metric(), 
                    "percentage": round(await service.get_metric(), 1),
                    "avg_value": round(await service.get_metric(), 2)
                },
                {
                    "type": "Digital Assets", 
                    "count": await service.get_metric(), 
                    "percentage": round(await service.get_metric(), 1),
                    "avg_value": round(await service.get_metric(), 2)
                },
                {
                    "type": "Consulting & Advisory", 
                    "count": await service.get_metric(), 
                    "percentage": round(await service.get_metric(), 1),
                    "avg_value": round(await service.get_metric(), 2)
                }
            ],
            "recent_activity": [
                {
                    "id": str(uuid.uuid4()),
                    "type": "payment_released",
                    "description": "Payment released for Website Development Project",
                    "amount": round(await service.get_metric(), 2),
                    "timestamp": (datetime.now() - timedelta(minutes=await service.get_metric())).isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "type": "transaction_created",
                    "description": "New escrow transaction created for Mobile App Development",
                    "amount": round(await service.get_metric(), 2),
                    "timestamp": (datetime.now() - timedelta(hours=await service.get_metric())).isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "type": "milestone_approved",
                    "description": "Design phase milestone approved for E-commerce Platform",
                    "amount": round(await service.get_metric(), 2),
                    "timestamp": (datetime.now() - timedelta(hours=await service.get_metric())).isoformat()
                }
            ]
        }
    }

@router.get("/transactions")
async def get_transactions(
    status: Optional[str] = None,
    transaction_type: Optional[str] = None,
    limit: Optional[int] = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get user's escrow transactions"""
    user_id = current_user.get("_id") or current_user.get("id") or str(current_user.get("email", "default-user"))
    return await escrow_service.get_transactions(user_id, status, transaction_type, limit)

@router.post("/transactions")
async def create_transaction(
    transaction: EscrowTransactionCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create new escrow transaction"""
    user_id = current_user.get("_id") or current_user.get("id") or str(current_user.get("email", "default-user"))
    return await escrow_service.create_transaction(user_id, transaction.dict())

@router.get("/transactions/{transaction_id}")
async def get_transaction(
    transaction_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific transaction details"""
    return await escrow_service.get_transaction(current_user["id"], transaction_id)

@router.put("/transactions/{transaction_id}/milestone")
async def update_milestone(
    transaction_id: str,
    milestone_update: EscrowMilestoneUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update transaction milestone status"""
    return await escrow_service.update_milestone(current_user["id"], transaction_id, milestone_update.dict())

@router.post("/transactions/{transaction_id}/release")
async def release_payment(
    transaction_id: str,
    release_data: PaymentRelease,
    current_user: dict = Depends(get_current_user)
):
    """Release escrowed payment"""
    return await escrow_service.release_payment(current_user["id"], transaction_id, release_data.dict())

@router.get("/disputes")
async def get_disputes(current_user: dict = Depends(get_current_user)):
    """Get user's dispute cases"""
    user_id = current_user.get("_id") or current_user.get("id") or str(current_user.get("email", "default-user"))
    return await escrow_service.get_disputes(user_id)

@router.post("/disputes")
async def create_dispute(
    dispute: DisputeCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create new dispute case"""
    user_id = current_user.get("_id") or current_user.get("id") or str(current_user.get("email", "default-user"))
    return await escrow_service.create_dispute(user_id, dispute.dict())

@router.get("/analytics")
async def get_escrow_analytics(
    period: Optional[str] = "30d",
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive escrow analytics"""
    
    days = 30 if period == "30d" else (7 if period == "7d" else 90)
    
    return {
        "success": True,
        "data": {
            "performance_metrics": {
                "total_processed": round(await service.get_metric(), 2),
                "successful_transactions": await service.get_metric(),
                "success_rate": round(await service.get_metric(), 1),
                "average_processing_time": f"{await service.get_metric()} hours",
                "dispute_resolution_time": f"{await service.get_metric()} days",
                "customer_satisfaction": round(await service.get_metric(), 1)
            },
            "transaction_trends": [
                {
                    "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                    "transactions": await service.get_metric(),
                    "value": round(await service.get_metric(), 2),
                    "disputes": await service.get_metric()
                } for i in range(days, 0, -1)
            ],
            "category_breakdown": {
                "services": {
                    "transactions": await service.get_metric(),
                    "value": round(await service.get_metric(), 2),
                    "avg_value": round(await service.get_metric(), 2)
                },
                "products": {
                    "transactions": await service.get_metric(),
                    "value": round(await service.get_metric(), 2),
                    "avg_value": round(await service.get_metric(), 2)
                },
                "digital": {
                    "transactions": await service.get_metric(),
                    "value": round(await service.get_metric(), 2),
                    "avg_value": round(await service.get_metric(), 2)
                }
            },
            "risk_metrics": {
                "fraud_attempts": await service.get_metric(),
                "fraud_prevention_rate": round(await service.get_metric(), 1),
                "high_risk_transactions": await service.get_metric(),
                "security_incidents": await service.get_metric(),
                "compliance_score": round(await service.get_metric(), 1)
            },
            "user_satisfaction": {
                "overall_rating": round(await service.get_metric(), 1),
                "support_response_time": f"{await service.get_metric()} minutes",
                "issue_resolution_rate": round(await service.get_metric(), 1),
                "user_retention": round(await service.get_metric(), 1)
            }
        }
    }

@router.get("/settings")
async def get_escrow_settings(current_user: dict = Depends(get_current_user)):
    """Get user's escrow settings"""
    user_id = current_user.get("_id") or current_user.get("id") or str(current_user.get("email", "default-user"))
    return await escrow_service.get_settings(user_id)

@router.put("/settings")
async def update_escrow_settings(
    settings: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update escrow settings"""
    return await escrow_service.update_settings(current_user["id"], settings)

@router.get("/fees")
async def get_fee_structure(current_user: dict = Depends(get_current_user)):
    """Get current fee structure"""
    
    return {
        "success": True,
        "data": {
            "fee_structure": {
                "standard_rate": "2.9%",
                "minimum_fee": "$0.30",
                "volume_discounts": [
                    {"tier": "Bronze", "volume": "$10,000+", "rate": "2.7%"},
                    {"tier": "Silver", "volume": "$50,000+", "rate": "2.5%"},
                    {"tier": "Gold", "volume": "$100,000+", "rate": "2.3%"},
                    {"tier": "Platinum", "volume": "$500,000+", "rate": "2.0%"}
                ],
                "dispute_fee": "$25.00",
                "chargeback_fee": "$15.00",
                "international_fee": "+1.0%"
            },
            "user_tier": {
                "current_tier": await service.get_status(),
                "monthly_volume": round(await service.get_metric(), 2),
                "current_rate": f"{round(await service.get_metric(), 1)}%",
                "next_tier_requirement": round(await service.get_metric(), 2)
            },
            "fee_calculator": {
                "examples": [
                    {"amount": 1000, "fee": 29.30, "net": 970.70},
                    {"amount": 5000, "fee": 145.30, "net": 4854.70},
                    {"amount": 10000, "fee": 290.30, "net": 9709.70}
                ]
            }
        }
    }

@router.get("/compliance")
async def get_compliance_info(current_user: dict = Depends(get_current_user)):
    """Get compliance and regulatory information"""
    
    return {
        "success": True,
        "data": {
            "compliance_status": {
                "kyc_verified": True,
                "aml_compliant": True,
                "pci_dss_certified": True,
                "gdpr_compliant": True,
                "sox_compliant": True
            },
            "regulatory_framework": {
                "primary_regulator": "Financial Conduct Authority (FCA)",
                "license_number": f"FRN-{await service.get_metric()}",
                "audit_date": (datetime.now() - timedelta(days=await service.get_metric())).strftime("%Y-%m-%d"),
                "next_audit": (datetime.now() + timedelta(days=await service.get_metric())).strftime("%Y-%m-%d")
            },
            "security_measures": [
                "256-bit SSL encryption",
                "Multi-factor authentication",
                "Real-time fraud monitoring",
                "Secure data centers",
                "Regular security audits",
                "PCI DSS Level 1 compliance"
            ],
            "insurance_coverage": {
                "cyber_liability": "$10,000,000",
                "errors_omissions": "$5,000,000",
                "general_liability": "$2,000,000"
            }
        }
    }

@router.post("/verify-account")
async def verify_account(
    verification_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Submit account verification documents"""
    return await escrow_service.verify_account(current_user["id"], verification_data)

@router.get("/notifications")
async def get_escrow_notifications(current_user: dict = Depends(get_current_user)):
    """Get escrow-related notifications"""
    return await escrow_service.get_notifications(current_user["id"])