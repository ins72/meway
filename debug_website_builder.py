#!/usr/bin/env python3
"""
Debug Website Builder Create Endpoint
"""

import requests
import json
import sys

# Configuration
BACKEND_URL = "https://3dc4dc3c-9195-4a26-87f6-3f23beffd557.preview.emergentagent.com"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

def test_website_builder_create():
    """Test the website builder create endpoint specifically"""
    
    print("🔐 AUTHENTICATING...")
    # Login to get token
    login_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
    response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Authentication failed: {response.status_code}")
        return False
    
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    print("✅ Authentication successful")
    
    print("\n🌐 TESTING WEBSITE BUILDER CREATE...")
    
    # Test data
    test_data = {
        "name": "Debug Test Website",
        "template_id": "modern-business",
        "domain": "debug-test.mewayz.com",
        "description": "Debug test website",
        "category": "business"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/website-builder/", 
            json=test_data, 
            headers=headers, 
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ CREATE endpoint working!")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ CREATE endpoint failed")
            print(f"Response Text: {response.text}")
            
            # Try to get more details
            try:
                error_data = response.json()
                print(f"Error JSON: {json.dumps(error_data, indent=2)}")
            except:
                print("Could not parse error as JSON")
            
            return False
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

if __name__ == "__main__":
    success = test_website_builder_create()
    sys.exit(0 if success else 1)