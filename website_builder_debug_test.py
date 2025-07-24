#!/usr/bin/env python3
"""
Website Builder CREATE Endpoint Debug Test
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://112c0499-f547-4297-a3d4-b823824978f4.preview.emergentagent.com"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

def authenticate():
    """Get JWT token"""
    try:
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            return token
        else:
            print(f"❌ Authentication failed - Status {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_website_builder_create(token):
    """Test Website Builder CREATE endpoint specifically"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    print(f"\n🌐 TESTING WEBSITE BUILDER CREATE ENDPOINT")
    print("=" * 60)
    
    # Test data
    test_data = {
        "name": "Test Website",
        "template_id": "modern-business",
        "domain": "test-site.mewayz.com",
        "description": "Test website for audit",
        "category": "business"
    }
    
    try:
        print(f"📤 Sending POST request to: {BACKEND_URL}/api/website-builder/")
        print(f"📋 Data: {json.dumps(test_data, indent=2)}")
        print(f"🔑 Headers: {headers}")
        
        response = requests.post(
            f"{BACKEND_URL}/api/website-builder/",
            json=test_data,
            headers=headers,
            timeout=30
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"📊 Response Data: {json.dumps(response_data, indent=2)}")
        except:
            print(f"📊 Response Text: {response.text}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("✅ CREATE endpoint working successfully")
            return True
        else:
            print(f"❌ CREATE endpoint failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ CREATE endpoint error: {e}")
        return False

def test_other_endpoints(token):
    """Test other Website Builder endpoints for comparison"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    print(f"\n🔍 TESTING OTHER WEBSITE BUILDER ENDPOINTS")
    print("=" * 60)
    
    endpoints = [
        ("GET", "/api/website-builder/health", "Health check"),
        ("GET", "/api/website-builder/", "List websites"),
        ("GET", "/api/website-builder/templates", "List templates"),
        ("GET", "/api/website-builder/stats", "Get stats"),
        ("POST", "/api/website-builder/test", "Test endpoint")
    ]
    
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=30)
            elif method == "POST":
                response = requests.post(f"{BACKEND_URL}{endpoint}", json={}, headers=headers, timeout=30)
            
            status = "✅" if response.status_code in [200, 201] else "❌"
            print(f"{status} {method} {endpoint} - Status {response.status_code} - {description}")
            
        except Exception as e:
            print(f"❌ {method} {endpoint} - Error: {e}")

def main():
    """Main execution"""
    print("🚀 WEBSITE BUILDER CREATE ENDPOINT DEBUG TEST")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test User: {TEST_EMAIL}")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    
    # Authenticate
    token = authenticate()
    if not token:
        print("❌ Cannot proceed without authentication")
        sys.exit(1)
    
    print("✅ Authentication successful")
    
    # Test CREATE endpoint specifically
    create_success = test_website_builder_create(token)
    
    # Test other endpoints for comparison
    test_other_endpoints(token)
    
    print(f"\n📊 SUMMARY")
    print("=" * 40)
    if create_success:
        print("✅ Website Builder CREATE endpoint is working")
    else:
        print("❌ Website Builder CREATE endpoint has issues")

if __name__ == "__main__":
    main()