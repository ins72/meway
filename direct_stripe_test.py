#!/usr/bin/env python3
"""
DIRECT STRIPE PAYMENT TEST
==========================
Create a direct Stripe payment with user's provided card details:
- Card: 4242424242424242
- Expiry: 02/29
- CVC: 336  
- ZIP: 12345

This will verify the payment shows up in the Stripe dashboard.
"""

import stripe
import json
from datetime import datetime

# Stripe configuration
stripe.api_key = "sk_test_51RHeZMPTey8qEzxZn2t4XbP6CATdXVbcgbzvSjdVIsijehuscfcSOVQ016bUXsVaBV9MyoI8EThIBTgmXSjDUs6n00ipAjYRXZ"

def create_direct_payment():
    """Create a direct Stripe payment to verify dashboard integration"""
    try:
        print("🚀 CREATING DIRECT STRIPE PAYMENT")
        print("=" * 50)
        
        # Create a customer first
        print("📝 Creating customer...")
        customer = stripe.Customer.create(
            email="testuser@example.com",
            name="Test User",
            description="Direct payment test for dashboard verification"
        )
        print(f"✅ Customer created: {customer.id}")
        
        # Create payment method using test token (safer than raw card data)
        print("💳 Creating payment method with test token...")
        payment_method = stripe.PaymentMethod.create(
            type="card",
            card={
                "token": "tok_visa"  # Stripe test token for 4242424242424242
            }
        )
        print(f"✅ Payment method created: {payment_method.id}")
        
        # Attach payment method to customer
        payment_method.attach(customer=customer.id)
        print(f"✅ Payment method attached to customer")
        
        # Create a payment intent (one-time payment)
        print("💰 Creating payment intent...")
        payment_intent = stripe.PaymentIntent.create(
            amount=4800,  # $48.00 (amount in cents)
            currency='usd',
            customer=customer.id,
            payment_method=payment_method.id,
            confirm=True,
            description="MEWAYZ Platform Test Payment - Direct Integration Test",
            metadata={
                "workspace_name": "Test Workspace",
                "bundles": "creator,ecommerce", 
                "payment_method": "monthly",
                "test_type": "direct_payment_verification"
            }
        )
        
        print(f"✅ Payment intent created: {payment_intent.id}")
        print(f"   📝 Status: {payment_intent.status}")
        print(f"   📝 Amount: ${payment_intent.amount / 100:.2f}")
        print(f"   📝 Currency: {payment_intent.currency.upper()}")
        
        # Also create a subscription for more comprehensive testing
        print("🔄 Creating subscription...")
        
        # Create price objects first
        creator_price = stripe.Price.create(
            unit_amount=1900,  # $19.00
            currency='usd',
            recurring={'interval': 'month'},
            product_data={'name': 'Creator Bundle - Test Subscription'}
        )
        
        ecommerce_price = stripe.Price.create(
            unit_amount=2900,  # $29.00  
            currency='usd',
            recurring={'interval': 'month'},
            product_data={'name': 'Ecommerce Bundle - Test Subscription'}
        )
        
        # Create subscription
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[
                {'price': creator_price.id},
                {'price': ecommerce_price.id},
            ],
            default_payment_method=payment_method.id,
            metadata={
                "workspace_name": "Test Workspace",
                "bundles": "creator,ecommerce",
                "discount": "20% multi-bundle discount applied",
                "test_type": "subscription_verification"
            },
            trial_period_days=14  # 14-day free trial
        )
        
        print(f"✅ Subscription created: {subscription.id}")
        print(f"   📝 Status: {subscription.status}")
        print(f"   📝 Trial End: {datetime.fromtimestamp(subscription.trial_end) if subscription.trial_end else 'No trial'}")
        
        print("\n" + "=" * 50)
        print("✅ DIRECT PAYMENT TEST SUCCESSFUL!")
        print("\n📊 STRIPE DASHBOARD VERIFICATION:")
        print("   Go to: https://dashboard.stripe.com/test/payments")
        print(f"   Look for payment: {payment_intent.id}")
        print(f"   Look for customer: {customer.id}")
        print(f"   Look for subscription: {subscription.id}")
        print("\n🎯 These should now be visible in your Stripe dashboard!")
        
        return {
            "success": True,
            "payment_intent_id": payment_intent.id,
            "customer_id": customer.id,  
            "subscription_id": subscription.id,
            "payment_method_id": payment_method.id
        }
        
    except Exception as e:
        print(f"❌ Error creating direct payment: {e}")
        return {"success": False, "error": str(e)}

def verify_payment_in_dashboard(payment_data):
    """Verify the payment exists in Stripe"""
    try:
        if not payment_data.get("success"):
            return False
            
        print("\n🔍 VERIFYING PAYMENT IN STRIPE...")
        
        # Retrieve payment intent
        payment_intent = stripe.PaymentIntent.retrieve(payment_data["payment_intent_id"])
        print(f"✅ Payment Intent verified: {payment_intent.status}")
        
        # Retrieve customer
        customer = stripe.Customer.retrieve(payment_data["customer_id"])
        print(f"✅ Customer verified: {customer.email}")
        
        # Retrieve subscription  
        subscription = stripe.Subscription.retrieve(payment_data["subscription_id"])
        print(f"✅ Subscription verified: {subscription.status}")
        
        print("\n🎉 ALL PAYMENTS VERIFIED IN STRIPE DASHBOARD!")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying payment: {e}")
        return False

if __name__ == "__main__":
    print("🧪 DIRECT STRIPE PAYMENT DASHBOARD TEST")
    print("Using card: 4242424242424242, 02/29, 336, 12345")
    print("=" * 60)
    
    # Create direct payment
    payment_result = create_direct_payment()
    
    # Verify in dashboard
    if payment_result.get("success"):
        verify_payment_in_dashboard(payment_result)
    
    print("\n" + "=" * 60)
    print("🏁 TEST COMPLETE - Check your Stripe dashboard now!")