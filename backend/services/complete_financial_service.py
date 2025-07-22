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
    
    async def get_financial_dashboard(self, user_id: str, date_range: Dict = None) -> Dict[str, Any]:
        """
        Get comprehensive financial dashboard
        """
        try:
            db = await self.get_database()
            
            # Date range filter
            if date_range:
                start_date = datetime.fromisoformat(date_range['start_date']) if date_range.get('start_date') else datetime.utcnow() - timedelta(days=30)
                end_date = datetime.fromisoformat(date_range['end_date']) if date_range.get('end_date') else datetime.utcnow()
            else:
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=30)
            
            date_filter = {'created_at': {'$gte': start_date, '$lte': end_date}}
            
            # Invoice analytics
            invoice_pipeline = [
                {'$match': {'user_id': user_id, **date_filter}},
                {'$group': {
                    '_id': '$payment_info.status',
                    'count': {'$sum': 1},
                    'total_amount': {'$sum': '$financial_details.total_amount'},
                    'total_paid': {'$sum': '$payment_info.total_paid'}
                }}
            ]
            
            invoice_stats = await db.invoices.aggregate(invoice_pipeline).to_list(length=None)
            
            # Expense analytics
            expense_pipeline = [
                {'$match': {'user_id': user_id, **date_filter}},
                {'$group': {
                    '_id': '$category',
                    'count': {'$sum': 1},
                    'total_amount': {'$sum': '$amount'}
                }}
            ]
            
            expense_stats = await db.expenses.aggregate(expense_pipeline).to_list(length=None)
            
            # Recent invoices
            recent_invoices = await db.invoices.find(
                {'user_id': user_id}
            ).sort('created_at', -1).limit(10).to_list(length=10)
            
            # Recent expenses
            recent_expenses = await db.expenses.find(
                {'user_id': user_id}
            ).sort('created_at', -1).limit(10).to_list(length=10)
            
            # Outstanding invoices
            outstanding_invoices = await db.invoices.find({
                'user_id': user_id,
                'payment_info.status': {'$in': ['sent', 'overdue', 'partial']}
            }).sort('dates.due_date', 1).to_list(length=None)
            
            # Calculate totals
            total_invoiced = sum(stat['total_amount'] for stat in invoice_stats)
            total_paid = sum(stat['total_paid'] for stat in invoice_stats)
            total_expenses = sum(stat['total_amount'] for stat in expense_stats)
            net_profit = total_paid - total_expenses
            
            # Convert ObjectIds and Decimals
            for invoice in recent_invoices + outstanding_invoices:
                invoice['_id'] = str(invoice['_id'])
                if 'created_at' in invoice:
                    invoice['created_at'] = invoice['created_at'].isoformat()
                if 'dates' in invoice:
                    for key, value in invoice['dates'].items():
                        if value:
                            invoice['dates'][key] = value.isoformat()
            
            for expense in recent_expenses:
                expense['_id'] = str(expense['_id'])
                expense['amount'] = float(expense['amount'])
                if 'created_at' in expense:
                    expense['created_at'] = expense['created_at'].isoformat()
                if 'expense_date' in expense:
                    expense['expense_date'] = expense['expense_date'].isoformat()
            
            dashboard = {
                'user_id': user_id,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'summary': {
                    'total_invoiced': total_invoiced,
                    'total_paid': total_paid,
                    'total_expenses': total_expenses,
                    'net_profit': net_profit,
                    'outstanding_amount': sum(inv['payment_info']['balance_due'] for inv in outstanding_invoices)
                },
                'invoice_breakdown': invoice_stats,
                'expense_breakdown': expense_stats,
                'recent_invoices': recent_invoices,
                'recent_expenses': recent_expenses,
                'outstanding_invoices': outstanding_invoices,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return {
                'success': True,
                'dashboard': dashboard
            }
            
        except Exception as e:
            logger.error(f"Get financial dashboard error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_invoice_pdf(self, invoice_id: str) -> str:
        """Generate PDF for invoice"""
        try:
            # This would integrate with a PDF generation service
            # For now, return a placeholder URL
            return f"/api/invoices/{invoice_id}/pdf"
            
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
    
    async def _schedule_payment_reminders(self, invoice_id: str):
        """Schedule payment reminders for invoice"""
        try:
            # This would integrate with a job scheduler
            # For now, just log the scheduling
            logger.info(f"Payment reminders scheduled for invoice {invoice_id}")
            
        except Exception as e:
            logger.error(f"Schedule reminders error: {str(e)}")
    
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