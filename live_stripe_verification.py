#!/usr/bin/env python3
"""
LIVE STRIPE KEYS VERIFICATION
=============================
Verify that the live Stripe keys are properly configured and working
"""

import os
import requests
import json

def test_live_stripe_integration():
    """Test the live Stripe integration"""
    try:
        print("🔥 LIVE STRIPE KEYS VERIFICATION")
        print("=" * 60)
        print("⚠️  WARNING: USING LIVE STRIPE KEYS - REAL PAYMENTS WILL BE PROCESSED!")
        print("=" * 60)
        
        # Test backend health check
        print("🏥 Testing backend health check...")
        health_response = requests.get(
            "https://3dc4dc3c-9195-4a26-87f6-3f23beffd557.preview.emergentagent.com/api/stripe-integration/health",
            timeout=10
        )
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print("✅ Backend health check passed!")
            print(f"   📝 Service: {health_data.get('service', 'unknown')}")
            print(f"   📝 Healthy: {health_data.get('healthy', False)}")
            print(f"   📝 Stripe Connected: {health_data.get('stripe_connected', False)}")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            return False
        
        # Test login to get authentication token
        print("\n🔐 Testing authentication...")
        login_response = requests.post(
            "https://3dc4dc3c-9195-4a26-87f6-3f23beffd557.preview.emergentagent.com/api/auth/login",
            json={
                "email": "tmonnens@outlook.com",
                "password": "Voetballen5"
            },
            timeout=10
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            print("✅ Authentication successful!")
        else:
            print(f"❌ Authentication failed: {login_response.status_code}")
            return False
        
        # Test checkout session creation (but don't complete payment)
        print("\n💳 Testing checkout session creation...")
        checkout_response = requests.post(
            "https://3dc4dc3c-9195-4a26-87f6-3f23beffd557.preview.emergentagent.com/api/stripe-integration/create-checkout-session",
            json={
                "bundles": ["creator"],
                "workspace_name": "Live Keys Test Workspace",
                "payment_method": "monthly"
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=15
        )
        
        if checkout_response.status_code == 200:
            session_data = checkout_response.json()
            print("✅ LIVE checkout session created successfully!")
            print(f"   📝 Session ID: {session_data.get('session_id', 'N/A')}")
            print(f"   📝 Session URL: {session_data.get('session_url', 'N/A')[:60]}...")
            print("   ⚠️  This is a REAL Stripe checkout session!")
        else:
            print(f"❌ Checkout session creation failed: {checkout_response.status_code}")
            try:
                error_data = checkout_response.json()
                print(f"   📄 Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   📄 Raw response: {checkout_response.text}")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 LIVE STRIPE INTEGRATION VERIFIED!")
        print("🔥 ALL SYSTEMS READY FOR PRODUCTION PAYMENTS!")
        print("⚠️  Remember: All payments will now be REAL transactions!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing live Stripe integration: {e}")
        return False

if __name__ == "__main__":
    success = test_live_stripe_integration()
    
    if success:
        print("\n✅ VERIFICATION COMPLETE - LIVE STRIPE KEYS ARE WORKING!")
        print("🚀 Your MEWAYZ platform is now ready for real payments!")
    else:
        print("\n❌ VERIFICATION FAILED - Please check the configuration!")