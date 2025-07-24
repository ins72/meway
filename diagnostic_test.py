#!/usr/bin/env python3
"""
Quick diagnostic test for specific failing endpoints
"""

import requests
import json

BACKEND_URL = "https://72c4cfb8-834d-427f-b182-685a764bee4b.preview.emergentagent.com"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

def get_auth_token():
    """Get authentication token"""
    auth_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
    response = requests.post(f"{BACKEND_URL}/api/auth/login", json=auth_data)
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def test_endpoint(method, endpoint, data=None):
    """Test a specific endpoint"""
    token = get_auth_token()
    if not token:
        print(f"❌ Authentication failed")
        return
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        if method.upper() == "GET":
            response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
        elif method.upper() == "POST":
            response = requests.post(f"{BACKEND_URL}{endpoint}", json=data, headers=headers)
        
        print(f"{method} {endpoint}: {response.status_code}")
        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)[:200]}...")
        except:
            print(f"Response: {response.text[:200]}...")
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ Error testing {endpoint}: {e}")

if __name__ == "__main__":
    print("🔍 DIAGNOSTIC TEST FOR FAILING ENDPOINTS")
    print("=" * 50)
    
    # Test some failing endpoints
    test_endpoint("GET", "/api/advanced-ui/wizard")
    test_endpoint("GET", "/api/advanced-ui/goals")
    test_endpoint("GET", "/api/advanced-ui/state")
    test_endpoint("GET", "/api/workflow-automation/stats")
    test_endpoint("GET", "/api/visual-builder/projects/stats")