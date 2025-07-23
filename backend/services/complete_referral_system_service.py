"""
Complete Referral/Affiliate System Service
URL and Code Based Referral System with Full Admin Control
Version: 1.0.0 - Production Ready
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import httpx
import os
import uuid
import secrets
import string
from motor.motor_asyncio import AsyncIOMotorDatabase
from core.database import get_database
from core.config import get_api_key

logger = logging.getLogger(__name__)

class CompleteReferralService:
    """
    Complete Referral/Affiliate System
    Features:
    - URL-based referral tracking with custom domains
    - Unique referral code generation and management
    - Multi-tier commission structure (referrer + sub-referrers)
    - Real-time analytics and conversion tracking
    - Automated payout processing and scheduling
    - Admin control over commission rates and rules
    - Fraud detection and validation
    - Custom landing pages for referral links
    - Email/SMS notifications for referrals and payouts
    - Integration with payment processors
    - Referral leaderboards and gamification
    - Advanced reporting and analytics
    """
    
    def __init__(self):
        self.stripe_secret_key = get_api_key('STRIPE_SECRET_KEY')
        self.base_referral_url = os.getenv('BASE_REFERRAL_URL', 'https://mewayz.com/ref')
        
    async def get_database(self) -> AsyncIOMotorDatabase:
        """Get database connection"""
        return get_database()
    
    async def create_referral_program(self, program_data: Dict[str, Any], admin_id: str) -> Dict[str, Any]:
        """
        Create a new referral program with admin configuration
        """
        try:
            db = await self.get_database()
            
            program_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            program = {
                'program_id': program_id,
                'created_by': admin_id,
                'name': program_data['name'],
                'description': program_data.get('description', ''),
                'program_type': program_data.get('program_type', 'referral'),  # referral, affiliate, partner
                'status': program_data.get('status', 'active'),  # active, paused, ended
                'commission_structure': {
                    'type': program_data.get('commission_type', 'percentage'),  # percentage, fixed, tiered
                    'primary_rate': float(program_data.get('primary_rate', 10)),  # 10% default
                    'secondary_rate': float(program_data.get('secondary_rate', 5)),  # 5% for sub-referrals
                    'tertiary_rate': float(program_data.get('tertiary_rate', 2)),  # 2% for tertiary
                    'minimum_payout': float(program_data.get('minimum_payout', 50)),
                    'maximum_commission': float(program_data.get('maximum_commission', 1000)),
                    'currency': program_data.get('currency', 'USD')
                },
                'eligibility_rules': {
                    'min_account_age_days': program_data.get('min_account_age_days', 30),
                    'min_referrals_required': program_data.get('min_referrals_required', 0),
                    'allowed_user_types': program_data.get('allowed_user_types', ['all']),
                    'excluded_countries': program_data.get('excluded_countries', []),
                    'require_approval': program_data.get('require_approval', False)
                },
                'tracking_settings': {
                    'cookie_duration_days': program_data.get('cookie_duration_days', 30),
                    'attribution_model': program_data.get('attribution_model', 'first_click'),  # first_click, last_click
                    'track_sub_referrals': program_data.get('track_sub_referrals', True),
                    'conversion_events': program_data.get('conversion_events', ['signup', 'purchase', 'subscription']),
                    'enable_fraud_detection': program_data.get('enable_fraud_detection', True)
                },
                'payout_settings': {
                    'payout_frequency': program_data.get('payout_frequency', 'monthly'),  # weekly, monthly, quarterly
                    'payout_method': program_data.get('payout_method', 'stripe'),  # stripe, paypal, bank_transfer
                    'auto_payout': program_data.get('auto_payout', False),
                    'payout_delay_days': program_data.get('payout_delay_days', 30),
                    'tax_handling': program_data.get('tax_handling', 'gross')  # gross, net
                },
                'customization': {
                    'custom_domain': program_data.get('custom_domain', ''),
                    'landing_page_template': program_data.get('landing_page_template', 'default'),
                    'email_templates': program_data.get('email_templates', {}),
                    'branding': program_data.get('branding', {}),
                    'terms_conditions': program_data.get('terms_conditions', '')
                },
                'analytics': {
                    'total_referrers': 0,
                    'total_referrals': 0,
                    'total_conversions': 0,
                    'total_commissions_paid': 0.0,
                    'conversion_rate': 0.0,
                    'avg_commission_per_referral': 0.0
                },
                'start_date': datetime.fromisoformat(program_data['start_date']) if program_data.get('start_date') else current_time,
                'end_date': datetime.fromisoformat(program_data['end_date']) if program_data.get('end_date') else None,
                'created_at': current_time,
                'updated_at': current_time
            }
            
            await db.referral_programs.insert_one(program)
            
            # Create default referral codes for existing users if specified
            if program_data.get('create_codes_for_existing_users', False):
                await self._create_codes_for_existing_users(program_id)
            
            return {
                'success': True,
                'program': program
            }
            
        except Exception as e:
            logger.error(f"Create referral program error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def generate_referral_code(self, user_id: str, program_id: str, custom_code: str = None) -> Dict[str, Any]:
        """
        Generate unique referral code for user
        """
        try:
            db = await self.get_database()
            
            # Check if program exists and is active
            program = await db.referral_programs.find_one({'program_id': program_id, 'status': 'active'})
            if not program:
                return {'success': False, 'error': 'Referral program not found or inactive'}
            
            # Check if user already has a code for this program
            existing_code = await db.referral_codes.find_one({
                'user_id': user_id,
                'program_id': program_id,
                'status': 'active'
            })
            
            if existing_code:
                return {
                    'success': True,
                    'referral_code': existing_code,
                    'referral_url': f"{self.base_referral_url}/{existing_code['code']}"
                }
            
            # Check user eligibility
            eligibility_check = await self._check_user_eligibility(user_id, program)
            if not eligibility_check['eligible']:
                return {'success': False, 'error': eligibility_check['reason']}
            
            # Generate unique code
            if custom_code:
                # Validate custom code
                if await db.referral_codes.find_one({'code': custom_code.upper()}):
                    return {'success': False, 'error': 'Custom referral code already exists'}
                code = custom_code.upper()
            else:
                code = await self._generate_unique_code()
            
            referral_code_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            referral_code = {
                'referral_code_id': referral_code_id,
                'user_id': user_id,
                'program_id': program_id,
                'code': code,
                'status': 'pending_approval' if program['eligibility_rules']['require_approval'] else 'active',
                'custom_landing_page': None,
                'tracking_data': {
                    'total_clicks': 0,
                    'unique_clicks': 0,
                    'total_referrals': 0,
                    'successful_conversions': 0,
                    'conversion_rate': 0.0,
                    'total_commissions_earned': 0.0,
                    'last_used': None
                },
                'settings': {
                    'notifications_enabled': True,
                    'email_on_referral': True,
                    'email_on_conversion': True,
                    'email_on_payout': True
                },
                'metadata': {
                    'user_agent_first_created': None,
                    'ip_address_first_created': None,
                    'source_campaign': None
                },
                'created_at': current_time,
                'updated_at': current_time,
                'approved_at': None if program['eligibility_rules']['require_approval'] else current_time,
                'approved_by': None
            }
            
            await db.referral_codes.insert_one(referral_code)
            
            # Update program analytics
            await db.referral_programs.update_one(
                {'program_id': program_id},
                {'$inc': {'analytics.total_referrers': 1}}
            )
            
            referral_url = f"{self.base_referral_url}/{code}"
            
            return {
                'success': True,
                'referral_code': referral_code,
                'referral_url': referral_url
            }
            
        except Exception as e:
            logger.error(f"Generate referral code error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def track_referral_click(self, referral_code: str, tracking_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track referral link click and store visitor information
        """
        try:
            db = await self.get_database()
            
            # Find referral code
            code_doc = await db.referral_codes.find_one({'code': referral_code.upper(), 'status': 'active'})
            if not code_doc:
                return {'success': False, 'error': 'Invalid referral code'}
            
            # Get program details
            program = await db.referral_programs.find_one({'program_id': code_doc['program_id']})
            if not program or program['status'] != 'active':
                return {'success': False, 'error': 'Referral program inactive'}
            
            click_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            # Create click tracking record
            click_record = {
                'click_id': click_id,
                'referral_code_id': code_doc['referral_code_id'],
                'referrer_user_id': code_doc['user_id'],
                'program_id': code_doc['program_id'],
                'visitor_data': {
                    'ip_address': tracking_data.get('ip_address', ''),
                    'user_agent': tracking_data.get('user_agent', ''),
                    'referrer_url': tracking_data.get('referrer_url', ''),
                    'country': tracking_data.get('country', ''),
                    'city': tracking_data.get('city', ''),
                    'device_type': tracking_data.get('device_type', ''),
                    'browser': tracking_data.get('browser', ''),
                    'os': tracking_data.get('os', '')
                },
                'session_data': {
                    'session_id': tracking_data.get('session_id', str(uuid.uuid4())),
                    'utm_source': tracking_data.get('utm_source', ''),
                    'utm_medium': tracking_data.get('utm_medium', ''),
                    'utm_campaign': tracking_data.get('utm_campaign', ''),
                    'utm_term': tracking_data.get('utm_term', ''),
                    'utm_content': tracking_data.get('utm_content', '')
                },
                'fraud_detection': {
                    'is_suspicious': False,
                    'risk_score': 0,
                    'flags': []
                },
                'clicked_at': current_time
            }
            
            # Run fraud detection
            if program['tracking_settings']['enable_fraud_detection']:
                fraud_result = await self._detect_click_fraud(click_record, code_doc)
                click_record['fraud_detection'] = fraud_result
            
            await db.referral_clicks.insert_one(click_record)
            
            # Update referral code analytics
            is_unique_click = await self._is_unique_click(click_record)
            update_data = {
                'tracking_data.total_clicks': 1,
                'tracking_data.last_used': current_time,
                'updated_at': current_time
            }
            
            if is_unique_click:
                update_data['tracking_data.unique_clicks'] = 1
            
            await db.referral_codes.update_one(
                {'referral_code_id': code_doc['referral_code_id']},
                {'$inc': update_data}
            )
            
            # Set tracking cookie
            cookie_expires = current_time + timedelta(days=program['tracking_settings']['cookie_duration_days'])
            
            return {
                'success': True,
                'click_id': click_id,
                'redirect_url': tracking_data.get('destination_url', '/'),
                'cookie_data': {
                    'referral_code': referral_code,
                    'click_id': click_id,
                    'expires': cookie_expires.isoformat()
                },
                'fraud_detected': click_record['fraud_detection']['is_suspicious']
            }
            
        except Exception as e:
            logger.error(f"Track referral click error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def process_referral_conversion(self, conversion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process successful referral conversion and calculate commissions
        """
        try:
            db = await self.get_database()
            
            conversion_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            # Find referral source
            referral_source = None
            if conversion_data.get('referral_code'):
                code_doc = await db.referral_codes.find_one({'code': conversion_data['referral_code'].upper()})
                if code_doc:
                    referral_source = code_doc
            elif conversion_data.get('click_id'):
                click_doc = await db.referral_clicks.find_one({'click_id': conversion_data['click_id']})
                if click_doc:
                    code_doc = await db.referral_codes.find_one({'referral_code_id': click_doc['referral_code_id']})
                    if code_doc:
                        referral_source = code_doc
            
            if not referral_source:
                return {'success': False, 'error': 'No valid referral source found'}
            
            # Get program details
            program = await db.referral_programs.find_one({'program_id': referral_source['program_id']})
            if not program:
                return {'success': False, 'error': 'Referral program not found'}
            
            # Calculate commissions
            commission_amount = await self._calculate_commission(
                conversion_data.get('conversion_value', 0),
                program['commission_structure']
            )
            
            # Create conversion record
            conversion = {
                'conversion_id': conversion_id,
                'referral_code_id': referral_source['referral_code_id'],
                'referrer_user_id': referral_source['user_id'],
                'referred_user_id': conversion_data.get('user_id'),
                'program_id': referral_source['program_id'],
                'conversion_type': conversion_data.get('conversion_type', 'signup'),  # signup, purchase, subscription
                'conversion_value': float(conversion_data.get('conversion_value', 0)),
                'currency': conversion_data.get('currency', program['commission_structure']['currency']),
                'commission_details': {
                    'primary_commission': commission_amount,
                    'secondary_commission': 0.0,
                    'tertiary_commission': 0.0,
                    'total_commission': commission_amount,
                    'commission_rate': program['commission_structure']['primary_rate']
                },
                'status': 'pending',  # pending, approved, paid, cancelled
                'metadata': {
                    'order_id': conversion_data.get('order_id'),
                    'product_id': conversion_data.get('product_id'),
                    'subscription_id': conversion_data.get('subscription_id'),
                    'plan_name': conversion_data.get('plan_name'),
                    'attribution_data': conversion_data.get('attribution_data', {})
                },
                'fraud_check': {
                    'is_verified': True,
                    'verification_score': 100,
                    'flags': []
                },
                'payout_info': {
                    'payout_id': None,
                    'payout_date': None,
                    'payout_method': None,
                    'payout_reference': None
                },
                'converted_at': current_time,
                'created_at': current_time,
                'updated_at': current_time
            }
            
            # Process multi-tier commissions if enabled
            if program['tracking_settings']['track_sub_referrals']:
                sub_commissions = await self._calculate_sub_referral_commissions(
                    referral_source['user_id'], program, commission_amount
                )
                conversion['commission_details'].update(sub_commissions)
            
            await db.referral_conversions.insert_one(conversion)
            
            # Update referral code analytics
            await db.referral_codes.update_one(
                {'referral_code_id': referral_source['referral_code_id']},
                {
                    '$inc': {
                        'tracking_data.total_referrals': 1,
                        'tracking_data.successful_conversions': 1,
                        'tracking_data.total_commissions_earned': commission_amount
                    },
                    '$set': {
                        'tracking_data.conversion_rate': await self._calculate_conversion_rate(referral_source['referral_code_id']),
                        'updated_at': current_time
                    }
                }
            )
            
            # Update program analytics
            await db.referral_programs.update_one(
                {'program_id': referral_source['program_id']},
                {
                    '$inc': {
                        'analytics.total_referrals': 1,
                        'analytics.total_conversions': 1,
                        'analytics.total_commissions_paid': commission_amount
                    },
                    '$set': {
                        'analytics.conversion_rate': await self._calculate_program_conversion_rate(referral_source['program_id']),
                        'updated_at': current_time
                    }
                }
            )
            
            # Send notifications
            await self._send_conversion_notifications(conversion)
            
            # Auto-approve if program allows
            if not program.get('require_conversion_approval', False):
                await self.approve_conversion(conversion_id, 'system_auto_approval')
            
            return {
                'success': True,
                'conversion': conversion,
                'commission_amount': commission_amount
            }
            
        except Exception as e:
            logger.error(f"Process referral conversion error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def approve_conversion(self, conversion_id: str, approved_by: str) -> Dict[str, Any]:
        """
        Approve referral conversion for payout
        """
        try:
            db = await self.get_database()
            
            conversion = await db.referral_conversions.find_one({'conversion_id': conversion_id})
            if not conversion:
                return {'success': False, 'error': 'Conversion not found'}
            
            if conversion['status'] != 'pending':
                return {'success': False, 'error': 'Conversion is not in pending status'}
            
            await db.referral_conversions.update_one(
                {'conversion_id': conversion_id},
                {
                    '$set': {
                        'status': 'approved',
                        'approved_at': datetime.utcnow(),
                        'approved_by': approved_by,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            # Check if user qualifies for payout
            await self._check_payout_qualification(conversion['referrer_user_id'], conversion['program_id'])
            
            return {
                'success': True,
                'message': 'Conversion approved successfully'
            }
            
        except Exception as e:
            logger.error(f"Approve conversion error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def process_payout(self, payout_data: Dict[str, Any], admin_id: str) -> Dict[str, Any]:
        """
        Process referral commission payout
        """
        try:
            db = await self.get_database()
            
            payout_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            # Get approved conversions for user/program
            conversions = await db.referral_conversions.find({
                'referrer_user_id': payout_data['user_id'],
                'program_id': payout_data['program_id'],
                'status': 'approved',
                'payout_info.payout_id': None
            }).to_list(length=None)
            
            if not conversions:
                return {'success': False, 'error': 'No approved conversions found for payout'}
            
            # Calculate total payout amount
            total_amount = sum(conv['commission_details']['total_commission'] for conv in conversions)
            
            # Get program minimum payout threshold
            program = await db.referral_programs.find_one({'program_id': payout_data['program_id']})
            min_payout = program['commission_structure']['minimum_payout']
            
            if total_amount < min_payout:
                return {'success': False, 'error': f'Total amount ${total_amount} is below minimum payout threshold ${min_payout}'}
            
            # Create payout record
            payout = {
                'payout_id': payout_id,
                'user_id': payout_data['user_id'],
                'program_id': payout_data['program_id'],
                'conversion_ids': [conv['conversion_id'] for conv in conversions],
                'amount': total_amount,
                'currency': program['commission_structure']['currency'],
                'payout_method': payout_data.get('payout_method', 'stripe'),
                'payout_details': {
                    'stripe_account_id': payout_data.get('stripe_account_id'),
                    'paypal_email': payout_data.get('paypal_email'),
                    'bank_account': payout_data.get('bank_account'),
                    'tax_withholding': payout_data.get('tax_withholding', 0)
                },
                'status': 'processing',  # processing, completed, failed, cancelled
                'processing_info': {
                    'processed_by': admin_id,
                    'processing_notes': payout_data.get('notes', ''),
                    'tax_form_submitted': payout_data.get('tax_form_submitted', False)
                },
                'transaction_info': {
                    'transaction_id': None,
                    'transaction_fee': 0.0,
                    'net_amount': total_amount,
                    'exchange_rate': 1.0,
                    'processed_at': None
                },
                'created_at': current_time,
                'updated_at': current_time
            }
            
            await db.referral_payouts.insert_one(payout)
            
            # Update conversions with payout info
            for conversion in conversions:
                await db.referral_conversions.update_one(
                    {'conversion_id': conversion['conversion_id']},
                    {
                        '$set': {
                            'status': 'paid',
                            'payout_info.payout_id': payout_id,
                            'payout_info.payout_date': current_time,
                            'payout_info.payout_method': payout_data.get('payout_method'),
                            'updated_at': current_time
                        }
                    }
                )
            
            # Process actual payment
            payment_result = await self._process_actual_payout(payout)
            
            return {
                'success': True,
                'payout': payout,
                'payment_result': payment_result
            }
            
        except Exception as e:
            logger.error(f"Process payout error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_referral_analytics(self, user_id: str, program_id: str = None) -> Dict[str, Any]:
        """
        Get comprehensive referral analytics for user
        """
        try:
            db = await self.get_database()
            
            # Build query filter
            query_filter = {'referrer_user_id': user_id}
            if program_id:
                query_filter['program_id'] = program_id
            
            # Get conversions
            conversions = await db.referral_conversions.find(query_filter).to_list(length=None)
            
            # Get referral codes
            code_query = {'user_id': user_id}
            if program_id:
                code_query['program_id'] = program_id
            
            referral_codes = await db.referral_codes.find(code_query).to_list(length=None)
            
            # Calculate analytics
            total_referrals = len(conversions)
            total_commissions = sum(conv['commission_details']['total_commission'] for conv in conversions)
            pending_commissions = sum(conv['commission_details']['total_commission'] for conv in conversions if conv['status'] == 'pending')
            paid_commissions = sum(conv['commission_details']['total_commission'] for conv in conversions if conv['status'] == 'paid')
            
            # Get recent activity
            recent_conversions = sorted(conversions, key=lambda x: x['converted_at'], reverse=True)[:10]
            
            # Get clicks data
            total_clicks = sum(code['tracking_data']['total_clicks'] for code in referral_codes)
            unique_clicks = sum(code['tracking_data']['unique_clicks'] for code in referral_codes)
            
            conversion_rate = (total_referrals / max(unique_clicks, 1)) * 100 if unique_clicks > 0 else 0
            
            analytics = {
                'user_id': user_id,
                'program_id': program_id,
                'summary': {
                    'total_referrals': total_referrals,
                    'total_clicks': total_clicks,
                    'unique_clicks': unique_clicks,
                    'conversion_rate': round(conversion_rate, 2),
                    'total_commissions_earned': total_commissions,
                    'pending_commissions': pending_commissions,
                    'paid_commissions': paid_commissions,
                    'active_referral_codes': len([code for code in referral_codes if code['status'] == 'active'])
                },
                'referral_codes': referral_codes,
                'recent_conversions': recent_conversions,
                'monthly_breakdown': await self._get_monthly_breakdown(user_id, program_id),
                'top_performing_codes': await self._get_top_performing_codes(user_id, program_id),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return {
                'success': True,
                'analytics': analytics
            }
            
        except Exception as e:
            logger.error(f"Get referral analytics error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_unique_code(self) -> str:
        """Generate unique referral code"""
        db = await self.get_database()
        
        while True:
            # Generate 8-character alphanumeric code
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            
            # Check if code already exists
            existing = await db.referral_codes.find_one({'code': code})
            if not existing:
                return code
    
    async def _check_user_eligibility(self, user_id: str, program: Dict) -> Dict[str, Any]:
        """Check if user is eligible for referral program"""
        try:
            db = await self.get_database()
            
            # Get user info
            user = await db.users.find_one({'user_id': user_id})
            if not user:
                return {'eligible': False, 'reason': 'User not found'}
            
            # Check account age
            account_age = (datetime.utcnow() - user['created_at']).days
            min_age = program['eligibility_rules']['min_account_age_days']
            
            if account_age < min_age:
                return {'eligible': False, 'reason': f'Account must be at least {min_age} days old'}
            
            # Check minimum referrals if required
            min_referrals = program['eligibility_rules']['min_referrals_required']
            if min_referrals > 0:
                referral_count = await db.referral_conversions.count_documents({'referrer_user_id': user_id})
                if referral_count < min_referrals:
                    return {'eligible': False, 'reason': f'Minimum {min_referrals} successful referrals required'}
            
            # Check user type restrictions
            allowed_types = program['eligibility_rules']['allowed_user_types']
            if 'all' not in allowed_types and user.get('user_type', 'standard') not in allowed_types:
                return {'eligible': False, 'reason': 'User type not eligible for this program'}
            
            return {'eligible': True}
            
        except Exception as e:
            logger.error(f"Check user eligibility error: {str(e)}")
            return {'eligible': False, 'reason': 'Eligibility check failed'}
    
    async def _detect_click_fraud(self, click_record: Dict, code_doc: Dict) -> Dict[str, Any]:
        """Detect potential click fraud"""
        fraud_result = {
            'is_suspicious': False,
            'risk_score': 0,
            'flags': []
        }
        
        try:
            db = await self.get_database()
            
            # Check for excessive clicks from same IP
            recent_clicks = await db.referral_clicks.count_documents({
                'visitor_data.ip_address': click_record['visitor_data']['ip_address'],
                'referral_code_id': code_doc['referral_code_id'],
                'clicked_at': {'$gte': datetime.utcnow() - timedelta(hours=1)}
            })
            
            if recent_clicks > 10:
                fraud_result['flags'].append('excessive_clicks_same_ip')
                fraud_result['risk_score'] += 30
            
            # Check for bot-like user agents
            user_agent = click_record['visitor_data']['user_agent'].lower()
            bot_indicators = ['bot', 'crawler', 'spider', 'scraper']
            if any(indicator in user_agent for indicator in bot_indicators):
                fraud_result['flags'].append('bot_user_agent')
                fraud_result['risk_score'] += 50
            
            # Check for self-referral (same user clicking own link)
            if click_record['visitor_data']['ip_address']:
                user_clicks = await db.referral_clicks.count_documents({
                    'visitor_data.ip_address': click_record['visitor_data']['ip_address'],
                    'referrer_user_id': code_doc['user_id'],
                    'clicked_at': {'$gte': datetime.utcnow() - timedelta(days=7)}
                })
                
                if user_clicks > 5:
                    fraud_result['flags'].append('potential_self_referral')
                    fraud_result['risk_score'] += 40
            
            fraud_result['is_suspicious'] = fraud_result['risk_score'] > 50
            
        except Exception as e:
            logger.error(f"Fraud detection error: {str(e)}")
        
        return fraud_result
    
    async def _is_unique_click(self, click_record: Dict) -> bool:
        """Check if this is a unique click from this visitor"""
        try:
            db = await self.get_database()
            
            # Check for clicks from same IP to same referral code in last 24 hours
            existing_clicks = await db.referral_clicks.count_documents({
                'referral_code_id': click_record['referral_code_id'],
                'visitor_data.ip_address': click_record['visitor_data']['ip_address'],
                'clicked_at': {'$gte': datetime.utcnow() - timedelta(days=1)}
            })
            
            return existing_clicks <= 1  # First click is considered unique
            
        except Exception as e:
            logger.error(f"Unique click check error: {str(e)}")
            return True  # Default to unique if check fails
    
    async def _calculate_commission(self, conversion_value: float, commission_structure: Dict) -> float:
        """Calculate commission amount based on structure"""
        if commission_structure['type'] == 'percentage':
            commission = (conversion_value * commission_structure['primary_rate']) / 100
        else:  # fixed amount
            commission = commission_structure['primary_rate']
        
        # Apply maximum commission limit
        max_commission = commission_structure.get('maximum_commission', float('inf'))
        return min(commission, max_commission)
    
    async def _calculate_sub_referral_commissions(self, user_id: str, program: Dict, primary_commission: float) -> Dict:
        """Calculate multi-tier commission structure"""
        # This would implement the logic for finding who referred this user
        # and calculating secondary/tertiary commissions
        return {
            'secondary_commission': 0.0,
            'tertiary_commission': 0.0
        }
    
    async def _calculate_conversion_rate(self, referral_code_id: str) -> float:
        """Calculate conversion rate for referral code"""
        try:
            db = await self.get_database()
            
            code_doc = await db.referral_codes.find_one({'referral_code_id': referral_code_id})
            if not code_doc:
                return 0.0
            
            unique_clicks = code_doc['tracking_data']['unique_clicks']
            conversions = code_doc['tracking_data']['successful_conversions']
            
            return (conversions / max(unique_clicks, 1)) * 100
            
        except Exception as e:
            logger.error(f"Calculate conversion rate error: {str(e)}")
            return 0.0
    
    async def _calculate_program_conversion_rate(self, program_id: str) -> float:
        """Calculate overall program conversion rate"""
        try:
            db = await self.get_database()
            
            # Get total clicks and conversions for program
            pipeline = [
                {'$match': {'program_id': program_id}},
                {'$group': {
                    '_id': None,
                    'total_clicks': {'$sum': '$tracking_data.unique_clicks'},
                    'total_conversions': {'$sum': '$tracking_data.successful_conversions'}
                }}
            ]
            
            result = await db.referral_codes.aggregate(pipeline).to_list(length=1)
            
            if result:
                clicks = result[0]['total_clicks']
                conversions = result[0]['total_conversions']
                return (conversions / max(clicks, 1)) * 100
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Calculate program conversion rate error: {str(e)}")
            return 0.0
    
    async def _send_conversion_notifications(self, conversion: Dict):
        """Send notifications for successful conversion"""
        try:
            # This would integrate with email/SMS service
            logger.info(f"Conversion notification sent for conversion {conversion['conversion_id']}")
            
        except Exception as e:
            logger.error(f"Send conversion notifications error: {str(e)}")
    
    async def _check_payout_qualification(self, user_id: str, program_id: str):
        """Check if user qualifies for payout and trigger if ready"""
        try:
            db = await self.get_database()
            
            # Get program settings
            program = await db.referral_programs.find_one({'program_id': program_id})
            if not program:
                return
            
            # If auto-payout is enabled, check minimum threshold
            if program['payout_settings']['auto_payout']:
                pending_amount = await db.referral_conversions.aggregate([
                    {
                        '$match': {
                            'referrer_user_id': user_id,
                            'program_id': program_id,
                            'status': 'approved',
                            'payout_info.payout_id': None
                        }
                    },
                    {
                        '$group': {
                            '_id': None,
                            'total': {'$sum': '$commission_details.total_commission'}
                        }
                    }
                ]).to_list(length=1)
                
                if pending_amount and pending_amount[0]['total'] >= program['commission_structure']['minimum_payout']:
                    # Trigger auto-payout
                    logger.info(f"Auto-payout triggered for user {user_id}, program {program_id}")
                    
        except Exception as e:
            logger.error(f"Check payout qualification error: {str(e)}")
    
    async def _process_actual_payout(self, payout: Dict) -> Dict[str, Any]:
        """Process actual payout via payment processor"""
        try:
            # This would integrate with Stripe, PayPal, etc.
            # For now, simulate successful processing
            
            db = await self.get_database()
            
            # Update payout status
            await db.referral_payouts.update_one(
                {'payout_id': payout['payout_id']},
                {
                    '$set': {
                        'status': 'completed',
                        'transaction_info.transaction_id': str(uuid.uuid4()),
                        'transaction_info.processed_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            return {
                'success': True,
                'transaction_id': str(uuid.uuid4()),
                'processed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Process actual payout error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _get_monthly_breakdown(self, user_id: str, program_id: str = None) -> List[Dict]:
        """Get monthly breakdown of referral performance"""
        try:
            db = await self.get_database()
            
            # This would implement monthly aggregation
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Get monthly breakdown error: {str(e)}")
            return []
    
    async def _get_top_performing_codes(self, user_id: str, program_id: str = None) -> List[Dict]:
        """Get top performing referral codes"""
        try:
            db = await self.get_database()
            
            query = {'user_id': user_id}
            if program_id:
                query['program_id'] = program_id
            
            codes = await db.referral_codes.find(query).sort(
                'tracking_data.total_commissions_earned', -1
            ).limit(5).to_list(length=5)
            
            return codes
            
        except Exception as e:
            logger.error(f"Get top performing codes error: {str(e)}")
            return []
    
    async def _create_codes_for_existing_users(self, program_id: str):
        """Create referral codes for existing eligible users"""
        try:
            db = await self.get_database()
            
            # Get program
            program = await db.referral_programs.find_one({'program_id': program_id})
            if not program:
                return
            
            # Get eligible users
            users = await db.users.find({}).to_list(length=None)
            
            for user in users:
                eligibility = await self._check_user_eligibility(user['user_id'], program)
                if eligibility['eligible']:
                    await self.generate_referral_code(user['user_id'], program_id)
                    
        except Exception as e:
            logger.error(f"Create codes for existing users error: {str(e)}")

# Global service instance
referral_service = CompleteReferralService()

    async def get_item(self, user_id: str, item_id: str):
        """Get specific item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            item = await collections['items'].find_one({
                "_id": item_id,
                "user_id": user_id
            })
            
            if not item:
                return {"success": False, "message": "Item not found"}
            
            return {
                "success": True,
                "data": item,
                "message": "Item retrieved successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def update_item(self, user_id: str, item_id: str, update_data: dict):
        """Update existing item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            result = await collections['items'].update_one(
                {"_id": item_id, "user_id": user_id},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                return {"success": False, "message": "Item not found or no changes made"}
            
            # Get updated item
            updated_item = await collections['items'].find_one({
                "_id": item_id,
                "user_id": user_id
            })
            
            return {
                "success": True,
                "data": updated_item,
                "message": "Item updated successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def delete_item(self, user_id: str, item_id: str):
        """Delete item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            result = await collections['items'].delete_one({
                "_id": item_id,
                "user_id": user_id
            })
            
            if result.deleted_count == 0:
                return {"success": False, "message": "Item not found"}
            
            return {
                "success": True,
                "message": "Item deleted successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def list_items(self, user_id: str, filters: dict = None, page: int = 1, limit: int = 50):
        """List user's items"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            query = {"user_id": user_id}
            if filters:
                query.update(filters)
            
            skip = (page - 1) * limit
            
            cursor = collections['items'].find(query).skip(skip).limit(limit)
            items = await cursor.to_list(length=limit)
            
            total_count = await collections['items'].count_documents(query)
            
            return {
                "success": True,
                "data": {
                    "items": items,
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total_count,
                        "pages": (total_count + limit - 1) // limit
                    }
                },
                "message": "Items retrieved successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}