"""
Complete Financial Management System API
Comprehensive financial tools with real data and full CRUD operations
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import uuid4
import logging

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field


from core.auth import get_current_user
from services.complete_financial_service import complete_financial_service
from typing import Dict, Any, List, Optional
from core.auth import get_current_active_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class InvoiceCreateRequest(BaseModel):
    client_email: str = Field(..., description="Client email address")
    client_name: str = Field(..., description="Client name")
    client_address: Optional[str] = Field(None, description="Client address")
    items: List[Dict[str, Any]] = Field(..., description="Invoice items")
    due_date: datetime = Field(..., description="Payment due date")
    tax_rate: Optional[float] = Field(0.0, description="Tax rate percentage")
    notes: Optional[str] = Field(None, description="Additional notes")

class InvoiceUpdateRequest(BaseModel):
    client_email: Optional[str] = None
    client_name: Optional[str] = None
    client_address: Optional[str] = None
    items: Optional[List[Dict[str, Any]]] = None
    due_date: Optional[datetime] = None
    tax_rate: Optional[float] = None
    notes: Optional[str] = None
    status: Optional[str] = None

class ExpenseCreateRequest(BaseModel):
    category: str = Field(..., description="Expense category")
    amount: float = Field(..., description="Expense amount")
    description: str = Field(..., description="Expense description")
    date: datetime = Field(..., description="Expense date")
    receipt_url: Optional[str] = Field(None, description="Receipt URL")
    tags: Optional[List[str]] = Field([], description="Expense tags")

class ExpenseUpdateRequest(BaseModel):
    category: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    receipt_url: Optional[str] = None
    tags: Optional[List[str]] = None

class BudgetCreateRequest(BaseModel):
    name: str = Field(..., description="Budget name")
    categories: Dict[str, float] = Field(..., description="Category budgets")
    period: str = Field("monthly", description="Budget period")
    start_date: datetime = Field(..., description="Budget start date")
    end_date: datetime = Field(..., description="Budget end date")

# Invoice Management Endpoints
@router.post("/invoices", tags=["Financial Management"])
async def create_invoice(
    invoice_data: InvoiceCreateRequest,
    user = Depends(get_current_user)
):
    """Create a new invoice with real data persistence"""
    try:
        # Convert API data to service format
        service_data = {
            'client_info': {
                'email': invoice_data.client_email,
                'name': invoice_data.client_name,
                'address': invoice_data.client_address or ""
            },
            'line_items': [
                {
                    'description': item.get('description', item.get('name', 'Service')),
                    'quantity': item.get('quantity', 1),
                    'rate': item.get('rate', item.get('price', item.get('amount', 0))),
                    'amount': item.get('amount', item.get('price', 0)) * item.get('quantity', 1)
                }
                for item in invoice_data.items
            ],
            'due_date': invoice_data.due_date,
            'tax_rate': invoice_data.tax_rate or 0.0,
            'notes': invoice_data.notes or "",
            'currency': 'USD'
        }
        
        result = await complete_financial_service.create_invoice(
            invoice_data=service_data,
            user_id=user.get('_id') or user.get('id') or user.get('user_id')
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create invoice")
            
        return {
            "success": True,
            "message": "Invoice created successfully",
            "invoice": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Create invoice error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/invoices", tags=["Financial Management"])
async def get_invoices(
    user = Depends(get_current_user),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, description="Number of invoices to return"),
    offset: int = Query(0, description="Offset for pagination")
):
    """Get user invoices with real data"""
    try:
        result = await complete_financial_service.get_user_invoices(
            user_id=user.get('_id') or user.get('id') or user.get('user_id'),
            filters={'status': status} if status else {},
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "invoices": result.get('invoices', []),
            "total_count": result.get('total_count', 0),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get invoices error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/invoices/{invoice_id}", tags=["Financial Management"])
async def get_invoice(
    invoice_id: str,
    user = Depends(get_current_user)
):
    """Get specific invoice details"""
    try:
        result = await complete_financial_service.get_invoice(
            invoice_id=invoice_id,
            user_id=user['id']
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Invoice not found")
            
        return {
            "success": True,
            "invoice": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get invoice error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/invoices/{invoice_id}", tags=["Financial Management"])
async def update_invoice(
    invoice_id: str,
    invoice_data: InvoiceUpdateRequest,
    user = Depends(get_current_user)
):
    """Update invoice with real data persistence"""
    try:
        result = await complete_financial_service.update_invoice(
            invoice_id=invoice_id,
            user_id=user['id'],
            update_data=invoice_data.dict(exclude_unset=True)
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Invoice not found or update failed")
            
        return {
            "success": True,
            "message": "Invoice updated successfully",
            "invoice": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Update invoice error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/invoices/{invoice_id}", tags=["Financial Management"])
async def delete_invoice(
    invoice_id: str,
    user = Depends(get_current_user)
):
    """Delete invoice"""
    try:
        result = await complete_financial_service.delete_invoice(
            invoice_id=invoice_id,
            user_id=user['id']
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Invoice not found")
            
        return {
            "success": True,
            "message": "Invoice deleted successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Delete invoice error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/invoices/{invoice_id}/send", tags=["Financial Management"])
async def send_invoice(
    invoice_id: str,
    user = Depends(get_current_user)
):
    """Send invoice to client"""
    try:
        result = await complete_financial_service.send_invoice(
            invoice_id=invoice_id,
            user_id=user['id']
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Invoice not found or failed to send")
            
        return {
            "success": True,
            "message": "Invoice sent successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Send invoice error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Expense Management Endpoints
@router.post("/expenses", tags=["Financial Management"])
async def create_expense(
    expense_data: ExpenseCreateRequest,
    user = Depends(get_current_user)
):
    """Create a new expense with real data persistence"""
    try:
        result = await complete_financial_service.create_expense(
            user_id=user['id'],
            category=expense_data.category,
            amount=expense_data.amount,
            description=expense_data.description,
            date=expense_data.date,
            receipt_url=expense_data.receipt_url,
            tags=expense_data.tags
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create expense")
            
        return {
            "success": True,
            "message": "Expense created successfully",
            "expense": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Create expense error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/expenses", tags=["Financial Management"])
async def get_expenses(
    user = Depends(get_current_user),
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    limit: int = Query(50, description="Number of expenses to return"),
    offset: int = Query(0, description="Offset for pagination")
):
    """Get user expenses with real data"""
    try:
        result = await complete_financial_service.get_user_expenses(
            user_id=user['id'],
            category=category,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "expenses": result.get('expenses', []),
            "total_count": result.get('total_count', 0),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get expenses error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/expenses/{expense_id}", tags=["Financial Management"])
async def update_expense(
    expense_id: str,
    expense_data: ExpenseUpdateRequest,
    user = Depends(get_current_user)
):
    """Update expense with real data persistence"""
    try:
        result = await complete_financial_service.update_expense(
            expense_id=expense_id,
            user_id=user['id'],
            update_data=expense_data.dict(exclude_unset=True)
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Expense not found or update failed")
            
        return {
            "success": True,
            "message": "Expense updated successfully",
            "expense": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Update expense error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/expenses/{expense_id}", tags=["Financial Management"])
async def delete_expense(
    expense_id: str,
    user = Depends(get_current_user)
):
    """Delete expense"""
    try:
        result = await complete_financial_service.delete_expense(
            expense_id=expense_id,
            user_id=user['id']
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Expense not found")
            
        return {
            "success": True,
            "message": "Expense deleted successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Delete expense error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Budget Management Endpoints
@router.post("/budgets", tags=["Financial Management"])
async def create_budget(
    budget_data: BudgetCreateRequest,
    user = Depends(get_current_user)
):
    """Create a new budget with real data persistence"""
    try:
        result = await complete_financial_service.create_budget(
            user_id=user['id'],
            name=budget_data.name,
            categories=budget_data.categories,
            period=budget_data.period,
            start_date=budget_data.start_date,
            end_date=budget_data.end_date
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create budget")
            
        return {
            "success": True,
            "message": "Budget created successfully",
            "budget": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Create budget error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/budgets", tags=["Financial Management"])
async def get_budgets(
    user = Depends(get_current_user),
    period: Optional[str] = Query(None, description="Filter by period")
):
    """Get user budgets with real data"""
    try:
        result = await complete_financial_service.get_user_budgets(
            user_id=user['id'],
            period=period
        )
        
        return {
            "success": True,
            "budgets": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get budgets error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/budgets/{budget_id}/analysis", tags=["Financial Management"])
async def get_budget_analysis(
    budget_id: str,
    user = Depends(get_current_user)
):
    """Get budget vs actual spending analysis"""
    try:
        result = await complete_financial_service.get_budget_analysis(
            budget_id=budget_id,
            user_id=user['id']
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Budget not found")
            
        return {
            "success": True,
            "analysis": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get budget analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Payment Processing Endpoints
@router.post("/payments/process", tags=["Financial Management"])
async def process_payment(
    payment_data: Dict[str, Any] = Body(...),
    user = Depends(get_current_user)
):
    """Process payment with real Stripe integration"""
    try:
        result = await complete_financial_service.process_payment(
            user_id=user['id'],
            amount=payment_data.get('amount'),
            currency=payment_data.get('currency', 'USD'),
            payment_method_id=payment_data.get('payment_method_id'),
            invoice_id=payment_data.get('invoice_id'),
            metadata=payment_data.get('metadata', {})
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Payment processing failed")
            
        return {
            "success": True,
            "message": "Payment processed successfully",
            "payment": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Process payment error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payments", tags=["Financial Management"])
async def get_payments(
    user = Depends(get_current_user),
    status: Optional[str] = Query(None, description="Filter by payment status"),
    limit: int = Query(50, description="Number of payments to return"),
    offset: int = Query(0, description="Offset for pagination")
):
    """Get user payments with real data"""
    try:
        result = await complete_financial_service.get_user_payments(
            user_id=user['id'],
            status=status,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "payments": result.get('payments', []),
            "total_count": result.get('total_count', 0),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get payments error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Financial Reports and Analytics
@router.get("/reports/revenue", tags=["Financial Management"])
async def get_revenue_report(
    user = Depends(get_current_user),
    start_date: datetime = Query(..., description="Report start date"),
    end_date: datetime = Query(..., description="Report end date"),
    group_by: str = Query("month", description="Group by period")
):
    """Get revenue report with real data"""
    try:
        result = await complete_financial_service.get_revenue_report(
            user_id=user['id'],
            start_date=start_date,
            end_date=end_date,
            group_by=group_by
        )
        
        return {
            "success": True,
            "report": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get revenue report error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/expenses", tags=["Financial Management"])
async def get_expense_report(
    user = Depends(get_current_user),
    start_date: datetime = Query(..., description="Report start date"),
    end_date: datetime = Query(..., description="Report end date"),
    group_by: str = Query("category", description="Group by category or period")
):
    """Get expense report with real data"""
    try:
        result = await complete_financial_service.get_expense_report(
            user_id=user['id'],
            start_date=start_date,
            end_date=end_date,
            group_by=group_by
        )
        
        return {
            "success": True,
            "report": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get expense report error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard", tags=["Financial Management"])
async def get_financial_dashboard(
    user = Depends(get_current_user)
):
    """Get comprehensive financial dashboard data"""
    try:
        result = await complete_financial_service.get_financial_dashboard(
            user_id=user['id']
        )
        
        return {
            "success": True,
            "dashboard": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get financial dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", tags=["Financial Management"])
async def financial_health_check():
    """Health check for financial management system"""
    return {
        "status": "healthy",
        "service": "Complete Financial Management",
        "features": [
            "Invoice Management",
            "Expense Tracking",
            "Budget Management",
            "Payment Processing",
            "Financial Reports",
            "Real-time Analytics"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }