"""
Financial Management API Routes
Professional Mewayz Platform - Migrated from Monolithic Structure
High-Value Feature Addition - Complete Financial System
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from core.auth import get_current_active_user
from core.database import get_database
from services.user_service import get_user_service

router = APIRouter()

# Initialize service instances
user_service = get_user_service()

class InvoiceCreate(BaseModel):
    client_name: str
    client_email: EmailStr
    client_address: Optional[str] = ""
    items: List[Dict[str, Any]]  # [{"name": "Service", "quantity": 1, "price": 100.00}]
    tax_rate: float = 0.0
    due_date: Optional[datetime] = None
    notes: Optional[str] = ""

class PaymentCreate(BaseModel):
    invoice_id: str
    amount: float
    payment_method: str = "manual"
    payment_date: Optional[datetime] = None
    notes: Optional[str] = ""

class ExpenseCreate(BaseModel):
    category: str
    description: str
    amount: float
    expense_date: Optional[datetime] = None
    receipt_url: Optional[str] = None
    tax_deductible: bool = False

def get_invoices_collection():
    """Get invoices collection"""
    db = get_database()
    return db.invoices

def get_payments_collection():
    """Get payments collection"""
    db = get_database()
    return db.payments

def get_expenses_collection():
    """Get expenses collection"""
    db = get_database()
    return db.expenses

def get_financial_analytics_collection():
    """Get financial analytics collection"""
    db = get_database()
    return db.financial_analytics

@router.get("/dashboard")
async def get_financial_dashboard(
    period: str = "month",  # month, quarter, year
    current_user: dict = Depends(get_current_active_user)
):
    """Get comprehensive financial dashboard with real database calculations"""
    try:
        # Determine date range based on period
        now = datetime.utcnow()
        if period == "month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "quarter":
            quarter_start_month = ((now.month - 1) // 3) * 3 + 1
            start_date = now.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "year":
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = now - timedelta(days=30)
        
        # Get collections
        invoices_collection = get_invoices_collection()
        payments_collection = get_payments_collection()
        expenses_collection = get_expenses_collection()
        
        # Calculate revenue metrics
        revenue_pipeline = [
            {"$match": {
                "user_id": current_user["_id"],
                "created_at": {"$gte": start_date},
                "status": {"$in": ["paid", "completed"]}
            }},
            {"$group": {
                "_id": None,
                "total_revenue": {"$sum": "$total_amount"},
                "total_invoices": {"$sum": 1},
                "average_invoice_value": {"$avg": "$total_amount"}
            }}
        ]
        
        revenue_stats = await invoices_collection.aggregate(revenue_pipeline).to_list(length=1)
        revenue_data = revenue_stats[0] if revenue_stats else {
            "total_revenue": 0, "total_invoices": 0, "average_invoice_value": 0
        }
        
        # Calculate expense metrics
        expense_pipeline = [
            {"$match": {
                "user_id": current_user["_id"],
                "expense_date": {"$gte": start_date}
            }},
            {"$group": {
                "_id": None,
                "total_expenses": {"$sum": "$amount"},
                "total_count": {"$sum": 1}
            }}
        ]
        
        expense_stats = await expenses_collection.aggregate(expense_pipeline).to_list(length=1)
        expense_data = expense_stats[0] if expense_stats else {"total_expenses": 0, "total_count": 0}
        
        # Calculate outstanding invoices
        outstanding_pipeline = [
            {"$match": {
                "user_id": current_user["_id"],
                "status": {"$in": ["pending", "sent"]},
                "due_date": {"$lte": now}
            }},
            {"$group": {
                "_id": None,
                "overdue_amount": {"$sum": "$total_amount"},
                "overdue_count": {"$sum": 1}
            }}
        ]
        
        outstanding_stats = await invoices_collection.aggregate(outstanding_pipeline).to_list(length=1)
        outstanding_data = outstanding_stats[0] if outstanding_stats else {"overdue_amount": 0, "overdue_count": 0}
        
        # Get recent payments
        recent_payments = await payments_collection.find({
            "user_id": current_user["_id"]
        }).sort("payment_date", -1).limit(5).to_list(length=None)
        
        # Calculate profit metrics
        profit = revenue_data["total_revenue"] - expense_data["total_expenses"]
        profit_margin = (profit / revenue_data["total_revenue"] * 100) if revenue_data["total_revenue"] > 0 else 0
        
        # Get expense breakdown by category
        expense_breakdown = await expenses_collection.aggregate([
            {"$match": {
                "user_id": current_user["_id"],
                "expense_date": {"$gte": start_date}
            }},
            {"$group": {
                "_id": "$category",
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"total": -1}},
            {"$limit": 10}
        ]).to_list(length=None)
        
        # Calculate cash flow projections (next 3 months)
        future_invoices = await invoices_collection.find({
            "user_id": current_user["_id"],
            "status": {"$in": ["pending", "sent"]},
            "due_date": {"$gte": now}
        }).to_list(length=None)
        
        cash_flow_projection = sum(invoice.get("total_amount", 0) for invoice in future_invoices)
        
        dashboard_data = {
            "period": period,
            "date_range": {
                "start": start_date.isoformat(),
                "end": now.isoformat()
            },
            "revenue_metrics": {
                "total_revenue": round(revenue_data["total_revenue"], 2),
                "total_invoices": revenue_data["total_invoices"],
                "average_invoice_value": round(revenue_data["average_invoice_value"], 2)
            },
            "expense_metrics": {
                "total_expenses": round(expense_data["total_expenses"], 2),
                "total_transactions": expense_data["total_count"],
                "expense_breakdown": expense_breakdown
            },
            "profit_metrics": {
                "gross_profit": round(profit, 2),
                "profit_margin": round(profit_margin, 1),
                "net_profit": round(profit, 2)  # Would subtract taxes in real implementation
            },
            "outstanding_receivables": {
                "overdue_amount": round(outstanding_data["overdue_amount"], 2),
                "overdue_count": outstanding_data["overdue_count"]
            },
            "cash_flow": {
                "projected_income_3_months": round(cash_flow_projection, 2),
                "current_cash_position": 0  # Would integrate with bank APIs
            },
            "recent_payments": recent_payments
        }
        
        return {
            "success": True,
            "data": dashboard_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch financial dashboard: {str(e)}"
        )

@router.get("/invoices")
async def get_invoices(
    status_filter: Optional[str] = None,
    client_filter: Optional[str] = None,
    limit: int = 50,
    page: int = 1,
    current_user: dict = Depends(get_current_active_user)
):
    """Get invoices with real database operations and filtering"""
    try:
        invoices_collection = get_invoices_collection()
        
        # Build query
        query = {"user_id": current_user["_id"]}
        if status_filter:
            query["status"] = status_filter
        if client_filter:
            query["$or"] = [
                {"client_name": {"$regex": client_filter, "$options": "i"}},
                {"client_email": {"$regex": client_filter, "$options": "i"}}
            ]
        
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Get invoices with pagination
        invoices = await invoices_collection.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(length=None)
        total_invoices = await invoices_collection.count_documents(query)
        
        # Calculate totals for the filtered set
        total_amount_pipeline = [
            {"$match": query},
            {"$group": {
                "_id": None,
                "total_amount": {"$sum": "$total_amount"},
                "paid_amount": {
                    "$sum": {"$cond": [
                        {"$eq": ["$status", "paid"]},
                        "$total_amount",
                        0
                    ]}
                }
            }}
        ]
        
        totals = await invoices_collection.aggregate(total_amount_pipeline).to_list(length=1)
        totals_data = totals[0] if totals else {"total_amount": 0, "paid_amount": 0}
        
        return {
            "success": True,
            "data": {
                "invoices": invoices,
                "pagination": {
                    "current_page": page,
                    "total_pages": (total_invoices + limit - 1) // limit,
                    "total_invoices": total_invoices,
                    "has_next": skip + limit < total_invoices,
                    "has_prev": page > 1
                },
                "summary": {
                    "total_amount": round(totals_data["total_amount"], 2),
                    "paid_amount": round(totals_data["paid_amount"], 2),
                    "outstanding_amount": round(totals_data["total_amount"] - totals_data["paid_amount"], 2)
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch invoices: {str(e)}"
        )

@router.post("/invoices")
async def create_invoice(
    invoice_data: InvoiceCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create invoice with real database operations and automatic calculations"""
    try:
        # Calculate invoice totals
        subtotal = sum(item.get("quantity", 1) * item.get("price", 0) for item in invoice_data.items)
        tax_amount = subtotal * invoice_data.tax_rate
        total_amount = subtotal + tax_amount
        
        # Generate invoice number
        invoices_collection = get_invoices_collection()
        invoice_count = await invoices_collection.count_documents({"user_id": current_user["_id"]})
        invoice_number = f"INV-{datetime.utcnow().strftime('%Y%m')}-{invoice_count + 1:04d}"
        
        # Set due date if not provided (default 30 days)
        due_date = invoice_data.due_date or (datetime.utcnow() + timedelta(days=30))
        
        # Create invoice document
        invoice_doc = {
            "_id": str(uuid.uuid4()),
            "user_id": current_user["_id"],
            "invoice_number": invoice_number,
            "client_name": invoice_data.client_name,
            "client_email": invoice_data.client_email,
            "client_address": invoice_data.client_address,
            "items": invoice_data.items,
            "subtotal": round(subtotal, 2),
            "tax_rate": invoice_data.tax_rate,
            "tax_amount": round(tax_amount, 2),
            "total_amount": round(total_amount, 2),
            "due_date": due_date,
            "status": "draft",
            "notes": invoice_data.notes,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "sent_at": None,
            "paid_at": None,
            "payment_history": []
        }
        
        # Save to database
        await invoices_collection.insert_one(invoice_doc)
        
        return {
            "success": True,
            "message": "Invoice created successfully",
            "data": invoice_doc
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create invoice: {str(e)}"
        )

