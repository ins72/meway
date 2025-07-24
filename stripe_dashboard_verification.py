#!/usr/bin/env python3
"""
STRIPE DASHBOARD VERIFICATION TEST
==================================
Verify that payments are actually showing up in Stripe dashboard
by checking the created checkout session details.
"""

import requests
import json

# Test the created session ID from our previous test
session_id = "cs_test_b1YGDu6WaF6xhPKUtavv8qNIjyovygnfa79Pzzn7Kk0K1R92aHORnJAu9n"
stripe_secret_key = "sk_test_51RHeZMPTey8qEzxZn2t4XbP6CATdXVbcgbzvSjdVIsijehuscfcSOVQ016bUXsVaBV9MyoI8EThIBTgmXSjDUs6n00ipAjYRXZ"

def verify_stripe_session():
    """Verify the checkout session exists in Stripe"""
    try:
        headers = {
            'Authorization': f'Bearer {stripe_secret_key}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        print(f"🔍 Verifying Stripe checkout session: {session_id}")
        
        response = requests.get(
            f'https://api.stripe.com/v1/checkout/sessions/{session_id}',
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            session_data = response.json()
            print(f"✅ Session found in Stripe dashboard!")
            print(f"   📝 Status: {session_data.get('status', 'unknown')}")
            print(f"   📝 Payment Status: {session_data.get('payment_status', 'unknown')}")
            print(f"   📝 Amount Total: ${session_data.get('amount_total', 0) / 100:.2f}")
            print(f"   📝 Currency: {session_data.get('currency', 'unknown').upper()}")
            print(f"   📝 Customer Email: {session_data.get('customer_email', 'N/A')}")
            print(f"   📝 Mode: {session_data.get('mode', 'unknown')}")
            
            # Check line items
            if 'line_items' in session_data:
                print(f"   📝 Line Items: {len(session_data['line_items'].get('data', []))}")
            
            # Check metadata
            metadata = session_data.get('metadata', {})
            if metadata:
                print(f"   📝 Workspace: {metadata.get('workspace_name', 'N/A')}")
                print(f"   📝 Bundles: {metadata.get('bundles', 'N/A')}")
                print(f"   📝 Payment Method: {metadata.get('payment_method', 'N/A')}")
            
            return True
        else:
            print(f"❌ Session not found in Stripe: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   📄 Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   📄 Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying session: {e}")
        return False

def list_recent_sessions():
    """List recent checkout sessions"""
    try:
        headers = {
            'Authorization': f'Bearer {stripe_secret_key}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        print(f"\n📋 Listing recent checkout sessions...")
        
        response = requests.get(
            'https://api.stripe.com/v1/checkout/sessions?limit=5',
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            sessions_data = response.json()
            sessions = sessions_data.get('data', [])
            print(f"✅ Found {len(sessions)} recent sessions:")
            
            for i, session in enumerate(sessions, 1):
                print(f"   {i}. Session ID: {session.get('id', 'N/A')}")
                print(f"      Status: {session.get('status', 'unknown')}")
                print(f"      Amount: ${session.get('amount_total', 0) / 100:.2f}")
                print(f"      Created: {session.get('created', 'N/A')}")
                metadata = session.get('metadata', {})
                if metadata.get('workspace_name'):
                    print(f"      Workspace: {metadata.get('workspace_name')}")
                print()
            
            return True
        else:
            print(f"❌ Failed to list sessions: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error listing sessions: {e}")
        return False

if __name__ == "__main__":
    print("🚀 STRIPE DASHBOARD VERIFICATION")
    print("=" * 50)
    
    # Verify specific session
    session_verified = verify_stripe_session()
    
    # List recent sessions
    list_verified = list_recent_sessions()
    
    print("=" * 50)
    if session_verified and list_verified:
        print("✅ VERIFICATION SUCCESSFUL: Payments are showing up in Stripe dashboard!")
    else:
        print("❌ VERIFICATION FAILED: Issues detected with Stripe dashboard integration")