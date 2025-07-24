"""
Stripe Webhook Handler Service
Handles all Stripe webhook events for payment management, 
subscription updates, and dunning management
"""

import stripe
import os
import logging
import json
from typing import Dict, Any, List
from datetime import datetime
from services.stripe_customer_service import StripeCustomerService
# from services.workspace_service import WorkspaceService  # We'll need to create this
from core.database import get_database

logger = logging.getLogger(__name__)

class StripeWebhookService:
    def __init__(self):
        self.webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
        self.customer_service = StripeCustomerService()
        # self.workspace_service = WorkspaceService()  # Uncomment when created
        self.collection_name = "webhook_events"
        
    async def _get_collection_async(self):
        """Get database collection for webhook event logging"""
        try:
            db = await get_database()
            return db[self.collection_name]
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return None

    async def verify_webhook_signature(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """Verify webhook signature and parse event"""
        try:
            if not self.webhook_secret:
                logger.warning("No webhook secret configured")
                return {"success": False, "error": "Webhook secret not configured"}

            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            
            return {"success": True, "event": event}
            
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            return {"success": False, "error": "Invalid payload"}
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")  
            return {"success": False, "error": "Invalid signature"}

    async def handle_webhook_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Route webhook events to appropriate handlers"""
        try:
            event_type = event.get('type', '')
            event_id = event.get('id', '')
            
            # Log webhook event
            await self._log_webhook_event(event)
            
            logger.info(f"Processing webhook event: {event_type} ({event_id})")
            
            # Route to specific handlers
            handlers = {
                'customer.subscription.created': self._handle_subscription_created,
                'customer.subscription.updated': self._handle_subscription_updated,
                'customer.subscription.deleted': self._handle_subscription_deleted,
                'invoice.payment_succeeded': self._handle_payment_succeeded,
                'invoice.payment_failed': self._handle_payment_failed,
                'payment_method.attached': self._handle_payment_method_attached,
                'customer.updated': self._handle_customer_updated,
                'setup_intent.succeeded': self._handle_setup_intent_succeeded,
                'payment_intent.succeeded': self._handle_payment_intent_succeeded,
                'payment_intent.payment_failed': self._handle_payment_intent_failed,
            }
            
            if event_type in handlers:
                result = await handlers[event_type](event['data']['object'])
                logger.info(f"Successfully processed {event_type}")
                return {"success": True, "processed": True, "result": result}
            else:
                logger.info(f"Unhandled webhook event type: {event_type}")
                return {"success": True, "processed": False, "message": f"Unhandled event type: {event_type}"}
                
        except Exception as e:
            logger.error(f"Error handling webhook event: {e}")
            return {"success": False, "error": str(e)}

    async def _log_webhook_event(self, event: Dict[str, Any]):
        """Log webhook event to database"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return

            event_log = {
                "stripe_event_id": event.get('id'),
                "event_type": event.get('type'),
                "created": event.get('created'),
                "livemode": event.get('livemode'),
                "data": event.get('data'),
                "processed_at": datetime.utcnow().isoformat(),
                "api_version": event.get('api_version')
            }
            
            await collection.insert_one(event_log)
            
        except Exception as e:
            logger.error(f"Error logging webhook event: {e}")

    async def _handle_payment_intent_succeeded(self, payment_intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful payment intent - create workspace and redirect"""
        try:
            customer_id = payment_intent.get('customer')
            
            if not customer_id:
                return {"success": True, "message": "No customer associated"}
            
            # Get customer from Stripe to find user_id
            customer = stripe.Customer.retrieve(customer_id)
            user_id = customer.metadata.get('user_id')
            
            if not user_id:
                return {"success": False, "error": "No user_id in customer metadata"}
            
            logger.info(f"Payment intent succeeded for user {user_id}: {payment_intent['id']}")
            
            # Check if this payment intent has workspace metadata
            workspace_name = payment_intent['metadata'].get('workspace_name')
            bundles = payment_intent['metadata'].get('bundles', '').split(',')
            
            if workspace_name and bundles:
                # This is an onboarding payment - create workspace
                workspace_result = await self._create_onboarding_workspace(user_id, workspace_name, bundles)
                
                # Save payment method for future use
                payment_method_id = payment_intent.get('payment_method')
                if payment_method_id:
                    await self.customer_service.save_payment_method(
                        user_id=user_id,
                        payment_method_id=payment_method_id,
                        set_as_default=True
                    )
                
                return {
                    "success": True,
                    "action": "onboarding_completed",
                    "user_id": user_id,
                    "payment_intent_id": payment_intent['id'],
                    "workspace_created": workspace_result.get("success", False),
                    "redirect_url": f"/workspace/{workspace_result.get('workspace_id', 'default')}/dashboard"
                }
            
            return {
                "success": True,
                "action": "payment_intent_succeeded",
                "user_id": user_id,
                "payment_intent_id": payment_intent['id']
            }
            
        except Exception as e:
            logger.error(f"Error handling payment intent success: {e}")
            return {"success": False, "error": str(e)}

    async def _create_onboarding_workspace(self, user_id: str, workspace_name: str, bundles: List[str]) -> Dict[str, Any]:
        """Create workspace after successful onboarding payment"""
        try:
            logger.info(f"Creating onboarding workspace '{workspace_name}' for user {user_id} with bundles: {bundles}")
            
            # For now, simulate workspace creation
            # TODO: Replace with actual workspace service call
            workspace_id = f"ws_{user_id}_{workspace_name.lower().replace(' ', '_')}"
            
            # Update user's onboarding status
            from core.database import get_database
            db = await get_database()
            users_collection = db["users"]
            
            await users_collection.update_one(
                {"id": user_id},
                {
                    "$set": {
                        "onboarding_completed": True,
                        "has_workspace": True,
                        "workspace_id": workspace_id,
                        "selected_bundles": bundles,
                        "updated_at": datetime.utcnow().isoformat()
                    }
                }
            )
            
            logger.info(f"Workspace '{workspace_name}' created for user {user_id}")
            return {
                "success": True,
                "workspace_id": workspace_id,
                "workspace_name": workspace_name,
                "bundles": bundles
            }
            
        except Exception as e:
            logger.error(f"Error creating onboarding workspace: {e}")
            return {"success": False, "error": str(e)}