@router.put("/invoices/{invoice_id}/status")
async def update_invoice_status(
    invoice_id: str,
    new_status: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Update invoice status with validation"""
    try:
        valid_statuses = ["draft", "sent", "paid", "overdue", "cancelled"]
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Valid options: {', '.join(valid_statuses)}"
            )
        
        invoices_collection = get_invoices_collection()
        
        # Find invoice
        invoice = await invoices_collection.find_one({
            "_id": invoice_id,
            "user_id": current_user["_id"]
        })
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        # Prepare update
        update_data = {
            "status": new_status,
            "updated_at": datetime.utcnow()
        }
        
        # Add timestamp for specific statuses
        if new_status == "sent" and not invoice.get("sent_at"):
            update_data["sent_at"] = datetime.utcnow()
        elif new_status == "paid" and not invoice.get("paid_at"):
            update_data["paid_at"] = datetime.utcnow()
        
        # Update invoice
        result = await invoices_collection.update_one(
            {"_id": invoice_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No changes made"
            )
        
        return {
            "success": True,
            "message": f"Invoice status updated to {new_status}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update invoice status: {str(e)}"
        )

@router.post("/payments")
async def record_payment(
    payment_data: PaymentCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Record payment against invoice"""
    try:
        invoices_collection = get_invoices_collection()
        payments_collection = get_payments_collection()
        
        # Find invoice
        invoice = await invoices_collection.find_one({
            "_id": payment_data.invoice_id,
            "user_id": current_user["_id"]
        })
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        # Validate payment amount
        if payment_data.amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment amount must be positive"
            )
        
        if payment_data.amount > invoice["total_amount"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment amount cannot exceed invoice total"
            )
        
        # Create payment record
        payment_doc = {
            "_id": str(uuid.uuid4()),
            "user_id": current_user["_id"],
            "invoice_id": payment_data.invoice_id,
            "invoice_number": invoice["invoice_number"],
            "client_name": invoice["client_name"],
            "amount": payment_data.amount,
            "payment_method": payment_data.payment_method,
            "payment_date": payment_data.payment_date or datetime.utcnow(),
            "notes": payment_data.notes,
            "created_at": datetime.utcnow()
        }
        
        # Save payment
        await payments_collection.insert_one(payment_doc)
        
        # Update invoice payment history and status
        payment_history = invoice.get("payment_history", [])
        payment_history.append({
            "payment_id": payment_doc["_id"],
            "amount": payment_data.amount,
            "payment_date": payment_doc["payment_date"],
            "method": payment_data.payment_method
        })
        
        # Calculate total paid
        total_paid = sum(p["amount"] for p in payment_history)
        
        # Determine new invoice status
        if total_paid >= invoice["total_amount"]:
            new_status = "paid"
            paid_at = datetime.utcnow()
        else:
            new_status = "partially_paid"
            paid_at = None
        
        # Update invoice
        update_data = {
            "payment_history": payment_history,
            "amount_paid": round(total_paid, 2),
            "balance_due": round(invoice["total_amount"] - total_paid, 2),
            "status": new_status,
            "updated_at": datetime.utcnow()
        }
        
        if paid_at:
            update_data["paid_at"] = paid_at
        
        await invoices_collection.update_one(
            {"_id": payment_data.invoice_id},
            {"$set": update_data}
        )
        
        return {
            "success": True,
            "message": "Payment recorded successfully",
            "data": {
                "payment_id": payment_doc["_id"],
                "new_invoice_status": new_status,
                "balance_due": update_data["balance_due"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record payment: {str(e)}"
        )

@router.get("/expenses")
async def get_expenses(
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user)
):
    """Get expenses with filtering"""
    try:
        expenses_collection = get_expenses_collection()
        
        # Build query
        query = {"user_id": current_user["_id"]}
        if category:
            query["category"] = category
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            query["expense_date"] = date_filter
        
        # Get expenses
        expenses = await expenses_collection.find(query).sort("expense_date", -1).limit(limit).to_list(length=None)
        
        # Get category breakdown
        category_pipeline = [
            {"$match": query},
            {"$group": {
                "_id": "$category",
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"total": -1}}
        ]
        
        category_breakdown = await expenses_collection.aggregate(category_pipeline).to_list(length=None)
        
        # Calculate totals
        total_amount = sum(expense.get("amount", 0) for expense in expenses)
        tax_deductible_amount = sum(expense.get("amount", 0) for expense in expenses if expense.get("tax_deductible"))
        
        return {
            "success": True,
            "data": {
                "expenses": expenses,
                "summary": {
                    "total_expenses": round(total_amount, 2),
                    "tax_deductible": round(tax_deductible_amount, 2),
                    "category_breakdown": category_breakdown
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch expenses: {str(e)}"
        )

@router.post("/expenses")
async def create_expense(
    expense_data: ExpenseCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create expense record"""
    try:
        # Create expense document
        expense_doc = {
            "_id": str(uuid.uuid4()),
            "user_id": current_user["_id"],
            "category": expense_data.category,
            "description": expense_data.description,
            "amount": expense_data.amount,
            "expense_date": expense_data.expense_date or datetime.utcnow(),
            "receipt_url": expense_data.receipt_url,
            "tax_deductible": expense_data.tax_deductible,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Save to database
        expenses_collection = get_expenses_collection()
        await expenses_collection.insert_one(expense_doc)
        
        return {
            "success": True,
            "message": "Expense recorded successfully",
            "data": expense_doc
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create expense: {str(e)}"
        )

@router.get("/reports/profit-loss")
async def get_profit_loss_report(
    period: str = "month",
    year: int = None,
    month: int = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Generate profit & loss report"""
    try:
        # Determine date range
        now = datetime.utcnow()
        year = year or now.year
        
        if period == "year":
            start_date = datetime(year, 1, 1)
            end_date = datetime(year + 1, 1, 1)
        elif period == "month":
            month = month or now.month
            start_date = datetime(year, month, 1)
            next_month = month + 1 if month < 12 else 1
            next_year = year if month < 12 else year + 1
            end_date = datetime(next_year, next_month, 1)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid period. Use 'month' or 'year'"
            )
        
        # Get revenue data
        invoices_collection = get_invoices_collection()
        revenue_pipeline = [
            {"$match": {
                "user_id": current_user["_id"],
                "status": "paid",
                "paid_at": {"$gte": start_date, "$lt": end_date}
            }},
            {"$group": {
                "_id": None,
                "total_revenue": {"$sum": "$total_amount"}
            }}
        ]
        
        revenue_result = await invoices_collection.aggregate(revenue_pipeline).to_list(length=1)
        total_revenue = revenue_result[0]["total_revenue"] if revenue_result else 0
        
        # Get expense data
        expenses_collection = get_expenses_collection()
        expense_pipeline = [
            {"$match": {
                "user_id": current_user["_id"],
                "expense_date": {"$gte": start_date, "$lt": end_date}
            }},
            {"$group": {
                "_id": "$category",
                "total": {"$sum": "$amount"}
            }}
        ]
        
        expense_breakdown = await expenses_collection.aggregate(expense_pipeline).to_list(length=None)
        total_expenses = sum(item["total"] for item in expense_breakdown)
        
        # Calculate profit metrics
        gross_profit = total_revenue - total_expenses
        profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        report = {
            "period": period,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "revenue": {
                "total_revenue": round(total_revenue, 2)
            },
            "expenses": {
                "total_expenses": round(total_expenses, 2),
                "breakdown": expense_breakdown
            },
            "profit": {
                "gross_profit": round(gross_profit, 2),
                "profit_margin": round(profit_margin, 1)
            }
        }
        
        return {
            "success": True,
            "data": report
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate profit & loss report: {str(e)}"
        )