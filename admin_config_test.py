#!/usr/bin/env python3
"""
Admin Configuration Endpoints Test
Testing the correct admin-config endpoints that are working according to test_result.md
"""

import requests
import json
import sys

# Backend URL from environment
BACKEND_URL = "https://77bda007-61bd-44ee-b130-58b448ff1a90.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

def authenticate():
    """Authenticate with the backend"""
    session = requests.Session()
    
    login_data = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = session.post(
        f"{API_BASE}/auth/login",
        data=login_data,
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        access_token = data.get("access_token")
        if access_token:
            session.headers.update({"Authorization": f"Bearer {access_token}"})
            print(f"✅ Authentication successful")
            return session
    
    print(f"❌ Authentication failed")
    return None

def test_admin_config_endpoints():
    """Test the correct admin-config endpoints"""
    session = authenticate()
    if not session:
        return
    
    print("\n=== ADMIN CONFIGURATION ENDPOINTS TEST ===")
    
    # Correct admin-config endpoints from test_result.md
    admin_endpoints = [
        "/admin-config/configuration",
        "/admin-config/integration-status", 
        "/admin-config/system-health",
        "/admin-config/system-logs",
        "/admin-config/available-services",
        "/admin-config/analytics-dashboard",
        "/admin-config/log-statistics",
        "/admin-config/test-stripe",
        "/admin-config/test-openai", 
        "/admin-config/test-sendgrid",
        "/admin-config/test-twitter"
    ]
    
    results = []
    
    for endpoint in admin_endpoints:
        try:
            response = session.get(f"{API_BASE}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint} - Working ({len(str(data))} chars)")
                results.append((endpoint, True, len(str(data))))
            else:
                print(f"❌ {endpoint} - Failed (Status {response.status_code})")
                results.append((endpoint, False, 0))
                
        except Exception as e:
            print(f"❌ {endpoint} - Error: {str(e)}")
            results.append((endpoint, False, 0))
    
    # Summary
    working = sum(1 for _, success, _ in results if success)
    total = len(results)
    print(f"\n=== ADMIN CONFIG SUMMARY ===")
    print(f"Working endpoints: {working}/{total} ({working/total*100:.1f}%)")
    
    return results

if __name__ == "__main__":
    test_admin_config_endpoints()