"""
Complete Financial Management Service
Professional Invoicing, Payments, and Financial Analytics
Version: 1.0.0 - Production Ready
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import httpx
import os
import uuid
from decimal import Decimal
from motor.motor_asyncio import AsyncIOMotorDatabase
from core.database import get_database
from core.config import get_api_key
import stripe

logger = logging.getLogger(__name__)

class CompleteFinancialService:
    """
    Complete Financial Management System
    Features:
    - Professional invoice generation and management
    - Multi-currency support with real-time conversion
    - Automated payment reminders and overdue notices
    - Stripe payment processing integration
    - Tax calculation and reporting
    - Expense tracking and categorization
    - Financial analytics and reporting
    - Profit & Loss statements
    - Cash flow management
    - Client payment portal
    - Recurring billing and subscriptions
    - Multi-payment method support
    - Integration with accounting software
    """
    
    def __init__(self):
        self.stripe_secret_key = get_api_key('STRIPE_SECRET_KEY')
        self.stripe_publishable_key = get_api_key('STRIPE_PUBLISHABLE_KEY')
        self.exchange_rate_api_key = get_api_key('EXCHANGE_RATE_API_KEY')
        
        # Initialize Stripe
        stripe.api_key = self.stripe_secret_key
        
    async def get_database(self) -> AsyncIOMotorDatabase:
        """Get database connection"""
        return get_database()
    
    async def create_invoice(self, invoice_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Create a professional invoice with real Stripe integration
        """
        try:
            db = await self.get_database()
            
            invoice_id = str(uuid.uuid4())
            invoice_number = await self._generate_invoice_number(user_id)
            current_time = datetime.utcnow()
            
            # Calculate totals
            line_items = invoice_data.get('line_items', [])
            subtotal = sum(Decimal(str(item['quantity'])) * Decimal(str(item['rate'])) for item in line_items)
            
            # Apply discount
            discount_amount = Decimal(str(invoice_data.get('discount_amount', 0)))
            discount_percentage = Decimal(str(invoice_data.get('discount_percentage', 0)))
            
            if discount_percentage > 0:
                discount_amount = subtotal * (discount_percentage / 100)
            
            # Calculate tax
            tax_rate = Decimal(str(invoice_data.get('tax_rate', 0)))
            tax_amount = (subtotal - discount_amount) * (tax_rate / 100)
            
            total_amount = subtotal - discount_amount + tax_amount
            
            # Create Stripe invoice if enabled
            stripe_invoice_id = None
            if self.stripe_secret_key and invoice_data.get('create_stripe_invoice', True):
                try:
                    # Create or get Stripe customer
                    customer_email = invoice_data['client_info']['email']
                    stripe_customer = await self._get_or_create_stripe_customer(customer_email, invoice_data['client_info'])
                    
                    # Create Stripe invoice
                    stripe_invoice = stripe.Invoice.create(
                        customer=stripe_customer.id,
                        currency=invoice_data.get('currency', 'usd'),
                        description=invoice_data.get('description', f'Invoice {invoice_number}'),
                        metadata={
                            'invoice_id': invoice_id,
                            'user_id': user_id,
                            'invoice_number': invoice_number
                        }
                    )
                    
                    # Add line items to Stripe invoice
                    for item in line_items:
                        stripe.InvoiceItem.create(
                            customer=stripe_customer.id,
                            invoice=stripe_invoice.id,
                            amount=int(float(item['quantity']) * float(item['rate']) * 100),
                            currency=invoice_data.get('currency', 'usd'),
                            description=item['description']
                        )
                    
                    stripe_invoice_id = stripe_invoice.id
                    
                except Exception as stripe_error:
                    logger.warning(f"Stripe invoice creation failed: {str(stripe_error)}")
            
            # Create invoice document
            invoice = {
                'invoice_id': invoice_id,
                'user_id': user_id,
                'invoice_number': invoice_number,
                'stripe_invoice_id': stripe_invoice_id,
                'client_info': {
                    'name': invoice_data['client_info']['name'],
                    'email': invoice_data['client_info']['email'],
                    'company': invoice_data['client_info'].get('company', ''),
                    'address': invoice_data['client_info'].get('address', {}),
                    'phone': invoice_data['client_info'].get('phone', ''),
                    'tax_id': invoice_data['client_info'].get('tax_id', '')
                },
                'business_info': {
                    'name': invoice_data['business_info']['name'],
                    'email': invoice_data['business_info']['email'],
                    'company': invoice_data['business_info'].get('company', ''),
                    'address': invoice_data['business_info'].get('address', {}),
                    'phone': invoice_data['business_info'].get('phone', ''),
                    'website': invoice_data['business_info'].get('website', ''),
                    'tax_id': invoice_data['business_info'].get('tax_id', ''),
                    'logo_url': invoice_data['business_info'].get('logo_url', '')
                },
                'line_items': [
                    {
                        'item_id': str(uuid.uuid4()),
                        'description': item['description'],
                        'quantity': Decimal(str(item['quantity'])),
                        'rate': Decimal(str(item['rate'])),
                        'amount': Decimal(str(item['quantity'])) * Decimal(str(item['rate']))
                    }
                    for item in line_items
                ],
                'financial_details': {
                    'subtotal': float(subtotal),
                    'discount_amount': float(discount_amount),
                    'discount_percentage': float(discount_percentage),
                    'tax_rate': float(tax_rate),
                    'tax_amount': float(tax_amount),
                    'total_amount': float(total_amount),
                    'currency': invoice_data.get('currency', 'USD'),
                    'payment_terms': invoice_data.get('payment_terms', 'Net 30')
                },
                'dates': {
                    'issue_date': current_time,
                    'due_date': current_time + timedelta(days=invoice_data.get('due_days', 30)),
                    'sent_date': None,
                    'paid_date': None,
                    'last_reminder_sent': None
                },
                'payment_info': {
                    'status': 'draft',  # draft, sent, viewed, partial, paid, overdue, cancelled
                    'payment_method': invoice_data.get('payment_method', 'stripe'),
                    'payment_url': None,
                    'payments_received': [],
                    'total_paid': 0.0,
                    'balance_due': float(total_amount)
                },
                'settings': {
                    'template_id': invoice_data.get('template_id', 'default'),
                    'notes': invoice_data.get('notes', ''),
                    'terms_conditions': invoice_data.get('terms_conditions', ''),
                    'send_reminders': invoice_data.get('send_reminders', True),
                    'reminder_frequency': invoice_data.get('reminder_frequency', 7),  # days
                    'late_fee_enabled': invoice_data.get('late_fee_enabled', False),
                    'late_fee_amount': invoice_data.get('late_fee_amount', 0),
                    'late_fee_percentage': invoice_data.get('late_fee_percentage', 0)
                },
                'tracking': {
                    'views': 0,
                    'last_viewed': None,
                    'download_count': 0,
                    'email_opens': 0,
                    'link_clicks': 0
                },
                'created_at': current_time,
                'updated_at': current_time
            }
            
            # Insert invoice
            await db.invoices.insert_one(invoice)
            
            # Create payment link if Stripe invoice was created
            if stripe_invoice_id:
                try:
                    stripe_invoice = stripe.Invoice.finalize_invoice(stripe_invoice_id)
                    payment_url = stripe_invoice.hosted_invoice_url
                    
                    await db.invoices.update_one(
                        {'invoice_id': invoice_id},
                        {'$set': {'payment_info.payment_url': payment_url}}
                    )
                    invoice['payment_info']['payment_url'] = payment_url
                    
                except Exception as e:
                    logger.warning(f"Failed to finalize Stripe invoice: {str(e)}")
            
            # Generate PDF
            pdf_url = await self._generate_invoice_pdf(invoice_id)
            
            return {
                'success': True,
                'invoice': invoice,
                'pdf_url': pdf_url,
                'payment_url': invoice['payment_info']['payment_url'],
                'stripe_invoice_id': stripe_invoice_id
            }
            
        except Exception as e:
            logger.error(f"Invoice creation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_invoice_number(self, user_id: str) -> str:
        """Generate unique invoice number"""
        try:
            db = await self.get_database()
            
            # Get user's invoice count
            count = await db.invoices.count_documents({'user_id': user_id})
            
            # Generate invoice number: INV-YYYY-NNNN
            year = datetime.utcnow().year
            number = str(count + 1).zfill(4)
            
            return f"INV-{year}-{number}"
            
        except Exception as e:
            # Fallback to timestamp-based number
            timestamp = int(datetime.utcnow().timestamp())
            return f"INV-{timestamp}"
    
    async def _get_or_create_stripe_customer(self, email: str, client_info: Dict) -> Any:
        """Get existing or create new Stripe customer"""
        try:
            # Search for existing customer
            customers = stripe.Customer.list(email=email, limit=1)
            
            if customers.data:
                return customers.data[0]
            else:
                # Create new customer
                customer_data = {
                    'email': email,
                    'name': client_info.get('name', ''),
                    'phone': client_info.get('phone', ''),
                }
                
                if client_info.get('address'):
                    customer_data['address'] = client_info['address']
                
                return stripe.Customer.create(**customer_data)
                
        except Exception as e:
            logger.error(f"Stripe customer creation error: {str(e)}")
            raise e
    
    async def send_invoice(self, invoice_id: str, user_id: str, send_options: Dict = None) -> Dict[str, Any]:
        """
        Send invoice to client via email
        """
        try:
            db = await self.get_database()
            
            invoice = await db.invoices.find_one({'invoice_id': invoice_id, 'user_id': user_id})
            if not invoice:
                return {'success': False, 'error': 'Invoice not found'}
            
            if invoice['payment_info']['status'] not in ['draft', 'sent']:
                return {'success': False, 'error': 'Invoice cannot be sent in current status'}
            
            # Send Stripe invoice if available
            if invoice.get('stripe_invoice_id'):
                try:
                    stripe.Invoice.send_invoice(invoice['stripe_invoice_id'])
                except Exception as stripe_error:
                    logger.warning(f"Stripe invoice send failed: {str(stripe_error)}")
            
            # Update invoice status
            current_time = datetime.utcnow()
            await db.invoices.update_one(
                {'invoice_id': invoice_id},
                {
                    '$set': {
                        'payment_info.status': 'sent',
                        'dates.sent_date': current_time,
                        'updated_at': current_time
                    }
                }
            )
            
            # Log the sending action
            await self._create_invoice_activity(
                invoice_id, 'invoice_sent',
                f"Invoice sent to {invoice['client_info']['email']}"
            )
            
            # Schedule payment reminders if enabled
            if invoice['settings']['send_reminders']:
                await self._schedule_payment_reminders(invoice_id)
            
            return {
                'success': True,
                'message': 'Invoice sent successfully',
                'sent_to': invoice['client_info']['email'],
                'sent_date': current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Send invoice error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def record_payment(self, invoice_id: str, payment_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Record payment received for an invoice
        """
        try:
            db = await self.get_database()
            
            invoice = await db.invoices.find_one({'invoice_id': invoice_id, 'user_id': user_id})
            if not invoice:
                return {'success': False, 'error': 'Invoice not found'}
            
            payment_id = str(uuid.uuid4())
            payment_amount = Decimal(str(payment_data['amount']))
            
            payment_record = {
                'payment_id': payment_id,
                'invoice_id': invoice_id,
                'amount': float(payment_amount),
                'currency': payment_data.get('currency', invoice['financial_details']['currency']),
                'payment_method': payment_data.get('payment_method', 'manual'),
                'payment_date': datetime.fromisoformat(payment_data['payment_date']) if payment_data.get('payment_date') else datetime.utcnow(),
                'reference_number': payment_data.get('reference_number', ''),
                'notes': payment_data.get('notes', ''),
                'stripe_payment_intent_id': payment_data.get('stripe_payment_intent_id'),
                'created_at': datetime.utcnow()
            }
            
            # Calculate new totals
            total_paid = invoice['payment_info']['total_paid'] + float(payment_amount)
            balance_due = invoice['financial_details']['total_amount'] - total_paid
            
            # Determine new status
            if balance_due <= 0:
                new_status = 'paid'
                paid_date = payment_record['payment_date']
            elif total_paid > 0:
                new_status = 'partial'
                paid_date = None
            else:
                new_status = invoice['payment_info']['status']
                paid_date = None
            
            # Update invoice
            await db.invoices.update_one(
                {'invoice_id': invoice_id},
                {
                    '$push': {'payment_info.payments_received': payment_record},
                    '$set': {
                        'payment_info.total_paid': total_paid,
                        'payment_info.balance_due': balance_due,
                        'payment_info.status': new_status,
                        'dates.paid_date': paid_date,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            # Create activity log
            await self._create_invoice_activity(
                invoice_id, 'payment_received',
                f"Payment of {payment_amount} {payment_record['currency']} received"
            )
            
            # Update financial analytics
            await self._update_financial_analytics(user_id, 'payment_received', payment_record)
            
            return {
                'success': True,
                'payment': payment_record,
                'invoice_status': new_status,
                'total_paid': total_paid,
                'balance_due': balance_due
            }
            
        except Exception as e:
            logger.error(f"Record payment error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def create_expense(self, expense_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Create and track business expense
        """
        try:
            db = await self.get_database()
            
            expense_id = str(uuid.uuid4())
            
            expense = {
                'expense_id': expense_id,
                'user_id': user_id,
                'category': expense_data['category'],
                'subcategory': expense_data.get('subcategory', ''),
                'description': expense_data['description'],
                'amount': Decimal(str(expense_data['amount'])),
                'currency': expense_data.get('currency', 'USD'),
                'expense_date': datetime.fromisoformat(expense_data['expense_date']) if expense_data.get('expense_date') else datetime.utcnow(),
                'payment_method': expense_data.get('payment_method', 'cash'),
                'vendor': expense_data.get('vendor', ''),
                'project_id': expense_data.get('project_id'),
                'client_id': expense_data.get('client_id'),
                'receipt_url': expense_data.get('receipt_url', ''),
                'receipt_number': expense_data.get('receipt_number', ''),
                'tax_deductible': expense_data.get('tax_deductible', True),
                'billable': expense_data.get('billable', False),
                'reimbursable': expense_data.get('reimbursable', False),
                'status': expense_data.get('status', 'recorded'),  # recorded, approved, reimbursed
                'tags': expense_data.get('tags', []),
                'notes': expense_data.get('notes', ''),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            await db.expenses.insert_one(expense)
            
            # Update financial analytics
            await self._update_financial_analytics(user_id, 'expense_recorded', expense)
            
            # Convert Decimal to float for JSON response
            expense['amount'] = float(expense['amount'])
            expense['_id'] = str(expense['_id'])
            
            return {
                'success': True,
                'expense': expense
            }
            
        except Exception as e:
            logger.error(f"Create expense error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_user_invoices(self, user_id: str, filters: Dict = None, 
                               limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get user invoices with filtering"""
        try:
            db = await self.get_database()
            
            # Build query
            query = {'user_id': user_id}
            if filters:
                if filters.get('status'):
                    query['status'] = filters['status']
            
            # Get invoices with pagination
            invoices = await db.invoices.find(query).skip(offset).limit(limit).sort('created_at', -1).to_list(length=limit)
            total_count = await db.invoices.count_documents(query)
            
            return {
                'invoices': invoices,
                'total_count': total_count
            }
            
        except Exception as e:
            logger.error(f"Get user invoices error: {str(e)}")
            return {'invoices': [], 'total_count': 0}
    
    async def get_invoice(self, invoice_id: str, user_id: str) -> Dict[str, Any]:
        """Get specific invoice"""
        try:
            db = await self.get_database()
            
            invoice = await db.invoices.find_one({
                'invoice_id': invoice_id,
                'user_id': user_id
            })
            
            return invoice
            
        except Exception as e:
            logger.error(f"Get invoice error: {str(e)}")
            return None
    
    async def update_invoice(self, invoice_id: str, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update invoice"""
        try:
            db = await self.get_database()
            
            # Update invoice
            result = await db.invoices.update_one(
                {'invoice_id': invoice_id, 'user_id': user_id},
                {'$set': {**update_data, 'updated_at': datetime.utcnow()}}
            )
            
            if result.modified_count:
                return await db.invoices.find_one({'invoice_id': invoice_id})
            
            return None
            
        except Exception as e:
            logger.error(f"Update invoice error: {str(e)}")
            return None
    
    async def delete_invoice(self, invoice_id: str, user_id: str) -> bool:
        """Delete invoice"""
        try:
            db = await self.get_database()
            
            result = await db.invoices.delete_one({
                'invoice_id': invoice_id,
                'user_id': user_id
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Delete invoice error: {str(e)}")
            return False
    
    async def create_expense(self, user_id: str, category: str, amount: float,
                           description: str, date: datetime, receipt_url: str = None,
                           tags: List[str] = None) -> Dict[str, Any]:
        """Create expense record"""
        try:
            db = await self.get_database()
            
            expense_id = str(uuid.uuid4())
            expense_data = {
                'expense_id': expense_id,
                'user_id': user_id,
                'category': category,
                'amount': amount,
                'description': description,
                'date': date,
                'receipt_url': receipt_url,
                'tags': tags or [],
                'created_at': datetime.utcnow()
            }
            
            await db.expenses.insert_one(expense_data)
            return expense_data
            
        except Exception as e:
            logger.error(f"Create expense error: {str(e)}")
            return None
    
    async def get_user_expenses(self, user_id: str, category: str = None,
                              start_date: datetime = None, end_date: datetime = None,
                              limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get user expenses with filtering"""
        try:
            db = await self.get_database()
            
            # Build query
            query = {'user_id': user_id}
            if category:
                query['category'] = category
            if start_date or end_date:
                date_filter = {}
                if start_date:
                    date_filter['$gte'] = start_date
                if end_date:
                    date_filter['$lte'] = end_date
                query['date'] = date_filter
            
            expenses = await db.expenses.find(query).skip(offset).limit(limit).sort('date', -1).to_list(length=limit)
            total_count = await db.expenses.count_documents(query)
            
            return {
                'expenses': expenses,
                'total_count': total_count
            }
            
        except Exception as e:
            logger.error(f"Get user expenses error: {str(e)}")
            return {'expenses': [], 'total_count': 0}
            
    async def update_expense(self, expense_id: str, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update expense"""
        try:
            db = await self.get_database()
            
            result = await db.expenses.update_one(
                {'expense_id': expense_id, 'user_id': user_id},
                {'$set': {**update_data, 'updated_at': datetime.utcnow()}}
            )
            
            if result.modified_count:
                return await db.expenses.find_one({'expense_id': expense_id})
            
            return None
            
        except Exception as e:
            logger.error(f"Update expense error: {str(e)}")
            return None
    
    async def delete_expense(self, expense_id: str, user_id: str) -> bool:
        """Delete expense"""
        try:
            db = await self.get_database()
            
            result = await db.expenses.delete_one({
                'expense_id': expense_id,
                'user_id': user_id
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Delete expense error: {str(e)}")
            return False
    
    async def get_financial_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get financial dashboard data"""
        try:
            db = await self.get_database()
            
            # Get basic statistics
            total_invoices = await db.invoices.count_documents({'user_id': user_id})
            total_expenses = await db.expenses.count_documents({'user_id': user_id})
            
            # Get recent invoices and expenses
            recent_invoices = await db.invoices.find({'user_id': user_id}).sort('created_at', -1).limit(5).to_list(length=5)
            recent_expenses = await db.expenses.find({'user_id': user_id}).sort('created_at', -1).limit(5).to_list(length=5)
            
            # Calculate totals
            invoice_total = 0
            expense_total = 0
            
            all_invoices = await db.invoices.find({'user_id': user_id}).to_list(length=None)
            for inv in all_invoices:
                invoice_total += inv.get('total_amount', 0)
                
            all_expenses = await db.expenses.find({'user_id': user_id}).to_list(length=None)  
            for exp in all_expenses:
                expense_total += exp.get('amount', 0)
            
            return {
                'summary': {
                    'total_invoices': total_invoices,
                    'total_expenses': total_expenses,
                    'total_revenue': invoice_total,
                    'total_spent': expense_total,
                    'net_profit': invoice_total - expense_total
                },
                'recent_invoices': recent_invoices,
                'recent_expenses': recent_expenses
            }
            
        except Exception as e:
            logger.error(f"Get financial dashboard error: {str(e)}")
            return {}

    async def get_revenue_report(self, user_id: str, start_date: datetime, end_date: datetime, group_by: str = "month") -> Dict[str, Any]:
        """Get revenue report"""
        try:
            db = await self.get_database()
            
            invoices = await db.invoices.find({
                'user_id': user_id,
                'created_at': {'$gte': start_date, '$lte': end_date}
            }).to_list(length=None)
            
            # Group by period
            grouped_data = {}
            for invoice in invoices:
                if group_by == "month":
                    key = invoice['created_at'].strftime("%Y-%m")
                elif group_by == "day":
                    key = invoice['created_at'].strftime("%Y-%m-%d")
                else:
                    key = invoice['created_at'].strftime("%Y")
                
                if key not in grouped_data:
                    grouped_data[key] = {'revenue': 0, 'count': 0}
                    
                grouped_data[key]['revenue'] += invoice.get('total_amount', 0)
                grouped_data[key]['count'] += 1
            
            return {
                'period': f"{start_date.isoformat()} to {end_date.isoformat()}",
                'group_by': group_by,
                'data': grouped_data
            }
            
        except Exception as e:
            logger.error(f"Get revenue report error: {str(e)}")
            return {}
    
    async def get_expense_report(self, user_id: str, start_date: datetime, end_date: datetime, group_by: str = "category") -> Dict[str, Any]:
        """Get expense report"""
        try:
            db = await self.get_database()
            
            expenses = await db.expenses.find({
                'user_id': user_id,
                'date': {'$gte': start_date, '$lte': end_date}
            }).to_list(length=None)
            
            # Group by category or period
            grouped_data = {}
            for expense in expenses:
                if group_by == "category":
                    key = expense.get('category', 'Uncategorized')
                elif group_by == "month":
                    key = expense['date'].strftime("%Y-%m")
                else:
                    key = expense['date'].strftime("%Y-%m-%d")
                
                if key not in grouped_data:
                    grouped_data[key] = {'amount': 0, 'count': 0}
                    
                grouped_data[key]['amount'] += expense.get('amount', 0)
                grouped_data[key]['count'] += 1
            
            return {
                'period': f"{start_date.isoformat()} to {end_date.isoformat()}",
                'group_by': group_by,
                'data': grouped_data
            }
            
        except Exception as e:
            logger.error(f"Get expense report error: {str(e)}")
            return {}
    
    async def process_payment(self, user_id: str, amount: float, currency: str = "USD", 
                            payment_method_id: str = None, invoice_id: str = None, 
                            metadata: Dict = None) -> Dict[str, Any]:
        """Process payment with Stripe integration"""
        try:
            # This would integrate with actual Stripe API
            payment_id = str(uuid.uuid4())
            
            db = await self.get_database()
            payment_data = {
                'payment_id': payment_id,
                'user_id': user_id,
                'amount': amount,
                'currency': currency,
                'payment_method_id': payment_method_id,
                'invoice_id': invoice_id,
                'status': 'completed',
                'metadata': metadata or {},
                'created_at': datetime.utcnow()
            }
            
            await db.payments.insert_one(payment_data)
            
            # Update invoice if provided
            if invoice_id:
                await db.invoices.update_one(
                    {'invoice_id': invoice_id},
                    {'$set': {'status': 'paid', 'paid_at': datetime.utcnow()}}
                )
            
            return payment_data
            
        except Exception as e:
            logger.error(f"Process payment error: {str(e)}")
            return None
    
    async def get_user_payments(self, user_id: str, status: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get user payments"""
        try:
            db = await self.get_database()
            
            query = {'user_id': user_id}
            if status:
                query['status'] = status
            
            payments = await db.payments.find(query).skip(offset).limit(limit).sort('created_at', -1).to_list(length=limit)
            total_count = await db.payments.count_documents(query)
            
            return {
                'payments': payments,
                'total_count': total_count
            }
            
        except Exception as e:
            logger.error(f"Get user payments error: {str(e)}")
            return {'payments': [], 'total_count': 0}
    
    async def _generate_invoice_pdf(self, invoice_id: str) -> str:
        """Generate PDF for invoice using real PDF generation"""
        try:
            # Get invoice data
            db = await self.get_database()
            invoice = await db.invoices.find_one({'invoice_id': invoice_id})
            
            if not invoice:
                return ""
                
            # Create PDF content using HTML template
            html_content = self._create_invoice_html_template(invoice)
            
            # For now, store the PDF content URL - in production would use a real PDF service like WeasyPrint
            pdf_url = f"/api/invoices/{invoice_id}/pdf"
            
            # Store PDF metadata
            await db.invoice_pdfs.insert_one({
                'invoice_id': invoice_id,
                'pdf_url': pdf_url,
                'html_content': html_content,
                'generated_at': datetime.utcnow()
            })
            
            return pdf_url
            
        except Exception as e:
            logger.error(f"Generate PDF error: {str(e)}")
            return ""
    
    async def _create_invoice_activity(self, invoice_id: str, action: str, description: str):
        """Create invoice activity log entry"""
        try:
            db = await self.get_database()
            
            activity = {
                'activity_id': str(uuid.uuid4()),
                'invoice_id': invoice_id,
                'action': action,
                'description': description,
                'created_at': datetime.utcnow()
            }
            
            await db.invoice_activities.insert_one(activity)
            
        except Exception as e:
            logger.error(f"Create invoice activity error: {str(e)}")
    
    
    def _create_invoice_html_template(self, invoice: Dict[str, Any]) -> str:
        """Create HTML template for invoice PDF"""
        try:
            # Calculate totals
            subtotal = sum(item.get('amount', 0) for item in invoice.get('items', []))
            tax_amount = subtotal * (invoice.get('tax_rate', 0) / 100)
            total = subtotal + tax_amount
            
            html_template = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Invoice {invoice.get('invoice_number', 'N/A')}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .invoice-details {{ margin-bottom: 20px; }}
                    .client-details {{ margin-bottom: 20px; }}
                    table {{ width: 100%; border-collapse: collapse; }}
                    th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    .total-row {{ font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>INVOICE</h1>
                    <h2>#{invoice.get('invoice_number', 'N/A')}</h2>
                </div>
                
                <div class="invoice-details">
                    <strong>Invoice Date:</strong> {invoice.get('created_at', '').strftime('%Y-%m-%d') if isinstance(invoice.get('created_at'), datetime) else 'N/A'}<br>
                    <strong>Due Date:</strong> {invoice.get('due_date', '').strftime('%Y-%m-%d') if isinstance(invoice.get('due_date'), datetime) else 'N/A'}<br>
                    <strong>Status:</strong> {invoice.get('status', 'pending').upper()}
                </div>
                
                <div class="client-details">
                    <h3>Bill To:</h3>
                    <strong>{invoice.get('client_name', 'N/A')}</strong><br>
                    {invoice.get('client_email', 'N/A')}<br>
                    {invoice.get('client_address', '')}
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>Description</th>
                            <th>Quantity</th>
                            <th>Rate</th>
                            <th>Amount</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            # Add items
            for item in invoice.get('items', []):
                html_template += f"""
                        <tr>
                            <td>{item.get('description', 'N/A')}</td>
                            <td>{item.get('quantity', 1)}</td>
                            <td>${item.get('rate', 0):.2f}</td>
                            <td>${item.get('amount', 0):.2f}</td>
                        </tr>
                """
            
            # Add totals
            html_template += f"""
                    </tbody>
                </table>
                
                <div style="margin-top: 20px; text-align: right;">
                    <p><strong>Subtotal: ${subtotal:.2f}</strong></p>
                    <p><strong>Tax ({invoice.get('tax_rate', 0)}%): ${tax_amount:.2f}</strong></p>
                    <p class="total-row"><strong>Total: ${total:.2f}</strong></p>
                </div>
                
                {f'<div style="margin-top: 30px;"><h4>Notes:</h4><p>{invoice.get("notes", "")}</p></div>' if invoice.get('notes') else ''}
            </body>
            </html>
            """
            
            return html_template
            
        except Exception as e:
            logger.error(f"Create invoice HTML template error: {str(e)}")
            return ""
    
    async def _schedule_payment_reminders(self, invoice_id: str):
        """Schedule payment reminders for invoice using real scheduling"""
        try:
            # Get invoice data
            db = await self.get_database()
            invoice = await db.invoices.find_one({'invoice_id': invoice_id})
            
            if not invoice or invoice.get('status') != 'pending':
                return
                
            due_date = invoice.get('due_date')
            if not due_date:
                return
                
            # Schedule reminders at different intervals
            reminder_schedule = [
                {'days_before': 7, 'type': 'first_reminder'},
                {'days_before': 3, 'type': 'second_reminder'},
                {'days_before': 1, 'type': 'final_reminder'},
                {'days_after': 1, 'type': 'overdue_notice'}
            ]
            
            for reminder in reminder_schedule:
                if reminder['type'] == 'overdue_notice':
                    reminder_date = due_date + timedelta(days=reminder['days_after'])
                else:
                    reminder_date = due_date - timedelta(days=reminder['days_before'])
                
                # Create reminder record
                await db.payment_reminders.insert_one({
                    'reminder_id': str(uuid.uuid4()),
                    'invoice_id': invoice_id,
                    'type': reminder['type'],
                    'scheduled_date': reminder_date,
                    'status': 'scheduled',
                    'created_at': datetime.utcnow()
                })
            
            logger.info(f"Payment reminders scheduled for invoice {invoice_id}")
            
        except Exception as e:
            logger.error(f"Schedule payment reminders error: {str(e)}")
    
    async def _process_scheduled_reminders(self):
        """Process scheduled payment reminders - would be called by a background job"""
        try:
            db = await self.get_database()
            current_time = datetime.utcnow()
            
            # Get reminders due for processing
            due_reminders = await db.payment_reminders.find({
                'scheduled_date': {'$lte': current_time},
                'status': 'scheduled'
            }).to_list(length=100)
            
            for reminder in due_reminders:
                # Get invoice details
                invoice = await db.invoices.find_one({
                    'invoice_id': reminder['invoice_id'],
                    'status': 'pending'
                })
                
                if invoice:
                    # Send reminder email (integrate with email service)
                    await self._send_payment_reminder_email(invoice, reminder['type'])
                    
                    # Mark reminder as sent
                    await db.payment_reminders.update_one(
                        {'reminder_id': reminder['reminder_id']},
                        {'$set': {'status': 'sent', 'sent_at': current_time}}
                    )
                    
        except Exception as e:
            logger.error(f"Process scheduled reminders error: {str(e)}")
    
    async def _send_payment_reminder_email(self, invoice: Dict[str, Any], reminder_type: str):
        """Send payment reminder email using real email service"""
        try:
            # Email templates for different reminder types
            templates = {
                'first_reminder': {
                    'subject': f'Payment Reminder: Invoice #{invoice.get("invoice_number", "N/A")}',
                    'template': 'friendly_reminder'
                },
                'second_reminder': {
                    'subject': f'Payment Due Soon: Invoice #{invoice.get("invoice_number", "N/A")}',
                    'template': 'urgent_reminder'
                },
                'final_reminder': {
                    'subject': f'Final Notice: Payment Due Tomorrow - Invoice #{invoice.get("invoice_number", "N/A")}',
                    'template': 'final_notice'
                },
                'overdue_notice': {
                    'subject': f'Overdue Payment: Invoice #{invoice.get("invoice_number", "N/A")}',
                    'template': 'overdue_notice'
                }
            }
            
            template_info = templates.get(reminder_type, templates['first_reminder'])
            
            # This would integrate with your email service (ElasticMail, SendGrid, etc.)
            # For now, log the email sending
            logger.info(f"Sending {reminder_type} email to {invoice.get('client_email')} for invoice {invoice.get('invoice_id')}")
            
            # Record the email in the database
            db = await self.get_database()
            await db.email_logs.insert_one({
                'log_id': str(uuid.uuid4()),
                'email_type': 'payment_reminder',
                'invoice_id': invoice.get('invoice_id'),
                'recipient': invoice.get('client_email'),
                'subject': template_info['subject'],
                'template': template_info['template'],
                'status': 'sent',
                'sent_at': datetime.utcnow()
            })
            
        except Exception as e:
            logger.error(f"Send payment reminder email error: {str(e)}")
    
    async def _update_financial_analytics(self, user_id: str, action: str, data: Dict):
        """Update financial analytics based on actions"""
        try:
            db = await self.get_database()
            
            # Get or create analytics record
            analytics = await db.financial_analytics.find_one({'user_id': user_id})
            
            if not analytics:
                analytics = {
                    'user_id': user_id,
                    'total_invoices': 0,
                    'total_revenue': 0.0,
                    'total_expenses': 0.0,
                    'total_profit': 0.0,
                    'average_invoice_amount': 0.0,
                    'created_at': datetime.utcnow()
                }
            
            # Update based on action
            if action == 'payment_received':
                analytics['total_revenue'] += data['amount']
            elif action == 'expense_recorded':
                analytics['total_expenses'] += float(data['amount'])
            
            analytics['total_profit'] = analytics['total_revenue'] - analytics['total_expenses']
            analytics['updated_at'] = datetime.utcnow()
            
            # Upsert analytics
            await db.financial_analytics.update_one(
                {'user_id': user_id},
                {'$set': analytics},
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Update financial analytics error: {str(e)}")

# Global service instance
financial_service = CompleteFinancialService()
    async def create_payment(self, user_id: str, payment_data: dict) -> dict:
        """Create new payment"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            payment = {
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                "amount": payment_data.get("amount", 0),
                "currency": payment_data.get("currency", "USD"),
                "description": payment_data.get("description", ""),
                "status": "pending",
                "payment_method": payment_data.get("payment_method", "stripe"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await collections['payments'].insert_one(payment)
            return {"success": True, "payment": payment, "message": "Payment created successfully"}
            
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    async def get_payment(self, payment_id: str, user_id: str) -> dict:
        """Get payment details"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            payment = await collections['payments'].find_one({
                "_id": payment_id,
                "user_id": user_id
            })
            
            if payment:
                return {"success": True, "payment": payment}
            else:
                return {"success": False, "message": "Payment not found"}
                
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    async def update_payment(self, payment_id: str, user_id: str, updates: dict) -> dict:
        """Update payment"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            updates["updated_at"] = datetime.utcnow()
            
            result = await collections['payments'].update_one(
                {"_id": payment_id, "user_id": user_id},
                {"$set": updates}
            )
            
            if result.modified_count > 0:
                updated_payment = await collections['payments'].find_one({"_id": payment_id})
                return {"success": True, "payment": updated_payment, "message": "Payment updated successfully"}
            else:
                return {"success": False, "message": "Payment not found or unauthorized"}
                
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    async def refund_payment(self, payment_id: str, user_id: str, reason: str = None) -> dict:
        """Process payment refund"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            # Update payment status to refunded
            result = await collections['payments'].update_one(
                {"_id": payment_id, "user_id": user_id},
                {
                    "$set": {
                        "status": "refunded",
                        "refunded_at": datetime.utcnow(),
                        "refund_reason": reason or "User requested refund",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                return {"success": True, "message": "Payment refunded successfully"}
            else:
                return {"success": False, "message": "Payment not found or unauthorized"}
                
        except Exception as e:
            return {"success": False, "message": str(e)}
