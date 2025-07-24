#!/usr/bin/env python3
"""
Stripe Webhook Testing Utility
Test webhook endpoint functionality and event handling
"""

import requests
import json
import hmac
import hashlib
import time
from datetime import datetime

def test_webhook_endpoint():
    """Test if webhook endpoint is accessible"""
    try:
        print("🧪 TESTING STRIPE WEBHOOK ENDPOINT")
        print("=" * 50)
        
        webhook_url = "https://b2614b52-973e-4c52-9dec-e3ec14470901.preview.emergentagent.com/api/payments/webhook"
        
        # Test if endpoint is accessible (should return 400 without proper signature)
        response = requests.post(webhook_url, json={"test": "data"}, timeout=10)
        
        print(f"📡 Webhook URL: {webhook_url}")
        print(f"📝 Response Status: {response.status_code}")
        print(f"📄 Response Text: {response.text}")
        
        if response.status_code == 400:
            if "stripe-signature" in response.text.lower() or "signature" in response.text.lower():
                print("✅ Webhook endpoint is working! (Correctly rejecting unsigned requests)")
                return True
            else:
                print("⚠️  Webhook endpoint exists but may have issues")
                return False
        elif response.status_code == 404:
            print("❌ Webhook endpoint not found - check routing")
            return False
        elif response.status_code == 500:
            print("❌ Webhook endpoint has server errors")
            return False
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing webhook endpoint: {e}")
        return False

def generate_test_webhook_payload():
    """Generate a test webhook payload"""
    return {
        "id": f"evt_test_{int(time.time())}",
        "object": "event",
        "api_version": "2025-03-31.basil",
        "created": int(time.time()),
        "data": {
            "object": {
                "id": f"pi_test_{int(time.time())}",
                "object": "payment_intent",
                "amount": 1900,
                "currency": "usd",
                "status": "succeeded",
                "customer": "cus_test_customer",
                "metadata": {
                    "user_id": "test_user_123",
                    "workspace_name": "Test Workspace",
                    "bundles": "creator"
                }
            }
        },
        "livemode": True,
        "pending_webhooks": 1,
        "request": {
            "id": f"req_test_{int(time.time())}",
            "idempotency_key": None
        },
        "type": "payment_intent.succeeded"
    }

def create_stripe_signature(payload_json, secret):
    """Create a Stripe-compatible signature"""
    timestamp = str(int(time.time()))
    payload_string = payload_json
    
    # Create the signed payload
    signed_payload = f"{timestamp}.{payload_string}"
    
    # Generate signature
    signature = hmac.new(
        secret.encode('utf-8'),
        signed_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return f"t={timestamp},v1={signature}"

def test_webhook_with_mock_signature():
    """Test webhook with a mock signature (will fail but shows endpoint is working)"""
    try:
        print("\n🔐 TESTING WEBHOOK WITH MOCK SIGNATURE")
        print("=" * 50)
        
        webhook_url = "https://b2614b52-973e-4c52-9dec-e3ec14470901.preview.emergentagent.com/api/payments/webhook"
        
        # Generate test payload
        test_payload = generate_test_webhook_payload()
        payload_json = json.dumps(test_payload, separators=(',', ':'))
        
        # Create mock signature (will be invalid but tests the flow)
        mock_signature = create_stripe_signature(payload_json, "whsec_mock_secret")
        
        headers = {
            'Content-Type': 'application/json',
            'Stripe-Signature': mock_signature
        }
        
        print(f"📡 Sending test webhook to: {webhook_url}")
        print(f"📝 Event Type: {test_payload['type']}")
        print(f"🔐 Mock Signature: {mock_signature[:50]}...")
        
        response = requests.post(
            webhook_url, 
            data=payload_json,
            headers=headers,
            timeout=15
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Body: {response.text}")
        
        if response.status_code == 400 and "signature" in response.text.lower():
            print("✅ Webhook signature verification is working!")
            print("   (Expected failure with mock signature)")
            return True
        elif response.status_code == 200:
            print("⚠️  Webhook accepted mock signature (security issue!)")
            return False
        else:
            print(f"❓ Unexpected webhook response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing webhook with signature: {e}")
        return False

if __name__ == "__main__":
    print("🎯 STRIPE WEBHOOK COMPREHENSIVE TEST")
    print("Testing webhook endpoint and signature verification")
    print("=" * 60)
    
    # Test 1: Basic endpoint accessibility
    endpoint_ok = test_webhook_endpoint()
    
    # Test 2: Signature verification
    signature_ok = test_webhook_with_mock_signature()
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY:")
    print(f"   🌐 Endpoint Accessible: {'✅ YES' if endpoint_ok else '❌ NO'}")
    print(f"   🔐 Signature Verification: {'✅ YES' if signature_ok else '❌ NO'}")
    
    if endpoint_ok and signature_ok:
        print("\n🎉 WEBHOOK SYSTEM READY!")
        print("✅ Your webhook endpoint is properly configured")
        print("✅ Signature verification is working")
        print("🔗 Add this URL to Stripe Dashboard:")
        print("   https://b2614b52-973e-4c52-9dec-e3ec14470901.preview.emergentagent.com/api/payments/webhook")
    else:
        print("\n⚠️  WEBHOOK SYSTEM NEEDS ATTENTION")
        print("❌ Please check the issues above before setting up Stripe webhooks")
    
    print("\n🏁 Test completed!")