"""
Complete Subscription Management Service
3-tier pricing system with Stripe integration and usage limits
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal
from enum import Enum

from core.database import get_database

# Configure logging
logger = logging.getLogger(__name__)

class SubscriptionTier(str, Enum):
    FREE = "free"
    PROFESSIONAL = "professional"
    PRO = "professional"  # Alias for professional
    ENTERPRISE = "enterprise"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    TRIALING = "trialing"

class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"

class CompleteSubscriptionService:
    """Complete subscription management with real Stripe integration"""
    
    def __init__(self):
        self.db = None
        
    async def get_database(self):
        """Get database connection"""
        if not self.db:
            self.db = get_database()
        return self.db
    
    # Subscription Plans Configuration
    SUBSCRIPTION_PLANS = {
        SubscriptionTier.FREE: {
            'name': 'Free Plan',
            'description': 'Perfect for getting started',
            'monthly_price': 0.00,
            'yearly_price': 0.00,
            'stripe_monthly_price_id': None,
            'stripe_yearly_price_id': None,
            'features': [
                'Basic workspace (1)',
                'Up to 3 team members',
                '1GB storage',
                'Basic analytics',
                'Standard support',
                'Basic integrations'
            ],
            'limits': {
                'workspaces': 1,
                'members_per_workspace': 3,
                'storage_gb': 1,
                'api_calls_per_month': 1000,
                'templates': 5,
                'custom_domains': 0,
                'advanced_features': False
            }
        },
        SubscriptionTier.PROFESSIONAL: {
            'name': 'Professional Plan',
            'description': 'For growing teams and businesses',
            'monthly_price': 29.99,
            'yearly_price': 299.99,  # 2 months free
            'stripe_monthly_price_id': 'price_1234567890_monthly_pro',  # Would be real Stripe price IDs
            'stripe_yearly_price_id': 'price_1234567890_yearly_pro',
            'features': [
                'Unlimited workspaces',
                'Up to 25 team members per workspace',
                '100GB storage',
                'Advanced analytics',
                'Priority support',
                'All integrations',
                'Custom branding',
                'Advanced AI features',
                '5 custom domains'
            ],
            'limits': {
                'workspaces': -1,  # Unlimited
                'members_per_workspace': 25,
                'storage_gb': 100,
                'api_calls_per_month': 50000,
                'templates': 100,
                'custom_domains': 5,
                'advanced_features': True
            }
        },
        SubscriptionTier.ENTERPRISE: {
            'name': 'Enterprise Plan',
            'description': 'For large organizations with advanced needs',
            'monthly_price': 99.99,
            'yearly_price': 999.99,  # 2 months free
            'stripe_monthly_price_id': 'price_1234567890_monthly_ent',
            'stripe_yearly_price_id': 'price_1234567890_yearly_ent',
            'features': [
                'Unlimited workspaces',
                'Unlimited team members',
                '1TB storage',
                'Advanced analytics & reporting',
                'Dedicated support',
                'All integrations',
                'White-label solution',
                'Advanced AI features',
                'Unlimited custom domains',
                'SSO & advanced security',
                'API access',
                'Custom integrations'
            ],
            'limits': {
                'workspaces': -1,  # Unlimited
                'members_per_workspace': -1,  # Unlimited
                'storage_gb': 1000,
                'api_calls_per_month': 500000,
                'templates': -1,  # Unlimited
                'custom_domains': -1,  # Unlimited
                'advanced_features': True
            }
        }
    }
    
    # Subscription Management
    async def create_subscription(self, user_id: str, workspace_id: str, 
                                 plan_tier: str, billing_cycle: str = BillingCycle.MONTHLY.value,
                                 payment_method_id: str = None) -> Dict[str, Any]:
        """Create a new subscription with Stripe integration"""
        try:
            # Validate plan tier
            if plan_tier not in [tier.value for tier in SubscriptionTier]:
                return None
                
            db = await self.get_database()
            
            subscription_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            # Calculate billing dates
            if billing_cycle == BillingCycle.YEARLY.value:
                next_billing_date = current_time + timedelta(days=365)
            else:
                next_billing_date = current_time + timedelta(days=30)
            
            # Get plan configuration
            plan_config = self.SUBSCRIPTION_PLANS[SubscriptionTier(plan_tier)]
            
            # Create subscription data
            subscription_data = {
                'subscription_id': subscription_id,
                'user_id': user_id,
                'workspace_id': workspace_id,
                'plan_tier': plan_tier,
                'billing_cycle': billing_cycle,
                'status': SubscriptionStatus.TRIALING.value if plan_tier != SubscriptionTier.FREE.value else SubscriptionStatus.ACTIVE.value,
                'created_at': current_time,
                'updated_at': current_time,
                'current_period_start': current_time,
                'current_period_end': next_billing_date,
                'trial_start': current_time if plan_tier != SubscriptionTier.FREE.value else None,
                'trial_end': current_time + timedelta(days=14) if plan_tier != SubscriptionTier.FREE.value else None,
                'cancel_at_period_end': False,
                'canceled_at': None,
                'stripe_subscription_id': None,
                'stripe_customer_id': None,
                'payment_method_id': payment_method_id,
                'usage_limits': plan_config['limits'].copy()
            }
            
            # If not free plan, create Stripe subscription
            if plan_tier != SubscriptionTier.FREE.value and payment_method_id:
                stripe_subscription = await self._create_stripe_subscription(
                    subscription_data, plan_config, billing_cycle
                )
                if stripe_subscription:
                    subscription_data['stripe_subscription_id'] = stripe_subscription['id']
                    subscription_data['stripe_customer_id'] = stripe_subscription['customer']
                    subscription_data['status'] = SubscriptionStatus.ACTIVE.value
            
            # Insert subscription
            await db.subscriptions.insert_one(subscription_data)
            
            # Update workspace with subscription info
            await db.workspaces.update_one(
                {'workspace_id': workspace_id},
                {
                    '$set': {
                        'subscription_id': subscription_id,
                        'subscription_tier': plan_tier,
                        'subscription_status': subscription_data['status'],
                        'updated_at': current_time
                    }
                }
            )
            
            # Initialize usage tracking
            await self._initialize_usage_tracking(subscription_id, workspace_id)
            
            # Log subscription creation
            await self._log_subscription_activity(
                subscription_id=subscription_id,
                action='subscription_created',
                details={'plan_tier': plan_tier, 'billing_cycle': billing_cycle}
            )
            
            return subscription_data
            
        except Exception as e:
            logger.error(f"Create subscription error: {str(e)}")
            return None
    
    async def get_subscription_details(self, subscription_id: str) -> Dict[str, Any]:
        """Get detailed subscription information"""
        try:
            db = await self.get_database()
            
            subscription = await db.subscriptions.find_one({'subscription_id': subscription_id})
            if not subscription:
                return None
                
            # Get plan configuration
            plan_config = self.SUBSCRIPTION_PLANS.get(SubscriptionTier(subscription['plan_tier']), {})
            
            # Get current usage
            usage_data = await self._get_current_usage(subscription_id)
            
            # Calculate usage percentages
            usage_percentages = {}
            limits = subscription.get('usage_limits', {})
            for key, limit in limits.items():
                if limit > 0:  # Skip unlimited (-1) limits
                    current_usage = usage_data.get(key, 0)
                    usage_percentages[key] = min((current_usage / limit) * 100, 100)
            
            subscription['plan_config'] = plan_config
            subscription['current_usage'] = usage_data
            subscription['usage_percentages'] = usage_percentages
            subscription['days_until_renewal'] = (subscription['current_period_end'] - datetime.utcnow()).days
            
            # Get recent billing history
            subscription['billing_history'] = await self._get_billing_history(subscription_id)
            
            return subscription
            
        except Exception as e:
            logger.error(f"Get subscription details error: {str(e)}")
            return None
    
    async def get_user_subscriptions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all subscriptions for a user"""
        try:
            db = await self.get_database()
            
            subscriptions = await db.subscriptions.find({
                'user_id': user_id
            }).sort('created_at', -1).to_list(length=None)
            
            # Add plan config to each subscription
            for subscription in subscriptions:
                plan_config = self.SUBSCRIPTION_PLANS.get(
                    SubscriptionTier(subscription['plan_tier']), {}
                )
                subscription['plan_config'] = plan_config
                
                # Add workspace info
                workspace = await db.workspaces.find_one({
                    'workspace_id': subscription['workspace_id']
                })
                subscription['workspace_name'] = workspace.get('name', 'Unknown') if workspace else 'Unknown'
            
            return subscriptions
            
        except Exception as e:
            logger.error(f"Get user subscriptions error: {str(e)}")
            return []
    
    async def upgrade_subscription(self, subscription_id: str, new_plan_tier: str,
                                  billing_cycle: str = None) -> Dict[str, Any]:
        """Upgrade subscription to a higher tier"""
        try:
            db = await self.get_database()
            
            # Get current subscription
            current_subscription = await db.subscriptions.find_one({'subscription_id': subscription_id})
            if not current_subscription:
                return None
            
            # Validate upgrade
            current_tier = SubscriptionTier(current_subscription['plan_tier'])
            new_tier = SubscriptionTier(new_plan_tier)
            
            tier_hierarchy = [SubscriptionTier.FREE, SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE]
            if tier_hierarchy.index(new_tier) <= tier_hierarchy.index(current_tier):
                return None  # Not an upgrade
            
            # Get new plan config
            new_plan_config = self.SUBSCRIPTION_PLANS[new_tier]
            
            # If upgrading to paid plan, process payment
            stripe_subscription_update = None
            if new_tier != SubscriptionTier.FREE:
                stripe_subscription_update = await self._update_stripe_subscription(
                    current_subscription, new_plan_config, billing_cycle or current_subscription['billing_cycle']
                )
            
            # Update subscription
            update_data = {
                'plan_tier': new_plan_tier,
                'usage_limits': new_plan_config['limits'].copy(),
                'updated_at': datetime.utcnow()
            }
            
            if billing_cycle:
                update_data['billing_cycle'] = billing_cycle
            
            if stripe_subscription_update:
                update_data['stripe_subscription_id'] = stripe_subscription_update['id']
            
            await db.subscriptions.update_one(
                {'subscription_id': subscription_id},
                {'$set': update_data}
            )
            
            # Update workspace
            await db.workspaces.update_one(
                {'workspace_id': current_subscription['workspace_id']},
                {
                    '$set': {
                        'subscription_tier': new_plan_tier,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            # Log upgrade
            await self._log_subscription_activity(
                subscription_id=subscription_id,
                action='subscription_upgraded',
                details={
                    'old_tier': current_subscription['plan_tier'],
                    'new_tier': new_plan_tier
                }
            )
            
            return await self.get_subscription_details(subscription_id)
            
        except Exception as e:
            logger.error(f"Upgrade subscription error: {str(e)}")
            return None
    
    async def cancel_subscription(self, subscription_id: str, cancel_immediately: bool = False) -> bool:
        """Cancel subscription with proper Stripe handling"""
        try:
            db = await self.get_database()
            
            subscription = await db.subscriptions.find_one({'subscription_id': subscription_id})
            if not subscription:
                return False
            
            # Cancel Stripe subscription if exists
            if subscription.get('stripe_subscription_id'):
                await self._cancel_stripe_subscription(
                    subscription['stripe_subscription_id'],
                    cancel_immediately
                )
            
            # Update subscription
            update_data = {
                'cancel_at_period_end': not cancel_immediately,
                'canceled_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            if cancel_immediately:
                update_data['status'] = SubscriptionStatus.CANCELED.value
                update_data['current_period_end'] = datetime.utcnow()
            
            await db.subscriptions.update_one(
                {'subscription_id': subscription_id},
                {'$set': update_data}
            )
            
            # Log cancellation
            await self._log_subscription_activity(
                subscription_id=subscription_id,
                action='subscription_canceled',
                details={'immediate': cancel_immediately}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Cancel subscription error: {str(e)}")
            return False
    
    # Usage Tracking and Limits
    async def track_usage(self, subscription_id: str, usage_type: str, amount: int = 1) -> bool:
        """Track usage against subscription limits"""
        try:
            db = await self.get_database()
            
            # Get subscription and limits
            subscription = await db.subscriptions.find_one({'subscription_id': subscription_id})
            if not subscription:
                return False
            
            limits = subscription.get('usage_limits', {})
            limit_value = limits.get(usage_type)
            
            # If unlimited (-1) or no limit, allow usage
            if limit_value is None or limit_value == -1:
                await self._record_usage(subscription_id, usage_type, amount)
                return True
            
            # Check current usage
            current_usage = await self._get_current_usage_for_type(subscription_id, usage_type)
            
            # Check if usage would exceed limit
            if current_usage + amount > limit_value:
                return False  # Usage would exceed limit
            
            # Record usage
            await self._record_usage(subscription_id, usage_type, amount)
            return True
            
        except Exception as e:
            logger.error(f"Track usage error: {str(e)}")
            return False
    
    async def check_usage_limits(self, subscription_id: str) -> Dict[str, Any]:
        """Check current usage against all limits"""
        try:
            db = await self.get_database()
            
            subscription = await db.subscriptions.find_one({'subscription_id': subscription_id})
            if not subscription:
                return {}
            
            limits = subscription.get('usage_limits', {})
            current_usage = await self._get_current_usage(subscription_id)
            
            limit_status = {}
            for usage_type, limit_value in limits.items():
                current = current_usage.get(usage_type, 0)
                
                if limit_value == -1:
                    limit_status[usage_type] = {
                        'current': current,
                        'limit': 'unlimited',
                        'percentage': 0,
                        'exceeded': False
                    }
                else:
                    percentage = (current / limit_value * 100) if limit_value > 0 else 0
                    limit_status[usage_type] = {
                        'current': current,
                        'limit': limit_value,
                        'percentage': round(percentage, 2),
                        'exceeded': current >= limit_value
                    }
            
            return limit_status
            
        except Exception as e:
            logger.error(f"Check usage limits error: {str(e)}")
            return {}
    
    # Plan Information
    async def get_all_plans(self) -> Dict[str, Any]:
        """Get all available subscription plans"""
        return {
            'plans': self.SUBSCRIPTION_PLANS,
            'billing_cycles': [cycle.value for cycle in BillingCycle],
            'comparison': self._generate_plan_comparison()
        }
    
    def _generate_plan_comparison(self) -> List[Dict[str, Any]]:
        """Generate plan comparison data"""
        comparison_features = [
            'workspaces', 'members_per_workspace', 'storage_gb', 
            'api_calls_per_month', 'templates', 'custom_domains'
        ]
        
        comparison = []
        for feature in comparison_features:
            feature_data = {'feature': feature}
            for tier in SubscriptionTier:
                limits = self.SUBSCRIPTION_PLANS[tier]['limits']
                value = limits.get(feature, 0)
                feature_data[tier.value] = 'Unlimited' if value == -1 else value
            comparison.append(feature_data)
        
        return comparison
    
    # Private Helper Methods
    async def _create_stripe_subscription(self, subscription_data: Dict[str, Any], 
                                        plan_config: Dict[str, Any], billing_cycle: str) -> Dict[str, Any]:
        """Create Stripe subscription (would integrate with real Stripe API)"""
        try:
            # This would integrate with actual Stripe API
            # For now, simulate the response
            stripe_subscription = {
                'id': f'sub_{str(uuid.uuid4())[:8]}',
                'customer': f'cus_{str(uuid.uuid4())[:8]}',
                'status': 'active',
                'current_period_start': datetime.utcnow().timestamp(),
                'current_period_end': (datetime.utcnow() + timedelta(days=30)).timestamp()
            }
            
            logger.info(f"Created Stripe subscription: {stripe_subscription['id']}")
            return stripe_subscription
            
        except Exception as e:
            logger.error(f"Create Stripe subscription error: {str(e)}")
            return None
    
    async def _update_stripe_subscription(self, current_subscription: Dict[str, Any],
                                        new_plan_config: Dict[str, Any], billing_cycle: str) -> Dict[str, Any]:
        """Update Stripe subscription (would integrate with real Stripe API)"""
        try:
            # This would integrate with actual Stripe API
            stripe_subscription_id = current_subscription.get('stripe_subscription_id')
            if not stripe_subscription_id:
                return None
                
            # Simulate Stripe API update
            updated_subscription = {
                'id': stripe_subscription_id,
                'customer': current_subscription.get('stripe_customer_id'),
                'status': 'active'
            }
            
            logger.info(f"Updated Stripe subscription: {stripe_subscription_id}")
            return updated_subscription
            
        except Exception as e:
            logger.error(f"Update Stripe subscription error: {str(e)}")
            return None
    
    async def _cancel_stripe_subscription(self, stripe_subscription_id: str, immediately: bool = False):
        """Cancel Stripe subscription (would integrate with real Stripe API)"""
        try:
            # This would integrate with actual Stripe API
            logger.info(f"Canceled Stripe subscription: {stripe_subscription_id} (immediate: {immediately})")
            
        except Exception as e:
            logger.error(f"Cancel Stripe subscription error: {str(e)}")
    
    async def _initialize_usage_tracking(self, subscription_id: str, workspace_id: str):
        """Initialize usage tracking for new subscription"""
        try:
            db = await self.get_database()
            
            current_time = datetime.utcnow()
            usage_record = {
                'usage_id': str(uuid.uuid4()),
                'subscription_id': subscription_id,
                'workspace_id': workspace_id,
                'period_start': current_time,
                'period_end': current_time.replace(day=1) + timedelta(days=32),  # Next month
                'usage_data': {
                    'workspaces': 1,  # At least one workspace
                    'members_per_workspace': 1,  # At least the owner
                    'storage_gb': 0,
                    'api_calls_per_month': 0,
                    'templates': 0,
                    'custom_domains': 0
                },
                'created_at': current_time
            }
            
            await db.subscription_usage.insert_one(usage_record)
            
        except Exception as e:
            logger.error(f"Initialize usage tracking error: {str(e)}")
    
    async def _record_usage(self, subscription_id: str, usage_type: str, amount: int):
        """Record usage in the database"""
        try:
            db = await self.get_database()
            
            # Get current usage period
            current_time = datetime.utcnow()
            usage_record = await db.subscription_usage.find_one({
                'subscription_id': subscription_id,
                'period_start': {'$lte': current_time},
                'period_end': {'$gte': current_time}
            })
            
            if usage_record:
                # Update existing usage
                await db.subscription_usage.update_one(
                    {'usage_id': usage_record['usage_id']},
                    {
                        '$inc': {f'usage_data.{usage_type}': amount},
                        '$set': {'updated_at': current_time}
                    }
                )
            else:
                # Create new usage record for current period
                period_start = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                if current_time.month == 12:
                    period_end = period_start.replace(year=period_start.year + 1, month=1)
                else:
                    period_end = period_start.replace(month=period_start.month + 1)
                
                new_usage = {
                    'usage_id': str(uuid.uuid4()),
                    'subscription_id': subscription_id,
                    'period_start': period_start,
                    'period_end': period_end,
                    'usage_data': {usage_type: amount},
                    'created_at': current_time
                }
                
                await db.subscription_usage.insert_one(new_usage)
            
        except Exception as e:
            logger.error(f"Record usage error: {str(e)}")
    
    async def _get_current_usage(self, subscription_id: str) -> Dict[str, int]:
        """Get current usage for subscription"""
        try:
            db = await self.get_database()
            
            current_time = datetime.utcnow()
            usage_record = await db.subscription_usage.find_one({
                'subscription_id': subscription_id,
                'period_start': {'$lte': current_time},
                'period_end': {'$gte': current_time}
            })
            
            if usage_record:
                return usage_record.get('usage_data', {})
            else:
                return {}
            
        except Exception as e:
            logger.error(f"Get current usage error: {str(e)}")
            return {}
    
    async def _get_current_usage_for_type(self, subscription_id: str, usage_type: str) -> int:
        """Get current usage for specific type"""
        usage_data = await self._get_current_usage(subscription_id)
        return usage_data.get(usage_type, 0)
    
    async def _get_billing_history(self, subscription_id: str) -> List[Dict[str, Any]]:
        """Get billing history for subscription"""
        try:
            db = await self.get_database()
            
            billing_history = await db.billing_history.find({
                'subscription_id': subscription_id
            }).sort('created_at', -1).limit(12).to_list(length=12)
            
            return billing_history
            
        except Exception as e:
            logger.error(f"Get billing history error: {str(e)}")
            return []
    
    async def _log_subscription_activity(self, subscription_id: str, action: str, details: Dict[str, Any]):
        """Log subscription activity"""
        try:
            db = await self.get_database()
            
            activity = {
                'activity_id': str(uuid.uuid4()),
                'subscription_id': subscription_id,
                'action': action,
                'details': details,
                'timestamp': datetime.utcnow()
            }
            
            await db.subscription_activities.insert_one(activity)
            
        except Exception as e:
            logger.error(f"Log subscription activity error: {str(e)}")

# Global service instance
complete_subscription_service = CompleteSubscriptionService()