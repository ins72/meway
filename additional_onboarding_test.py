#!/usr/bin/env python3
"""
ADDITIONAL ONBOARDING API TESTING - CORRECT ENDPOINTS
====================================================
Testing the correct bundle and pricing endpoints discovered in the API
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://eff6f53c-47df-43a1-9962-4d20b26f6dc5.preview.emergentagent.com"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

def authenticate():
    """Get authentication token"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                return {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    except Exception as e:
        print(f"Authentication failed: {e}")
    
    return {"Content-Type": "application/json"}

def test_correct_bundle_endpoints():
    """Test the correct bundle and pricing endpoints"""
    print("🔍 TESTING CORRECT BUNDLE AND PRICING ENDPOINTS")
    print("=" * 60)
    
    headers = authenticate()
    
    # Test 1: Get available bundles (correct endpoint)
    print("\n1. Testing /api/workspace-subscription/bundles/available")
    try:
        response = requests.get(f"{BACKEND_URL}/api/workspace-subscription/bundles/available", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            bundles = response.json()
            print("✅ Available bundles retrieved successfully:")
            print(json.dumps(bundles, indent=2))
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Calculate pricing for bundle combinations
    print("\n2. Testing /api/workspace-subscription/pricing/calculate")
    
    # Test different bundle combinations
    test_combinations = [
        {"bundles": "creator", "billing_cycle": "monthly"},
        {"bundles": "creator,ecommerce", "billing_cycle": "monthly"},
        {"bundles": "creator,social_media,business", "billing_cycle": "yearly"},
        {"bundles": "education,operations", "billing_cycle": "monthly"}
    ]
    
    for combo in test_combinations:
        try:
            response = requests.get(
                f"{BACKEND_URL}/api/workspace-subscription/pricing/calculate",
                params=combo,
                headers=headers
            )
            print(f"\n📊 Bundles: {combo['bundles']} | Cycle: {combo['billing_cycle']}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                pricing = response.json()
                print("✅ Pricing calculated successfully:")
                print(json.dumps(pricing, indent=2))
            else:
                print(f"❌ Failed: {response.text}")
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    # Test 3: Test workspace subscription creation with real workspace
    print("\n3. Testing workspace subscription creation with real workspace")
    
    # First create a workspace
    workspace_data = {
        "name": "Subscription Test Workspace",
        "industry": "technology",
        "team_size": "1-5"
    }
    
    try:
        workspace_response = requests.post(
            f"{BACKEND_URL}/api/workspace/",
            json=workspace_data,
            headers=headers
        )
        
        if workspace_response.status_code == 200:
            workspace = workspace_response.json()
            workspace_id = workspace.get("data", {}).get("id")
            print(f"✅ Created workspace: {workspace_id}")
            
            # Now try to create subscription for this workspace
            subscription_data = {
                "selected_bundles": ["creator", "social_media"],
                "billing_cycle": "monthly",
                "payment_method": "stripe",
                "auto_renew": True
            }
            
            subscription_response = requests.post(
                f"{BACKEND_URL}/api/workspace-subscription/workspace/{workspace_id}/subscription",
                json=subscription_data,
                headers=headers
            )
            
            print(f"Subscription creation status: {subscription_response.status_code}")
            if subscription_response.status_code in [200, 201]:
                subscription = subscription_response.json()
                print("✅ Subscription created successfully:")
                print(json.dumps(subscription, indent=2))
            else:
                print(f"❌ Subscription creation failed: {subscription_response.text}")
                
        else:
            print(f"❌ Workspace creation failed: {workspace_response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_correct_bundle_endpoints()