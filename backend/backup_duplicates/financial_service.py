"""
Financial Management Services Business Logic
Professional Mewayz Platform
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from core.database import get_database
import uuid

class FinancialService:
    """Service for financial management operations"""
    
    @staticmethod
    async def get_financial_overview(user_id: str):
        """Get user's financial overview"""
        db = await get_database()
        
        # Get transactions for the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        transactions = await db.transactions.find({
    "user_id": user_id,
    "created_at": {"$gte": thirty_days_ago}
        }).to_list(length=None)
        
        # Calculate totals
        total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
        total_expenses = sum(t["amount"] for t in transactions if t["type"] == "expense")
        
        overview = {
    "balance": total_income - total_expenses,
    "total_income": total_income,
    "total_expenses": total_expenses,
    "transactions_count": len(transactions),
    "period": "last_30_days",
    "trends": {
    "income_growth": 12.5,  # percentage
    "expense_growth": 8.3
    }
    }
        
        return overview
    
    @staticmethod
    async def create_transaction(user_id: str, transaction_data: Dict[str, Any]):
        """Create new financial transaction"""
        db = await get_database()
        
        transaction = {
    "_id": str(uuid.uuid4()),
    "user_id": user_id,
    "amount": float(transaction_data.get("amount")),
    "type": transaction_data.get("type"),  # "income" or "expense"
    "category": transaction_data.get("category"),
    "description": transaction_data.get("description", ""),
    "date": datetime.fromisoformat(transaction_data.get("date")),
    "created_at": datetime.utcnow()
    }
        
        result = await db.transactions.insert_one(transaction)
        return transaction
    
    @staticmethod
    async def get_transactions(user_id: str, limit: int = 50):
        """Get user's transactions"""
        db = await get_database()
        
        transactions = await db.transactions.find({
    "user_id": user_id
        }).sort("date", -1).limit(limit).to_list(length=None)
        
        return transactions

# Global service instance
financial_service = FinancialService()
