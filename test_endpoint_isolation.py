#!/usr/bin/env python3
"""
Test Website Builder CREATE endpoint without authentication
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://0b0b9ebf-d7aa-41df-aa42-dd8ab4b72b68.preview.emergentagent.com"

def test_create_without_auth():
    """Test CREATE endpoint without authentication to isolate the issue"""
    headers = {"Content-Type": "application/json"}
    
    test_data = {
        "name": "Test Website",
        "template_id": "modern-business",
        "domain": "test-site.mewayz.com",
        "description": "Test website for audit",
        "category": "business"
    }
    
    try:
        print(f"📤 Testing CREATE without authentication...")
        response = requests.post(
            f"{BACKEND_URL}/api/website-builder/",
            json=test_data,
            headers=headers,
            timeout=30
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📊 Response: {response.text}")
        
        if response.status_code == 401:
            print("✅ Expected 401 - Authentication required (endpoint is reachable)")
            return True
        elif response.status_code == 500:
            print("❌ 500 error - Internal server error (same issue)")
            return False
        else:
            print(f"❓ Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def test_test_endpoint():
    """Test the /test endpoint that doesn't require auth"""
    try:
        print(f"📤 Testing /test endpoint...")
        response = requests.post(
            f"{BACKEND_URL}/api/website-builder/test",
            json={},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📊 Response: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Test endpoint error: {e}")
        return False

def main():
    """Main execution"""
    print("🚀 WEBSITE BUILDER ENDPOINT ISOLATION TEST")
    print("=" * 60)
    
    # Test without auth
    no_auth_success = test_create_without_auth()
    
    # Test the test endpoint
    test_endpoint_success = test_test_endpoint()
    
    print(f"\n📊 RESULTS")
    print("=" * 30)
    print(f"CREATE without auth: {'✅' if no_auth_success else '❌'}")
    print(f"Test endpoint: {'✅' if test_endpoint_success else '❌'}")

if __name__ == "__main__":
    main()