"""
Enhanced Stripe Customer & Payment Management Service
Handles customer creation, payment method storage, subscription management,
and dunning management following Stripe best practices 2025
"""

import stripe
import os
import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from core.objectid_serializer import safe_document_return, serialize_objectid
from core.database import get_database

logger = logging.getLogger(__name__)

class StripeCustomerService:
    def __init__(self):
        self.collection_name = "stripe_customers"
        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
        self.service_name = "stripe_customer_management"
        
    async def _get_collection_async(self):
        """Get database collection with async support"""
        try:
            db = await get_database()
            return db[self.collection_name]
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return None

    async def create_or_get_customer(self, user_id: str, user_email: str, user_name: str = None) -> dict:
        """Create or retrieve Stripe customer for user"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}

            # Check if customer already exists
            existing_customer = await collection.find_one({"user_id": user_id})
            if existing_customer:
                # Verify customer still exists in Stripe
                try:
                    stripe_customer = stripe.Customer.retrieve(existing_customer["stripe_customer_id"])
                    return {
                        "success": True,
                        "customer": serialize_objectid(existing_customer),
                        "stripe_customer": stripe_customer
                    }
                except stripe.error.InvalidRequestError:
                    # Customer was deleted from Stripe, remove from our DB
                    await collection.delete_one({"user_id": user_id})

            # Create new Stripe customer
            stripe_customer = stripe.Customer.create(
                email=user_email,
                name=user_name or user_email.split('@')[0],
                metadata={
                    'user_id': user_id,
                    'platform': 'MEWAYZ',
                    'created_at': datetime.utcnow().isoformat()
                }
            )

            # Store customer in our database
            customer_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "user_email": user_email,
                "user_name": user_name,
                "stripe_customer_id": stripe_customer.id,
                "default_payment_method": None,
                "payment_methods": [],
                "subscriptions": [],
                "payment_failures": [],
                "account_status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            await collection.insert_one(customer_data)
            logger.info(f"Created Stripe customer {stripe_customer.id} for user {user_id}")

            return {
                "success": True,
                "customer": serialize_objectid(customer_data),
                "stripe_customer": stripe_customer
            }

        except Exception as e:
            logger.error(f"Error creating/getting customer: {e}")
            return {"success": False, "error": str(e)}

    async def save_payment_method(self, user_id: str, payment_method_id: str, set_as_default: bool = False) -> dict:
        """Save payment method to customer account"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}

            # Get customer
            customer_record = await collection.find_one({"user_id": user_id})
            if not customer_record:
                return {"success": False, "error": "Customer not found"}

            # Retrieve payment method from Stripe
            payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
            
            # Attach payment method to customer
            payment_method.attach(customer=customer_record["stripe_customer_id"])

            # Prepare payment method data
            pm_data = {
                "id": payment_method.id,
                "type": payment_method.type,
                "card": payment_method.card if payment_method.type == "card" else None,
                "created": payment_method.created,
                "is_default": set_as_default
            }

            # Update customer record
            update_data = {
                "$push": {"payment_methods": pm_data},
                "$set": {"updated_at": datetime.utcnow().isoformat()}
            }

            if set_as_default:
                # Set all other payment methods as non-default
                customer_record["payment_methods"] = [
                    {**pm, "is_default": False} for pm in customer_record.get("payment_methods", [])
                ]
                customer_record["payment_methods"].append(pm_data)
                
                update_data["$set"]["default_payment_method"] = payment_method_id
                update_data["$set"]["payment_methods"] = customer_record["payment_methods"]

            await collection.update_one(
                {"user_id": user_id},
                update_data
            )

            logger.info(f"Saved payment method {payment_method_id} for user {user_id}")
            return {
                "success": True,
                "payment_method": pm_data,
                "message": "Payment method saved successfully"
            }

        except Exception as e:
            logger.error(f"Error saving payment method: {e}")
            return {"success": False, "error": str(e)}

    async def create_subscription(self, user_id: str, price_ids: List[str], workspace_name: str = None, trial_days: int = 14) -> dict:
        """Create subscription for customer"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}

            # Get customer
            customer_record = await collection.find_one({"user_id": user_id})
            if not customer_record:
                return {"success": False, "error": "Customer not found"}

            # Create subscription in Stripe
            subscription_data = {
                "customer": customer_record["stripe_customer_id"],
                "items": [{"price": price_id} for price_id in price_ids],
                "payment_behavior": "default_incomplete",
                "payment_settings": {"save_default_payment_method": "on_subscription"},
                "expand": ["latest_invoice.payment_intent"],
                "metadata": {
                    "user_id": user_id,
                    "workspace_name": workspace_name or "Default Workspace",
                    "platform": "MEWAYZ"
                }
            }

            if trial_days > 0:
                subscription_data["trial_period_days"] = trial_days

            subscription = stripe.Subscription.create(**subscription_data)

            # Store subscription info
            sub_data = {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "trial_start": subscription.trial_start,
                "trial_end": subscription.trial_end,
                "workspace_name": workspace_name,
                "price_ids": price_ids,
                "created_at": datetime.utcnow().isoformat()
            }

            await collection.update_one(
                {"user_id": user_id},
                {
                    "$push": {"subscriptions": sub_data},
                    "$set": {"updated_at": datetime.utcnow().isoformat()}
                }
            )

            logger.info(f"Created subscription {subscription.id} for user {user_id}")
            return {
                "success": True,
                "subscription": subscription,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret if subscription.latest_invoice.payment_intent else None
            }

        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            return {"success": False, "error": str(e)}

    async def handle_payment_failure(self, user_id: str, subscription_id: str, invoice_id: str, attempt_count: int = 1) -> dict:
        """Handle payment failure with retry logic"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}

            # Record payment failure
            failure_data = {
                "id": str(uuid.uuid4()),
                "subscription_id": subscription_id,
                "invoice_id": invoice_id,
                "attempt_count": attempt_count,
                "failed_at": datetime.utcnow().isoformat(),
                "status": "retry_pending" if attempt_count < 3 else "payment_failed",
                "next_retry": (datetime.utcnow() + timedelta(days=attempt_count)).isoformat() if attempt_count < 3 else None
            }

            await collection.update_one(
                {"user_id": user_id},
                {
                    "$push": {"payment_failures": failure_data},
                    "$set": {
                        "account_status": "payment_failed" if attempt_count >= 3 else "payment_retry",
                        "updated_at": datetime.utcnow().isoformat()
                    }
                }
            )

            # Disable features if max attempts reached
            if attempt_count >= 3:
                await self._disable_workspace_features(user_id)

            logger.info(f"Recorded payment failure for user {user_id}, attempt {attempt_count}")
            return {
                "success": True,
                "failure_data": failure_data,
                "should_disable_features": attempt_count >= 3
            }

        except Exception as e:
            logger.error(f"Error handling payment failure: {e}")
            return {"success": False, "error": str(e)}

    async def _disable_workspace_features(self, user_id: str):
        """Disable workspace features for user with payment issues"""
        try:
            # This would integrate with your workspace service
            # For now, we'll just log it
            logger.info(f"Disabling features for user {user_id} due to payment failure")
            
            # TODO: Implement feature disabling logic
            # - Disable workspace creation
            # - Limit API usage
            # - Disable premium features
            # - Show payment required banners
            
        except Exception as e:
            logger.error(f"Error disabling features: {e}")

    async def get_customer_payment_methods(self, user_id: str) -> dict:
        """Get all saved payment methods for customer"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}

            customer_record = await collection.find_one({"user_id": user_id})
            if not customer_record:
                return {"success": False, "error": "Customer not found"}

            return {
                "success": True,
                "payment_methods": customer_record.get("payment_methods", []),
                "default_payment_method": customer_record.get("default_payment_method")
            }

        except Exception as e:
            logger.error(f"Error getting payment methods: {e}")
            return {"success": False, "error": str(e)}

    async def update_default_payment_method(self, user_id: str, payment_method_id: str) -> dict:
        """Update default payment method for customer"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}

            # Update Stripe customer default payment method
            customer_record = await collection.find_one({"user_id": user_id})
            if not customer_record:
                return {"success": False, "error": "Customer not found"}

            stripe.Customer.modify(
                customer_record["stripe_customer_id"],
                invoice_settings={"default_payment_method": payment_method_id}
            )

            # Update our database
            await collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "default_payment_method": payment_method_id,
                        "updated_at": datetime.utcnow().isoformat()
                    }
                }
            )

            # Update payment methods list
            await collection.update_one(
                {"user_id": user_id, "payment_methods.id": {"$ne": payment_method_id}},
                {"$set": {"payment_methods.$.is_default": False}}
            )
            
            await collection.update_one(
                {"user_id": user_id, "payment_methods.id": payment_method_id},
                {"$set": {"payment_methods.$.is_default": True}}
            )

            logger.info(f"Updated default payment method for user {user_id}")
            return {"success": True, "message": "Default payment method updated"}

        except Exception as e:
            logger.error(f"Error updating default payment method: {e}")
            return {"success": False, "error": str(e)}