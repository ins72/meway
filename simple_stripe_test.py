#!/usr/bin/env python3
"""
SIMPLE STRIPE CHARGE TEST
=========================
Create a simple Stripe charge to verify dashboard integration
"""

import stripe
import json
from datetime import datetime

# Stripe configuration
stripe.api_key = "sk_test_51RHeZMPTey8qEzxZn2t4XbP6CATdXVbcgbzvSjdVIsijehuscfcSOVQ016bUXsVaBV9MyoI8EThIBTgmXSjDUs6n00ipAjYRXZ"

def create_simple_charge():
    """Create a simple Stripe charge"""
    try:
        print("🚀 CREATING SIMPLE STRIPE CHARGE")
        print("=" * 50)
        
        # Create a simple charge using test token
        print("💳 Creating charge...")
        charge = stripe.Charge.create(
            amount=4800,  # $48.00
            currency='usd',
            source='tok_visa',  # Test token for 4242...4242
            description='MEWAYZ Platform - Test Payment (Dashboard Verification)',
            metadata={
                'workspace_name': 'Test Workspace',
                'bundles': 'creator,ecommerce',
                'payment_method': 'monthly',
                'test_type': 'dashboard_verification',
                'user_card': '4242424242424242'
            }
        )
        
        print(f"✅ Charge created successfully!")
        print(f"   📝 Charge ID: {charge.id}")
        print(f"   📝 Status: {charge.status}")
        print(f"   📝 Amount: ${charge.amount / 100:.2f}")
        print(f"   📝 Currency: {charge.currency.upper()}")
        print(f"   📝 Paid: {charge.paid}")
        print(f"   📝 Created: {datetime.fromtimestamp(charge.created)}")
        
        # Also create a customer for better dashboard tracking
        print("\n👤 Creating customer...")
        customer = stripe.Customer.create(
            email='testuser@mewayz.com',
            name='Test User - Dashboard Verification',
            description='Customer created for Stripe dashboard verification test',
            metadata={
                'workspace': 'Test Workspace',
                'plan': 'Creator + Ecommerce Bundles'
            }
        )
        
        print(f"✅ Customer created!")
        print(f"   📝 Customer ID: {customer.id}")
        print(f"   📝 Email: {customer.email}")
        
        print("\n" + "=" * 50)
        print("✅ STRIPE CHARGE TEST SUCCESSFUL!")
        print("\n📊 STRIPE DASHBOARD VERIFICATION:")
        print("   🔗 Go to: https://dashboard.stripe.com/test/payments")
        print(f"   🔍 Look for charge: {charge.id}")
        print(f"   🔍 Look for customer: {customer.id}")
        print("   💰 Amount should show: $48.00")
        print("   📝 Status should be: succeeded")
        print("\n🎯 This payment should now be visible in your Stripe dashboard!")
        
        return {
            "success": True,
            "charge_id": charge.id,
            "customer_id": customer.id,
            "amount": charge.amount / 100,
            "status": charge.status
        }
        
    except Exception as e:
        print(f"❌ Error creating charge: {e}")
        return {"success": False, "error": str(e)}

def test_checkout_session_api():
    """Test our backend checkout session API"""
    try:
        print("\n🧪 TESTING BACKEND CHECKOUT SESSION API")
        print("=" * 50)
        
        import requests
        
        # First login to get token
        login_response = requests.post(
            "https://eff6f53c-47df-43a1-9962-4d20b26f6dc5.preview.emergentagent.com/api/auth/login",
            json={
                "email": "tmonnens@outlook.com",
                "password": "Voetballen5"
            }
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            print("✅ Login successful")
            
            # Test checkout session creation
            checkout_response = requests.post(
                "https://eff6f53c-47df-43a1-9962-4d20b26f6dc5.preview.emergentagent.com/api/stripe-integration/create-checkout-session",
                json={
                    "bundles": ["creator", "ecommerce"],
                    "workspace_name": "API Test Workspace",
                    "payment_method": "monthly"
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if checkout_response.status_code == 200:
                session_data = checkout_response.json()
                print("✅ Checkout session created via API!")
                print(f"   📝 Session ID: {session_data.get('session_id', 'N/A')}")
                print(f"   📝 Session URL: {session_data.get('session_url', 'N/A')}")
                return True
            else:
                print(f"❌ Checkout session failed: {checkout_response.status_code}")
                print(f"   📄 Response: {checkout_response.text}")
                return False
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

if __name__ == "__main__":
    print("🧪 STRIPE DASHBOARD VERIFICATION TEST")
    print("Testing with card equivalent: 4242424242424242")
    print("=" * 60)
    
    # Create simple charge
    charge_result = create_simple_charge()
    
    # Test our backend API
    api_result = test_checkout_session_api()
    
    print("\n" + "=" * 60)
    if charge_result.get("success") and api_result:
        print("🎉 ALL TESTS SUCCESSFUL!")
        print("✅ Direct Stripe charge created - check dashboard")
        print("✅ Backend API checkout session created")
    else:
        print("⚠️  Some tests failed - check output above")
    
    print("\n🏁 TEST COMPLETE - Check your Stripe dashboard now!")
    print("   The payments should be visible at: https://dashboard.stripe.com/test/payments")